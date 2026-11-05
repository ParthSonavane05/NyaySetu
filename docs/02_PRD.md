# NyaySetu - Product Requirements Document (PRD)

*Phase 3. Version 1.0 draft. Builds on `01_Frontend_Review_and_Gap_Analysis.md`. Legal content (sections, limitation periods, citations) must be validated by a practising revenue advocate before release.*

---

## 1. Product vision

NyaySetu is a secure, multilingual workspace where Indian revenue-law firms turn scanned land records into verified title chains and evidence-linked court drafts, with every action auditable and every AI output reviewed by an advocate before it leaves the firm.

**One-line positioning:** *Revenue-law litigation and title diligence, built for Gujarat first, with privacy you can show a client.*

## 2. Problem statement

Revenue lawyers lose days on: reading scanned and handwritten records (7/12, 8A, Ferfar, mutation registers) in Gujarati; tracing 30+ years of title; finding relevant revenue-authority and High Court rulings; rewriting near-identical appeals and revisions; and tracking limitation and hearings across forums. Existing legal-AI tools are general-purpose and do not understand land records or revenue procedure, and firms hesitate to upload client files to tools they cannot inspect.

## 3. Goals

| # | Goal | Measure |
|---|---|---|
| G1 | Cut time from "documents received" to "first reviewable draft" | Median under 2 hours vs 1-2 days baseline (validate in pilot) |
| G2 | Make drafts trustworthy | 100% of citations verified or flagged before approval |
| G3 | Prevent missed deadlines | Zero missed limitation dates on tracked matters |
| G4 | Make privacy visible and provable | Privacy receipt available for every matter |
| G5 | Reach paying firms | 20 paying firms by month 12 after MVP |

## 4. Non-goals (v1)

- Not a general legal research tool for all practice areas.
- No outcome prediction or "chance of winning".
- No autonomous filing with courts; no direct e-filing in v1.
- No replacement of advocate judgement. All outputs are assistance.
- No live scraping of government portals unless a stable, permitted source is confirmed.
- No marketplace, billing, or time-tracking in v1.
- No states other than Gujarat in v1.

## 5. Target users and personas

| Persona | Description | Primary needs | Key pains |
|---|---|---|---|
| **Senior Partner** (Rajesh, 50) | Owns firm and client relationships; signs off filings | Fast review, confidence in citations, firm-wide control, proof of privacy | Time to review; fear of fake citations; client confidentiality |
| **Associate Advocate** (Anita, 30) | Drafts appeals/revisions, argues in court | Fast first drafts, evidence links, deadline alerts, Gujarati/English output | Re-typing templates; missing a ground; tracking hearings |
| **Paralegal** (Parth, 26) | Ingests documents, validates extraction | Quick upload, clear review queue, easy corrections | Manual data entry from poor scans |
| **Legal Researcher** (Meera, 28) | Finds precedents and builds research notes | Accurate search, full judgments, save to matter | Scattered sources, Gujarati orders hard to search |
| **Firm Admin** (office manager or partner) | Manages users, retention, audit | Easy user setup, audit export, policy controls | Compliance questions from clients |
| **Client** (Ramesh, 55, landowner) | Wants to know where the case stands | Simple Gujarati updates, hearing dates | Does not understand legal terms; cannot reach lawyer |
| **Bank/NBFC analyst** (Phase 3+) | Needs title reports for loans | Standard report, fast turnaround | Slow external lawyers |

## 6. User stories and acceptance criteria

*Priority: M = MVP, V1 = first release after MVP, V2 = later.*

### 6.1 Accounts and firm

| ID | Story | Pri |
|---|---|---|
| US-01 | As a firm admin I can register my firm and invite users by email so my team can join. | M |
| US-02 | As a user I must set up MFA so my account is protected. | M |
| US-03 | As a firm admin I can assign each user a role and revoke access. | M |
| US-04 | As a user I can reset my password and see my active sessions and sign out other devices. | M |
| US-05 | As a firm admin I can set retention and legal-hold rules. | V1 |
| US-06 | As a firm admin I can enable SSO. | V2 |

