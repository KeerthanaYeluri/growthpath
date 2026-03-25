import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Timer,
  ChevronRight,
  ChevronLeft,
  Send,
  MessageSquare,
  Lightbulb,
  Code,
  Mic,
  MicOff,
  Layers,
  AlertTriangle,
  CheckCircle,
} from "lucide-react";
import { GlassCard, GlassCardContent } from "@/components/ui/glass-card";
import { cn } from "@/lib/utils";
import { apiFetch } from "@/lib/api";
import LoadingSpinner from "@/components/common/LoadingSpinner";
import MockResultsView from "@/components/mock/MockResultsView";
import { useBrowserSpeech } from "@/hooks/useBrowserSpeech";

interface MockInterviewScreenProps {
  onComplete: (results: any) => void;
  onNavigate: (screen: string) => void;
}

const roundColors = [
  "bg-indigo-500",
  "bg-purple-500",
  "bg-cyan-500",
  "bg-amber-500",
  "bg-emerald-500",
];

const answerModeIcons: Record<string, React.ReactNode> = {
  code: <Code className="w-3 h-3" />,
  voice: <Mic className="w-3 h-3" />,
  hybrid: <Layers className="w-3 h-3" />,
};

export default function MockInterviewScreen({ onComplete, onNavigate }: MockInterviewScreenProps) {
  const [loading, setLoading] = useState(true);
  const [mockData, setMockData] = useState<any>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [currentRound, setCurrentRound] = useState(0);
  const [currentQIdx, setCurrentQIdx] = useState(0);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [timeLeft, setTimeLeft] = useState(0);
  const [submitting, setSubmitting] = useState(false);
  const [results, setResults] = useState<any>(null);
  const [error, setError] = useState("");
  const [convKey, setConvKey] = useState<string | null>(null);
  const [convMessages, setConvMessages] = useState<any[]>([]);
  const [convLoading, setConvLoading] = useState(false);
  const [convDepth, setConvDepth] = useState(0);
  const [convComplete, setConvComplete] = useState(false);
  const [hintsUsed, setHintsUsed] = useState(0);
  const timerRef = useRef<any>(null);
  const { transcript, listening, supported: micSupported, startListening, stopListening, reset: resetSpeech } = useBrowserSpeech();

  useEffect(() => {
    apiFetch("/mock/start", { method: "POST" })
      .then((r) => r.json())
      .then((data) => {
        if (data.error) {
          setError(data.error);
          setLoading(false);
          return;
        }
        setSessionId(data.session_id);
        setMockData(data);
        setTimeLeft(data.rounds[0].time_minutes * 60);
        setLoading(false);
      })
      .catch(() => {
        setError("Cannot start mock interview");
        setLoading(false);
      });
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, []);

  // Timer
  useEffect(() => {
    if (!mockData || results) return;
    if (timerRef.current) clearInterval(timerRef.current);
    timerRef.current = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1) {
          clearInterval(timerRef.current);
          if (currentRound < mockData.rounds.length - 1) {
            setTimeout(() => advanceRound(), 500);
          }
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
    return () => clearInterval(timerRef.current);
  }, [currentRound, mockData, results]);

  // Sync speech transcript to answer for voice/hybrid modes
  useEffect(() => {
    if (transcript && listening) {
      const q = mockData?.rounds?.[currentRound]?.questions?.[currentQIdx];
      if (q && q.answer_mode !== "code") {
        setAnswers((prev) => ({ ...prev, [q.id]: transcript }));
      }
    }
  }, [transcript, listening, currentRound, currentQIdx, mockData]);

  // Stop listening and auto-speak question when moving between questions/rounds
  useEffect(() => {
    if (listening) stopListening();
    resetSpeech();
    // Auto-read question aloud for voice/hybrid modes
    const q = mockData?.rounds?.[currentRound]?.questions?.[currentQIdx];
    if (q && q.answer_mode !== "code" && "speechSynthesis" in window) {
      setTimeout(() => speakQuestion(q.question), 500);
    }
  }, [currentRound, currentQIdx, mockData]);

  // Read question aloud using browser TTS
  const speakQuestion = (text: string) => {
    if ("speechSynthesis" in window) {
      window.speechSynthesis.cancel();
      const utter = new SpeechSynthesisUtterance(text);
      utter.rate = 0.95;
      utter.pitch = 1;
      utter.lang = "en-US";
      window.speechSynthesis.speak(utter);
    }
  };

  const round = mockData?.rounds?.[currentRound];
  const allQsInRound = round?.questions || [];
  const currentQ = allQsInRound[currentQIdx];
  const totalAnswered = Object.keys(answers).length;
  const totalQs = mockData?.total_questions || 0;
  const formatTime = (s: number) => `${Math.floor(s / 60)}:${(s % 60).toString().padStart(2, "0")}`;

  const timerColor =
    timeLeft < 30 ? "text-red-400" : timeLeft < 60 ? "text-amber-400" : "text-white";

  const handleAnswer = (text: string) => {
    if (currentQ) setAnswers((prev) => ({ ...prev, [currentQ.id]: text }));
  };

  // Reset conversation when switching questions
  useEffect(() => {
    setConvKey(null);
    setConvMessages([]);
    setConvDepth(0);
    setConvComplete(false);
  }, [currentRound, currentQIdx]);

  const startConversation = async () => {
    if (!currentQ || !sessionId) return;
    setConvLoading(true);
    try {
      const res = await apiFetch("/conversation/start", {
        method: "POST",
        body: JSON.stringify({ session_id: sessionId, question: currentQ, company: mockData.company }),
      });
      const data = await res.json();
      setConvKey(data.conversation_key);
      setConvMessages([{ role: "interviewer", content: currentQ.question }]);
      setConvDepth(0);
      setConvComplete(false);
    } catch {
      setError("Failed to start conversation");
    }
    setConvLoading(false);
  };

  const sendToInterviewer = async (hintMode = false) => {
    if (!convKey || convComplete) return;
    const answerText = answers[currentQ?.id] || "";
    if (!answerText.trim() && !hintMode) return;
    setConvLoading(true);
    setConvMessages((prev) => [...prev, { role: "candidate", content: hintMode ? "[Requested hint]" : answerText }]);
    try {
      const res = await apiFetch("/conversation/respond", {
        method: "POST",
        body: JSON.stringify({ conversation_key: convKey, answer_text: answerText, hint_requested: hintMode }),
      });
      const data = await res.json();
      setConvMessages((prev) => [
        ...prev,
        {
          role: "interviewer",
          content: data.interviewer_response,
          quality: data.quality,
          depth: data.probe_depth,
          isHint: data.is_hint,
        },
      ]);
      setConvDepth(data.probe_depth);
      setConvComplete(data.is_complete);
      if (data.is_hint) setHintsUsed(data.hints_used);
    } catch {
      setError("AI interviewer unavailable");
    }
    setConvLoading(false);
  };

  const advanceRound = () => {
    if (currentRound < (mockData?.rounds?.length || 0) - 1) {
      const nextRound = currentRound + 1;
      setCurrentRound(nextRound);
      setCurrentQIdx(0);
      setTimeLeft(mockData.rounds[nextRound].time_minutes * 60);
    }
  };

  const handleNext = () => {
    if (currentQIdx < allQsInRound.length - 1) {
      setCurrentQIdx(currentQIdx + 1);
    } else if (currentRound < (mockData?.rounds?.length || 0) - 1) {
      advanceRound();
    }
  };

  const handlePrev = () => {
    if (currentQIdx > 0) setCurrentQIdx(currentQIdx - 1);
  };

  const handleSubmitAll = async () => {
    setSubmitting(true);
    if (timerRef.current) clearInterval(timerRef.current);
    const allQuestions = mockData.rounds.flatMap((r: any) => r.questions);
    const answerList = allQuestions.map((q: any) => ({
      question_id: q.id,
      answer_text: answers[q.id] || "",
    }));
    try {
      const res = await apiFetch(`/mock/${sessionId}/submit`, {
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
      setError("Failed to submit");
    }
    setSubmitting(false);
  };

  const isLastQuestion =
    currentQIdx === allQsInRound.length - 1 &&
    currentRound === (mockData?.rounds?.length || 1) - 1;

  if (loading) return <LoadingSpinner />;
  if (error && !mockData)
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="glass-strong rounded-2xl p-8 max-w-md text-center"
        >
          <AlertTriangle className="w-8 h-8 text-red-400 mx-auto mb-3" />
          <p className="text-red-400 mb-4">{error}</p>
          <button
            onClick={() => onNavigate("dashboard")}
            className="px-6 py-2 rounded-xl text-sm bg-slate-700 hover:bg-slate-600 text-white"
          >
            Back to Dashboard
          </button>
        </motion.div>
      </div>
    );

  // Results
  if (results) {
    const eloResult = results.elo;
    const sc = results.scorecard;
    const readinessResult = results.readiness;
    return (
      <MockResultsView
        elo={eloResult}
        sc={sc}
        readiness={readinessResult}
        mockData={mockData}
        sessionId={sessionId!}
        onNavigate={onNavigate}
      />
    );
  }

  // Interview in progress
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="max-w-3xl mx-auto p-4 md:p-6"
    >
      {/* Round Indicator - 5 colored segments */}
      <div className="flex items-center gap-1.5 mb-4">
        {mockData.rounds.map((r: any, i: number) => (
          <motion.div
            key={r.round_type}
            initial={{ scaleX: 0 }}
            animate={{ scaleX: 1 }}
            transition={{ delay: i * 0.1, duration: 0.4 }}
            className={cn(
              "flex-1 h-2 rounded-full origin-left transition-all",
              i < currentRound
                ? roundColors[i % roundColors.length]
                : i === currentRound
                  ? cn(roundColors[i % roundColors.length], "animate-pulse")
                  : "bg-slate-700"
            )}
          />
        ))}
      </div>

      {/* Header */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2 }}
        className="flex items-center justify-between mb-4"
      >
        <div>
          <h2 className="text-lg font-bold flex items-center gap-2">
            {round?.label}
            <AnimatePresence mode="wait">
              <motion.span
                key={currentRound}
                initial={{ opacity: 0, x: 10 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -10 }}
                className="text-xs text-slate-500 font-normal"
              >
                Round {currentRound + 1}/5
              </motion.span>
            </AnimatePresence>
          </h2>
          <p className="text-slate-500 text-xs">
            Q{currentQIdx + 1}/{allQsInRound.length} | {totalAnswered}/{totalQs} total
          </p>
        </div>
        <motion.div
          animate={{
            borderColor: timeLeft < 30 ? "rgba(239,68,68,0.5)" : "transparent",
          }}
          className="glass rounded-xl px-4 py-2 text-center border"
        >
          <motion.p
            key={timeLeft}
            animate={{ color: timeLeft < 30 ? "#f87171" : timeLeft < 60 ? "#fbbf24" : "#ffffff" }}
            className="text-xl font-bold font-mono flex items-center gap-2"
          >
            <Timer className="w-4 h-4" />
            {formatTime(timeLeft)}
          </motion.p>
          <p className="text-slate-500 text-[10px] flex items-center gap-1 justify-center">
            {answerModeIcons[round?.answer_mode] || null}
            {round?.answer_mode} mode
          </p>
        </motion.div>
      </motion.div>

      <AnimatePresence mode="wait">
        {currentQ && (
          <motion.div
            key={`${currentRound}-${currentQIdx}`}
            initial={{ opacity: 0, x: 30 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -30 }}
            transition={{ duration: 0.3 }}
          >
            <GlassCard className="p-0">
              <GlassCardContent className="pt-6">
                {/* Badges */}
                <div className="flex gap-2 mb-3 flex-wrap">
                  <motion.span
                    whileHover={{ scale: 1.05 }}
                    className="px-2 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 text-[10px] uppercase"
                  >
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
                </div>

                <div className="flex items-start gap-3 mb-4">
                  <p className="text-white text-base leading-relaxed flex-1">{currentQ.question}</p>
                  <motion.button
                    onClick={() => speakQuestion(currentQ.question)}
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.9 }}
                    title="Listen to question"
                    className="flex-shrink-0 mt-1 w-8 h-8 rounded-full bg-indigo-500/15 hover:bg-indigo-500/25 text-indigo-400 flex items-center justify-center transition-colors"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M15.54 8.46a5 5 0 0 1 0 7.07"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14"/></svg>
                  </motion.button>
                </div>

                {/* Voice Answer Section for non-code rounds */}
                {currentQ.answer_mode !== "code" && (
                  <div className="mb-4 p-4 rounded-xl bg-slate-800/40 border border-purple-500/20">
                    <div className="flex items-center justify-between mb-3">
                      <p className="text-purple-300 text-xs font-semibold uppercase tracking-wider flex items-center gap-1.5">
                        <Mic className="w-3.5 h-3.5" />
                        Voice Answer
                      </p>
                      <span className="text-slate-500 text-[10px]">
                        {currentQ.answer_mode === "voice" ? "Voice recommended" : "Voice or type"}
                      </span>
                    </div>
                    {micSupported ? (
                      <div className="flex items-center gap-3">
                        <motion.button
                          onClick={listening ? stopListening : startListening}
                          whileHover={{ scale: 1.05 }}
                          whileTap={{ scale: 0.95 }}
                          className={cn(
                            "flex items-center justify-center gap-2 px-6 py-3 rounded-xl text-sm font-semibold transition-all",
                            listening
                              ? "bg-red-500/30 text-red-200 border-2 border-red-500/50 shadow-lg shadow-red-500/20"
                              : "bg-purple-600/30 text-purple-200 border-2 border-purple-500/40 hover:bg-purple-600/40 shadow-lg shadow-purple-500/20"
                          )}
                        >
                          {listening ? (
                            <>
                              <MicOff className="w-5 h-5" />
                              Stop Recording
                            </>
                          ) : (
                            <>
                              <Mic className="w-5 h-5" />
                              Start Speaking
                            </>
                          )}
                        </motion.button>
                        {listening && (
                          <div className="flex items-center gap-2">
                            <span className="w-3 h-3 rounded-full bg-red-500 animate-pulse" />
                            <span className="text-red-300 text-xs font-medium">Recording... Speak now</span>
                          </div>
                        )}
                        {!listening && (answers[currentQ.id] || "").trim() && (
                          <span className="text-emerald-400 text-xs flex items-center gap-1">
                            <CheckCircle className="w-3.5 h-3.5" />
                            Answer captured
                          </span>
                        )}
                      </div>
                    ) : (
                      <p className="text-amber-400 text-xs">
                        Voice input not supported in this browser. Please type your answer below.
                      </p>
                    )}
                  </div>
                )}

                <textarea
                  value={answers[currentQ.id] || ""}
                  onChange={(e) => handleAnswer(e.target.value)}
                  placeholder={
                    currentQ.answer_mode === "code"
                      ? "Write your code/solution here..."
                      : "Explain your answer thoroughly -- show your thinking process..."
                  }
                  rows={currentQ.answer_mode === "code" ? 12 : 8}
                  className={cn(
                    "w-full bg-slate-800/60 border border-slate-700/50 rounded-xl px-4 py-3 text-sm placeholder-slate-600 focus:border-indigo-500/50 transition-all resize-none",
                    currentQ.answer_mode === "code" ? "font-mono text-emerald-300" : "text-white"
                  )}
                />
                <div className="flex justify-between items-center mt-1">
                  <p className="text-slate-600 text-[10px]">
                    {(answers[currentQ.id] || "").split(/\s+/).filter(Boolean).length} words
                  </p>
                  <p className="text-slate-600 text-[10px] flex items-center gap-1">
                    {currentQ.answer_mode === "code" ? (
                      <><Code className="w-3 h-3" /> Code Editor</>
                    ) : currentQ.answer_mode === "voice" ? (
                      <><Mic className="w-3 h-3" /> Voice (text fallback)</>
                    ) : (
                      <><Layers className="w-3 h-3" /> Hybrid</>
                    )}
                  </p>
                </div>

                {/* AI Interviewer Conversation */}
                <div className="mt-4 border-t border-slate-700/30 pt-4">
                  {!convKey ? (
                    <motion.button
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      onClick={startConversation}
                      disabled={convLoading || !(answers[currentQ.id] || "").trim()}
                      className="px-4 py-2 rounded-xl text-xs font-medium bg-purple-600/20 text-purple-300 hover:bg-purple-600/30 border border-purple-500/20 transition-all disabled:opacity-30 flex items-center gap-2"
                    >
                      <MessageSquare className="w-3.5 h-3.5" />
                      {convLoading ? "Starting..." : "Get AI Interviewer Feedback"}
                    </motion.button>
                  ) : (
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <p className="text-purple-300 text-xs font-semibold uppercase tracking-wider flex items-center gap-1.5">
                          <MessageSquare className="w-3.5 h-3.5" />
                          AI Interviewer
                        </p>
                        <div className="flex items-center gap-2">
                          <span className="text-slate-500 text-[10px]">Depth: {convDepth}/5</span>
                          {hintsUsed > 0 && (
                            <span className="text-amber-400 text-[10px] flex items-center gap-0.5">
                              <Lightbulb className="w-3 h-3" />
                              {hintsUsed} hint{hintsUsed > 1 ? "s" : ""} used
                            </span>
                          )}
                          {convComplete && (
                            <span className="text-emerald-400 text-[10px] flex items-center gap-0.5">
                              <CheckCircle className="w-3 h-3" /> Complete
                            </span>
                          )}
                        </div>
                      </div>

                      {/* Depth progress */}
                      <div className="flex gap-1 mb-3">
                        {[1, 2, 3, 4, 5].map((d) => (
                          <motion.div
                            key={d}
                            initial={{ scaleX: 0 }}
                            animate={{ scaleX: d <= convDepth ? 1 : 0.3, opacity: d <= convDepth ? 1 : 0.3 }}
                            transition={{ type: "spring", stiffness: 300, damping: 20 }}
                            className={cn(
                              "flex-1 h-1 rounded-full origin-left",
                              d <= convDepth ? "bg-purple-500" : "bg-slate-700"
                            )}
                          />
                        ))}
                      </div>

                      {/* Messages */}
                      <div className="space-y-2 max-h-48 overflow-y-auto mb-3">
                        {convMessages.slice(1).map((msg: any, i: number) => (
                          <motion.div
                            key={i}
                            initial={{ opacity: 0, x: msg.role === "candidate" ? 20 : -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ duration: 0.3 }}
                            className={`flex ${msg.role === "candidate" ? "justify-end" : "justify-start"}`}
                          >
                            <div
                              className={cn(
                                "max-w-[80%] px-3 py-2 rounded-xl text-xs",
                                msg.role === "candidate"
                                  ? "bg-indigo-600/20 text-indigo-200"
                                  : "bg-slate-800/80 text-slate-300"
                              )}
                            >
                              {msg.isHint && (
                                <span className="text-amber-400 text-[9px] block mb-0.5 flex items-center gap-0.5">
                                  <Lightbulb className="w-2.5 h-2.5" /> Hint (-penalty)
                                </span>
                              )}
                              {msg.content}
                              {msg.quality && (
                                <span
                                  className={cn(
                                    "ml-2 text-[9px] px-1.5 py-0.5 rounded-full",
                                    msg.quality === "strong"
                                      ? "bg-emerald-500/20 text-emerald-300"
                                      : msg.quality === "average"
                                        ? "bg-amber-500/20 text-amber-300"
                                        : "bg-red-500/20 text-red-300"
                                  )}
                                >
                                  {msg.quality}
                                </span>
                              )}
                            </div>
                          </motion.div>
                        ))}
                        {convLoading && (
                          <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            className="flex justify-start"
                          >
                            <div className="bg-slate-800/80 px-3 py-2 rounded-xl text-xs text-slate-500">
                              Thinking...
                            </div>
                          </motion.div>
                        )}
                      </div>

                      {/* Response buttons */}
                      {!convComplete && (
                        <motion.div
                          initial={{ opacity: 0, y: 10 }}
                          animate={{ opacity: 1, y: 0 }}
                          className="flex gap-2"
                        >
                          <motion.button
                            whileHover={{ scale: 1.02 }}
                            whileTap={{ scale: 0.98 }}
                            onClick={() => sendToInterviewer(false)}
                            disabled={convLoading || !(answers[currentQ.id] || "").trim()}
                            className="px-4 py-1.5 rounded-lg text-xs font-medium bg-purple-600/20 text-purple-300 hover:bg-purple-600/30 border border-purple-500/20 transition-all disabled:opacity-30 flex items-center gap-1.5"
                          >
                            <Send className="w-3 h-3" />
                            Send Updated Answer
                          </motion.button>
                          <motion.button
                            whileHover={{ scale: 1.02 }}
                            whileTap={{ scale: 0.98 }}
                            onClick={() => sendToInterviewer(true)}
                            disabled={convLoading}
                            className="px-4 py-1.5 rounded-lg text-xs font-medium bg-amber-600/20 text-amber-300 hover:bg-amber-600/30 border border-amber-500/20 transition-all disabled:opacity-30 flex items-center gap-1.5"
                          >
                            <Lightbulb className="w-3 h-3" />
                            Get Hint (-penalty)
                          </motion.button>
                        </motion.div>
                      )}
                    </div>
                  )}
                </div>
              </GlassCardContent>
            </GlassCard>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Navigation */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.4 }}
        className="flex items-center justify-between mt-4"
      >
        <motion.button
          whileHover={{ x: -2 }}
          whileTap={{ scale: 0.95 }}
          onClick={handlePrev}
          disabled={currentQIdx === 0 && currentRound === 0}
          className="px-4 py-2 rounded-xl text-sm text-slate-400 hover:text-white disabled:opacity-30 transition-all flex items-center gap-1"
        >
          <ChevronLeft className="w-4 h-4" />
          Previous
        </motion.button>
        <div className="flex gap-2">
          {currentQIdx < allQsInRound.length - 1 || currentRound < mockData.rounds.length - 1 ? (
            <motion.button
              whileHover={{ x: 2 }}
              whileTap={{ scale: 0.95 }}
              onClick={handleNext}
              className="px-6 py-2 rounded-xl text-sm font-medium bg-indigo-600 hover:bg-indigo-500 text-white transition-all flex items-center gap-1"
            >
              {currentQIdx < allQsInRound.length - 1 ? (
                <>Next Question <ChevronRight className="w-4 h-4" /></>
              ) : (
                <motion.span
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="flex items-center gap-1"
                >
                  Next Round <ChevronRight className="w-4 h-4" />
                </motion.span>
              )}
            </motion.button>
          ) : (
            <motion.button
              whileHover={{ scale: 1.03 }}
              whileTap={{ scale: 0.97 }}
              animate={
                isLastQuestion
                  ? { boxShadow: ["0 0 0px rgba(16,185,129,0)", "0 0 20px rgba(16,185,129,0.4)", "0 0 0px rgba(16,185,129,0)"] }
                  : {}
              }
              transition={isLastQuestion ? { duration: 2, repeat: Infinity } : {}}
              onClick={handleSubmitAll}
              disabled={submitting}
              className="px-6 py-2 rounded-xl text-sm font-medium bg-emerald-600 hover:bg-emerald-500 text-white transition-all disabled:opacity-50 flex items-center gap-1.5"
            >
              <Send className="w-4 h-4" />
              {submitting ? "Evaluating..." : "Submit Mock Interview"}
            </motion.button>
          )}
        </div>
      </motion.div>

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
  );
}
