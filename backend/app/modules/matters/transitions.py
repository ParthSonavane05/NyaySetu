"""
Stage transition table for Matter.stage (see BRAIN.md §7).

Allowed forward transitions (no note required):
  INTAKE → DUE_DILIGENCE → DRAFTING → REVIEW → FILED → CLOSED

Backward transitions (note required):
  Any reverse of the above forward chain.

ARCHIVED is only reachable via the /archive endpoint, NOT via /transition.
"""

from __future__ import annotations

from app.modules.matters.models import MatterStage

# Forward adjacency — key → set of allowed next stages
_FORWARD: dict[MatterStage, set[MatterStage]] = {
    MatterStage.INTAKE: {MatterStage.DUE_DILIGENCE},
    MatterStage.DUE_DILIGENCE: {MatterStage.DRAFTING},
    MatterStage.DRAFTING: {MatterStage.REVIEW},
    MatterStage.REVIEW: {MatterStage.FILED},
    MatterStage.FILED: {MatterStage.CLOSED},
    MatterStage.CLOSED: set(),
    MatterStage.ARCHIVED: set(),
}

# Backward adjacency (reverse of forward)
_BACKWARD: dict[MatterStage, set[MatterStage]] = {
    MatterStage.DUE_DILIGENCE: {MatterStage.INTAKE},
    MatterStage.DRAFTING: {MatterStage.DUE_DILIGENCE},
    MatterStage.REVIEW: {MatterStage.DRAFTING},
    MatterStage.FILED: {MatterStage.REVIEW},
    MatterStage.CLOSED: {MatterStage.FILED},
    MatterStage.INTAKE: set(),
    MatterStage.ARCHIVED: set(),
}


def is_valid_transition(from_stage: MatterStage, to_stage: MatterStage) -> bool:
    """Return True if the transition is allowed (forward OR backward)."""
    if to_stage == MatterStage.ARCHIVED:
        return False  # ARCHIVED only via /archive endpoint
    return (
        to_stage in _FORWARD.get(from_stage, set())
        or to_stage in _BACKWARD.get(from_stage, set())
    )


def is_backward(from_stage: MatterStage, to_stage: MatterStage) -> bool:
    """Return True if the transition is a backward move (note required)."""
    return to_stage in _BACKWARD.get(from_stage, set())


def transition_error_message(from_stage: MatterStage, to_stage: MatterStage) -> str:
    allowed = _FORWARD.get(from_stage, set()) | _BACKWARD.get(from_stage, set())
    allowed_names = sorted(s.value for s in allowed) if allowed else ["(none)"]
    return (
        f"Cannot transition from {from_stage.value} to {to_stage.value}. "
        f"Allowed targets: {', '.join(allowed_names)}"
    )
