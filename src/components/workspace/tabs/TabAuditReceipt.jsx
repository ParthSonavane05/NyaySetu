import React from 'react';
import {
  ShieldCheck,
  Lock,
  Download,
  CheckCircle2,
  KeyRound,
  Server,
  Trash2,
  Clock
} from 'lucide-react';

export default function TabAuditReceipt({
  auditLogs = [],
  onShowToast,
}) {
  const handleDownloadReceipt = () => {
    onShowToast('Downloading Cryptographic DPDP Privacy Receipt (Matter_809_Receipt.pdf)...');
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Privacy Receipt Card */}
      <div className="bg-graphite border border-hairline rounded-2xl p-6 shadow-xl space-y-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-hairline pb-4">
          <div>
            <div className="flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-champagne" />
              <h3 className="text-xs font-semibold text-light-gray uppercase tracking-wider">
                Cryptographic Firm Privacy Receipt
              </h3>
            </div>
            <p className="text-[11px] text-muted-gray mt-0.5">
              Verified compliance certificate under Digital Personal Data Protection (DPDP) Act, 2023.
            </p>
          </div>

          <button
            onClick={handleDownloadReceipt}
            className="inline-flex items-center gap-2 px-4 py-2 bg-champagne hover:bg-[#968a6f] text-obsidian text-xs font-medium tracking-wide rounded-xl transition-all shadow-sm active:scale-[0.98]"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Download Cryptographic Privacy Receipt (.pdf)</span>
          </button>
        </div>

        {/* Technical Specification Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="p-4 bg-obsidian/60 border border-hairline rounded-xl space-y-1">
            <div className="flex items-center gap-1.5 text-titanium text-[10px] font-mono uppercase">
              <Lock className="w-3 h-3 text-champagne" />
              <span>DATA ENCRYPTION</span>
            </div>
            <div className="text-xs font-medium text-light-gray">
              AES-256-GCM Air-Gapped
            </div>
            <div className="text-[10px] text-muted-gray font-mono">
              Key: #CH-9942 (Client HSM)
            </div>
          </div>

          <div className="p-4 bg-obsidian/60 border border-hairline rounded-xl space-y-1">
            <div className="flex items-center gap-1.5 text-titanium text-[10px] font-mono uppercase">
              <Server className="w-3 h-3 text-champagne" />
              <span>HOSTING SOVEREIGNTY</span>
            </div>
            <div className="text-xs font-medium text-light-gray">
              India Central (MeitY Audited)
            </div>
            <div className="text-[10px] text-muted-gray font-mono">
              GovCloud Enclave Mumbai
            </div>
          </div>

          <div className="p-4 bg-obsidian/60 border border-hairline rounded-xl space-y-1">
            <div className="flex items-center gap-1.5 text-titanium text-[10px] font-mono uppercase">
              <Trash2 className="w-3 h-3 text-champagne" />
              <span>RETENTION POLICY</span>
            </div>
            <div className="text-xs font-medium text-light-gray">
              Purge in 30 Days Post-Filing
            </div>
            <div className="text-[10px] text-muted-gray font-mono">
              Zero Model Training Policy
            </div>
          </div>

          <div className="p-4 bg-obsidian/60 border border-hairline rounded-xl space-y-1">
            <div className="flex items-center gap-1.5 text-titanium text-[10px] font-mono uppercase">
              <CheckCircle2 className="w-3 h-3 text-champagne" />
              <span>COMPLIANCE LEVEL</span>
            </div>
            <div className="text-xs font-medium text-champagne">
              DPDP Act 2023 Enterprise
            </div>
            <div className="text-[10px] text-muted-gray font-mono">
              Bar Council Rule 39 Compliant
            </div>
          </div>
        </div>

        {/* Cryptographic Hash Verification Pill */}
        <div className="p-3 bg-obsidian/80 border border-hairline rounded-xl flex flex-wrap items-center justify-between gap-2 text-[10px] font-mono text-titanium">
          <span className="flex items-center gap-2">
            <KeyRound className="w-3.5 h-3.5 text-champagne" />
            SHA-256 PROOF: 9f82a1b7e40c883d6e5f8842ac901842eef014792b0c114e
          </span>
          <span className="text-champagne">IMMUTABLE BLOCK #809-REV</span>
        </div>
      </div>

      {/* Append-Only Audit Trail Table */}
      <div className="bg-graphite border border-hairline rounded-2xl p-6 shadow-xl space-y-4">
        <div className="flex items-center justify-between border-b border-hairline pb-4">
          <div>
            <div className="flex items-center gap-2">
              <Clock className="w-4 h-4 text-champagne" />
              <h3 className="text-xs font-semibold text-light-gray uppercase tracking-wider">
                Append-Only Chamber Audit Trail
              </h3>
            </div>
            <p className="text-[11px] text-muted-gray mt-0.5">
              Cryptographically signed chronological action log for Matter #2026-REV-809.
            </p>
          </div>
          <span className="text-[10px] font-mono text-titanium bg-slate-glass px-2.5 py-1 rounded-full border border-hairline">
            {auditLogs.length} EVENTS RECORDED
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-hairline text-titanium text-[10px] font-mono uppercase bg-obsidian/60">
                <th className="py-2.5 px-3">TIMESTAMP</th>
                <th className="py-2.5 px-3">ACTOR & ROLE</th>
                <th className="py-2.5 px-3">ACTION EVENT</th>
                <th className="py-2.5 px-3 text-right">SIGNATURE / HASH</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-hairline font-mono text-[11px]">
              {auditLogs.map((log, idx) => (
                <tr key={idx} className="hover:bg-obsidian/40 transition-colors">
                  <td className="py-2.5 px-3 text-muted-gray whitespace-nowrap">
                    {log.time}
                  </td>
                  <td className="py-2.5 px-3 text-light-gray font-sans font-medium">
                    {log.actor}
                  </td>
                  <td className="py-2.5 px-3 text-titanium font-sans">
                    {log.action}
                  </td>
                  <td className="py-2.5 px-3 text-right text-champagne text-[10px]">
                    {log.hash}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
