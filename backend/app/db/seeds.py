"""Idempotent seed data for NyaySetu MVP.

Seeds:
1. Reference Masters (Forums, Statutes, Sections, Document Types) flagged `needs_review=True`.
2. Canonical Demo Fixture (BRAIN.md section 7):
   - Firm: Mehta & Associates
   - Users: 4 role users (Partner, Associate, Paralegal, Researcher) with Argon2id passwords
   - Matter: MAT-2026-0809 (Sec. 203 appeal before Dy. Collector Bavla)
   - Land Parcel: Survey 142/A, Khata 247, Moje Bavla, Taluka Bavla, District Ahmedabad (1-22-00 = 12,200 sqm)
   - Title Events:
     - 410 (18-05-1996 ancestral partition)
     - 621 (04-11-2008 registered sale deed Rs 32,50,000)
     - 809 (14-07-2017 mutation certified after notice, disputed, challenged 08-01-2026)
     - 842 (14-08-2018 SBI Bavla agricultural mortgage Rs 8,50,000, active)
   - Encumbrance: SBI Bavla mortgage
   - Hearing: 2026-11-18 11:30 at Dy. Collector Bavla
   - Document: 7/12 extract and mutation entry
"""

from __future__ import annotations

import asyncio
import hashlib
from datetime import UTC, date, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.auth_crypto import hash_password
from app.core.config import get_settings
from app.core.models import (
    Document,
    DocumentPage,
    DocumentVersion,
    Encumbrance,
    Firm,
    FirmMembership,
    Forum,
    Hearing,
    LandParcel,
    Matter,
    MatterMember,
    MatterParty,
    MatterStage,
    Party,
    Statute,
    StatuteSection,
    TitleEvent,
    TitleEventLink,
    TitleFlag,
    User,
)

# Deterministic IDs for idempotent seeds so running multiple times is safe and predictable
MEHTA_FIRM_ID = UUID("018f0000-0000-7000-8000-000000000001")
PARTNER_USER_ID = UUID("018f0000-0000-7000-8000-000000000011")
ASSOCIATE_USER_ID = UUID("018f0000-0000-7000-8000-000000000012")
PARALEGAL_USER_ID = UUID("018f0000-0000-7000-8000-000000000013")
RESEARCHER_USER_ID = UUID("018f0000-0000-7000-8000-000000000014")

DY_COLLECTOR_FORUM_ID = UUID("018f0000-0000-7000-8000-000000000101")
MAMLATDAR_FORUM_ID = UUID("018f0000-0000-7000-8000-000000000102")
COLLECTOR_AHM_FORUM_ID = UUID("018f0000-0000-7000-8000-000000000103")
SSRD_FORUM_ID = UUID("018f0000-0000-7000-8000-000000000104")
GRT_FORUM_ID = UUID("018f0000-0000-7000-8000-000000000105")
GUJARAT_HC_FORUM_ID = UUID("018f0000-0000-7000-8000-000000000106")

BLRC_STATUTE_ID = UUID("018f0000-0000-7000-8000-000000000201")
MATTER_809_ID = UUID("018f0000-0000-7000-8000-000000000301")
PARCEL_142A_ID = UUID("018f0000-0000-7000-8000-000000000401")

EVENT_410_ID = UUID("018f0000-0000-7000-8000-000000000501")
EVENT_621_ID = UUID("018f0000-0000-7000-8000-000000000502")
EVENT_809_ID = UUID("018f0000-0000-7000-8000-000000000503")
EVENT_842_ID = UUID("018f0000-0000-7000-8000-000000000504")


