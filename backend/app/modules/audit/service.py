"""Audit service: tamper-evident, hash-chained, append-only event log (M2).

Design
------
- Per-firm **gapless** monotonic `seq` obtained inside the same transaction
  using `pg_advisory_xact_lock` on PostgreSQL or a simple MAX()+1 on SQLite
  (test database).
- Each event stores `hash = SHA-256(prev_hash ‖ canonical_json(fields))`.
  `prev_hash` for `seq == 1` is 32 null bytes.
- Canonical JSON: sorted keys, ISO-8601 UTC datetimes, UUID as strings.
- Nightly Celery job writes `audit_anchors`.
"""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

import structlog
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models import AuditAnchor, AuditEvent

logger = structlog.get_logger("app.modules.audit")

# Sentinel prev_hash for the first event in a firm's log
_GENESIS_HASH = b"\x00" * 32


def _canonical_json(fields: dict[str, Any]) -> bytes:
    """Return deterministic UTF-8 JSON for a canonical event fields dict."""

    def _serialize(v: Any) -> Any:
        if isinstance(v, UUID):
            return str(v)
        if isinstance(v, datetime):
            # Always UTC ISO-8601 with explicit timezone marker
            if v.tzinfo is None:
                v = v.replace(tzinfo=UTC)
            return v.isoformat()
        if isinstance(v, dict):
            return {k: _serialize(val) for k, val in sorted(v.items())}
        return v

    ordered = {k: _serialize(v) for k, v in sorted(fields.items())}
    return json.dumps(ordered, ensure_ascii=False, separators=(",", ":")).encode()


def _compute_hash(prev_hash: bytes, canonical: bytes) -> bytes:
    return hashlib.sha256(prev_hash + canonical).digest()


_FORBIDDEN_METADATA_KEYS = frozenset(
    {
        "password",
        "password_hash",
        "token",
        "secret",
        "otp",
        "access_token",
        "refresh_token",
        "totp_secret",
        "recovery_code",
        "pii",
    }
)


def _sanitise_metadata(meta: dict[str, Any] | None) -> dict[str, Any]:
    """Strip any keys that could carry secrets or PII from metadata."""
    if not meta:
        return {}
    return {k: v for k, v in meta.items() if k.lower() not in _FORBIDDEN_METADATA_KEYS}


