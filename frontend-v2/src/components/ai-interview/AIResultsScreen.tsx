import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Check, AlertTriangle, ArrowLeft } from "lucide-react";
import { apiFetch } from "@/lib/api";
import LoadingSpinner from "@/components/common/LoadingSpinner";

interface AIResultsScreenProps {
  interviewId: string;
  onNavigate: (screen: string, params?: any) => void;
}

export default function AIResultsScreen({ interviewId, onNavigate }: AIResultsScreenProps) {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiFetch(`/ai-interview/${interviewId}/results`)
      .then((r) => r.json())
      .then((d) => {
        setData(d);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [interviewId]);

  if (loading) return <LoadingSpinner />;
  if (!data) return <div className="text-center py-20 text-slate-400">No results found</div>;

  const result = data.result;
  const transcript = data.transcript || [];
  const interview = data.interview || {};

  const recColors: Record<string, string> = {
    strong_hire: "text-emerald-400 bg-emerald-400/10",
    hire: "text-green-400 bg-green-400/10",
    maybe: "text-amber-400 bg-amber-400/10",
    no_hire: "text-red-400 bg-red-400/10",
  };
  const recLabels: Record<string, string> = {
    strong_hire: "Strong Hire",
    hire: "Hire",
    maybe: "Maybe",
    no_hire: "Not Recommended",
  };
  const dimColors: Record<string, string> = {
    relevance: "bg-blue-500",
    depth: "bg-purple-500",
    communication: "bg-emerald-500",
    examples: "bg-amber-500",
  };

  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="max-w-4xl mx-auto px-4 py-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-white">Interview Results</h1>
          <p className="text-slate-400 text-sm">
            {interview.interest_area} | {interview.job_role}
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => onNavigate("ai_interview")}
            className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg text-xs font-medium transition-all flex items-center gap-1"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            Back to Interviews
          </button>
          <button
            onClick={() => onNavigate("dashboard")}
            className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-medium transition-all flex items-center gap-1"
          >
            Dashboard
          </button>
        </div>
      </div>

      {result && (
        <>
          {/* Overall Score Card */}
          <div className="glass rounded-2xl p-6 mb-6 glow">
            <div className="flex items-center justify-between mb-4">
              <div>
                <p className="text-slate-400 text-sm">Overall Score</p>
                <p className="text-4xl font-bold text-white">
                  {result.overall_score}
                  <span className="text-lg text-slate-500">/100</span>
                </p>
              </div>
              <span className={`px-4 py-2 rounded-xl text-sm font-bold ${recColors[result.recommendation] || "text-slate-400 bg-slate-400/10"}`}>
                {recLabels[result.recommendation] || result.recommendation}
              </span>
            </div>

            {/* Category Scores */}
            {result.category_scores && (
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
                {Object.entries(result.category_scores).map(([cat, score]: any) => (
                  <div key={cat} className="glass-strong rounded-xl p-3 text-center">
                    <p className="text-slate-500 text-xs capitalize">{cat}</p>
                    <p className="text-white text-lg font-bold">{score}</p>
                  </div>
                ))}
              </div>
            )}

            {/* Summary */}
            {result.summary && <p className="text-slate-300 text-sm leading-relaxed">{result.summary}</p>}
          </div>

          {/* Strengths & Improvements */}
          <div className="grid md:grid-cols-2 gap-4 mb-6">
            <div className="glass rounded-2xl p-5">
              <h3 className="text-emerald-400 text-sm font-semibold mb-3 flex items-center gap-2">
                <Check className="w-4 h-4" />
                Strengths
              </h3>
              <ul className="space-y-2">
                {(result.top_strengths || []).map((s: string, i: number) => (
                  <li key={i} className="text-slate-300 text-sm flex items-start gap-2">
                    <span className="text-emerald-500 mt-1">+</span> {s}
                  </li>
                ))}
              </ul>
            </div>
            <div className="glass rounded-2xl p-5">
              <h3 className="text-amber-400 text-sm font-semibold mb-3 flex items-center gap-2">
                <AlertTriangle className="w-4 h-4" />
                Areas to Improve
              </h3>
              <ul className="space-y-2">
                {(result.improvement_areas || []).map((s: string, i: number) => (
                  <li key={i} className="text-slate-300 text-sm flex items-start gap-2">
                    <span className="text-amber-500 mt-1">!</span> {s}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </>
      )}

      {/* Transcript with Evaluations */}
      <div className="glass rounded-2xl p-6">
        <h3 className="text-white text-lg font-semibold mb-4">Interview Transcript</h3>
        <div className="space-y-6">
          {transcript.map((ex: any, i: number) => (
            <div key={i} className="glass-strong rounded-xl p-4">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-indigo-400 text-xs font-bold">Q{ex.sequence + 1}</span>
                <span
                  className={`px-2 py-0.5 rounded-full text-xs ${
                    ex.category === "technical"
                      ? "bg-blue-500/20 text-blue-300"
                      : ex.category === "behavioral"
                      ? "bg-green-500/20 text-green-300"
                      : ex.category === "situational"
                      ? "bg-amber-500/20 text-amber-300"
                      : "bg-purple-500/20 text-purple-300"
                  }`}
                >
                  {ex.category}
                </span>
              </div>
              <p className="text-white text-sm font-medium mb-2">{ex.question}</p>
              <p className="text-slate-400 text-sm mb-3">
                {ex.answer || <span className="italic text-slate-600">No answer</span>}
              </p>

              {ex.evaluation && (
                <div className="border-t border-slate-700/50 pt-3 mt-3">
                  <div className="flex gap-3 mb-2">
                    {["relevance", "depth", "communication", "examples"].map((dim) => (
                      <div key={dim} className="flex items-center gap-1.5">
                        <div className={`w-2 h-2 rounded-full ${dimColors[dim]}`} />
                        <span className="text-slate-500 text-xs capitalize">{dim}</span>
                        <span className="text-white text-xs font-bold">{ex.evaluation[dim + "_score"]}/10</span>
                      </div>
                    ))}
                  </div>
                  {ex.evaluation.strengths && ex.evaluation.strengths.length > 0 && (
                    <p className="text-emerald-400/70 text-xs mt-1">
                      + {(Array.isArray(ex.evaluation.strengths) ? ex.evaluation.strengths : [ex.evaluation.strengths]).join(", ")}
                    </p>
                  )}
                  {ex.evaluation.suggestions && ex.evaluation.suggestions.length > 0 && (
                    <p className="text-amber-400/70 text-xs mt-1">
                      Tip: {(Array.isArray(ex.evaluation.suggestions) ? ex.evaluation.suggestions : [ex.evaluation.suggestions]).join(", ")}
                    </p>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </motion.div>
  );
}
