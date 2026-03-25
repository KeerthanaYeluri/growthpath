import { useState, useEffect } from "react";
import { apiFetch } from "@/lib/api";
import LoadingSpinner from "@/components/common/LoadingSpinner";

interface QuickAssessmentScreenProps {
  onComplete: (results: any) => void;
  onSkip: () => void;
}

export default function QuickAssessmentScreen({ onComplete, onSkip }: QuickAssessmentScreenProps) {
  const [loading, setLoading] = useState(true);
  const [questions, setQuestions] = useState<any[]>([]);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [currentIdx, setCurrentIdx] = useState(0);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [submitting, setSubmitting] = useState(false);
  const [results, setResults] = useState<any>(null);
  const [error, setError] = useState("");
  const [assessmentMeta, setAssessmentMeta] = useState<any>({});

  useEffect(() => {
    apiFetch("/quick-assessment/start", { method: "POST" })
      .then((r) => r.json())
      .then((data) => {
        if (data.error) {
          setError(data.error);
          setLoading(false);
          return;
        }
        setSessionId(data.session_id);
        setQuestions(data.questions);
        setAssessmentMeta({ company: data.company, role: data.role, level: data.level });
        setLoading(false);
      })
      .catch(() => {
        setError("Cannot connect to server");
        setLoading(false);
      });
  }, []);

  const currentQ = questions[currentIdx];
  const progress = questions.length > 0 ? Math.round((currentIdx / questions.length) * 100) : 0;

  const handleAnswer = (text: string) => {
    setAnswers((prev) => ({ ...prev, [currentQ.id]: text }));
  };

  const handleNext = () => {
    if (currentIdx < questions.length - 1) {
      setCurrentIdx(currentIdx + 1);
    }
  };

  const handlePrev = () => {
    if (currentIdx > 0) setCurrentIdx(currentIdx - 1);
  };

  const handleSubmit = async () => {
    setSubmitting(true);
    const answerList = questions.map((q: any) => ({
      question_id: q.id,
      answer_text: answers[q.id] || "",
    }));
    try {
      const res = await apiFetch("/quick-assessment/submit", {
        method: "POST",
        body: JSON.stringify({ session_id: sessionId, answers: answerList }),
      });
      const data = await res.json();
      if (data.error) {
        setError(data.error);
        setSubmitting(false);
        return;
      }
      setResults(data);
    } catch {
      setError("Failed to submit assessment");
    }
    setSubmitting(false);
  };

  if (loading) return <LoadingSpinner />;
  if (error && !questions.length)
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <div className="glass-strong rounded-2xl p-8 max-w-md text-center">
          <p className="text-red-400 mb-4">{error}</p>
          <button onClick={onSkip} className="px-6 py-2 rounded-xl text-sm bg-slate-700 hover:bg-slate-600 text-white">
            Skip to Dashboard
          </button>
        </div>
      </div>
    );

  // Results screen
  if (results) {
    const elo = results.elo;
    const readiness = results.readiness;
    const scorecard = results.scorecard;
    return (
      <div className="min-h-screen flex items-center justify-center p-4 animate-fade-in">
        <div className="glass-strong rounded-2xl p-8 max-w-2xl w-full glow">
          <div className="text-center mb-6">
            <h2 className="text-2xl font-bold mb-2">Quick Assessment Complete</h2>
            <p className="text-slate-400 text-sm">Here's your starting position</p>
          </div>

          {/* ELO Result */}
          <div className="glass rounded-xl p-6 mb-6 text-center">
            <p className="text-slate-500 text-xs uppercase tracking-wider mb-1">Your ELO Rating</p>
            <p className="text-5xl font-black text-indigo-400 mb-1">{elo.after}</p>
            <p className="text-sm mb-2">
              <span
                className={`px-3 py-1 rounded-full ${readiness.is_ready ? "bg-emerald-500/20 text-emerald-300" : "bg-amber-500/20 text-amber-300"}`}
              >
                {readiness.readiness?.label || "Getting There"}
              </span>
            </p>
            <div className="w-full bg-slate-800/50 rounded-full h-3 mt-3 mb-2">
              <div
                className="h-3 rounded-full bg-gradient-to-r from-indigo-500 to-purple-500 transition-all"
                style={{ width: `${Math.min(100, (elo.after / (readiness.hiring_bar || 1800)) * 100)}%` }}
              ></div>
            </div>
            <div className="flex justify-between text-xs text-slate-500">
              <span>You: {elo.after}</span>
              <span>
                {assessmentMeta.company?.charAt(0).toUpperCase() + assessmentMeta.company?.slice(1)} Bar:{" "}
                {readiness.hiring_bar}
              </span>
            </div>
            {readiness.gap > 0 && (
              <p className="text-amber-400 text-sm mt-2 font-medium">{readiness.gap} points to interview ready</p>
            )}
          </div>

          {/* Round Scores */}
          <div className="glass rounded-xl p-4 mb-6">
            <h3 className="text-white text-sm font-semibold mb-3 uppercase tracking-wider">Score by Round</h3>
            <div className="space-y-2">
              {Object.entries(scorecard?.per_round || {}).map(([round, score]: [string, any]) => (
                <div key={round} className="flex items-center gap-3">
                  <span className="text-slate-400 text-xs w-28 capitalize">{round.replace(/_/g, " ")}</span>
                  <div className="flex-1 bg-slate-800/50 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full transition-all ${score >= 70 ? "bg-emerald-500" : score >= 40 ? "bg-amber-500" : "bg-red-500"}`}
                      style={{ width: `${score}%` }}
                    ></div>
                  </div>
                  <span className="text-slate-300 text-xs w-8 text-right">{score}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Focus Areas */}
          {scorecard?.recommended_focus?.length > 0 && (
            <div className="glass rounded-xl p-4 mb-6">
              <h3 className="text-red-400 text-sm font-semibold mb-2 uppercase tracking-wider">Focus Areas</h3>
              <div className="flex flex-wrap gap-2">
                {scorecard.recommended_focus.map((f: string) => (
                  <span key={f} className="px-3 py-1 rounded-full bg-red-500/20 text-red-300 text-xs">
                    {f}
                  </span>
                ))}
              </div>
            </div>
          )}

          <button
            onClick={() => onComplete(results)}
            className="w-full py-3 rounded-xl font-semibold text-sm bg-indigo-600 hover:bg-indigo-500 text-white shadow-lg shadow-indigo-500/20 transition-all"
          >
            Go to Dashboard
          </button>
        </div>
      </div>
    );
  }

  // Question screen
  return (
    <div className="min-h-screen flex items-center justify-center p-4 animate-fade-in">
      <div className="glass-strong rounded-2xl p-8 max-w-2xl w-full glow">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-lg font-bold">Quick Assessment</h2>
            <p className="text-slate-500 text-xs capitalize">
              {assessmentMeta.company} | {(assessmentMeta.role || "").replace(/_/g, " ")} | {assessmentMeta.level}
            </p>
          </div>
          <span className="text-slate-400 text-sm">
            {currentIdx + 1} / {questions.length}
          </span>
        </div>

        {/* Progress bar */}
        <div className="w-full bg-slate-800/50 rounded-full h-1.5 mb-6">
          <div className="h-1.5 rounded-full bg-indigo-500 transition-all" style={{ width: `${progress}%` }}></div>
        </div>

        {currentQ && (
          <div>
            {/* Question metadata */}
            <div className="flex gap-2 mb-3">
              <span className="px-2 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 text-[10px] uppercase">
                {currentQ.round_type?.replace(/_/g, " ")}
              </span>
              <span className="px-2 py-0.5 rounded-full bg-slate-500/20 text-slate-400 text-[10px]">
                {currentQ.pattern}
              </span>
              <span
                className={`px-2 py-0.5 rounded-full text-[10px] ${currentQ.difficulty === "hard" ? "bg-red-500/20 text-red-300" : currentQ.difficulty === "easy" ? "bg-emerald-500/20 text-emerald-300" : "bg-amber-500/20 text-amber-300"}`}
              >
                {currentQ.difficulty}
              </span>
              <span className="px-2 py-0.5 rounded-full bg-purple-500/20 text-purple-300 text-[10px]">
                {currentQ.answer_mode}
              </span>
            </div>

            {/* Question */}
            <p className="text-white text-base mb-4 leading-relaxed">{currentQ.question}</p>

            {/* Answer input */}
            <textarea
              value={answers[currentQ.id] || ""}
              onChange={(e) => handleAnswer(e.target.value)}
              placeholder="Type your answer here... Be thorough -- explain your thinking process, consider trade-offs, and structure your response."
              rows={8}
              className="w-full bg-slate-800/60 border border-slate-700/50 rounded-xl px-4 py-3 text-white text-sm placeholder-slate-600 focus:border-indigo-500/50 transition-all resize-none"
            />
            <p className="text-slate-600 text-[10px] mt-1 text-right">
              {(answers[currentQ.id] || "").split(/\s+/).filter(Boolean).length} words
            </p>

            {/* Navigation */}
            <div className="flex items-center justify-between mt-4">
              <button
                onClick={handlePrev}
                disabled={currentIdx === 0}
                className="px-4 py-2 rounded-xl text-sm text-slate-400 hover:text-white disabled:opacity-30 transition-all"
              >
                Previous
              </button>
              <div className="flex gap-2">
                {currentIdx < questions.length - 1 ? (
                  <button
                    onClick={handleNext}
                    className="px-6 py-2 rounded-xl text-sm font-medium bg-indigo-600 hover:bg-indigo-500 text-white transition-all"
                  >
                    Next
                  </button>
                ) : (
                  <button
                    onClick={handleSubmit}
                    disabled={submitting}
                    className="px-6 py-2 rounded-xl text-sm font-medium bg-emerald-600 hover:bg-emerald-500 text-white transition-all disabled:opacity-50"
                  >
                    {submitting ? "Evaluating..." : "Submit Assessment"}
                  </button>
                )}
              </div>
            </div>
          </div>
        )}

        {error && <p className="text-red-400 text-sm mt-3">{error}</p>}
      </div>
    </div>
  );
}
