import React from 'react';
import { ShieldCheck, Cpu, Database, FileText, Lock, X, CheckCircle2 } from 'lucide-react';

export default function ArchitectureModal({ isOpen, onClose, onLaunchWorkspace }) {
  if (!isOpen) return null;

  const pipelineLayers = [
    {
      step: '01',
      title: 'Multimodal Lexicon Ingestion',
      icon: FileText,
      desc: 'Deep OCR pipeline engineered specifically for Gujarati revenue phonetics, degraded 7/12 scans, 8A khatas, and handwritten Ferfar Nondh (Mutation Register No. 6).',
      spec: '99.4% Character Match · Kaachi Nondh Decoder',
    },
    {
      step: '02',
      title: '30-Year Title Chain Graph',
      icon: Database,
      desc: 'Deterministic graph engine reconstructing ancestor succession (Varasaai), sale deeds, agricultural mortgage releases, and tenancy regularizations without gaps.',
      spec: 'Temporal Consistency Validator · Encumbrance Flagging',
    },
    {
      step: '03',
      title: 'Statutory Grounding & Precedents',
      icon: Cpu,
      desc: 'Synthesizes appeals strictly referenced to Gujarat Land Revenue Code 1879 (Sec. 135D, 203, 211) and landmark High Court / SSRD judgments with zero hallucinations.',
      spec: 'Raghav Natha Doctrine · SSRD Case Cross-Reference',
    },
    {
      step: '04',
      title: 'Air-Gapped DPDP Vault',
      icon: Lock,
      desc: 'Zero-retention infrastructure. Per-case ephemeral decryption keys, cryptographic audit trails, and DPDP Act 2023 compliance built for senior chambers.',
      spec: 'Client-side HSM Keys · Cryptographic Privacy Receipts',
    },
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 bg-obsidian/80 backdrop-blur-md animate-fade-in">
      <div 
        className="relative w-full max-w-3xl bg-graphite border border-hairline rounded-2xl p-6 sm:p-8 shadow-2xl overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Subtle background glow */}
        <div className="absolute -top-24 -right-24 w-72 h-72 bg-champagne/10 rounded-full blur-3xl pointer-events-none" />
        
        {/* Modal Header */}
        <div className="flex items-center justify-between pb-6 border-b border-hairline">
          <div>
            <div className="inline-flex items-center gap-2 px-2.5 py-0.5 rounded-full bg-slate-glass border border-hairline text-titanium text-[10px] font-mono tracking-widest uppercase mb-1.5">
              <Cpu className="w-3 h-3 text-champagne" />
              SYSTEM ARCHITECTURE SPECIFICATION
            </div>
            <h2 className="text-xl sm:text-2xl font-light text-light-gray tracking-tight">
              Deterministic Revenue Intelligence Pipeline
            </h2>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg border border-hairline bg-slate-glass hover:bg-slate-glass/80 text-muted-gray hover:text-light-gray transition-colors"
            aria-label="Close modal"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Pipeline Layers */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 py-6">
          {pipelineLayers.map((layer) => {
            const IconComponent = layer.icon;
            return (
              <div 
                key={layer.step}
                className="bg-obsidian/60 border border-hairline rounded-xl p-4 flex flex-col justify-between hover:border-champagne/30 transition-colors"
              >
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-[11px] font-mono text-champagne font-semibold tracking-wider">
                      LAYER {layer.step}
                    </span>
                    <IconComponent className="w-4 h-4 text-titanium" />
                  </div>
                  <h3 className="text-sm font-medium text-light-gray mb-1.5">
                    {layer.title}
                  </h3>
                  <p className="text-xs text-muted-gray leading-relaxed mb-3">
                    {layer.desc}
                  </p>
                </div>
                <div className="pt-2 border-t border-hairline/60 flex items-center gap-1.5 text-[10px] font-mono text-titanium">
                  <CheckCircle2 className="w-3 h-3 text-champagne" />
                  <span>{layer.spec}</span>
                </div>
              </div>
            );
          })}
        </div>

        {/* Modal Footer */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-4 border-t border-hairline">
          <div className="text-xs text-muted-gray flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-champagne" />
            <span>Audited against Digital Personal Data Protection (DPDP) Act 2023.</span>
          </div>
          <div className="flex items-center gap-3 w-full sm:w-auto">
            <button
              onClick={onClose}
              className="flex-1 sm:flex-none px-4 py-2 text-xs text-titanium hover:text-light-gray transition-colors"
            >
              Close
            </button>
            <button
              onClick={() => {
                onClose();
                onLaunchWorkspace();
              }}
              className="flex-1 sm:flex-none px-4 py-2 bg-champagne hover:bg-[#968a6f] text-obsidian text-xs font-medium tracking-wide rounded-lg transition-colors"
            >
              Launch Workspace
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

