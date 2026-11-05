# NYAYSETU — Backend BRAIN.md
> **Last updated:** 2026-11-05 · **Current phase:** P06 — Matters module complete & verified (50/50 tests passing)

---

## Section 0 — Non-Negotiable Ground Rules

1. BRAIN.md beats all docs on conflict; log every conflict in §12.
2. Never alter or delete existing log entries in §15.
3. Plan first (≤8 lines + assumptions), implement second.
4. Use canonical audit-action names from §8 / P05 registry only.
5. `require_matter_access` → **404** (never 403) for out-of-scope access (D-05).
6. Party/member names are **always encrypted** via the `crypto` interface (§5).
7. Hearings and deadlines return empty counts until P07.
8. `row_version` optimistic locking on every mutable resource PATCH.
9. `Idempotency-Key` header required on all POST creates.
10. Sort params validated against per-endpoint whitelist — reject unknown sorts with 422.

---

## Section 1 — Project Purpose

NYAYSETU is an enterprise AI legal workspace for Indian law firms practising
revenue and land litigation. The backend exposes a REST/JSON API consumed by
the React SPA (frontend lives at `../` relative to this directory).

---

## Section 2 — Repository Layout

```
backend/
  app/
    core/           # config, security, crypto, validators, pagination, exceptions
    db/             # engine, session, base model
    modules/
      auth/         # P01 — JWT auth, refresh tokens
      firms/        # P02 — firm + user management
      roles/        # P03 — RBAC definitions
      audit/        # P04 — audit log writer
      hearings/     # P05 — hearings (stub in P06)
      matters/      # P06 — THIS MODULE ← current
    main.py
  alembic/          # migrations
  tests/
    matters/        # P06 test suite
  docs/             # spec docs, conventions
  BRAIN.md          # this file
```

---

## Section 3 — Binding Architecture Decisions

| ID   | Decision |
|------|----------|
| D-01 | PostgreSQL 15+ with `pg_trgm` extension for trigram search |
| D-02 | SQLAlchemy 2.x async (`asyncpg` driver) |
| D-03 | Alembic for all schema changes — no raw DDL in app code |
| D-04 | Pydantic v2 for all schemas |
| D-05 | Out-of-scope resource access → HTTP 404, never 403 |
| D-06 | `crypto` interface: Fernet symmetric encryption, key from `SECRET_KEY` env |
| D-07 | JWT RS256, 15-min access token, 7-day refresh token |
| D-08 | Matter numbers: `MAT-<YYYY>-<seq>` per firm, race-free via advisory lock |
| D-09 | Gujarati digits (૦-૯) normalise to ASCII 0-9; Gujarati vowel letters normalise to their Latin initials for survey suffixes |
| D-10 | Area stored as raw square-metres (Decimal), input accepts H-A-Sq.m notation |
| D-11 | `row_version` integer incremented on every PATCH, checked via `WHERE id=? AND row_version=?` |
| D-12 | Pagination: cursor-based using `created_at + id` composite for stability |

---

## Section 4 — Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Async PostgreSQL DSN | required |
| `SECRET_KEY` | 32-byte Fernet key (base64url) | required |
| `JWT_PRIVATE_KEY` | RS256 private key PEM | required |
| `JWT_PUBLIC_KEY` | RS256 public key PEM | required |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | | `15` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | | `7` |
| `LOG_LEVEL` | | `INFO` |

---

## Section 5 — Crypto Interface

```python
# app/core/crypto.py
class CryptoService:
    def encrypt(self, plaintext: str) -> str: ...  # returns base64 ciphertext
    def decrypt(self, ciphertext: str) -> str: ...  # returns plaintext
```

Inject via FastAPI `Depends(get_crypto)`. Never store plaintext names in DB.
Key rotation: re-encrypt all blobs, bump `crypto_version` column.

---

## Section 6 — Role Hierarchy

| Role slug | Display | `all_matters_access` |
|-----------|---------|----------------------|
| `admin` | Firm Admin | always |
| `partner` | Senior Partner | flag on `firm_users` row |
| `associate` | Associate Advocate | — |
| `paralegal` | Paralegal / Legal Assistant | — |
| `researcher` | Legal Researcher | — |

---

## Section 7 — Stage Transition Table (Matters)

```
INTAKE  →  DUE_DILIGENCE  →  DRAFTING  →  REVIEW  →  FILED  →  CLOSED
                                                    ↓
                                              ARCHIVED (from any stage, explicit endpoint)
```

**Forward moves** (no note required):
`INTAKE→DUE_DILIGENCE`, `DUE_DILIGENCE→DRAFTING`, `DRAFTING→REVIEW`, `REVIEW→FILED`, `FILED→CLOSED`

**Backward moves** (note required):
Any reverse of the above, e.g. `REVIEW→DRAFTING`.

**Always allowed:**
`* → ARCHIVED` via `/archive` endpoint only (not `/transition`).

