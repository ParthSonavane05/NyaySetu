import React, { useState } from 'react';
import {
  CheckCircle2,
  Lock,
  Download,
  Copy,
  Check,
  X,
  BookOpen,
  Sparkles
} from 'lucide-react';

export default function TabDraftingStudio({
  currentRole,
  insertedCitations = [],
  onLogAction,
  onShowToast,
}) {
  const [selectedTemplate, setSelectedTemplate] = useState('sec203');
  const [selectedLanguage, setSelectedLanguage] = useState('en'); // 'en' | 'gu' | 'hi'
  const [copiedDraft, setCopiedDraft] = useState(false);
  const [isApproved, setIsApproved] = useState(false);
  const [selectedCitationDetail, setSelectedCitationDetail] = useState(null);

  const canApprove = currentRole.id === 'partner';
  const canExport = currentRole.id === 'partner' || currentRole.id === 'associate';

  // Multi-language petition texts
  const drafts = {
    sec203: {
      en: {
        title: 'BEFORE THE HON’BLE DEPUTY COLLECTOR (PRANT OFFICER), DHOLKA-BAVLA',
        subtitle: 'RTS REVENUE APPEAL NO. 42 OF 2026',
        parties: 'Patel Rameshchandra K. (Appellant) vs. State of Gujarat & Anr. (Respondents)',
        subject: 'APPEAL UNDER SECTION 203 OF THE BOMBAY LAND REVENUE CODE, 1879',
        grounds: [
          {
            num: '1',
            text: 'The impugned order dated 08.01.2026 passed by the Ld. Mamlatdar, Bavla reopening certified Mutation Entry No. 809 after an inexplicable delay of 9 years is ex-facie illegal, arbitrary, and without jurisdiction.',
            tags: [
              { label: 'Evidence: 7/12 Pg. 1, Col. 4', type: 'doc', content: 'Village Form No. 7/12, Kalol/Bavla Moje, Survey No. 142/A, certified on 14.07.2017 without pending disputes.' },
              { label: 'Statute: BLRC Sec. 135D', type: 'statute', content: 'Section 135D, Bombay Land Revenue Code 1879: The revenue officer shall serve notice on all persons appearing from the record of rights to be interested in the mutation.' },
            ],
          },
          {
            num: '2',
            text: 'The statutory notice as mandated under Section 135D was personally served upon all predecessor co-owners and interested parties on 22.06.2017. No objection was raised within the prescribed 30-day window, whereupon the Mamlatdar certified the entry.',
            tags: [
              { label: 'Evidence: Ferfar Nondh #809', type: 'doc', content: 'Ferfar Nondh Register No. 6: Statutory 30-day notice served; certificate issued under signature of Mamlatdar Bavla.' },
              { label: 'Precedent: AIR 1969 SC 1297', type: 'precedent', content: 'State of Gujarat v. Patel Raghav Natha (AIR 1969 SC 1297): The revisional and supervisory powers under the Land Revenue Code must be exercised within a reasonable time.' },
            ],
          },
          {
            num: '3',
            text: 'It is a settled proposition of law that revenue authorities have no jurisdiction to adjudicate upon complicated questions of title or validity of registered sale deeds in summary mutation proceedings.',
            tags: [
              { label: 'Precedent: 2008 (3) GLH 440', type: 'precedent', content: 'Evergreen Apartment Co-op. Housing Society v. Special Secretary (2008): Revenue officers cannot sit in judgment over registered conveyance deeds.' },
            ],
          },
        ],
        prayer: 'WHEREFORE, it is respectfully prayed that this Hon’ble Court be pleased to quash and set aside the impugned order dated 08.01.2026 and confirm Mutation Entry No. 809 as final and binding.',
      },
      gu: {
        title: 'માનનીય નાયબ કલેક્ટર શ્રી (પ્રાંત અધિકારી), ધોળકા-બાવળા ની કોર્ટમાં',
        subtitle: 'આર.ટી.એસ. રેવન્યુ અપીલ નં. ૪૨ / ૨૦૨૬',
        parties: 'પટેલ રમેશચંદ્ર કે. (અપીલકર્તા) વિરુદ્ધ ગુજરાત સરકાર અને અન્ય (સામાવાળા)',
        subject: 'જમીન મહેસૂલ કાયદાની કલમ ૨૦૩ અન્વયે દાખલ કરેલ અપીલ અરજી',
        grounds: [
          {
            num: '૧',
            text: 'મામલતદાર શ્રી બાવળા દ્વારા ૯ વર્ષના અક્ષમ્ય વિલંબ બાદ પ્રમાણિત નોંધ નં. ૮૦૯ ની પુનઃ તપાસણી કરવાનો હુકમ કાયદાકીય દ્રષ્ટિએ ગેરબંધારણીય અને હકુમત બહારનો છે.',
            tags: [
              { label: 'પુરાવો: ગામ નમૂનો નં. ૭/૧૨', type: 'doc', content: 'ગામ નમૂનો નં. ૭/૧૨ સર્વે નં. ૧૪૨/અ ખાતા નં. ૨૪૭.' },
              { label: 'કાયદાકીય જોગવાઈ: કલમ ૧૩૫-ડી', type: 'statute', content: 'જમીન મહેસૂલ કાયદાની કલમ ૧૩૫-ડી અન્વયે તમામ પક્ષકારોને નોટિસ બજવણી ફરજિયાત છે.' },
            ],
          },
          {
            num: '૨',
            text: 'નોંધ નં. ૮૦૯ ની કલમ ૧૩૫-ડી ની નોટિસ નિયમ મુજબ તમામ હિતધારકોને બજવાઈ હતી અને ૩૦ દિવસમાં કોઈ વાંધો ન આવતા યોગ્ય પ્રક્રિયાથી પ્રમાણિત થયેલ છે.',
            tags: [
              { label: 'પુરાવો: ફેરફાર નોંધ નં. ૮૦૯', type: 'doc', content: 'ફેરફાર નોંધ નં. ૮૦૯: મામલતદાર કચેરી પ્રમાણિત નકલ.' },
              { label: 'ચુકાદો: AIR 1969 SC 1297', type: 'precedent', content: 'સ્ટેટ ઓફ ગુજરાત વિ. પટેલ રાઘવ નાથા: વ્યાજબી સમય મર્યાદાનો સિદ્ધાંત.' },
            ],
          },
        ],
        prayer: 'આથી નમ્ર પ્રાર્થના છે કે તા. ૦૮/૦૧/૨૦૨૬ નો રદબાતલ હુકમ રદ કરી ફેરફાર નોંધ નં. ૮૦૯ કાયમ રાખવા હુકમ કરવા કૃપા કરશોજી.',
      },
      hi: {
        title: 'माननीय उप-कलेक्टर (प्रांत अधिकारी), धोलका-बावला के समक्ष',
        subtitle: 'राजस्व अपील संख्या ४२ / २०२६',
        parties: 'पटेल रमेशचंद्र के. (अपीलार्थी) बनाम गुजरात राज्य एवं अन्य (प्रतिवादी)',
        subject: 'बॉम्बे लैंड रेवेन्यू कोड, १८७९ की धारा २०३ के तहत राजस्व अपील',
        grounds: [
          {
            num: '१',
            text: 'मामलतदार बावला द्वारा ९ वर्ष के अत्यधिक विलंब के बाद प्रमाणित म्यूटेशन प्रविष्टि संख्या ८०९ को पुनः खोलने का आदेश क्षेत्राधिकार से परे एवं विधि विरुद्ध है।',
            tags: [
              { label: 'साक्ष्य: ७/१२ पृष्ठ १', type: 'doc', content: 'ग्राम नमूना संख्या ७/१२, सर्वे १४२/अ।' },
              { label: 'विधि: बीएलआरसी धारा १३५-डी', type: 'statute', content: 'म्यूटेशन नोटिस तामील की वैधानिक अनिवार्यता।' },
            ],
          },
        ],
        prayer: 'अतः सविनय प्रार्थना है कि आलोच्य आदेश को निरस्त कर म्यूटेशन प्रविष्टि संख्या ८०९ को वैध घोषित किया जाए।',
      },
    },
    sec211: {
      en: {
        title: 'BEFORE THE HON’BLE SPECIAL SECRETARY (REVENUE DEPARTMENT), AHMEDABAD',
        subtitle: 'REVISION APPLICATION UNDER SECTION 211 OF BOMBAY LAND REVENUE CODE',
        parties: 'Patel Rameshchandra K. (Revisionist) vs. District Collector, Ahmedabad & Ors.',
        subject: 'CHAMBER REVISION PETITION AGAINST BELATED SUO MOTU NOTICE',
        grounds: [
          {
            num: '1',
            text: 'The District Collector has committed a manifest error of law by exercising suo motu powers under Section 211 after a lapse of nearly a decade.',
            tags: [
              { label: 'Statute: BLRC Sec. 211', type: 'statute', content: 'Section 211: Revisional jurisdiction of State Government and revenue officers.' },
              { label: 'Precedent: AIR 1969 SC 1297', type: 'precedent', content: 'Raghav Natha: Suo motu revisional power cannot be exercised after 9 years.' },
            ],
          },
        ],
        prayer: 'Quash and set aside the Suo Motu Show Cause Notice issued by the Collector.',
      },
      gu: {
        title: 'માનનીય વિશેષ સચિવ શ્રી (મહેસૂલ વિભાગ) એસ.એસ.આર.ડી. અમદાવાદ',
        subtitle: 'જમીન મહેસૂલ કાયદાની કલમ ૨૧૧ અન્વયે રિવિઝન અરજી',
        parties: 'પટેલ રમેશચંદ્ર કે. વિરુદ્ધ જિલ્લા કલેક્ટર શ્રી અમદાવાદ',
        subject: 'સુઓ મોટો નોટિસ સામે ચેમ્બર રિવિઝન અરજી',
        grounds: [
          {
            num: '૧',
            text: 'જિલ્લા કલેક્ટર શ્રી દ્વારા લગભગ એક દાયકા બાદ સુઓ મોટો કલમ ૨૧૧ નો ઉપયોગ કરવો કાયદાની વિરુદ્ધ છે.',
            tags: [{ label: 'કાયદો: કલમ ૨૧૧ GLRC', type: 'statute', content: 'કલમ ૨૧૧ રિવિઝન સત્તાઓ.' }],
          },
        ],
        prayer: 'કલેક્ટર શ્રીની સુઓ મોટો નોટિસ રદ કરવા હુકમ કરશોજી.',
      },
      hi: {
        title: 'माननीय विशेष सचिव (राजस्व विभाग), अहमदाबाद',
        subtitle: 'धारा २११ के अंतर्गत पुनरीक्षण आवेदन',
        parties: 'पटेल रमेशचंद्र बनाम जिला कलेक्टर',
        subject: 'विलंबित सुओ मोटो नोटिस के विरुद्ध याचिका',
        grounds: [
          {
            num: '१',
            text: 'धारा २१૧ के अंतर्गत १० वर्ष बाद सुओ मोटो शक्ति का प्रयोग विधि विरुद्ध है।',
            tags: [{ label: 'विधि: धारा २११', type: 'statute', content: 'सुओ मोटो पुनरीक्षण सीमा।' }],
          },
        ],
        prayer: 'कलेक्टर द्वारा जारी कारण बताओ नोटिस को निरस्त किया जाए।',
      },
    },
    stay: {
      en: {
        title: 'BEFORE THE HON’BLE REVENUE APPELLATE FORUM, GUJARAT',
        subtitle: 'APPLICATION FOR INTERIM STAY / STATUS QUO PENDING APPEAL',
        parties: 'Patel Rameshchandra K. (Applicant) vs. State of Gujarat & Ors.',
        subject: 'APPLICATION FOR STAY UNDER SECTION 204 OF BOMBAY LAND REVENUE CODE',
        grounds: [
          {
            num: '1',
            text: 'The applicant has a prima facie strong case on merits, balance of convenience lies entirely in favor of the applicant, and irreparable injury will be caused if the revenue record is altered during appeal.',
            tags: [{ label: 'Statute: BLRC Sec. 204', type: 'statute', content: 'Power to suspend execution of order of subordinate revenue officer.' }],
          },
        ],
        prayer: 'Stay the implementation, operation, and execution of the impugned order pending final hearing.',
      },
      gu: {
        title: 'માનનીય મહેસૂલ કોર્ટ, ગુજરાત',
        subtitle: 'અપીલ પેન્ડિંગ દરમિયાન વચગાળાના મનાઈ હુકમ (સ્ટે) ની અરજી',
        parties: 'પટેલ રમેશચંદ્ર કે. વિરુદ્ધ ગુજરાત સરકાર',
        subject: 'કલમ ૨૦૪ અન્વયે વચગાળાના મનાઈ હુકમની અરજી',
        grounds: [
          {
            num: '૧',
            text: 'અરજદારના પક્ષે પ્રાઈમા ફેસી મજબૂત કેસ છે અને જો સ્ટે નહીં અપાય તો ન પૂરી શકાય તેવી નુકસાની થશે.',
            tags: [{ label: 'કાયદો: કલમ ૨૦૪', type: 'statute', content: 'હુકમની અમલવારી મોકૂફ રાખવાની સત્તા.' }],
          },
        ],
        prayer: 'અપીલની આખરી સુનાવણી સુધી વિવાદાસ્પદ હુકમ પર વચગાળાનો મનાઈ હુકમ આપવા વિનંતી.',
      },
      hi: {
        title: 'माननीय राजस्व न्यायालय',
        subtitle: 'अंतरिम स्थगन (Stay) हेतु प्रार्थना पत्र',
        parties: 'पटेल रमेशचंद्र बनाम गुजरात राज्य',
        subject: 'धारा २०४ के तहत स्थगन आवेदन',
        grounds: [
          {
            num: '१',
            text: 'अपीलार्थी के पक्ष में प्रथम दृष्टया वाद बनता है। स्थगन न दिए जाने पर अपूरणीय क्षति होगी।',
            tags: [{ label: 'विधि: धारा २०४', type: 'statute', content: 'अंतरिम स्थगन शक्ति।' }],
          },
        ],
        prayer: 'अपील के अंतिम निस्तारण तक आक्षेपित आदेश के क्रियान्वयन पर रोक लगाई जाए।',
      },
    },
    delay: {
      en: {
        title: 'BEFORE THE HON’BLE REVENUE APPELLATE FORUM',
        subtitle: 'APPLICATION FOR CONDONATION OF DELAY (SECTION 5, LIMITATION ACT, 1963)',
        parties: 'Patel Rameshchandra K. (Applicant) vs. State of Gujarat & Ors.',
        subject: 'APPLICATION FOR CONDONING DELAY IN FILING REVENUE APPEAL',
        grounds: [
          {
            num: '1',
            text: 'The certified copy of the impugned order was applied on 10.01.2026 and delivered on 28.01.2026. The applicant was prevented by sufficient cause due to medical hospitalization from filing within 60 days.',
            tags: [{ label: 'Statute: Sec. 5 Limitation Act', type: 'statute', content: 'Extension of prescribed period in certain cases on showing sufficient cause.' }],
          },
        ],
        prayer: 'Condone the procedural delay of 14 days in filing the accompanying appeal in the interest of justice.',
      },
      gu: {
        title: 'માનનીય મહેસૂલ અપીલ કોર્ટ',
        subtitle: 'વિલંબ માફી અરજી (કલમ ૫, લિમિટેશન એક્ટ ૧૯૬૩)',
        parties: 'પટેલ રમેશચંદ્ર કે. વિરુદ્ધ ગુજરાત સરકાર',
        subject: 'અપીલ દાખલ કરવામાં થયેલ વિલંબ માફ કરવાની અરજી',
        grounds: [
          {
            num: '૧',
            text: 'નકલ મળવામાં થયેલ વિલંબ અને વાજબી કારણોસર અપીલ દાખલ કરવામાં થયેલ ૧૪ દિવસનો વિલંબ માફ કરવો ન્યાયોચિત છે.',
            tags: [{ label: 'કાયદો: કલમ ૫ લિમિટેશન', type: 'statute', content: 'વાજબી કારણ સાબિત થયે વિલંબ માફી.' }],
          },
        ],
        prayer: 'ન્યાયના હિતમાં ૧૪ દિવસનો અપીલ વિલંબ માફ કરવા હુકમ કરશોજી.',
      },
      hi: {
        title: 'माननीय राजस्व अपीलीय न्यायालय',
        subtitle: 'विलंब क्षमा प्रार्थना पत्र (धारा ५, परिसीमा अधिनियम)',
        parties: 'पटेल रमेशचंद्र बनाम गुजरात राज्य',
        subject: 'अपील प्रस्तुत करने में हुए विलंब को क्षमा करने हेतु आवेदन',
        grounds: [
          {
            num: '१',
            text: 'पर्याप्त कारणों के चलते अपील दायर करने में हुए १४ दिनों के विलंब को न्यायहित में क्षमा किया जाए।',
            tags: [{ label: 'विधि: धारा ५', type: 'statute', content: 'विलंब क्षमादान प्रावधान।' }],
          },
        ],
        prayer: 'अपील में हुए विलंब को क्षमा कर अपील को सुनवाई हेतु स्वीकार किया जाए।',
      },
    },
  };

  const currentTemplateDrafts = drafts[selectedTemplate] || drafts.sec203;
  const activeDraft = currentTemplateDrafts[selectedLanguage] || currentTemplateDrafts.en;

  const handleCopy = () => {
    const text = `${activeDraft.title}\n${activeDraft.subtitle}\n\n${activeDraft.parties}\n\n${activeDraft.subject}\n\n${activeDraft.grounds.map((g) => `${g.num}. ${g.text}`).join('\n\n')}\n\nPRAYER:\n${activeDraft.prayer}`;
    navigator.clipboard?.writeText(text);
    setCopiedDraft(true);
    onShowToast('Court petition copied to clipboard.');
    setTimeout(() => setCopiedDraft(false), 2000);
  };

  const handleApproveSeal = () => {
    if (!canApprove) {
      onShowToast('Partner Approval Required: Only Senior Partners can seal court filings.');
      return;
    }
    setIsApproved(true);
    onLogAction(`Senior Partner sealed & digitally signed petition for filing under Enrollment GJ/1842/2016.`);
    onShowToast('Petition Sealed & Digitally Signed with Bar Council Credentials.');
  };

  const handleExportPdf = () => {
    if (!canExport) {
      onShowToast('Export restricted to Associate Advocates and Senior Partners.');
      return;
    }
    onLogAction(`${currentRole.shortLabel} exported verified court brief PDF for Matter #809.`);
    onShowToast('Generating clean court-formatted filing document (.PDF)...');
  };

  return (
    <div className="bg-graphite border border-hairline rounded-2xl p-6 shadow-xl space-y-6 animate-fade-in relative">
      {/* Top Studio Controls */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-hairline pb-4">
        {/* Template Selector */}
        <div className="flex flex-wrap items-center gap-3">
          <div className="text-xs font-mono text-titanium uppercase">
            CHAMBER TEMPLATE:
          </div>
          <select
            value={selectedTemplate}
            onChange={(e) => setSelectedTemplate(e.target.value)}
            className="px-3 py-1.5 rounded-xl bg-obsidian border border-hairline text-light-gray text-xs focus:outline-none focus:border-champagne transition-colors font-medium"
          >
            <option value="sec203">Appeal under Sec. 203 (Bombay Land Revenue Code)</option>
            <option value="sec211">Revision Application under Sec. 211 (SSRD)</option>
            <option value="stay">Interim Stay Application (Sec. 204 BLRC)</option>
            <option value="delay">Condonation of Delay (Sec. 5 Limitation Act)</option>
          </select>
        </div>

        {/* Language Switcher & Copy */}
        <div className="flex items-center gap-3">
          <div className="flex items-center p-1 bg-obsidian border border-hairline rounded-xl text-xs font-mono">
            <button
              onClick={() => setSelectedLanguage('en')}
              className={`px-2.5 py-1 rounded-lg transition-colors ${
                selectedLanguage === 'en' ? 'bg-champagne text-obsidian font-semibold' : 'text-titanium hover:text-light-gray'
              }`}
            >
              English
            </button>
            <button
              onClick={() => setSelectedLanguage('gu')}
              className={`px-2.5 py-1 rounded-lg transition-colors ${
                selectedLanguage === 'gu' ? 'bg-champagne text-obsidian font-semibold' : 'text-titanium hover:text-light-gray'
              }`}
            >
              ગુજરાતી
            </button>
            <button
              onClick={() => setSelectedLanguage('hi')}
              className={`px-2.5 py-1 rounded-lg transition-colors ${
                selectedLanguage === 'hi' ? 'bg-champagne text-obsidian font-semibold' : 'text-titanium hover:text-light-gray'
              }`}
            >
              हिन्दी
            </button>
          </div>

          <button
            onClick={handleCopy}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-hairline bg-obsidian hover:bg-obsidian/80 text-xs font-mono text-titanium hover:text-light-gray transition-colors"
          >
            {copiedDraft ? <Check className="w-3.5 h-3.5 text-champagne" /> : <Copy className="w-3.5 h-3.5" />}
            <span>{copiedDraft ? 'COPIED' : 'COPY'}</span>
          </button>
        </div>
      </div>

      {/* Petition Editor Preview Paper */}
      <div className="p-6 sm:p-8 bg-[#0E1116] border border-hairline/80 rounded-xl font-serif space-y-6 shadow-inner max-h-[640px] overflow-auto">
        {/* Court Header */}
        <div className="text-center border-b border-hairline/60 pb-5 space-y-1">
          <div className="text-sm font-semibold tracking-wide text-light-gray uppercase">
            {activeDraft.title}
          </div>
          <div className="text-xs text-titanium font-mono">
            {activeDraft.subtitle}
          </div>
        </div>

        {/* Cause Title */}
        <div className="text-xs text-light-gray font-medium leading-relaxed bg-obsidian/40 p-3 rounded-lg border border-hairline/40">
          {activeDraft.parties}
        </div>

        {/* Subject */}
        <div className="text-xs font-bold text-champagne tracking-wide uppercase border-l-2 border-champagne pl-3">
          {activeDraft.subject}
        </div>

        {/* Grounds */}
        <div className="space-y-4 text-xs leading-relaxed text-light-gray/90">
          <div className="font-semibold text-titanium font-mono text-[11px] uppercase tracking-wider">
            MEMORANDUM OF GROUNDS & EVIDENCE:
          </div>

          {activeDraft.grounds.map((ground) => (
            <div key={ground.num} className="p-3.5 bg-obsidian/50 border border-hairline/70 rounded-xl space-y-2.5">
              <div className="flex items-start gap-2.5">
                <span className="font-mono font-bold text-champagne text-[11px]">
                  {ground.num}.
                </span>
                <p className="flex-1 text-xs leading-relaxed">
                  {ground.text}
                </p>
              </div>

              {/* Interactive Citation Pills */}
              <div className="flex flex-wrap gap-2 pt-1.5 border-t border-hairline/40 pl-5">
                {ground.tags.map((tag, idx) => (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => setSelectedCitationDetail(tag)}
                    className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-slate-glass hover:bg-slate-glass/80 border border-hairline hover:border-champagne/60 text-[10px] font-mono text-champagne transition-all"
                  >
                    <BookOpen className="w-2.5 h-2.5" />
                    <span>{tag.label}</span>
                    <span className="text-titanium text-[9px]">↗</span>
                  </button>
                ))}
              </div>
            </div>
          ))}

          {/* Dynamic Inserted Citations (from Tab 4) */}
          {insertedCitations.length > 0 && (
            <div className="space-y-2 pt-2">
              <div className="text-[10px] font-mono text-champagne uppercase flex items-center gap-1.5">
                <Sparkles className="w-3 h-3" />
                <span>ADDITIONAL RESEARCH CITATIONS INSERTED:</span>
              </div>
              {insertedCitations.map((cite, i) => (
                <div key={i} className="p-3 bg-champagne/10 border border-champagne/40 rounded-xl text-xs space-y-1 animate-fade-in">
                  <div className="flex items-center justify-between font-mono text-[10px] text-champagne font-semibold">
                    <span>GROUND C.{i + 1}: {cite.caseName}</span>
                    <span>{cite.citation}</span>
                  </div>
                  <p className="text-[11px] text-light-gray leading-relaxed">
                    "{cite.holding}"
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Prayer Clause */}
        <div className="p-4 bg-obsidian/60 border border-hairline rounded-xl space-y-1.5">
          <div className="font-mono font-bold text-champagne text-[11px] uppercase">
            PRAYER CLAUSE:
          </div>
          <p className="text-xs text-light-gray italic leading-relaxed">
            {activeDraft.prayer}
          </p>
        </div>
      </div>

      {/* Action Toolbar */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-2">
        <div className="text-xs text-muted-gray flex items-center gap-2">
          {isApproved ? (
            <span className="inline-flex items-center gap-1.5 text-champagne font-mono text-[11px]">
              <CheckCircle2 className="w-4 h-4" />
              SEALED & DIGITALLY VERIFIED BY SENIOR PARTNER (GJ/1842/2016)
            </span>
          ) : (
            <span className="font-mono text-[11px] text-titanium">
              STATUS: DRAFT PREPARATION (REQUIRES PARTNER SEAL)
            </span>
          )}
        </div>

        <div className="flex items-center gap-3 w-full sm:w-auto">
          {/* Export PDF Button */}
          <button
            onClick={handleExportPdf}
            disabled={!canExport}
            className={`px-4 py-2.5 rounded-xl border text-xs font-medium inline-flex items-center justify-center gap-2 transition-all ${
              canExport
                ? 'bg-obsidian border-hairline hover:border-titanium/50 text-light-gray'
                : 'bg-obsidian/40 border-hairline/40 text-muted-gray cursor-not-allowed opacity-60'
            }`}
            title={canExport ? 'Export Court Filing PDF' : 'Export requires Advocate or Partner authorization'}
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export Clean Court PDF</span>
          </button>

          {/* Approve & Seal Button */}
          <button
            onClick={handleApproveSeal}
            disabled={!canApprove}
            className={`px-5 py-2.5 rounded-xl text-xs font-medium tracking-wide inline-flex items-center justify-center gap-2 transition-all ${
              canApprove
                ? isApproved
                  ? 'bg-emerald-500/20 border border-emerald-500/50 text-emerald-400'
                  : 'bg-champagne hover:bg-[#968a6f] text-obsidian shadow-md active:scale-[0.98]'
                : 'bg-obsidian/40 border border-hairline text-muted-gray cursor-not-allowed opacity-60'
            }`}
            title={canApprove ? 'Approve & Seal Court Filing' : 'Partner Approval Required'}
          >
            {canApprove ? (
              <>
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>{isApproved ? 'Approved & Sealed' : 'Approve & Seal Draft'}</span>
              </>
            ) : (
              <>
                <Lock className="w-3.5 h-3.5" />
                <span>Partner Approval Required</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Citation Detail Modal / Slide-Over Drawer */}
      {selectedCitationDetail && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-obsidian/80 backdrop-blur-md animate-fade-in">
          <div className="bg-graphite border border-hairline rounded-2xl p-6 max-w-lg w-full shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-hairline pb-3">
              <div className="flex items-center gap-2">
                <BookOpen className="w-4 h-4 text-champagne" />
                <h4 className="text-xs font-semibold text-light-gray uppercase tracking-wider">
                  Underlying Citation Grounding
                </h4>
              </div>
              <button
                onClick={() => setSelectedCitationDetail(null)}
                className="p-1 text-muted-gray hover:text-light-gray"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="text-xs text-champagne font-mono font-medium">
              {selectedCitationDetail.label}
            </div>

            <p className="text-xs text-light-gray/90 leading-relaxed p-3.5 bg-obsidian/70 border border-hairline rounded-xl">
              {selectedCitationDetail.content}
            </p>

            <div className="pt-2 flex justify-end">
              <button
                onClick={() => setSelectedCitationDetail(null)}
                className="px-4 py-2 bg-champagne text-obsidian text-xs font-medium rounded-lg"
              >
                Close Inspector
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
