import React, { useState } from 'react';
import {
  Calendar,
  AlertTriangle,
  CheckCircle2,
  Scale,
  CalendarCheck
} from 'lucide-react';

export default function TabLimitation({
  onLogAction,
  onShowToast,
  currentRole,
}) {
  // Date of service of impugned order
  const [serviceDate, setServiceDate] = useState('2026-08-20');
  const [statutoryWindowDays, setStatutoryWindowDays] = useState(90); // 90 days under Sec 205
  const [syncedCalendar, setSyncedCalendar] = useState(false);

  // Dynamic limitation calculation based on service date
  const calculateLimitation = () => {
    const sDate = new Date(serviceDate);
    if (isNaN(sDate.getTime())) {
      return {
        daysRemaining: 12,
        daysElapsed: 78,
        deadlineStr: '18 November 2026',
        isExpired: false,
      };
    }

    // Add statutory window
    const deadline = new Date(sDate);
    deadline.setDate(deadline.getDate() + statutoryWindowDays);

    const today = new Date('2026-11-04'); // App timeline base date
    const diffTime = deadline - today;
    const daysRemaining = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    const elapsed = statutoryWindowDays - daysRemaining;

    const deadlineStr = deadline.toLocaleDateString('en-GB', {
      day: 'numeric',
      month: 'long',
      year: 'numeric',
    });

    return {
      daysRemaining,
      daysElapsed: elapsed > 0 ? elapsed : 0,
      deadlineStr,
      isExpired: daysRemaining < 0,
    };
  };

  const { daysRemaining, daysElapsed, deadlineStr, isExpired } = calculateLimitation();

  const handleSyncCalendar = () => {
    setSyncedCalendar(true);
    onLogAction(`${currentRole.shortLabel} synced Matter #809 hearing to Chamber Docket Calendar.`);
    onShowToast('Hearing date (18-Nov-2026) synchronized to Google / Outlook Chamber Docket.');
    setTimeout(() => setSyncedCalendar(false), 3000);
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Top Banner: Big Countdown Widget & Statutory Status */}
      <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
        {/* Big Countdown Card (5 cols) */}
        <div className={`md:col-span-5 p-6 rounded-2xl border flex flex-col justify-between shadow-xl transition-all ${
          isExpired
            ? 'bg-rose-950/20 border-rose-500/40 text-rose-300'
            : daysRemaining <= 15
              ? 'bg-amber-950/20 border-amber-500/40 text-amber-300'
              : 'bg-graphite border-hairline text-light-gray'
        }`}>
          <div>
            <div className="flex items-center justify-between font-mono text-[11px] mb-2">
              <span className="uppercase text-titanium">STATUTORY LIMITATION COUNTDOWN</span>
              <span className="px-2 py-0.5 rounded bg-slate-glass border border-hairline text-champagne">
                SEC. 205 BLRC
              </span>
            </div>

            <div className="flex items-baseline gap-2 my-2">
              <span className="text-5xl font-light font-mono tracking-tight text-light-gray">
                {isExpired ? Math.abs(daysRemaining) : daysRemaining}
              </span>
              <span className="text-sm font-medium text-titanium">
                {isExpired ? 'Days OVERDUE' : 'Days Remaining'}
              </span>
            </div>

            <p className="text-xs text-muted-gray leading-relaxed mt-2">
              {isExpired ? (
                <span className="text-rose-400 font-medium">
                  Limitation period expired. Mandatory Section 5 Condonation of Delay application required.
                </span>
              ) : (
                <span>
                  Appeal window strictly ends on <strong className="text-light-gray font-normal">{deadlineStr}</strong>.
                </span>
              )}
            </p>
          </div>

          <div className="pt-4 border-t border-hairline/60 flex items-center justify-between text-[11px] font-mono text-titanium mt-4">
            <span>Elapsed: {daysElapsed} Days</span>
            <span>Window: {statutoryWindowDays} Days</span>
          </div>
        </div>

        {/* Interactive Limitation Calculator (7 cols) */}
        <div className="md:col-span-7 bg-graphite border border-hairline rounded-2xl p-6 shadow-xl space-y-4">
          <div className="flex items-center justify-between border-b border-hairline pb-3">
            <div className="flex items-center gap-2">
              <Scale className="w-4 h-4 text-champagne" />
              <h3 className="text-xs font-semibold text-light-gray uppercase tracking-wider">
                Limitation Calculator & Section 5 Delay Audit
              </h3>
            </div>
            <span className="text-[10px] font-mono text-titanium bg-slate-glass px-2 py-0.5 rounded border border-hairline">
              BOMBAY LRC 1879
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {/* Service Date Picker */}
            <div>
              <label className="block text-[11px] font-mono text-titanium uppercase mb-1.5">
                Date of Service of Impugned Order
              </label>
              <input
                type="date"
                value={serviceDate}
                onChange={(e) => {
                  setServiceDate(e.target.value);
                  onShowToast('Recalculating limitation timeline...');
                }}
                className="w-full px-3 py-2 bg-obsidian border border-hairline rounded-xl text-xs font-mono text-light-gray focus:outline-none focus:border-champagne"
              />
            </div>

            {/* Statutory Window Selector */}
            <div>
              <label className="block text-[11px] font-mono text-titanium uppercase mb-1.5">
                Statutory Appeal Window
              </label>
              <select
                value={statutoryWindowDays}
                onChange={(e) => setStatutoryWindowDays(Number(e.target.value))}
                className="w-full px-3 py-2 bg-obsidian border border-hairline rounded-xl text-xs font-mono text-light-gray focus:outline-none focus:border-champagne"
              >
                <option value={90}>90 Days (Sec. 205 Appeal before Prant / Collector)</option>
                <option value={60}>60 Days (Sec. 211 Revision before SSRD)</option>
                <option value={30}>30 Days (Interlocutory Stay Petition)</option>
              </select>
            </div>
          </div>

          {/* Calculator Output Diagnosis Box */}
          <div className="p-3.5 bg-obsidian/70 border border-hairline rounded-xl text-xs space-y-1.5">
            <div className="flex items-center justify-between">
              <span className="font-mono text-titanium uppercase text-[10px]">DIAGNOSIS & FILING DEADLINE:</span>
              <span className="font-mono text-champagne text-[11px]">{deadlineStr}</span>
            </div>
            <div className="text-light-gray font-medium flex items-center gap-2">
              {isExpired ? (
                <>
                  <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0" />
                  <span className="text-rose-400">Section 5 Condonation of Delay Application REQUIRED</span>
                </>
              ) : (
                <>
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                  <span className="text-emerald-400">Within Statutory Limitation (Direct Appeal Maintainable)</span>
                </>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Cause List & Next Hearing Tracker */}
      <div className="bg-graphite border border-hairline rounded-2xl p-6 shadow-xl space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-hairline pb-4">
          <div>
            <div className="flex items-center gap-2">
              <Calendar className="w-4 h-4 text-champagne" />
              <h3 className="text-xs font-semibold text-light-gray uppercase tracking-wider">
                Court Cause List Hearing Tracker
              </h3>
            </div>
            <p className="text-[11px] text-muted-gray mt-0.5">
              Automated listing sync with Gujarat Revenue Department Cause List Portal.
            </p>
          </div>

          <button
            onClick={handleSyncCalendar}
            className={`inline-flex items-center gap-2 px-3.5 py-1.5 rounded-xl border text-xs font-medium transition-all ${
              syncedCalendar
                ? 'bg-emerald-500/20 border-emerald-500/50 text-emerald-400'
                : 'bg-champagne hover:bg-[#968a6f] text-obsidian shadow-sm active:scale-[0.98]'
            }`}
          >
            <CalendarCheck className="w-3.5 h-3.5" />
            <span>{syncedCalendar ? 'Calendar Synced!' : 'Sync to Chamber Calendar'}</span>
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 bg-obsidian/60 border border-hairline rounded-xl space-y-1">
            <span className="text-[10px] font-mono text-titanium uppercase">NEXT HEARING DATE & TIME</span>
            <div className="text-sm font-semibold text-light-gray">
              18 November 2026 at 11:30 AM
            </div>
            <div className="text-[11px] text-champagne font-mono">
              BOARD ITEM NO: #14 (URGENT)
            </div>
          </div>

          <div className="p-4 bg-obsidian/60 border border-hairline rounded-xl space-y-1">
            <span className="text-[10px] font-mono text-titanium uppercase">REVENUE COURT FORUM</span>
            <div className="text-xs font-medium text-light-gray">
              Court of the Deputy Collector (Prant Officer)
            </div>
            <div className="text-[11px] text-muted-gray">
              Dholka-Bavla Sub-Division, Ahmedabad
            </div>
          </div>

          <div className="p-4 bg-obsidian/60 border border-hairline rounded-xl space-y-1">
            <span className="text-[10px] font-mono text-titanium uppercase">PROCEEDING STAGE</span>
            <div className="text-xs font-medium text-light-gray">
              Preliminary Hearing on Ad-Interim Stay
            </div>
            <div className="text-[11px] text-titanium font-mono">
              Lead Counsel: Rajesh Mehta, Adv.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
