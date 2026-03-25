import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  User,
  Mail,
  Building2,
  Briefcase,
  GraduationCap,
  Target,
  Clock,
  Sparkles,
  CheckCircle2,
  AlertCircle,
} from "lucide-react";
import { GlassCard, GlassCardContent, GlassCardHeader, GlassCardTitle } from "@/components/ui/glass-card";
import { API } from "@/lib/api";

interface RegisterScreenProps {
  onRegister: (data: any) => void;
  onSwitchToLogin: () => void;
}

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.08 },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.4 } },
};

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
      <div className="min-h-screen flex items-center justify-center p-4 relative overflow-hidden">
        {/* Background blobs */}
        <div className="absolute top-[-20%] left-[-10%] w-[500px] h-[500px] bg-emerald-600/10 rounded-full blur-3xl animate-pulse" />
        <div className="absolute bottom-[-20%] right-[-10%] w-[500px] h-[500px] bg-indigo-600/10 rounded-full blur-3xl animate-pulse" />

        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ type: "spring", stiffness: 200, damping: 20 }}
          className="relative z-10 w-full max-w-md"
        >
          <GlassCard className="p-10 glow-green text-center">
            <GlassCardContent className="flex flex-col items-center">
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ type: "spring", stiffness: 300, damping: 15, delay: 0.2 }}
                className="w-16 h-16 rounded-full bg-emerald-500/20 mb-4 flex items-center justify-center"
              >
                <CheckCircle2 className="w-8 h-8 text-emerald-400" />
              </motion.div>
              <motion.h2
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                className="text-2xl font-bold mb-2 bg-gradient-to-r from-white to-slate-300 bg-clip-text text-transparent"
              >
                Registration Successful!
              </motion.h2>
              {elo && (
                <motion.div
                  initial={{ opacity: 0, y: 15 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.4 }}
                  className="bg-slate-800/60 rounded-xl p-4 mb-4 text-left w-full"
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-slate-400 text-xs uppercase">Starting ELO</span>
                    <motion.span
                      className="text-2xl font-bold text-indigo-400"
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ delay: 0.6 }}
                    >
                      {elo.current_elo}
                    </motion.span>
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
                  <div className="w-full bg-slate-700/50 rounded-full h-2 mt-3 overflow-hidden">
                    <motion.div
                      className="h-2 rounded-full bg-gradient-to-r from-indigo-500 to-purple-500"
                      initial={{ width: 0 }}
                      animate={{ width: `${Math.min(100, (elo.current_elo / elo.hiring_bar) * 100)}%` }}
                      transition={{ duration: 1, delay: 0.7, ease: "easeOut" }}
                    />
                  </div>
                  <p className="text-xs mt-2 text-center">
                    <span
                      className={`px-2 py-0.5 rounded-full ${elo.is_ready ? "bg-emerald-500/20 text-emerald-300" : "bg-amber-500/20 text-amber-300"}`}
                    >
                      {elo.readiness.label}
                    </span>
                  </p>
                </motion.div>
              )}
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.5 }}
                className="w-full"
              >
                <p className="text-slate-400 text-sm mb-2">Your default password is:</p>
                <div className="bg-slate-800/60 rounded-xl px-6 py-3 mb-4 inline-block">
                  <code className="text-indigo-400 text-lg font-bold">{success.password}</code>
                </div>
                <p className="text-slate-500 text-xs mb-6">You'll be asked to change this on first login.</p>
              </motion.div>
              <motion.button
                onClick={() => onRegister(success)}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className="w-full py-3 rounded-xl font-semibold text-sm bg-gradient-to-r from-indigo-600 to-indigo-500 hover:from-indigo-500 hover:to-indigo-400 text-white transition-all shadow-lg shadow-indigo-500/20"
              >
                Continue to Login
              </motion.button>
            </GlassCardContent>
          </GlassCard>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4 relative overflow-hidden">
      {/* Background blobs */}
      <div className="absolute top-[-20%] left-[-10%] w-[500px] h-[500px] bg-indigo-600/10 rounded-full blur-3xl animate-pulse" />
      <div className="absolute bottom-[-20%] right-[-10%] w-[400px] h-[400px] bg-purple-600/10 rounded-full blur-3xl animate-pulse" />
      <div className="absolute top-[50%] right-[-5%] w-[300px] h-[300px] bg-emerald-600/5 rounded-full blur-3xl animate-pulse" />

      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="relative z-10 w-full max-w-lg"
      >
        <GlassCard className="p-8 glow">
          <GlassCardContent>
            <motion.div
              variants={containerVariants}
              initial="hidden"
              animate="visible"
              className="space-y-4"
            >
              {/* Header */}
              <motion.div variants={itemVariants} className="text-center mb-6">
                <div className="flex items-center justify-center gap-2 mb-1">
                  <Sparkles className="w-5 h-5 text-indigo-400" />
                  <h1 className="text-2xl font-bold bg-gradient-to-r from-white to-slate-300 bg-clip-text text-transparent">
                    Create Account
                  </h1>
                </div>
                <p className="text-slate-400 text-sm">Target a FAANG company. Prep like the real interview.</p>
              </motion.div>

              {/* Error */}
              <AnimatePresence>
                {error && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: "auto" }}
                    exit={{ opacity: 0, height: 0 }}
                    className="bg-red-500/10 border border-red-500/20 text-red-400 px-4 py-2 rounded-xl text-sm flex items-center gap-2"
                  >
                    <AlertCircle className="w-4 h-4 shrink-0" />
                    {error}
                  </motion.div>
                )}
              </AnimatePresence>

              <form onSubmit={handleSubmit} className="space-y-4">
                {/* Name & Email */}
                <motion.div variants={itemVariants} className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="flex items-center gap-1.5 text-slate-400 text-xs font-medium mb-1.5 uppercase tracking-wider">
                      <User className="w-3 h-3" />
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
                    <label className="flex items-center gap-1.5 text-slate-400 text-xs font-medium mb-1.5 uppercase tracking-wider">
                      <Mail className="w-3 h-3" />
                      Email
                    </label>
                    <input
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="your@email.com"
                      required
                      className="w-full bg-slate-800/60 border border-slate-700/50 rounded-xl px-4 py-2.5 text-white text-sm placeholder-slate-600 focus:border-indigo-500/50 transition-all"
                    />
                  </div>
                </motion.div>

                {/* Interview Target - GlassCard */}
                <motion.div variants={itemVariants}>
                  <GlassCard className="p-4">
                    <GlassCardHeader className="px-0 py-0">
                      <GlassCardTitle>
                        <label className="flex items-center gap-1.5 text-indigo-300 text-xs font-semibold uppercase tracking-wider">
                          <Target className="w-3.5 h-3.5" />
                          Interview Target
                        </label>
                      </GlassCardTitle>
                    </GlassCardHeader>
                    <GlassCardContent className="px-0">
                      <div className="grid grid-cols-3 gap-2">
                        <div>
                          <label className="flex items-center gap-1 text-slate-500 text-[10px] mb-1 uppercase">
                            <Building2 className="w-2.5 h-2.5" />
                            Company
                          </label>
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
                          <label className="flex items-center gap-1 text-slate-500 text-[10px] mb-1 uppercase">
                            <Briefcase className="w-2.5 h-2.5" />
                            Role
                          </label>
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
                          <label className="flex items-center gap-1 text-slate-500 text-[10px] mb-1 uppercase">
                            <GraduationCap className="w-2.5 h-2.5" />
                            Level
                          </label>
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
                    </GlassCardContent>
                  </GlassCard>
                </motion.div>

                {/* Tech Stack */}
                <motion.div variants={itemVariants}>
                  <label className="flex items-center gap-1.5 text-slate-400 text-xs font-medium mb-2 uppercase tracking-wider">
                    <Sparkles className="w-3 h-3" />
                    Tech Stack (select your skills)
                  </label>
                  <div className="flex flex-wrap gap-1.5 max-h-24 overflow-y-auto p-1">
                    {techOptions.map((t) => (
                      <motion.button
                        type="button"
                        key={t}
                        onClick={() => toggleTag(techStack, setTechStack, t)}
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        className={`tag-pill transition-all ${
                          techStack.includes(t)
                            ? "bg-indigo-600/30 border border-indigo-500/40 text-indigo-300"
                            : "bg-slate-800/60 border border-slate-700/40 text-slate-500 hover:text-slate-300"
                        }`}
                      >
                        {t}
                      </motion.button>
                    ))}
                  </div>
                </motion.div>

                {/* Interest Areas */}
                <motion.div variants={itemVariants}>
                  <label className="flex items-center gap-1.5 text-slate-400 text-xs font-medium mb-2 uppercase tracking-wider">
                    <GraduationCap className="w-3 h-3" />
                    Interest Areas (what to learn)
                  </label>
                  <div className="flex flex-wrap gap-1.5 max-h-24 overflow-y-auto p-1">
                    {interestOptions.map((t) => (
                      <motion.button
                        type="button"
                        key={t}
                        onClick={() => toggleTag(interests, setInterests, t)}
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        className={`tag-pill transition-all ${
                          interests.includes(t)
                            ? "bg-emerald-600/30 border border-emerald-500/40 text-emerald-300"
                            : "bg-slate-800/60 border border-slate-700/40 text-slate-500 hover:text-slate-300"
                        }`}
                      >
                        {t}
                      </motion.button>
                    ))}
                  </div>
                </motion.div>

                {/* Hours per day */}
                <motion.div variants={itemVariants}>
                  <label className="flex items-center gap-1.5 text-slate-400 text-xs font-medium mb-2 uppercase tracking-wider">
                    <Clock className="w-3 h-3" />
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
                </motion.div>

                {/* Submit button */}
                <motion.div variants={itemVariants}>
                  <motion.button
                    type="submit"
                    disabled={loading}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    className="w-full py-3 rounded-xl font-semibold text-sm bg-gradient-to-r from-indigo-600 to-indigo-500 hover:from-indigo-500 hover:to-indigo-400 text-white shadow-lg shadow-indigo-500/20 transition-all disabled:opacity-50 flex items-center justify-center gap-2"
                  >
                    {loading ? (
                      <>
                        <motion.div
                          className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full"
                          animate={{ rotate: 360 }}
                          transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                        />
                        Creating account...
                      </>
                    ) : (
                      <>
                        <Sparkles className="w-4 h-4" />
                        Create Account
                      </>
                    )}
                  </motion.button>
                </motion.div>
              </form>

              <motion.p variants={itemVariants} className="text-center text-slate-500 text-sm mt-4">
                Already have an account?{" "}
                <button onClick={onSwitchToLogin} className="text-indigo-400 hover:text-indigo-300 font-medium transition-colors">
                  Sign In
                </button>
              </motion.p>
            </motion.div>
          </GlassCardContent>
        </GlassCard>
      </motion.div>
    </div>
  );
}