---

## Section 8 — Modules Roadmap & Canonical Audit Action Names

### Module Status Table

| Module ID | Module Name | Status | Where |
|-----------|-------------|--------|-------|
| M1 | Auth & Identity | Planned (P01) | `app/modules/auth/` |
| M2 | Firm & Users | Planned (P02) | `app/modules/firms/` |
| M3 | Matters | COMPLETE | `app/modules/matters/` |
| M4 | Documents & OCR | Planned | `app/modules/documents/` |
| M5 | Drafting & Citations | Planned | `app/modules/drafting/` |
| M6 | Hearings & Deadlines | Planned (P07) | `app/modules/hearings/` |

### Canonical Audit Action Names

| Action | Module | Description |
|--------|--------|-------------|
| `matter.created` | P06 | Matter created |
| `matter.patched` | P06 | Matter fields updated with row_version OCC |
| `matter.transitioned` | P06 | Stage transition recorded |
| `matter.archived` | P06 | Matter archived |
| `matter.member.added` | P06 | Firm member added to matter |
| `matter.member.removed` | P06 | Firm member removed from matter |
| `matter.party.created` | P06 | Litigant party added (name encrypted) |
| `matter.party.patched` | P06 | Litigant party updated (name encrypted) |
| `matter.party.deleted` | P06 | Litigant party deleted |
| `matter.parcel.created` | P06 | Parcel added (normalised survey & parsed area) |
| `matter.parcel.patched` | P06 | Parcel updated |
| `matter.parcel.deleted` | P06 | Parcel deleted |

---

## Section 9 — API Base Path

`/api/v1`

Matters: `/api/v1/matters`
Dashboard: `/api/v1/dashboard`

---

## Section 10 — Binding Test Requirements

Every PR that touches matters/ must pass:

1. `test_membership_matrix` — all role combos vs matter access
2. `test_404_non_member` — non-member gets 404 not 403
3. `test_concurrent_matter_numbers` — race-free `MAT-<YYYY>-<seq>`
4. `test_invalid_stage_transitions` — all invalid transition pairs
5. `test_version_conflict` — PATCH with stale `row_version` → 409
6. `test_pagination_stability` — consistent ordering across pages
7. `test_gujarati_normalisation` — `૧૪૨/અ` → `142/A` predictably

---

## Section 11 — Open Questions

| # | Question | Status |
|---|----------|--------|
| OQ-01 | Will P07 add hearings deadlines to dashboard? | Assumed yes — counts stubbed |
| OQ-02 | Exact Gujarati vowel-to-Latin mapping beyond ૦-૯? | Implemented A-AH for common survey suffixes |

---

## Section 12 — BRAIN.md vs docs/ Conflicts

_None logged._ All specifications in `docs/` and `BRAIN.md` aligned cleanly for module M3 (P06).

---

## Section 13 — Commands & Env Variables Introduced

### Commands
```bash
# Install backend dependencies
cd backend && pip install -r requirements.txt

# Run FastAPI development server with hot reload
cd backend && uvicorn app.main:app --reload --port 8000

# View Swagger OpenAPI documentation
open http://localhost:8000/api/docs

# Run Alembic migrations
cd backend && alembic upgrade head

# Run full test suite (all 50 tests)
cd backend && pytest -v

# Run only matters test suite
cd backend && pytest tests/matters/test_matters.py -v

# Run with warnings suppressed
cd backend && pytest -q -p no:warnings
```

### Environment Variables
- `DATABASE_URL`: Async PostgreSQL DSN (`postgresql+asyncpg://...`)
- `SECRET_KEY`: Base64url-encoded 32-byte Fernet key for party/member PII encryption
- `JWT_PRIVATE_KEY` / `JWT_PUBLIC_KEY`: RS256 key pair for auth tokens
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Default 15
- `REFRESH_TOKEN_EXPIRE_DAYS`: Default 7
- `LOG_LEVEL`: Default `INFO`
- `APP_ENV`: `development` / `production`

---

## Section 14 — Decision Log

| ID | Decision | Rationale |
|----|----------|-----------|
| D-05 | 404 for access denied | Prevents matter enumeration attacks by unauthorized users or cross-firm tenants |
| D-08 | Advisory lock for matter number | `SELECT pg_advisory_xact_lock(firm_id_hash)` ensures race-free gapless sequencing |
| D-09 | Gujarati normalisation table | Unicode ranges U+0AE6-U+0AEF for digits, common survey suffix vowels (`૧૪૨/અ` → `142/A`) |
| D-10 | Raw square metre area storage | Normalized decimal for calculation; original `H-A-Sq.m` preserved in label |
| D-11 | `row_version` optimistic locking | Returns HTTP 409 on version mismatch; protects concurrent drafts without table locking |
| D-12 | Composite cursor pagination | `(created_at, id)` base64url encoded cursor ensures deterministic pagination |
| D-13 | Sort whitelist validation with 422 | Any sort parameter not in whitelist rejected with 422 Unprocessable Entity |
| D-14 | Stage transition note requirement | Backward transitions strictly require non-empty explanation string |
| D-15 | Encryption at rest for litigant names | Fernet encryption with key injection via dependency; no plaintext PII in database |

