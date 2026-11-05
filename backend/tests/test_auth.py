"""Test suite for authentication, authorization, MFA, sessions, and security constraints."""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.db import get_db_session
from app.main import create_app
from app.modules.auth.models import Base
from app.modules.auth.router import get_auth_service, get_redis
from app.modules.auth.service import AuthService


class InMemoryRedis:
    def __init__(self) -> None:
        self.store: dict[str, str] = {}
        self.ttls: dict[str, int] = {}

    async def get(self, key: str) -> str | None:
        return self.store.get(key)

    async def setex(self, key: str, seconds: int, value: str) -> None:
        self.store[key] = value
        self.ttls[key] = seconds

    async def delete(self, *keys: str) -> None:
        for k in keys:
            self.store.pop(k, None)

    async def ping(self) -> bool:
        return True

    async def aclose(self) -> None:
        pass

    def pipeline(self, transaction: bool = True):
        return InMemoryPipeline(self)


class InMemoryPipeline:
    def __init__(self, r: InMemoryRedis) -> None:
        self.r = r
        self.ops = []

    def incr(self, key: str):
        self.ops.append(("incr", key))
        return self

    def expire(self, key: str, seconds: int, nx: bool = False):
        self.ops.append(("expire", key, seconds))
        return self

    async def execute(self):
        results = []
        for op in self.ops:
            if op[0] == "incr":
                k = op[1]
                curr = int(self.r.store.get(k, 0)) + 1
                self.r.store[k] = str(curr)
                results.append(curr)
            elif op[0] == "expire":
                results.append(True)
        self.ops.clear()
        return results


@pytest.fixture
async def test_db_session():
    # Use SQLite in-memory for fast unit/integration testing
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)
    async with session_factory() as session:
        yield session

    await engine.dispose()


@pytest.fixture
def fake_redis() -> InMemoryRedis:
    return InMemoryRedis()


