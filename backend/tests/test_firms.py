"""Tests for M1b Firms module: firm settings, invitations, user administration, roles, retention, advocate profiles, and RBAC matrix."""

from __future__ import annotations

from uuid import UUID

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from uuid_utils import uuid7

from app.core.auth_crypto import create_access_token, hash_password
from app.core.db import get_db_session
from app.core.models import Base, Firm, FirmMembership, User
from app.core.permissions import (
    generate_matrix_markdown,
    get_capabilities_for_role,
)
from app.main import create_app


@pytest.fixture
async def test_db():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)
    async with session_factory() as session:
        yield session

    await engine.dispose()


@pytest.fixture
async def client(test_db: AsyncSession) -> AsyncClient:
    app = create_app()

    async def _override_db():
        yield test_db

    app.dependency_overrides[get_db_session] = _override_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


def make_auth_headers(user_id: UUID, firm_id: UUID, role: str) -> dict[str, str]:
    token = create_access_token(
        user_id=user_id,
        firm_id=firm_id,
        role=role,
        is_client=False,
        mfa_completed=True,
    )
    return {"Authorization": f"Bearer {token}"}


# ── 1. RBAC Matrix Verification Test ──


def test_generated_matrix_matches_prd_spec() -> None:
    """The generated matrix markdown must match Docs 02 Section 10 definitions."""
    md = generate_matrix_markdown()
    assert "| Capability | Admin | Partner | Associate | Paralegal | Researcher | Client |" in md
    assert "| Manage users/roles/retention | Y | - | - | - | - | - |" in md
    assert "| View all firm matters | Y | Y | - | - | - | - |" in md
    assert "| Approve draft | - | M | - | - | - | - |" in md
    assert "| Publish client update | - | M | M | - | - | - |" in md

    # Check capabilities returned for each role
    admin_caps = get_capabilities_for_role("admin")
    assert "user.manage" in admin_caps
    assert "firm.manage" in admin_caps
    assert "draft.approve" not in admin_caps

    partner_caps = get_capabilities_for_role("partner")
    assert "draft.approve" in partner_caps
    assert "user.manage" not in partner_caps

    associate_caps = get_capabilities_for_role("associate")
    assert "draft.edit" in associate_caps
    assert "draft.approve" not in associate_caps


# ── 2. Firm Settings & Retention Tests ──


