"""Role to capability definitions (Docs 02 section 10 and Docs 04 A7).

Single source of truth for the RBAC permissions matrix.
"""

from __future__ import annotations

# Exact capabilities from Docs 04 A7 and Docs 02 section 10:
# Manage users/roles/retention -> user.manage, firm.manage
# View all firm matters -> matter.view_all
# Create matter -> matter.create
# View assigned matter -> matter.view
# Upload documents -> document.upload
# Verify/correct extracted fields -> field.verify, field.edit
# Reveal masked PII -> pii.reveal
# View title chain -> title.view
# Edit drafts -> draft.edit
# Submit for review -> draft.submit
# Approve draft -> draft.approve
# Export approved draft -> draft.export
# Export unapproved draft (watermarked) -> draft.export_unapproved
# Search research -> research.search
# Save research to matter -> research.save
# Compute/edit deadlines -> deadline.edit, deadline.view
# Manage hearings -> hearing.edit, hearing.view
# View matter audit trail -> audit.view, audit.view_own
# Download privacy receipt -> receipt.generate, receipt.download
# Publish client update -> portal.publish

ROLE_CAPABILITIES: dict[str, set[str]] = {
    "admin": {
        "user.manage",
        "user.view",
        "firm.manage",
        "matter.view_all",
        "matter.create",
        "audit.view",
        "audit.export",
        "receipt.generate",
        "receipt.download",
    },
    "partner": {
        "matter.view_all",
        "matter.view",
        "matter.create",
        "matter.edit",
        "matter.stage",
        "matter.archive",
        "matter.team",
        "matter.hold",
        "document.upload",
        "document.download",
        "document.edit",
        "document.delete",
        "field.edit",
        "field.verify",
        "pii.reveal",
        "title.view",
        "title.edit",
        "title.report",
        "title.signoff",
        "draft.view",
        "draft.create",
        "draft.edit",
        "draft.submit",
        "draft.comment",
        "draft.approve",
        "draft.export",
        "draft.export_unapproved",
        "research.search",
        "research.save",
        "deadline.view",
        "deadline.edit",
        "hearing.view",
        "hearing.edit",
        "audit.view",
        "receipt.generate",
        "receipt.download",
        "portal.publish",
    },
    "associate": {
        "matter.view",
        "matter.create",
        "matter.edit",
        "matter.stage",
        "matter.archive",
        "matter.team",
        "document.upload",
        "document.download",
        "document.edit",
        "field.edit",
        "field.verify",
        "pii.reveal",
        "title.view",
        "title.edit",
        "draft.view",
        "draft.create",
        "draft.edit",
        "draft.submit",
        "draft.comment",
        "draft.export_unapproved",
        "draft.export",
        "research.search",
        "research.save",
        "deadline.view",
        "deadline.edit",
        "hearing.view",
        "hearing.edit",
        "audit.view_own",
        "portal.publish",
    },
    "paralegal": {
        "matter.view",
        "document.upload",
        "document.download",
        "document.edit",
        "field.edit",
        "field.verify",
        "pii.reveal",
        "title.view",
        "research.search",
        "deadline.view",
        "audit.view_own",
    },
    "researcher": {
        "matter.view",
        "research.search",
        "research.save",
        "audit.view_own",
    },
    "client": {
        "matter.view",  # published only
        "portal.view",
    },
}

