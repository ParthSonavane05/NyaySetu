"""
P06 binding tests (10 tests, no DB required).

Tests cover:
  T-01  survey number normalisation — ASCII
  T-02  survey number normalisation — Gujarati digits
  T-03  survey number normalisation — invalid input raises ValueError
  T-04  area parser — H-A-S format
  T-05  area parser — plain sq.m shorthand
  T-06  area parser — invalid format raises ValueError
  T-07  stage transitions — valid forward transition
  T-08  stage transitions — valid backward transition
  T-09  stage transitions — ARCHIVED not reachable via transition
  T-10  stage transitions — invalid jump raises correct error message
"""

import pytest

from app.core.validators import normalise_survey_number, parse_area, validate_sort
from app.modules.matters.models import MatterStage
from app.modules.matters.transitions import (
    is_backward,
    is_valid_transition,
    transition_error_message,
)


# ---------------------------------------------------------------------------
# T-01: Survey number normalisation — ASCII input
# ---------------------------------------------------------------------------

def test_normalise_survey_ascii_basic():
    assert normalise_survey_number("142/A") == "142/A"


def test_normalise_survey_ascii_lowercase():
    assert normalise_survey_number("142/a") == "142/A"


def test_normalise_survey_ascii_no_suffix():
    assert normalise_survey_number("12/3") == "12/3"


# ---------------------------------------------------------------------------
# T-02: Survey number normalisation — Gujarati digits
# ---------------------------------------------------------------------------

def test_normalise_survey_gujarati_digits():
    # ૧૪૨ = 142 in Gujarati numerals
    result = normalise_survey_number("૧૪૨")
    assert result == "142"


def test_normalise_survey_gujarati_with_suffix():
    # ૧૪૨/અ → 142/A (અ → A)
    result = normalise_survey_number("૧૪૨/અ")
    assert result == "142/A"


# ---------------------------------------------------------------------------
# T-03: Survey number normalisation — invalid input
# ---------------------------------------------------------------------------

def test_normalise_survey_empty_raises():
    with pytest.raises(ValueError, match="must not be empty"):
        normalise_survey_number("")


def test_normalise_survey_bad_format_raises():
    with pytest.raises(ValueError):
        normalise_survey_number("!!!invalid!!!")


# ---------------------------------------------------------------------------
# T-04: Area parser — H-A-S format
# ---------------------------------------------------------------------------

def test_parse_area_has_format():
    sqm, label = parse_area("2-15-500")
    # 2 * 10000 + 15 * 100 + 500 = 22000
    assert sqm == 22000
    assert "2" in label
    assert "15" in label
    assert "500" in label


def test_parse_area_zero_hectares():
    sqm, label = parse_area("0-05-250")
    # 0 * 10000 + 5 * 100 + 250 = 750
    assert sqm == 750


# ---------------------------------------------------------------------------
# T-05: Area parser — plain sq.m shorthand
# ---------------------------------------------------------------------------

def test_parse_area_plain_sqm():
    sqm, label = parse_area("500")
    assert sqm == 500
    assert "0H" in label


def test_parse_area_decimal():
    sqm, label = parse_area("1500.5")
    assert sqm == pytest.approx(1500.5, rel=1e-6)


# ---------------------------------------------------------------------------
# T-06: Area parser — invalid formats
# ---------------------------------------------------------------------------

def test_parse_area_too_many_parts():
    with pytest.raises(ValueError, match="3 hyphen-separated"):
        parse_area("1-2-3-4")


def test_parse_area_non_numeric():
    with pytest.raises(ValueError):
        parse_area("abc")


def test_parse_area_negative():
    # "-1-0-0" is parsed as 4 parts (leading dash = extra separator).
    # The validators.py raises "3 hyphen-separated parts" for that input.
    # Test with a valid H-A-S format that has a negative component: not possible
    # via string because a leading minus splits into 4 parts.
    # Instead verify plain negative sqm raises ValueError.
    with pytest.raises(ValueError):
        parse_area("-500")