async def test_firm_settings_and_retention(client: AsyncClient, test_db: AsyncSession) -> None:
    firm_id = uuid7()
    admin_id = uuid7()
    associate_id = uuid7()

    test_db.add_all(
        [
            Firm(id=firm_id, name="Parekh & Co", status="active", settings={"court": "Revenue"}),
            User(
                id=admin_id,
                email="admin@parekh.in",
                password_hash=hash_password("Pass1234567!"),
                full_name="Admin Parekh",
                status="active",
            ),
            User(
                id=associate_id,
                email="assoc@parekh.in",
                password_hash=hash_password("Pass1234567!"),
                full_name="Assoc Parekh",
                status="active",
            ),
            FirmMembership(firm_id=firm_id, user_id=admin_id, role="admin", status="active"),
            FirmMembership(
                firm_id=firm_id, user_id=associate_id, role="associate", status="active"
            ),
        ]
    )
    await test_db.commit()

    admin_headers = make_auth_headers(admin_id, firm_id, "admin")
    assoc_headers = make_auth_headers(associate_id, firm_id, "associate")

    # Associate cannot view firm settings (firm.manage required -> 404 per D-05)
    resp = await client.get("/api/v1/firm", headers=assoc_headers)
    assert resp.status_code == 404

    # Admin views firm settings
    resp = await client.get("/api/v1/firm", headers=admin_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Parekh & Co"
    assert data["settings"]["court"] == "Revenue"

    # Admin updates firm settings
    resp = await client.patch(
        "/api/v1/firm",
        headers=admin_headers,
        json={"name": "Parekh & Partners", "settings": {"primary_locale": "gu"}},
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "Parekh & Partners"
    assert resp.json()["settings"]["primary_locale"] == "gu"

    # Retention policy configuration
    ret_resp = await client.get("/api/v1/firm/retention", headers=admin_headers)
    assert ret_resp.status_code == 200
    assert ret_resp.json()["retention_default_days"] is None

    # Set retention to 2555 days (7 years)
    set_ret = await client.put(
        "/api/v1/firm/retention",
        headers=admin_headers,
        json={"retention_default_days": 2555},
    )
    assert set_ret.status_code == 200
    assert set_ret.json()["retention_default_days"] == 2555


# ── 3. User Administration & Guard Tests ──


async def test_admin_user_management_and_last_admin_protection(
    client: AsyncClient, test_db: AsyncSession
) -> None:
    firm_id = uuid7()
    admin_id = uuid7()
    paralegal_id = uuid7()

    test_db.add_all(
        [
            Firm(id=firm_id, name="Desai Legal", status="active"),
            User(
                id=admin_id,
                email="admin@desai.in",
                password_hash=hash_password("Pass1234567!"),
                full_name="Admin Desai",
                status="active",
            ),
            User(
                id=paralegal_id,
                email="para@desai.in",
                password_hash=hash_password("Pass1234567!"),
                full_name="Para Desai",
                status="active",
            ),
            FirmMembership(firm_id=firm_id, user_id=admin_id, role="admin", status="active"),
            FirmMembership(
                firm_id=firm_id, user_id=paralegal_id, role="paralegal", status="active"
            ),
        ]
    )
    await test_db.commit()

    admin_headers = make_auth_headers(admin_id, firm_id, "admin")

    # List users in firm
    resp = await client.get("/api/v1/firm/users", headers=admin_headers)
    assert resp.status_code == 200
    users = resp.json()
    assert len(users) == 2

    # Guard: Attempting to demote the sole admin must return 409 conflict
    demote_resp = await client.patch(
        f"/api/v1/firm/users/{admin_id}",
        headers=admin_headers,
        json={"role": "partner"},
    )
    assert demote_resp.status_code == 409
    assert demote_resp.json()["code"] == "last_admin_protected"

    # Guard: Attempting to suspend the sole admin must return 409 conflict
    suspend_admin_resp = await client.patch(
        f"/api/v1/firm/users/{admin_id}",
        headers=admin_headers,
        json={"status": "suspended"},
    )
    assert suspend_admin_resp.status_code == 409
    assert suspend_admin_resp.json()["code"] == "last_admin_protected"

    # Promote paralegal to associate
    promote_resp = await client.patch(
        f"/api/v1/firm/users/{paralegal_id}",
        headers=admin_headers,
        json={"role": "associate"},
    )
    assert promote_resp.status_code == 200
    assert promote_resp.json()["role"] == "associate"

    # Suspend user
    suspend_resp = await client.patch(
        f"/api/v1/firm/users/{paralegal_id}",
        headers=admin_headers,
        json={"status": "suspended"},
    )
    assert suspend_resp.status_code == 200
    assert suspend_resp.json()["status"] == "suspended"


# ── 4. Invitations Single-Use, 72h Expiry & Acceptance ──


async def test_invitations_creation_and_acceptance(
    client: AsyncClient, test_db: AsyncSession
) -> None:
    firm_id = uuid7()
    admin_id = uuid7()

    test_db.add_all(
        [
            Firm(id=firm_id, name="Kothari Advocates", status="active"),
            User(
                id=admin_id,
                email="admin@kothari.in",
                password_hash=hash_password("Pass1234567!"),
                full_name="Admin Kothari",
                status="active",
            ),
            FirmMembership(firm_id=firm_id, user_id=admin_id, role="admin", status="active"),
        ]
    )
    await test_db.commit()

    admin_headers = make_auth_headers(admin_id, firm_id, "admin")

    # Create invitation
    inv_resp = await client.post(
        "/api/v1/firm/invitations",
        headers=admin_headers,
        json={"email": "newassociate@kothari.in", "role": "associate"},
    )
    assert inv_resp.status_code == 201
    inv_data = inv_resp.json()
    assert inv_data["email"] == "newassociate@kothari.in"
    assert inv_data["role"] == "associate"
    assert "token=" in inv_data["invite_url"]

    # Extract token
    token = inv_data["invite_url"].split("token=")[1]

    # Accept invitation (public endpoint from M1a)
    accept_resp = await client.post(
        "/api/v1/auth/invitations/accept",
        json={
            "token": token,
            "full_name": "Adv. Bhavin Kothari",
            "password": "StrongPassword2026!",
        },
    )
    assert accept_resp.status_code == 200

    # Single-use: Reusing the same invite token must fail with 404
    reuse_resp = await client.post(
        "/api/v1/auth/invitations/accept",
        json={
            "token": token,
            "full_name": "Adv. Bhavin Kothari",
            "password": "StrongPassword2026!",
        },
    )
    assert reuse_resp.status_code == 404


# ── 5. Cross-Firm User Access Impossible ──


async def test_cross_firm_user_access_impossible(
    client: AsyncClient, test_db: AsyncSession
) -> None:
    firm_1 = uuid7()
    firm_2 = uuid7()
    admin_1 = uuid7()
    admin_2 = uuid7()

    test_db.add_all(
        [
            Firm(id=firm_1, name="Firm One", status="active"),
            Firm(id=firm_2, name="Firm Two", status="active"),
            User(
                id=admin_1,
                email="admin1@firm1.in",
                password_hash=hash_password("Pass1234567!"),
                full_name="Admin One",
                status="active",
            ),
            User(
                id=admin_2,
                email="admin2@firm2.in",
                password_hash=hash_password("Pass1234567!"),
                full_name="Admin Two",
                status="active",
            ),
            FirmMembership(firm_id=firm_1, user_id=admin_1, role="admin", status="active"),
            FirmMembership(firm_id=firm_2, user_id=admin_2, role="admin", status="active"),
        ]
    )
    await test_db.commit()

    headers_1 = make_auth_headers(admin_1, firm_1, "admin")

    # Admin 1 requests /firm/users: must only see Admin 1, never Admin 2
    users_resp = await client.get("/api/v1/firm/users", headers=headers_1)
    assert users_resp.status_code == 200
    user_ids = [u["id"] for u in users_resp.json()]
    assert str(admin_1) in user_ids
    assert str(admin_2) not in user_ids

    # Admin 1 attempts to modify Admin 2 (from Firm 2) through Firm 1's user endpoint -> 404
    cross_modify = await client.patch(
        f"/api/v1/firm/users/{admin_2}",
        headers=headers_1,
        json={"role": "paralegal"},
    )
    assert cross_modify.status_code == 404


# ── 6. Advocate Profile & Enrolment Format Validation ──


async def test_advocate_profile_and_verification(
    client: AsyncClient, test_db: AsyncSession
) -> None:
    firm_id = uuid7()
    admin_id = uuid7()
    advocate_id = uuid7()

    test_db.add_all(
        [
            Firm(id=firm_id, name="Vakil Chambers", status="active"),
            User(
                id=admin_id,
                email="admin@vakil.in",
                password_hash=hash_password("Pass1234567!"),
                full_name="Admin Vakil",
                status="active",
            ),
            User(
                id=advocate_id,
                email="adv@vakil.in",
                password_hash=hash_password("Pass1234567!"),
                full_name="Adv. Hardik",
                status="active",
            ),
            FirmMembership(firm_id=firm_id, user_id=admin_id, role="admin", status="active"),
            FirmMembership(firm_id=firm_id, user_id=advocate_id, role="partner", status="active"),
        ]
    )
    await test_db.commit()

    adv_headers = make_auth_headers(advocate_id, firm_id, "partner")
    admin_headers = make_auth_headers(admin_id, firm_id, "admin")

    # View my profile
    prof_resp = await client.get("/api/v1/me/profile", headers=adv_headers)
    assert prof_resp.status_code == 200
    assert prof_resp.json()["email"] == "adv@vakil.in"
    assert prof_resp.json()["advocate_profile"] is None

    # Invalid enrolment format rejection
    invalid_patch = await client.patch(
        "/api/v1/me/profile",
        headers=adv_headers,
        json={"advocate_profile": {"enrolment_no": "invalid_enrolment_no"}},
    )
    assert invalid_patch.status_code == 422 or invalid_patch.status_code == 400

    # Valid enrolment format GJ/1842/2016
    valid_patch = await client.patch(
        "/api/v1/me/profile",
        headers=adv_headers,
        json={"advocate_profile": {"enrolment_no": "GJ/1842/2016"}},
    )
    assert valid_patch.status_code == 200
    adv_data = valid_patch.json()["advocate_profile"]
    assert adv_data["enrolment_no"] == "GJ/1842/2016"
    assert adv_data["state_code"] == "GJ"
    assert adv_data["is_verified"] is False
    assert "Does not imply live Bar Council verification" in adv_data["notice"]

    # Manual admin verification flag
    verify_resp = await client.post(
        f"/api/v1/firm/users/{advocate_id}/verify-advocate",
        headers=admin_headers,
        json={"is_verified": True},
    )
    assert verify_resp.status_code == 200
    assert verify_resp.json()["is_verified"] is True
    assert verify_resp.json()["verified_by"] == str(admin_id)
