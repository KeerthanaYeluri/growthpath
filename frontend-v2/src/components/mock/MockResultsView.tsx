import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Trophy,
  TrendingUp,
  TrendingDown,
  Target,
  Users,
  AlertTriangle,
  CheckCircle,
  XCircle,
  ChevronDown,
  ChevronUp,
  Eye,
  MessageSquare,
} from "lucide-react";
import { GlassCard, GlassCardHeader, GlassCardTitle, GlassCardContent, GlassCardFooter } from "@/components/ui/glass-card";
import { cn } from "@/lib/utils";
import { apiFetch } from "@/lib/api";

interface MockResultsViewProps {
  elo: any;
  sc: any;
  readiness: any;
  mockData: any;
  sessionId: string;
  onNavigate: (screen: string) => void;
}

function AnimatedCounter({ from, to, duration = 1.2 }: { from: number; to: number; duration?: number }) {
  const [value, setValue] = useState(from);
  useEffect(() => {
    const start = performance.now();
    const tick = (now: number) => {
      const elapsed = (now - start) / 1000;
      const progress = Math.min(elapsed / duration, 1);
      // ease-out
      const eased = 1 - Math.pow(1 - progress, 3);
      setValue(Math.round(from + (to - from) * eased));
      if (progress < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  }, [from, to, duration]);
  return <>{value}</>;
}

const stagger = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.12 },
  },
};

const fadeUp = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.5 } },
};

