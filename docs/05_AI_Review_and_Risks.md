# NyaySetu - AI Feature Review & Risk Register

*Phases 8 and 9.*

---

# Part A. AI feature review

## A1. Principles

1. **AI only where rules cannot do the job.** Limitation dates, permissions, approvals, audit, and citation verification are **deterministic**, never generative.
2. **Grounded or nothing.** Any generated legal text must point to source references (documents, statutes, passages). If no source exists, the system says so.
3. **Human in the loop.** AI output is a suggestion; an advocate accepts it. Nothing is auto-approved or auto-filed.
4. **Private by design.** Self-hosted models in India; PII redacted before model calls; no training on client data; every call logged.
5. **Measure before promising.** Ship accuracy numbers from your own test sets, not marketing percentages.

## A2. Feature-by-feature review

| # | Feature | Is AI actually needed? | Verdict |
|---|---|---|---|
| 1 | OCR of Gujarati/Hindi land records | Yes, no practical alternative | **MVP** |
| 2 | Field extraction from OCR text (survey no., khata, area, owner, mutation entries) | Hybrid: rules and layout first, LLM as fallback | **MVP** |
| 3 | PII detection and redaction | Hybrid: regex and name lists plus NER model | **MVP** |
| 4 | Hybrid semantic search over judgments | Yes (embeddings help with paraphrase and Gujarati/English mix) | **MVP** |
| 5 | Citation verifier | **No AI.** Deterministic matching against the corpus | **MVP** |
| 6 | Limitation calculator | **No AI.** Rules engine | **MVP** |
| 7 | Title-chain flags | **Rules first.** LLM only to suggest explanations | **MVP (rules)** |
| 8 | Template variable filling | **No AI.** Direct mapping from matter data | **MVP** |
| 9 | Draft ground suggestions | Yes, with mandatory references | **V1** |
| 10 | Translation (en, gu, hi) | Yes, with legal glossary and human review | **V1** |
| 11 | Summarising judgments and orders | Yes, extractive-first | **V1** |
| 12 | Language improvement of a selected paragraph | Yes, low risk | **V1** |
| 13 | Order analyzer (suggest grounds of appeal from an adverse order) | Yes, but high-risk; needs checklist-based design | **V2** |
| 14 | Document risk check (forgery, inconsistency) | Mostly rules (area mismatch, date errors); ML later | **V2** |
| 15 | Plain-language client updates (Gujarati) | Yes, advocate-reviewed before publishing | **V1/V2** |
| 16 | Outcome prediction | Not credible with available data; liability risk | **Do not build** |
| 17 | Chatbot for clients answering legal questions | High risk of giving legal advice | **Do not build** |

## A3. Detailed specs for each recommended AI feature

### AI-1. Gujarati/Hindi OCR

| | |
|---|---|
| **Purpose** | Convert scanned 7/12, 8A, Ferfar, sale deed and order pages to text with positions. |
| **User value** | Removes manual typing; enables search and evidence linking by page region. |
| **Model type** | OCR engine (open-source, e.g. PaddleOCR or Tesseract with Gujarati data), optionally fine-tuned on consented firm documents; layout detection for table forms. |
| **Inputs** | Page image (deskewed, denoised), language hints. |
| **Outputs** | Text lines/words with bounding boxes and confidences; page-level quality score. |
| **Cost** | CPU or small GPU; low per page. Fine-tuning cost is one-time. |
| **Privacy** | Runs in own VPC; images never leave. |
| **Phase** | **MVP.** Benchmark 2-3 engines on your own documents before choosing. |
| **Caveats** | Handwriting and Modi script are much harder than printed Gujarati. Do not promise them until measured; provide manual entry fallback. Correct the UI claim "Devanagari OCR" for Gujarati documents. |

### AI-2. Field extraction

| | |
|---|---|
| **Purpose** | Map OCR output to structured fields and mutation entries. |
| **User value** | Pre-filled review form; builds the title chain. |
| **Model type** | Template/rule extraction for known forms (7/12, 8A); LLM with JSON-schema output as fallback for free-text mutation notes. |
| **Inputs** | OCR text and boxes, document type. |
| **Outputs** | `{field_key, value_raw, value_norm, confidence, page, bbox}`; validators (area format, date, survey format) mark low-confidence or invalid values `needs_review`. |
| **Cost** | Small per document; LLM only for fallbacks. |
| **Privacy** | PII redaction not applied here (needs the real names) so this step runs only on the in-VPC model; no external API. |
| **Phase** | **MVP** (rules plus validators), LLM fallback in V1. |

