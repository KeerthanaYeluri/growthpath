import { useState } from "react";
import { apiFetch } from "@/lib/api";

interface ChangePasswordScreenProps {
  onComplete: () => void;
}

function getPasswordStrength(pw: string): { label: string; color: string; width: string; score: number } {
  let score = 0;
  if (pw.length >= 6) score++;
  if (pw.length >= 8) score++;
  if (/[A-Z]/.test(pw)) score++;
  if (/[0-9]/.test(pw)) score++;
  if (/[^A-Za-z0-9]/.test(pw)) score++;

  if (score <= 1) return { label: "Weak", color: "bg-red-500", width: "w-1/5", score };
  if (score <= 2) return { label: "Fair", color: "bg-amber-500", width: "w-2/5", score };
  if (score <= 3) return { label: "Good", color: "bg-yellow-500", width: "w-3/5", score };
  if (score <= 4) return { label: "Strong", color: "bg-emerald-500", width: "w-4/5", score };
  return { label: "Very Strong", color: "bg-emerald-400", width: "w-full", score };
}

export default function ChangePasswordScreen({ onComplete }: ChangePasswordScreenProps) {
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const strength = getPasswordStrength(password);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (password !== confirm) {
      setError("Passwords don't match");
      return;
    }
    if (password.length < 6) {
      setError("Password must be at least 6 characters");
      return;
    }
    setError("");
    setLoading(true);
    try {
      const res = await apiFetch("/auth/password", {
        method: "PUT",
        body: JSON.stringify({ new_password: password }),
      });
      const data = await res.json();
      if (!res.ok) {
        setError(data.error || "Failed");
        setLoading(false);
        return;
      }
      onComplete();
    } catch {
      setError("Connection error");
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 animate-fade-in">
      <div className="glass-strong rounded-2xl p-10 max-w-md w-full glow">
        <div className="text-center mb-6">
          <div className="w-14 h-14 rounded-2xl bg-amber-500/20 mx-auto mb-4 flex items-center justify-center">
            <svg className="w-7 h-7 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
              />
            </svg>
          </div>
          <h2 className="text-2xl font-bold mb-1">Change Password</h2>
          <p className="text-slate-400 text-sm">Please set a new password to continue</p>
        </div>
        {error && (
          <div className="bg-red-500/10 border border-red-500/20 text-red-400 px-4 py-2 rounded-xl text-sm mb-4">
            {error}
          </div>
        )}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-slate-400 text-xs font-medium mb-1.5 uppercase tracking-wider">
              New Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="At least 6 characters"
              required
              autoComplete="new-password"
              className="w-full bg-slate-800/60 border border-slate-700/50 rounded-xl px-4 py-3 text-white placeholder-slate-600 focus:border-indigo-500/50 transition-all"
            />
            {password && (
              <div className="mt-2">
                <div className="w-full bg-slate-700/50 rounded-full h-1.5 overflow-hidden">
                  <div className={`h-1.5 rounded-full ${strength.color} ${strength.width} transition-all duration-300`} />
                </div>
                <p className={`text-[10px] mt-1 ${strength.score <= 2 ? "text-amber-400" : "text-emerald-400"}`}>
                  {strength.label} {strength.score <= 2 && "— add uppercase, numbers, or symbols"}
                </p>
              </div>
            )}
          </div>
          <div>
            <label className="block text-slate-400 text-xs font-medium mb-1.5 uppercase tracking-wider">
              Confirm Password
            </label>
            <input
              type="password"
              value={confirm}
              onChange={(e) => setConfirm(e.target.value)}
              placeholder="Repeat password"
              required
              className="w-full bg-slate-800/60 border border-slate-700/50 rounded-xl px-4 py-3 text-white placeholder-slate-600 focus:border-indigo-500/50 transition-all"
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="w-full py-3.5 rounded-xl font-semibold text-sm bg-indigo-600 hover:bg-indigo-500 text-white transition-all disabled:opacity-50"
          >
            {loading ? "Saving..." : "Set Password & Continue"}
          </button>
        </form>
      </div>
    </div>
  );
}
