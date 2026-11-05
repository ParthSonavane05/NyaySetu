import React, { useState } from 'react';
import { Search, ArrowLeft, ShieldCheck, CheckCircle2, Calendar, ChevronRight } from 'lucide-react';

export default function ClientPortalView({ onBackToLanding }) {
  const [searchQuery, setSearchQuery] = useState('142/A');
  const [selectedCase, setSelectedCase] = useState({
    surveyNo: '142/A',
    khataNo: '247',
    village: 'Kalol',
    district: 'Gandhinagar',
    caseNo: 'RTS/APPEAL/2026/084',
    forum: 'Court of the Prant Officer (Deputy Collector), Kalol',
    matterType: 'RTS Appeal under Sec. 203, Gujarat Land Revenue Code',
    nextHearing: '12 November 2026',
    status: 'Notice under Sec. 135D Verified',
    advocateName: 'R. K. Mehta & Associates (Senior Revenue Advocate)',
  });

  const handleSearch = (e) => {
    e?.preventDefault();
    if (searchQuery.trim()) {
      setSelectedCase({
        surveyNo: searchQuery.toUpperCase(),
        khataNo: '247',
        village: 'Kalol',
        district: 'Gandhinagar',
        caseNo: `RTS/APPEAL/2026/${Math.floor(Math.random() * 800 + 100)}`,
        forum: 'Court of the Prant Officer (Deputy Collector), Kalol',
        matterType: 'RTS Appeal under Sec. 203, Gujarat Land Revenue Code',
        nextHearing: '12 November 2026',
        status: 'Notice under Sec. 135D Verified',
        advocateName: 'R. K. Mehta & Associates (Senior Revenue Advocate)',
      });
    }
  };

  const timelineSteps = [
    {
      date: '14 Jul 2017',
      title: 'Mutation Entry 809 Certified',
      desc: 'Mamlatdar certified sale deed transfer after statutory Sec. 135D notice.',
      completed: true,
    },
    {
      date: '08 Jan 2026',
      title: 'RTS Appeal Lodged (Delayed by 9 Years)',
      desc: 'Challenged before Prant Officer under Sec. 203 of Land Revenue Code.',
      completed: true,
    },
    {
      date: '19 Feb 2026',
      title: 'Records & Proceedings (R&P) Summoned',
      desc: 'Mamlatdar Office, Kalol produced original Mutation Register No. 6.',
      completed: true,
    },
    {
      date: '12 Nov 2026',
      title: 'Final Hearing on Limitation & Sec. 135D Grounding',
      desc: 'NYAYSETU synthesized grounds relying on Patel Raghav Natha precedent.',
      completed: false,
      current: true,
    },
  ];

  return (
    <div className="min-h-screen bg-obsidian text-light-gray flex flex-col justify-between selection:bg-champagne/30 selection:text-light-gray">
      {/* Top Header */}
      <header className="border-b border-hairline bg-obsidian/80 backdrop-blur-xl px-4 sm:px-8 py-4">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <button
            onClick={onBackToLanding}
            className="inline-flex items-center gap-2 text-xs text-titanium hover:text-light-gray transition-colors group"
          >
            <ArrowLeft className="w-4 h-4 group-hover:-translate-x-0.5 transition-transform" />
            <span>Return to Landing Page</span>
          </button>

          <div className="flex items-center gap-2">
            <span className="text-light-gray font-semibold text-xs tracking-[0.24em]">
              NYAYSETU
            </span>
            <span className="px-2 py-0.5 rounded-full text-[9px] font-mono tracking-widest uppercase bg-graphite border border-hairline text-titanium">
              CLIENT CASE PORTAL
            </span>
          </div>
        </div>
      </header>

      {/* Main Body */}
      <main className="flex-1 max-w-5xl mx-auto w-full px-4 sm:px-6 py-8 sm:py-12">
        {/* Search Bar Section */}
        <div className="text-center max-w-xl mx-auto mb-10">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-graphite border border-hairline text-titanium text-[10px] font-mono uppercase tracking-widest mb-3">
            <Search className="w-3 h-3 text-champagne" />
            Live Revenue Court Docket
          </div>
          <h1 className="text-2xl sm:text-3xl font-light text-light-gray tracking-tight mb-3">
            Track Revenue Case & Title Records
          </h1>
          <p className="text-xs sm:text-sm text-muted-gray mb-6">
            Enter your Land Survey Number, Khata Number, or RTS Appeal Docket Number.
          </p>

          <form onSubmit={handleSearch} className="flex items-center gap-2 bg-graphite border border-hairline rounded-2xl p-1.5 shadow-lg focus-within:border-champagne/60 transition-colors">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="e.g. Survey 142/A or RTS/APPEAL/2026/084"
              className="flex-1 bg-transparent px-3 py-2 text-xs sm:text-sm text-light-gray placeholder:text-muted-gray/60 focus:outline-none"
            />
            <button
              type="submit"
              className="px-4 py-2 rounded-xl bg-champagne hover:bg-[#968a6f] text-obsidian text-xs font-medium tracking-wide transition-colors"
            >
              Search Docket
            </button>
          </form>
        </div>

        {/* Case Details Card */}
        {selectedCase && (
          <div className="bg-graphite border border-hairline rounded-2xl p-6 sm:p-8 shadow-2xl space-y-6">
            {/* Case Header Details */}
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-6 border-b border-hairline">
              <div>
                <span className="text-[10px] font-mono text-champagne tracking-wider uppercase">
                  DOCKET: {selectedCase.caseNo}
                </span>
                <h2 className="text-lg sm:text-xl font-medium text-light-gray mt-1">
                  Survey No. {selectedCase.surveyNo} (Khata {selectedCase.khataNo}), {selectedCase.village}
                </h2>
                <div className="text-xs text-muted-gray mt-1">
                  {selectedCase.forum}
                </div>
              </div>

              <div className="text-left sm:text-right">
                <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-slate-glass border border-hairline text-champagne text-[11px] font-mono">
                  <span className="w-1.5 h-1.5 rounded-full bg-champagne animate-pulse" />
                  {selectedCase.status}
                </div>
                <div className="text-[11px] text-muted-gray mt-1.5 flex items-center sm:justify-end gap-1.5">
                  <Calendar className="w-3.5 h-3.5 text-titanium" />
                  <span>Next Hearing: <strong className="text-light-gray font-normal">{selectedCase.nextHearing}</strong></span>
                </div>
              </div>
            </div>

            {/* Matter Specifications Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 p-4 bg-obsidian/60 border border-hairline rounded-xl text-xs">
              <div>
                <span className="text-muted-gray text-[10px] uppercase font-mono">Subject Matter</span>
                <p className="text-light-gray mt-0.5 font-medium">{selectedCase.matterType}</p>
              </div>
              <div>
                <span className="text-muted-gray text-[10px] uppercase font-mono">Chamber Counsel</span>
                <p className="text-light-gray mt-0.5 font-medium">{selectedCase.advocateName}</p>
              </div>
              <div>
                <span className="text-muted-gray text-[10px] uppercase font-mono">Statutory Defense</span>
                <p className="text-champagne mt-0.5 font-medium">Sec. 135D Compliance Certified</p>
              </div>
            </div>

            {/* Interactive Timeline of Matter */}
            <div className="pt-2">
              <h3 className="text-xs font-mono uppercase tracking-wider text-titanium mb-4">
                Procedural Revenue Timeline
              </h3>

              <div className="relative pl-6 space-y-6 before:absolute before:left-2 before:top-2 before:bottom-2 before:w-[1px] before:bg-hairline">
                {timelineSteps.map((step, idx) => (
                  <div key={idx} className="relative">
                    <span 
                      className={`absolute -left-6 top-1 w-3 h-3 rounded-full border border-graphite flex items-center justify-center ${
                        step.completed 
                          ? 'bg-champagne text-obsidian' 
                          : step.current 
                            ? 'bg-titanium ring-2 ring-champagne/40' 
                            : 'bg-obsidian border-hairline'
                      }`}
                    >
                      {step.completed && <CheckCircle2 className="w-3 h-3 text-obsidian" />}
                    </span>

                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1">
                      <h4 className="text-xs font-medium text-light-gray">
                        {step.title}
                      </h4>
                      <span className="text-[10px] font-mono text-muted-gray">
                        {step.date}
                      </span>
                    </div>
                    <p className="text-[11px] text-muted-gray mt-1 leading-relaxed">
                      {step.desc}
                    </p>
                  </div>
                ))}
              </div>
            </div>

            {/* Footer Trust strip */}
            <div className="pt-4 border-t border-hairline/60 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-[11px] text-muted-gray">
              <span className="flex items-center gap-1.5 text-titanium">
                <ShieldCheck className="w-3.5 h-3.5 text-champagne" />
                Synchronized with Gujarat Revenue Department & Sub-Registrar Index-II
              </span>
              <button
                onClick={onBackToLanding}
                className="text-xs text-champagne hover:underline inline-flex items-center gap-1"
              >
                <span>Back to Overview</span>
                <ChevronRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-hairline py-4 px-4 text-center text-xs text-muted-gray">
        NYAYSETU Client Case Gateway · Secure, Encrypted & Verified Land Docket Information.
      </footer>
    </div>
  );
}