### AI-3. PII detection and redaction

| | |
|---|---|
| **Purpose** | Mask names, phone, Aadhaar-like numbers, addresses before sharing or before generative steps. |
| **User value** | Safer sharing and a smaller blast radius for AI steps. |
| **Model type** | Regex and checksum rules for ID numbers; NER model for names; match against party names known from the matter. |
| **Inputs / outputs** | OCR text with boxes -> PII spans with boxes -> redacted rendition (pixel masks) and masked text. |
| **Cost** | Low. |
| **Privacy** | Server-side only; the original is never exposed to the client when masked. |
| **Phase** | **MVP.** |

### AI-4. Hybrid search over judgments

| | |
|---|---|
| **Purpose** | Find relevant revenue rulings by concept, section, or fact pattern. |
| **User value** | Cuts research time; finds Gujarati orders that keyword search misses. |
| **Model type** | Multilingual embedding model + Postgres FTS + trigram; reciprocal-rank fusion; optional cross-encoder re-ranker later. |
| **Inputs** | Query text and filters. |
| **Outputs** | Ranked passages with snippets, citations, links. No invented percentages. |
| **Cost** | One-time embedding of corpus; low query cost. |
| **Privacy** | Corpus is public legal text; queries can reveal matter facts, so log queries only as hashed/minimal and keep them tenant-private. |
| **Phase** | **MVP** (seed corpus), full corpus V1. |
| **Dependency** | Licensed or lawfully obtained corpus; this, not the model, is the hard part. |

### AI-5. Draft ground suggestions

| | |
|---|---|
| **Purpose** | Propose grounds of appeal or revision from matter facts and linked evidence. |
| **User value** | Speeds the first draft and reduces missed grounds. |
| **Model type** | Self-hosted LLM with retrieval; structured output: `{ground_text, references[]}`. |
| **Inputs** | Verified extracted facts, title flags, selected template, retrieved statute sections and precedent passages. |
| **Outputs** | Candidate grounds each tied to at least one reference; items without references are dropped. |
| **Cost** | Moderate (GPU). Control with quotas and caching. |
| **Privacy** | Runs in VPC; redact party names to placeholders (`[APPELLANT]`) in prompts and restore after. |
| **Guardrails** | Citation verifier runs on every output; unsupported claims are flagged; label "AI suggested"; never auto-insert. |
| **Phase** | **V1.** |

### AI-6. Translation with glossary

| | |
|---|---|
| **Purpose** | Produce Gujarati/Hindi/English versions of drafts and client updates. |
| **User value** | Multilingual drafting is a core promise. |
| **Model type** | LLM or dedicated MT model, constrained by a legal glossary (term pairs) and fixed citation strings. |
| **Inputs** | Canonical draft text, target language, glossary. |
| **Outputs** | Translated text with citations and numbers unchanged; parity check (same number of grounds and references); status `machine` until an advocate marks `reviewed`. |
| **Cost** | Moderate. |
| **Privacy** | In VPC. |
| **Phase** | **V1.** Build the glossary with advocates first. |

### AI-7. Summaries of judgments and orders

| | |
|---|---|
| **Purpose** | Short summary: facts, issue, holding, relief. |
| **User value** | Faster triage of long orders. |
| **Model type** | Extractive-first (select key passages), then LLM rewrite with paragraph references. |
| **Output** | Summary with paragraph pointers; "AI summary - verify against the judgment". |
| **Phase** | **V1.** |

### AI-8. Order analyzer

| | |
|---|---|
| **Purpose** | Highlight possible procedural and substantive defects in an adverse order. |
| **Model type** | Checklist-driven prompts (notice, hearing, jurisdiction, limitation, reasoning) over the order text. |
| **Risk** | High; false confidence can mislead. Provide as "points to examine", with quotes from the order. |
| **Phase** | **V2**, after real usage data. |

### AI-9. Document risk check

| | |
|---|---|
| **Purpose** | Flag area mismatches, date inconsistencies, duplicate survey numbers across documents. |
| **Model type** | Rules first; anomaly detection later. |
| **Phase** | **V1 (rules)**, ML in V2. |

## A4. Cross-cutting AI requirements