**Acceptance (US-02):** Given a new user accepts an invite, when they first sign in, then they cannot reach any matter until TOTP (or OTP) enrolment is complete; Given 5 failed attempts in 10 minutes, then the account is locked for 15 minutes and the admin is notified.

### 6.2 Matters

| ID | Story | Pri |
|---|---|---|
| US-10 | As an associate I can create a matter with forum, statute, parties, survey numbers, and team. | M |
| US-11 | As a partner I can see all firm matters; others see only matters they are assigned to. | M |
| US-12 | As a user I can search, filter and sort matters by stage, forum, deadline, assigned lawyer. | M |
| US-13 | As a partner I can move a matter through stages and archive it. | M |
| US-14 | As an associate I can run a conflict check on parties before opening a matter. | V1 |

**Acceptance (US-11):** Given user A is not on matter M, when A requests M by ID, then the response is 404, and the attempt is audit-logged.

### 6.3 Documents and extraction

| ID | Story | Pri |
|---|---|---|
| US-20 | As a paralegal I can upload PDFs/images to a matter and see processing status. | M |
| US-21 | As a paralegal I can view the scan with extracted fields highlighted and correct any field. | M |
| US-22 | As a paralegal I can see a queue of low-confidence fields needing review. | M |
| US-23 | As a user I can mask PII; masked renditions never contain the original text. | M |
| US-24 | As a user I can tag documents by type and source, and group multiple documents per survey number. | M |
| US-25 | As a paralegal I can enter fields manually when OCR fails. | M |
| US-26 | As a user I can see version history of any corrected field. | V1 |

**Acceptance (US-20):** Given I upload a 20 MB PDF, then upload progress is shown, a processing job is created, status moves Queued -> Processing -> Ready or Failed (with reason), and the action is audit-logged. Unsupported types or files over the limit are rejected with a clear message before upload begins.

**Acceptance (US-23):** Given PII masking is on, when I view or download the masked rendition, then the original text is not present in the file or API response. Revealing PII requires permission and writes an audit event.

### 6.4 Title chain

| ID | Story | Pri |
|---|---|---|
| US-30 | As an associate I can see a chronological title chain built from verified mutation entries. | M |
| US-31 | As an associate I can see flagged issues (gap, area mismatch, active encumbrance, conflicting owner). | M |
| US-32 | As an associate I can open the source page for any entry. | M |
| US-33 | As a partner I can generate and sign off a title search report. | V1 |

### 6.5 Drafting

| ID | Story | Pri |
|---|---|---|
| US-40 | As an associate I can create a draft from a template; matter facts fill the variables. | M |
| US-41 | As an associate I can edit grounds, reorder, and insert evidence, statutes and precedents. | M |
| US-42 | As an associate I can see which citations are verified, unverified, or not found. | M |
| US-43 | As an associate I can submit a draft for review; the partner can comment, request changes, or approve. | M |
| US-44 | As a partner I can approve only when no citation is unverified and no placeholder is unfilled. | M |
| US-45 | As an associate I can export DOCX and PDF in court format. Unapproved exports are watermarked "DRAFT". | M |
| US-46 | As an associate I can view a Gujarati or Hindi version marked "translation - needs review". | V1 |
| US-47 | As an associate I can ask the assistant to suggest grounds from matter facts, each with citations. | V1 |
| US-48 | As a partner I can manage firm templates. | V1 |

**Acceptance (US-44):** Given a draft has one unverified citation, when the partner clicks Approve, then the action is blocked with the list of offending citations; when all are resolved, approval locks the version and records approver, time, and version hash.

### 6.6 Research

| ID | Story | Pri |
|---|---|---|
| US-50 | As a researcher I can search judgments by keyword or natural language in English or Gujarati. | M |
| US-51 | As a researcher I can filter by court, year, statute section and bench. | M |
| US-52 | As a researcher I can open the full judgment and see the exact matching passage with paragraph number. | M |
| US-53 | As a researcher I can save results to a matter. | M |
| US-54 | As a researcher I can flag treatment (followed, distinguished, overruled). | V1 |

