import React, { useState } from 'react';
import {
  ChevronDown,
  LogOut,
  Check,
  Sparkles
} from 'lucide-react';
import { FIRM_ROLES } from '../../constants/roles';
import { SAMPLE_MATTERS } from '../../constants/matters';

// Import Tabs
import TabDocumentOcr from './tabs/TabDocumentOcr';
import TabTitleChain from './tabs/TabTitleChain';
import TabDraftingStudio from './tabs/TabDraftingStudio';
import TabPrecedents from './tabs/TabPrecedents';
import TabLimitation from './tabs/TabLimitation';
import TabAuditReceipt from './tabs/TabAuditReceipt';

export default function FirmWorkspace({
  currentUser,
  currentRole: propRole,
  userRole,
  activeMatter: propActiveMatter,
  onMatterChange: propOnMatterChange,
  firmUser,
  onSignOut,
  onRoleChange,
}) {
  const currentRole = propRole || FIRM_ROLES.find((r) => r.id === userRole) || currentUser?.role || firmUser?.role || FIRM_ROLES[0];
  const [activeMatterId, setActiveMatterId] = useState(propActiveMatter || '809');
  const [activeTab, setActiveTab] = useState('ocr'); // 'ocr' | 'chain' | 'draft' | 'precedents' | 'limitation' | 'audit'

  // Dynamic citations inserted from Precedent Research into Drafting Studio
  const [insertedCitations, setInsertedCitations] = useState([]);

  // Toast notification state
  const [toastMessage, setToastMessage] = useState(null);

  // Append-only audit logs
  const [auditLogs, setAuditLogs] = useState([
    {
      time: '14:22',
      actor: 'Paralegal (P. Joshi)',
      action: 'Uploaded 7_12_kalol_scanned_extract.pdf into Vault',
      hash: 'sha256:4a9f2...8b1',
    },
    {
      time: '14:35',
      actor: 'Associate Advocate (A. Sharma)',
      action: 'Formulated Ground A: Statutory notice under Sec. 135D',
      hash: 'sha256:7c10d...4e3',
    },
    {
      time: '15:10',
      actor: 'Senior Partner (K. Mehta, Sr. Adv.)',
      action: 'Reviewed 30-Year Title Chain & flagged Entry 742 bank charge',
      hash: 'sha256:9f82a...901',
    },
  ]);

  const activeMatter = SAMPLE_MATTERS.find((m) => m.id === activeMatterId) || SAMPLE_MATTERS[0];

  const showToast = (msg) => {
    setToastMessage(msg);
    setTimeout(() => {
      setToastMessage((prev) => (prev === msg ? null : prev));
    }, 3200);
  };

  const logAction = (actionText) => {
    const now = new Date();
    const timeStr = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`;
    const hash = `sha256:${Math.random().toString(16).substring(2, 7)}...${Math.random().toString(16).substring(2, 5)}`;
    
    setAuditLogs((prev) => [
      {
        time: timeStr,
        actor: `${currentRole.shortLabel} (${firmUser?.email?.split('@')[0] || 'User'})`,
        action: actionText,
        hash,
      },
      ...prev,
    ]);
  };

  const handleInsertCitation = (precedent) => {
    setInsertedCitations((prev) => [...prev, precedent]);
  };

  const stages = [
    { id: 'ocr', label: '7/12 Ingestion', completed: true },
    { id: 'chain', label: '30-Year Title Chain', completed: true },
    { id: 'draft', label: 'Drafting Grounds', current: true },
    { id: 'partner_review', label: 'Partner Review', pending: true },
    { id: 'court_filing', label: 'Court Filing', pending: true },
  ];

  return (
    <div className="min-h-screen bg-obsidian text-light-gray flex flex-col font-sans selection:bg-champagne/30 selection:text-light-gray">
      {/* 1. TOP CHAMBER HEADER (Sticky Glass Surface) */}
      <header className="sticky top-0 z-40 w-full backdrop-blur-xl bg-slate-glass border-b border-hairline px-4 sm:px-6 lg:px-8 py-3 transition-colors shadow-lg">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row md:items-center justify-between gap-3">
          {/* Left: Wordmark & Understated Active Matter Badge */}
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2">
              <span className="text-light-gray font-semibold text-sm tracking-[0.22em]">
                NYAYSETU
              </span>
              <span className="px-1.5 py-0.5 rounded text-[8px] font-mono tracking-widest uppercase bg-graphite border border-hairline text-titanium">
                LAW FIRM CORE
              </span>
            </div>

            <div className="hidden sm:inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-graphite/80 border border-hairline text-[10px] font-mono text-champagne">
              <span className="w-1.5 h-1.5 rounded-full bg-champagne animate-pulse" />
              <span>{activeMatter.badgeText}</span>
            </div>
          </div>

          {/* Center: Quick Matter Switcher Dropdown */}
          <div className="flex items-center gap-2">
            <span className="text-[10px] font-mono text-titanium uppercase hidden lg:inline">
              MATTER DOSSIER:
            </span>
            <div className="relative">
              <select
                value={activeMatterId}
                onChange={(e) => {
                  const newId = e.target.value;
                  setActiveMatterId(newId);
                  if (propOnMatterChange) propOnMatterChange(newId);
                  const m = SAMPLE_MATTERS.find((mat) => mat.id === newId);
                  showToast(`Switched active matter to #${newId}: ${m?.title}`);
                  logAction(`Switched matter docket to #${newId}`);
                }}
                className="w-full sm:w-auto px-3 py-1.5 rounded-xl bg-graphite border border-hairline hover:border-champagne/60 text-light-gray text-xs font-medium focus:outline-none focus:border-champagne transition-colors pr-8 appearance-none cursor-pointer"
              >
                {SAMPLE_MATTERS.map((matter) => (
                  <option key={matter.id} value={matter.id}>
                    {matter.title}
                  </option>
                ))}
              </select>
              <ChevronDown className="w-3.5 h-3.5 text-titanium absolute right-2.5 top-2.5 pointer-events-none" />
            </div>
          </div>

          {/* Right Actions: Role Switcher Dropdown, DPDP Pill, Sign Out */}
          <div className="flex items-center gap-3 sm:gap-4">
            {/* Interactive Role Switcher Dropdown */}
            <div className="flex items-center gap-1.5">
              <span className="text-[10px] font-mono text-muted-gray uppercase hidden xl:inline">
                ROLE:
              </span>
              <div className="relative">
                <select
                  value={currentRole.id}
                  onChange={(e) => {
                    const r = FIRM_ROLES.find((role) => role.id === e.target.value);
                    if (r) {
                      onRoleChange(r);
                      showToast(`Role switched to: ${r.label}`);
                      logAction(`Switched role session to ${r.shortLabel}`);
                    }
                  }}
                  className="px-3 py-1.5 rounded-xl bg-graphite border border-champagne text-champagne text-xs font-mono font-medium focus:outline-none transition-colors pr-7 appearance-none cursor-pointer shadow-sm ring-1 ring-champagne/30"
                >
                  {FIRM_ROLES.map((role) => (
                    <option key={role.id} value={role.id}>
                      {role.shortLabel}
                    </option>
                  ))}
                </select>
                <ChevronDown className="w-3 h-3 text-champagne absolute right-2 top-2.5 pointer-events-none" />
              </div>
            </div>

            {/* DPDP Vault Status Pill */}
            <div className="hidden md:inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-slate-glass border border-hairline text-[10px] font-mono text-titanium">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
              <span>Encrypted • Key #CH-9942</span>
            </div>

            {/* Sign Out Button */}
            <button
              onClick={onSignOut}
              className="inline-flex items-center gap-1.5 text-xs text-titanium hover:text-light-gray px-2.5 py-1.5 rounded-lg border border-hairline hover:border-titanium/40 transition-colors"
              title="Return to Landing Page"
            >
              <LogOut className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">Sign Out</span>
            </button>
          </div>
        </div>
      </header>

      {/* Main Workspace Body */}
      <main className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-5 space-y-6">
        {/* 2. MATTER STAGE INDICATOR & BREADCRUMBS */}
        <div className="p-4 bg-graphite border border-hairline rounded-2xl shadow-md">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-mono uppercase tracking-wider text-titanium">
                MATTER LIFECYCLE:
              </span>
              <span className="text-xs font-medium text-light-gray">
                {activeMatter.forum}
              </span>
            </div>

            {/* Linear Progress Bar */}
            <div className="flex items-center gap-1.5 sm:gap-3 overflow-x-auto text-xs font-mono py-1">
              {stages.map((st, idx) => (
                <React.Fragment key={st.id}>
                  <button
                    onClick={() => {
                      if (st.id === 'ocr' || st.id === 'chain' || st.id === 'draft') {
                        setActiveTab(st.id);
                      }
                    }}
                    className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-lg transition-all ${
                      st.completed
                        ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                        : st.current
                          ? 'bg-champagne text-obsidian font-semibold shadow-sm'
                          : 'bg-obsidian/50 text-muted-gray border border-hairline/60'
                    }`}
                  >
                    {st.completed && <Check className="w-3 h-3" />}
                    {st.current && <span className="w-1.5 h-1.5 rounded-full bg-obsidian animate-ping" />}
                    {st.pending && <span className="w-1.5 h-1.5 rounded-full bg-titanium/50" />}
                    <span>{st.label}</span>
                  </button>
                  {idx < stages.length - 1 && (
                    <span className="text-titanium/40 text-[10px]">→</span>
                  )}
                </React.Fragment>
              ))}
            </div>
          </div>
        </div>

        {/* 3. MULTI-TAB NAVIGATION BAR (Apple-Style Graphite Pills) */}
        <div className="flex items-center gap-2 overflow-x-auto pb-1 border-b border-hairline">
          {[
            { id: 'ocr', label: 'Document OCR & 7/12 Viewer', badge: '2 Docs Verified' },
            { id: 'chain', label: '30-Year Title Chain Graph', badge: '1 Charge Flagged' },
            { id: 'draft', label: 'Evidence-Linked Drafting Studio', badge: 'Sec. 203 Ready' },
            { id: 'precedents', label: 'Precedents & SSRD Research', badge: '4 Citations' },
            { id: 'limitation', label: 'Limitation & Cause List Engine', badge: '12 Days Left' },
            { id: 'audit', label: 'Firm Privacy & Audit Receipt', badge: `${auditLogs.length} Events` },
          ].map((tab) => {
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-3.5 py-2 rounded-xl text-xs font-medium tracking-wide transition-all shrink-0 flex items-center gap-2 border ${
                  isActive
                    ? 'bg-graphite text-light-gray border-champagne shadow-md ring-1 ring-champagne/30'
                    : 'bg-obsidian/60 text-muted-gray border-hairline hover:text-light-gray hover:border-hairline/80'
                }`}
              >
                <span>{tab.label}</span>
                <span className={`text-[10px] font-mono px-2 py-0.5 rounded-full border ${
                  isActive
                    ? 'bg-champagne/20 text-champagne border-champagne/40'
                    : 'bg-graphite text-titanium border-hairline'
                }`}>
                  {tab.badge}
                </span>
              </button>
            );
          })}
        </div>

        {/* 4. ACTIVE TAB CONTENT RENDERING */}
        <div className="pt-2">
          {activeTab === 'ocr' && (
            <TabDocumentOcr
              currentRole={currentRole}
              onLogAction={logAction}
              onShowToast={showToast}
            />
          )}

          {activeTab === 'chain' && (
            <TabTitleChain
              onSelectNode={(nodeId) => logAction(`Inspected title node Entry #${nodeId}`)}
              onShowToast={showToast}
            />
          )}

          {activeTab === 'draft' && (
            <TabDraftingStudio
              currentRole={currentRole}
              insertedCitations={insertedCitations}
              onLogAction={logAction}
              onShowToast={showToast}
            />
          )}

          {activeTab === 'precedents' && (
            <TabPrecedents
              onInsertCitation={handleInsertCitation}
              onLogAction={logAction}
              onShowToast={showToast}
              currentRole={currentRole}
            />
          )}

          {activeTab === 'limitation' && (
            <TabLimitation
              onLogAction={logAction}
              onShowToast={showToast}
              currentRole={currentRole}
            />
          )}

          {activeTab === 'audit' && (
            <TabAuditReceipt
              auditLogs={auditLogs}
              onShowToast={showToast}
            />
          )}
        </div>
      </main>

      {/* Floating Micro-Toast Feedback */}
      {toastMessage && (
        <div className="fixed bottom-6 right-6 z-50 bg-graphite border border-champagne px-4 py-3 rounded-xl shadow-2xl flex items-center gap-3 animate-fade-in text-xs text-light-gray max-w-sm">
          <Sparkles className="w-4 h-4 text-champagne shrink-0" />
          <span className="flex-1 font-medium">{toastMessage}</span>
          <button
            onClick={() => setToastMessage(null)}
            className="text-titanium hover:text-light-gray text-xs ml-1"
          >
            ✕
          </button>
        </div>
      )}

      {/* Minimal Chamber Footer */}
      <footer className="border-t border-hairline py-4 px-4 sm:px-8 text-center text-xs text-muted-gray bg-obsidian">
        NYAYSETU Enterprise Law Firm Workspace · Mehta & Associates Law Chambers · DPDP Act 2023 Isolated Tenant.
      </footer>
    </div>
  );
}