@pytest.fixture
async def auth_client(test_db_session: AsyncSession, fake_redis: InMemoryRedis) -> AsyncClient:
    app = create_app()

    async def _override_db():
        yield test_db_session

    async def _override_redis():
        return fake_redis

    async def _override_auth_service():
        return AuthService(db=test_db_session, redis=fake_redis)

    app.dependency_overrides[get_db_session] = _override_db
    app.dependency_overrides[get_redis] = _override_redis
    app.dependency_overrides[get_auth_service] = _override_auth_service

    transport = ASGITransport(app=app, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.anyio
async def test_register_firm_and_password_policy(auth_client: AsyncClient) -> None:
    # 1. Short password (<12 chars) rejected
    resp = await auth_client.post(
        "/api/v1/auth/register",
        json={
            "firm_name": "Mehta & Associates",
            "admin_name": "Rajesh Mehta",
            "email": "rajesh@mehtalaw.in",
            "password": "short",
        },
    )
    assert resp.status_code == 422
    body = resp.json()
    assert "12 characters" in str(body)

    # 2. Valid registration succeeds
    resp = await auth_client.post(
        "/api/v1/auth/register",
        json={
            "firm_name": "Mehta & Associates",
            "admin_name": "Rajesh Mehta",
            "email": "rajesh@mehtalaw.in",
            "password": "CorrectHorseBatteryStaple2026!",
        },
    )
    assert resp.status_code == 201
    assert "firm_id" in resp.json()

    # 3. Duplicate registration rejected with 409
    dup_resp = await auth_client.post(
        "/api/v1/auth/register",
        json={
            "firm_name": "Mehta Duplicate",
            "admin_name": "Rajesh Mehta",
            "email": "rajesh@mehtalaw.in",
            "password": "CorrectHorseBatteryStaple2026!",
        },
    )
    assert dup_resp.status_code == 409


@pytest.mark.anyio
async def test_wrong_password_and_lockout(auth_client: AsyncClient) -> None:
    await auth_client.post(
        "/api/v1/auth/register",
        json={
            "firm_name": "Lockout Firm",
            "admin_name": "Anita Partner",
            "email": "anita@firm.in",
            "password": "ValidPassword12345!",
        },
    )

    # 4 bad attempts
    for _ in range(4):
        resp = await auth_client.post(
            "/api/v1/auth/login",
            json={"email": "anita@firm.in", "password": "WrongPassword!"},
        )
        assert resp.status_code == 401
        assert resp.json()["code"] == "unauthenticated"

    # 5th bad attempt triggers lockout
    resp = await auth_client.post(
        "/api/v1/auth/login",
        json={"email": "anita@firm.in", "password": "WrongPassword!"},
    )
    assert resp.status_code == 401

    # 6th attempt should be blocked with 423 account_locked
    resp = await auth_client.post(
        "/api/v1/auth/login",
        json={"email": "anita@firm.in", "password": "ValidPassword12345!"},
    )
    assert resp.status_code == 423
    assert resp.json()["code"] == "account_locked"


@pytest.mark.anyio
async def test_mfa_flow_and_mandatory_protection(
    auth_client: AsyncClient, test_db_session: AsyncSession
) -> None:
    # Register user
    reg = await auth_client.post(
        "/api/v1/auth/register",
        json={
            "firm_name": "MFA Test Firm",
            "admin_name": "Parth Admin",
            "email": "parth@firm.in",
            "password": "ValidPassword12345!",
        },
    )
    assert reg.status_code == 201

    # Login without MFA enabled gives access token to set up MFA
    login_resp = await auth_client.post(
        "/api/v1/auth/login",
        json={"email": "parth@firm.in", "password": "ValidPassword12345!"},
    )
    assert login_resp.status_code == 200
    token_data = login_resp.json()
    access_token = token_data["access_token"]
    auth_headers = {"Authorization": f"Bearer {access_token}"}

    # Start MFA enrollment
    enroll_resp = await auth_client.post("/api/v1/auth/mfa/enroll", headers=auth_headers)
    assert enroll_resp.status_code == 200
    enroll_data = enroll_resp.json()
    secret = enroll_data["secret"]

    # Generate valid code with pyotp
    import pyotp

    totp = pyotp.TOTP(secret)
    valid_code = totp.now()

    # Confirm MFA
    confirm_resp = await auth_client.post(
        "/api/v1/auth/mfa/confirm",
        json={"secret": secret, "code": valid_code},
        headers=auth_headers,
    )
    assert confirm_resp.status_code == 200
    recovery_codes = confirm_resp.json()["recovery_codes"]
    assert len(recovery_codes) == 8

    # Next login now returns mfa_required
    mfa_login_resp = await auth_client.post(
        "/api/v1/auth/login",
        json={"email": "parth@firm.in", "password": "ValidPassword12345!"},
    )
    assert mfa_login_resp.status_code == 200
    mfa_info = mfa_login_resp.json()
    assert mfa_info["mfa_required"] is True
    challenge_id = mfa_info["challenge_id"]

    # Bad MFA code rejected
    bad_verify = await auth_client.post(
        "/api/v1/auth/mfa/verify",
        json={"challenge_id": challenge_id, "code": "000000"},
    )
    assert bad_verify.status_code == 401

    # Valid recovery code succeeds
    rec_verify = await auth_client.post(
        "/api/v1/auth/mfa/verify",
        json={"challenge_id": challenge_id, "code": recovery_codes[0]},
    )
    assert rec_verify.status_code == 200
    assert "access_token" in rec_verify.json()


@pytest.mark.anyio
async def test_refresh_token_rotation_and_reuse_detection(auth_client: AsyncClient) -> None:
    await auth_client.post(
        "/api/v1/auth/register",
        json={
            "firm_name": "Rotation Firm",
            "admin_name": "Meera Researcher",
            "email": "meera@firm.in",
            "password": "ValidPassword12345!",
        },
    )

    login_resp = await auth_client.post(
        "/api/v1/auth/login",
        json={"email": "meera@firm.in", "password": "ValidPassword12345!"},
    )
    refresh_cookie = login_resp.cookies.get("refresh_token")
    csrf_token = login_resp.json()["csrf_token"]
    assert refresh_cookie is not None

    # Rotate refresh token
    rotate_resp = await auth_client.post(
        "/api/v1/auth/refresh",
        cookies={"refresh_token": refresh_cookie},
        headers={"X-CSRF-Token": csrf_token},
    )
    assert rotate_resp.status_code == 200
    new_refresh_cookie = rotate_resp.cookies.get("refresh_token")
    new_csrf_token = rotate_resp.json()["csrf_token"]
    assert new_refresh_cookie != refresh_cookie

    # REUSE OLD REFRESH TOKEN -> Must trigger reuse detection, revoke family and 401
    reuse_resp = await auth_client.post(
        "/api/v1/auth/refresh",
        cookies={"refresh_token": refresh_cookie},
        headers={"X-CSRF-Token": csrf_token},
    )
    assert reuse_resp.status_code == 401
    assert reuse_resp.json()["code"] == "token_reused"

    # Now the new token is also revoked because the entire family got invalidated!
    new_token_resp = await auth_client.post(
        "/api/v1/auth/refresh",
        cookies={"refresh_token": new_refresh_cookie},
        headers={"X-CSRF-Token": new_csrf_token},
    )
    assert new_token_resp.status_code == 401


@pytest.mark.anyio
async def test_auth_me_returns_firm_and_capabilities(auth_client: AsyncClient) -> None:
    await auth_client.post(
        "/api/v1/auth/register",
        json={
            "firm_name": "Mehta Law Chambers",
            "admin_name": "Rajesh Partner",
            "email": "rajesh@chambers.in",
            "password": "ValidPassword12345!",
        },
    )

    login_resp = await auth_client.post(
        "/api/v1/auth/login",
        json={"email": "rajesh@chambers.in", "password": "ValidPassword12345!"},
    )
    access_token = login_resp.json()["access_token"]

    me_resp = await auth_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert me_resp.status_code == 200
    me_data = me_resp.json()
    assert me_data["user"]["email"] == "rajesh@chambers.in"
    assert me_data["role"] == "admin"
    assert "user.manage" in me_data["capabilities"]
    assert len(me_data["firms"]) == 1
    assert me_data["firms"][0]["name"] == "Mehta Law Chambers"


@pytest.mark.anyio
async def test_client_otp_flow(auth_client: AsyncClient, fake_redis: InMemoryRedis) -> None:
    mobile = "+919876543210"

    # Request OTP
    req = await auth_client.post("/api/v1/auth/client/otp/request", json={"mobile": mobile})
    assert req.status_code == 200

    # Cooldown blocks immediate re-request
    dup_req = await auth_client.post("/api/v1/auth/client/otp/request", json={"mobile": mobile})
    assert dup_req.status_code == 429

    # Bad OTP fails
    bad_verify = await auth_client.post(
        "/api/v1/auth/client/otp/verify",
        json={"mobile": mobile, "code": "000000"},
    )
    assert bad_verify.status_code == 401

    # Extract stored OTP hash from fake redis
    otp_raw = await fake_redis.get(f"client_otp:{mobile}")
    assert otp_raw is not None


@pytest.mark.anyio
async def test_server_authoritative_roles_no_client_injection(auth_client: AsyncClient) -> None:
    # Verify that registration body or headers cannot elevate or specify role
    reg = await auth_client.post(
        "/api/v1/auth/register",
        json={
            "firm_name": "Test Security Firm",
            "admin_name": "Associate User",
            "email": "user@security.in",
            "password": "ValidPassword12345!",
            "role": "superadmin",  # Attacker tries to inject role
            "firm_id": "00000000-0000-0000-0000-000000000000",
        },
    )
    assert reg.status_code == 201

    login_resp = await auth_client.post(
        "/api/v1/auth/login",
        json={"email": "user@security.in", "password": "ValidPassword12345!"},
    )
    token = login_resp.json()["access_token"]

    me_resp = await auth_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    # The first registered user is strictly 'admin' by server rule, client input is ignored
    assert me_resp.json()["role"] == "admin"