### 6.7 Deadlines and hearings

| ID | Story | Pri |
|---|---|---|
| US-60 | As an associate I can compute a limitation deadline and see how it was counted. | M |
| US-61 | As an associate I can record hearings per matter. | M |
| US-62 | As a user I get reminders at 7, 3 and 1 day before a deadline or hearing. | M |
| US-63 | As a partner I see a firm-wide deadline dashboard. | M |
| US-64 | As a user I can subscribe to an `.ics` calendar feed. | V1 |

**Acceptance (US-60):** Given an order service date and a rule, when I calculate, then the result shows start day, excluded days (with reason), holidays applied, rule source, and a disclaimer; the calculation is saved with the rule version used.

### 6.8 Audit and privacy

| ID | Story | Pri |
|---|---|---|
| US-70 | As a partner I can view and filter the audit trail for a matter. | M |
| US-71 | As a partner I can export a privacy receipt (PDF) for a matter. | M |
| US-72 | As an admin I can export the audit log (CSV). | V1 |

### 6.9 Client portal

| ID | Story | Pri |
|---|---|---|
| US-80 | As a client I can sign in with OTP on my registered mobile number. | V1 |
| US-81 | As a client I see only updates my advocate published, in Gujarati or English. | V1 |
| US-82 | As an advocate I can publish a plain-language update and hearing date to the client. | V1 |
| US-83 | As a client I get WhatsApp/SMS when a new update is published. | V1 |

### 6.10 Admin and notifications

| ID | Story | Pri |
|---|---|---|
| US-90 | As a user I see in-app notifications and optional email for assignments, reviews, deadlines. | M |
| US-91 | As an admin I see usage and storage per firm. | V1 |

---

## 7. Functional requirements

*FR IDs map to modules in doc 04.*

| ID | Requirement | Pri |
|---|---|---|
| FR-AUTH-1 | Email + password login with mandatory MFA; password min 12 chars, breached-password check | M |
| FR-AUTH-2 | Short-lived access token + rotating refresh token; revoke on logout/password change | M |
| FR-AUTH-3 | Account lockout, rate limits, new-device notice | M |
| FR-AUTH-4 | Invitation flow with expiry (72h) | M |
| FR-TEN-1 | Every record belongs to one firm; cross-firm access is impossible | M |
| FR-RBAC-1 | Roles: Firm Admin, Partner, Associate, Paralegal, Researcher, Client (external) | M |
| FR-RBAC-2 | Matter-level membership controls access; partners may be set to "all matters" | M |
| FR-MAT-1 | Matter CRUD, stage workflow with allowed transitions, archive (not delete) | M |
| FR-MAT-2 | Multiple parcels (survey numbers) and multiple parties per matter | M |
| FR-DOC-1 | Upload PDF/JPG/PNG/TIFF up to 50 MB per file; antivirus scan; checksum; duplicate detection | M |
| FR-DOC-2 | Originals immutable; processing creates renditions (page images, redacted copy) | M |
| FR-OCR-1 | Async OCR producing text, boxes, per-field confidence | M |
| FR-OCR-2 | Field review workflow: accept, edit, reject; track who verified | M |
| FR-OCR-3 | Server-side PII redaction renditions; reveal needs permission and logs | M |
| FR-TITLE-1 | Mutation entries and encumbrances stored as structured records linked to source pages | M |
| FR-TITLE-2 | Rules flag gaps, area mismatch, active charges, owner conflicts | M |
| FR-DRAFT-1 | Templates with variables, versioned | M |
| FR-DRAFT-2 | Draft = ordered grounds + prayer + evidence/citation links; version on every save | M |
| FR-DRAFT-3 | Review workflow: draft -> in review -> changes requested -> approved (locked) | M |
| FR-DRAFT-4 | Export DOCX/PDF with embedded Gujarati/Hindi fonts; watermark unless approved | M |
| FR-CITE-1 | Citation verifier checks each citation against the indexed corpus; statuses: verified, unverified, not found | M |
| FR-RES-1 | Hybrid search (keyword + semantic) over judgments with filters and snippets | M |
| FR-RES-2 | Full-text judgment viewer with paragraph anchors | M |
| FR-LIM-1 | Limitation rules table (act, section, forum, days, exclusions, source, version, reviewed_by) | M |
| FR-LIM-2 | Holiday calendar per state/court; deadline calculation with explanation | M |
| FR-LIM-3 | Reminders via in-app/email; WhatsApp/SMS in V1 | M/V1 |
| FR-AUD-1 | Append-only, hash-chained audit events written only by the server | M |
| FR-AUD-2 | Privacy receipt PDF from real data | M |
| FR-NOT-1 | In-app notifications with read/unread; email delivery | M |
| FR-CLI-1 | Client accounts, OTP login, published-update feed | V1 |
| FR-ADM-1 | User management, role assignment, retention policy, legal hold | M/V1 |

