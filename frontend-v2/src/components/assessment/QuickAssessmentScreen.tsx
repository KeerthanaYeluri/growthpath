import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Brain,
  ChevronRight,
  ChevronLeft,
  Send,
  Clock,
  Tag,
  BarChart,
  Target,
  Trophy,
  AlertTriangle,
  Sparkles,
} from "lucide-react";
import { GlassCard, GlassCardHeader, GlassCardTitle, GlassCardContent, GlassCardFooter } from "@/components/ui/glass-card";
import { cn } from "@/lib/utils";
import { apiFetch } from "@/lib/api";
import LoadingSpinner from "@/components/common/LoadingSpinner";

interface QuickAssessmentScreenProps {
  onComplete: (results: any) => void;
  onSkip: () => void;
}

const slideVariants = {
  enterRight: { x: 60, opacity: 0 },
  enterLeft: { x: -60, opacity: 0 },
  center: { x: 0, opacity: 1 },
  exitLeft: { x: -60, opacity: 0 },
  exitRight: { x: 60, opacity: 0 },
};

export default function QuickAssessmentScreen({ onComplete, onSkip }: QuickAssessmentScreenProps) {
  const [started, setStarted] = useState(false);
  const [loading, setLoading] = useState(false);
  const [questions, setQuestions] = useState<any[]>([]);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [currentIdx, setCurrentIdx] = useState(0);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [submitting, setSubmitting] = useState(false);
  const [results, setResults] = useState<any>(null);
  const [error, setError] = useState("");
  const [assessmentMeta, setAssessmentMeta] = useState<any>({});
  const [direction, setDirection] = useState<"right" | "left">("right");

  const beginAssessment = () => {
    setStarted(true);
    setLoading(true);
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
  };

  const currentQ = questions[currentIdx];
  const progress = questions.length > 0 ? Math.round(((currentIdx + 1) / questions.length) * 100) : 0;

  const handleAnswer = (text: string) => {
    setAnswers((prev) => ({ ...prev, [currentQ.id]: text }));
  };

  const handleNext = () => {
    if (currentIdx < questions.length - 1) {
      setDirection("right");
      setCurrentIdx(currentIdx + 1);
    }
  };

  const handlePrev = () => {
    if (currentIdx > 0) {
      setDirection("left");
      setCurrentIdx(currentIdx - 1);
    }
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

  const wordCount = (answers[currentQ?.id] || "").split(/\s+/).filter(Boolean).length;

  // Intro screen before assessment starts
  if (!started)
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="glass-strong rounded-2xl p-8 max-w-lg text-center"
        >
          <Brain className="w-12 h-12 text-indigo-400 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-white mb-2">Quick Assessment</h2>
          <p className="text-slate-400 text-sm mb-4">
            This short assessment calibrates your starting ELO rating and creates a personalized learning path based on your strengths and weaknesses.
          </p>
          <div className="glass rounded-xl p-4 mb-6 text-left space-y-2">
            <div className="flex items-center gap-2 text-slate-300 text-xs">
              <Target className="w-3.5 h-3.5 text-indigo-400 flex-shrink-0" />
              <span><strong>10 questions</strong> — mostly specific to your selected role</span>
            </div>
            <div className="flex items-center gap-2 text-slate-300 text-xs">
              <Clock className="w-3.5 h-3.5 text-indigo-400 flex-shrink-0" />
              <span><strong>~10 minutes</strong> — take your time, no rush</span>
            </div>
            <div className="flex items-center gap-2 text-slate-300 text-xs">
              <BarChart className="w-3.5 h-3.5 text-indigo-400 flex-shrink-0" />
              <span><strong>ELO calibrated</strong> — your score determines your starting rating</span>
            </div>
            <div className="flex items-center gap-2 text-slate-300 text-xs">
              <Sparkles className="w-3.5 h-3.5 text-indigo-400 flex-shrink-0" />
              <span><strong>Learning path generated</strong> — weak areas become top priority</span>
            </div>
          </div>
          <p className="text-slate-500 text-[10px] mb-4">
            You can retake this assessment anytime from the Dashboard to recalibrate.
          </p>
          <div className="flex gap-3 justify-center">
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={onSkip}
              className="px-6 py-3 rounded-xl text-sm font-medium bg-slate-700 hover:bg-slate-600 text-white transition-all"
            >
              Skip for Now
            </motion.button>
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={beginAssessment}
              className="px-8 py-3 rounded-xl text-sm font-semibold bg-gradient-to-r from-indigo-600 to-indigo-500 hover:from-indigo-500 hover:to-indigo-400 text-white shadow-lg shadow-indigo-500/20 transition-all flex items-center gap-2"
            >
              <Brain className="w-4 h-4" />
              Begin Assessment
            </motion.button>
          </div>
        </motion.div>
      </div>
    );

  if (loading)
    return (
      <div className="min-h-screen flex flex-col items-center justify-center p-4 gap-4">
        <LoadingSpinner />
        <div className="text-center">
          <p className="text-white text-lg font-semibold mb-1">Preparing Quick Assessment</p>
          <p className="text-slate-400 text-sm">Generating role-specific questions to calibrate your ELO...</p>
        </div>
      </div>
    );
  if (error && !questions.length)
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="glass-strong rounded-2xl p-8 max-w-md text-center"
        >
          <AlertTriangle className="w-8 h-8 text-red-400 mx-auto mb-3" />
          <p className="text-red-400 mb-4">{error}</p>
          <button onClick={onSkip} className="px-6 py-2 rounded-xl text-sm bg-slate-700 hover:bg-slate-600 text-white">
            Skip to Dashboard
          </button>
        </motion.div>
      </div>
    );

  // Results screen
  if (results) {
    const elo = results.elo;
    const readiness = results.readiness;
    const scorecard = results.scorecard;
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <GlassCard className="p-8 max-w-2xl w-full glow">
            <GlassCardContent>
              <motion.div
                initial={{ scale: 0.8 }}
                animate={{ scale: 1 }}
                transition={{ type: "spring", stiffness: 200, damping: 15 }}
                className="text-center mb-6"
              >
                <Trophy className="w-10 h-10 text-amber-400 mx-auto mb-2" />
                <h2 className="text-2xl font-bold mb-2">Quick Assessment Complete</h2>
                <p className="text-slate-400 text-sm">Here's your starting position</p>
              </motion.div>

              {/* ELO Result */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="glass rounded-xl p-6 mb-6 text-center"
              >
                <p className="text-slate-500 text-xs uppercase tracking-wider mb-1 flex items-center justify-center gap-1">
                  <Sparkles className="w-3 h-3" /> Your ELO Rating
                </p>
                <motion.p
                  initial={{ scale: 0.5, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  transition={{ type: "spring", stiffness: 180, damping: 12, delay: 0.4 }}
                  className="text-5xl font-black text-indigo-400 mb-1"
                >
                  {elo.after}
                </motion.p>
                <p className="text-sm mb-2">
                  <span
                    className={cn(
                      "px-3 py-1 rounded-full",
                      readiness.is_ready ? "bg-emerald-500/20 text-emerald-300" : "bg-amber-500/20 text-amber-300"
                    )}
                  >
                    {readiness.readiness?.label || "Getting There"}
                  </span>
                </p>
                <div className="w-full bg-slate-800/50 rounded-full h-3 mt-3 mb-2 overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${Math.min(100, (elo.after / (readiness.hiring_bar || 1800)) * 100)}%` }}
                    transition={{ duration: 1, delay: 0.5, ease: "easeOut" }}
                    className="h-3 rounded-full bg-gradient-to-r from-indigo-500 to-purple-500"
                  />
                </div>
                <div className="flex justify-between text-xs text-slate-500">
                  <span className="flex items-center gap-1">
                    <Target className="w-3 h-3" /> You: {elo.after}
                  </span>
                  <span className="flex items-center gap-1">
                    <BarChart className="w-3 h-3" />
                    {assessmentMeta.company?.charAt(0).toUpperCase() + assessmentMeta.company?.slice(1)} Bar:{" "}
                    {readiness.hiring_bar}
                  </span>
                </div>
                {readiness.gap > 0 && (
                  <motion.p
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.8 }}
                    className="text-amber-400 text-sm mt-2 font-medium flex items-center justify-center gap-1"
                  >
                    <AlertTriangle className="w-3.5 h-3.5" />
                    {readiness.gap} points to interview ready
                  </motion.p>
                )}
              </motion.div>

              {/* Round Scores */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 }}
                className="glass rounded-xl p-4 mb-6"
              >
                <h3 className="text-white text-sm font-semibold mb-3 uppercase tracking-wider flex items-center gap-1.5">
                  <BarChart className="w-4 h-4 text-indigo-400" /> Score by Round
                </h3>
                <div className="space-y-2">
                  {Object.entries(scorecard?.per_round || {}).map(([round, score]: [string, any], idx: number) => (
                    <div key={round} className="flex items-center gap-3">
                      <span className="text-slate-400 text-xs w-28 capitalize">{round.replace(/_/g, " ")}</span>
                      <div className="flex-1 bg-slate-800/50 rounded-full h-2 overflow-hidden">
                        <motion.div
                          initial={{ width: 0 }}
                          animate={{ width: `${score}%` }}
                          transition={{ duration: 0.8, delay: 0.5 + idx * 0.1, ease: "easeOut" }}
                          className={cn(
                            "h-2 rounded-full",
                            score >= 70 ? "bg-emerald-500" : score >= 40 ? "bg-amber-500" : "bg-red-500"
                          )}
                        />
                      </div>
                      <span className="text-slate-300 text-xs w-8 text-right">{score}</span>
                    </div>
                  ))}
                </div>
              </motion.div>

              {/* Focus Areas */}
              {scorecard?.recommended_focus?.length > 0 && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.6 }}
                  className="glass rounded-xl p-4 mb-6"
                >
                  <h3 className="text-red-400 text-sm font-semibold mb-2 uppercase tracking-wider flex items-center gap-1.5">
                    <AlertTriangle className="w-4 h-4" /> Focus Areas
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {scorecard.recommended_focus.map((f: string, i: number) => (
                      <motion.span
                        key={f}
                        initial={{ opacity: 0, scale: 0.8 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ delay: 0.7 + i * 0.08 }}
                        className="px-3 py-1 rounded-full bg-red-500/20 text-red-300 text-xs"
                      >
                        {f}
                      </motion.span>
                    ))}
                  </div>
                </motion.div>
              )}

              <motion.button
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.8 }}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => onComplete(results)}
                className="w-full py-3 rounded-xl font-semibold text-sm bg-indigo-600 hover:bg-indigo-500 text-white shadow-lg shadow-indigo-500/20 transition-all"
              >
                Go to Dashboard
              </motion.button>
            </GlassCardContent>
          </GlassCard>
        </motion.div>
      </div>
    );
  }

  // Question screen
  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-2xl"
      >
        <GlassCard className="p-0 glow">
          <GlassCardContent className="pt-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="text-lg font-bold flex items-center gap-2">
                  <Brain className="w-5 h-5 text-indigo-400" />
                  Quick Assessment
                </h2>
                <p className="text-slate-500 text-xs capitalize">
                  {assessmentMeta.company} | {(assessmentMeta.role || "").replace(/_/g, " ")} | {assessmentMeta.level}
                </p>
              </div>
              <span className="text-slate-400 text-sm font-mono">
                {currentIdx + 1} / {questions.length}
              </span>
            </div>

            {/* Animated Progress bar */}
            <div className="w-full bg-slate-800/50 rounded-full h-1.5 mb-6 overflow-hidden">
              <motion.div
                animate={{ width: `${progress}%` }}
                transition={{ duration: 0.4, ease: "easeOut" }}
                className="h-1.5 rounded-full bg-gradient-to-r from-indigo-500 to-purple-500"
              />
            </div>

            <AnimatePresence mode="wait" custom={direction}>
              {currentQ && (
                <motion.div
                  key={currentIdx}
                  initial={direction === "right" ? "enterRight" : "enterLeft"}
                  animate="center"
                  exit={direction === "right" ? "exitLeft" : "exitRight"}
                  variants={slideVariants}
                  transition={{ duration: 0.3 }}
                >
                  {/* Question metadata badges */}
                  <div className="flex gap-2 mb-3 flex-wrap">
                    <motion.span
                      whileHover={{ scale: 1.05 }}
                      className="px-2 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 text-[10px] uppercase flex items-center gap-1"
                    >
                      <Tag className="w-2.5 h-2.5" />
                      {currentQ.round_type?.replace(/_/g, " ")}
                    </motion.span>
                    <motion.span
                      whileHover={{ scale: 1.05 }}
                      className="px-2 py-0.5 rounded-full bg-slate-500/20 text-slate-400 text-[10px]"
                    >
                      {currentQ.pattern}
                    </motion.span>
                    <motion.span
                      whileHover={{ scale: 1.05 }}
                      className={cn(
                        "px-2 py-0.5 rounded-full text-[10px]",
                        currentQ.difficulty === "hard"
                          ? "bg-red-500/20 text-red-300"
                          : currentQ.difficulty === "easy"
                            ? "bg-emerald-500/20 text-emerald-300"
                            : "bg-amber-500/20 text-amber-300"
                      )}
                    >
                      {currentQ.difficulty}
                    </motion.span>
                    <motion.span
                      whileHover={{ scale: 1.05 }}
                      className="px-2 py-0.5 rounded-full bg-purple-500/20 text-purple-300 text-[10px] flex items-center gap-1"
                    >
                      <Clock className="w-2.5 h-2.5" />
                      {currentQ.answer_mode}
                    </motion.span>
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
                  <p
                    className={cn(
                      "text-[10px] mt-1 text-right transition-colors",
                      wordCount > 100 ? "text-emerald-500" : wordCount > 50 ? "text-amber-500" : "text-slate-600"
                    )}
                  >
                    {wordCount} words
                  </p>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Navigation */}
            <div className="flex items-center justify-between mt-4">
              <motion.button
                whileHover={{ x: -2 }}
                whileTap={{ scale: 0.95 }}
                onClick={handlePrev}
                disabled={currentIdx === 0}
                className="px-4 py-2 rounded-xl text-sm text-slate-400 hover:text-white disabled:opacity-30 transition-all flex items-center gap-1"
              >
                <ChevronLeft className="w-4 h-4" />
                Previous
              </motion.button>
              <div className="flex gap-2">
                {currentIdx < questions.length - 1 ? (
                  <motion.button
                    whileHover={{ x: 2 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={handleNext}
                    className="px-6 py-2 rounded-xl text-sm font-medium bg-indigo-600 hover:bg-indigo-500 text-white transition-all flex items-center gap-1"
                  >
                    Next
                    <ChevronRight className="w-4 h-4" />
                  </motion.button>
                ) : (
                  <motion.button
                    whileHover={{ scale: 1.03 }}
                    whileTap={{ scale: 0.97 }}
                    onClick={handleSubmit}
                    disabled={submitting}
                    className="px-6 py-2 rounded-xl text-sm font-medium bg-emerald-600 hover:bg-emerald-500 text-white transition-all disabled:opacity-50 flex items-center gap-1.5"
                  >
                    <Send className="w-4 h-4" />
                    {submitting ? "Evaluating..." : "Submit Assessment"}
                  </motion.button>
                )}
              </div>
            </div>
          </GlassCardContent>
        </GlassCard>

        {error && (
          <motion.p
            initial={{ opacity: 0, y: 5 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-red-400 text-sm mt-3 flex items-center gap-1.5"
          >
            <AlertTriangle className="w-4 h-4" />
            {error}
          </motion.p>
        )}
      </motion.div>
    </div>
  );
}
