import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { CheckCircle, AlertCircle, Star, Eye } from "lucide-react";
import { apiFetch } from "@/lib/api";
import LoadingSpinner from "@/components/common/LoadingSpinner";

function Stars({ rating, size = "sm" }: { rating: number; size?: string }) {
  const sz = size === "lg" ? "w-5 h-5" : "w-3.5 h-3.5";
  return (
    <div className="flex gap-0.5">
      {[1, 2, 3, 4, 5].map((i) => (
        <Star key={i} className={`${sz} ${i <= rating ? "text-amber-400 fill-amber-400" : "text-slate-700"}`} />
      ))}
    </div>
  );
}

interface TopicAssessmentScreenProps {
  topicId: string;
  topicTitle: string;
  onComplete: () => void;
  onNavigate: (screen: string, params?: any) => void;
}

export default function TopicAssessmentScreen({ topicId, topicTitle, onComplete, onNavigate }: TopicAssessmentScreenProps) {
  const [questions, setQuestions] = useState<any[]>([]);
  const [currentIdx, setCurrentIdx] = useState(0);
  const [answer, setAnswer] = useState("");
  const [result, setResult] = useState<any>(null);
  const [showAnswer, setShowAnswer] = useState(false);
  const [modelAnswer, setModelAnswer] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [loading, setLoading] = useState(true);
  const [quotaError, setQuotaError] = useState(false);
  const [completed, setCompleted] = useState(false);
  const [finalResult, setFinalResult] = useState<any>(null);

  useEffect(() => {
    apiFetch(`/assessment/topic/${topicId}/questions`)
      .then((r) => {
        if (r.status === 429) {
          setQuotaError(true);
          setLoading(false);
          return r.json();
        }
        return r.json();
      })
      .then((data) => {
        if (data.questions) setQuestions(data.questions);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [topicId]);

  const handleShowAnswer = async () => {
    const res = await apiFetch(`/assessment/topic/${topicId}/show-answer`, {
      method: "POST",
      body: JSON.stringify({ question_id: questions[currentIdx].id }),
    });
    const data = await res.json();
    setModelAnswer(data.model_answer);
    setShowAnswer(true);
  };

  const handleSubmit = async () => {
    if (submitting) return;
    setSubmitting(true);
    try {
      const res = await apiFetch(`/assessment/topic/${topicId}/submit`, {
        method: "POST",
        body: JSON.stringify({ question_id: questions[currentIdx].id, answer, show_answer_used: showAnswer }),
      });
      if (res.status === 429) {
        setQuotaError(true);
        setSubmitting(false);
        return;
      }
      const data = await res.json();
      setResult(data);
    } catch {}
    setSubmitting(false);
  };

  const handleNext = () => {
    setAnswer("");
    setResult(null);
    setShowAnswer(false);
    setModelAnswer("");
    if (currentIdx < questions.length - 1) {
      setCurrentIdx(currentIdx + 1);
    } else {
      apiFetch(`/assessment/topic/${topicId}/complete`, { method: "POST" })
        .then((r) => r.json())
        .then((data) => {
          setFinalResult(data);
          setCompleted(true);
        });
    }
  };

  if (loading) return <LoadingSpinner />;

  if (quotaError) {
    return (
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="max-w-lg mx-auto p-6 text-center">
        <div className="glass rounded-xl p-8">
          <div className="w-16 h-16 rounded-full bg-amber-500/20 mx-auto mb-4 flex items-center justify-center">
            <AlertCircle className="w-8 h-8 text-amber-400" />
          </div>
          <h2 className="text-xl font-bold mb-2">Daily Limit Reached</h2>
          <p className="text-slate-400 text-sm mb-4">You've used all your questions for today. Come back tomorrow!</p>
          <button onClick={() => onNavigate("dashboard")} className="px-5 py-2 rounded-xl text-sm font-medium bg-indigo-600 text-white">
            Back to Dashboard
          </button>
        </div>
      </motion.div>
    );
  }

  if (completed && finalResult) {
    return (
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="max-w-lg mx-auto p-6 text-center">
        <div className="glass-strong rounded-2xl p-8 glow-green">
          <div className="w-16 h-16 rounded-full bg-emerald-500/20 mx-auto mb-4 flex items-center justify-center">
            <CheckCircle className="w-8 h-8 text-emerald-400" />
          </div>
          <h2 className="text-2xl font-bold mb-2">Assessment Complete!</h2>
          <p className="text-slate-400 text-sm mb-4">{topicTitle}</p>
          <div className="flex justify-center mb-4">
            <Stars rating={finalResult.final_rating} size="lg" />
          </div>
          <div className="grid grid-cols-2 gap-3 mb-6">
            <div className="glass rounded-lg p-3">
              <p className="text-slate-500 text-xs">Avg Score</p>
              <p className="text-2xl font-bold text-indigo-400">{finalResult.average_score}</p>
            </div>
            <div className="glass rounded-lg p-3">
              <p className="text-slate-500 text-xs">Questions</p>
              <p className="text-2xl font-bold text-emerald-400">{finalResult.questions_answered}</p>
            </div>
          </div>
          <div className="flex gap-3 justify-center">
            <button onClick={() => onNavigate("learning")} className="px-5 py-2 rounded-xl text-sm font-medium bg-indigo-600 text-white">
              Continue Learning
            </button>
            <button onClick={() => onNavigate("dashboard")} className="px-5 py-2 rounded-xl text-sm text-slate-400 hover:text-white">
              Dashboard
            </button>
          </div>
        </div>
      </motion.div>
    );
  }

  const q = questions[currentIdx];
  if (!q) return <div className="text-center py-12 text-slate-500">No questions available</div>;

  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="max-w-3xl mx-auto p-4 md:p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h1 className="text-lg font-bold">{topicTitle} Assessment</h1>
          <p className="text-slate-500 text-xs">
            Question {currentIdx + 1} of {questions.length}
          </p>
        </div>
        <button onClick={() => onNavigate("learning")} className="text-slate-500 hover:text-slate-300 text-xs">
          Exit
        </button>
      </div>

      {/* Progress */}
      <div className="w-full bg-slate-800/50 rounded-full h-1.5 mb-6">
        <div
          className="bg-indigo-500 h-1.5 rounded-full transition-all"
          style={{ width: `${((currentIdx + 1) / questions.length) * 100}%` }}
        ></div>
      </div>

      {/* Question */}
      <div className="glass-strong rounded-2xl p-6 mb-4 glow">
        <p className="text-slate-200 text-base leading-relaxed">{q.question}</p>
      </div>

      {!result ? (
        <>
          {/* Answer input */}
          <div className="glass rounded-2xl p-1 mb-4">
            <textarea
              value={answer}
              onChange={(e) => setAnswer(e.target.value)}
              placeholder="Type your answer here..."
              className="w-full min-h-[120px] bg-transparent rounded-xl px-5 py-4 text-white placeholder-slate-600 resize-none text-sm leading-relaxed"
            />
          </div>

          {/* Show Answer */}
          {showAnswer && (
            <div className="glass rounded-xl p-4 mb-4 border border-amber-500/20 fade-in">
              <p className="text-amber-400 text-xs font-semibold mb-1 uppercase tracking-wider">Model Answer (50% penalty applied)</p>
              <p className="text-slate-300 text-sm leading-relaxed">{modelAnswer}</p>
            </div>
          )}

          {/* Actions */}
          <div className="flex items-center justify-between">
            <button
              onClick={handleShowAnswer}
              disabled={showAnswer}
              className="px-4 py-2 rounded-xl text-xs font-medium bg-amber-600/20 text-amber-400 hover:bg-amber-600/30 border border-amber-500/20 transition-all disabled:opacity-30 flex items-center gap-1"
            >
              <Eye className="w-3 h-3" />
              {showAnswer ? "Answer Shown (-50%)" : "Show Answer"}
            </button>
            <div className="flex items-center gap-2">
              <span className="text-slate-600 text-xs">{answer.split(/\s+/).filter(Boolean).length} words</span>
              <button
                onClick={handleSubmit}
                disabled={submitting || !answer.trim()}
                className="px-6 py-2.5 rounded-xl text-sm font-medium bg-indigo-600 hover:bg-indigo-500 text-white transition-all disabled:opacity-30"
              >
                {submitting ? "Submitting..." : "Submit"}
              </button>
            </div>
          </div>
        </>
      ) : (
        /* Result view */
        <div className="fade-in">
          <div className="glass rounded-xl p-5 mb-4">
            <div className="flex items-center justify-between mb-3">
              <span className="text-white text-sm font-semibold">Your Score</span>
              <div className="flex items-center gap-2">
                <span
                  className={`text-2xl font-bold ${
                    result.score.total_score >= 70
                      ? "text-emerald-400"
                      : result.score.total_score >= 40
                      ? "text-amber-400"
                      : "text-red-400"
                  }`}
                >
                  {result.score.total_score}/100
                </span>
                <Stars rating={result.rating} />
              </div>
            </div>
            {result.score.penalty_applied && <p className="text-amber-400 text-xs mb-2">Penalty: {result.score.penalty_applied}</p>}
            <div className="grid grid-cols-3 gap-2 mb-3">
              <div className="bg-slate-800/30 rounded-lg p-2 text-center">
                <p className="text-slate-500 text-[10px]">Keywords</p>
                <p className="text-white text-sm font-bold">{result.score.keyword_score}%</p>
              </div>
              <div className="bg-slate-800/30 rounded-lg p-2 text-center">
                <p className="text-slate-500 text-[10px]">Detail</p>
                <p className="text-white text-sm font-bold">{result.score.detail_score}%</p>
              </div>
              <div className="bg-slate-800/30 rounded-lg p-2 text-center">
                <p className="text-slate-500 text-[10px]">Relevance</p>
                <p className="text-white text-sm font-bold">{result.score.relevance_score}%</p>
              </div>
            </div>
            <p className="text-slate-400 text-xs">{result.score.feedback}</p>
          </div>

          {/* Correct answer */}
          <div className="glass rounded-xl p-4 mb-4 border border-emerald-500/20">
            <p className="text-emerald-400 text-xs font-semibold mb-1 uppercase tracking-wider">Correct Answer</p>
            <p className="text-slate-300 text-sm leading-relaxed">{result.correct_answer}</p>
          </div>

          <div className="text-right">
            <button
              onClick={handleNext}
              className="px-6 py-2.5 rounded-xl text-sm font-medium bg-indigo-600 hover:bg-indigo-500 text-white transition-all"
            >
              {currentIdx < questions.length - 1 ? "Next Question" : "Finish Assessment"}
            </button>
          </div>
        </div>
      )}
    </motion.div>
  );
}
