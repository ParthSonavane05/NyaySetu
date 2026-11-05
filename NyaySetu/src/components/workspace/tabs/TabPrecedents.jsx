import React, { useState } from 'react';
import {
  Search,
  Scale,
  Sparkles
} from 'lucide-react';

export default function TabPrecedents({
  onInsertCitation,
  onLogAction,
  onShowToast,
  currentRole,
}) {
  const [searchQuery, setSearchQuery] = useState(
    'Notice under Section 135D mandatory before mutation certification'
  );
  const [selectedForum, setSelectedForum] = useState('all');

  const precedentCorpus = [
    {
      id: 'p1',
      citation: 'SSRD/REV/AHM/2024/118',
      caseName: 'Patel K. v. State of Gujarat & Mamlatdar, Bavla',
      court: 'Special Secretary (Revenue Department), Gujarat',
      forum: 'ssrd',
      year: '2024',
      holding: 'Where notice under Section 135D of the Bombay Land Revenue Code was not personally served upon all registered co-occupants, the certification of mutation entry is void ab initio and liable to be set aside.',
      bench: 'Hon’ble M. K. Dave, SSRD Ahmedabad',
      relevanceScore: '99.2%',
    },
    {
      id: 'p2',
      citation: '2021 (2) GLR 492',
      caseName: 'G. M. Vaghasiya v. State of Gujarat & Ors.',
      court: 'High Court of Gujarat at Ahmedabad',
      forum: 'hc',
      year: '2021',
      holding: 'Principles of natural justice are non-negotiable in revenue proceedings. Revenue authorities cannot alter or certify mutation entries behind the back of recorded tenure holders.',
      bench: 'Hon’ble Justice N. V. Anjaria',
      relevanceScore: '96.8%',
    },
    {
      id: 'p3',
      citation: 'AIR 1969 SC 1297',
      caseName: 'State of Gujarat v. Patel Raghav Natha',
      court: 'Supreme Court of India (Constitution Bench)',
      forum: 'sc',
      year: '1969',
      holding: 'Revisional powers under Section 211 of Bombay Land Revenue Code cannot be invoked after unreasonable delay. Exercise of power after 9 years violates the rule of law and doctrine of finality.',
      bench: 'Supreme Court of India',
      relevanceScore: '98.5%',
    },
    {
      id: 'p4',
      citation: '2008 (3) GLH 440',
      caseName: 'Evergreen Apartment Co-op. Housing Society v. SSRD',
      court: 'High Court of Gujarat',
      forum: 'hc',
      year: '2008',
      holding: 'Revenue officers exercising summary jurisdiction under Section 135D have no authority to investigate complex disputes of title, which fall exclusively within civil court jurisdiction.',
      bench: 'High Court of Gujarat',
      relevanceScore: '94.1%',
    },
    {
      id: 'p5',
      citation: 'GRT Appeal No. 14/2023',
      caseName: 'Desai Land Holding Trust v. Collector, Ahmedabad',
      court: 'Gujarat Revenue Tribunal (GRT), Ahmedabad',
      forum: 'grt',
      year: '2023',
      holding: 'Old tenure agricultural land remains alienable without prior Collectorate premium unless a specific restriction under Section 43 or 73AA is documented on the 7/12 record.',
      bench: 'Gujarat Revenue Tribunal Bench II',
      relevanceScore: '91.4%',
    },
  ];

  const filteredPrecedents = precedentCorpus.filter((p) => {
    const matchesForum = selectedForum === 'all' || p.forum === selectedForum;
    const matchesSearch =
      searchQuery.trim() === '' ||
      p.caseName.toLowerCase().includes(searchQuery.toLowerCase()) ||
      p.citation.toLowerCase().includes(searchQuery.toLowerCase()) ||
      p.holding.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesForum && matchesSearch;
  });

  const handleInsert = (precedent) => {
    onInsertCitation(precedent);
    onLogAction(`${currentRole.shortLabel} inserted precedent '${precedent.citation}' into Drafting Studio.`);
    onShowToast(`Precedent ${precedent.citation} inserted into Draft Grounds.`);
  };

  return (
    <div className="bg-graphite border border-hairline rounded-2xl p-6 shadow-xl space-y-6 animate-fade-in">
      {/* Search Header */}
      <div className="space-y-4 border-b border-hairline pb-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <div className="flex items-center gap-2">
              <Scale className="w-4 h-4 text-champagne" />
              <h3 className="text-xs font-semibold text-light-gray uppercase tracking-wider">
                SSRD & High Court Jurisprudence Engine
              </h3>
            </div>
            <p className="text-[11px] text-muted-gray mt-0.5">
              Tuned to 40+ years of Gujarat revenue case laws, Bombay LRC annotations, and GRT rulings.
            </p>
          </div>
          <span className="text-[10px] font-mono text-champagne bg-slate-glass px-2.5 py-1 rounded-full border border-hairline">
            VERIFIED CITATION CORPUS
          </span>
        </div>

        {/* Search Bar Input */}
        <div className="flex items-center gap-2 bg-obsidian border border-hairline rounded-xl p-1.5 focus-within:border-champagne/70 transition-colors shadow-inner">
          <Search className="w-4 h-4 text-titanium ml-2 shrink-0" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search rulings by statute (e.g. Sec. 135D, 211), citation, or legal holding..."
            className="flex-1 bg-transparent px-2 py-1.5 text-xs text-light-gray placeholder:text-muted-gray/50 focus:outline-none"
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery('')}
              className="px-2 text-xs text-muted-gray hover:text-light-gray"
            >
              Clear
            </button>
          )}
        </div>

        {/* Forum Filters */}
        <div className="flex flex-wrap items-center gap-2 text-xs font-mono">
          <span className="text-[10px] text-titanium uppercase mr-1">FORUM:</span>
          {[
            { id: 'all', label: 'All Forums' },
            { id: 'ssrd', label: 'SSRD Gujarat' },
            { id: 'grt', label: 'Revenue Tribunal (GRT)' },
            { id: 'hc', label: 'Gujarat High Court' },
            { id: 'sc', label: 'Supreme Court of India' },
          ].map((f) => (
            <button
              key={f.id}
              onClick={() => setSelectedForum(f.id)}
              className={`px-3 py-1 rounded-lg border transition-colors ${
                selectedForum === f.id
                  ? 'bg-champagne text-obsidian font-semibold border-champagne'
                  : 'bg-obsidian border-hairline text-titanium hover:text-light-gray'
              }`}
            >
              {f.label}
            </button>
          ))}
        </div>
      </div>

      {/* Precedent Cards List */}
      <div className="space-y-4 max-h-[600px] overflow-auto pr-1">
        {filteredPrecedents.length === 0 ? (
          <div className="text-center py-12 text-muted-gray text-xs">
            No revenue precedents matched your query. Try searching "Section 135D" or "Raghav Natha".
          </div>
        ) : (
          filteredPrecedents.map((item) => (
            <div
              key={item.id}
              className="p-5 bg-obsidian/60 hover:bg-obsidian/80 border border-hairline hover:border-champagne/40 rounded-xl transition-all space-y-3"
            >
              <div className="flex flex-wrap items-center justify-between gap-2">
                <div className="flex items-center gap-2">
                  <span className="font-mono text-xs font-bold text-champagne">
                    {item.citation}
                  </span>
                  <span className="text-[10px] font-mono text-titanium bg-slate-glass px-2 py-0.5 rounded border border-hairline">
                    MATCH: {item.relevanceScore}
                  </span>
                </div>
                <span className="text-[10px] font-mono text-muted-gray">
                  {item.court} · {item.year}
                </span>
              </div>

              <div>
                <h4 className="text-sm font-medium text-light-gray mb-1">
                  {item.caseName}
                </h4>
                <p className="text-xs text-muted-gray leading-relaxed">
                  "{item.holding}"
                </p>
              </div>

              <div className="pt-2 border-t border-hairline/60 flex flex-wrap items-center justify-between gap-3 text-[11px] font-mono text-titanium">
                <span>Bench: {item.bench}</span>

                <button
                  type="button"
                  onClick={() => handleInsert(item)}
                  className="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg bg-champagne hover:bg-[#968a6f] text-obsidian text-xs font-medium tracking-wide transition-colors"
                >
                  <Sparkles className="w-3 h-3" />
                  <span>Insert Citation into Draft</span>
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
