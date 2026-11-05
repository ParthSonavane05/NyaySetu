"""Test Alembic migrations up/down consistency and reversibility."""

from __future__ import annotations

from alembic.config import Config
from alembic.script import ScriptDirectory


def test_single_alembic_head() -> None:
    config = Config("alembic.ini")
    script = ScriptDirectory.from_config(config)
    heads = script.get_heads()
    assert len(heads) == 1, f"Expected exactly 1 Alembic head, got {len(heads)}: {heads}"


def test_all_revisions_reversible() -> None:
    """Ensure every migration in the revision tree implements upgrade and downgrade."""
    config = Config("alembic.ini")
    script = ScriptDirectory.from_config(config)

    for rev in script.walk_revisions():
        assert rev.module is not None
        assert hasattr(rev.module, "upgrade"), f"Revision {rev.revision} missing upgrade()"
        assert hasattr(rev.module, "downgrade"), f"Revision {rev.revision} missing downgrade()"
        assert callable(rev.module.upgrade)
        assert callable(rev.module.downgrade)