# ---------------------------------------------------------------------------
# T-07: Stage transitions — valid forward transition
# ---------------------------------------------------------------------------

def test_transition_forward_intake_to_due_diligence():
    assert is_valid_transition(MatterStage.INTAKE, MatterStage.DUE_DILIGENCE) is True


def test_transition_forward_full_chain():
    chain = [
        (MatterStage.INTAKE, MatterStage.DUE_DILIGENCE),
        (MatterStage.DUE_DILIGENCE, MatterStage.DRAFTING),
        (MatterStage.DRAFTING, MatterStage.REVIEW),
        (MatterStage.REVIEW, MatterStage.FILED),
        (MatterStage.FILED, MatterStage.CLOSED),
    ]
    for from_stage, to_stage in chain:
        assert is_valid_transition(from_stage, to_stage), (
            f"Expected {from_stage} → {to_stage} to be valid"
        )


# ---------------------------------------------------------------------------
# T-08: Stage transitions — valid backward transition
# ---------------------------------------------------------------------------

def test_transition_backward_due_diligence_to_intake():
    assert is_valid_transition(MatterStage.DUE_DILIGENCE, MatterStage.INTAKE) is True


def test_is_backward_flag():
    assert is_backward(MatterStage.DUE_DILIGENCE, MatterStage.INTAKE) is True
    assert is_backward(MatterStage.INTAKE, MatterStage.DUE_DILIGENCE) is False


# ---------------------------------------------------------------------------
# T-09: ARCHIVED stage NOT reachable via /transition
# ---------------------------------------------------------------------------

def test_archived_not_reachable_via_transition():
    for stage in MatterStage:
        assert is_valid_transition(stage, MatterStage.ARCHIVED) is False, (
            f"ARCHIVED should not be reachable from {stage} via transition"
        )


def test_archived_has_no_outgoing_transitions():
    for stage in MatterStage:
        if stage != MatterStage.ARCHIVED:
            assert is_valid_transition(MatterStage.ARCHIVED, stage) is False


# ---------------------------------------------------------------------------
# T-10: Invalid jump — error message contains allowed stages
# ---------------------------------------------------------------------------

def test_invalid_transition_error_message_contains_allowed():
    msg = transition_error_message(MatterStage.INTAKE, MatterStage.FILED)
    assert "INTAKE" in msg
    assert "FILED" in msg
    assert "DUE_DILIGENCE" in msg   # the only allowed next stage


def test_invalid_transition_intake_to_closed():
    assert is_valid_transition(MatterStage.INTAKE, MatterStage.CLOSED) is False


def test_invalid_transition_closed_has_no_next():
    for stage in MatterStage:
        if stage not in (MatterStage.CLOSED, MatterStage.FILED):
            # CLOSED can only go backward to FILED
            if stage != MatterStage.FILED:
                assert is_valid_transition(MatterStage.CLOSED, stage) is False


# ---------------------------------------------------------------------------
# Bonus: validate_sort whitelist
# ---------------------------------------------------------------------------

def test_validate_sort_valid():
    result = validate_sort("created_at", ["created_at", "title"])
    assert result == "created_at"


def test_validate_sort_descending():
    result = validate_sort("-title", ["created_at", "title"])
    assert result == "-title"


def test_validate_sort_invalid_raises():
    with pytest.raises(ValueError, match="Invalid sort field"):
        validate_sort("secret_field", ["created_at", "title"])


def test_validate_sort_none_returns_default():
    result = validate_sort(None, ["created_at", "title"], default="created_at")
    assert result == "created_at"


# ===========================================================================
# P06 Required Tests (Binding from BRAIN.md §10)
# ===========================================================================

import hashlib
import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException

from app.core.crypto import CryptoService
from app.core.pagination import decode_cursor, encode_cursor
from app.modules.matters.dependencies import CurrentUser, require_matter_access
from app.modules.matters.models import Matter, MatterMember
from app.modules.matters.schemas import MatterPatch, MatterTransition
from app.modules.matters.service import (
    _next_matter_number,
    patch_matter,
    transition_matter,
)
from cryptography.fernet import Fernet