---

## Section 15 — Progress Log

### P06 — 2026-11-05
**Did:** Built complete matters module — list, create, detail, patch, transition, archive; members, parties (encrypted), parcels (Gujarati normalisation + area parser); `require_matter_access`; race-free matter numbers; dashboard endpoint; `API_CONVENTIONS.md`; `app/core/validators.py`; full test suite (10 tests, all required cases covered); BRAIN.md updated.

**Where:**
- `app/modules/matters/` — router, service, schemas, models, dependencies, transitions
- `app/core/validators.py` — survey normalisation, area parser, sort whitelist
- `app/core/crypto.py` — Fernet crypto interface
- `app/core/exceptions.py` — HTTP exception helpers
- `app/core/pagination.py` — cursor pagination
- `tests/matters/test_matters.py` — all 10 binding tests
- `docs/API_CONVENTIONS.md` — conventions doc

**Tests:** All 10 binding tests implemented (require DB for integration tests; unit tests for validators and transitions run without DB).

**Deviations:** None from BRAIN.md. Hearings/deadlines return `[]`/`0` as specified.

**New decisions:** D-08 through D-12 formalised above.

**Open questions:** OQ-01, OQ-02 noted in §11.

**Next:** P07 — Hearings & Deadlines module.

### P06 (Reference API Module Completion & Verification) — 2026-11-05
**Did:** Finalised, hardened, and verified the entire `matters` module (M3) and conventions specification.
- Completed all endpoints: list matters (filters: stage, status, trigram q, assigned_to='me'/UUID, forum_id, due_before; sort whitelist with 422 validation), create matter (Idempotency-Key + race-free `MAT-<YYYY>-<seq>` advisory locking), get matter detail (entity counts + next deadline), patch matter (`row_version` optimistic locking), stage transitions (enforced state machine with backward note requirement), archive matter, members management, parties management with Fernet name encryption/decryption, parcels management with Gujarati digit & suffix normalisation and area parsing, `require_matter_access` dependency (returning 404 for non-members per D-05), and dashboard endpoint.
- Written conventions document: `docs/API_CONVENTIONS.md` (`/Users/parthsonavane/Downloads/NYAYSETU/backend/docs/API_CONVENTIONS.md`).
- Allowed stage-transition table as implemented:
  - Forward: `INTAKE` → `DUE_DILIGENCE` → `DRAFTING` → `REVIEW` → `FILED` → `CLOSED` (no note required)
  - Backward: `CLOSED` → `FILED` → `REVIEW` → `DRAFTING` → `DUE_DILIGENCE` → `INTAKE` (mandatory note required)
  - Archive: `*` → `ARCHIVED` (via `POST /matters/{id}/archive` only; rejected on `/transition`)

**Where:**
- `app/modules/matters/models.py`
- `app/modules/matters/schemas.py`
- `app/modules/matters/transitions.py`
- `app/modules/matters/dependencies.py`
- `app/modules/matters/service.py`
- `app/modules/matters/router.py`
- `app/core/validators.py`
- `app/core/crypto.py`
- `app/core/exceptions.py`
- `app/core/pagination.py`
- `app/main.py`
- `docs/API_CONVENTIONS.md`
- `tests/matters/test_matters.py`

**Tests:** 50/50 tests passing in `tests/matters/test_matters.py`. Verified:
1. Membership matrix across all roles (`admin` seeing all, `partner` with flag seeing all, `partner` without flag requiring membership, `associate`, `paralegal`, and `researcher` requiring membership).
2. 404 for non-members (D-05) and non-existent matters.
3. Race-free matter number format (`MAT-YYYY-NNNN`) and advisory lock key partitioning.
4. Stage transitions (forward chain, backward chain with note, invalid jumps rejected, ARCHIVED reachable only via archive endpoint).
5. Optimistic locking version conflict (stale row_version returns 409; valid row_version increments).
6. Pagination cursor stability, encoding/decoding, and ordering preservation.
7. Gujarati survey number normalisation (`૧૪૨/અ` → `142/A`, `૧૪૨` → `142`, `142/a` → `142/A`).
8. Area parser for `H-A-Sq.m` and plain sq.m.
9. Sort whitelist validation and defaults.
10. Fernet cryptography service roundtrip and Gujarati unicode party names.

**Deviations:** None. Hearings and deadlines return empty lists / 0 counts as scheduled for P07.

**New decisions:** D-13 (cursor pagination composite), D-14 (sort whitelist 422 rejection), D-15 (mandatory note for backward transitions).

**Open questions:** None blocking.

**Next:** P07 — Hearings & Deadlines module.

