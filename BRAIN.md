# BRAIN.md - NyaySetu project memory

> **Read this whole file before doing anything.** It is the single source of project context for every AI assistant and developer. Detailed specs live in `docs/`. Update this file at the end of every task (see section 0).
> Last updated: 2026-11-05 | Current phase: **M0, P02 Schema & M1a Auth Complete; M1b/M2 Next**

---

## 0. Working agreement (rules for every AI assistant)

1. **Read order:** this file -> the docs sections named in your prompt -> existing code. Do not read or change anything outside your task's scope.
2. **Priority when sources conflict:** Section 3 (Locked decisions) > this file > `docs/` > your own preferences. If you find a conflict or gap, do **not** silently choose: write it under "Open questions" (section 12) and continue with the safest option, stating it.
3. **Never invent legal content.** Statutes, section numbers, limitation periods, forums and case citations are *data reviewed by a named advocate*. Use placeholders flagged `needs_review`. See section 10.
4. **Never invent facts about the product's security or compliance.** Banned claims are listed in section 10.
5. **Stay inside the prompt's scope.** No extra modules, tables, endpoints or dependencies unless the task needs them. If you add one, log it.
6. **Definition of done** for any task: code + tests passing + migrations reversible + authorisation tests + audit events + no PII in logs + docs updated + this file updated.
7. **At the end of every task, update BRAIN.md** (only these parts):
   - Section 8: change the status of the module(s) you finished (`Not started` -> `In progress` -> `Done`) and fill the "Where" column with the path.
   - Section 14: add any new decision as `D-xx` (never edit or delete old ones; supersede with a new one).
   - Section 12: add open questions or assumptions.
   - Section 13: add commands, env variables or setup steps you introduced.
   - Section 15: **append** one Progress Log entry using the template there. Append only; never rewrite history.
   - Update the "Last updated" line and "Current phase" line at the top.
8. Keep this file under about 700 lines. When section 15 has more than 40 entries, compress the oldest 20 into one "Archive" entry.

---

## 1. Product in brief

**NyaySetu** is a secure, multilingual (Gujarati / Hindi / English) AI workspace for **Indian revenue-law firms**, starting with **Gujarat**. It turns scanned land records into verified title chains and evidence-linked court drafts, tracks limitation and hearings, searches revenue-authority and High Court rulings, and keeps a tamper-evident audit trail. An advocate reviews and approves every AI output. It assists advocates; it does not give legal advice.

**Users:** Firm Admin, Senior Partner, Associate Advocate, Paralegal, Legal Researcher (firm users); Client (external, portal, later). Later: Bank/NBFC analyst, government offices.

**Core flow:** create matter -> upload scanned records (7/12, 8A, Ferfar/mutation registers, sale deeds, orders) -> OCR + field extraction -> paralegal review -> title chain with flags -> evidence-linked drafting + citation verification -> partner approval -> DOCX/PDF export -> limitation/hearing tracking -> client updates.

**Priorities (from practising lawyers, in order):** 1) security, 2) drafting, 3) research / similar cases, 4) multilingual output.

**Unique angles to protect:** (1) evidence-linked drafting (every fact and citation links to its source page), (2) per-matter privacy receipt built from real facts, (3) Gujarati revenue-court focus (Collector, SSRD, Revenue Tribunal, High Court), (4) advocate-maintained limitation rules, (5) later: senior-advocate template library, Land Watch alerts (subject to portal terms), government pleader mode.

**Market context (public info, 2026; verify before pitching):** general Indian legal-AI tools (CaseMine, Manupatra AI, SCC Online, Jhana.ai, Lexlegis.AI, BharatLaw.AI) are broad, not built around revenue procedure; land-title companies (Landeed/Terra, TEAL, Landseek AI) focus on due diligence for banks, not on litigation drafting. The open space is revenue-litigation drafting + Gujarati + land-record understanding + strong security.

**Business model (planned):** subscription for advocates and firms; per-report pricing for banks/NBFCs; enterprise and on-premise licences. Rough budget assumption (not quotes): team Rs 50-90 lakh over 14 months; cloud+GPU Rs 0.5-2 lakh/month; legal/security audit Rs 3-8 lakh one-time.

---

## 2. Status snapshot