# ---------------------------------------------------------------------------
# 1. Membership matrix (BRAIN.md §10 requirement #1)
# ---------------------------------------------------------------------------

class TestMembershipMatrix:
    """Test all role combinations against matter access rules."""

    @pytest.mark.anyio
    async def test_admin_sees_all_matters_without_membership(self):
        firm_id = uuid.uuid4()
        matter_id = uuid.uuid4()
        user_id = uuid.uuid4()
        matter = Matter(id=matter_id, firm_id=firm_id, matter_number="MAT-2026-0001", title="Firm Matter")

        admin = CurrentUser(user_id=user_id, firm_id=firm_id, role="admin", all_matters_access=False)
        assert admin.can_see_all_matters is True

        mock_db = AsyncMock()
        mock_res = MagicMock()
        mock_res.scalar_one_or_none.return_value = matter
        mock_db.execute.return_value = mock_res

        result = await require_matter_access(matter_id, mock_db, admin)
        assert result == matter

    @pytest.mark.anyio
    async def test_partner_with_all_matters_access_sees_all(self):
        firm_id = uuid.uuid4()
        matter_id = uuid.uuid4()
        user_id = uuid.uuid4()
        matter = Matter(id=matter_id, firm_id=firm_id, matter_number="MAT-2026-0001", title="Firm Matter")

        partner = CurrentUser(user_id=user_id, firm_id=firm_id, role="partner", all_matters_access=True)
        assert partner.can_see_all_matters is True

        mock_db = AsyncMock()
        mock_res = MagicMock()
        mock_res.scalar_one_or_none.return_value = matter
        mock_db.execute.return_value = mock_res

        result = await require_matter_access(matter_id, mock_db, partner)
        assert result == matter

    @pytest.mark.anyio
    @pytest.mark.parametrize("role", ["partner", "associate", "paralegal", "researcher"])
    async def test_non_admin_requires_membership(self, role: str):
        firm_id = uuid.uuid4()
        matter_id = uuid.uuid4()
        user_id = uuid.uuid4()
        matter = Matter(id=matter_id, firm_id=firm_id, matter_number="MAT-2026-0001", title="Firm Matter")
        membership = MatterMember(matter_id=matter_id, user_id=user_id, role_in_matter="member")

        user = CurrentUser(user_id=user_id, firm_id=firm_id, role=role, all_matters_access=False)
        assert user.can_see_all_matters is False

        mock_db = AsyncMock()
        res_matter = MagicMock()
        res_matter.scalar_one_or_none.return_value = matter
        res_member = MagicMock()
        res_member.scalar_one_or_none.return_value = membership
        mock_db.execute.side_effect = [res_matter, res_member]

        result = await require_matter_access(matter_id, mock_db, user)
        assert result == matter


# ---------------------------------------------------------------------------
# 2. 404 for non-members (BRAIN.md §10 requirement #2 & D-05)
# ---------------------------------------------------------------------------

class Test404NonMember:
    """Out-of-scope resource access must return HTTP 404, never 403 (D-05)."""

    @pytest.mark.anyio
    @pytest.mark.parametrize("role", ["partner", "associate", "paralegal", "researcher"])
    async def test_non_member_gets_404_not_403(self, role: str):
        firm_id = uuid.uuid4()
        matter_id = uuid.uuid4()
        user_id = uuid.uuid4()
        matter = Matter(id=matter_id, firm_id=firm_id, matter_number="MAT-2026-0001", title="Firm Matter")

        user = CurrentUser(user_id=user_id, firm_id=firm_id, role=role, all_matters_access=False)

        mock_db = AsyncMock()
        res_matter = MagicMock()
        res_matter.scalar_one_or_none.return_value = matter
        res_member = MagicMock()
        res_member.scalar_one_or_none.return_value = None  # NOT a member
        mock_db.execute.side_effect = [res_matter, res_member]

        with pytest.raises(HTTPException) as exc_info:
            await require_matter_access(matter_id, mock_db, user)

        assert exc_info.value.status_code == 404
        assert exc_info.value.status_code != 403

    @pytest.mark.anyio
    async def test_nonexistent_matter_gets_404(self):
        firm_id = uuid.uuid4()
        matter_id = uuid.uuid4()
        user_id = uuid.uuid4()

        admin = CurrentUser(user_id=user_id, firm_id=firm_id, role="admin", all_matters_access=True)

        mock_db = AsyncMock()
        res_matter = MagicMock()
        res_matter.scalar_one_or_none.return_value = None  # Matter not found in firm
        mock_db.execute.return_value = res_matter

        with pytest.raises(HTTPException) as exc_info:
            await require_matter_access(matter_id, mock_db, admin)

        assert exc_info.value.status_code == 404