## 8. Non-functional requirements

| Category | Requirement |
|---|---|
| Security | TLS 1.2+; AES-256 at rest; envelope encryption with per-firm data keys; secrets in a manager; OWASP ASVS L2 targeted; dependency scanning; annual penetration test |
| Privacy | Data stored in India region; no client data used to train models; PII minimisation; consent and notice flows; data export/deletion requests; DPDP-aligned processes (confirm with counsel) |
| Performance | p95 API under 400 ms for reads; search p95 under 1.5 s; upload initiation under 1 s; OCR of a 10-page document under 3 min (async); draft export under 30 s |
| Availability | 99.5% monthly at launch; 99.9% target in year 2 |
| Backup and recovery | Daily backups, point-in-time recovery; RPO 15 min, RTO 4 h |
| Scalability | Support 200 firms, 5,000 users, 1 million document pages in year 1 without redesign |
| Accessibility | WCAG 2.1 AA; keyboard navigable; minimum 12px text; screen-reader labels |
| Internationalisation | UI in English, Gujarati, Hindi; Unicode NFC; Gujarati/Devanagari digit normalisation in search |
| Browser support | Latest two versions of Chrome, Edge, Safari, Firefox; responsive from 360px |
| Observability | Structured logs with request IDs (no PII), metrics, tracing, alerting on errors and queue depth |
| Auditability | All reads of sensitive data and all writes are audit-logged |
| Data integrity | Soft delete; versioned drafts and corrected fields; checksums on files |
| Maintainability | OpenAPI-first; migrations via Alembic; 80%+ test coverage on core modules |

## 9. Business rules and validation rules

### 9.1 Business rules

| ID | Rule |
|---|---|
| BR-01 | Role comes only from the server. No user can switch their own role. |
| BR-02 | A user can access a matter only if they are a matter member, or a partner with "all matters" access. |
| BR-03 | Original uploaded documents are immutable. Corrections apply to extracted fields, not originals. |
| BR-04 | A draft can be approved only by a Partner who is not the sole author (configurable), with zero unverified citations and zero unresolved placeholders. |
| BR-05 | Approval locks the draft version. Further edits create a new version that needs re-approval. |
| BR-06 | Final (approved) exports are unwatermarked; all other exports carry a "DRAFT - NOT FOR FILING" watermark. |
| BR-07 | Clients see only items explicitly published for them. Privileged notes and grounds are never client-visible. |
| BR-08 | Researchers can search and save research but cannot upload documents, edit extracted fields, or approve drafts. |
| BR-09 | Paralegals can upload and verify extraction but cannot export or approve drafts. |
| BR-10 | Audit events cannot be edited or deleted by any user, including admins. |
| BR-11 | Retention is firm-configurable. Default: retain until the firm archives and requests deletion; legal hold overrides deletion. (Do not default to "purge after filing".) |
| BR-12 | Limitation results always show the rule, version, and counting steps, and a notice that the advocate must confirm. |
| BR-13 | AI outputs are never saved as final text without a user action. Every AI-generated item is labelled and logged. |
| BR-14 | Citations in approved drafts must resolve to a corpus record or be manually marked "verified externally" by an advocate with a reason. |