| Area | Requirement |
|---|---|
| Model hosting | Self-hosted open-weight models behind adapters; swap without API change; GPU node isolated from the internet except for model downloads in build stage |
| Model selection | Evaluate candidates on **your** Gujarati test sets (extraction, translation, summarisation) before choosing; record model name/version in `ai_runs` |
| Evaluation | Maintain gold datasets per task; run on every model or prompt change; block release on regression |
| Prompt injection | Documents are untrusted input. Separate instructions from data, strip tool access, validate output against a schema, never execute instructions found inside documents |
| Hallucination control | Require references; verifier; refuse when evidence is missing; show uncertainty |
| Logging | `ai_runs`: model, version, prompt hash, input IDs, tokens, latency, outcome. Do not store raw prompts or text unless the firm opts in |
| Quotas and cost | Per-firm daily quotas; queue priority; caching of embeddings and repeat calls; track cost per matter |
| Privacy | No external API; PII placeholders before generation; retention for AI logs aligned to firm policy; no training on client data (contractual and technical) |
| Transparency | UI labels every AI-generated item; privacy receipt lists which AI steps ran on which documents |
| Feedback | Thumbs and reason on suggestions; use only aggregate, de-identified signals for improvement, and only with consent |
| Disclaimer | The product assists advocates and does not give legal advice; show at point of use |

## A5. Rough cost considerations

| Item | Notes |
|---|---|
| OCR | CPU is often enough; GPU speeds up large batches |
| Embeddings | One-time corpus embedding plus per-query; small |
| LLM inference | The main cost. One GPU node for MVP evaluation; scale with usage; use smaller models for extraction and larger ones only for drafting |
| Storage | Page images dominate; use lifecycle rules to move old pages to cold storage |
| Human review | Advocate time for glossary, rules, gold sets is a real cost; budget for it |

Get actual quotes for GPU instances in the India region and test throughput on your chosen models before fixing pricing.

---

# Part B. Risk register

*Likelihood (L) and Impact (I): H/M/L.*

## B1. Technical risks

| ID | Risk | L | I | Mitigation |
|---|---|---|---|---|
| T1 | OCR accuracy too low on old/handwritten Gujarati and Modi records | H | H | Benchmark early; scope MVP to printed/typed forms; manual entry path; collect consented samples to fine-tune; show per-field confidence |
| T2 | LLM quality in Gujarati insufficient | M | H | Evaluate on gold sets before committing; keep English as canonical; translation requires review; glossary constraints |
| T3 | Overcomplicated architecture slows delivery | M | M | Modular monolith; Postgres for search; defer Kafka/microservices |
| T4 | Search relevance poor | M | H | Relevance test set; hybrid ranking; feedback loop; curate corpus |
| T5 | Export formatting fails court norms | M | M | Advocate-reviewed golden files; per-forum format profiles |
| T6 | Async pipeline failures leave documents stuck | M | M | Idempotent steps, retries, dead-letter queue, status page, stuck-job alerts |
| T7 | Gujarati text edge cases (digits, conjuncts, normalisation) break search and validation | H | M | NFC and digit normalisation everywhere; test fixtures with mixed scripts |
| T8 | Vendor/model licence limits | L | M | Check licences of models and fonts before launch |

## B2. Product risks

| ID | Risk | L | I | Mitigation |
|---|---|---|---|---|
| P1 | Advocates do not trust AI output | H | H | Evidence links, citation verifier, approval workflow, show sources, start with assistive features |
| P2 | Wrong problem prioritised | M | H | Interview 10 advocates; instrument usage; build what saves the most hours first |
| P3 | Scope creep (many tabs, little depth) | H | M | MVP limited to upload -> extract -> title chain -> draft -> approve -> deadline |
| P4 | Marketing claims exceed reality | H | H | Remove unverifiable claims; publish measured results only |
| P5 | Law changes make templates and rules stale | M | H | Versioned rules with reviewer and effective dates; change alerts; quarterly review |
| P6 | Single-state niche too small | M | M | Plan state packs (rules, templates, corpus) as a repeatable unit |
| P7 | Clients misread portal updates | M | M | Advocate-published plain-language updates only |

## B3. Security risks

| ID | Risk | L | I | Mitigation |
|---|---|---|---|---|
| S1 | Cross-tenant data leak | M | Critical | RLS plus code checks; automated isolation tests; pen test |
| S2 | IDOR on matters, documents, client portal | H | Critical | 404 on out-of-scope; authorisation test suite per endpoint; opaque IDs |
| S3 | Account takeover | M | High | MFA mandatory, Argon2id, lockout, new-device alerts, session revocation |
| S4 | Malicious uploads (malware, PDF exploits) | M | High | AV scan, sandboxed rendering workers, MIME sniffing, size limits |
| S5 | Prompt injection through uploaded documents | M | High | Treat as untrusted, schema validation, no tool access, no secrets in prompts |
| S6 | Secrets or tokens leaked in logs | M | High | Log scrubbing, secret manager, no body logging |
| S7 | Insider misuse | M | High | Least privilege, matter-level access, audit of reads and exports, alerts on mass downloads |
| S8 | Tampered audit log | L | High | Append-only, hash chain, anchors, nightly verification |
| S9 | Supply-chain vulnerabilities | M | M | Pinned dependencies, scanning, SBOM, minimal images |
| S10 | Public claims of compliance without evidence | H | High | Compliance claims only after an actual assessment |
| S11 | Backup or object storage misconfiguration | L | Critical | Private buckets, block public access, IaC review, restore drills |