export default function MockResultsView({ elo, sc, readiness, mockData, sessionId, onNavigate }: MockResultsViewProps) {
  const [rubrics, setRubrics] = useState<any[] | null>(null);
  const [committee, setCommittee] = useState<any>(null);
  const [showRubric, setShowRubric] = useState(false);
  const [showCommittee, setShowCommittee] = useState(false);
  const [loadingRubric, setLoadingRubric] = useState(false);
  const [loadingCommittee, setLoadingCommittee] = useState(false);

  const loadRubrics = async () => {
    if (rubrics) {
      setShowRubric(!showRubric);
      return;
    }
    setLoadingRubric(true);
    try {
      const res = await apiFetch(`/mock/${sessionId}/rubric`);
      const data = await res.json();
      setRubrics(data.rubric_reveals || []);
      setShowRubric(true);
    } catch {}
    setLoadingRubric(false);
  };

  const loadCommittee = async () => {
    if (committee) {
      setShowCommittee(!showCommittee);
      return;
    }
    setLoadingCommittee(true);
    try {
      const res = await apiFetch(`/mock/${sessionId}/committee`);
      const data = await res.json();
      setCommittee(data);
      setShowCommittee(true);
    } catch {}
    setLoadingCommittee(false);
  };

  return (
    <motion.div
      variants={stagger}
      initial="hidden"
      animate="visible"
      className="max-w-3xl mx-auto p-4 md:p-6"
    >
      {/* Sticky navigation */}
      <motion.div variants={fadeUp} className="flex justify-end mb-4">
        <button
          onClick={() => onNavigate("dashboard")}
          className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-medium transition-all flex items-center gap-1.5"
        >
          Back to Dashboard
        </button>
      </motion.div>

      {/* Title */}
      <motion.div variants={fadeUp} className="text-center mb-6">
        <Trophy className="w-10 h-10 text-amber-400 mx-auto mb-2" />
        <h2 className="text-2xl font-bold mb-1">Mock Interview Complete</h2>
        <p className="text-slate-400 text-sm capitalize">
          {mockData?.company} | {(mockData?.role || "").replace(/_/g, " ")} | {mockData?.level}
        </p>
      </motion.div>

      {/* ELO Change */}
      <motion.div variants={fadeUp}>
        <GlassCard className="mb-6 text-center glow">
          <GlassCardContent>
            <p className="text-slate-500 text-xs uppercase mb-1">ELO Rating</p>
            <div className="flex items-center justify-center gap-3">
              <span className="text-slate-500 text-xl">{elo?.before}</span>
              <span className="text-2xl text-slate-600">{"-->"}</span>
              <motion.span
                initial={{ scale: 0.5, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ type: "spring", stiffness: 200, damping: 12, delay: 0.3 }}
                className="text-4xl font-black text-indigo-400"
              >
                <AnimatedCounter from={elo?.before || 0} to={elo?.after || 0} />
              </motion.span>
              <motion.span
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.6 }}
                className={cn(
                  "text-sm font-bold flex items-center gap-1",
                  (elo?.delta || 0) >= 0 ? "text-emerald-400" : "text-red-400"
                )}
              >
                {(elo?.delta || 0) >= 0 ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
                {(elo?.delta || 0) >= 0 ? "+" : ""}
                {elo?.delta}
              </motion.span>
            </div>
            <p className="mt-2">
              <span
                className={cn(
                  "px-3 py-1 rounded-full text-xs",
                  readiness?.is_ready ? "bg-emerald-500/20 text-emerald-300" : "bg-amber-500/20 text-amber-300"
                )}
              >
                {readiness?.readiness?.label || "--"}
              </span>
            </p>
            {(readiness?.gap || 0) > 0 && (
              <p className="text-slate-500 text-xs mt-1 flex items-center justify-center gap-1">
                <Target className="w-3 h-3" />
                {readiness.gap} points to go
              </p>
            )}
          </GlassCardContent>
        </GlassCard>
      </motion.div>

      {/* Round Scores */}
      <motion.div variants={fadeUp}>
        <GlassCard className="mb-6">
          <GlassCardHeader>
            <GlassCardTitle className="text-sm uppercase tracking-wider">Round Scores</GlassCardTitle>
          </GlassCardHeader>
          <GlassCardContent>
            <div className="space-y-3">
              {(mockData?.rounds || []).map((rnd: any, idx: number) => {
                const score = sc?.per_round?.[rnd.round_type] || 0;
                return (
                  <div key={rnd.round_type} className="flex items-center gap-3">
                    <span className="text-slate-400 text-xs w-32">{rnd.label}</span>
                    <div className="flex-1 bg-slate-800/50 rounded-full h-2.5 overflow-hidden">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${score}%` }}
                        transition={{ duration: 0.8, delay: 0.2 + idx * 0.1, ease: "easeOut" }}
                        className={cn(
                          "h-2.5 rounded-full",
                          score >= 70 ? "bg-emerald-500" : score >= 40 ? "bg-amber-500" : "bg-red-500"
                        )}
                      />
                    </div>
                    <span className="text-slate-300 text-sm w-10 text-right font-medium">{score}</span>
                    {rnd.is_critical && (
                      <span className="text-[9px] px-1.5 py-0.5 rounded bg-red-500/20 text-red-300 flex items-center gap-0.5">
                        <AlertTriangle className="w-2.5 h-2.5" /> critical
                      </span>
                    )}
                  </div>
                );
              })}
            </div>
          </GlassCardContent>
        </GlassCard>
      </motion.div>

      {/* Focus Areas */}
      {sc?.recommended_focus?.length > 0 && (
        <motion.div variants={fadeUp}>
          <GlassCard className="mb-6">
            <GlassCardHeader>
              <GlassCardTitle className="text-sm text-red-400 uppercase tracking-wider flex items-center gap-1.5">
                <AlertTriangle className="w-4 h-4" /> Focus Areas
              </GlassCardTitle>
            </GlassCardHeader>
            <GlassCardContent>
              <div className="flex flex-wrap gap-2">
                {sc.recommended_focus.map((f: string, i: number) => (
                  <motion.span
                    key={f}
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.1 * i }}
                    className="px-3 py-1 rounded-full bg-red-500/20 text-red-300 text-xs"
                  >
                    {f}
                  </motion.span>
                ))}
              </div>
            </GlassCardContent>
          </GlassCard>
        </motion.div>
      )}

      {/* Action Buttons: Rubric Reveal + Hiring Committee */}
      <motion.div variants={fadeUp} className="grid grid-cols-2 gap-3 mb-6">
        <motion.button
          whileHover={{ y: -2 }}
          whileTap={{ scale: 0.97 }}
          onClick={loadRubrics}
          disabled={loadingRubric}
          className="glass rounded-xl p-4 text-center hover:bg-white/[0.04] transition-all cursor-pointer"
        >
          <Eye className="w-5 h-5 text-purple-400 mx-auto mb-1" />
          <p className="text-purple-400 text-sm font-semibold flex items-center justify-center gap-1">
            {loadingRubric ? "Loading..." : showRubric ? "Hide Rubric" : "Rubric Reveal"}
            <motion.span animate={{ rotate: showRubric ? 180 : 0 }} transition={{ duration: 0.3 }}>
              <ChevronDown className="w-4 h-4" />
            </motion.span>
          </p>
          <p className="text-slate-500 text-[10px] mt-1">See what interviewer was evaluating</p>
        </motion.button>
        <motion.button
          whileHover={{ y: -2 }}
          whileTap={{ scale: 0.97 }}
          onClick={loadCommittee}
          disabled={loadingCommittee}
          className="glass rounded-xl p-4 text-center hover:bg-white/[0.04] transition-all cursor-pointer"
        >
          <Users className="w-5 h-5 text-amber-400 mx-auto mb-1" />
          <p className="text-amber-400 text-sm font-semibold flex items-center justify-center gap-1">
            {loadingCommittee ? "Loading..." : showCommittee ? "Hide Committee" : "Hiring Committee"}
            <motion.span animate={{ rotate: showCommittee ? 180 : 0 }} transition={{ duration: 0.3 }}>
              <ChevronDown className="w-4 h-4" />
            </motion.span>
          </p>
          <p className="text-slate-500 text-[10px] mt-1">See HIRE / NO HIRE verdict</p>
        </motion.button>
      </motion.div>

      {/* Rubric Reveal Panel */}
      <AnimatePresence>
        {showRubric && rubrics && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.4 }}
            className="overflow-hidden"
          >
            <GlassCard className="mb-6">
              <GlassCardHeader>
                <GlassCardTitle className="text-sm text-purple-300 uppercase tracking-wider flex items-center gap-1.5">
                  <Eye className="w-4 h-4" /> Rubric Reveal -- What the Interviewer Was Looking For
                </GlassCardTitle>
              </GlassCardHeader>
              <GlassCardContent>
                <div className="space-y-4 max-h-96 overflow-y-auto">
                  {rubrics.map((r: any, i: number) => (
                    <motion.div
                      key={i}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: i * 0.08 }}
                      className="bg-slate-800/40 rounded-lg p-3"
                    >
                      <div className="flex items-center justify-between mb-2">
                        <p className="text-white text-xs font-medium truncate flex-1">{r.question}</p>
                        <span className="text-slate-400 text-[10px] ml-2">
                          {r.covered_count}/{r.total_count} covered
                        </span>
                      </div>
                      <div className="space-y-1">
                        {r.rubric_points.map((p: any, j: number) => (
                          <motion.div
                            key={j}
                            initial={{ opacity: 0, x: -10 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: i * 0.08 + j * 0.04 }}
                            className="flex items-center gap-2"
                          >
                            {p.covered ? (
                              <CheckCircle className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0" />
                            ) : (
                              <XCircle className="w-3.5 h-3.5 text-red-400 flex-shrink-0" />
                            )}
                            <span className={cn("text-xs", p.covered ? "text-slate-300" : "text-slate-500")}>
                              {p.point}
                            </span>
                          </motion.div>
                        ))}
                      </div>
                      {r.keywords_missed.length > 0 && (
                        <p className="text-slate-500 text-[10px] mt-2">Missed keywords: {r.keywords_missed.join(", ")}</p>
                      )}
                    </motion.div>
                  ))}
                </div>
              </GlassCardContent>
            </GlassCard>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Hiring Committee Panel */}
      <AnimatePresence>
        {showCommittee && committee && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.4 }}
            className="overflow-hidden"
          >
            <GlassCard className="mb-6">
              <GlassCardContent>
                {/* Verdict */}
                <motion.div
                  initial={{ scale: 0.8, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  transition={{ type: "spring", stiffness: 200, damping: 15 }}
                  className={cn(
                    "text-center p-4 rounded-xl mb-4",
                    committee.verdict.includes("NO")
                      ? "bg-red-500/10 border border-red-500/20"
                      : "bg-emerald-500/10 border border-emerald-500/20"
                  )}
                >
                  <p
                    className={cn(
                      "text-xl font-bold",
                      committee.verdict.includes("NO") ? "text-red-400" : "text-emerald-400"
                    )}
                  >
                    {committee.verdict_label}
                  </p>
                  {committee.veto_applied && (
                    <p className="text-red-300 text-xs mt-1 flex items-center justify-center gap-1">
                      <AlertTriangle className="w-3 h-3" /> Veto applied on critical round
                    </p>
                  )}
                  <p className="text-slate-400 text-xs mt-2">{committee.recommendation}</p>
                </motion.div>

                {/* Interviewers */}
                <h3 className="text-amber-300 text-sm font-semibold mb-3 uppercase tracking-wider flex items-center gap-1.5">
                  <Users className="w-4 h-4" /> Committee Members
                </h3>
                <div className="space-y-3">
                  {committee.interviewers.map((inv: any, i: number) => (
                    <motion.div
                      key={i}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.15 * i }}
                      className="bg-slate-800/40 rounded-lg p-3"
                    >
                      <div className="flex items-center justify-between mb-1">
                        <div>
                          <span className="text-white text-xs font-medium">{inv.name}</span>
                          <span className="text-slate-500 text-[10px] ml-2">{inv.title}</span>
                        </div>
                        <motion.span
                          initial={{ scale: 0 }}
                          animate={{ scale: 1 }}
                          transition={{ type: "spring", delay: 0.3 + 0.1 * i }}
                          className={cn(
                            "px-2 py-0.5 rounded-full text-[10px] font-semibold",
                            inv.vote.includes("NO")
                              ? "bg-red-500/20 text-red-300"
                              : "bg-emerald-500/20 text-emerald-300"
                          )}
                        >
                          {inv.vote.replace(/_/g, " ")}
                        </motion.span>
                      </div>
                      <p className="text-slate-500 text-[10px] mb-1">
                        Evaluated: {inv.assigned_round_labels.join(", ")}
                      </p>
                      <p className="text-slate-400 text-xs italic flex items-start gap-1">
                        <MessageSquare className="w-3 h-3 flex-shrink-0 mt-0.5" />
                        "{inv.reasoning}"
                      </p>
                      {inv.quotes.map((q: string, j: number) => (
                        <p key={j} className="text-slate-500 text-[10px] mt-1 pl-4">
                          -- {q}
                        </p>
                      ))}
                    </motion.div>
                  ))}
                </div>
              </GlassCardContent>
            </GlassCard>
          </motion.div>
        )}
      </AnimatePresence>

      <motion.button
        variants={fadeUp}
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        onClick={() => onNavigate("dashboard")}
        className="w-full py-3 rounded-xl font-semibold text-sm bg-indigo-600 hover:bg-indigo-500 text-white transition-all"
      >
        Back to Dashboard
      </motion.button>
    </motion.div>
  );
}
