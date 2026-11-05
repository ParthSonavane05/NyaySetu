"""
FastAPI dependencies for the Matters module.

Key: require_matter_access — returns 404 (not 403) for out-of-scope access.
See BRAIN.md D-05.
"""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import Depends, Header
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import not_found
from app.db.engine import get_db
from app.modules.matters.models import Matter, MatterMember


# ---------------------------------------------------------------------------
# Stub current-user dependency
# (Real JWT auth wired in P01 — here we use a header stub for P06 scope)
# ---------------------------------------------------------------------------

class CurrentUser:
    def __init__(
        self,
        user_id: uuid.UUID,
        firm_id: uuid.UUID,
        role: str,
        all_matters_access: bool = False,
    ) -> None:
        self.user_id = user_id
        self.firm_id = firm_id
        self.role = role
        self.all_matters_access = all_matters_access

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"

    @property
    def can_see_all_matters(self) -> bool:
        return self.is_admin or self.all_matters_access


async def get_current_user(
    x_user_id: Annotated[str, Header()] = str(uuid.uuid4()),
    x_firm_id: Annotated[str, Header()] = str(uuid.uuid4()),
    x_role: Annotated[str, Header()] = "associate",
    x_all_matters: Annotated[str, Header()] = "false",
) -> CurrentUser:
    """Stub dependency — replace with real JWT decode in P01 integration."""
    try:
        return CurrentUser(
            user_id=uuid.UUID(x_user_id),
            firm_id=uuid.UUID(x_firm_id),
            role=x_role,
            all_matters_access=x_all_matters.lower() == "true",
        )
    except ValueError:
        raise not_found("Invalid user context")


# ---------------------------------------------------------------------------
# require_matter_access
# ---------------------------------------------------------------------------

async def require_matter_access(
    matter_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
) -> Matter:
    """
    Load a matter and verify the current user may access it.

    Access rules (BRAIN.md §6):
      - admin → any matter in firm
      - partner with all_matters_access → any matter in firm
      - others → only matters where they are a MatterMember

    Returns 404 for both "not found" and "not a member" (D-05).
    """
    result = await db.execute(
        select(Matter).where(
            Matter.id == matter_id,
            Matter.firm_id == current_user.firm_id,
        )
    )
    matter = result.scalar_one_or_none()
    if matter is None:
        raise not_found()

    if current_user.can_see_all_matters:
        return matter

    # Check membership
    mem_result = await db.execute(
        select(MatterMember).where(
            MatterMember.matter_id == matter_id,
            MatterMember.user_id == current_user.user_id,
        )
    )
    if mem_result.scalar_one_or_none() is None:
        raise not_found()  # D-05: 404 not 403

    return matter
