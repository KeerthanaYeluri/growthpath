import { useState, useEffect, useRef } from "react";
import { apiFetch } from "@/lib/api";
import LoadingSpinner from "@/components/common/LoadingSpinner";
import MockResultsView from "@/components/mock/MockResultsView";

interface MockInterviewScreenProps {
  onComplete: (results: any) => void;
  onNavigate: (screen: string) => void;
}

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

  const round = mockData?.rounds?.[currentRound];
  const allQsInRound = round?.questions || [];
  const currentQ = allQsInRound[currentQIdx];
  const totalAnswered = Object.keys(answers).length;
  const totalQs = mockData?.total_questions || 0;
  const formatTime = (s: number) => `${Math.floor(s / 60)}:${(s % 60).toString().padStart(2, "0")}`;

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

  if (loading) return <LoadingSpinner />;
  if (error && !mockData)
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <div className="glass-strong rounded-2xl p-8 max-w-md text-center">
          <p className="text-red-400 mb-4">{error}</p>
          <button
            onClick={() => onNavigate("dashboard")}
            className="px-6 py-2 rounded-xl text-sm bg-slate-700 hover:bg-slate-600 text-white"
          >
            Back to Dashboard
          </button>
        </div>
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
    <div className="max-w-3xl mx-auto p-4 md:p-6 animate-fade-in">
      {/* Round Indicator */}
      <div className="flex items-center gap-1.5 mb-4">
        {mockData.rounds.map((r: any, i: number) => (
          <div
            key={r.round_type}
            className={`flex-1 h-1.5 rounded-full transition-all ${i < currentRound ? "bg-emerald-500" : i === currentRound ? "bg-indigo-500" : "bg-slate-700"}`}
          ></div>
        ))}
      </div>

      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-lg font-bold">{round?.label}</h2>
          <p className="text-slate-500 text-xs">
            Round {currentRound + 1}/5 | Q{currentQIdx + 1}/{allQsInRound.length} | {totalAnswered}/{totalQs} total
          </p>
        </div>
        <div className={`glass rounded-xl px-4 py-2 text-center ${timeLeft < 30 ? "border-red-500/50" : ""}`}>
          <p className={`text-xl font-bold font-mono ${timeLeft < 30 ? "text-red-400" : "text-white"}`}>
            {formatTime(timeLeft)}
          </p>
          <p className="text-slate-500 text-[10px]">{round?.answer_mode} mode</p>
        </div>
      </div>

      {currentQ && (
        <div className="glass-strong rounded-2xl p-6">
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
          </div>
          <p className="text-white text-base mb-4 leading-relaxed">{currentQ.question}</p>
          <textarea
            value={answers[currentQ.id] || ""}
            onChange={(e) => handleAnswer(e.target.value)}
            placeholder={
              currentQ.answer_mode === "code"
                ? "Write your code/solution here..."
                : "Explain your answer thoroughly -- show your thinking process..."
            }
            rows={currentQ.answer_mode === "code" ? 12 : 8}
            className={`w-full bg-slate-800/60 border border-slate-700/50 rounded-xl px-4 py-3 text-sm placeholder-slate-600 focus:border-indigo-500/50 transition-all resize-none ${currentQ.answer_mode === "code" ? "font-mono text-emerald-300" : "text-white"}`}
          />
          <div className="flex justify-between items-center mt-1">
            <p className="text-slate-600 text-[10px]">
              {(answers[currentQ.id] || "").split(/\s+/).filter(Boolean).length} words
            </p>
            <p className="text-slate-600 text-[10px]">
              {currentQ.answer_mode === "code"
                ? "Code Editor"
                : currentQ.answer_mode === "voice"
                  ? "Voice (text fallback)"
                  : "Hybrid"}
            </p>
          </div>

          {/* AI Interviewer Conversation */}
          <div className="mt-4 border-t border-slate-700/30 pt-4">
            {!convKey ? (
              <button
                onClick={startConversation}
                disabled={convLoading || !(answers[currentQ.id] || "").trim()}
                className="px-4 py-2 rounded-xl text-xs font-medium bg-purple-600/20 text-purple-300 hover:bg-purple-600/30 border border-purple-500/20 transition-all disabled:opacity-30"
              >
                {convLoading ? "Starting..." : "Get AI Interviewer Feedback"}
              </button>
            ) : (
              <div>
                <div className="flex items-center justify-between mb-2">
                  <p className="text-purple-300 text-xs font-semibold uppercase tracking-wider">AI Interviewer</p>
                  <div className="flex items-center gap-2">
                    <span className="text-slate-500 text-[10px]">Depth: {convDepth}/5</span>
                    {hintsUsed > 0 && (
                      <span className="text-amber-400 text-[10px]">
                        {hintsUsed} hint{hintsUsed > 1 ? "s" : ""} used
                      </span>
                    )}
                    {convComplete && <span className="text-emerald-400 text-[10px]">Complete</span>}
                  </div>
                </div>
                {/* Depth progress */}
                <div className="flex gap-1 mb-3">
                  {[1, 2, 3, 4, 5].map((d) => (
                    <div
                      key={d}
                      className={`flex-1 h-1 rounded-full ${d <= convDepth ? "bg-purple-500" : "bg-slate-700"}`}
                    ></div>
                  ))}
                </div>
                {/* Messages */}
                <div className="space-y-2 max-h-48 overflow-y-auto mb-3">
                  {convMessages.slice(1).map((msg: any, i: number) => (
                    <div key={i} className={`flex ${msg.role === "candidate" ? "justify-end" : "justify-start"}`}>
                      <div
                        className={`max-w-[80%] px-3 py-2 rounded-xl text-xs ${msg.role === "candidate" ? "bg-indigo-600/20 text-indigo-200" : "bg-slate-800/80 text-slate-300"}`}
                      >
                        {msg.isHint && <span className="text-amber-400 text-[9px] block mb-0.5">Hint (-penalty)</span>}
                        {msg.content}
                        {msg.quality && (
                          <span
                            className={`ml-2 text-[9px] px-1.5 py-0.5 rounded-full ${msg.quality === "strong" ? "bg-emerald-500/20 text-emerald-300" : msg.quality === "average" ? "bg-amber-500/20 text-amber-300" : "bg-red-500/20 text-red-300"}`}
                          >
                            {msg.quality}
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                  {convLoading && (
                    <div className="flex justify-start">
                      <div className="bg-slate-800/80 px-3 py-2 rounded-xl text-xs text-slate-500">Thinking...</div>
                    </div>
                  )}
                </div>
                {/* Response buttons */}
                {!convComplete && (
                  <div className="flex gap-2">
                    <button
                      onClick={() => sendToInterviewer(false)}
                      disabled={convLoading || !(answers[currentQ.id] || "").trim()}
                      className="px-4 py-1.5 rounded-lg text-xs font-medium bg-purple-600/20 text-purple-300 hover:bg-purple-600/30 border border-purple-500/20 transition-all disabled:opacity-30"
                    >
                      Send Updated Answer
                    </button>
                    <button
                      onClick={() => sendToInterviewer(true)}
                      disabled={convLoading}
                      className="px-4 py-1.5 rounded-lg text-xs font-medium bg-amber-600/20 text-amber-300 hover:bg-amber-600/30 border border-amber-500/20 transition-all disabled:opacity-30"
                    >
                      Get Hint (-penalty)
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Navigation */}
      <div className="flex items-center justify-between mt-4">
        <button
          onClick={handlePrev}
          disabled={currentQIdx === 0 && currentRound === 0}
          className="px-4 py-2 rounded-xl text-sm text-slate-400 hover:text-white disabled:opacity-30 transition-all"
        >
          Previous
        </button>
        <div className="flex gap-2">
          {currentQIdx < allQsInRound.length - 1 || currentRound < mockData.rounds.length - 1 ? (
            <button
              onClick={handleNext}
              className="px-6 py-2 rounded-xl text-sm font-medium bg-indigo-600 hover:bg-indigo-500 text-white transition-all"
            >
              {currentQIdx < allQsInRound.length - 1 ? "Next Question" : "Next Round ->"}
            </button>
          ) : (
            <button
              onClick={handleSubmitAll}
              disabled={submitting}
              className="px-6 py-2 rounded-xl text-sm font-medium bg-emerald-600 hover:bg-emerald-500 text-white transition-all disabled:opacity-50"
            >
              {submitting ? "Evaluating..." : "Submit Mock Interview"}
            </button>
          )}
        </div>
      </div>
      {error && <p className="text-red-400 text-sm mt-3">{error}</p>}
    </div>
  );
}