| Area | State |
| --- | --- |
| Frontend (React 19 + Vite + Tailwind, `NyaySetu-main`) | UI complete but **all mock data**; needs fixes before wiring (section 7) |
| Backend | Not started |
| Docs | PRD, architecture and DB, API and roadmap, AI review and risks written (in `docs/`) |
| Legal content (statutes, limitation rules, citations, templates) | **Unverified.** Needs advocate review |
| Corpus of judgments | Not sourced; licensing unresolved |
| Pilot advocates | Not recruited |

---

## 3. Locked decisions (summary; full list in section 14)

| ID | Decision |
| --- | --- |
| D-01 | **Modular monolith** (FastAPI), not microservices. |
| D-02 | PostgreSQL 16 is the main store: relational, full-text, trigram, `pgvector`, **Row-Level Security**. No separate vector DB or search engine in v1. |
| D-03 | **Celery + Redis** for OCR/AI/export/reminder jobs (not FastAPI BackgroundTasks). **SSE** for progress and notifications, not WebSockets. |
| D-04 | **Role and firm come only from the server.** No role switcher, no role chosen at login. Matter-level membership controls access. |
| D-05 | Out-of-scope resources return **404**, not 403. |
| D-06 | Auth: Argon2id, mandatory MFA, 15-min access JWT in memory, rotating refresh token in httpOnly cookie, CSRF header on refresh. |
| D-07 | **Audit is server-written, append-only, hash-chained**, in the same transaction as the change. Client never writes audit. |
| D-08 | AI runs **self-hosted in India**; no external AI API for client data; PII placeholders before generation; every call logged in `ai_runs`. |
| D-09 | Deterministic features stay deterministic: limitation calculator, citation verifier, approvals, permissions. |
| D-10 | Originals are immutable; corrections apply to extracted fields with history. |
| D-11 | Retention is **firm-configurable with legal hold**; no default "purge after filing". |
| D-12 | A draft can be approved only by a Partner, with zero unverified citations and zero unresolved placeholders; approval locks the version. Unapproved exports are watermarked. |
| D-13 | Clients see only items explicitly **published** for them. |
| D-14 | Gujarati/Devanagari digits and Unicode NFC are normalised on all text input and before indexing. |
| D-15 | IDs are UUIDv7; timestamps UTC (`timestamptz`), shown in IST; soft delete via `deleted_at`. |

---

## 4. Stack

| Area | Choice |
| --- | --- |
| Backend | Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2.0 (async, asyncpg), Alembic |
| Data | PostgreSQL 16 + pgvector, pg_trgm, citext, pgcrypto; Redis; S3-compatible storage (AWS S3 `ap-south-1` or MinIO) |
| Jobs | Celery (+ Beat), queues `ocr`, `ai`, `default`, `notify` |
| Auth | Argon2id, `pyotp` TOTP, JWT, SMS/email OTP for clients |
| AI | Self-hosted OCR (PaddleOCR or Tesseract+Gujarati, benchmark first), self-hosted LLM and embedding model behind adapters (choose after Gujarati evaluation) |
| Export | `python-docx` + HTML-to-PDF with Noto Sans Gujarati / Devanagari embedded |
| Scan | ClamAV |
| Observability | structlog JSON logs, OpenTelemetry, Prometheus/Grafana, Sentry (PII scrubbed) |
| Infra | Docker; Terraform; start on ECS/Fargate or VM pair; Kubernetes only if needed |
| Frontend | React 19, Vite, Tailwind 3, framer-motion, lucide-react; **to add:** React Router, TanStack Query, TypeScript, i18n, generated OpenAPI client |
| Not used | Microservices, GraphQL, Kafka, separate vector DB, blockchain, external AI APIs |

---

## 5. Engineering rules (every module)

