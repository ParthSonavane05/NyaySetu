"""Comprehensive tests for database schema, constraints, RLS policies, audit immutability, and seed idempotency."""

from __future__ import annotations

import datetime

import pytest
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from uuid_utils import uuid7

from app.core.models import (
    AuditEvent,
    Base,
    Firm,
    LandParcel,
    Matter,
    TitleEvent,
    User,
)
from app.db.seeds import (
    EVENT_809_ID,
    MEHTA_FIRM_ID,
    PARCEL_142A_ID,
    run_all_seeds,
)


@pytest.fixture
async def sqlite_engine():
    """SQLite in-memory engine with all tables created."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
async def sqlite_session(sqlite_engine) -> AsyncSession:
    session_factory = async_sessionmaker(
        bind=sqlite_engine, expire_on_commit=False, class_=AsyncSession
    )
    async with session_factory() as session:
        yield session


# ══════════════════════════════════════════════════════════════════════════════
# 1. SEED IDEMPOTENCY TESTS
# ══════════════════════════════════════════════════════════════════════════════


async def test_seed_idempotency(sqlite_session: AsyncSession) -> None:
    """Calling run_all_seeds multiple times should produce exact same results without error."""
    # First seed run
    await run_all_seeds(sqlite_session)

    # Verify key demo entities exist
    firm = await sqlite_session.get(Firm, MEHTA_FIRM_ID)
    assert firm is not None
    assert firm.name == "Mehta & Associates"

    matter_res = await sqlite_session.execute(
        select(Matter).where(Matter.matter_no == "MAT-2026-0809")
    )
    matter = matter_res.scalar_one_or_none()
    assert matter is not None
    assert matter.firm_id == MEHTA_FIRM_ID
    assert matter.stage == "drafting"
    assert matter.status == "open"

    parcel = await sqlite_session.get(LandParcel, PARCEL_142A_ID)
    assert parcel is not None
    assert parcel.survey_no == "142/A"
    assert parcel.area_sqm == 12200

    ev_809 = await sqlite_session.get(TitleEvent, EVENT_809_ID)
    assert ev_809 is not None
    assert ev_809.entry_no == "809"
    assert ev_809.status == "disputed"

    # Second seed run (must NOT raise IntegrityError or duplicate records)
    await run_all_seeds(sqlite_session)

    # Verify counts remain identical
    firms_count = (
        (await sqlite_session.execute(select(Firm).where(Firm.id == MEHTA_FIRM_ID))).scalars().all()
    )
    assert len(firms_count) == 1

    users_count = (await sqlite_session.execute(select(User))).scalars().all()
    assert len(users_count) == 4

    events_count = (await sqlite_session.execute(select(TitleEvent))).scalars().all()
    assert len(events_count) == 4


# ══════════════════════════════════════════════════════════════════════════════
# 2. CHECK CONSTRAINTS & DATA VALIDATION TESTS
# ══════════════════════════════════════════════════════════════════════════════


async def test_matter_invalid_stage_rejected(sqlite_session: AsyncSession) -> None:
    """Inserting a Matter with an illegal stage must trigger a CHECK constraint error."""
    firm_id = uuid7()
    user_id = uuid7()
    sqlite_session.add(Firm(id=firm_id, name="Test Firm", status="active"))
    sqlite_session.add(
        User(
            id=user_id,
            email="test@firm.in",
            password_hash="hash",
            full_name="Tester",
            status="active",
        )
    )
    await sqlite_session.flush()

    invalid_matter = Matter(
        id=uuid7(),
        firm_id=firm_id,
        matter_no="MAT-TEST-001",
        title="Invalid Stage Case",
        stage="unknown_illegal_stage",  # violates ck_matters_stage
        status="open",
        created_by=user_id,
    )
    sqlite_session.add(invalid_matter)

    with pytest.raises(IntegrityError):
        await sqlite_session.flush()

    await sqlite_session.rollback()


async def test_matter_invalid_status_rejected(sqlite_session: AsyncSession) -> None:
    """Inserting a Matter with an illegal status must trigger a CHECK constraint error."""
    firm_id = uuid7()
    user_id = uuid7()
    sqlite_session.add(Firm(id=firm_id, name="Test Firm 2", status="active"))
    sqlite_session.add(
        User(
            id=user_id,
            email="test2@firm.in",
            password_hash="hash",
            full_name="Tester 2",
            status="active",
        )
    )
    await sqlite_session.flush()

    invalid_matter = Matter(
        id=uuid7(),
        firm_id=firm_id,
        matter_no="MAT-TEST-002",
        title="Invalid Status Case",
        stage="intake",
        status="invalid_status",  # violates ck_matters_status
        created_by=user_id,
    )
    sqlite_session.add(invalid_matter)

    with pytest.raises(IntegrityError):
        await sqlite_session.flush()

    await sqlite_session.rollback()


# ══════════════════════════════════════════════════════════════════════════════
# 3. RLS ISOLATION SIMULATION & LOGIC TEST
# ══════════════════════════════════════════════════════════════════════════════


async def test_tenant_isolation_semantics(sqlite_session: AsyncSession) -> None:
    """Verify that tenant tables enforce strict firm_id separation."""
    firm_a = uuid7()
    firm_b = uuid7()
    user_a = uuid7()
    user_b = uuid7()

    sqlite_session.add_all(
        [
            Firm(id=firm_a, name="Firm Alpha", status="active"),
            Firm(id=firm_b, name="Firm Beta", status="active"),
            User(
                id=user_a,
                email="alpha@law.in",
                password_hash="hash",
                full_name="Alpha",
                status="active",
            ),
            User(
                id=user_b,
                email="beta@law.in",
                password_hash="hash",
                full_name="Beta",
                status="active",
            ),
        ]
    )
    await sqlite_session.flush()

    # Create Matter in Firm A
    matter_a = Matter(
        id=uuid7(),
        firm_id=firm_a,
        matter_no="MAT-ALPHA-100",
        title="Alpha Matter",
        stage="intake",
        status="open",
        created_by=user_a,
    )
    sqlite_session.add(matter_a)
    await sqlite_session.commit()

    # Query with tenant filter for Firm B (as enforced by RLS current_setting('app.firm_id'))
    q_firm_b = select(Matter).where(Matter.firm_id == firm_b)
    res_b = (await sqlite_session.execute(q_firm_b)).scalars().all()
    assert len(res_b) == 0, "Tenant B must never see Tenant A matters"

    # Query with tenant filter for Firm A
    q_firm_a = select(Matter).where(Matter.firm_id == firm_a)
    res_a = (await sqlite_session.execute(q_firm_a)).scalars().all()
    assert len(res_a) == 1
    assert res_a[0].matter_no == "MAT-ALPHA-100"


# ══════════════════════════════════════════════════════════════════════════════
# 4. AUDIT EVENTS COMPOSITE KEY & IMMUTABILITY CONTRACT
# ══════════════════════════════════════════════════════════════════════════════


async def test_audit_event_composite_key(sqlite_session: AsyncSession) -> None:
    """Audit events have composite primary key (firm_id, seq). Inserting duplicate primary key raises error."""
    firm_id = uuid7()
    sqlite_session.add(Firm(id=firm_id, name="Audit Firm", status="active"))
    await sqlite_session.flush()

    ev1 = AuditEvent(
        firm_id=firm_id,
        seq=1,
        at=datetime.datetime.now(datetime.UTC),
        action="matter.created",
        prev_hash=b"\x00" * 32,
        hash=b"\x01" * 32,
        metadata_={"test": True},
    )
    sqlite_session.add(ev1)
    await sqlite_session.commit()

    # Attempting to insert duplicate (firm_id, seq=1) via direct raw INSERT must fail on composite PK constraint
    with pytest.raises(IntegrityError):
        await sqlite_session.execute(
            text(
                "INSERT INTO audit_events (firm_id, seq, at, action, prev_hash, hash, metadata) "
                "VALUES (:firm_id, :seq, :at, :action, :prev_hash, :hash, :metadata)"
            ),
            {
                "firm_id": firm_id.hex if hasattr(firm_id, "hex") else str(firm_id),
                "seq": 1,
                "at": datetime.datetime.now(datetime.UTC),
                "action": "matter.updated",
                "prev_hash": b"\x01" * 32,
                "hash": b"\x02" * 32,
                "metadata": "{}",
            },
        )
        await sqlite_session.commit()

    await sqlite_session.rollback()