### 9.2 Validation rules

| Field | Rule |
|---|---|
| Email | RFC-valid, lowercase-normalised, firm domain optional policy |
| Password | 12-128 chars, not in breached list, not equal to email |
| MFA code | 6 digits, 30-second window, 1 step tolerance |
| Mobile | E.164, +91 default, 10 digits after country code |
| Bar enrolment | `<STATE>/<number>/<year>` pattern, e.g. `GJ/1842/2016`; year 1950 to current |
| Survey number | Alphanumeric with `/` and optional suffix, e.g. `142/A`, `304/1`, `142/1/P2`; max 30 chars; Gujarati digits normalised |
| Khata number | Digits, max 12 |
| Area (H-A-Sq.m) | Pattern `H-AA-SS` where are 0-99 and sq.m 0-99; stored as raw string and total sq.m integer |
| Dates | ISO 8601 stored; displayed DD/MM/YYYY; not before 1800; not more than 1 year in future (except hearings and deadlines) |
| Currency | INR, non-negative, 2 decimals |
| Files | PDF, JPG, PNG, TIFF; max 50 MB; max 300 pages; reject encrypted PDFs with a clear message |
| Matter number | System generated: `MAT-<YYYY>-<seq>` per firm |
| Draft | No unfilled placeholders at approval; title and forum required |
| Text | Normalise to Unicode NFC; strip control characters |

## 10. Roles and permissions matrix

*Y = allowed, M = only for assigned matters, - = not allowed.*

| Capability | Admin | Partner | Associate | Paralegal | Researcher | Client |
|---|---|---|---|---|---|---|
| Manage users/roles/retention | Y | - | - | - | - | - |
| View all firm matters | Y | Y (setting) | - | - | - | - |
| Create matter | Y | Y | Y | - | - | - |
| View assigned matter | Y | Y | M | M | M | M (published only) |
| Upload documents | - | M | M | M | - | - |
| Verify/correct extracted fields | - | M | M | M | - | - |
| Reveal masked PII | - | M | M | M (logged) | - | - |
| View title chain | - | M | M | M | - | - |
| Edit drafts | - | M | M | - | - | - |
| Submit for review | - | M | M | - | - | - |
| Approve draft | - | M | - | - | - | - |
| Export approved draft | - | M | M | - | - | - |
| Export unapproved draft (watermarked) | - | M | M | - | - | - |
| Search research | - | Y | Y | Y | Y | - |
| Save research to matter | - | M | M | - | M | - |
| Compute/edit deadlines | - | M | M | M (view) | - | - |
| Manage hearings | - | M | M | - | - | - |
| View matter audit trail | Y | M | Own actions | Own actions | Own actions | - |
| Download privacy receipt | Y | M | - | - | - | - |
| Publish client update | - | M | M | - | - | - |

## 11. User flows

**F1. Firm onboarding:** Landing -> Request demo/Register firm -> admin verifies email -> sets password -> enrols MFA -> invites users -> users accept invite, set password, enrol MFA -> land on dashboard.

**F2. New matter to first draft:** Create matter (parties, forum, survey numbers, team) -> upload documents -> OCR jobs run -> paralegal reviews low-confidence fields -> title chain builds with flags -> associate selects template -> variables auto-fill -> associate edits grounds, links evidence, inserts precedents -> citation verifier runs -> submit for review.

**F3. Review and approval:** Partner opens review queue -> reads draft with evidence links -> comments or requests changes -> associate revises (new version) -> partner approves (blocked if unverified citations) -> version locked -> export final.

**F4. Deadline handling:** Order received -> associate enters service date and picks rule -> system shows deadline and steps -> reminders scheduled -> dashboard flags due-soon -> on filing, associate marks filed -> reminders stop.

