import React, { useState } from 'react';
import {
  Scale,
  ShieldCheck,
  FileText,
  Lock,
  ArrowRight,
  CheckCircle2,
  Copy,
  Check,
  Sparkles,
  Layers,
  BookOpen,
  Users
} from 'lucide-react';
import ArchitectureModal from './ArchitectureModal';

export default function LandingPage({
  onNavigateToAuth,
}) {
  const [activeEntry, setActiveEntry] = useState('809');
  const [copiedDraft, setCopiedDraft] = useState(false);
  const [isArchModalOpen, setIsArchModalOpen] = useState(false);

  const handleCopyDraft = () => {
    const textToCopy = `BEFORE THE HON'BLE SPECIAL SECRETARY, REVENUE DEPARTMENT (SSRD), AHMEDABAD, GUJARAT\n\nREVENUE REVISION APPLICATION NO. SSRD/RTS/2026/084\n\nIN THE MATTER OF:\nChallenge to Mutation Entry No. 809 in respect of Survey No. 142/A, Khata No. 247, Moje Kalol, District Gandhinagar.\n\nGROUND (A) - STATUTORY COMPLIANCE UNDER SECTION 135D OF GUJARAT LAND REVENUE CODE:\n1. It is respectfully submitted that Mutation Entry No. 809 was recorded on 14.07.2017 pursuant to Registered Sale Deed No. 2451/2017.\n2. In strict compliance with Section 135D of the Gujarat Land Revenue Code, 1879, statutory notice was duly served upon all interested parties and legal predecessors. No dispute was lodged within the statutory 30-day window, whereupon the Mamlatdar certified the entry.\n3. The present belated challenge initiated after an inexplicable delay of 9 years is directly hit by the settled principle of law laid down by the Hon'ble Supreme Court in State of Gujarat v. Patel Raghav Natha (AIR 1969 SC 1297), holding that revisional powers under the Land Revenue Code cannot be exercised beyond a reasonable time.\n\nVERIFIED CITATION GROUNDING: Section 135D GLRC | AIR 1969 SC 1297`;

    navigator.clipboard?.writeText(textToCopy);
    setCopiedDraft(true);
    setTimeout(() => setCopiedDraft(false), 2500);
  };

  const scrollToSection = (id) => {
    const el = document.getElementById(id);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <div className="min-h-screen bg-obsidian text-light-gray selection:bg-champagne/30 selection:text-light-gray flex flex-col font-sans">
      {/* 1. TOP STICKY NAVIGATION */}
      <header className="sticky top-0 z-40 w-full backdrop-blur-xl bg-obsidian/85 border-b border-hairline transition-colors">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          {/* Left: Wordmark & Enterprise Badge */}
          <div className="flex items-center gap-3">
            <a 
              href="#" 
              className="text-light-gray font-semibold text-sm sm:text-base tracking-[0.24em] hover:text-white transition-colors"
            >
              NYAYSETU
            </a>
            <span className="hidden sm:inline-flex items-center px-2.5 py-0.5 rounded-full text-[9px] font-mono tracking-wider uppercase bg-graphite border border-hairline text-titanium">
              ENTERPRISE REVENUE AI
            </span>
          </div>

          {/* Center Links */}
          <nav className="hidden md:flex items-center gap-8 text-xs font-medium text-muted-gray">
            <button
              onClick={() => scrollToSection('chamber-solutions')}
              className="hover:text-light-gray transition-colors"
            >
              Chamber Solutions
            </button>
            <button
              onClick={() => scrollToSection('practice-areas')}
              className="hover:text-light-gray transition-colors"
            >
              Practice Areas
            </button>
            <button
              onClick={() => scrollToSection('firm-security')}
              className="hover:text-light-gray transition-colors"
            >
              Firm Security
            </button>
          </nav>

          {/* Right Action: Chamber Sign In */}
          <div className="flex items-center gap-3">
            <button
              onClick={() => onNavigateToAuth('partner')}
              className="inline-flex items-center gap-1.5 px-4 py-2 rounded-full text-xs font-medium bg-graphite hover:bg-slate-glass text-light-gray border border-hairline hover:border-champagne/50 shadow-sm transition-all duration-200 group"
            >
              <span>Chamber Sign In</span>
              <ArrowRight className="w-3.5 h-3.5 text-titanium group-hover:text-champagne group-hover:translate-x-0.5 transition-all" />
            </button>
          </div>
        </div>
      </header>

      <main className="flex-1">
        {/* 2. HERO SECTION */}
        <section className="relative pt-24 pb-20 md:pt-32 md:pb-28 px-4 sm:px-6 lg:px-8 overflow-hidden">
          {/* Subtle Ambient Radial Lighting */}
          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[720px] h-[380px] bg-[radial-gradient(ellipse_at_top,rgba(130,119,96,0.14),rgba(11,13,16,0)_70%)] pointer-events-none" />

          <div className="max-w-4xl mx-auto text-center relative z-10">
            {/* Minimal Badge */}
            <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-slate-glass border border-hairline text-titanium text-[11px] font-medium tracking-wide mb-8 backdrop-blur-md shadow-sm">
              <Scale className="w-3.5 h-3.5 text-champagne" />
              <span>Built Exclusively for Indian Law Firms & Legal Chambers</span>
            </div>

            {/* Clean Bold Headline */}
            <h1 className="text-3xl sm:text-5xl md:text-6xl font-light text-light-gray tracking-tight leading-[1.12] mb-6">
              Precision Revenue Intelligence for Modern Law Firms.
            </h1>

            {/* Concise Subtitle */}
            <p className="text-muted-gray text-base sm:text-lg leading-relaxed max-w-2xl mx-auto font-normal mb-10">
              Empower partners, associates, and paralegals to parse decades of land records, 
              reconstruct 30-year title chains, and generate citation-grounded revenue appeals in minutes.
            </p>

            {/* Dual Call-to-Action Buttons */}
            <div className="flex flex-col sm:flex-row items-center justify-center gap-3.5">
              <button
                onClick={() => onNavigateToAuth('partner')}
                className="w-full sm:w-auto px-6 py-3 rounded-full bg-champagne hover:bg-[#968a6f] text-obsidian text-xs sm:text-sm font-medium tracking-wide inline-flex items-center justify-center gap-2 transition-all shadow-[0_0_24px_rgba(130,119,96,0.18)] hover:shadow-[0_0_32px_rgba(130,119,96,0.28)] active:scale-[0.98]"
              >
                <span>Launch Chamber Workspace</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>

              <button
                onClick={() => scrollToSection('firm-security')}
                className="w-full sm:w-auto px-6 py-3 rounded-full bg-graphite/70 hover:bg-graphite text-light-gray hover:text-white border border-hairline hover:border-titanium/40 text-xs sm:text-sm font-medium tracking-wide inline-flex items-center justify-center gap-2 transition-all active:scale-[0.98]"
              >
                <span>Explore Firm Security</span>
              </button>
            </div>

            {/* Subtle System Metric Strip */}
            <div className="mt-14 pt-8 border-t border-hairline/60 grid grid-cols-2 md:grid-cols-4 gap-4 max-w-3xl mx-auto text-left">
              <div className="p-2">
                <div className="text-[11px] font-mono text-titanium uppercase tracking-wider mb-1">Title Diligence</div>
                <div className="text-xs text-light-gray font-medium">30-Year Chain Reconstruction</div>
              </div>
              <div className="p-2">
                <div className="text-[11px] font-mono text-titanium uppercase tracking-wider mb-1">Drafting Studio</div>
                <div className="text-xs text-light-gray font-medium">Sec. 135D / 211 GLRC Grounds</div>
              </div>
              <div className="p-2">
                <div className="text-[11px] font-mono text-titanium uppercase tracking-wider mb-1">Role-Based Access</div>
                <div className="text-xs text-light-gray font-medium">Partners, Associates, Paralegals</div>
              </div>
              <div className="p-2">
                <div className="text-[11px] font-mono text-titanium uppercase tracking-wider mb-1">Firm Data Vault</div>
                <div className="text-xs text-light-gray font-medium">DPDP Act 2023 Isolated Tenant</div>
              </div>
            </div>
          </div>
        </section>

        {/* 3. LIVE SPLIT-RECORD SHOWCASE (MATTER_DOSSIER_712.RAW) */}
        <section className="py-16 md:py-24 px-4 sm:px-6 lg:px-8">
          <div className="max-w-6xl mx-auto">
            {/* Section Header */}
            <div className="text-center max-w-2xl mx-auto mb-10">
              <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-graphite border border-hairline text-titanium text-[10px] font-mono uppercase tracking-widest mb-3">
                <Sparkles className="w-3 h-3 text-champagne" />
                Enterprise Matter Extraction Studio
              </div>
              <h2 className="text-2xl sm:text-3xl font-light text-light-gray tracking-tight mb-3">
                From Raw Land Ledgers to Verified Court Pleadings
              </h2>
              <p className="text-xs sm:text-sm text-muted-gray leading-relaxed">
                Review how firm associates and paralegals process archived Village Form 7/12 records, 
                index mutation entries, and prepare statutory revision briefs for partner review.
              </p>
            </div>

            {/* Split Record Card Container */}
            <div className="bg-graphite border border-hairline rounded-2xl overflow-hidden shadow-2xl transition-all">
              {/* Mac-Style Window Header */}
              <div className="px-5 py-3.5 bg-[#12151A] border-b border-hairline flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="w-2.5 h-2.5 rounded-full bg-[#FF5F56]/80" />
                  <div className="w-2.5 h-2.5 rounded-full bg-[#FFBD2E]/80" />
                  <div className="w-2.5 h-2.5 rounded-full bg-[#27C93F]/80" />
                  <span className="ml-3 font-mono text-[11px] tracking-widest text-titanium">
                    MATTER_DOSSIER_712.RAW
                  </span>
                </div>

                <div className="flex items-center gap-3">
                  <div className="hidden sm:inline-flex items-center gap-1.5 text-[10px] font-mono text-muted-gray">
                    <span className="w-1.5 h-1.5 rounded-full bg-champagne animate-pulse" />
                    OCR CONFIDENCE: 99.4%
                  </div>
                  <div className="px-2 py-0.5 rounded bg-slate-glass border border-hairline text-[10px] font-mono text-titanium">
                    MATTER: KALOL / 142/A (FIRM-ID: #2026-809)
                  </div>
                </div>
              </div>

              {/* Split Content Columns */}
              <div className="grid grid-cols-1 lg:grid-cols-12 divide-y lg:divide-y-0 lg:divide-x divide-hairline">
                {/* Left Column: Raw Scanned 7/12 Record Mockup in Gujarati */}
                <div className="lg:col-span-6 p-5 sm:p-6 bg-[#0E1116] flex flex-col justify-between">
                  <div>
                    {/* Raw Document Top Header */}
                    <div className="border-b border-hairline/80 pb-4 mb-4">
                      <div className="flex items-center justify-between text-[11px] font-mono text-titanium mb-1">
                        <span>મહેસૂલ દફતર પ્રમાણિત નકલ</span>
                        <span className="text-champagne font-semibold">ગામ નમૂનો નં. ૭ & ૮-અ</span>
                      </div>
                      <div className="text-xs text-light-gray font-serif tracking-wide">
                        અધિકાર પત્રક (ગાંધીનગર / કલોલ / મોજે કલોલ)
                      </div>
                    </div>

                    {/* Meta Indicators Grid */}
                    <div className="grid grid-cols-3 gap-2 p-3 bg-graphite/70 border border-hairline rounded-xl text-[11px] mb-4">
                      <div>
                        <div className="text-muted-gray text-[10px]">સર્વે નં. (Survey)</div>
                        <div className="text-light-gray font-mono font-medium">142/A (૧૪૨/અ)</div>
                      </div>
                      <div>
                        <div className="text-muted-gray text-[10px]">ખાતા નં. (Khata)</div>
                        <div className="text-light-gray font-mono font-medium">247</div>
                      </div>
                      <div>
                        <div className="text-muted-gray text-[10px]">સત્તા પ્રકાર (Tenure)</div>
                        <div className="text-champagne font-medium">Old Tenure (જૂની શરત)</div>
                      </div>
                    </div>

                    {/* Area & Assessment */}
                    <div className="flex items-center justify-between px-3 py-2 bg-obsidian/40 border border-hairline/60 rounded-lg text-[10px] font-mono text-titanium mb-5">
                      <span>ક્ષેત્રફળ (Area): 1-45-68 હે.આરે.ચો.મી.</span>
                      <span>આકાર (Assessment): ₹ 8.40</span>
                    </div>

                    {/* Mutation Registers Section */}
                    <div className="space-y-3">
                      <div className="text-[11px] font-mono text-titanium flex items-center justify-between">
                        <span>ફેરફાર નોંધ પત્રક (MUTATION LEDGER ENTRIES):</span>
                        <span className="text-[9px] text-muted-gray">SELECT ENTRY</span>
                      </div>

                      {/* Entry 312 */}
                      <button
                        type="button"
                        onClick={() => setActiveEntry('312')}
                        className={`w-full text-left p-3 rounded-xl border text-xs transition-all ${
                          activeEntry === '312'
                            ? 'bg-slate-glass border-champagne/60 text-light-gray shadow-sm'
                            : 'bg-graphite/40 border-hairline text-muted-gray hover:border-hairline/80'
                        }`}
                      >
                        <div className="flex items-center justify-between font-mono text-[10px] mb-1">
                          <span className="font-semibold text-titanium">નોંધ નં. ૩૧૨ (Entry 312)</span>
                          <span>તા. ૧૮/૦૫/૧૯૯૬</span>
                        </div>
                        <p className="text-[11px] leading-relaxed line-clamp-2">
                          વારસાઈ હક્ક નોંધ: મૂળ ખાતેદારના અવસાન બાદ પેઢીનામા મુજબ વારસદારોના નામો રેવન્યુ દફતરે દાખલ કરાયા.
                        </p>
                      </button>

                      {/* Entry 540 */}
                      <button
                        type="button"
                        onClick={() => setActiveEntry('540')}
                        className={`w-full text-left p-3 rounded-xl border text-xs transition-all ${
                          activeEntry === '540'
                            ? 'bg-slate-glass border-champagne/60 text-light-gray shadow-sm'
                            : 'bg-graphite/40 border-hairline text-muted-gray hover:border-hairline/80'
                        }`}
                      >
                        <div className="flex items-center justify-between font-mono text-[10px] mb-1">
                          <span className="font-semibold text-titanium">નોંધ નં. ૫૪૦ (Entry 540)</span>
                          <span>તા. ૦૨/૧૧/૨૦૦૮</span>
                        </div>
                        <p className="text-[11px] leading-relaxed line-clamp-2">
                          ખેતી ધિરાણ બોજો: સ્ટેટ બેંક ઓફ ઇન્ડિયા, કલોલ શાખા જોગ ₹ ૪,૫૦,૦૦૦ નું ધિરાણ. બોજા મુક્તિ પ્રમાણપત્ર તા. ૧૨/૦૩/૨૦૧૫.
                        </p>
                      </button>

                      {/* Entry 809 - HIGHLIGHTED */}
                      <button
                        type="button"
                        onClick={() => setActiveEntry('809')}
                        className={`w-full text-left p-3.5 rounded-xl border transition-all relative overflow-hidden ${
                          activeEntry === '809'
                            ? 'bg-slate-glass border-champagne text-light-gray shadow-[0_0_20px_rgba(130,119,96,0.15)] ring-1 ring-champagne/40'
                            : 'bg-graphite/60 border-champagne/40 text-light-gray hover:border-champagne'
                        }`}
                      >
                        <div className="flex items-center justify-between font-mono text-[10px] mb-1.5">
                          <span className="font-semibold text-champagne flex items-center gap-1.5">
                            <span className="w-1.5 h-1.5 rounded-full bg-champagne animate-pulse" />
                            નોંધ નં. ૮૦૯ (Entry 809 — Key Focus)
                          </span>
                          <span className="text-titanium">તા. ૧૪/૦૭/૨૦૧૭</span>
                        </div>
                        <p className="text-[11px] text-light-gray leading-relaxed mb-2">
                          રજીસ્ટર્ડ વેચાણ દસ્તાવેજ નં. ૨૪૫૧/૨૦૧૭ આધારે હક્ક દાખલ. જમીન મહેસૂલ કાયદાની કલમ ૧૩૫-ડી અન્વયે હિત ધરાવનારાઓને નોટિસ બજવણી કરાઈ. મુદતમાં કોઈ વાંધા ન આવતા મામલતદાર દ્વારા પ્રમાણિત કરાઈ.
                        </p>
                        <div className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded bg-champagne/15 border border-champagne/30 text-champagne text-[9px] font-mono tracking-wider">
                          <CheckCircle2 className="w-2.5 h-2.5" />
                          <span>SEC. 135D STATUTORY SERVICE CERTIFIED</span>
                        </div>
                      </button>
                    </div>
                  </div>

                  {/* Certified Stamp Badge */}
                  <div className="mt-5 pt-3 border-t border-hairline/60 flex items-center justify-between text-[10px] text-titanium font-mono">
                    <span className="flex items-center gap-1.5">
                      <ShieldCheck className="w-3.5 h-3.5 text-champagne" />
                      ઇ-ધરા ડિજિટલ રેકોર્ડ · Sub-Registrar Index-II Synced
                    </span>
                    <span className="text-muted-gray">FIRM DOSSIER #2026-809</span>
                  </div>
                </div>

                {/* Right Column: AI Extraction Cards */}
                <div className="lg:col-span-6 p-5 sm:p-6 bg-graphite/40 flex flex-col justify-between">
                  <div className="space-y-5">
                    {/* Card 1: Extracted Title Chain */}
                    <div className="bg-graphite border border-hairline rounded-xl p-4 sm:p-5 shadow-sm">
                      <div className="flex items-center justify-between pb-3 border-b border-hairline/80 mb-3">
                        <div className="flex items-center gap-2">
                          <Layers className="w-3.5 h-3.5 text-champagne" />
                          <h3 className="text-xs font-semibold text-light-gray uppercase tracking-wider">
                            Extracted Title Chain (1996–2026)
                          </h3>
                        </div>
                        <span className="text-[10px] font-mono text-titanium bg-slate-glass px-2 py-0.5 rounded border border-hairline">
                          30-YR UNBROKEN
                        </span>
                      </div>

                      {/* Timeline Steps */}
                      <div className="relative pl-5 space-y-3.5 before:absolute before:left-2 before:top-2 before:bottom-2 before:w-[1px] before:bg-hairline">
                        {/* 1996 Step */}
                        <div className="relative">
                          <span className="absolute -left-5 top-1 w-2.5 h-2.5 rounded-full bg-titanium/40 border border-graphite" />
                          <div className="flex items-baseline justify-between text-[11px]">
                            <span className="font-mono text-titanium">1996 · Entry 312</span>
                            <span className="text-[10px] text-muted-gray">Succession (વારસાઈ)</span>
                          </div>
                          <p className="text-[10px] text-muted-gray mt-0.5">
                            Unencumbered ancestral partition among coparceners.
                          </p>
                        </div>

                        {/* 2008 Step */}
                        <div className="relative">
                          <span className="absolute -left-5 top-1 w-2.5 h-2.5 rounded-full bg-titanium/40 border border-graphite" />
                          <div className="flex items-baseline justify-between text-[11px]">
                            <span className="font-mono text-titanium">2008 · Entry 540</span>
                            <span className="text-[10px] text-muted-gray">Agricultural Mortgage</span>
                          </div>
                          <p className="text-[10px] text-muted-gray mt-0.5">
                            Charge created for SBI credit; fully discharged in 2015 with registered NOC.
                          </p>
                        </div>

                        {/* 2017 Step - Highlighted */}
                        <div className="relative">
                          <span className="absolute -left-5 top-1 w-2.5 h-2.5 rounded-full bg-champagne border border-graphite ring-2 ring-champagne/30" />
                          <div className="flex items-baseline justify-between text-[11px]">
                            <span className="font-mono text-champagne font-medium">2017 · Entry 809 (Active)</span>
                            <span className="text-[10px] text-champagne">Registered Sale Deed</span>
                          </div>
                          <p className="text-[10px] text-light-gray mt-0.5">
                            Reg. No. 2451/2017. Section 135D notice served without objection. Mamlatdar certified.
                          </p>
                        </div>

                        {/* 2026 Step */}
                        <div className="relative">
                          <span className="absolute -left-5 top-1 w-2.5 h-2.5 rounded-full bg-titanium/40 border border-graphite" />
                          <div className="flex items-baseline justify-between text-[11px]">
                            <span className="font-mono text-titanium">2026 · Marketable Title</span>
                            <span className="text-[10px] text-muted-gray">No Pending Lis Pendens</span>
                          </div>
                          <p className="text-[10px] text-muted-gray mt-0.5">
                            Clean title verified against Sub-Registrar Index-II and revenue court registers.
                          </p>
                        </div>
                      </div>
                    </div>

                    {/* Card 2: Grounded Legal Draft Snippet */}
                    <div className="bg-graphite border border-hairline rounded-xl p-4 sm:p-5 shadow-sm">
                      <div className="flex items-center justify-between pb-3 border-b border-hairline/80 mb-3">
                        <div className="flex items-center gap-2">
                          <FileText className="w-3.5 h-3.5 text-champagne" />
                          <h3 className="text-xs font-semibold text-light-gray uppercase tracking-wider">
                            Chamber Appellate Brief Snippet
                          </h3>
                        </div>
                        <button
                          onClick={handleCopyDraft}
                          className="inline-flex items-center gap-1 text-[10px] font-mono text-titanium hover:text-champagne transition-colors"
                          title="Copy Draft"
                        >
                          {copiedDraft ? (
                            <>
                              <Check className="w-3 h-3 text-champagne" />
                              <span className="text-champagne">COPIED</span>
                            </>
                          ) : (
                            <>
                              <Copy className="w-3 h-3" />
                              <span>COPY CLAUSE</span>
                            </>
                          )}
                        </button>
                      </div>

                      <div className="p-3 bg-obsidian/70 border border-hairline rounded-lg font-mono text-[11px] text-light-gray/90 leading-relaxed mb-3 space-y-2">
                        <div className="text-champagne text-[10px] font-semibold">
                          [GROUND A: SECTION 135D STATUTORY COMPLIANCE & DELAY]
                        </div>
                        <p className="text-muted-gray text-[10px] sm:text-[11px]">
                          "It is respectfully submitted that Mutation Entry No. 809 was certified following strict statutory compliance of notice under <span className="text-light-gray font-medium underline decoration-champagne/60 underline-offset-2">Section 135D of the Gujarat Land Revenue Code, 1879</span>. The respondent's delayed challenge after 9 years is directly barred under the doctrine of reasonable time affirmed in <span className="text-light-gray font-medium">State of Gujarat v. Patel Raghav Natha (AIR 1969 SC 1297)</span>."
                        </p>
                      </div>

                      {/* Citation Grounding Verification Pill */}
                      <div className="flex flex-wrap items-center justify-between gap-2 pt-2 border-t border-hairline/60 text-[10px] font-mono text-titanium">
                        <div className="flex items-center gap-1.5 text-champagne">
                          <CheckCircle2 className="w-3.5 h-3.5" />
                          <span>Statutory Citation Grounded · Zero Hallucinations</span>
                        </div>
                        <span className="text-muted-gray">SSRD / Bombay LRC 1879</span>
                      </div>
                    </div>
                  </div>

                  {/* Extraction Card Action */}
                  <div className="mt-4 pt-3 border-t border-hairline/60 flex items-center justify-between">
                    <span className="text-[10px] text-muted-gray">
                      Ready for Partner Review, RTS Appeal Filing & Title Certificate.
                    </span>
                    <button
                      onClick={() => onNavigateToAuth('associate')}
                      className="inline-flex items-center gap-1 text-xs text-champagne hover:underline font-medium"
                    >
                      <span>Open Drafting Studio</span>
                      <ArrowRight className="w-3 h-3" />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* 4. THREE ENTERPRISE CAPABILITY CARDS */}
        <section id="chamber-solutions" className="py-16 md:py-24 px-4 sm:px-6 lg:px-8 border-t border-hairline">
          <div className="max-w-6xl mx-auto">
            {/* Section Header */}
            <div className="text-center max-w-2xl mx-auto mb-14">
              <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-graphite border border-hairline text-titanium text-[10px] font-mono uppercase tracking-widest mb-3">
                <BookOpen className="w-3 h-3 text-champagne" />
                Chamber Solutions
              </div>
              <h2 className="text-2xl sm:text-4xl font-light text-light-gray tracking-tight mb-4">
                Enterprise Infrastructure for Real Estate & Revenue Practices
              </h2>
              <p className="text-sm text-muted-gray leading-relaxed">
                Standardized intelligence tailored to law firm partners, litigation associates, and paralegals handling complex property transactions and appellate revenue forums.
              </p>
            </div>

            {/* 3 Grid Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Capability 1: Automated Land Due Diligence */}
              <div className="bg-graphite border border-hairline rounded-2xl p-6 sm:p-7 flex flex-col justify-between hover:border-champagne/40 transition-all duration-300 group">
                <div>
                  <div className="w-10 h-10 rounded-xl bg-slate-glass border border-hairline flex items-center justify-center mb-6 group-hover:border-champagne/50 transition-colors">
                    <FileText className="w-5 h-5 text-champagne" />
                  </div>
                  <h3 className="text-lg font-medium text-light-gray mb-2.5">
                    Automated Land Due Diligence
                  </h3>
                  <p className="text-xs sm:text-sm text-muted-gray leading-relaxed mb-6">
                    Deep OCR parsing of 7/12, 8A, and mutation registers to support complex property transactions and litigation.
                  </p>
                  
                  <div className="space-y-2.5 py-4 border-t border-hairline/60">
                    <div className="flex items-center gap-2 text-xs text-titanium">
                      <span className="w-1 h-1 rounded-full bg-champagne" />
                      <span>Archaic Modi & handwritten Gujarati revenue registers</span>
                    </div>
                    <div className="flex items-center gap-2 text-xs text-titanium">
                      <span className="w-1 h-1 rounded-full bg-champagne" />
                      <span>Automated 30-year unbroken title chain generation</span>
                    </div>
                    <div className="flex items-center gap-2 text-xs text-titanium">
                      <span className="w-1 h-1 rounded-full bg-champagne" />
                      <span>Instant flagging of conditional tenures (Navi Sharat)</span>
                    </div>
                  </div>
                </div>

                <div className="pt-4 border-t border-hairline/60 flex items-center justify-between text-[11px] font-mono text-titanium">
                  <span>TRANSACTION DILIGENCE</span>
                  <span className="text-champagne">PARSED IN SECONDS</span>
                </div>
              </div>

              {/* Capability 2: Citation-Grounded Drafting Studio */}
              <div className="bg-graphite border border-hairline rounded-2xl p-6 sm:p-7 flex flex-col justify-between hover:border-champagne/40 transition-all duration-300 group">
                <div>
                  <div className="w-10 h-10 rounded-xl bg-slate-glass border border-hairline flex items-center justify-center mb-6 group-hover:border-champagne/50 transition-colors">
                    <Scale className="w-5 h-5 text-champagne" />
                  </div>
                  <h3 className="text-lg font-medium text-light-gray mb-2.5">
                    Citation-Grounded Drafting Studio
                  </h3>
                  <p className="text-xs sm:text-sm text-muted-gray leading-relaxed mb-6">
                    Ready-to-file chamber templates for SSRD, Collector, and High Court filings with zero hallucination.
                  </p>

                  <div className="space-y-2.5 py-4 border-t border-hairline/60">
                    <div className="flex items-center gap-2 text-xs text-titanium">
                      <span className="w-1 h-1 rounded-full bg-champagne" />
                      <span>Section 135D, 203 & 211 GLRC statutory anchoring</span>
                    </div>
                    <div className="flex items-center gap-2 text-xs text-titanium">
                      <span className="w-1 h-1 rounded-full bg-champagne" />
                      <span>Automated Patel Raghav Natha delay bar synthesis</span>
                    </div>
                    <div className="flex items-center gap-2 text-xs text-titanium">
                      <span className="w-1 h-1 rounded-full bg-champagne" />
                      <span>Direct source paragraph linking in every chamber draft</span>
                    </div>
                  </div>
                </div>

                <div className="pt-4 border-t border-hairline/60 flex items-center justify-between text-[11px] font-mono text-titanium">
                  <span>CHAMBER TEMPLATES</span>
                  <span className="text-champagne">ZERO HALLUCINATIONS</span>
                </div>
              </div>

              {/* Capability 3: Firm Data Sovereignty */}
              <div id="firm-security" className="bg-graphite border border-hairline rounded-2xl p-6 sm:p-7 flex flex-col justify-between hover:border-champagne/40 transition-all duration-300 group">
                <div>
                  <div className="w-10 h-10 rounded-xl bg-slate-glass border border-hairline flex items-center justify-center mb-6 group-hover:border-champagne/50 transition-colors">
                    <Lock className="w-5 h-5 text-champagne" />
                  </div>
                  <h3 className="text-lg font-medium text-light-gray mb-2.5">
                    Firm Data Sovereignty
                  </h3>
                  <p className="text-xs sm:text-sm text-muted-gray leading-relaxed mb-6">
                    Isolated tenant vaults per firm, per-matter encryption keys, DPDP Act 2023 compliance, and zero model training on client files.
                  </p>

                  <div className="space-y-2.5 py-4 border-t border-hairline/60">
                    <div className="flex items-center gap-2 text-xs text-titanium">
                      <span className="w-1 h-1 rounded-full bg-champagne" />
                      <span>Dedicated encrypted tenant per chamber practice</span>
                    </div>
                    <div className="flex items-center gap-2 text-xs text-titanium">
                      <span className="w-1 h-1 rounded-full bg-champagne" />
                      <span>Role-gated matter files (Partners vs Associates vs Paralegals)</span>
                    </div>
                    <div className="flex items-center gap-2 text-xs text-titanium">
                      <span className="w-1 h-1 rounded-full bg-champagne" />
                      <span>Zero data retention on foundational LLM weights</span>
                    </div>
                  </div>
                </div>

                <div className="pt-4 border-t border-hairline/60 flex items-center justify-between text-[11px] font-mono text-titanium">
                  <span>STANDARD: DPDP 2023</span>
                  <span className="text-champagne">AIR-GAPPED VAULT</span>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* 5. PRACTICE AREAS & CHAMBER FORUMS */}
        <section id="practice-areas" className="py-16 md:py-20 px-4 sm:px-6 lg:px-8 border-t border-hairline bg-[#0E1116]/60">
          <div className="max-w-6xl mx-auto">
            <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-10">
              <div>
                <div className="text-[10px] font-mono text-champagne tracking-widest uppercase mb-1">
                  PRACTICE AREA COVERAGE
                </div>
                <h3 className="text-xl sm:text-2xl font-light text-light-gray">
                  Supported Law Firm Practice Groups
                </h3>
                <p className="text-xs text-muted-gray mt-1 max-w-xl">
                  Engineered to scale partner billables across real estate diligence, dispute resolution, and appellate revenue courts.
                </p>
              </div>
              <div className="flex items-center gap-3">
                <button
                  onClick={() => onNavigateToAuth('partner')}
                  className="px-5 py-2.5 rounded-full bg-champagne hover:bg-[#968a6f] text-obsidian text-xs font-medium tracking-wide transition-all inline-flex items-center gap-2"
                >
                  <Users className="w-3.5 h-3.5" />
                  <span>Chamber Gateway</span>
                </button>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="p-4 bg-graphite border border-hairline rounded-xl">
                <div className="text-xs font-medium text-light-gray mb-1">Real Estate Transactions</div>
                <p className="text-[11px] text-muted-gray leading-relaxed">
                  30-year search reports, mutation trace verification, encumbrance certificates & RERA title audit.
                </p>
              </div>

              <div className="p-4 bg-graphite border border-hairline rounded-xl">
                <div className="text-xs font-medium text-light-gray mb-1">Appellate Revenue Litigation</div>
                <p className="text-[11px] text-muted-gray leading-relaxed">
                  RTS appeals under Sec. 203, Suo Motu revisions under Sec. 211, and stay petitions before SSRD.
                </p>
              </div>

              <div className="p-4 bg-graphite border border-hairline rounded-xl">
                <div className="text-xs font-medium text-light-gray mb-1">Tenancy & Land Reforms</div>
                <p className="text-[11px] text-muted-gray leading-relaxed">
                  Gujarat Tenancy & Agricultural Lands Act, 1948 proceedings, 32M certificates, and farmer status audits.
                </p>
              </div>

              <div className="p-4 bg-graphite border border-hairline rounded-xl">
                <div className="text-xs font-medium text-light-gray mb-1">High Court Special Civil Applications</div>
                <p className="text-[11px] text-muted-gray leading-relaxed">
                  Writ petitions challenging SSRD & Gujarat Revenue Tribunal (GRT) final orders under Articles 226/227.
                </p>
              </div>
            </div>
          </div>
        </section>
      </main>

      {/* 6. MINIMAL FOOTER */}
      <footer className="border-t border-hairline bg-obsidian py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-start md:items-center justify-between gap-8 pb-10 border-b border-hairline/60">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <span className="text-light-gray font-semibold text-sm tracking-[0.24em]">
                NYAYSETU
              </span>
              <span className="px-2 py-0.5 rounded-full text-[9px] font-mono tracking-widest uppercase bg-graphite border border-hairline text-titanium">
                ENTERPRISE REVENUE AI
              </span>
            </div>
            <p className="text-xs text-muted-gray max-w-sm">
              NYAYSETU Enterprise — Indian Legal Intelligence.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-6 sm:gap-8 text-xs text-muted-gray">
            <button
              onClick={() => scrollToSection('chamber-solutions')}
              className="hover:text-light-gray transition-colors"
            >
              Chamber Solutions
            </button>
            <button
              onClick={() => scrollToSection('practice-areas')}
              className="hover:text-light-gray transition-colors"
            >
              Practice Areas
            </button>
            <button
              onClick={() => scrollToSection('firm-security')}
              className="hover:text-light-gray transition-colors"
            >
              Firm Security
            </button>
            <button
              onClick={() => onNavigateToAuth('partner')}
              className="hover:text-light-gray transition-colors"
            >
              Chamber Sign In
            </button>
          </div>
        </div>

        {/* Mandatory Legal Disclaimer */}
        <div className="max-w-6xl mx-auto pt-8 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 text-[11px] text-muted-gray/80">
          <p className="max-w-2xl leading-relaxed">
            <strong className="text-titanium font-medium">Mandatory Disclaimer:</strong> NYAYSETU is an AI assistance platform for advocates and law firms. It does not substitute independent legal judgment.
          </p>
          <div className="text-titanium/80 font-mono text-[10px] whitespace-nowrap">
            © 2026 NYAYSETU Legal Technologies. All rights reserved.
          </div>
        </div>
      </footer>

      {/* Architecture Modal */}
      <ArchitectureModal
        isOpen={isArchModalOpen}
        onClose={() => setIsArchModalOpen(false)}
        onLaunchWorkspace={() => onNavigateToAuth('partner')}
      />
    </div>
  );
}