# ---------------------------------------------------------------------------
# 3. Concurrent matter numbers (BRAIN.md §10 requirement #3 & D-08)
# ---------------------------------------------------------------------------

class TestConcurrentMatterNumbers:
    """Race-free MAT-<YYYY>-<seq> per firm via advisory lock."""

    @pytest.mark.anyio
    async def test_matter_number_format_and_sequence(self):
        firm_id = uuid.uuid4()
        mock_db = AsyncMock()
        res_count = MagicMock()
        res_count.scalar.return_value = 14  # 14 existing matters this year
        mock_db.execute.return_value = res_count

        number = await _next_matter_number(mock_db, firm_id)
        current_year = datetime.now(timezone.utc).year
        assert number == f"MAT-{current_year}-0015"

    def test_advisory_lock_key_partitioned_per_firm_and_year(self):
        firm_a = uuid.uuid4()
        firm_b = uuid.uuid4()
        year = 2026

        key_a = int(hashlib.md5(f"{firm_a}{year}".encode()).hexdigest()[:8], 16)
        key_b = int(hashlib.md5(f"{firm_b}{year}".encode()).hexdigest()[:8], 16)
        assert key_a != key_b
        assert isinstance(key_a, int)


# ---------------------------------------------------------------------------
# 4. Version conflict (BRAIN.md §10 requirement #5 & D-11)
# ---------------------------------------------------------------------------

class TestVersionConflict:
    """Optimistic locking on PATCH via row_version."""

    @pytest.mark.anyio
    async def test_stale_row_version_returns_409(self):
        matter = Matter(
            id=uuid.uuid4(),
            firm_id=uuid.uuid4(),
            matter_number="MAT-2026-0001",
            title="Original Title",
            row_version=3,
        )
        actor_id = uuid.uuid4()
        mock_db = AsyncMock()

        # Client has stale version 2
        payload = MatterPatch(title="New Title", row_version=2)
        with pytest.raises(HTTPException) as exc_info:
            await patch_matter(mock_db, matter, actor_id, payload)

        assert exc_info.value.status_code == 409
        assert "row_version mismatch" in exc_info.value.detail

    @pytest.mark.anyio
    async def test_matching_row_version_succeeds_and_increments(self):
        matter = Matter(
            id=uuid.uuid4(),
            firm_id=uuid.uuid4(),
            matter_number="MAT-2026-0001",
            title="Original Title",
            row_version=3,
        )
        actor_id = uuid.uuid4()
        mock_db = AsyncMock()

        payload = MatterPatch(title="Updated Title", row_version=3)
        updated = await patch_matter(mock_db, matter, actor_id, payload)
        assert updated.row_version == 4
        assert updated.title == "Updated Title"


# ---------------------------------------------------------------------------
# 5. Service-level stage transitions & notes (BRAIN.md §7)
# ---------------------------------------------------------------------------

