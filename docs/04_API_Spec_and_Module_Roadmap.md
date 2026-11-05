# NyaySetu - Backend API Plan & Development Roadmap

*Phases 6 and 7. Base path: `/api/v1`. OpenAPI is generated from FastAPI; the frontend generates its TypeScript client from it.*

---

# Part A. API plan

## A1. Conventions

| Topic | Decision |
|---|---|
| Format | JSON, UTF-8, `snake_case` fields, ISO 8601 UTC timestamps, IDs are UUIDs |
| Auth | `Authorization: Bearer <access_token>`; refresh via httpOnly cookie on `/auth/*` only |
| Versioning | URL prefix `/api/v1`; breaking changes go to `/v2` |
| Idempotency | `Idempotency-Key` header on creating POSTs and notification-sending POSTs |
| Concurrency | `row_version` in body or `If-Match` header for updates; `409` on mismatch |
| Request tracing | Client may send `X-Request-ID`; server always returns it |
| Content negotiation | `Accept-Language: en|gu|hi` for messages |
| Success shape | Single resource: the object itself. List: `{ "items": [...], "next_cursor": "...", "total": 123? }` |
| Dates in queries | `from`, `to` as ISO dates |

## A2. Error format (RFC 7807 style)

```json
{
  "type": "https://api.nyaysetu.in/errors/validation_error",
  "code": "validation_error",
  "title": "Request validation failed",
  "status": 422,
  "detail": "One or more fields are invalid.",
  "request_id": "01JABC...",
  "errors": [
    {"field": "survey_no", "code": "invalid_format", "message": "Use format like 142/A"}
  ]
}
```

