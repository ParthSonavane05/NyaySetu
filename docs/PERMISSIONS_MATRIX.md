# NyaySetu RBAC Permissions Matrix

*Generated from single source of truth `app/core/permissions.py` according to Docs 02 Section 10 and Docs 04 A7.*

| Capability | Admin | Partner | Associate | Paralegal | Researcher | Client |
|---|---|---|---|---|---|---|
| Manage users/roles/retention | Y | - | - | - | - | - |
| View all firm matters | Y | Y | - | - | - | - |
| Create matter | Y | Y | Y | - | - | - |
| View assigned matter | Y | Y | M | M | M | M |
| Upload documents | - | M | M | M | - | - |
| Verify/correct extracted fields | - | M | M | M | - | - |
| Reveal masked PII | - | M | M | M | - | - |
| View title chain | - | M | M | M | - | - |
| Edit drafts | - | M | M | - | - | - |
| Submit for review | - | M | M | - | - | - |
| Approve draft | - | M | - | - | - | - |
| Export approved draft | - | M | M | - | - | - |
| Export unapproved draft (watermarked) | - | M | M | - | - | - |
| Search research | - | Y | Y | Y | Y | - |
| Save research to matter | - | M | M | - | M | - |
| Compute/edit deadlines | - | M | M | M | - | - |
| Manage hearings | - | M | M | - | - | - |
| View matter audit trail | Y | M | Own actions | Own actions | Own actions | - |
| Download privacy receipt | Y | M | - | - | - | - |
| Publish client update | - | M | M | - | - | - |

**Legend:**
- `Y`: Allowed across firm
- `M`: Only for assigned matters (membership or all-matters partner setting)
- `Own actions`: Scoped to events where `actor_id == current_user_id`
- `-`: Forbidden (403 if in scope, 404 if out of scope)