# Mapping of PRD Section 10 human capability names to internal permission keys for verification & documentation
PRD_CAPABILITY_MAP: dict[str, dict[str, str]] = {
    "Manage users/roles/retention": {
        "admin": "Y",
        "partner": "-",
        "associate": "-",
        "paralegal": "-",
        "researcher": "-",
        "client": "-",
    },
    "View all firm matters": {
        "admin": "Y",
        "partner": "Y",
        "associate": "-",
        "paralegal": "-",
        "researcher": "-",
        "client": "-",
    },
    "Create matter": {
        "admin": "Y",
        "partner": "Y",
        "associate": "Y",
        "paralegal": "-",
        "researcher": "-",
        "client": "-",
    },
    "View assigned matter": {
        "admin": "Y",
        "partner": "Y",
        "associate": "M",
        "paralegal": "M",
        "researcher": "M",
        "client": "M",
    },
    "Upload documents": {
        "admin": "-",
        "partner": "M",
        "associate": "M",
        "paralegal": "M",
        "researcher": "-",
        "client": "-",
    },
    "Verify/correct extracted fields": {
        "admin": "-",
        "partner": "M",
        "associate": "M",
        "paralegal": "M",
        "researcher": "-",
        "client": "-",
    },
    "Reveal masked PII": {
        "admin": "-",
        "partner": "M",
        "associate": "M",
        "paralegal": "M",
        "researcher": "-",
        "client": "-",
    },
    "View title chain": {
        "admin": "-",
        "partner": "M",
        "associate": "M",
        "paralegal": "M",
        "researcher": "-",
        "client": "-",
    },
    "Edit drafts": {
        "admin": "-",
        "partner": "M",
        "associate": "M",
        "paralegal": "-",
        "researcher": "-",
        "client": "-",
    },
    "Submit for review": {
        "admin": "-",
        "partner": "M",
        "associate": "M",
        "paralegal": "-",
        "researcher": "-",
        "client": "-",
    },
    "Approve draft": {
        "admin": "-",
        "partner": "M",
        "associate": "-",
        "paralegal": "-",
        "researcher": "-",
        "client": "-",
    },
    "Export approved draft": {
        "admin": "-",
        "partner": "M",
        "associate": "M",
        "paralegal": "-",
        "researcher": "-",
        "client": "-",
    },
    "Export unapproved draft (watermarked)": {
        "admin": "-",
        "partner": "M",
        "associate": "M",
        "paralegal": "-",
        "researcher": "-",
        "client": "-",
    },
    "Search research": {
        "admin": "-",
        "partner": "Y",
        "associate": "Y",
        "paralegal": "Y",
        "researcher": "Y",
        "client": "-",
    },
    "Save research to matter": {
        "admin": "-",
        "partner": "M",
        "associate": "M",
        "paralegal": "-",
        "researcher": "M",
        "client": "-",
    },
    "Compute/edit deadlines": {
        "admin": "-",
        "partner": "M",
        "associate": "M",
        "paralegal": "M",
        "researcher": "-",
        "client": "-",
    },
    "Manage hearings": {
        "admin": "-",
        "partner": "M",
        "associate": "M",
        "paralegal": "-",
        "researcher": "-",
        "client": "-",
    },
    "View matter audit trail": {
        "admin": "Y",
        "partner": "M",
        "associate": "Own actions",
        "paralegal": "Own actions",
        "researcher": "Own actions",
        "client": "-",
    },
    "Download privacy receipt": {
        "admin": "Y",
        "partner": "M",
        "associate": "-",
        "paralegal": "-",
        "researcher": "-",
        "client": "-",
    },
    "Publish client update": {
        "admin": "-",
        "partner": "M",
        "associate": "M",
        "paralegal": "-",
        "researcher": "-",
        "client": "-",
    },
}


def get_capabilities_for_role(role: str) -> list[str]:
    """Return alphabetical list of capabilities granted to a role."""
    return sorted(ROLE_CAPABILITIES.get(role.lower(), set()))


def generate_matrix_markdown() -> str:
    """Generate Markdown representation matching Docs 02 Section 10."""
    roles = ["Admin", "Partner", "Associate", "Paralegal", "Researcher", "Client"]
    header = "| Capability | " + " | ".join(roles) + " |"
    separator = "|---|---|---|---|---|---|---|"
    lines = [header, separator]

    for capability, perms in PRD_CAPABILITY_MAP.items():
        row = f"| {capability} | " + " | ".join(perms[r.lower()] for r in roles) + " |"
        lines.append(row)

    return "\n".join(lines) + "\n"