**F5. Client update:** Advocate writes plain-language update (Gujarati) -> publishes -> client gets SMS/WhatsApp -> client signs in with OTP -> reads update and next hearing.

**F6. Privacy receipt:** Partner opens matter -> Privacy & Audit -> generates receipt -> PDF lists documents, processing steps, region, key status, retention date, and audit hash anchor.

## 12. Notifications

| Trigger | Recipient | Channel | Pri |
|---|---|---|---|
| Invitation | New user | Email | M |
| Matter assigned | Assignee | In-app, email | M |
| Document processed / failed | Uploader | In-app | M |
| Fields need review | Paralegal | In-app | M |
| Draft submitted for review | Partner | In-app, email | M |
| Draft approved / changes requested | Author | In-app, email | M |
| Deadline in 7/3/1 days; overdue | Matter team, partners | In-app, email, WhatsApp/SMS (V1) | M |
| Hearing in 3/1 days | Matter team, client (if published) | In-app, email, SMS/WhatsApp | M/V1 |
| New device sign-in | User | Email | M |
| Account locked | User, admin | Email | M |
| Client update published | Client | SMS/WhatsApp | V1 |
| Retention/deletion due | Admin | Email | V1 |

## 13. Error handling

| Case | User-facing behaviour |
|---|---|
| Validation error | Field-level message; form keeps input |
| Unauthenticated / expired session | Redirect to login, return to the same page after |
| Forbidden / not a matter member | Show "not found" (no information leak) |
| Upload failure | Show reason, offer retry; resumable for large files |
| OCR failure | Status Failed with reason; "Enter manually" option |
| AI/search service down | Feature shows "unavailable, try again"; rest of app works |
| Rate limit | Message with retry time |
| Conflict (edit collision) | "Someone else changed this" with compare and merge |
| Unexpected error | Generic message plus request ID the user can quote to support |

All API errors use a single format (doc 04) with machine-readable `code`, message, and `request_id`.

## 14. Success metrics and KPIs

| Metric | Target (6 months after MVP) |
|---|---|
| Pilot firms active weekly | 10 |
| Time to first draft | Median under 2 hours |
| Draft edit rate (share of AI/template text changed) | Tracked, used to improve |
| OCR field accuracy on held-out set | Agreed with advocates; start with 90% on key fields |
| Citations verified at approval | 100% |
| Missed deadlines on tracked matters | 0 |
| Weekly active users per firm seat | 60%+ |
| Net Promoter Score (advocates) | 40+ |
| Support tickets per 100 matters | Under 10 |
| Paying firms | 20 by month 12 |
| Security incidents | 0 |

## 15. Release roadmap

| Release | Content |
|---|---|
| **MVP (months 1-5)** | Accounts, MFA, RBAC, matters, upload, OCR, review queue, redaction, title chain v1, drafting editor with 4 templates, citation verifier, review/approval, export, basic research on a seed corpus, limitation rules v1, hearings, notifications, audit, privacy receipt |
| **V1 (months 6-9)** | Full research corpus, Gujarati/Hindi translation with review, AI draft suggestions, client portal, WhatsApp/SMS, title search report, firm templates, retention and legal hold, calendar feed |
| **V2 (months 10-14)** | Bank/NBFC workspace, API, SSO/SCIM, on-premise option, second state, audit exports to SIEM |
| **Later** | Marketplace for advocate templates, Land Watch alerts (portal terms permitting), government pleader mode |

## 16. Open questions for the founder and advocates

1. Which three drafts do advocates write most often? (Confirm templates beyond the four mocked.)
2. Which sources of judgments and records may legally be indexed, and under what licence?
3. Who verifies statutory text and limitation rules, and how often?
4. Are advocates comfortable with a client-facing portal, and what may clients see?
5. What retention periods do firms require, and are there Bar Council or court requirements?
6. Is e-signature needed in v1, or is internal approval enough?
7. Will early customers insist on on-premise or private cloud?
