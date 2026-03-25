import { useState, useEffect } from "react";
import { API } from "@/lib/api";

interface RegisterScreenProps {
  onRegister: (data: any) => void;
  onSwitchToLogin: () => void;
}

export default function RegisterScreen({ onRegister, onSwitchToLogin }: RegisterScreenProps) {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [techStack, setTechStack] = useState<string[]>([]);
  const [interests, setInterests] = useState<string[]>([]);
  const [hours, setHours] = useState(2);
  const [targetCompany, setTargetCompany] = useState("");
  const [targetRole, setTargetRole] = useState("");
  const [targetLevel, setTargetLevel] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState<any>(null);
  const [techOptions, setTechOptions] = useState<string[]>([]);
  const [interestOptions, setInterestOptions] = useState<string[]>([]);
  const [companyOptions, setCompanyOptions] = useState<any>({ companies: [], profiles: {} });
  const [roleOptions, setRoleOptions] = useState<any>({ roles: [], labels: {} });
  const [levelOptions, setLevelOptions] = useState<any>({ levels: [], labels: {} });

  useEffect(() => {
    fetch(`${API}/config/tech-stacks`).then((r) => r.json()).then(setTechOptions).catch(() => {});
    fetch(`${API}/config/interest-areas`).then((r) => r.json()).then(setInterestOptions).catch(() => {});
    fetch(`${API}/config/companies`).then((r) => r.json()).then(setCompanyOptions).catch(() => {});
    fetch(`${API}/config/roles`).then((r) => r.json()).then(setRoleOptions).catch(() => {});
    fetch(`${API}/config/levels`).then((r) => r.json()).then(setLevelOptions).catch(() => {});
  }, []);

  const toggleTag = (list: string[], setList: (v: string[]) => void, item: string) => {
    setList(list.includes(item) ? list.filter((i) => i !== item) : [...list, item]);
  };

  const selectClass =
    "w-full bg-slate-800/60 border border-slate-700/50 rounded-xl px-4 py-2.5 text-white text-sm focus:border-indigo-500/50 transition-all appearance-none cursor-pointer";
  const selectActiveClass = (val: string) => (val ? "border-indigo-500/40" : "");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!targetCompany || !targetRole || !targetLevel) {
      setError("Select target company, role, and level");
      return;
    }
    if (interests.length === 0) {
      setError("Select at least one interest area");
      return;
    }
    setError("");
    setLoading(true);
    try {
      const res = await fetch(`${API}/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          full_name: name,
          email,
          tech_stack: techStack,
          interest_areas: interests,
          hours_per_day: hours,
          target_company: targetCompany,
          target_role: targetRole,
          target_level: targetLevel,
        }),
      });
      const data = await res.json();
      if (!res.ok) {
        setError(data.error || "Registration failed");
        setLoading(false);
        return;
      }
      setSuccess(data);
    } catch {
      setError("Cannot connect to server");
    }
    setLoading(false);
  };

  if (success) {
    const elo = success.elo;
    return (
      <div className="min-h-screen flex items-center justify-center p-4 animate-fade-in">
        <div className="glass-strong rounded-2xl p-10 max-w-md w-full glow-green text-center">
          <div className="w-16 h-16 rounded-full bg-emerald-500/20 mx-auto mb-4 flex items-center justify-center">
            <svg className="w-8 h-8 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h2 className="text-2xl font-bold mb-2">Registration Successful!</h2>
          {elo && (
            <div className="bg-slate-800/60 rounded-xl p-4 mb-4 text-left">
              <div className="flex items-center justify-between mb-2">
                <span className="text-slate-400 text-xs uppercase">Starting ELO</span>
                <span className="text-2xl font-bold text-indigo-400">{elo.current_elo}</span>
              </div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-slate-400 text-xs uppercase">
                  {success.target_company} {success.target_level} Bar
                </span>
                <span className="text-sm font-medium text-slate-300">{elo.hiring_bar}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-slate-400 text-xs uppercase">Gap to close</span>
                <span className="text-sm font-medium text-amber-400">{elo.gap} points</span>
              </div>
              <div className="w-full bg-slate-700/50 rounded-full h-2 mt-3">
                <div
                  className="h-2 rounded-full bg-indigo-500 transition-all"
                  style={{ width: `${Math.min(100, (elo.current_elo / elo.hiring_bar) * 100)}%` }}
                ></div>
              </div>
              <p className="text-xs mt-2 text-center">
                <span
                  className={`px-2 py-0.5 rounded-full ${elo.is_ready ? "bg-emerald-500/20 text-emerald-300" : "bg-amber-500/20 text-amber-300"}`}
                >
                  {elo.readiness.label}
                </span>
              </p>
            </div>
          )}
          <p className="text-slate-400 text-sm mb-2">Your default password is:</p>
          <div className="bg-slate-800/60 rounded-xl px-6 py-3 mb-4 inline-block">
            <code className="text-indigo-400 text-lg font-bold">{success.password}</code>
          </div>
          <p className="text-slate-500 text-xs mb-6">You'll be asked to change this on first login.</p>
          <button
            onClick={() => onRegister(success)}
            className="w-full py-3 rounded-xl font-semibold text-sm bg-indigo-600 hover:bg-indigo-500 text-white transition-all"
          >
            Continue to Login
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4 animate-fade-in">
      <div className="glass-strong rounded-2xl p-8 max-w-lg w-full glow">
        <div className="text-center mb-6">
          <h1 className="text-2xl font-bold mb-1">Create Account</h1>
          <p className="text-slate-400 text-sm">Target a FAANG company. Prep like the real interview.</p>
        </div>
        {error && (
          <div className="bg-red-500/10 border border-red-500/20 text-red-400 px-4 py-2 rounded-xl text-sm mb-4">
            {error}
          </div>
        )}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-slate-400 text-xs font-medium mb-1.5 uppercase tracking-wider">
                Full Name
              </label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Your name"
                required
                className="w-full bg-slate-800/60 border border-slate-700/50 rounded-xl px-4 py-2.5 text-white text-sm placeholder-slate-600 focus:border-indigo-500/50 transition-all"
              />
            </div>
            <div>
              <label className="block text-slate-400 text-xs font-medium mb-1.5 uppercase tracking-wider">Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="your@email.com"
                required
                className="w-full bg-slate-800/60 border border-slate-700/50 rounded-xl px-4 py-2.5 text-white text-sm placeholder-slate-600 focus:border-indigo-500/50 transition-all"
              />
            </div>
          </div>
          {/* v2: Target Company / Role / Level */}
          <div className="glass rounded-xl p-4">
            <label className="block text-indigo-300 text-xs font-semibold mb-3 uppercase tracking-wider">
              Interview Target
            </label>
            <div className="grid grid-cols-3 gap-2">
              <div>
                <label className="block text-slate-500 text-[10px] mb-1 uppercase">Company</label>
                <select
                  value={targetCompany}
                  onChange={(e) => setTargetCompany(e.target.value)}
                  className={`${selectClass} ${selectActiveClass(targetCompany)}`}
                  required
                >
                  <option value="">Select...</option>
                  {(companyOptions.companies || []).map((c: string) => (
                    <option key={c} value={c}>
                      {(companyOptions.profiles || {})[c]?.name || c}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-slate-500 text-[10px] mb-1 uppercase">Role</label>
                <select
                  value={targetRole}
                  onChange={(e) => setTargetRole(e.target.value)}
                  className={`${selectClass} ${selectActiveClass(targetRole)}`}
                  required
                >
                  <option value="">Select...</option>
                  {(roleOptions.roles || []).map((r: string) => (
                    <option key={r} value={r}>
                      {(roleOptions.labels || {})[r] || r}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-slate-500 text-[10px] mb-1 uppercase">Level</label>
                <select
                  value={targetLevel}
                  onChange={(e) => setTargetLevel(e.target.value)}
                  className={`${selectClass} ${selectActiveClass(targetLevel)}`}
                  required
                >
                  <option value="">Select...</option>
                  {(levelOptions.levels || []).map((l: string) => (
                    <option key={l} value={l}>
                      {(levelOptions.labels || {})[l] || l}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            {targetCompany && (
              <p className="text-slate-500 text-[10px] mt-2">
                {(companyOptions.profiles || {})[targetCompany]?.description || ""}
              </p>
            )}
          </div>
          <div>
            <label className="block text-slate-400 text-xs font-medium mb-2 uppercase tracking-wider">
              Tech Stack (select your skills)
            </label>
            <div className="flex flex-wrap gap-1.5 max-h-24 overflow-y-auto p-1">
              {techOptions.map((t) => (
                <button
                  type="button"
                  key={t}
                  onClick={() => toggleTag(techStack, setTechStack, t)}
                  className={`tag-pill ${
                    techStack.includes(t)
                      ? "bg-indigo-600/30 border border-indigo-500/40 text-indigo-300"
                      : "bg-slate-800/60 border border-slate-700/40 text-slate-500 hover:text-slate-300"
                  }`}
                >
                  {t}
                </button>
              ))}
            </div>
          </div>
          <div>
            <label className="block text-slate-400 text-xs font-medium mb-2 uppercase tracking-wider">
              Interest Areas (what to learn)
            </label>
            <div className="flex flex-wrap gap-1.5 max-h-24 overflow-y-auto p-1">
              {interestOptions.map((t) => (
                <button
                  type="button"
                  key={t}
                  onClick={() => toggleTag(interests, setInterests, t)}
                  className={`tag-pill ${
                    interests.includes(t)
                      ? "bg-emerald-600/30 border border-emerald-500/40 text-emerald-300"
                      : "bg-slate-800/60 border border-slate-700/40 text-slate-500 hover:text-slate-300"
                  }`}
                >
                  {t}
                </button>
              ))}
            </div>
          </div>
          <div>
            <label className="block text-slate-400 text-xs font-medium mb-2 uppercase tracking-wider">
              Hours per day: {hours}h
            </label>
            <input
              type="range"
              min="0.5"
              max="8"
              step="0.5"
              value={hours}
              onChange={(e) => setHours(parseFloat(e.target.value))}
              className="w-full accent-indigo-500"
            />
            <div className="flex justify-between text-slate-600 text-[10px]">
              <span>0.5h</span>
              <span>4h</span>
              <span>8h</span>
            </div>
          </div>
          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 rounded-xl font-semibold text-sm bg-indigo-600 hover:bg-indigo-500 text-white shadow-lg shadow-indigo-500/20 transition-all disabled:opacity-50"
          >
            {loading ? "Creating account..." : "Create Account"}
          </button>
        </form>
        <p className="text-center text-slate-500 text-sm mt-4">
          Already have an account?{" "}
          <button onClick={onSwitchToLogin} className="text-indigo-400 hover:text-indigo-300 font-medium">
            Sign In
          </button>
        </p>
      </div>
    </div>
  );
}
