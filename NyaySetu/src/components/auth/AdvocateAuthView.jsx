import React, { useState } from 'react';
import { Scale, Lock, ArrowLeft, ArrowRight, CheckCircle2, KeyRound, Fingerprint } from 'lucide-react';

export default function AdvocateAuthView({ onBackToLanding, onLoginSuccess }) {
  const [enrollmentNo, setEnrollmentNo] = useState('GJ/1842/2016');
  const [selectedState, setSelectedState] = useState('Gujarat');
  const [authMethod, setAuthMethod] = useState('otp'); // 'otp' | 'token'
  const [otpSent, setOtpSent] = useState(false);
  const [authenticated, setAuthenticated] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!otpSent && authMethod === 'otp') {
      setOtpSent(true);
    } else {
      setAuthenticated(true);
      if (onLoginSuccess) {
        setTimeout(() => onLoginSuccess(), 1200);
      }
    }
  };

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
              ADVOCATE ACCESS
            </span>
          </div>
        </div>
      </header>

      {/* Main Authentication Card */}
      <main className="flex-1 flex items-center justify-center p-4 sm:p-6">
        <div className="w-full max-w-md bg-graphite border border-hairline rounded-2xl p-6 sm:p-8 shadow-2xl relative overflow-hidden">
          {/* Subtle Accent Glow */}
          <div className="absolute -top-24 -left-24 w-64 h-64 bg-champagne/10 rounded-full blur-3xl pointer-events-none" />

          {/* Card Header */}
          <div className="text-center mb-6 relative z-10">
            <div className="inline-flex items-center justify-center w-12 h-12 rounded-2xl bg-slate-glass border border-hairline mb-4">
              <Scale className="w-6 h-6 text-champagne" />
            </div>
            <h1 className="text-xl sm:text-2xl font-light text-light-gray tracking-tight mb-2">
              Chamber Authentication
            </h1>
            <p className="text-xs text-muted-gray leading-relaxed">
              Verify your State Bar Council credentials to access air-gapped revenue litigation files.
            </p>
          </div>

          {authenticated ? (
            <div className="text-center py-8 space-y-4">
              <div className="w-12 h-12 rounded-full bg-champagne/20 border border-champagne text-champagne mx-auto flex items-center justify-center animate-bounce">
                <CheckCircle2 className="w-6 h-6" />
              </div>
              <div>
                <h3 className="text-sm font-medium text-light-gray">
                  Credentials Verified
                </h3>
                <p className="text-xs text-muted-gray mt-1">
                  Connecting to Bar Council of Gujarat encrypted session...
                </p>
              </div>
              <div className="pt-4">
                <button
                  onClick={onBackToLanding}
                  className="px-5 py-2 text-xs rounded-lg border border-hairline text-titanium hover:text-light-gray"
                >
                  Return to Overview
                </button>
              </div>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-4 relative z-10">
              {/* State Bar Selection */}
              <div>
                <label className="block text-[11px] font-mono text-titanium uppercase tracking-wider mb-1.5">
                  State Bar Council
                </label>
                <select
                  value={selectedState}
                  onChange={(e) => setSelectedState(e.target.value)}
                  className="w-full px-3 py-2.5 rounded-xl bg-obsidian/70 border border-hairline text-light-gray text-xs focus:outline-none focus:border-champagne/70 transition-colors"
                >
                  <option value="Gujarat">Bar Council of Gujarat</option>
                  <option value="Maharashtra">Bar Council of Maharashtra & Goa</option>
                  <option value="Rajasthan">Bar Council of Rajasthan</option>
                  <option value="Delhi">Bar Council of Delhi</option>
                </select>
              </div>

              {/* Enrollment Number */}
              <div>
                <label className="block text-[11px] font-mono text-titanium uppercase tracking-wider mb-1.5">
                  Bar Enrollment Number
                </label>
                <input
                  type="text"
                  value={enrollmentNo}
                  onChange={(e) => setEnrollmentNo(e.target.value)}
                  placeholder="e.g. GJ/1842/2016"
                  className="w-full px-3 py-2.5 rounded-xl bg-obsidian/70 border border-hairline text-light-gray text-xs focus:outline-none focus:border-champagne/70 font-mono transition-colors"
                  required
                />
              </div>

              {/* Authentication Mode Tabs */}
              <div className="pt-1">
                <div className="grid grid-cols-2 gap-2 p-1 bg-obsidian/50 border border-hairline rounded-xl text-xs">
                  <button
                    type="button"
                    onClick={() => setAuthMethod('otp')}
                    className={`py-1.5 rounded-lg flex items-center justify-center gap-1.5 transition-all ${
                      authMethod === 'otp'
                        ? 'bg-graphite text-light-gray border border-hairline shadow-sm'
                        : 'text-muted-gray hover:text-light-gray'
                    }`}
                  >
                    <KeyRound className="w-3.5 h-3.5 text-champagne" />
                    <span>Registered OTP</span>
                  </button>
                  <button
                    type="button"
                    onClick={() => setAuthMethod('token')}
                    className={`py-1.5 rounded-lg flex items-center justify-center gap-1.5 transition-all ${
                      authMethod === 'token'
                        ? 'bg-graphite text-light-gray border border-hairline shadow-sm'
                        : 'text-muted-gray hover:text-light-gray'
                    }`}
                  >
                    <Fingerprint className="w-3.5 h-3.5 text-champagne" />
                    <span>e-Sign / Token</span>
                  </button>
                </div>
              </div>

              {otpSent && authMethod === 'otp' && (
                <div className="p-3 bg-slate-glass border border-hairline rounded-xl space-y-2 animate-fade-in">
                  <div className="flex items-center justify-between text-[11px]">
                    <span className="text-muted-gray">One-Time Code sent to registered mobile</span>
                    <span className="font-mono text-champagne">•••• 7412</span>
                  </div>
                  <input
                    type="text"
                    defaultValue="842091"
                    placeholder="Enter 6-digit OTP"
                    className="w-full px-3 py-2 bg-obsidian border border-hairline rounded-lg text-center font-mono text-sm tracking-widest text-light-gray focus:outline-none focus:border-champagne"
                  />
                </div>
              )}

              {/* Submit CTA */}
              <button
                type="submit"
                className="w-full py-3 rounded-xl bg-champagne hover:bg-[#968a6f] text-obsidian text-xs font-medium tracking-wide flex items-center justify-center gap-2 transition-all shadow-[0_0_20px_rgba(130,119,96,0.2)] mt-2"
              >
                <span>{otpSent ? 'Authenticate & Open Workspace' : 'Verify Bar Credentials'}</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>

              {/* Demo Fast-Track Button */}
              <button
                type="button"
                onClick={() => setAuthenticated(true)}
                className="w-full py-2 rounded-xl bg-graphite/60 hover:bg-graphite text-titanium hover:text-light-gray border border-hairline text-[11px] transition-colors"
              >
                Simulate Verified Advocate Login
              </button>
            </form>
          )}

          {/* Footer Security Badge */}
          <div className="mt-6 pt-4 border-t border-hairline/60 flex items-center justify-between text-[10px] text-muted-gray">
            <span className="flex items-center gap-1.5">
              <Lock className="w-3 h-3 text-champagne" />
              256-Bit Hardware Token Validated
            </span>
            <span className="font-mono text-titanium">DPDP 2023</span>
          </div>
        </div>
      </main>

      {/* Subtle Minimal Footer */}
      <footer className="border-t border-hairline py-4 px-4 text-center text-xs text-muted-gray">
        NYAYSETU Advocate Gateway · In accordance with Bar Council of India Guidelines.
      </footer>
    </div>
  );
}
