import React, { useState } from 'react';
import {
  Layers,
  AlertTriangle,
  FileText,
  Scale,
  ChevronRight
} from 'lucide-react';

export default function TabTitleChain({
  onSelectNode,
  onShowToast,
}) {
  const [selectedNodeId, setSelectedNodeId] = useState('809');

  const nodes = [
    {
      id: '410',
      year: '1996',
      date: '18 May 1996',
      entryNo: 'Mutation Entry 410',
      title: 'Ancestral Partition (વારસાઈ હક્ક)',
      status: 'Certified',
      badgeColor: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30',
      officer: 'Mamlatdar, Bavla (Revenue Circle Officer)',
      summary: 'Ancestral partition recorded among 4 legal coparceners pursuant to registered family tree. Unencumbered succession.',
      evidence: 'Village Form No. 6, Page 42, Serial No. 410',
      statutoryNote: 'Sec. 135C compliance verified. No third-party disputes registered.',
      alert: null,
    },
    {
      id: '621',
      year: '2008',
      date: '04 November 2008',
      entryNo: 'Mutation Entry 621',
      title: 'Registered Sale Deed (વેચાણ દસ્તાવેજ)',
      status: 'Certified',
      badgeColor: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30',
      officer: 'Mamlatdar, Bavla',
      summary: 'Registered Sale Deed No. 1842/2008 executed in favor of Patel Rameshchandra K. Consideration ₹ 32,50,000 paid via pay order.',
      evidence: 'Sub-Registrar Bavla Index-II, Book No. 1, Vol. 412',
      statutoryNote: 'Section 135D notices served personally on predecessors without objection within 30 days.',
      alert: null,
    },
    {
      id: '742',
      year: '2018',
      date: '14 August 2018',
      entryNo: 'Mutation Entry 742',
      title: 'Bank Mortgage (ખેતી ધિરાણ બોજો)',
      status: 'Active Charge',
      badgeColor: 'text-amber-400 bg-amber-500/10 border-amber-500/30',
      officer: 'Revenue Circle Inspector, Bavla',
      summary: 'Simple agricultural mortgage created in favor of State Bank of India, Bavla Branch for ₹ 8,50,000 credit facility.',
      evidence: 'SBI Sanction Letter No. AGR/2018/901 & Ferfar Entry 742',
      statutoryNote: 'Encumbrance remains active on revenue records. NOC satisfaction entry pending.',
      alert: 'Outstanding Bank Encumbrance Flagged for Title Clearance',
    },
    {
      id: '809',
      year: '2026',
      date: '14 July 2017 (Challenged 2026)',
      entryNo: 'Mutation Entry 809',
      title: 'Disputed Transfer (હક્ક ફેરફાર પડકાર)',
      status: 'Flagged with Dispute',
      badgeColor: 'text-rose-400 bg-rose-500/10 border-rose-500/30',
      officer: 'Deputy Collector / Prant Officer Proceedings',
      summary: 'Opposite party lodged delayed RTS challenge alleging lack of personal notice under Section 135D upon legal heirs.',
      evidence: 'RTS Appeal Docket #2026-REV-809',
      statutoryNote: 'Firm Defense Ground: 9-year inexplicable delay directly barred by Supreme Court in State of Gujarat v. Patel Raghav Natha (AIR 1969 SC 1297).',
      alert: 'Notice under Sec. 135D not served to legal heirs (Challenged after 9 years)',
    },
  ];

  const activeNode = nodes.find((n) => n.id === selectedNodeId) || nodes[3];

  const handleNodeClick = (nodeId) => {
    setSelectedNodeId(nodeId);
    if (onSelectNode) onSelectNode(nodeId);
    onShowToast(`Opened Dossier for Mutation Entry ${nodeId}`);
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 animate-fade-in">
      {/* LEFT: 30-Year DAG / Timeline Flow (7 cols) */}
      <div className="lg:col-span-7 bg-graphite border border-hairline rounded-2xl p-6 shadow-xl space-y-6">
        <div className="flex items-center justify-between border-b border-hairline pb-4">
          <div>
            <div className="flex items-center gap-2">
              <Layers className="w-4 h-4 text-champagne" />
              <h3 className="text-xs font-semibold text-light-gray uppercase tracking-wider">
                30-Year Chain of Title (1996–2026)
              </h3>
            </div>
            <p className="text-[11px] text-muted-gray mt-0.5">
              Interactive temporal DAG. Click any mutation milestone to inspect underlying revenue records.
            </p>
          </div>
          <span className="text-[10px] font-mono text-titanium bg-slate-glass px-2.5 py-1 rounded-full border border-hairline">
            4 RECORDED ENTRIES
          </span>
        </div>

        {/* Chronological Flow Nodes */}
        <div className="relative pl-8 space-y-6 before:absolute before:left-3.5 before:top-4 before:bottom-4 before:w-[2px] before:bg-hairline">
          {nodes.map((node) => {
            const isSelected = node.id === selectedNodeId;
            return (
              <div key={node.id} className="relative">
                {/* Node Milestone Dot */}
                <button
                  type="button"
                  onClick={() => handleNodeClick(node.id)}
                  className={`absolute -left-8 top-1 w-7 h-7 rounded-full border flex items-center justify-center transition-all ${
                    isSelected
                      ? 'bg-champagne text-obsidian border-champagne ring-4 ring-champagne/20 scale-110 shadow-lg'
                      : 'bg-obsidian border-hairline text-titanium hover:border-champagne/60'
                  }`}
                  aria-label={`Select ${node.entryNo}`}
                >
                  <span className="text-[10px] font-mono font-bold">
                    {node.year.slice(-2)}
                  </span>
                </button>

                {/* Node Card */}
                <div
                  onClick={() => handleNodeClick(node.id)}
                  className={`p-4 rounded-xl border cursor-pointer transition-all ${
                    isSelected
                      ? 'bg-slate-glass border-champagne shadow-md ring-1 ring-champagne/30'
                      : 'bg-obsidian/50 border-hairline hover:border-hairline/80 hover:bg-obsidian/70'
                  }`}
                >
                  <div className="flex flex-wrap items-center justify-between gap-2 mb-1.5">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-mono font-semibold text-light-gray">
                        {node.entryNo}
                      </span>
                      <span className="text-[10px] text-muted-gray">
                        ({node.year})
                      </span>
                    </div>
                    <span className={`text-[10px] font-mono px-2 py-0.5 rounded border ${node.badgeColor}`}>
                      {node.status}
                    </span>
                  </div>

                  <h4 className="text-sm font-medium text-light-gray mb-1">
                    {node.title}
                  </h4>

                  <p className="text-xs text-muted-gray line-clamp-2 leading-relaxed mb-2">
                    {node.summary}
                  </p>

                  {node.alert && (
                    <div className="p-2 rounded bg-amber-500/10 border border-amber-500/30 text-amber-400 text-[11px] flex items-center gap-1.5">
                      <AlertTriangle className="w-3.5 h-3.5 shrink-0" />
                      <span>{node.alert}</span>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* RIGHT: Slide-Over Inspection Panel for Selected Node (5 cols) */}
      <div className="lg:col-span-5 bg-graphite border border-hairline rounded-2xl p-6 shadow-xl flex flex-col justify-between">
        <div>
          {/* Panel Header */}
          <div className="flex items-center justify-between border-b border-hairline pb-4 mb-5">
            <div>
              <span className="text-[10px] font-mono text-champagne tracking-wider uppercase">
                MUTATION ENTRY DOSSIER
              </span>
              <h3 className="text-base font-medium text-light-gray mt-0.5">
                {activeNode.entryNo} ({activeNode.year})
              </h3>
            </div>
            <span className={`text-[10px] font-mono px-2 py-0.5 rounded border ${activeNode.badgeColor}`}>
              {activeNode.status}
            </span>
          </div>

          {/* Details Grid */}
          <div className="space-y-4 text-xs">
            <div className="p-3 bg-obsidian/60 border border-hairline rounded-xl">
              <span className="text-[10px] font-mono text-titanium uppercase block mb-1">
                Transaction Classification
              </span>
              <div className="text-light-gray font-medium">{activeNode.title}</div>
              <div className="text-[11px] text-muted-gray mt-1 leading-relaxed">
                {activeNode.summary}
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div className="p-3 bg-obsidian/60 border border-hairline rounded-xl">
                <span className="text-[10px] font-mono text-titanium uppercase block mb-1">
                  Certification Date
                </span>
                <div className="text-light-gray font-mono">{activeNode.date}</div>
              </div>

              <div className="p-3 bg-obsidian/60 border border-hairline rounded-xl">
                <span className="text-[10px] font-mono text-titanium uppercase block mb-1">
                  Certifying Authority
                </span>
                <div className="text-light-gray">{activeNode.officer}</div>
              </div>
            </div>

            <div className="p-3 bg-obsidian/60 border border-hairline rounded-xl">
              <span className="text-[10px] font-mono text-titanium uppercase block mb-1">
                Primary Archive Index Reference
              </span>
              <div className="font-mono text-light-gray text-[11px] flex items-center gap-1.5">
                <FileText className="w-3.5 h-3.5 text-champagne" />
                <span>{activeNode.evidence}</span>
              </div>
            </div>

            <div className="p-3.5 bg-slate-glass border border-champagne/40 rounded-xl space-y-1.5">
              <div className="text-champagne font-medium flex items-center gap-1.5 text-xs">
                <Scale className="w-3.5 h-3.5" />
                <span>Statutory Grounding & Defense Analysis</span>
              </div>
              <p className="text-[11px] text-light-gray/90 leading-relaxed">
                {activeNode.statutoryNote}
              </p>
            </div>
          </div>
        </div>

        {/* Panel Bottom Action */}
        <div className="pt-5 border-t border-hairline mt-6 flex items-center justify-between">
          <span className="text-[10px] text-muted-gray">
            Cross-referenced with Sub-Registrar Index-II.
          </span>
          <button
            onClick={() => onShowToast(`Entry ${activeNode.entryNo} copied to chamber clipboard.`)}
            className="text-xs text-champagne hover:underline inline-flex items-center gap-1 font-medium"
          >
            <span>Copy Citation</span>
            <ChevronRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </div>
  );
}
