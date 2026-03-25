import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  TrendingUp,
  Target,
  Zap,
  Award,
  Trophy,
  ArrowRight,
  BarChart3,
  Shield,
  AlertTriangle,
  Star,
  Play,
  BookOpen,
} from "lucide-react";
import { GlassCard, GlassCardContent, GlassCardHeader, GlassCardTitle } from "@/components/ui/glass-card";
import { apiFetch } from "@/lib/api";
import LoadingSpinner from "@/components/common/LoadingSpinner";
import Stars from "@/components/common/Stars";

interface DashboardScreenProps {
  onNavigate: (screen: string, params?: any) => void;
}

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.1 },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.4 } },
};

export default function DashboardScreen({ onNavigate }: DashboardScreenProps) {
  const [data, setData] = useState<any>(null);
  const [eloData, setEloData] = useState<any>(null);
  const [gapMap, setGapMap] = useState<any>(null);
  const [readiness, setReadiness] = useState<any>(null);
  const [comparison, setComparison] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [showCelebration, setShowCelebration] = useState(false);

  useEffect(() => {
    Promise.all([
      apiFetch("/dashboard").then((r) => r.json()),
      apiFetch("/elo")
        .then((r) => (r.ok ? r.json() : null))
        .catch(() => null),
      apiFetch("/gap-map")
        .then((r) => (r.ok ? r.json() : null))
        .catch(() => null),
      apiFetch("/readiness")
        .then((r) => (r.ok ? r.json() : null))
        .catch(() => null),
      apiFetch("/mock/comparison?limit=5")
        .then((r) => (r.ok ? r.json() : null))
        .catch(() => null),
    ])
      .then(([d, e, g, r, c]) => {
        setData(d);
        setEloData(e);
        setGapMap(g);
        setReadiness(r);
        setComparison(c);
        if (r?.celebrate) setShowCelebration(true);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  if (loading) return <LoadingSpinner />;
  if (!data) return <div className="text-center py-12 text-slate-500">Failed to load dashboard</div>;

  const { user, stats, plan_progress, next_topic, plan_timeline, overall_proficiency } = data;
  const pp = plan_progress || {};
  const eloReadiness = eloData?.readiness || {};
  const eloPercent = eloData ? Math.min(100, (eloData.overall / (eloReadiness.hiring_bar || 1800)) * 100) : 0;

  const statCards = [
    {
      label: "Plan Progress",
      value: `${pp.progress_pct || 0}%`,
      color: "text-indigo-400",
      icon: Target,
      iconBg: "bg-indigo-500/10",
      iconColor: "text-indigo-400",
    },
    {
      label: "Sessions",
      value: stats.total_sessions,
      color: "text-emerald-400",
      icon: Zap,
      iconBg: "bg-emerald-500/10",
      iconColor: "text-emerald-400",
    },
    {
      label: "Avg Score",
      value: stats.average_score || 0,
      color: "text-amber-400",
      icon: BarChart3,
      iconBg: "bg-amber-500/10",
      iconColor: "text-amber-400",
    },
  ];

  return (
    <motion.div
      className="max-w-5xl mx-auto p-4 md:p-6"
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      {/* Action-First Hero */}
      <motion.div variants={itemVariants}>
        <GlassCard className="p-6 mb-6 glow">
          <GlassCardContent className="px-0">
            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
              <div className="flex-1">
                <h1 className="text-2xl font-bold mb-1 bg-gradient-to-r from-white to-slate-300 bg-clip-text text-transparent">
                  Welcome back, {user.full_name}
                </h1>
                {user.target_company && (
                  <p className="text-slate-400 text-sm flex items-center gap-1.5">
                    <Target className="w-3.5 h-3.5 text-indigo-400" />
                    Targeting <span className="text-indigo-300 font-medium capitalize">{user.target_company}</span>{" "}
                    <span className="text-slate-500">|</span>{" "}
                    <span className="text-slate-300 capitalize">{(user.target_role || "").replace(/_/g, " ")}</span>{" "}
                    <span className="text-slate-500">|</span>{" "}
                    <span className="text-slate-300 capitalize">{user.target_level}</span>
                  </p>
                )}
                {next_topic ? (
                  <motion.button
                    onClick={() => onNavigate("learning", { topicId: next_topic.topic_id })}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    className="mt-3 px-6 py-2.5 rounded-xl text-sm font-semibold bg-gradient-to-r from-indigo-600 to-indigo-500 hover:from-indigo-500 hover:to-indigo-400 text-white shadow-lg shadow-indigo-500/20 transition-all flex items-center gap-2"
                  >
                    <BookOpen className="w-4 h-4" />
                    Continue Learning: {next_topic.title}
                    <ArrowRight className="w-4 h-4" />
                  </motion.button>
                ) : (
                  <motion.button
                    onClick={() => onNavigate("interview")}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    className="mt-3 px-6 py-2.5 rounded-xl text-sm font-semibold bg-gradient-to-r from-indigo-600 to-indigo-500 hover:from-indigo-500 hover:to-indigo-400 text-white shadow-lg shadow-indigo-500/20 transition-all flex items-center gap-2"
                  >
                    <Play className="w-4 h-4" />
                    Start Mock Interview
                    <ArrowRight className="w-4 h-4" />
                  </motion.button>
                )}
              </div>
              {/* ELO Display */}
              {eloData && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.3 }}
                  className="glass rounded-xl p-4 min-w-[220px] text-center"
                >
                  <p className="text-slate-500 text-[10px] uppercase tracking-wider mb-1 flex items-center justify-center gap-1">
                    <TrendingUp className="w-3 h-3" />
                    Your ELO Rating
                  </p>
                  <motion.p
                    className="text-4xl font-black text-indigo-400"
                    initial={{ opacity: 0, scale: 0.5 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ type: "spring", stiffness: 200, damping: 15, delay: 0.5 }}
                  >
                    {eloData.overall}
                  </motion.p>
                  <div className="w-full bg-slate-800/50 rounded-full h-2 mt-2 mb-1 overflow-hidden">
                    <motion.div
                      className="h-2 rounded-full bg-gradient-to-r from-indigo-500 to-purple-500"
                      initial={{ width: 0 }}
                      animate={{ width: `${eloPercent}%` }}
                      transition={{ duration: 1, delay: 0.6, ease: "easeOut" }}
                    />
                  </div>
                  <div className="flex items-center justify-between text-[10px]">
                    <span className="text-slate-500">You: {eloData.overall}</span>
                    <span className="text-slate-500">Bar: {eloReadiness.hiring_bar || "--"}</span>
                  </div>
                  <p className="mt-2">
                    <span
                      className={`text-xs px-2 py-0.5 rounded-full ${eloReadiness.is_ready ? "bg-emerald-500/20 text-emerald-300" : "bg-amber-500/20 text-amber-300"}`}
                    >
                      {eloReadiness.readiness?.label || "--"}
                    </span>
                  </p>
                  {eloReadiness.gap > 0 && (
                    <p className="text-slate-500 text-[10px] mt-1">{eloReadiness.gap} points to go</p>
                  )}
                </motion.div>
              )}
            </div>
          </GlassCardContent>
        </GlassCard>
      </motion.div>

      {/* Interview Ready Celebration */}
      <AnimatePresence>
        {showCelebration && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            transition={{ type: "spring", stiffness: 200, damping: 20 }}
          >
            <GlassCard className="p-6 mb-6 text-center glow-green border border-emerald-500/30">
              <GlassCardContent className="px-0 flex flex-col items-center">
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ type: "spring", stiffness: 300, damping: 10, delay: 0.2 }}
                >
                  <Trophy className="w-12 h-12 text-emerald-400 mb-2" />
                </motion.div>
                <h2 className="text-2xl font-bold text-emerald-400 mb-1">You're Interview Ready!</h2>
                <p className="text-slate-400 text-sm mb-3">
                  Your ELO of {readiness?.elo} has reached the {readiness?.company} {readiness?.level} hiring bar of{" "}
                  {readiness?.hiring_bar}
                </p>
                <div className="flex gap-3 justify-center">
                  <motion.button
                    onClick={() => setShowCelebration(false)}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    className="px-4 py-2 rounded-xl text-xs bg-emerald-600/20 text-emerald-300 hover:bg-emerald-600/30 border border-emerald-500/20"
                  >
                    Keep Practicing
                  </motion.button>
                </div>
              </GlassCardContent>
            </GlassCard>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Score Comparison (ELO over time) */}
      {comparison?.comparisons?.length > 1 && (
        <motion.div variants={itemVariants}>
          <GlassCard className="p-4 mb-6">
            <GlassCardContent className="px-0">
              <h3 className="text-white text-xs font-semibold mb-3 uppercase tracking-wider flex items-center gap-1.5">
                <BarChart3 className="w-3.5 h-3.5 text-indigo-400" />
                Mock Interview History
              </h3>
              <div className="flex items-end gap-2 h-16">
                {comparison.comparisons
                  .slice()
                  .reverse()
                  .map((c: any, i: number) => {
                    const maxElo = Math.max(...comparison.comparisons.map((x: any) => x.elo_after || 1200));
                    const height = Math.max(10, ((c.elo_after || 1200) / maxElo) * 100);
                    return (
                      <div key={i} className="flex-1 flex flex-col items-center gap-1">
                        <span
                          className={`text-[9px] font-medium ${(c.elo_delta || 0) >= 0 ? "text-emerald-400" : "text-red-400"}`}
                        >
                          {(c.elo_delta || 0) >= 0 ? "+" : ""}
                          {c.elo_delta || 0}
                        </span>
                        <motion.div
                          className="w-full bg-indigo-500/60 rounded-t"
                          initial={{ height: 0 }}
                          animate={{ height: `${height}%` }}
                          transition={{ duration: 0.6, delay: i * 0.1, ease: "easeOut" }}
                        />
                        <span className="text-[8px] text-slate-500">{c.elo_after || "--"}</span>
                      </div>
                    );
                  })}
              </div>
            </GlassCardContent>
          </GlassCard>
        </motion.div>
      )}

      {/* Sub-ELO Breakdown */}
      {eloData?.sub_elos && (
        <motion.div variants={itemVariants} className="grid grid-cols-5 gap-2 mb-6">
          {Object.entries(eloData.sub_elos).map(([round, elo]: [string, any], i) => (
            <motion.div
              key={round}
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 * i }}
            >
              <GlassCard className="p-3 text-center">
                <GlassCardContent className="px-0 py-0">
                  <p className="text-lg font-bold text-slate-200">{elo}</p>
                  <p className="text-slate-500 text-[10px] mt-0.5 capitalize">{round.replace(/_/g, " ")}</p>
                </GlassCardContent>
              </GlassCard>
            </motion.div>
          ))}
        </motion.div>
      )}

      {/* Stats Cards */}
      <motion.div variants={itemVariants} className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
        {statCards.map((card, i) => {
          const Icon = card.icon;
          return (
            <motion.div
              key={card.label}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 * i }}
            >
              <GlassCard className="p-4 text-center relative overflow-hidden">
                <GlassCardContent className="px-0 py-0">
                  <div className={`absolute top-2 right-2 ${card.iconBg} rounded-full p-1.5`}>
                    <Icon className={`w-3.5 h-3.5 ${card.iconColor}`} />
                  </div>
                  <p className={`text-3xl font-bold ${card.color}`}>{card.value}</p>
                  <p className="text-slate-500 text-xs mt-1">{card.label}</p>
                </GlassCardContent>
              </GlassCard>
            </motion.div>
          );
        })}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <GlassCard className="p-4 text-center relative overflow-hidden">
            <GlassCardContent className="px-0 py-0">
              <div className="absolute top-2 right-2 bg-amber-500/10 rounded-full p-1.5">
                <Award className="w-3.5 h-3.5 text-amber-400" />
              </div>
              <div className="flex justify-center mb-1">
                <Stars rating={Math.round(overall_proficiency || 0)} size="lg" />
              </div>
              <p className="text-slate-500 text-xs mt-1">Proficiency</p>
            </GlassCardContent>
          </GlassCard>
        </motion.div>
      </motion.div>

      {/* Gap Map */}
      {gapMap && (
        <motion.div variants={itemVariants}>
          <GlassCard className="p-5 mb-6">
            <GlassCardContent className="px-0">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-white text-sm font-semibold uppercase tracking-wider flex items-center gap-1.5">
                  <Shield className="w-4 h-4 text-indigo-400" />
                  Skill Gap Map
                </h3>
                <span className="text-indigo-400 text-xs font-medium">
                  {gapMap.coverage_percent}% coverage ({gapMap.covered_demands}/{gapMap.total_demands} skills)
                </span>
              </div>
              <div className="w-full bg-slate-800/50 rounded-full h-2 mb-4 overflow-hidden">
                <motion.div
                  className="h-2 rounded-full bg-gradient-to-r from-emerald-500 to-indigo-500"
                  initial={{ width: 0 }}
                  animate={{ width: `${gapMap.coverage_percent}%` }}
                  transition={{ duration: 1, delay: 0.3, ease: "easeOut" }}
                />
              </div>
              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <p className="text-emerald-400 text-xs font-semibold uppercase tracking-wider mb-2 flex items-center gap-1">
                    <Star className="w-3 h-3" />
                    Strengths ({gapMap.strengths.length})
                  </p>
                  <div className="space-y-1 max-h-32 overflow-y-auto">
                    {gapMap.strengths.map((s: any, i: number) => (
                      <motion.div
                        key={s.skill}
                        className="flex items-center gap-2"
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.05 * i }}
                      >
                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                        <span className="text-slate-300 text-xs">{s.skill}</span>
                        <span className="text-slate-600 text-[10px]">({s.matched_by.join(", ")})</span>
                      </motion.div>
                    ))}
                  </div>
                </div>
                <div>
                  <p className="text-red-400 text-xs font-semibold uppercase tracking-wider mb-2 flex items-center gap-1">
                    <AlertTriangle className="w-3 h-3" />
                    Gaps ({gapMap.gaps.length})
                  </p>
                  <div className="space-y-1 max-h-32 overflow-y-auto">
                    {gapMap.gaps.map((g: any, i: number) => (
                      <motion.div
                        key={g.skill}
                        className="flex items-center gap-2"
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.05 * i }}
                      >
                        <span
                          className={`w-1.5 h-1.5 rounded-full ${g.priority === "high" ? "bg-red-400" : "bg-amber-400"}`}
                        />
                        <span className="text-slate-300 text-xs">{g.skill}</span>
                        <span
                          className={`text-[10px] px-1.5 py-0 rounded-full ${g.priority === "high" ? "bg-red-500/20 text-red-300" : "bg-amber-500/20 text-amber-300"}`}
                        >
                          {g.priority}
                        </span>
                      </motion.div>
                    ))}
                  </div>
                </div>
              </div>
            </GlassCardContent>
          </GlassCard>
        </motion.div>
      )}

      <motion.div variants={itemVariants} className="grid md:grid-cols-2 gap-4 mb-6">
        {/* Next Topic / Resume */}
        <GlassCard className="p-5">
          <GlassCardContent className="px-0">
            <h3 className="text-white text-sm font-semibold mb-3 uppercase tracking-wider flex items-center gap-1.5">
              <BookOpen className="w-4 h-4 text-indigo-400" />
              Continue Learning
            </h3>
            {next_topic ? (
              <div>
                <p className="text-slate-300 text-sm font-medium">{next_topic.title}</p>
                <p className="text-slate-500 text-xs mt-1">{next_topic.interest_area}</p>
                <p className="text-xs mt-1">
                  <span
                    className={`px-2 py-0.5 rounded-full ${next_topic.status === "in_progress" ? "bg-amber-500/20 text-amber-300" : "bg-slate-500/20 text-slate-400"}`}
                  >
                    {next_topic.status.replace(/_/g, " ")}
                  </span>
                </p>
                <motion.button
                  onClick={() => onNavigate("learning", { topicId: next_topic.topic_id })}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className="mt-3 px-5 py-2 rounded-xl text-sm font-medium bg-indigo-600 hover:bg-indigo-500 text-white transition-all flex items-center gap-2"
                >
                  <Play className="w-3.5 h-3.5" />
                  Resume Learning
                </motion.button>
              </div>
            ) : (
              <p className="text-slate-500 text-sm">No active topics. Generate a learning plan from your profile.</p>
            )}
            {data.has_resumable_session && (
              <motion.button
                onClick={() => onNavigate("interview", { resumeSessionId: data.resumable_session_id })}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className="mt-3 px-5 py-2 rounded-xl text-sm font-medium bg-emerald-600/20 text-emerald-400 hover:bg-emerald-600/30 border border-emerald-500/20 transition-all block flex items-center gap-2"
              >
                <ArrowRight className="w-3.5 h-3.5" />
                Resume Interview Session
              </motion.button>
            )}
          </GlassCardContent>
        </GlassCard>

        {/* Topic Scores */}
        <GlassCard className="p-5">
          <GlassCardContent className="px-0">
            <h3 className="text-white text-sm font-semibold mb-3 uppercase tracking-wider flex items-center gap-1.5">
              <BarChart3 className="w-4 h-4 text-indigo-400" />
              Topic Scores
            </h3>
            {Object.keys(stats.topic_scores || {}).length > 0 ? (
              <div className="space-y-2 max-h-40 overflow-y-auto">
                {Object.entries(stats.topic_scores)
                  .sort((a: any, b: any) => b[1] - a[1])
                  .map(([topic, score]: [string, any], i) => (
                    <motion.div
                      key={topic}
                      className="flex items-center gap-2"
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.05 * i }}
                    >
                      <span className="text-slate-400 text-xs w-24 truncate">{topic}</span>
                      <div className="flex-1 bg-slate-800/50 rounded-full h-1.5 overflow-hidden">
                        <motion.div
                          className={`h-1.5 rounded-full ${score >= 75 ? "bg-emerald-500" : score >= 50 ? "bg-amber-500" : "bg-red-500"}`}
                          initial={{ width: 0 }}
                          animate={{ width: `${score}%` }}
                          transition={{ duration: 0.6, delay: 0.1 * i, ease: "easeOut" }}
                        />
                      </div>
                      <span className="text-slate-500 text-xs w-8 text-right">{score}</span>
                    </motion.div>
                  ))}
              </div>
            ) : (
              <p className="text-slate-500 text-sm">Complete sessions to see scores</p>
            )}
          </GlassCardContent>
        </GlassCard>
      </motion.div>

      {/* Learning Plan Timeline */}
      {plan_timeline && plan_timeline.length > 0 && (
        <motion.div variants={itemVariants}>
          <GlassCard className="p-5">
            <GlassCardContent className="px-0">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-white text-sm font-semibold uppercase tracking-wider flex items-center gap-1.5">
                  <TrendingUp className="w-4 h-4 text-indigo-400" />
                  Learning Path
                </h3>
                <span className="text-slate-500 text-xs">
                  {pp.completed}/{pp.total} topics complete
                </span>
              </div>
              <div className="space-y-1.5 max-h-64 overflow-y-auto">
                {plan_timeline.map((t: any, i: number) => {
                  const isDelayed = t.revised_end_date > t.original_end_date;
                  return (
                    <motion.div
                      key={t.topic_id}
                      className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-white/[0.02] cursor-pointer transition-colors"
                      onClick={() => onNavigate("learning", { topicId: t.topic_id })}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.03 * i }}
                      whileHover={{ x: 4 }}
                    >
                      <span className="text-slate-600 text-xs w-5">{i + 1}</span>
                      <div
                        className={`w-2 h-2 rounded-full ${t.status === "completed" ? "bg-emerald-400" : t.status === "in_progress" ? "bg-amber-400" : "bg-slate-700"}`}
                      />
                      <span className="text-slate-300 text-sm flex-1 truncate">{t.title}</span>
                      <span className="text-slate-600 text-[10px] w-20 truncate">{t.interest_area}</span>
                      {t.assessment_rating && <Stars rating={t.assessment_rating} />}
                      <span className={`text-[10px] w-16 text-right ${isDelayed ? "text-red-400" : "text-slate-600"}`}>
                        {t.revised_end_date}
                      </span>
                      {isDelayed && (
                        <AlertTriangle className="w-3 h-3 text-red-400" />
                      )}
                    </motion.div>
                  );
                })}
              </div>
            </GlassCardContent>
          </GlassCard>
        </motion.div>
      )}
    </motion.div>
  );
}
