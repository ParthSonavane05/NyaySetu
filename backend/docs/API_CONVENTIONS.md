# API Conventions — NYAYSETU Backend (P06)

> **Treat this document as binding.** Any deviation must be approved and documented here.

---

## 1. URL Structure

| Pattern | Example |
|---------|---------|
| `/api/v1/<resource>` | `/api/v1/matters` |
| `/api/v1/<resource>/{id}` | `/api/v1/matters/{matter_id}` |
| `/api/v1/<resource>/{id}/<sub>` | `/api/v1/matters/{matter_id}/members` |
| `/api/v1/<resource>/{id}/<action>` | `/api/v1/matters/{matter_id}/transition` |

- **Plural nouns** for collections: `/matters`, `/parties`, `/parcels`
- **Action verbs** for state mutations: `/transition`, `/archive`
- No trailing slashes

---

## 2. HTTP Methods

| Method | Semantics |
|--------|-----------|
| `GET` | Read — never mutates state |
| `POST` | Create a new resource or trigger an action |
| `PATCH` | Partial update (JSON Merge Patch style) |
| `DELETE` | Soft or hard delete per resource rules |
| `PUT` | Not used — PATCH preferred |

---

## 3. Response Envelope

### Success

```json
{
  "id": "uuid",
  "field": "value"
}
```

Collections return a pagination envelope:

```json
{
  "items": [...],
  "next_cursor": "base64string | null",
  "has_more": true,
  "total_returned": 20
}
```

### Error

FastAPI default — RFC 7807 style:

```json
{
  "detail": "Human-readable error message"
}
```

---

## 4. Pagination (D-12)

- **Cursor-based** pagination using `(created_at, id)` composite cursor
- Cursor is base64url-encoded JSON: `{"ts": "ISO8601", "id": "uuid"}`
- Query params: `?limit=20&cursor=<opaque>`
- Max limit: 100

---

## 5. Idempotency (D-07)

- `POST /matters` accepts `Idempotency-Key` header
- Same key → same response (cached for 24 h)
- Key stored in `matters.idempotency_key` (unique per firm)

---

## 6. Optimistic Locking (D-06)

- All PATCH requests must include `row_version` matching the current DB value
- Mismatch → `409 Conflict`

---

## 7. Access Control (D-05)

> **Never return 403.** Access-denied → 404.

| Role | Scope |
|------|-------|
| `admin` | All matters in firm |
| `partner` with `all_matters_access=true` | All matters in firm |
| `associate` / others | Only matters where they are a `MatterMember` |

---

## 8. Stage Transitions

Valid forward chain (no note required):

```
INTAKE → DUE_DILIGENCE → DRAFTING → REVIEW → FILED → CLOSED
```

Backward transitions require a `note` in the request body.

`ARCHIVED` is only reachable via `POST /matters/{id}/archive` — **never** via `/transition`.

---

## 9. Audit Trail (§8 Canonical Actions)

| Action | Trigger |
|--------|---------|
| `matter.created` | New matter |
| `matter.patched` | PATCH update |
| `matter.transitioned` | Stage change |
| `matter.archived` | Archive |
| `matter.member.added` | Member added |
| `matter.member.removed` | Member removed |
| `matter.party.created` | Party created |
| `matter.party.patched` | Party updated |
| `matter.party.deleted` | Party deleted |
| `matter.parcel.created` | Parcel created |
| `matter.parcel.patched` | Parcel updated |
| `matter.parcel.deleted` | Parcel deleted |

---

## 10. Encryption (§5)

- Party names (`name_enc`) stored as **Fernet-encrypted ciphertext**
- Key: `settings.SECRET_KEY` (base64url-encoded 32-byte key)
- Decrypted before returning in API responses
- Rotation strategy: re-encrypt all ciphertexts with new key, update `SECRET_KEY`

---

## 11. Survey Number Normalisation (D-09)

- Gujarati-script digits → ASCII digits
- Gujarati suffix vowels → ASCII letter equivalents
- Result uppercased
- Pattern: `<digits>[/<digits>][/<letter>]`
- Examples: `"૧૪૨/અ"` → `"142/A"`, `"142/a"` → `"142/A"`

---

## 12. Area Format (D-10)

Gujarat revenue area format: `H-A-Sq.m`

| Input | Hectares | Ares | Sq.m | Total Sq.m |
|-------|----------|------|------|-----------|
| `2-15-500` | 2 | 15 | 500 | 22,000 |
| `0-05-250` | 0 | 5 | 250 | 750 |

Stored as `area_sqm` (Decimal 18,4) and human label `area_label`.

---

## 13. Headers

| Header | Used in | Description |
|--------|---------|-------------|
| `X-User-Id` | All requests | Current user UUID (stub in P06) |
| `X-Firm-Id` | All requests | Current firm UUID (stub in P06) |
| `X-Role` | All requests | User role: `admin`, `partner`, `associate` |
| `X-All-Matters` | All requests | `"true"` grants full firm scope |
| `Idempotency-Key` | POST /matters | Dedup key (max 128 chars) |

---

## 14. Versioning

- Current version: `v1`
- Breaking changes → new version prefix (`/api/v2/`)
- Non-breaking additions are backwards compatible within `v1`
