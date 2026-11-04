import React, { useState } from 'react';
import {
  ZoomIn,
  ZoomOut,
  Eye,
  EyeOff,
  Upload,
  CheckCircle2,
  AlertTriangle,
  Lock,
  FileText,
  ShieldCheck,
  Sparkles
} from 'lucide-react';

export default function TabDocumentOcr({
  currentRole,
  onLogAction,
  onShowToast,
}) {
  const [zoom, setZoom] = useState(100);
  const [isRedacted, setIsRedacted] = useState(false);
  const [activeHighlight, setActiveHighlight] = useState('survey');
  const [showEncumbranceDetail, setShowEncumbranceDetail] = useState(false);

  // Form field states
  const [formData, setFormData] = useState({
    surveyNo: '142/A',
    khataNo: '247',
    tenure: 'Old Tenure / જૂની શરત',
    totalArea: '1-22-00 Hectares (12,200 Sq.m)',
    occupantName: 'Patel Rameshchandra K.',
    assessment: '₹ 14.80 per annum',
  });

  const isEditable = currentRole.id !== 'researcher';
  const canUpload = currentRole.id !== 'researcher';

  const handleZoomIn = () => setZoom((prev) => Math.min(prev + 15, 145));
  const handleZoomOut = () => setZoom((prev) => Math.max(prev - 15, 70));

  const handleBoxClick = (field) => {
    setActiveHighlight(field);
    onShowToast(`OCR Field Focused: ${field.toUpperCase()}`);
  };

  const handleSaveMetadata = () => {
    if (!isEditable) {
      onShowToast('Metadata editing restricted for Legal Researcher role.');
      return;
    }
    onLogAction(`${currentRole.shortLabel} validated & updated 7/12 metadata for Survey ${formData.surveyNo}`);
    onShowToast('7/12 Metadata successfully verified and committed to vault.');
  };

  const handleUploadSimulate = () => {
    if (!canUpload) {
      onShowToast('Document upload restricted to Paralegals, Associates, and Partners.');
      return;
    }
    onLogAction(`${currentRole.shortLabel} uploaded 'Mamlatdar_Certified_712_Extract_2026.pdf'`);
    onShowToast('Document ingested. Devanagari OCR pipeline matched 99.4% confidence.');
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 animate-fade-in">
      {/* LEFT COLUMN: Scanned Gujarati 7/12 Document Viewer (7 cols) */}
      <div className="lg:col-span-7 bg-graphite border border-hairline rounded-2xl overflow-hidden flex flex-col justify-between shadow-xl">
        {/* Document Viewer Header Toolbar */}
        <div className="px-4 py-3 bg-[#12151A] border-b border-hairline flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <span className="font-mono text-xs text-titanium flex items-center gap-1.5">
              <FileText className="w-3.5 h-3.5 text-champagne" />
              E-DHARA_EXTRACT_712_2026.RAW
            </span>
            <span className="text-[10px] font-mono text-champagne bg-champagne/10 px-2 py-0.5 rounded border border-champagne/30">
              ORIGINAL ARCHIVE
            </span>
          </div>

          {/* Action Toolbar */}
          <div className="flex items-center gap-2">
            {/* Zoom Controls */}
            <div className="flex items-center bg-obsidian/70 border border-hairline rounded-lg p-0.5 text-xs text-titanium">
              <button
                onClick={handleZoomOut}
                className="p-1 hover:text-light-gray transition-colors"
                title="Zoom Out"
              >
                <ZoomOut className="w-3.5 h-3.5" />
              </button>
              <span className="px-2 font-mono text-[10px]">{zoom}%</span>
              <button
                onClick={handleZoomIn}
                className="p-1 hover:text-light-gray transition-colors"
                title="Zoom In"
              >
                <ZoomIn className="w-3.5 h-3.5" />
              </button>
            </div>

            {/* PII Redaction Toggle */}
            <button
              onClick={() => {
                setIsRedacted(!isRedacted);
                onShowToast(isRedacted ? 'PII Unmasked for Authorized Counsel' : 'PII Redacted with Blackout Masks');
              }}
              className={`inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg border text-xs font-mono transition-all ${
                isRedacted
                  ? 'bg-champagne/20 border-champagne text-champagne'
                  : 'bg-obsidian/70 border-hairline text-titanium hover:text-light-gray'
              }`}
              title="Toggle PII Privacy Redaction"
            >
              {isRedacted ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
              <span className="text-[10px]">{isRedacted ? 'PII REDACTED' : 'MASK PII'}</span>
            </button>

            {/* Document Upload Button */}
            <button
              onClick={handleUploadSimulate}
              disabled={!canUpload}
              className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                canUpload
                  ? 'bg-champagne hover:bg-[#968a6f] text-obsidian shadow-sm'
                  : 'bg-obsidian/50 border border-hairline/60 text-muted-gray cursor-not-allowed opacity-60'
              }`}
              title={canUpload ? 'Upload Land Records' : 'Upload locked for Legal Researcher'}
            >
              {canUpload ? <Upload className="w-3.5 h-3.5" /> : <Lock className="w-3.5 h-3.5" />}
              <span>Upload PDF</span>
            </button>
          </div>
        </div>

        {/* Document Content Canvas */}
        <div className="p-6 bg-[#0B0D10]/95 flex-1 overflow-auto max-h-[620px]">
          <div
            style={{ transform: `scale(${zoom / 100})`, transformOrigin: 'top left' }}
            className="transition-transform duration-200 w-full min-w-[500px] border border-hairline/80 rounded-xl p-6 bg-[#111419] shadow-inner relative"
          >
            {/* Watermark */}
            <div className="absolute inset-0 flex items-center justify-center pointer-events-none opacity-5">
              <span className="text-6xl font-serif text-light-gray tracking-widest rotate-[-25deg]">
                REVENUE RECORD
              </span>
            </div>

            {/* Official Gujarat Revenue Header */}
            <div className="border-b-2 border-hairline/60 pb-4 mb-5 text-center">
              <div className="text-[11px] font-mono text-champagne tracking-wider">
                ગુજરાત સરકાર — મહેસૂલ વિભાગ
              </div>
              <h2 className="text-base font-serif text-light-gray tracking-wide mt-0.5">
                ગામ નમૂનો નં. ૭ (અધિકાર પત્રક) તથા ગામ નમૂનો નં. ૮-અ
              </h2>
              <div className="text-[11px] text-muted-gray font-serif mt-1">
                મોજે: બાવળા | તાલુકો: બાવળા | જિલ્લો: અમદાવાદ
              </div>
            </div>

            {/* Interactive Document Grid */}
            <div className="grid grid-cols-3 gap-3 mb-5">
              {/* Box 1: Survey Number (Interactive Bounding Box) */}
              <div
                onClick={() => handleBoxClick('survey')}
                className={`p-3 rounded-lg border cursor-pointer transition-all ${
                  activeHighlight === 'survey'
                    ? 'border-champagne bg-champagne/15 ring-2 ring-champagne/40'
                    : 'border-dashed border-champagne/40 bg-obsidian/60 hover:border-champagne'
                }`}
              >
                <div className="flex items-center justify-between text-[10px] font-mono text-champagne mb-1">
                  <span>સર્વે / બ્લોક નં.</span>
                  <span className="text-[9px] uppercase">[CLICK OCR]</span>
                </div>
                <div className="text-sm font-semibold font-mono text-light-gray">
                  142/A (૧૪૨/અ)
                </div>
              </div>

              {/* Box 2: Khata Number */}
              <div
                onClick={() => handleBoxClick('khata')}
                className={`p-3 rounded-lg border cursor-pointer transition-all ${
                  activeHighlight === 'khata'
                    ? 'border-champagne bg-champagne/15 ring-2 ring-champagne/40'
                    : 'border-hairline bg-obsidian/40 hover:border-hairline/80'
                }`}
              >
                <div className="text-[10px] font-mono text-muted-gray mb-1">ખાતા નં.</div>
                <div className="text-sm font-semibold font-mono text-light-gray">
                  247
                </div>
              </div>

              {/* Box 3: Tenure (Interactive Bounding Box) */}
              <div
                onClick={() => handleBoxClick('tenure')}
                className={`p-3 rounded-lg border cursor-pointer transition-all ${
                  activeHighlight === 'tenure'
                    ? 'border-champagne bg-champagne/15 ring-2 ring-champagne/40'
                    : 'border-dashed border-champagne/40 bg-obsidian/60 hover:border-champagne'
                }`}
              >
                <div className="flex items-center justify-between text-[10px] font-mono text-champagne mb-1">
                  <span>સત્તા પ્રકાર</span>
                  <span className="text-[9px] uppercase">[CLICK OCR]</span>
                </div>
                <div className="text-xs font-semibold text-champagne">
                  જૂની શરત (Old Tenure)
                </div>
              </div>
            </div>

            {/* Occupants & Area Table */}
            <div className="border border-hairline/80 rounded-lg overflow-hidden mb-5 text-xs">
              <div className="grid grid-cols-2 bg-obsidian/80 border-b border-hairline text-titanium text-[11px] p-2.5 font-mono">
                <div>ખાતેદારનું નામ (Occupant)</div>
                <div>ક્ષેત્રફળ (Area) & આકાર</div>
              </div>
              <div className="p-3 bg-graphite/40 flex items-center justify-between font-serif">
                <div>
                  {isRedacted ? (
                    <span className="inline-block bg-black text-black/0 px-4 py-0.5 rounded select-none">
                      XXXXXXXXXXXXXX
                    </span>
                  ) : (
                    <span className="text-light-gray font-medium">
                      પટેલ રમેશચંદ્ર કેશવલાલ (Patel Rameshchandra K.)
                    </span>
                  )}
                  <div className="text-[10px] text-muted-gray font-mono mt-0.5">
                    વારસાઈ હક્ક નં. ૪૧૦ અન્વયે હક્ક દાખલ
                  </div>
                </div>
                <div className="text-right font-mono text-xs text-light-gray">
                  <div>1-22-00 હે.આરે.ચો.મી.</div>
                  <div className="text-[10px] text-muted-gray">આકાર: ₹ 14.80</div>
                </div>
              </div>
            </div>

            {/* Box 4: Mutation 809 (Interactive Bounding Box) */}
            <div
              onClick={() => handleBoxClick('mutation')}
              className={`p-3.5 rounded-xl border cursor-pointer transition-all ${
                activeHighlight === 'mutation'
                  ? 'border-champagne bg-champagne/15 ring-2 ring-champagne/40 shadow-lg'
                  : 'border-dashed border-champagne/60 bg-obsidian/70 hover:border-champagne'
              }`}
            >
              <div className="flex items-center justify-between font-mono text-[10px] text-champagne mb-1">
                <span className="font-semibold flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-champagne animate-pulse" />
                  નોંધ નં. ૮૦૯ (Mutation Entry 809 — Litigated Focus)
                </span>
                <span>તા. ૧૪/૦૭/૨૦૧૭</span>
              </div>
              <p className="text-[11px] text-light-gray leading-relaxed font-serif">
                નોંધણીકૃત વેચાણ દસ્તાવેજ નં. ૨૪૫૧/૨૦૧૭ અન્વયે હક્ક દાખલ. જમીન મહેસૂલ કાયદાની કલમ ૧૩૫-ડી અન્વયે નોટિસ બજવણી કરાઈ અને વાંધા ન આવતા મામલતદાર બાવળા દ્વારા પ્રમાણિત કરાઈ.
              </p>
              <div className="mt-2 flex items-center justify-between text-[10px] font-mono text-titanium pt-2 border-t border-hairline/60">
                <span className="text-champagne flex items-center gap-1">
                  <CheckCircle2 className="w-3 h-3" />
                  Sec. 135D Compliance Certified
                </span>
                <span className="text-muted-gray">MAMLATDAR BAVLA STAMP</span>
              </div>
            </div>

            {/* Official Digital Seal */}
            <div className="mt-5 pt-3 border-t border-hairline/60 flex items-center justify-between text-[10px] font-mono text-titanium">
              <span className="flex items-center gap-1.5">
                <ShieldCheck className="w-3.5 h-3.5 text-champagne" />
                મામલતદાર કચેરી બાવળા - પ્રમાણિત ઇ-નકલ
              </span>
              <span>INDEX-II VERIFIED</span>
            </div>
          </div>
        </div>

        {/* Bottom Status bar */}
        <div className="px-4 py-2.5 bg-[#12151A] border-t border-hairline flex items-center justify-between text-[11px] font-mono text-muted-gray">
          <span>PII REDACTION: {isRedacted ? 'ACTIVE (SECURE)' : 'OFF (VISIBLE)'}</span>
          <span className="text-titanium">ACTIVE FIELD: {activeHighlight.toUpperCase()}</span>
        </div>
      </div>

      {/* RIGHT COLUMN: Extracted Structured Record (5 cols) */}
      <div className="lg:col-span-5 space-y-4">
        <div className="bg-graphite border border-hairline rounded-2xl p-5 sm:p-6 shadow-xl space-y-5">
          {/* Header */}
          <div className="flex items-center justify-between border-b border-hairline pb-3.5">
            <div>
              <div className="flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-champagne" />
                <h3 className="text-xs font-semibold text-light-gray uppercase tracking-wider">
                  Extracted Structured Record
                </h3>
              </div>
              <p className="text-[11px] text-muted-gray mt-0.5">
                Verified against Revenue Department e-Dhara Ledger.
              </p>
            </div>
            <span className="text-[10px] font-mono text-champagne bg-slate-glass px-2 py-0.5 rounded border border-hairline">
              CONFIDENCE: 99.4%
            </span>
          </div>

          {/* Form Fields */}
          <div className="space-y-3.5">
            {/* Survey Number */}
            <div className={`p-2.5 rounded-xl border transition-all ${
              activeHighlight === 'survey' ? 'border-champagne bg-champagne/10' : 'border-hairline bg-obsidian/50'
            }`}>
              <label className="block text-[10px] font-mono text-titanium uppercase mb-1">
                Survey Number (સર્વે નંબર)
              </label>
              <input
                type="text"
                disabled={!isEditable}
                value={formData.surveyNo}
                onChange={(e) => setFormData({ ...formData, surveyNo: e.target.value })}
                className="w-full bg-transparent text-xs text-light-gray font-mono font-medium focus:outline-none disabled:opacity-75"
              />
            </div>

            {/* Khata Number */}
            <div className={`p-2.5 rounded-xl border transition-all ${
              activeHighlight === 'khata' ? 'border-champagne bg-champagne/10' : 'border-hairline bg-obsidian/50'
            }`}>
              <label className="block text-[10px] font-mono text-titanium uppercase mb-1">
                Khata Number (ખાતા નંબર)
              </label>
              <input
                type="text"
                disabled={!isEditable}
                value={formData.khataNo}
                onChange={(e) => setFormData({ ...formData, khataNo: e.target.value })}
                className="w-full bg-transparent text-xs text-light-gray font-mono font-medium focus:outline-none disabled:opacity-75"
              />
            </div>

            {/* Land Tenure */}
            <div className={`p-2.5 rounded-xl border transition-all ${
              activeHighlight === 'tenure' ? 'border-champagne bg-champagne/10' : 'border-hairline bg-obsidian/50'
            }`}>
              <label className="block text-[10px] font-mono text-titanium uppercase mb-1">
                Land Tenure (સત્તા પ્રકાર)
              </label>
              <input
                type="text"
                disabled={!isEditable}
                value={formData.tenure}
                onChange={(e) => setFormData({ ...formData, tenure: e.target.value })}
                className="w-full bg-transparent text-xs text-champagne font-medium focus:outline-none disabled:opacity-75"
              />
            </div>

            {/* Total Area */}
            <div className="p-2.5 rounded-xl border border-hairline bg-obsidian/50">
              <label className="block text-[10px] font-mono text-titanium uppercase mb-1">
                Total Land Area (ક્ષેત્રફળ)
              </label>
              <input
                type="text"
                disabled={!isEditable}
                value={formData.totalArea}
                onChange={(e) => setFormData({ ...formData, totalArea: e.target.value })}
                className="w-full bg-transparent text-xs text-light-gray font-mono focus:outline-none disabled:opacity-75"
              />
            </div>

            {/* Registered Occupant */}
            <div className="p-2.5 rounded-xl border border-hairline bg-obsidian/50">
              <label className="block text-[10px] font-mono text-titanium uppercase mb-1">
                Registered Occupant (ખાતેદારનું નામ)
              </label>
              <input
                type="text"
                disabled={!isEditable}
                value={isRedacted ? '[REDACTED BY FIRM POLICY]' : formData.occupantName}
                onChange={(e) => setFormData({ ...formData, occupantName: e.target.value })}
                className="w-full bg-transparent text-xs text-light-gray focus:outline-none disabled:opacity-75 font-serif"
              />
            </div>
          </div>

          {/* Active Encumbrances Box (Clickable Alert) */}
          <div
            onClick={() => setShowEncumbranceDetail(!showEncumbranceDetail)}
            className="p-3.5 bg-obsidian/70 border border-amber-500/40 hover:border-amber-500 rounded-xl cursor-pointer transition-all"
          >
            <div className="flex items-center justify-between text-xs">
              <div className="flex items-center gap-2 text-amber-400 font-medium">
                <AlertTriangle className="w-4 h-4 shrink-0" />
                <span>SBI Agricultural Mortgage (Active since 2018)</span>
              </div>
              <span className="text-[10px] font-mono text-titanium">
                {showEncumbranceDetail ? 'HIDE DETAILS ▲' : 'VIEW DETAILS ▼'}
              </span>
            </div>

            {showEncumbranceDetail && (
              <div className="mt-3 pt-3 border-t border-hairline/60 space-y-1.5 text-[11px] text-muted-gray animate-fade-in">
                <div className="flex justify-between">
                  <span>Mortgage Deed Reg. No:</span>
                  <span className="font-mono text-light-gray">3412 / 2018 (Bavla SR)</span>
                </div>
                <div className="flex justify-between">
                  <span>Principal Charge:</span>
                  <span className="font-mono text-light-gray">₹ 8,50,000 (SBI Bavla Branch)</span>
                </div>
                <div className="flex justify-between">
                  <span>No Objection Certificate:</span>
                  <span className="text-amber-400 font-medium">Pending Discharge Entry in Ferfar</span>
                </div>
              </div>
            )}
          </div>

          {/* Save & Validate Metadata Button */}
          <button
            onClick={handleSaveMetadata}
            disabled={!isEditable}
            className={`w-full py-2.5 rounded-xl text-xs font-medium tracking-wide flex items-center justify-center gap-2 transition-all ${
              isEditable
                ? 'bg-champagne hover:bg-[#968a6f] text-obsidian shadow-md active:scale-[0.99]'
                : 'bg-obsidian/40 border border-hairline text-muted-gray cursor-not-allowed opacity-60'
            }`}
          >
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>{isEditable ? 'Save & Validate Metadata' : 'Metadata Validation Locked (Researcher)'}</span>
          </button>
        </div>
      </div>
    </div>
  );
}
