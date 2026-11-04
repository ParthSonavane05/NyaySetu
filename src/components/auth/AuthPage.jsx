import React, { useState } from 'react';
import {
  Building2,
  Lock,
  ArrowRight,
  ShieldCheck,
  KeyRound
} from 'lucide-react';
import { FIRM_ROLES } from '../../constants/roles';

export default function AuthPage({
  initialRoleId = 'partner',
  onBackToLanding,
  onLoginSuccess,
}) {
  const [selectedRoleId, setSelectedRoleId] = useState(initialRoleId);
  const selectedRole = FIRM_ROLES.find((r) => r.id === selectedRoleId) || FIRM_ROLES[0];

  const [email, setEmail] = useState('advocate@mehtachambers.in');
  const [password, setPassword] = useState('••••••••');
  const [securityPin, setSecurityPin] = useState('842091');
  const [isAuthenticating, setIsAuthenticating] = useState(false);

  const handleRoleChange = (roleId) => {
    setSelectedRoleId(roleId);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setIsAuthenticating(true);
    setTimeout(() => {
      setIsAuthenticating(false);
      if (onLoginSuccess) {
        onLoginSuccess({
          role: selectedRole,
          email,
          firmName: 'Mehta & Associates Law Chambers',
        });
      }
    }, 600);
  };

  return (
    <div className="min-h-screen bg-obsidian text-light-gray flex flex-col justify-between selection:bg-champagne/30 selection:text-light-gray font-sans">
      {/* Top Header */}
      <header className="border-b border-hairline bg-obsidian/85 backdrop-blur-xl px-4 sm:px-8 py-4">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <button
            onClick={onBackToLanding}
            className="inline-flex items-center gap-1.5 text-xs text-titanium hover:text-light-gray transition-colors group"
          >
            <span className="group-hover:-translate-x-0.5 transition-transform">←</span>
            <span>Return to Landing Page</span>
          </button>

          <div className="flex items-center gap-2.5">
            <span className="text-light-gray font-semibold text-xs tracking-[0.24em]">
              NYAYSETU
            </span>
            <span className="px-2 py-0.5 rounded-full text-[9px] font-mono tracking-widest uppercase bg-graphite border border-hairline text-titanium">
              ENTERPRISE GATEWAY
            </span>
          </div>
        </div>
      </header>

      {/* Main Authentication Section */}
      <main className="flex-1 flex items-center justify-center p-4 sm:p-6 my-6">
        <div className="w-full max-w-xl bg-graphite border border-hairline rounded-2xl p-6 sm:p-8 shadow-2xl relative overflow-hidden">
          {/* Subtle Accent Glow */}
          <div className="absolute -top-28 -left-28 w-72 h-72 bg-champagne/10 rounded-full blur-3xl pointer-events-none" />

          {/* Gateway Header */}
          <div className="text-center mb-7 relative z-10">
            <div className="inline-flex items-center justify-center w-12 h-12 rounded-2xl bg-slate-glass border border-hairline mb-3">
              <Building2 className="w-6 h-6 text-champagne" />
            </div>
            <h1 className="text-xl sm:text-2xl font-light text-light-gray tracking-tight mb-1.5">
              NYAYSETU Chamber Gateway
            </h1>
            <p className="text-xs text-muted-gray leading-relaxed max-w-md mx-auto">
              Sign in with firm credentials and matter authorization.
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5 relative z-10">
            {/* Interactive 4-Role Switcher Tabs (Horizontal Pills) */}
            <div>
              <label className="block text-[11px] font-mono text-titanium uppercase tracking-wider mb-2">
                Select Law Firm Role
              </label>
              <div className="grid grid-cols-2 gap-2">
                {FIRM_ROLES.map((role) => {
                  const isSelected = role.id === selectedRoleId;
                  const Icon = role.icon;
                  return (
                    <button
                      key={role.id}
                      type="button"
                      onClick={() => handleRoleChange(role.id)}
                      className={`text-left p-2.5 rounded-xl border text-xs transition-all flex items-start gap-2.5 ${
                        isSelected
                          ? 'bg-slate-glass border-champagne text-light-gray shadow-[0_0_15px_rgba(130,119,96,0.15)] ring-1 ring-champagne/40'
                          : 'bg-obsidian/40 border-hairline text-muted-gray hover:text-light-gray hover:border-hairline/80'
                      }`}
                    >
                      <Icon className={`w-4 h-4 mt-0.5 shrink-0 ${isSelected ? 'text-champagne' : 'text-titanium'}`} />
                      <div className="min-w-0">
                        <div className={`font-medium truncate ${isSelected ? 'text-light-gray' : 'text-muted-gray'}`}>
                          {role.label}
                        </div>
                        <div className="text-[10px] text-titanium/80 truncate">
                          {role.desc}
                        </div>
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Selected Role Permissions Matrix Preview Card */}
            <div className="p-3.5 bg-obsidian/70 border border-hairline rounded-xl text-xs space-y-1.5 animate-fade-in">
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-mono text-champagne tracking-wider">
                  ROLE PERMISSIONS MATRIX: {selectedRole.label.toUpperCase()}
                </span>
                <span className="text-[9px] font-mono text-titanium bg-slate-glass px-2 py-0.5 rounded border border-hairline">
                  {selectedRole.badge}
                </span>
              </div>
              <p className="text-[11px] text-muted-gray leading-relaxed">
                {selectedRole.permissions}
              </p>
            </div>

            {/* Input Fields */}
            <div className="space-y-3.5">
              <div>
                <label className="block text-[11px] font-mono text-titanium uppercase tracking-wider mb-1.5">
                  Firm Work Email
                </label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="advocate@mehtachambers.in"
                  className="w-full px-3.5 py-2.5 rounded-xl bg-obsidian/70 border border-hairline text-light-gray text-xs focus:outline-none focus:border-champagne/70 font-mono transition-colors"
                  required
                />
              </div>

              <div>
                <label className="block text-[11px] font-mono text-titanium uppercase tracking-wider mb-1.5">
                  Matter Access Key
                </label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full px-3.5 py-2.5 rounded-xl bg-obsidian/70 border border-hairline text-light-gray text-xs focus:outline-none focus:border-champagne/70 font-mono transition-colors"
                  required
                />
              </div>

              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <label className="text-[11px] font-mono text-titanium uppercase tracking-wider">
                    2FA Security Token / PIN
                  </label>
                  <span className="text-[10px] font-mono text-champagne">OPTIONAL PIN</span>
                </div>
                <div className="relative">
                  <KeyRound className="w-3.5 h-3.5 text-titanium absolute left-3.5 top-3" />
                  <input
                    type="text"
                    value={securityPin}
                    onChange={(e) => setSecurityPin(e.target.value)}
                    placeholder="842091"
                    className="w-full pl-9 pr-3.5 py-2.5 rounded-xl bg-obsidian/70 border border-hairline text-light-gray text-xs focus:outline-none focus:border-champagne/70 font-mono transition-colors"
                  />
                </div>
              </div>
            </div>

            {/* Action Button */}
            <button
              type="submit"
              disabled={isAuthenticating}
              className="w-full py-3 rounded-xl bg-champagne hover:bg-[#968a6f] text-obsidian text-xs font-medium tracking-wide flex items-center justify-center gap-2 transition-all shadow-[0_0_20px_rgba(130,119,96,0.2)] active:scale-[0.99] disabled:opacity-70"
            >
              <span>{isAuthenticating ? 'Connecting Chamber...' : 'Enter Firm Workspace'}</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </form>

          {/* Footer Security Badge */}
          <div className="mt-6 pt-4 border-t border-hairline/60 flex items-center justify-between text-[10px] text-muted-gray">
            <span className="flex items-center gap-1.5">
              <Lock className="w-3 h-3 text-champagne" />
              Isolated Law Firm Tenant · DPDP Act 2023 Audited
            </span>
            <span className="font-mono text-titanium flex items-center gap-1">
              <ShieldCheck className="w-3 h-3 text-champagne" />
              AES-256
            </span>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-hairline py-4 px-4 text-center text-xs text-muted-gray">
        NYAYSETU Enterprise — Built exclusively for Indian law firms and legal chambers.
      </footer>
    </div>
  );
}
