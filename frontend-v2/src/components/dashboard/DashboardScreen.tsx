import { useState, useEffect } from "react";
import { apiFetch } from "@/lib/api";
import LoadingSpinner from "@/components/common/LoadingSpinner";
import Stars from "@/components/common/Stars";

interface DashboardScreenProps {
  onNavigate: (screen: string, params?: any) => void;
}

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

  return (
    <div className="max-w-5xl mx-auto p-4 md:p-6 animate-fade-in">
      {/* v2: Action-First Hero */}
      <div className="glass-strong rounded-2xl p-6 mb-6 glow">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div className="flex-1">
            <h1 className="text-2xl font-bold mb-1">Welcome back, {user.full_name}</h1>
            {user.target_company && (
              <p className="text-slate-400 text-sm">
                Targeting <span className="text-indigo-300 font-medium capitalize">{user.target_company}</span>{" "}
                <span className="text-slate-500">|</span>{" "}
                <span className="text-slate-300 capitalize">{(user.target_role || "").replace(/_/g, " ")}</span>{" "}
                <span className="text-slate-500">|</span>{" "}
                <span className="text-slate-300 capitalize">{user.target_level}</span>
              </p>
            )}
            {next_topic ? (
              <button
                onClick={() => onNavigate("learning", { topicId: next_topic.topic_id })}
                className="mt-3 px-6 py-2.5 rounded-xl text-sm font-semibold bg-indigo-600 hover:bg-indigo-500 text-white shadow-lg shadow-indigo-500/20 transition-all"
              >
                Continue Learning: {next_topic.title}
              </button>
            ) : (
              <button
                onClick={() => onNavigate("interview")}
                className="mt-3 px-6 py-2.5 rounded-xl text-sm font-semibold bg-indigo-600 hover:bg-indigo-500 text-white shadow-lg shadow-indigo-500/20 transition-all"
              >
                Start Mock Interview
              </button>
            )}
          </div>
          {/* ELO Display */}
          {eloData && (
            <div className="glass rounded-xl p-4 min-w-[220px] text-center">
              <p className="text-slate-500 text-[10px] uppercase tracking-wider mb-1">Your ELO Rating</p>
              <p className="text-4xl font-black text-indigo-400">{eloData.overall}</p>
              <div className="w-full bg-slate-800/50 rounded-full h-2 mt-2 mb-1">
                <div
                  className="h-2 rounded-full bg-gradient-to-r from-indigo-500 to-purple-500 transition-all"
                  style={{ width: `${eloPercent}%` }}
                ></div>
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
            </div>
          )}
        </div>
      </div>

      {/* Interview Ready Celebration */}
      {showCelebration && (
        <div className="glass-strong rounded-2xl p-6 mb-6 text-center glow-green border border-emerald-500/30 animate-fade-in">
          <p className="text-4xl mb-2">{"\\ud83c\\udf89"}</p>
          <h2 className="text-2xl font-bold text-emerald-400 mb-1">You're Interview Ready!</h2>
          <p className="text-slate-400 text-sm mb-3">
            Your ELO of {readiness?.elo} has reached the {readiness?.company} {readiness?.level} hiring bar of{" "}
            {readiness?.hiring_bar}
          </p>
          <div className="flex gap-3 justify-center">
            <button
              onClick={() => setShowCelebration(false)}
              className="px-4 py-2 rounded-xl text-xs bg-emerald-600/20 text-emerald-300 hover:bg-emerald-600/30 border border-emerald-500/20"
            >
              Keep Practicing
            </button>
          </div>
        </div>
      )}

      {/* Score Comparison (ELO over time) */}
      {comparison?.comparisons?.length > 1 && (
        <div className="glass rounded-xl p-4 mb-6">
          <h3 className="text-white text-xs font-semibold mb-3 uppercase tracking-wider">Mock Interview History</h3>
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
                    <div className="w-full bg-indigo-500/60 rounded-t" style={{ height: `${height}%` }}></div>
                    <span className="text-[8px] text-slate-500">{c.elo_after || "--"}</span>
                  </div>
                );
              })}
          </div>
        </div>
      )}

      {/* v2: Sub-ELO Breakdown */}
      {eloData?.sub_elos && (
        <div className="grid grid-cols-5 gap-2 mb-6">
          {Object.entries(eloData.sub_elos).map(([round, elo]: [string, any]) => (
            <div key={round} className="glass rounded-xl p-3 text-center">
              <p className="text-lg font-bold text-slate-200">{elo}</p>
              <p className="text-slate-500 text-[10px] mt-0.5 capitalize">{round.replace(/_/g, " ")}</p>
            </div>
          ))}
        </div>
      )}

      {/* Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
        <div className="glass rounded-xl p-4 text-center">
          <p className="text-3xl font-bold text-indigo-400">{pp.progress_pct || 0}%</p>
          <p className="text-slate-500 text-xs mt-1">Plan Progress</p>
        </div>
        <div className="glass rounded-xl p-4 text-center">
          <p className="text-3xl font-bold text-emerald-400">{stats.total_sessions}</p>
          <p className="text-slate-500 text-xs mt-1">Sessions</p>
        </div>
        <div className="glass rounded-xl p-4 text-center">
          <p className="text-3xl font-bold text-amber-400">{stats.average_score || 0}</p>
          <p className="text-slate-500 text-xs mt-1">Avg Score</p>
        </div>
        <div className="glass rounded-xl p-4 text-center">
          <div className="flex justify-center mb-1">
            <Stars rating={Math.round(overall_proficiency || 0)} size="lg" />
          </div>
          <p className="text-slate-500 text-xs mt-1">Proficiency</p>
        </div>
      </div>

      {/* v2: Gap Map */}
      {gapMap && (
        <div className="glass rounded-xl p-5 mb-6">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-white text-sm font-semibold uppercase tracking-wider">Skill Gap Map</h3>
            <span className="text-indigo-400 text-xs font-medium">
              {gapMap.coverage_percent}% coverage ({gapMap.covered_demands}/{gapMap.total_demands} skills)
            </span>
          </div>
          <div className="w-full bg-slate-800/50 rounded-full h-2 mb-4">
            <div
              className="h-2 rounded-full bg-gradient-to-r from-emerald-500 to-indigo-500 transition-all"
              style={{ width: `${gapMap.coverage_percent}%` }}
            ></div>
          </div>
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <p className="text-emerald-400 text-xs font-semibold uppercase tracking-wider mb-2">
                Strengths ({gapMap.strengths.length})
              </p>
              <div className="space-y-1 max-h-32 overflow-y-auto">
                {gapMap.strengths.map((s: any) => (
                  <div key={s.skill} className="flex items-center gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
                    <span className="text-slate-300 text-xs">{s.skill}</span>
                    <span className="text-slate-600 text-[10px]">({s.matched_by.join(", ")})</span>
                  </div>
                ))}
              </div>
            </div>
            <div>
              <p className="text-red-400 text-xs font-semibold uppercase tracking-wider mb-2">
                Gaps ({gapMap.gaps.length})
              </p>
              <div className="space-y-1 max-h-32 overflow-y-auto">
                {gapMap.gaps.map((g: any) => (
                  <div key={g.skill} className="flex items-center gap-2">
                    <span
                      className={`w-1.5 h-1.5 rounded-full ${g.priority === "high" ? "bg-red-400" : "bg-amber-400"}`}
                    ></span>
                    <span className="text-slate-300 text-xs">{g.skill}</span>
                    <span
                      className={`text-[10px] px-1.5 py-0 rounded-full ${g.priority === "high" ? "bg-red-500/20 text-red-300" : "bg-amber-500/20 text-amber-300"}`}
                    >
                      {g.priority}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="grid md:grid-cols-2 gap-4 mb-6">
        {/* Next Topic / Resume */}
        <div className="glass rounded-xl p-5">
          <h3 className="text-white text-sm font-semibold mb-3 uppercase tracking-wider">Continue Learning</h3>
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
              <button
                onClick={() => onNavigate("learning", { topicId: next_topic.topic_id })}
                className="mt-3 px-5 py-2 rounded-xl text-sm font-medium bg-indigo-600 hover:bg-indigo-500 text-white transition-all"
              >
                Resume Learning
              </button>
            </div>
          ) : (
            <p className="text-slate-500 text-sm">No active topics. Generate a learning plan from your profile.</p>
          )}
          {data.has_resumable_session && (
            <button
              onClick={() => onNavigate("interview", { resumeSessionId: data.resumable_session_id })}
              className="mt-3 px-5 py-2 rounded-xl text-sm font-medium bg-emerald-600/20 text-emerald-400 hover:bg-emerald-600/30 border border-emerald-500/20 transition-all block"
            >
              Resume Interview Session
            </button>
          )}
        </div>

        {/* Topic Scores */}
        <div className="glass rounded-xl p-5">
          <h3 className="text-white text-sm font-semibold mb-3 uppercase tracking-wider">Topic Scores</h3>
          {Object.keys(stats.topic_scores || {}).length > 0 ? (
            <div className="space-y-2 max-h-40 overflow-y-auto">
              {Object.entries(stats.topic_scores)
                .sort((a: any, b: any) => b[1] - a[1])
                .map(([topic, score]: [string, any]) => (
                  <div key={topic} className="flex items-center gap-2">
                    <span className="text-slate-400 text-xs w-24 truncate">{topic}</span>
                    <div className="flex-1 bg-slate-800/50 rounded-full h-1.5">
                      <div
                        className={`h-1.5 rounded-full ${score >= 75 ? "bg-emerald-500" : score >= 50 ? "bg-amber-500" : "bg-red-500"}`}
                        style={{ width: `${score}%` }}
                      ></div>
                    </div>
                    <span className="text-slate-500 text-xs w-8 text-right">{score}</span>
                  </div>
                ))}
            </div>
          ) : (
            <p className="text-slate-500 text-sm">Complete sessions to see scores</p>
          )}
        </div>
      </div>

      {/* Learning Plan Timeline */}
      {plan_timeline && plan_timeline.length > 0 && (
        <div className="glass rounded-xl p-5">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-white text-sm font-semibold uppercase tracking-wider">Learning Path</h3>
            <span className="text-slate-500 text-xs">
              {pp.completed}/{pp.total} topics complete
            </span>
          </div>
          <div className="space-y-1.5 max-h-64 overflow-y-auto">
            {plan_timeline.map((t: any, i: number) => {
              const isDelayed = t.revised_end_date > t.original_end_date;
              return (
                <div
                  key={t.topic_id}
                  className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-white/[0.02] cursor-pointer"
                  onClick={() => onNavigate("learning", { topicId: t.topic_id })}
                >
                  <span className="text-slate-600 text-xs w-5">{i + 1}</span>
                  <div
                    className={`w-2 h-2 rounded-full ${t.status === "completed" ? "bg-emerald-400" : t.status === "in_progress" ? "bg-amber-400" : "bg-slate-700"}`}
                  ></div>
                  <span className="text-slate-300 text-sm flex-1 truncate">{t.title}</span>
                  <span className="text-slate-600 text-[10px] w-20 truncate">{t.interest_area}</span>
                  {t.assessment_rating && <Stars rating={t.assessment_rating} />}
                  <span className={`text-[10px] w-16 text-right ${isDelayed ? "text-red-400" : "text-slate-600"}`}>
                    {t.revised_end_date}
                  </span>
                  {isDelayed && <span className="w-1.5 h-1.5 rounded-full bg-red-400"></span>}
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