| HTTP | `code` examples |
|---|---|
| 400 | `bad_request`, `invalid_cursor` |
| 401 | `unauthenticated`, `token_expired`, `mfa_required` |
| 403 | `forbidden`, `capability_missing` |
| 404 | `not_found` (also for resources outside the caller's scope) |
| 409 | `version_conflict`, `duplicate`, `invalid_state_transition`, `approval_blocked` |
| 413 | `file_too_large` |
| 415 | `unsupported_media_type` |
| 422 | `validation_error` |
| 423 | `account_locked`, `draft_locked` |
| 429 | `rate_limited` (with `Retry-After`) |
| 500/503 | `internal_error`, `service_unavailable` (never leak internals) |

## A3. Pagination, filtering, sorting, search

- **Cursor pagination** by default: `?limit=25&cursor=<opaque>`; max `limit=100`. Offset pagination only for small admin tables.
- **Filtering:** explicit query params per endpoint (`stage=drafting&assigned_to=me&due_before=2026-12-01`); multi-value as repeated params.
- **Sorting:** `sort=-updated_at,title` (prefix `-` = descending); whitelist of sortable fields per endpoint.
- **Search:** `q=` for text; matter and party search uses trigram; research search has its own endpoint with filters and returns snippets.
- **Field selection:** `fields=` is not supported in v1 (keep responses predictable).

## A4. Rate limiting

| Scope | Limit (starting values) |
|---|---|
| Login / MFA / OTP | 5 per 10 min per account and per IP |
| Password reset | 3 per hour per email |
| General API | 300 per minute per user |
| Upload init | 60 per hour per user |
| Search | 60 per minute per user |
| AI endpoints | 20 per minute per user, and per-firm daily quota |
| Client portal | 30 per minute per IP |

Responses include `X-RateLimit-Remaining` and `Retry-After` on 429. Implemented with Redis.

## A5. Logging, audit and exception handling

- **Application logs:** JSON via `structlog`; fields: `ts, level, request_id, user_id, firm_id, route, status, duration_ms`. Never log request bodies, document text, tokens, or PII.
- **Audit events:** written by a service function `audit.record(...)` inside the same DB transaction as the change. Never exposed for write via API.
- **Exception handling:** global handlers map domain exceptions (`NotFound`, `PermissionDenied`, `Conflict`, `ValidationFailed`, `ExternalServiceError`) to the error format; unknown exceptions become `500 internal_error` with the request ID, and are sent to Sentry with PII scrubbed.
- **Health:** `GET /health/live`, `GET /health/ready` (DB, Redis, storage), unauthenticated, no sensitive data.

## A6. Authentication and authorisation

- Every endpoint declares a required **capability** (e.g. `matter.create`) via a dependency. Role-to-capability mapping lives in `modules/firms/permissions.py` and is returned by `/auth/me`.
- Matter-scoped endpoints additionally call `require_matter_access(matter_id)`.
- The server never accepts `firm_id` or `role` from the client body.

## A7. Endpoint catalogue

*Cap = capability required. Pri: M = MVP, V1 = after MVP.*

### Auth (`/auth`)
| Method | Path | Purpose | Pri |
|---|---|---|---|
| POST | `/auth/login` | Email + password -> `mfa_required` challenge or tokens | M |
| POST | `/auth/mfa/verify` | Verify TOTP/OTP, issue tokens | M |
| POST | `/auth/mfa/enroll` | Start TOTP enrolment (QR secret) | M |
| POST | `/auth/mfa/confirm` | Confirm first code, return recovery codes | M |
| POST | `/auth/refresh` | Rotate refresh token | M |
| POST | `/auth/logout`, `/auth/logout-all` | Revoke session(s) | M |
| POST | `/auth/password/forgot`, `/auth/password/reset` | Reset flow | M |
| POST | `/auth/password/change` | Change password, revoke other sessions | M |
| POST | `/auth/invitations/accept` | Accept invite, set password | M |
| GET | `/auth/me` | User, firm(s), role, capabilities, locale | M |
| GET/DELETE | `/auth/sessions`, `/auth/sessions/{id}` | List/revoke devices | V1 |
| POST | `/auth/client/otp/request`, `/auth/client/otp/verify` | Client OTP login | V1 |

### Firm and users (`/firm`)
| Method | Path | Purpose | Cap |
|---|---|---|---|
| POST | `/firms/register` | Create firm and first admin (public, rate-limited, verified by email) | public |
| GET/PATCH | `/firm` | View/update firm settings | `firm.manage` |
| GET | `/firm/users` | List users | `user.view` |
| POST | `/firm/invitations` | Invite user with role | `user.manage` |
| PATCH | `/firm/users/{id}` | Change role, suspend | `user.manage` |
| GET/PUT | `/firm/retention` | Retention policy | `firm.manage` |
| POST/DELETE | `/matters/{id}/legal-hold` | Legal hold | `matter.hold` |

### Matters (`/matters`)
| Method | Path | Purpose | Cap |
|---|---|---|---|
| GET | `/matters` | List with filters (`stage`, `status`, `q`, `assigned_to`, `forum_id`, `due_before`) | `matter.view` |
| POST | `/matters` | Create | `matter.create` |
| GET | `/matters/{id}` | Detail + summary counts (docs, flags, deadlines) | member |
| PATCH | `/matters/{id}` | Update | `matter.edit` |
| POST | `/matters/{id}/stage` | Transition stage (validates allowed transition) | `matter.stage` |
| POST | `/matters/{id}/archive` | Archive | `matter.archive` |
| GET/POST/DELETE | `/matters/{id}/members` | Team | `matter.team` |
| GET/POST/PATCH | `/matters/{id}/parties` | Parties on matter | `matter.edit` |
| GET/POST/PATCH | `/matters/{id}/parcels` | Survey-number parcels | `matter.edit` |
| POST | `/matters/conflict-check` | Check names against existing parties | `matter.create` (V1) |
| GET | `/parties`, POST `/parties` | Party directory | `party.manage` |

### Documents (`/matters/{id}/documents`)
| Method | Path | Purpose | Cap |
|---|---|---|---|
| POST | `/matters/{id}/documents` | Create document record and return **presigned upload URL** | `document.upload` |
| POST | `/documents/{id}/complete` | Confirm upload, start pipeline | `document.upload` |
| GET | `/matters/{id}/documents` | List with status, type | member |
| GET | `/documents/{id}` | Metadata and versions | member |
| GET | `/documents/{id}/pages` | Page list with image URLs (short-lived signed) | member |
| GET | `/documents/{id}/pages/{n}/image?redacted=true|false` | Page rendition; unredacted requires `pii.reveal` and audits | member |
| GET | `/documents/{id}/download` | Original (signed URL), audited | `document.download` |
| PATCH | `/documents/{id}` | Tag type/source | `document.edit` |
| DELETE | `/documents/{id}` | Soft delete (reason required) | `document.delete` |
| GET | `/documents/{id}/events` | SSE job progress | member |

### Extraction (`/extraction`)
| Method | Path | Purpose | Cap |
|---|---|---|---|
| GET | `/documents/{id}/fields` | Fields with confidence, bbox, status | member |
| PATCH | `/fields/{id}` | Correct a field (`row_version`) | `field.edit` |
| POST | `/fields/{id}/verify`, `/fields/{id}/reject` | Review actions | `field.verify` |
| POST | `/documents/{id}/fields` | Manual field entry | `field.edit` |
| GET | `/matters/{id}/review-queue` | Fields needing review | `field.verify` |
| POST | `/documents/{id}/reprocess` | Re-run OCR | `document.upload` |

### Title chain (`/matters/{id}/title`)
| Method | Path | Purpose | Cap |
|---|---|---|---|
| GET | `/matters/{id}/title/chain?parcel_id=` | Events + links + flags | member |
| POST/PATCH | `/matters/{id}/title/events` | Create/edit event (from fields or manual) | `title.edit` |
| GET | `/matters/{id}/title/flags` | Flags list | member |
| POST | `/title/flags/{id}/resolve` | Resolve with note | `title.edit` |
| POST | `/matters/{id}/title/rebuild` | Rebuild chain from verified fields | `title.edit` |
| POST/GET | `/matters/{id}/title/reports` | Generate/list reports | `title.report` (V1) |
| POST | `/title/reports/{id}/signoff` | Partner sign-off | `title.signoff` (V1) |
| GET/POST | `/matters/{id}/notes` | Privileged advocate notes | `note.edit` |

### Research (`/research`)
| Method | Path | Purpose | Cap |
|---|---|---|---|
| POST | `/research/search` | Hybrid search: `{q, filters, limit, cursor}` returns passages with snippets | `research.search` |
| GET | `/research/sources/{id}` | Judgment metadata and text | `research.search` |
| GET | `/research/sources/{id}/passages` | Paragraphs | `research.search` |
| POST | `/matters/{id}/research-items` | Save to matter | `research.save` |
| GET | `/matters/{id}/research-items` | List saved | member |
| POST | `/research/sources/{id}/treatments` | Add treatment flag | `research.curate` (V1) |
| POST | `/research/feedback` | Result feedback | `research.search` |
| POST | `/admin/research/ingest` | Start ingestion batch (internal/admin) | `corpus.manage` |

### Drafting (`/drafts`, `/templates`)
| Method | Path | Purpose | Cap |
|---|---|---|---|
| GET | `/templates` | System + firm templates | `draft.view` |
| POST/PATCH | `/templates` | Firm templates (versions) | `template.manage` (V1) |
| GET | `/matters/{id}/drafts` | List | member |
| POST | `/matters/{id}/drafts` | Create from template; auto-fill variables | `draft.create` |
| GET | `/drafts/{id}` | Current version + references + checks | member |
| PUT | `/drafts/{id}` | Save new version (`row_version`) | `draft.edit` |
| GET | `/drafts/{id}/versions`, `/drafts/{id}/versions/{n}` | History | member |
| POST | `/drafts/{id}/references` | Add evidence/statute/precedent link | `draft.edit` |
| DELETE | `/draft-references/{id}` | Remove link | `draft.edit` |
| POST | `/drafts/{id}/verify-citations` | Run citation verifier | `draft.edit` |
| POST | `/drafts/{id}/submit` | Submit for review | `draft.submit` |
| POST | `/drafts/{id}/comments` | Add comment | `draft.comment` |
| POST | `/drafts/{id}/request-changes` | Reviewer returns draft | `draft.approve` |
| POST | `/drafts/{id}/approve` | Approve and lock; blocked if unverified citations or placeholders | `draft.approve` |
| POST | `/drafts/{id}/unlock` | New version from approved (reason) | `draft.approve` |
| POST | `/drafts/{id}/export` | `{format: docx|pdf}` -> export job | `draft.export` |
| GET | `/exports/{id}` | Status + signed URL | `draft.export` |
| POST | `/drafts/{id}/translate` | Create translation draft (AI, flagged) | `draft.edit` (V1) |
| POST | `/drafts/{id}/ai/suggest-grounds` | AI suggestions with references | `ai.use` (V1) |
| POST | `/drafts/{id}/ai/improve` | Tighten language of a selection | `ai.use` (V1) |

### Deadlines and hearings
| Method | Path | Purpose | Cap |
|---|---|---|---|
| GET | `/limitation/rules` | Rules (filter by forum, act) | `deadline.view` |
| POST | `/limitation/calculate` | `{rule_id, trigger_date, exclusions}` -> due date + steps (no save) | `deadline.view` |
| POST | `/matters/{id}/deadlines` | Save a calculated deadline | `deadline.edit` |
| PATCH | `/deadlines/{id}` | Update, mark filed/dismissed (reason) | `deadline.edit` |
| GET | `/deadlines` | Firm-wide dashboard (`due_before`, `status`, `owner`) | `deadline.view` |
| GET/POST/PATCH | `/matters/{id}/hearings` | Hearings | `hearing.edit` |
| GET | `/hearings?from=&to=` | Calendar list | `hearing.view` |
| GET | `/calendar/feed.ics?token=` | Per-user ICS feed | V1 |
| GET/POST | `/admin/holidays` | Holiday calendar | `corpus.manage` |

### Audit and privacy
| Method | Path | Purpose | Cap |
|---|---|---|---|
| GET | `/audit/events` | Filter by `matter_id, actor_id, action, from, to`; cursor | `audit.view` (own only for others) |
| GET | `/audit/verify` | Verify hash chain for a range | `audit.view` |
| POST | `/matters/{id}/privacy-receipt` | Generate receipt PDF job | `receipt.generate` |
| GET | `/matters/{id}/privacy-summary` | Region, key status, processing steps, retention date | member |
| GET | `/admin/audit/export` | CSV export | `audit.export` (V1) |

### Notifications
| Method | Path | Purpose |
|---|---|---|
| GET | `/notifications` | List (`unread=true`) |
| POST | `/notifications/{id}/read`, `/notifications/read-all` | Mark read |
| GET | `/notifications/stream` | SSE stream |
| GET/PUT | `/me/notification-preferences` | Channels per type |

### Client portal (`/portal`) - V1
| Method | Path | Purpose |
|---|---|---|
| GET | `/portal/matters` | Matters for the signed-in client |
| GET | `/portal/matters/{id}` | Published summary, next hearing |
| GET | `/portal/matters/{id}/updates` | Published updates in client locale |
| POST | `/matters/{id}/portal-updates` | Advocate publishes update (`portal.publish`) |
| POST | `/matters/{id}/portal-invite` | Invite client by mobile |

### Misc
| Method | Path | Purpose |
|---|---|---|
| GET | `/me/profile`, PATCH | Profile, locale, advocate details |
| GET | `/search/global?q=` | Matters, parties, documents (scoped) |
| GET | `/dashboard` | Widgets: due soon, awaiting review, recent activity |
| POST | `/leads` | Demo request from landing (public, rate-limited) |
| GET | `/meta/reference` | Forums, statutes, document types, enums |

## A8. Key request and response models (Pydantic v2)

```python
from datetime import date, datetime
from enum import StrEnum
from uuid import UUID
from pydantic import BaseModel, Field, field_validator

class Stage(StrEnum):
    intake="intake"; ingestion="ingestion"; title="title"
    drafting="drafting"; review="review"; filed="filed"; closed="closed"

class ParcelIn(BaseModel):
    village: str = Field(min_length=1, max_length=80)
    taluka: str
    district: str
    survey_no: str = Field(max_length=30)
    khata_no: str | None = Field(default=None, max_length=12)

    @field_validator("survey_no")
    @classmethod
    def survey_format(cls, v: str) -> str:
        v = normalise_digits(v.strip())              # Gujarati/Devanagari digits -> ASCII
        if not SURVEY_RE.fullmatch(v):
            raise ValueError("invalid_format")
        return v

class MatterCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    forum_id: UUID
    statute_id: UUID | None = None
    parties: list[PartyRef] = Field(min_length=1)
    parcels: list[ParcelIn] = Field(default_factory=list, max_length=50)
    team_user_ids: list[UUID] = []

class MatterOut(BaseModel):
    id: UUID; matter_no: str; title: str; stage: Stage; status: str
    forum: ForumOut; parcels: list[ParcelOut]; team: list[UserRef]
    counts: MatterCounts; next_deadline: DeadlineBrief | None
    created_at: datetime; row_version: int

class UploadInit(BaseModel):
    filename: str; mime: str; size_bytes: int = Field(gt=0, le=50*1024*1024)
    doc_type: DocType; sha256: str | None = None

class UploadInitOut(BaseModel):
    document_id: UUID; upload_url: str; headers: dict[str, str]; expires_at: datetime

class FieldOut(BaseModel):
    id: UUID; field_key: str; value_raw: str | None; value_norm: str | None
    confidence: float | None; status: str; page_no: int | None
    bbox: list[float] | None; verified_by: UserRef | None; row_version: int

class FieldPatch(BaseModel):
    value_raw: str; reason: str | None = None; row_version: int

class DraftSave(BaseModel):
    row_version: int
    language: Literal["en","gu","hi"]
    header: DraftHeader
    grounds: list[GroundIn] = Field(max_length=100)   # each: text, ordinal, source(user|ai|template)
    prayer: str
    references: list[ReferenceIn] = []

class ApproveOut(BaseModel):
    draft_id: UUID; version_no: int; approved_by: UserRef
    approved_at: datetime; content_hash: str

class ApprovalBlocked(BaseModel):                  # returned in 409 `errors`
    unverified_citations: list[UUID]
    unresolved_placeholders: list[str]

class LimitationCalcIn(BaseModel):
    rule_id: UUID; trigger_date: date
    copy_applied_on: date | None = None; copy_received_on: date | None = None

class LimitationCalcOut(BaseModel):
    due_date: date; rule: RuleBrief; steps: list[CalcStep]   # day-by-day working
    excluded_days: list[ExcludedDay]; notice: str            # advocate-must-confirm text

class SearchIn(BaseModel):
    q: str = Field(min_length=2, max_length=500)
    court_ids: list[UUID] = []; year_from: int | None = None; year_to: int | None = None
    section_ids: list[UUID] = []; limit: int = Field(25, le=50); cursor: str | None = None

class PassageHit(BaseModel):
    source_id: UUID; citation: str; case_name: str; court: str; decided_on: date
    para_no: int | None; snippet: str; highlights: list[tuple[int,int]]
    rank: int; match_kind: Literal["keyword","semantic","both"]   # no fake percentages

class AuditEventOut(BaseModel):
    seq: int; at: datetime; actor: UserRef | None; actor_role: str | None
    action: str; resource_type: str | None; resource_id: UUID | None
    matter_id: UUID | None; ip: str | None; hash: str
```

## A9. Validation rules (server side)

Mirror PRD section 9.2. Specific checks: survey number regex and digit normalisation; area string parser (H-A-Sq.m) with range limits; file MIME sniffing (do not trust the extension); SHA-256 match after upload; date sanity; enrolment-number format; role/capability allow-list; state-machine checks for matter stage and draft review states; text normalisation (NFC) and control-character stripping; maximum JSON size per request (1 MB, except draft saves 2 MB).

## A10. Authorisation checks to test on every endpoint

1. No token -> 401.
2. Valid token, other firm's resource -> 404.
3. Valid token, same firm, not a matter member -> 404.
4. Member without the capability -> 403.
5. Capability present -> success and audit event written.

---

# Part B. Backend development roadmap

*Each module is independently buildable and shippable behind its API. Suggested order = dependency order. Time estimates assume 2-3 engineers.*

## M0. Foundation and platform

| Item | Detail |
|---|---|
| **Objective** | Runnable skeleton with config, DB, migrations, logging, errors, CI. |
| **Scope** | FastAPI app factory; settings; async SQLAlchemy session; Alembic baseline; error handlers; request ID middleware; structlog; health endpoints; pagination and rate-limit helpers; Docker Compose (api, postgres, redis, minio); CI pipeline; pre-commit. |
| **Dependencies** | None |
| **Files** | `app/main.py`, `app/core/{config,db,errors,logging,pagination,ratelimit,security}.py`, `alembic/`, `docker-compose.yml`, `Dockerfile`, `.github/workflows/ci.yml`, `pyproject.toml`, `tests/conftest.py` |
| **Folder structure** | As doc 03 section A4 |
| **APIs** | `GET /health/live`, `GET /health/ready` |
| **DB changes** | Extensions; empty baseline revision |
| **Testing** | Health tests; error-format tests; migration up/down test; lint and mypy in CI |
| **Done when** | `docker compose up` gives a working API; CI is green; a request ID appears in logs and responses; one sample error returns the standard format. |
| **Time** | 1 week |

## M1. Auth, firms, users, RBAC, tenancy

| Item | Detail |
|---|---|
| **Objective** | Secure identity and tenant isolation. |
| **Scope** | Firm registration; invitations; Argon2id login; TOTP MFA; JWT + refresh rotation; sessions; lockout; password reset; `/auth/me` with capabilities; capability dependency; RLS policies and per-request `app.firm_id`; user admin. |
| **Dependencies** | M0 |
| **Files** | `modules/auth/*`, `modules/firms/*`, `core/security.py`, `core/permissions.py`, `core/tenancy.py`, migrations for identity tables and RLS |
| **APIs** | Auth, Firm/users sections of A7 |
| **DB changes** | `firms, users, firm_memberships, invitations, sessions, mfa_credentials, login_attempts, advocate_profiles` |
| **Testing** | Login success/failure; MFA; lockout; refresh reuse detection; role-capability matrix tests; cross-tenant isolation tests (including direct SQL with RLS); rate-limit tests; password policy; invitation expiry |
| **Done when** | A user cannot see another firm's data by any route; refresh reuse revokes the family; `/auth/me` drives the frontend; matrix tests pass. |
| **Time** | 2-3 weeks |

## M2. Audit service

| Item | Detail |
|---|---|
| **Objective** | Tamper-evident audit used by every later module. Build early. |
| **Scope** | `audit.record()` helper in the same transaction; hash chain with per-firm sequence (advisory lock or sequence table); append-only enforcement (privileges + trigger); verify job; query API with filters; CSV export later. |
| **Dependencies** | M0, M1 |
| **Files** | `modules/audit/{service,models,router,schemas,verify}.py`, trigger migration |
| **APIs** | `GET /audit/events`, `GET /audit/verify` |
| **DB changes** | `audit_events`, `audit_anchors` |
| **Testing** | Chain verifies; tampering detected; UPDATE/DELETE blocked; concurrent writes keep sequence correct; permission scoping (own vs all) |
| **Done when** | Every M1 action is audited; verify detects a manually altered row; concurrent writes do not break the chain. |
| **Time** | 1 week |

## M3. Matters, parties, parcels, stages

| Item | Detail |
|---|---|
| **Objective** | The matter as the central object. |
| **Scope** | Matter CRUD; matter number generator; members and access; parties; parcels; stage transitions with allowed graph; archive; list/search/filter/sort; dashboard summary; reference data (forums, statutes); conflict check (V1). |
| **Dependencies** | M1, M2 |
| **Files** | `modules/matters/*`, `modules/reference/*`, seeds |
| **APIs** | Matters, parties, `/meta/reference`, `/dashboard` |
| **DB changes** | `matters, matter_members, matter_parties, matter_stages, parties, land_parcels, forums, statutes, statute_sections` |
| **Testing** | Access by membership; partner "all matters" rule; stage-transition table tests; unique matter number under concurrency; survey-number validation and digit normalisation; pagination stability |
| **Done when** | Frontend matter list and creation work end to end; 404 for non-members; audit entries exist. |
| **Time** | 2 weeks |

## M4. Documents and storage

| Item | Detail |
|---|---|
| **Objective** | Safe upload, storage, and viewing of originals and renditions. |
| **Scope** | Presigned upload; completion; checksum verify; MIME sniffing; antivirus; versions; duplicate detection; signed URLs with short expiry; page renditions; soft delete; SSE job events; envelope encryption helper. |
| **Dependencies** | M3 |
| **Files** | `modules/documents/*`, `core/storage.py`, `core/crypto.py`, `workers/documents.py` |
| **APIs** | Documents section of A7 |
| **DB changes** | `documents, document_versions, document_pages, processing_jobs` |
| **Testing** | Upload flow with MinIO; oversize/wrong type rejected; checksum mismatch; duplicate warning; signed URL expiry; infected file path; access control; audit on download |
| **Done when** | A 20 MB PDF uploads, is scanned, split into pages, and viewable; originals cannot be overwritten. |
| **Time** | 2 weeks |

## M5. OCR and extraction

| Item | Detail |
|---|---|
| **Objective** | Turn scans into reviewed structured fields. |
| **Scope** | OCR adapter interface and first engine; per-page text and boxes; field extractor (rules plus optional LLM) for 7/12, 8A and Ferfar; confidence; review queue; corrections with history; manual entry; PII detection and **server-side redacted renditions**; reveal with audit; benchmark harness. |
| **Dependencies** | M4 |
| **Files** | `modules/extraction/*`, `workers/ocr.py`, `modules/extraction/engines/*`, `modules/extraction/extractors/*`, `modules/documents/redaction.py`, `benchmarks/` |
| **APIs** | Extraction section of A7 |
| **DB changes** | `ocr_results, extracted_fields, extracted_field_versions, pii_findings` |
| **Testing** | Golden dataset of real (consented) documents with expected fields; accuracy report per field; retry/idempotency; low-confidence routing; redacted image contains no original text (pixel/text test); correction history; role rules |
| **Done when** | Agreed accuracy targets on the held-out set; paralegal can review and verify; redacted rendition verified; failures give actionable reasons. |
| **Time** | 4-6 weeks (benchmark first) |

## M6. Title chain

| Item | Detail |
|---|---|
| **Objective** | Build and explain the chain of title. |
| **Scope** | Events from verified fields or manual; links; encumbrances; rule engine for flags (gap, area mismatch, active charge, owner conflict, date order); chain query; source links; notes; report generation (V1). |
| **Dependencies** | M5 |
| **Files** | `modules/title/{models,service,rules,router,reports}.py` |
| **APIs** | Title chain section of A7 |
| **DB changes** | `title_events, title_event_links, encumbrances, title_flags, title_reports, matter_notes` |
| **Testing** | Rule unit tests with fixtures (clean chain, gap, active mortgage, discharged mortgage, partition branch); ordering tests; source page links resolve |
| **Done when** | The canonical matter 809 produces the expected chain and flags; every node links to a document page. |
| **Time** | 2-3 weeks |

## M7. Research corpus and search

| Item | Detail |
|---|---|
| **Objective** | Searchable, licensed corpus of revenue rulings. |
| **Scope** | Ingestion pipeline (PDF/text to passages, metadata, citation aliases); provenance and licence fields; embeddings; hybrid search (FTS + trigram + vector) with filters; judgment view; save to matter; feedback; treatments (V1). |
| **Dependencies** | M0, M1 (corpus is global); matters for saves (M3) |
| **Files** | `modules/research/*`, `workers/ingest.py`, `modules/ai/embeddings.py` |
| **APIs** | Research section of A7 |
| **DB changes** | `legal_sources, source_passages, citation_aliases, source_treatments, matter_research_items, ingestion_batches, feedback` |
| **Testing** | Relevance test set (query -> expected judgments) with recall@10; Gujarati and English queries; digit normalisation; filter correctness; latency p95 target; ingestion idempotency |
| **Done when** | Relevance targets met on the test set; each result shows an exact passage and source link; licence data recorded. |
| **Time** | 3-4 weeks (corpus acquisition is the real risk) |

## M8. Drafting, citations, review workflow

| Item | Detail |
|---|---|
| **Objective** | Editable, versioned, evidence-linked drafts with approval. |
| **Scope** | Templates and versions; variable auto-fill from matter; draft CRUD and versions; references (document page, statute, precedent); citation verifier; placeholder detection; review states; comments; approval lock; unlock; optimistic concurrency. |
| **Dependencies** | M3, M5 (evidence), M7 (precedents), M2 |
| **Files** | `modules/drafting/*`, `modules/citations/*` |
| **APIs** | Drafting section of A7 |
| **DB changes** | `templates, template_versions, drafts, draft_versions, draft_grounds, draft_references, citation_checks, draft_reviews, draft_comments, draft_approvals` |
| **Testing** | Variable fill; version history; concurrency conflict; approval blocked by unverified citation/placeholder; locked draft cannot be edited; role matrix; citation verifier cases (exact, alias, not found, wrong year) |
| **Done when** | End-to-end: create from template, link evidence, verify, submit, approve, lock; audit trail complete. |
| **Time** | 3-4 weeks |

## M9. Export (DOCX/PDF)

| Item | Detail |
|---|---|
| **Objective** | Court-format output. |
| **Scope** | DOCX and PDF renderers; Noto Sans Gujarati/Devanagari embedding; page setup; numbering; verification page with version hash; DRAFT watermark rule; export job and signed link. |
| **Dependencies** | M8 |
| **Files** | `modules/drafting/export/*`, `templates/export/*`, fonts |
| **APIs** | `/drafts/{id}/export`, `/exports/{id}` |
| **DB changes** | `exports` |
| **Testing** | Golden-file comparison; Gujarati glyph rendering; watermark on unapproved; no watermark on approved; large draft performance |
| **Done when** | Advocates confirm output matches filing norms for each of the 4 templates in en and gu. |
| **Time** | 2 weeks |

## M10. Deadlines, hearings, reminders, notifications

| Item | Detail |
|---|---|
| **Objective** | No missed deadlines. |
| **Scope** | Limitation rules (reviewed data); holiday calendar; calculator with working steps; saved deadlines; hearings; reminder scheduler (Celery Beat); notification service (in-app, email); SSE stream; preferences; ICS feed (V1); SMS/WhatsApp adapters (V1). |
| **Dependencies** | M3, M2 |
| **Files** | `modules/deadlines/*`, `modules/notifications/*`, `workers/reminders.py` |
| **APIs** | Deadlines/hearings and Notifications sections |
| **DB changes** | `limitation_rules, holidays, deadlines, hearings, reminders, notifications, notification_deliveries` |
| **Testing** | Calculator unit tests from advocate-supplied worked examples; holiday and exclusion cases; timezone (IST) edge cases; reminder idempotency; notification delivery retries |
| **Done when** | Advocate signs off a written list of worked examples; reminders fire at 7/3/1 days exactly once. |
| **Time** | 3 weeks |

## M11. Privacy summary and receipt

| Item | Detail |
|---|---|
| **Objective** | Make privacy provable. |
| **Scope** | Collect facts: storage region, encryption/key status, processing steps per document (from `processing_jobs` and `ai_runs`), retention date, audit anchor; generate signed PDF; show summary in matter header. |
| **Dependencies** | M2, M4, M5, M8 |
| **Files** | `modules/audit/receipts.py`, `workers/receipts.py` |
| **APIs** | `/matters/{id}/privacy-receipt`, `/privacy-summary` |
| **DB changes** | `privacy_receipts` |
| **Testing** | Receipt facts match DB; changes to retention reflect; chain anchor included; no unverifiable claims text |
| **Done when** | Every statement in the receipt maps to a database fact or config value. |
| **Time** | 1-2 weeks |

## M12. AI services

| Item | Detail |
|---|---|
| **Objective** | Safe, logged, replaceable AI layer. |
| **Scope** | Model adapter interfaces (LLM, embeddings, OCR); prompt templates; PII redaction before calls; output schema validation; grounding rules (draft suggestions must cite references); `ai_runs` logging; quotas; evaluation harness; translation with glossary. |
| **Dependencies** | M5, M7, M8 |
| **Files** | `modules/ai/{adapters,prompts,guardrails,eval}/*`, `workers/ai.py` |
| **APIs** | `/drafts/{id}/ai/*`, `/drafts/{id}/translate` |
| **DB changes** | `ai_runs`, `draft_translations` |
| **Testing** | Eval sets for extraction, translation, suggestion quality; prompt-injection tests (hostile text inside documents); refusal when no source; PII not in prompts; timeouts and fallbacks |
| **Done when** | AI features are behind flags; every output is labelled and logged; evaluation scores meet agreed thresholds. |
| **Time** | 4 weeks (parallel with M8-M10) |

## M13. Client portal

| Item | Detail |
|---|---|
| **Objective** | Safe, simple client updates. |
| **Scope** | Client accounts; OTP login; published updates; locale; SMS/WhatsApp notices; invite flow; strict data scoping. |
| **Dependencies** | M3, M10 |
| **Files** | `modules/portal/*` |
| **APIs** | Portal section |
| **DB changes** | `client_accounts, portal_updates` |
| **Testing** | Client cannot see unpublished items; client cannot enumerate other matters; OTP limits; locale fallback |
| **Done when** | Penetration-style tests on enumeration and IDOR pass. |
| **Time** | 2 weeks |

## M14. Admin, retention, data requests, hardening

| Item | Detail |
|---|---|
| **Objective** | Production readiness. |
| **Scope** | Retention policies and legal hold; deletion jobs; data export/deletion requests; usage stats; security headers; dependency and container scanning; backup/restore drills; load tests; runbooks; penetration test fixes. |
| **Dependencies** | All |
| **Files** | `modules/admin/*`, `workers/retention.py`, `ops/runbooks/*` |
| **APIs** | Admin endpoints |
| **DB changes** | `retention_policies, legal_holds, data_requests` |
| **Testing** | Legal hold blocks deletion; deletion removes files and records and writes audit; restore drill succeeds; load test meets NFRs |
| **Done when** | Pen-test criticals closed; restore drill documented; NFR targets verified. |
| **Time** | 3 weeks |

## Suggested build timeline

| Months | Modules |
|---|---|
| 1 | M0, M1, M2 |
| 2 | M3, M4 |
| 3-4 | M5 (with parallel M7 corpus work) |
| 4-5 | M6, M8, M9 |
| 5 | M10, M11, MVP hardening and pilot |
| 6-8 | M12 (features), M13, M7 full corpus |
| 9 | M14 and V1 release |

## Cross-module definition of done

- Endpoints documented in OpenAPI with examples.
- Migrations reversible and tested.
- Authorisation tests (A10) pass for every endpoint.
- Audit events written for state changes and sensitive reads.
- Structured logs without PII.
- Unit and integration tests; coverage at least 80% for the module.
- Frontend contract confirmed by generating the TypeScript client without manual edits.