async def seed_reference_data(session: AsyncSession) -> None:
    """Idempotently seed master reference data."""
    # 1. Forums
    forums_data = [
        {
            "id": DY_COLLECTOR_FORUM_ID,
            "code": "DY_COLLECTOR_BAVLA",
            "name": "Court of the Deputy Collector (Prant Officer), Dholka-Bavla",
            "level": "subdivision",
            "state": "GJ",
            "needs_review": True,
        },
        {
            "id": MAMLATDAR_FORUM_ID,
            "code": "MAMLATDAR_BAVLA",
            "name": "Court of the Mamlatdar, Bavla",
            "level": "taluka",
            "state": "GJ",
            "needs_review": True,
        },
        {
            "id": COLLECTOR_AHM_FORUM_ID,
            "code": "COLLECTOR_AHM",
            "name": "Court of the Collector, Ahmedabad",
            "level": "district",
            "state": "GJ",
            "needs_review": True,
        },
        {
            "id": SSRD_FORUM_ID,
            "code": "SSRD",
            "name": "Special Secretary (Revenue Department), Gujarat",
            "level": "state",
            "state": "GJ",
            "needs_review": True,
        },
        {
            "id": GRT_FORUM_ID,
            "code": "GRT",
            "name": "Gujarat Revenue Tribunal",
            "level": "tribunal",
            "state": "GJ",
            "needs_review": True,
        },
        {
            "id": GUJARAT_HC_FORUM_ID,
            "code": "GUJARAT_HC",
            "name": "High Court of Gujarat at Ahmedabad",
            "level": "high_court",
            "state": "GJ",
            "needs_review": True,
        },
    ]

    for f in forums_data:
        existing = await session.get(Forum, f["id"])
        if not existing:
            session.add(Forum(**f))

    # 2. Statutes and Sections
    existing_statute = await session.get(Statute, BLRC_STATUTE_ID)
    if not existing_statute:
        statute = Statute(
            id=BLRC_STATUTE_ID,
            short_title="Bombay Land Revenue Code, 1879",
            official_title="The Bombay Land Revenue Code, 1879 (Bombay Act No. V of 1879)",
            year=1879,
            jurisdiction="Gujarat",
            source_url="https://indiacode.nic.in",
            needs_review=True,
        )
        session.add(statute)

    sections_data = [
        {
            "section_number": "135D",
            "title": "Notice of mutation register entries and certification",
            "text_content": "[needs_review] Statutory procedure for notice and hearing before mutation certification.",
        },
        {
            "section_number": "203",
            "title": "Appeal to lie from any order passed by a revenue officer to his superior",
            "text_content": "[needs_review] Right of appeal against revenue officer order to higher revenue authority.",
        },
        {
            "section_number": "204",
            "title": "Stay of proceedings on appeal",
            "text_content": "[needs_review] Stay power of appellate revenue authority during appeal pendency.",
        },
        {
            "section_number": "205",
            "title": "Limitation of appeals",
            "text_content": "[needs_review] Limitation periods for revenue appeals (typically 60 days).",
        },
        {
            "section_number": "211",
            "title": "Power of State Government and certain revenue officers to call for and examine records",
            "text_content": "[needs_review] Revisional powers of State Government, Collector and designated authorities.",
        },
    ]

    for s in sections_data:
        res = await session.execute(
            select(StatuteSection).where(
                StatuteSection.statute_id == BLRC_STATUTE_ID,
                StatuteSection.section_number == s["section_number"],
            )
        )
        if not res.scalar_one_or_none():
            session.add(
                StatuteSection(
                    statute_id=BLRC_STATUTE_ID,
                    section_number=s["section_number"],
                    title=s["title"],
                    text_content=s["text_content"],
                    needs_review=True,
                )
            )

    await session.flush()


