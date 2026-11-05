"""Nightly audit chain verification Celery task (M2).

Runs once a day for every active firm; verifies the full chain and writes
an ``AuditAnchor`` recording the last verified seq and its hash.
"""

from __future__ import annotations

import asyncio
from uuid import UUID

import structlog

from app.workers.celery_app import celery_app

logger = structlog.get_logger("app.workers.audit_verify")


def _run_async(coro):  # type: ignore[no-untyped-def]
    """Run a coroutine in a fresh event loop (Celery worker context)."""
    return asyncio.get_event_loop().run_until_complete(coro)


async def _verify_all_firms() -> None:
    from sqlalchemy import select

    from app.core.db import get_session_factory
    from app.core.models import Firm
    from app.modules.audit.service import AuditService

    factory = get_session_factory()

    async with factory() as session:
        async with session.begin():
            firms = (await session.execute(select(Firm).where(Firm.status == "active"))).scalars().all()

    for firm in firms:
        firm_id: UUID = firm.id
        async with factory() as db:
            async with db.begin():
                svc = AuditService(db)
                result = await svc.verify_chain(firm_id)
                if not result["ok"]:
                    logger.error(
                        "audit_chain_tampered",
                        firm_id=str(firm_id),
                        first_tampered_seq=result["first_tampered_seq"],
                    )
                else:
                    anchor = await svc.write_anchor(firm_id)
                    logger.info(
                        "audit_anchor_written",
                        firm_id=str(firm_id),
                        up_to_seq=anchor.up_to_seq if anchor else None,
                        verified_count=result["verified_count"],
                    )


@celery_app.task(name="audit.nightly_verify", bind=True, max_retries=3)
def nightly_audit_verify(self) -> None:  # type: ignore[no-untyped-def]
    """Celery task: verify every firm's audit chain and write anchors."""
    try:
        _run_async(_verify_all_firms())
    except Exception as exc:
        logger.exception("audit_verify_failed", error=str(exc))
        raise self.retry(exc=exc, countdown=300) from exc
