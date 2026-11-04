import {
  Scale,
  FileText,
  UserCheck,
  Search
} from 'lucide-react';

export const FIRM_ROLES = [
  {
    id: 'partner',
    label: 'Senior Partner',
    shortLabel: 'Senior Partner',
    desc: 'Full chamber administration & court filing sign-off',
    icon: Scale,
    permissions: 'Full chamber privileges: Final pleading sign-off, client fee allocation, firm policy control, and partner-level audit oversight.',
    badge: 'FULL CHAMBER ADMINISTRATION',
    defaultEmail: 'advocate@mehtachambers.in',
  },
  {
    id: 'associate',
    label: 'Associate Advocate',
    shortLabel: 'Associate Advocate',
    desc: 'Draft editing, citation verifier, court calendar',
    icon: FileText,
    permissions: 'Drafting studio access, primary statutory citation linking, SSRD & High Court appeal formulation, and junior review rights.',
    badge: 'DRAFTING & CITATION ACCESS',
    defaultEmail: 'advocate@mehtachambers.in',
  },
  {
    id: 'paralegal',
    label: 'Paralegal',
    shortLabel: 'Paralegal',
    desc: 'Document ingestion, OCR validation, metadata entry',
    icon: UserCheck,
    permissions: 'Restricted to document ingestion and title extraction review. Approval rights disabled.',
    badge: 'INGESTION & AUDIT ONLY',
    defaultEmail: 'advocate@mehtachambers.in',
  },
  {
    id: 'researcher',
    label: 'Legal Researcher',
    shortLabel: 'Legal Researcher',
    desc: 'SSRD precedent search, limitation calculator',
    icon: Search,
    permissions: 'Search and index access across Gujarat Revenue Tribunal, High Court, and SSRD case laws. Matter drafting restricted.',
    badge: 'JURISPRUDENCE SEARCH ONLY',
    defaultEmail: 'advocate@mehtachambers.in',
  },
];