- Layout: `app/core/`, `app/modules/<name>/{router,schemas,models,service,repository,permissions,tasks,tests}`, `app/workers/`. Modules call each other **only through `service.py`**.
- Every tenant table has `firm_id` + RLS (`app.firm_id`), FORCE RLS; app DB role is not superuser/BYPASSRLS.
- Every endpoint declares a capability; matter endpoints also check matter access. Never accept `role` or `firm_id` from the client.
- Errors: RFC 7807-style JSON with `code`, `status`, `detail`, `request_id`. Lists: `{items, next_cursor}`, cursor pagination, max limit 100.
- Optimistic concurrency with `row_version` (409 `version_conflict`). `Idempotency-Key` on creating POSTs.
- Versions are append-only for drafts, templates, field corrections, limitation rules.
- Logs: JSON with request id; **never** log bodies, tokens, document text or PII.
- Every state change and every sensitive read (document view, PII reveal, export, audit view) writes an audit event.
- Validation lives in `app/core/validators.py` and is shared (survey number, area H-A-Sq.m, dates, mobile, enrolment `<STATE>/<number>/<year>`, files).
- Tests: authorisation matrix (401 / 404 other firm / 404 non-member / 403 missing capability / success) for every endpoint; RLS isolation tests; 80% coverage on core modules.
- Migrations: one per change, reversible, single Alembic head.

---

## 6. Domain glossary (as used in the frontend; advocate to verify)

| Term | Meaning in this product |
| --- | --- |
| 7/12 (Village Form 7/12) | Land record of rights extract with survey number, occupant, area, tenure |
| 8A | Holding/khata register extract |
| Ferfar Nondh / Mutation entry (Nondh) | Register of changes in land records; each entry has a number and date |
| Hakpatrak | Record of rights register (Gujarati) |
| Survey no. / Khata no. | Land parcel identifier / holding account number |
| Area format `H-A-Sq.m` | Hectare-Are-Square metre, e.g. `1-22-00`; store raw string + total sq.m |
| Old Tenure / New Tenure (Navi Sharat) | Land tenure type; new tenure has restrictions |
| Mamlatdar | Taluka revenue officer who certifies mutation entries |
| Prant Officer (Deputy Collector) | Sub-division revenue authority; first appeal forum in the demo |
| Collector | District revenue authority |
| SSRD | Special Secretary (Revenue Department), revision/appeal forum |
| GRT | Gujarat Revenue Tribunal |
| BLRC | Bombay Land Revenue Code, 1879 (UI also says "Gujarat Land Revenue Code" - **canonical name to confirm**) |
| Sec. 135D, 203, 204, 205, 211 | Sections cited in the UI for notice, appeal, stay, limitation, revision. **Unverified**; treat as placeholders |
| RTS appeal | Term used in the UI; **confirm meaning** with an advocate |
| e-Dhara, Index-II | Government land-record and Sub-Registrar index sources named in the UI |
| Matter | A case or engagement in a law firm |

---

## 7. Frontend facts (what exists, what is wrong)

**Structure:** `src/App.jsx` (view switch via `useState`), `components/landing/{LandingPage,ArchitectureModal}`, `components/auth/{AuthPage,AdvocateAuthView}`, `components/workspace/FirmWorkspace` + tabs `{TabDocumentOcr, TabTitleChain, TabDraftingStudio, TabPrecedents, TabLimitation, TabAuditReceipt}`, `components/portal/ClientPortalView`, `constants/{matters,roles}.js`. No router, no API layer, no persistence, no tests, no TypeScript.

**Tab -> backend mapping:**

| UI tab / screen | Backend modules |
| --- | --- |
| Matter switcher + stage bar + dashboard (to build) | M3 matters |
| Document OCR & 7/12 viewer | M4 documents, M5 extraction |
| Title chain | M6 title |
| Drafting studio | M8 drafting + citations, M9 export, M12 AI |
| Precedents & research | M7 research |
| Limitation & cause list | M10 deadlines/hearings |
| Privacy & audit receipt | M2 audit, M11 receipt |
| Client portal (orphaned) | M13 portal |
| Login, invite, MFA, profile, admin (to build) | M1 auth/firms, M14 admin |

**Fix-first list (frontend, before/while wiring):**

