import { useState } from "react";
import { apiFetch } from "@/lib/api";

interface MockResultsViewProps {
  elo: any;
  sc: any;
  readiness: any;
  mockData: any;
  sessionId: string;
  onNavigate: (screen: string) => void;
}

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
    <div className="max-w-3xl mx-auto p-4 md:p-6 animate-fade-in">
      <div className="text-center mb-6">
        <h2 className="text-2xl font-bold mb-1">Mock Interview Complete</h2>
        <p className="text-slate-400 text-sm capitalize">
          {mockData?.company} | {(mockData?.role || "").replace(/_/g, " ")} | {mockData?.level}
        </p>
      </div>

      {/* ELO Change */}
      <div className="glass-strong rounded-2xl p-6 mb-6 text-center glow">
        <p className="text-slate-500 text-xs uppercase mb-1">ELO Rating</p>
        <div className="flex items-center justify-center gap-3">
          <span className="text-slate-500 text-xl">{elo?.before}</span>
          <span className="text-2xl">{"->"}</span>
          <span className="text-4xl font-black text-indigo-400">{elo?.after}</span>
          <span className={`text-sm font-bold ${(elo?.delta || 0) >= 0 ? "text-emerald-400" : "text-red-400"}`}>
            {(elo?.delta || 0) >= 0 ? "+" : ""}
            {elo?.delta}
          </span>
        </div>
        <p className="mt-2">
          <span
            className={`px-3 py-1 rounded-full text-xs ${readiness?.is_ready ? "bg-emerald-500/20 text-emerald-300" : "bg-amber-500/20 text-amber-300"}`}
          >
            {readiness?.readiness?.label || "--"}
          </span>
        </p>
        {(readiness?.gap || 0) > 0 && <p className="text-slate-500 text-xs mt-1">{readiness.gap} points to go</p>}
      </div>

      {/* Round Scores */}
      <div className="glass rounded-xl p-5 mb-6">
        <h3 className="text-white text-sm font-semibold mb-3 uppercase tracking-wider">Round Scores</h3>
        <div className="space-y-3">
          {(mockData?.rounds || []).map((rnd: any) => {
            const score = sc?.per_round?.[rnd.round_type] || 0;
            return (
              <div key={rnd.round_type} className="flex items-center gap-3">
                <span className="text-slate-400 text-xs w-32">{rnd.label}</span>
                <div className="flex-1 bg-slate-800/50 rounded-full h-2.5">
                  <div
                    className={`h-2.5 rounded-full transition-all ${score >= 70 ? "bg-emerald-500" : score >= 40 ? "bg-amber-500" : "bg-red-500"}`}
                    style={{ width: `${score}%` }}
                  ></div>
                </div>
                <span className="text-slate-300 text-sm w-10 text-right font-medium">{score}</span>
                {rnd.is_critical && (
                  <span className="text-[9px] px-1.5 py-0.5 rounded bg-red-500/20 text-red-300">critical</span>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Focus Areas */}
      {sc?.recommended_focus?.length > 0 && (
        <div className="glass rounded-xl p-4 mb-6">
          <h3 className="text-red-400 text-sm font-semibold mb-2 uppercase tracking-wider">Focus Areas</h3>
          <div className="flex flex-wrap gap-2">
            {sc.recommended_focus.map((f: string) => (
              <span key={f} className="px-3 py-1 rounded-full bg-red-500/20 text-red-300 text-xs">
                {f}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Action Buttons: Rubric Reveal + Hiring Committee */}
      <div className="grid grid-cols-2 gap-3 mb-6">
        <button
          onClick={loadRubrics}
          disabled={loadingRubric}
          className="glass rounded-xl p-4 text-center hover:bg-white/[0.04] transition-all cursor-pointer"
        >
          <p className="text-purple-400 text-sm font-semibold">
            {loadingRubric ? "Loading..." : showRubric ? "Hide Rubric" : "Rubric Reveal"}
          </p>
          <p className="text-slate-500 text-[10px] mt-1">See what interviewer was evaluating</p>
        </button>
        <button
          onClick={loadCommittee}
          disabled={loadingCommittee}
          className="glass rounded-xl p-4 text-center hover:bg-white/[0.04] transition-all cursor-pointer"
        >
          <p className="text-amber-400 text-sm font-semibold">
            {loadingCommittee ? "Loading..." : showCommittee ? "Hide Committee" : "Hiring Committee"}
          </p>
          <p className="text-slate-500 text-[10px] mt-1">See HIRE / NO HIRE verdict</p>
        </button>
      </div>

      {/* Rubric Reveal Panel */}
      {showRubric && rubrics && (
        <div className="glass rounded-xl p-5 mb-6 animate-fade-in">
          <h3 className="text-purple-300 text-sm font-semibold mb-4 uppercase tracking-wider">
            Rubric Reveal -- What the Interviewer Was Looking For
          </h3>
          <div className="space-y-4 max-h-96 overflow-y-auto">
            {rubrics.map((r: any, i: number) => (
              <div key={i} className="bg-slate-800/40 rounded-lg p-3">
                <div className="flex items-center justify-between mb-2">
                  <p className="text-white text-xs font-medium truncate flex-1">{r.question}</p>
                  <span className="text-slate-400 text-[10px] ml-2">
                    {r.covered_count}/{r.total_count} covered
                  </span>
                </div>
                <div className="space-y-1">
                  {r.rubric_points.map((p: any, j: number) => (
                    <div key={j} className="flex items-center gap-2">
                      <span className={`text-sm ${p.covered ? "text-emerald-400" : "text-red-400"}`}>
                        {p.covered ? "\u2713" : "\u2717"}
                      </span>
                      <span className={`text-xs ${p.covered ? "text-slate-300" : "text-slate-500"}`}>{p.point}</span>
                    </div>
                  ))}
                </div>
                {r.keywords_missed.length > 0 && (
                  <p className="text-slate-500 text-[10px] mt-2">Missed keywords: {r.keywords_missed.join(", ")}</p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Hiring Committee Panel */}
      {showCommittee && committee && (
        <div className="glass rounded-xl p-5 mb-6 animate-fade-in">
          {/* Verdict */}
          <div
            className={`text-center p-4 rounded-xl mb-4 ${committee.verdict.includes("NO") ? "bg-red-500/10 border border-red-500/20" : "bg-emerald-500/10 border border-emerald-500/20"}`}
          >
            <p
              className={`text-xl font-bold ${committee.verdict.includes("NO") ? "text-red-400" : "text-emerald-400"}`}
            >
              {committee.verdict_label}
            </p>
            {committee.veto_applied && <p className="text-red-300 text-xs mt-1">Veto applied on critical round</p>}
            <p className="text-slate-400 text-xs mt-2">{committee.recommendation}</p>
          </div>
          {/* Interviewers */}
          <h3 className="text-amber-300 text-sm font-semibold mb-3 uppercase tracking-wider">Committee Members</h3>
          <div className="space-y-3">
            {committee.interviewers.map((inv: any, i: number) => (
              <div key={i} className="bg-slate-800/40 rounded-lg p-3">
                <div className="flex items-center justify-between mb-1">
                  <div>
                    <span className="text-white text-xs font-medium">{inv.name}</span>
                    <span className="text-slate-500 text-[10px] ml-2">{inv.title}</span>
                  </div>
                  <span
                    className={`px-2 py-0.5 rounded-full text-[10px] font-semibold ${inv.vote.includes("NO") ? "bg-red-500/20 text-red-300" : "bg-emerald-500/20 text-emerald-300"}`}
                  >
                    {inv.vote.replace(/_/g, " ")}
                  </span>
                </div>
                <p className="text-slate-500 text-[10px] mb-1">
                  Evaluated: {inv.assigned_round_labels.join(", ")}
                </p>
                <p className="text-slate-400 text-xs italic">"{inv.reasoning}"</p>
                {inv.quotes.map((q: string, j: number) => (
                  <p key={j} className="text-slate-500 text-[10px] mt-1">
                    -- {q}
                  </p>
                ))}
              </div>
            ))}
          </div>
        </div>
      )}

      <button
        onClick={() => onNavigate("dashboard")}
        className="w-full py-3 rounded-xl font-semibold text-sm bg-indigo-600 hover:bg-indigo-500 text-white transition-all"
      >
        Back to Dashboard
      </button>
    </div>
  );
}