async def seed_canonical_demo_fixture(session: AsyncSession) -> None:
    """Seed the canonical demo fixture from BRAIN.md Section 7."""
    demo_password_hash = hash_password("DemoPassword123!")

    # 1. Firm: Mehta & Associates
    firm = await session.get(Firm, MEHTA_FIRM_ID)
    if not firm:
        firm = Firm(
            id=MEHTA_FIRM_ID,
            name="Mehta & Associates",
            status="active",
            region="ap-south-1",
            kms_key_id="alias/nyaysetu-default",
            retention_default_days=2555,  # 7 years
            settings={"state": "GJ", "primary_jurisdiction": "Revenue"},
        )
        session.add(firm)
        await session.flush()

    # 2. Four role users
    users_data = [
        {
            "id": PARTNER_USER_ID,
            "email": "partner@mehtalaw.in",
            "full_name": "Adv. Rajesh Mehta",
            "role": "partner",
            "all_matters_access": True,
        },
        {
            "id": ASSOCIATE_USER_ID,
            "email": "associate@mehtalaw.in",
            "full_name": "Adv. Sneha Patel",
            "role": "associate",
            "all_matters_access": False,
        },
        {
            "id": PARALEGAL_USER_ID,
            "email": "paralegal@mehtalaw.in",
            "full_name": "Ketan Dave",
            "role": "paralegal",
            "all_matters_access": False,
        },
        {
            "id": RESEARCHER_USER_ID,
            "email": "researcher@mehtalaw.in",
            "full_name": "Pooja Trivedi",
            "role": "researcher",
            "all_matters_access": False,
        },
    ]

    for u in users_data:
        existing_user = await session.get(User, u["id"])
        if not existing_user:
            user = User(
                id=u["id"],
                email=u["email"],
                password_hash=demo_password_hash,
                full_name=u["full_name"],
                locale="gu",
                mfa_enabled=False,
                status="active",
            )
            session.add(user)
            await session.flush()

        res_membership = await session.execute(
            select(FirmMembership).where(
                FirmMembership.firm_id == MEHTA_FIRM_ID,
                FirmMembership.user_id == u["id"],
            )
        )
        if not res_membership.scalar_one_or_none():
            session.add(
                FirmMembership(
                    firm_id=MEHTA_FIRM_ID,
                    user_id=u["id"],
                    role=u["role"],
                    all_matters_access=u["all_matters_access"],
                    status="active",
                )
            )

    # 3. Client Party: Patel Rameshchandra K.
    client_party_id = UUID("018f0000-0000-7000-8000-000000000302")
    existing_party = await session.get(Party, client_party_id)
    if not existing_party:
        party = Party(
            id=client_party_id,
            firm_id=MEHTA_FIRM_ID,
            type="individual",
            name_enc="[ENC:Patel Rameshchandra K.]",
            mobile_enc="[ENC:+919876543210]",
            address_enc="[ENC:Moje Bavla, Taluka Bavla, District Ahmedabad]",
            name_norm="patel rameshchandra k",
        )
        session.add(party)
        await session.flush()

    # 4. Matter MAT-2026-0809
    matter = await session.get(Matter, MATTER_809_ID)
    if not matter:
        matter = Matter(
            id=MATTER_809_ID,
            firm_id=MEHTA_FIRM_ID,
            matter_no="MAT-2026-0809",
            title="Sec. 203 appeal before Dy. Collector (Bavla)",
            forum_id=DY_COLLECTOR_FORUM_ID,
            statute_id=BLRC_STATUTE_ID,
            stage="drafting",
            status="open",
            opened_at=datetime(2026, 1, 15, 10, 0, 0, tzinfo=UTC),
            created_by=PARTNER_USER_ID,
        )
        session.add(matter)
        await session.flush()

        # Members: Partner & Associate
        session.add(
            MatterMember(
                matter_id=MATTER_809_ID,
                user_id=PARTNER_USER_ID,
                firm_id=MEHTA_FIRM_ID,
                matter_role="lead",
            )
        )
        session.add(
            MatterMember(
                matter_id=MATTER_809_ID,
                user_id=ASSOCIATE_USER_ID,
                firm_id=MEHTA_FIRM_ID,
                matter_role="member",
            )
        )
        session.add(
            MatterParty(
                matter_id=MATTER_809_ID,
                party_id=client_party_id,
                firm_id=MEHTA_FIRM_ID,
                side="our_client",
            )
        )
        session.add(
            MatterStage(
                matter_id=MATTER_809_ID,
                firm_id=MEHTA_FIRM_ID,
                from_stage="title",
                to_stage="drafting",
                transitioned_by=PARTNER_USER_ID,
                note="Title chain completed and flagged; drafting appeal grounds.",
            )
        )

    # 5. Land Parcel: Survey 142/A, Khata 247
    parcel = await session.get(LandParcel, PARCEL_142A_ID)
    if not parcel:
        parcel = LandParcel(
            id=PARCEL_142A_ID,
            matter_id=MATTER_809_ID,
            firm_id=MEHTA_FIRM_ID,
            village="Bavla",
            taluka="Bavla",
            district="Ahmedabad",
            survey_no="142/A",
            khata_no="247",
            area_raw="1-22-00",
            area_sqm=12200,
        )
        session.add(parcel)
        await session.flush()

    # 6. Title Events: 410, 621, 809, 842
    title_events = [
        {
            "id": EVENT_410_ID,
            "parcel_id": PARCEL_142A_ID,
            "firm_id": MEHTA_FIRM_ID,
            "event_type": "partition",
            "entry_no": "410",
            "event_date": date(1996, 5, 18),
            "certification_date": date(1996, 7, 2),
            "parties": [{"name": "Ancestral Partition", "role": "co-sharers"}],
            "area_sqm": 12200,
            "status": "superseded",
        },
        {
            "id": EVENT_621_ID,
            "parcel_id": PARCEL_142A_ID,
            "firm_id": MEHTA_FIRM_ID,
            "event_type": "sale",
            "entry_no": "621",
            "event_date": date(2008, 11, 4),
            "certification_date": date(2008, 12, 10),
            "parties": [{"buyer": "Patel Rameshchandra K.", "consideration_inr": 3250000}],
            "area_sqm": 12200,
            "status": "superseded",
        },
        {
            "id": EVENT_809_ID,
            "parcel_id": PARCEL_142A_ID,
            "firm_id": MEHTA_FIRM_ID,
            "event_type": "mutation",
            "entry_no": "809",
            "event_date": date(2017, 7, 14),
            "certification_date": date(2017, 9, 5),
            "parties": [
                {"description": "Mutation certified after 135D notice; challenged 2026-01-08"}
            ],
            "area_sqm": 12200,
            "status": "disputed",
        },
        {
            "id": EVENT_842_ID,
            "parcel_id": PARCEL_142A_ID,
            "firm_id": MEHTA_FIRM_ID,
            "event_type": "mortgage",
            "entry_no": "842",
            "event_date": date(2018, 8, 14),
            "certification_date": date(2018, 9, 20),
            "parties": [{"holder": "State Bank of India, Bavla Branch", "amount": 850000}],
            "area_sqm": 12200,
            "status": "active",
        },
    ]

    for ev in title_events:
        existing_ev = await session.get(TitleEvent, ev["id"])
        if not existing_ev:
            session.add(TitleEvent(**ev))

    await session.flush()

    # Link events sequentially (410 -> 621 -> 809 -> 842)
    links = [
        (EVENT_410_ID, EVENT_621_ID),
        (EVENT_621_ID, EVENT_809_ID),
        (EVENT_809_ID, EVENT_842_ID),
    ]
    for p_id, c_id in links:
        res = await session.execute(
            select(TitleEventLink).where(
                TitleEventLink.parent_event_id == p_id,
                TitleEventLink.child_event_id == c_id,
            )
        )
        if not res.scalar_one_or_none():
            session.add(TitleEventLink(parent_event_id=p_id, child_event_id=c_id))

    # 7. Encumbrance: SBI mortgage
    enc_id = UUID("018f0000-0000-7000-8000-000000000601")
    existing_enc = await session.get(Encumbrance, enc_id)
    if not existing_enc:
        session.add(
            Encumbrance(
                id=enc_id,
                parcel_id=PARCEL_142A_ID,
                firm_id=MEHTA_FIRM_ID,
                kind="mortgage",
                holder="State Bank of India, Bavla Branch",
                amount=850000.00,
                created_event_id=EVENT_842_ID,
            )
        )

    # 8. Title Flag on disputed entry 809
    flag_id = UUID("018f0000-0000-7000-8000-000000000602")
    existing_flag = await session.get(TitleFlag, flag_id)
    if not existing_flag:
        session.add(
            TitleFlag(
                id=flag_id,
                parcel_id=PARCEL_142A_ID,
                firm_id=MEHTA_FIRM_ID,
                rule_code="FLAG_DISPUTED_MUTATION",
                severity="warning",
                message="Mutation Entry No. 809 subject to challenge under Sec. 203 appeal (impugned order dt 2026-01-08).",
                event_ids=[str(EVENT_809_ID)],
            )
        )

    # 9. Hearing: 2026-11-18 11:30
    hearing_id = UUID("018f0000-0000-7000-8000-000000000701")
    existing_hearing = await session.get(Hearing, hearing_id)
    if not existing_hearing:
        session.add(
            Hearing(
                id=hearing_id,
                matter_id=MATTER_809_ID,
                firm_id=MEHTA_FIRM_ID,
                forum_id=DY_COLLECTOR_FORUM_ID,
                hearing_at=datetime(2026, 11, 18, 11, 30, 0, tzinfo=UTC),
                board_item="Item No. 14",
                stage="Arguments on Stay Application",
                outcome=None,
                source="manual",
            )
        )

    # 10. Sample Document: 7/12 extract
    doc_id = UUID("018f0000-0000-7000-8000-000000000801")
    existing_doc = await session.get(Document, doc_id)
    if not existing_doc:
        doc = Document(
            id=doc_id,
            matter_id=MATTER_809_ID,
            firm_id=MEHTA_FIRM_ID,
            doc_type="7_12",
            source="client",
            certified=True,
            title="Village Form 7/12 - Bavla Survey 142/A",
        )
        session.add(doc)
        await session.flush()

        doc_ver_id = UUID("018f0000-0000-7000-8000-000000000802")
        fake_sha256 = hashlib.sha256(b"DEMO_7_12_DOCUMENT_CONTENT").digest()
        doc_ver = DocumentVersion(
            id=doc_ver_id,
            document_id=doc_id,
            firm_id=MEHTA_FIRM_ID,
            version_no=1,
            storage_key=f"firms/{MEHTA_FIRM_ID}/matters/{MATTER_809_ID}/docs/{doc_id}/v1.pdf",
            sha256=fake_sha256,
            size_bytes=245760,
            mime="application/pdf",
            page_count=1,
            scan_status="clean",
            uploaded_by=PARALEGAL_USER_ID,
        )
        session.add(doc_ver)
        await session.flush()

        doc.current_version_id = doc_ver_id

        doc_page_id = UUID("018f0000-0000-7000-8000-000000000803")
        doc_page = DocumentPage(
            id=doc_page_id,
            version_id=doc_ver_id,
            firm_id=MEHTA_FIRM_ID,
            page_no=1,
            image_key=f"firms/{MEHTA_FIRM_ID}/matters/{MATTER_809_ID}/pages/{doc_page_id}.png",
        )
        session.add(doc_page)

    await session.commit()


async def run_all_seeds(session: AsyncSession) -> None:
    """Run master reference data and demo fixture seeds idempotently."""
    await seed_reference_data(session)
    await seed_canonical_demo_fixture(session)


async def main() -> None:
    settings = get_settings()
    engine = create_async_engine(settings.database_url, echo=False)
    async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async with async_session() as session:
        # Seeding NyaySetu MVP database
        await run_all_seeds(session)

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