1. Remove role selection at login and the header role switcher; use `/auth/me` capabilities.
2. Take the public client portal offline; rebuild as authenticated, invite/OTP based, published-updates only.
3. Remove all banned claims (section 10) from landing, auth, receipt, portal, architecture modal.
4. One canonical seed matter (below); delete contradicting demo data.
5. Add React Router, TanStack Query, TypeScript, generated API client, error boundaries.
6. Add matters list/dashboard, create matter, real upload with progress, real document viewer with bounding boxes.
7. Make drafts editable: canonical text + variables + grounds + evidence links + versions + review/approval flow.
8. Replace the hard-coded "today" (2026-11-04) and calendar-day limitation logic with server calculation and advocate-reviewed rules.
9. Add loading, empty and error states; minimum 12px text; focus handling; icons plus text for status.
10. Hindi text bug: Gujarati digit inside a Hindi draft ("२१૧"); add script/digit validators.

**Canonical demo fixture (proposal, founder to confirm; use for seeds, tests, demos):**

| Field | Value |
| --- | --- |
| Matter | `MAT-2026-0809` "Sec. 203 appeal before Dy. Collector (Bavla)" |
| Parcel | Survey 142/A, Khata 247, Moje Bavla, Taluka Bavla, District Ahmedabad |
| Area / assessment | 1-22-00 (H-A-Sq.m) = 12,200 sq.m; Rs 14.80 |
| Occupant (demo) | Patel Rameshchandra K. |
| Forum | Court of the Deputy Collector (Prant Officer), Dholka-Bavla |
| Title events | 410 - 18-05-1996 ancestral partition; 621 - 04-11-2008 registered sale deed (Rs 32,50,000); 809 - 14-07-2017 mutation certified after notice (**disputed**, challenged 08-01-2026); 842 - 14-08-2018 SBI Bavla agricultural mortgage Rs 8,50,000 (**active**). *Proposal changes the UI's entry 742 to 842 so numbers rise with dates.* |
| Impugned order | dated 08-01-2026 |
| Next hearing | 18-11-2026 11:30 (one source of truth: `hearings`) |
| Firm / users (demo) | Mehta & Associates; partner, associate, paralegal, researcher accounts with synthetic emails |
| Rule for all fixtures | Demo legal text is marked `DEMO - not legal authority`. Real precedents are loaded only from a licensed corpus. |

---

## 8. Module map and status

*Spec for each module: `docs/04_API_Spec_and_Module_Roadmap.md` Part B (M0-M14). Prompts are in `PROMPTS.md`.*

| Module | What | Prompt | Status | Where |
| --- | --- | --- | --- | --- |
| M0 | Foundation: app factory, config, db, logging, errors, CI, Docker | P01 | Done | `backend/app/`, `backend/alembic/`, `backend/tests/` |
| - | Core schema and RLS migrations | P02 | Done | `backend/app/core/models.py`, `backend/alembic/versions/4934e7e9f4f6_mvp_schema_and_rls.py`, `backend/app/db/seeds.py` |
| M1a | Auth, MFA, sessions, invitations, client OTP | P03 | Done | `backend/app/modules/auth/`, `backend/app/core/{auth_crypto,dependencies,permissions}.py` |
| M1b | Firms, users, roles, capabilities, retention settings | P04 | Not started | |
| M2 | Audit service (hash chain) | P05 | Not started | |
| M3 | Matters, parcels, members, stages, dashboard | P06 | Not started | |
| M3+ | Parties, reference data, hearings, notes, templates, saved research | P07 | Not started | |
| M4 | Documents and storage | P08 | Not started | |
| M5 | Jobs, OCR, extraction, redaction | P09 | Not started | |
| M6 | Title chain | P10 | Not started | |
| M7 | Research corpus and search | P11 | Not started | |
| M8 | Drafting, citations, review workflow | P12 | Not started | |
| M9 | Export DOCX/PDF | P13 | Not started | |
| M10 | Deadlines, limitation, reminders, notifications | P14 | Not started | |
| M11 | Privacy summary and receipt | P15 | Not started | |
| M12 | AI services | P16 | Not started | |
| M13 | Client portal | P17 | Not started | |
| M14 | Admin, retention, legal hold, hardening | P18 | Not started | |
| - | Testing strategy and suites | P19 | Not started | |
| - | Deployment and operations | P20 | Not started | |
| - | Documentation | P21 | Not started | |
| FE | Frontend foundation and wiring | F1 | Not started | |