## B4. Scalability and performance risks

| ID | Risk | L | I | Mitigation |
|---|---|---|---|---|
| SC1 | OCR queue backlog during bulk uploads | M | M | Separate queues, autoscaled workers, per-firm concurrency limits, progress UI |
| SC2 | Vector/FTS performance as corpus grows | M | M | HNSW tuning, partitioning, caching, move to OpenSearch only if measured need |
| SC3 | GPU cost spikes | M | M | Quotas, batching, smaller models for simple tasks, caching |
| SC4 | Large PDFs exhaust memory | M | M | Page-streaming, size and page limits, worker memory caps |
| SC5 | Audit table growth | M | L | Partition by firm/month, archive old partitions |
| SC6 | Hot tenants affect others | L | M | Per-firm rate limits and queue fairness |

## B5. Data risks

| ID | Risk | L | I | Mitigation |
|---|---|---|---|---|
| D1 | Corpus licensing or provenance problems | M | High | Record source and licence per batch; legal review; prefer official/public sources |
| D2 | Wrong extracted data enters a filing | M | Critical | Review queue, verified-only title chain, approval blocks, evidence links |
| D3 | Retention conflicts (deleting records advocates must keep) | M | High | Firm-configurable retention, legal hold, conservative defaults, counsel review |
| D4 | Data loss | L | Critical | PITR, object versioning, cross-region backup copy in India, restore drills |
| D5 | Inconsistent demo/seed data propagates | H | M | One canonical fixture; tests assert consistency |
| D6 | PII exposure through AI logs | M | High | Do not store prompts by default; hash inputs; redact before generation |
| D7 | Cross-border transfer concerns | L | High | India-region hosting; no external AI; sub-processor list; counsel review |

## B6. UX risks

| ID | Risk | L | I | Mitigation |
|---|---|---|---|---|
| U1 | Dense UI with tiny text tires users | H | M | Minimum 12px, simpler layouts, progressive disclosure |
| U2 | Gujarati rendering or input issues | M | M | Embedded fonts, input method testing, IME-friendly editor |
| U3 | Approval friction slows firms | M | M | Clear queues, mobile review, configurable approval rules |
| U4 | Users miss warnings (colour only) | M | M | Icons plus text; blocking dialogs for critical flags |
| U5 | Mobile unusable in court | M | M | Responsive layouts, offline-friendly read views for hearings |
| U6 | Over-trust in AI | H | High | Labels, visible uncertainty, mandatory verification steps |
| U7 | Client confusion from legal jargon | M | M | Plain-language Gujarati updates, advocate reviewed |

## B7. Legal and regulatory risks (to confirm with counsel)

| ID | Risk | Mitigation |
|---|---|---|
| R1 | Product perceived as giving legal advice | Assistive positioning, disclaimers, advocate approval, no client-facing legal Q&A |
| R2 | Bar Council or court rules on technology use and confidentiality | Obtain legal opinion; share compliance statement only after review |
| R3 | DPDP obligations (notice, consent, grievance, breach notification, children's data) | Appoint a contact, build consent and request workflows, breach runbook |
| R4 | Copyright in judgments and commentary | Use public-domain/official text or licensed sources; store provenance |
| R5 | E-signature and filing norms | Do not claim digital signing until integrated with a recognised provider |

## B8. Top 10 risks to act on first

1. S2 IDOR (design 404-for-out-of-scope and test it on day one).
2. S1 tenant isolation (RLS from the first migration).
3. T1 OCR accuracy (benchmark before building the rest of the pipeline).
4. D1 corpus licensing (start sourcing now; it takes longest).
5. P4/S10 unverifiable claims (remove from the frontend immediately).
6. D2 wrong data in filings (review queue and approval blocks).
7. D3 retention defaults (get counsel's view).
8. T2 Gujarati LLM quality (evaluate before committing to features).
9. P1 trust (evidence links and verifier are the product).
10. S3 account takeover (mandatory MFA from launch).