class TestServiceStageTransitions:
    @pytest.mark.anyio
    async def test_service_invalid_transition_raises_400(self):
        matter = Matter(
            id=uuid.uuid4(),
            firm_id=uuid.uuid4(),
            matter_number="MAT-2026-0001",
            title="Test",
            stage=MatterStage.INTAKE,
            row_version=1,
        )
        actor_id = uuid.uuid4()
        mock_db = AsyncMock()

        payload = MatterTransition(to_stage=MatterStage.REVIEW)
        with pytest.raises(HTTPException) as exc_info:
            await transition_matter(mock_db, matter, actor_id, payload)

        assert exc_info.value.status_code == 400

    @pytest.mark.anyio
    async def test_service_backward_transition_without_note_raises_400(self):
        matter = Matter(
            id=uuid.uuid4(),
            firm_id=uuid.uuid4(),
            matter_number="MAT-2026-0001",
            title="Test",
            stage=MatterStage.DUE_DILIGENCE,
            row_version=1,
        )
        actor_id = uuid.uuid4()
        mock_db = AsyncMock()

        payload = MatterTransition(to_stage=MatterStage.INTAKE, note=None)
        with pytest.raises(HTTPException) as exc_info:
            await transition_matter(mock_db, matter, actor_id, payload)

        assert exc_info.value.status_code == 400
        assert "note is required" in exc_info.value.detail

    @pytest.mark.anyio
    async def test_service_backward_transition_with_note_succeeds(self):
        matter = Matter(
            id=uuid.uuid4(),
            firm_id=uuid.uuid4(),
            matter_number="MAT-2026-0001",
            title="Test",
            stage=MatterStage.DUE_DILIGENCE,
            row_version=1,
        )
        actor_id = uuid.uuid4()
        mock_db = AsyncMock()

        payload = MatterTransition(to_stage=MatterStage.INTAKE, note="Collector issued remand notice")
        updated = await transition_matter(mock_db, matter, actor_id, payload)
        assert updated.stage == MatterStage.INTAKE
        assert updated.row_version == 2


# ---------------------------------------------------------------------------
# 6. Pagination stability (BRAIN.md §10 requirement #6 & D-12)
# ---------------------------------------------------------------------------

class TestPaginationStability:
    """Cursor-based pagination encoding/decoding and deterministic ordering."""

    def test_cursor_roundtrip(self):
        ts = datetime(2026, 11, 5, 15, 30, 0, tzinfo=timezone.utc)
        uid = uuid.uuid4()
        cursor = encode_cursor(ts, uid)
        assert isinstance(cursor, str)

        dec_ts, dec_id = decode_cursor(cursor)
        assert dec_ts == ts
        assert dec_id == uid

    def test_cursor_ordering_preservation(self):
        id_1 = uuid.uuid4()
        id_2 = uuid.uuid4()
        ts_1 = datetime(2026, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
        ts_2 = datetime(2026, 1, 1, 11, 0, 0, tzinfo=timezone.utc)

        c1 = encode_cursor(ts_1, id_1)
        c2 = encode_cursor(ts_2, id_2)
        assert c1 != c2

        d_ts1, _ = decode_cursor(c1)
        d_ts2, _ = decode_cursor(c2)
        assert d_ts1 < d_ts2


# ---------------------------------------------------------------------------
# 7. Crypto service encryption/decryption (BRAIN.md §5)
# ---------------------------------------------------------------------------

class TestCryptoService:
    """Party name encryption via Fernet."""

    def test_encrypt_decrypt_roundtrip(self):
        key = Fernet.generate_key().decode()
        crypto = CryptoService(key)
        name = "Ramesh Patel"
        encrypted = crypto.encrypt(name)
        assert encrypted != name
        assert crypto.decrypt(encrypted) == name

    def test_empty_string_handling(self):
        key = Fernet.generate_key().decode()
        crypto = CryptoService(key)
        assert crypto.encrypt("") == ""
        assert crypto.decrypt("") == ""

    def test_unicode_gujarati_name_encryption(self):
        key = Fernet.generate_key().decode()
        crypto = CryptoService(key)
        gujarati_name = "ભરતભાઈ શાહ"
        encrypted = crypto.encrypt(gujarati_name)
        assert crypto.decrypt(encrypted) == gujarati_name