**Build order:** P01 -> P02 -> P03 -> P04 -> P05 -> P06 -> P07 -> P08 -> P09 -> P10 -> P11 (start corpus sourcing early) -> P12 -> P13 -> P14 -> P15 -> P16 -> P17 -> P18. P19 starts with P01 and grows. P20 starts after P06 (staging). P21 runs throughout. F1 can start after P03 and continues as endpoints appear.
**MVP = M0-M11 (+ basic M12 flags).** V1 = full corpus, translation, AI suggestions, portal. V2 = bank/NBFC workspace, API, SSO, on-prem, second state.

---

## 9. Document index (`docs/`)

| File | Use it for | Key sections |
| --- | --- | --- |
| `docs/02_PRD.md` | What to build and why: personas, user stories (6.x), FRs (7), NFRs (8), business rules BR-xx and validation rules (9), permissions matrix (10), flows (11), notifications (12), errors (13), KPIs (14), roadmap (15) | 6, 7, 9, 10 most used |
| `docs/03_Backend_Architecture_and_Database.md` | How: stack (A2), modules (A4), tenancy (A5), auth flows (A6), encryption (A7), document pipeline (A8), AI boundary (A9), conventions (A10), deployment (A11), table catalogue (B2), DDL (B3), RLS (B4), indexes (B5), deletion rules (B6), audit/versioning (B7) | A4-A10, B2-B7 |
| `docs/04_API_Spec_and_Module_Roadmap.md` | API conventions and error format (A1-A3), rate limits (A4), logging (A5), endpoint catalogue (A7), Pydantic models (A8), validation (A9), authorisation tests (A10), modules M0-M14 with scope, files, tests, done criteria (Part B) | A7, Part B most used |
| `docs/05_AI_Review_and_Risks.md` | Which features use AI and which do not (A2), AI specs (A3), guardrails (A4), cost (A5), risks and mitigations (B1-B8) | A2-A4, B8 |

*Not in `docs/`:* the frontend review (findings are summarised in section 7).

---

## 10. Legal content, claims and compliance policy

**Legal content policy.** Statutes, sections, limitation rules, forums, templates and citations are **data with a named advocate reviewer, a review date, a source reference and a version**. Until reviewed they carry `needs_review` and the UI shows a notice. AI may not create statutory text or citations. Every citation in an approved draft must resolve to a corpus record or be marked "verified externally" by an advocate with a reason.

**Banned claims (unless proven and evidenced at the time):** "DPDP Act audited/certified", "MeitY audited", "Bar Council Rule 39 compliant", "air-gapped", "client HSM", "GovCloud", "zero hallucinations", "immutable block", "digitally signed with Bar Council credentials", "synchronised with Gujarat Revenue Department / Sub-Registrar / cause-list portals", "99.x% OCR accuracy" (use measured numbers with test-set description only), "Devanagari OCR" for Gujarati documents, "verified citation corpus" for demo data, fake match percentages.

**Allowed wording once true:** "encrypted at rest with per-firm keys", "data stored in India", "no client data used to train models", "audit log is hash-chained and verifiable", "approved internally by [advocate name]".

**Retention:** firm-configurable, legal hold overrides deletion, conservative defaults; confirm with counsel (open question Q-05).

**Disclaimer text (show at point of use):** "NyaySetu assists advocates and does not provide legal advice. Verify all outputs before filing."

---

## 11. Permissions summary (source of truth: `docs/02_PRD.md` section 10)

- **Admin:** firm settings, users, roles, retention, audit view/export, receipts. Does not work on matter content by default.
- **Partner:** everything on assigned matters (or all if `all_matters_access`); the only role that approves drafts and signs off title reports; publishes client updates.
- **Associate:** create matters, upload, edit fields, title chain, draft, submit, export (watermarked unless approved), deadlines, hearings.
- **Paralegal:** upload, verify/correct extracted fields, view title chain; no export, no approval.
- **Researcher:** search and save research; no upload, no field edits, no approval.
- **Client (portal):** only published updates for their own matters.

---

## 12. Open questions and assumptions