class AuditService:
    """Core audit recorder.  Must be called inside the caller's transaction."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    # ── Internal helpers ──────────────────────────────────────────────────────

    async def _next_seq_and_prev_hash(self, firm_id: UUID) -> tuple[int, bytes]:
        """Return (next_seq, prev_hash) atomically within the current transaction.

        On PostgreSQL we acquire a transaction-scoped advisory lock keyed on a
        hash of the firm_id string so that concurrent inserts for the same firm
        are serialised.  SQLite (used in tests) doesn't support advisory locks —
        there we simply take the MAX and increment.
        """
        dialect = self.db.bind.dialect.name if self.db.bind else "sqlite"  # type: ignore[union-attr]

        if dialect == "postgresql":
            # Advisory lock is automatically released at transaction end
            await self.db.execute(
                text("SELECT pg_advisory_xact_lock(hashtext(:firm_id))"),
                {"firm_id": str(firm_id)},
            )

        result = await self.db.execute(
            text(
                "SELECT COALESCE(MAX(seq), 0) + 1, "
                "COALESCE(MAX(seq), 0) "
                "FROM audit_events WHERE firm_id = :firm_id"
            ),
            {"firm_id": str(firm_id)},
        )
        row = result.fetchone()
        next_seq: int = row[0]  # type: ignore[index]
        max_seq: int = row[1]  # type: ignore[index]

        if max_seq == 0:
            prev_hash = _GENESIS_HASH
        else:
            # Fetch last hash in this firm's chain
            hash_result = await self.db.execute(
                text(
                    "SELECT hash FROM audit_events "
                    "WHERE firm_id = :firm_id AND seq = :seq"
                ),
                {"firm_id": str(firm_id), "seq": max_seq},
            )
            prev_hash_row = hash_result.fetchone()
            prev_hash = prev_hash_row[0] if prev_hash_row else _GENESIS_HASH  # type: ignore[index]

        return next_seq, prev_hash

    # ── Public API ────────────────────────────────────────────────────────────

    async def record(
        self,
        *,
        firm_id: UUID,
        actor_id: UUID | None,
        actor_role: str | None,
        action: str,
        resource_type: str | None = None,
        resource_id: UUID | None = None,
        matter_id: UUID | None = None,
        ip: str | None = None,
        user_agent: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> AuditEvent:
        """Append one audit event inside the **caller's** transaction."""
        safe_meta = _sanitise_metadata(metadata)
        at = datetime.now(UTC)

        next_seq, prev_hash = await self._next_seq_and_prev_hash(firm_id)

        canonical_fields: dict[str, Any] = {
            "seq": next_seq,
            "at": at.isoformat(),
            "actor_id": str(actor_id) if actor_id else None,
            "actor_role": actor_role,
            "action": action,
            "resource_type": resource_type,
            "resource_id": str(resource_id) if resource_id else None,
            "matter_id": str(matter_id) if matter_id else None,
            "metadata": safe_meta,
        }
        canonical = _canonical_json(canonical_fields)
        new_hash = _compute_hash(prev_hash, canonical)

        event = AuditEvent(
            firm_id=firm_id,
            seq=next_seq,
            at=at,
            actor_id=actor_id,
            actor_role=actor_role,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            matter_id=matter_id,
            ip=ip,
            user_agent=user_agent,
            metadata_=safe_meta,
            prev_hash=prev_hash,
            hash=new_hash,
        )
        self.db.add(event)
        await self.db.flush()
        return event

    async def verify_chain(
        self,
        firm_id: UUID,
        from_seq: int = 1,
        to_seq: int | None = None,
    ) -> dict[str, Any]:
        """Re-derive every hash in [from_seq, to_seq] and report tampering."""
        if to_seq is None:
            max_result = await self.db.execute(
                select(func.max(AuditEvent.seq)).where(AuditEvent.firm_id == firm_id)
            )
            to_seq = max_result.scalar() or 0

        if to_seq == 0:
            return {"ok": True, "verified_count": 0, "first_tampered_seq": None,
                    "from_seq": from_seq, "to_seq": to_seq}

        rows_result = await self.db.execute(
            select(AuditEvent)
            .where(
                AuditEvent.firm_id == firm_id,
                AuditEvent.seq >= from_seq,
                AuditEvent.seq <= to_seq,
            )
            .order_by(AuditEvent.seq)
        )
        events = rows_result.scalars().all()

        verified_count = 0
        first_tampered: int | None = None

        for evt in events:
            canonical_fields = {
                "seq": evt.seq,
                "at": evt.at.isoformat() if evt.at.tzinfo else evt.at.replace(tzinfo=UTC).isoformat(),
                "actor_id": str(evt.actor_id) if evt.actor_id else None,
                "actor_role": evt.actor_role,
                "action": evt.action,
                "resource_type": evt.resource_type,
                "resource_id": str(evt.resource_id) if evt.resource_id else None,
                "matter_id": str(evt.matter_id) if evt.matter_id else None,
                "metadata": evt.metadata_,
            }
            canonical = _canonical_json(canonical_fields)
            expected_hash = _compute_hash(evt.prev_hash, canonical)

            if expected_hash != evt.hash:
                if first_tampered is None:
                    first_tampered = evt.seq
            else:
                if first_tampered is None:
                    verified_count += 1

        return {
            "ok": first_tampered is None,
            "verified_count": verified_count,
            "first_tampered_seq": first_tampered,
            "from_seq": from_seq,
            "to_seq": to_seq,
        }

    async def write_anchor(self, firm_id: UUID) -> AuditAnchor | None:
        """Write an anchor for the current max seq of this firm (nightly job)."""
        max_result = await self.db.execute(
            select(func.max(AuditEvent.seq)).where(AuditEvent.firm_id == firm_id)
        )
        max_seq = max_result.scalar()
        if not max_seq:
            return None

        # Fetch current last hash
        hash_result = await self.db.execute(
            text("SELECT hash FROM audit_events WHERE firm_id = :firm_id AND seq = :seq"),
            {"firm_id": str(firm_id), "seq": max_seq},
        )
        last_hash_row = hash_result.fetchone()
        if not last_hash_row:
            return None

        anchor = AuditAnchor(
            firm_id=firm_id,
            up_to_seq=max_seq,
            hash=last_hash_row[0],
            anchored_at=datetime.now(UTC),
        )
        self.db.add(anchor)
        await self.db.flush()
        return anchor