| ID | Question / assumption | Owner | Status |
| --- | --- | --- | --- |
| Q-01 | Is Gujarat the only launch state? (assumed yes) | Founder | Open |
| Q-02 | Which task costs advocates the most time (build and sell this first)? | Founder + advocates | Open |
| Q-03 | Which judgment and land-record sources may be lawfully indexed, under what licence? | Founder + counsel | Open |
| Q-04 | Who is the named advocate reviewer for statutes, limitation rules and templates? | Founder | Open |
| Q-05 | Retention defaults and Bar Council / court requirements | Counsel | Open |
| Q-06 | Is e-signature needed in v1, or is internal approval enough? | Founder | Open |
| Q-07 | Canonical statute name (BLRC vs "Gujarat Land Revenue Code") and meaning of "RTS appeal" | Advocate | Open |
| Q-08 | Confirm canonical demo fixture in section 7 (entry 742 -> 842 change) | Founder | Open |
| Q-09 | First paying customer type: individual advocates, firms, or banks? | Founder | Open |
| Q-10 | Web only for v1, or mobile app too? | Founder | Open |
| Q-11 | Consented sample documents (7/12, 8A, Ferfar, orders) for OCR benchmark: who provides? | Founder | Open |
| A-01 | Assumed: single region `ap-south-1`; managed Postgres; GPU only for AI workers | Eng | Assumption |

---

## 13. Environment and commands

*Fill in as modules are built. Format: command | what it does | introduced by (prompt).*

| Command / variable | Purpose | Prompt |
| --- | --- | --- |
| `docker compose up -d --build` | Starts api, postgres (pgvector), redis, minio | P01 |
| `pytest tests/ -v --tb=short` | Runs the test suite | P01 |
| `ruff check app/ tests/` | Lints backend code | P01 |
| `ruff format app/ tests/` | Auto-formats backend code | P01 |
| `mypy app/` | Runs type checks | P01 |
| `alembic upgrade head` | Applies pending database migrations | P01 |
| `alembic revision -m "<msg>"` | Generates a new Alembic migration | P01 |
| `NYAYSETU_ENV` | Environment profile (`local`, `staging`, `production`) | P01 |
| `DATABASE_URL` | PostgreSQL async connection string (`postgresql+asyncpg://...`) | P01 |
| `REDIS_URL` | Redis connection URL | P01 |
| `SECRET_KEY` | Application secret key for crypto and signing | P01 |
| `S3_ENDPOINT_URL`, `S3_ACCESS_KEY`, `S3_SECRET_KEY`, `S3_BUCKET_NAME`, `S3_REGION` | Object storage credentials and endpoint | P01 |
| `RATE_LIMIT_PER_MINUTE` | General rate limit default | P01 |
| `python -m app.db.seeds` | Seeds master reference data & canonical demo fixture idempotently | P02 |

---

## 14. Decision log (append only)

| ID | Date | Decision | Why | Prompt |
| --- | --- | --- | --- | --- |
| D-01..D-15 | 2026-11-05 | See section 3 | Planning phase (docs 02-05) | planning |
| D-16 | 2026-11-05 | Pure ASGI middleware pipeline (RequestID, AccessLog, SecurityHeaders) | Ensures request-id and headers wrap custom exception handlers cleanly | P01 |
| D-17 | 2026-11-05 | Refresh token cookie path set to `/api/v1/auth`, SameSite=Strict, Secure, HttpOnly, 7 days | Limits credential exposure to auth endpoints; paired with rotating refresh family and CSRF header validation | P03 |
| D-18 | 2026-11-05 | RLS policies enforced on all 36 tenant tables using `current_setting('app.firm_id', true)::uuid` and immutable trigger `trg_audit_events_immutable` preventing UPDATE/DELETE on `audit_events` | Enforces multitenancy at DB engine level and append-only tamper resistance for audit log (BR-10) | P02 |

*Add new rows as `D-16`, `D-17`... Never edit old rows; supersede with a new row that names the old ID.*

---

## 15. Progress log (append only)

**Template for every new entry:**

```
### YYYY-MM-DD | Prompt P## | <short title>
- Did: what was built (modules, tables, endpoints, files)
- Where: key paths
- Tests: what runs, how many pass, coverage
- Deviations: anything that differs from docs/ or this file, and why
- New decisions: D-xx
- Open questions: Q-xx
- Next: the next prompt and anything it needs from this one
```

### 2026-10 | Planning | Product concept, features, early blueprint

- Did: defined the product (AI lawyer-assistant focused on revenue law); friends in the sector ranked security first, then drafting, research, multilingual. Produced a 14-feature list (voice input removed), data-flow diagrams (level 0 and 1), a 14-month implementation blueprint (architecture, roadmap, team, budget, risks), competitor scan, unique-feature ideas, and a project summary.
- Where: earlier PDFs and project summary outside this repo (Revenue_AI_Features, Revenue_AI_Plan_DFD, Revenue_AI_Implementation_Blueprint, Revenue_AI_Project_Summary).
- Next: frontend review.

### 2026-11-05 | Planning | Frontend review and documentation set

- Did: reviewed the completed frontend as a product (about 120 findings), wrote PRD, backend architecture and database design, API spec and module roadmap, AI review and risk register, and the AI coding prompts; created this BRAIN.md and `PROMPTS.md`.
- Where: `docs/02`-`docs/05`, `BRAIN.md`, `PROMPTS.md`.
- Tests: n/a.
- Deviations: none.
- New decisions: D-01..D-15.
- Open questions: Q-01..Q-11.
- Next: P01 (foundation); in parallel, start corpus sourcing (Q-03), recruit pilot advocates, and begin frontend fix-first items (F1).

### 2026-11-05 | Prompt P01 | M0 Foundation and platform skeleton

- Did: Created `backend/` skeleton with `app/core/` (config, db, errors, logging, pagination, ratelimit, security, tenancy, text), `app/modules/health/`, `app/workers/celery_app.py`, `alembic/` with reversible baseline extension migration, pure ASGI request-ID/access-logging/security-headers middleware, standard RFC 7807 error responses, Docker Compose with pgvector + redis + minio, multi-stage non-root Dockerfile, Makefile, pre-commit config, and GitHub Actions CI.
- Where: `backend/app/`, `backend/alembic/`, `backend/tests/`, `backend/Dockerfile`, `backend/docker-compose.yml`, `backend/.github/workflows/ci.yml`.
- Tests: 24 tests passed across health checks, RFC 7807 error format, request-ID propagation, cursor pagination/sorting, unicode NFC/Gujarati-Devanagari digit conversion, single Alembic head and migration reversibility.
- Deviations: none from BRAIN.md. Error schema aligned exactly with docs/04 A2 (`type`, `code`, `title`, `status`, `detail`, `request_id`, `errors`).
- New decisions: D-16.
- Open questions: none new.
- Next: P02 (Core schema and RLS migrations).

### 2026-11-05 | Prompt P02 | MVP Schema, Alembic Migrations, RLS, and Demo Fixture Seeds

- Did: Implemented declarative SQLAlchemy 2.0 schema for MVP modules M1 through M11 (59 tables, mixins for UUIDv7, timestamps, soft delete, tenancy, optimistic concurrency `row_version`). Created reversible Alembic migration `4934e7e9f4f6_mvp_schema_and_rls.py` enabling & forcing Row-Level Security on all 36 tenant tables, partial unique indexes for soft delete, GIN trigram & HNSW vector indexes, and tamper-proofing trigger `trg_audit_events_immutable` on `audit_events`. Built idempotent database seeder (`app/db/seeds.py`) populating master forums, BLRC 1879 statute sections (flagged `needs_review`), and the Section 7 canonical demo fixture (Mehta & Associates firm, 4 users, matter MAT-2026-0809, parcel 142/A, title events 410, 621, 809, 842, encumbrances, and hearings).
- Where: `backend/app/core/models_base.py`, `backend/app/core/models.py`, `backend/alembic/versions/4934e7e9f4f6_mvp_schema_and_rls.py`, `backend/app/db/seeds.py`, `backend/tests/test_schema.py`, `backend/tests/test_migrations.py`.
- Tests: 36 tests passed in pytest across schema constraints, seed idempotency, tenant isolation semantics, composite primary key constraints on audit_events, migration reversibility, auth/MFA/lockout, and platform foundation.
- Deviations: None. Later-phase tables (e.g. `client_accounts`, `portal_updates`, `source_treatments`, `draft_translations`, `legal_holds`, `retention_policies`, `data_requests`, `feedback`) excluded per prompt instructions.
- New decisions: D-18.
- Open questions: None new.
- Next: P04 (Module M1b - Firms, users, roles, capabilities, retention settings).
