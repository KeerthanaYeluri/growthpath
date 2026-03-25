import { useState, useEffect, useRef } from "react";
import { motion } from "framer-motion";
import { Mic, Volume2, ArrowRight, Check, Loader2, XCircle } from "lucide-react";
import { apiFetch } from "@/lib/api";
import LoadingSpinner from "@/components/common/LoadingSpinner";

interface AIInterviewRoomProps {
  interviewId: string;
  evaluateMode?: boolean;
  onNavigate: (screen: string, params?: any) => void;
}

export default function AIInterviewRoom({ interviewId, evaluateMode, onNavigate }: AIInterviewRoomProps) {
  const [interview, setInterview] = useState<any>(null);
  const [currentQ, setCurrentQ] = useState(0);
  const [totalQ, setTotalQ] = useState(0);
  const [question, setQuestion] = useState("");
  const [category, setCategory] = useState("");
  const [exchangeId, setExchangeId] = useState<string | null>(null);
  const [answer, setAnswer] = useState("");
  const [aiResponse, setAiResponse] = useState("");
  const [greeting, setGreeting] = useState("");
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [finished, setFinished] = useState(false);
  const [evaluating, setEvaluating] = useState(false);
  const [listening, setListening] = useState(false);
  const [speaking, setSpeaking] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const recognitionRef = useRef<any>(null);
  const synthRef = useRef(window.speechSynthesis);

  useEffect(() => {
    loadInterview();
  }, [interviewId]);

  const loadInterview = async () => {
    try {
      const res = await apiFetch(`/ai-interview/${interviewId}`);
      const data = await res.json();
      setInterview(data);
      setTotalQ(data.total_questions);

      if (evaluateMode && data.status === "completed") {
        handleEvaluate();
        return;
      }

      if (data.status === "pending" || data.status === "in_progress") {
        await startInterview();
      } else if (data.status === "evaluated") {
        onNavigate("ai_results", { interviewId });
      } else {
        setFinished(true);
      }
    } catch (e) {
      setError("Failed to load interview");
    }
    setLoading(false);
  };

  const startInterview = async () => {
    try {
      const res = await apiFetch(`/ai-interview/${interviewId}/start`, { method: "POST" });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error);
      setCurrentQ(data.current_question);
      setTotalQ(data.total_questions);
      setQuestion(data.question);
      setCategory(data.category);
      setExchangeId(data.exchange_id);
      setGreeting(data.greeting);
      speak(data.greeting + " " + data.question);
    } catch (e: any) {
      setError(e.message);
    }
    setLoading(false);
  };

  const speak = (text: string) => {
    if (!synthRef.current) return;
    synthRef.current.cancel();
    const utter = new SpeechSynthesisUtterance(text);
    utter.rate = 0.95;
    utter.pitch = 1;
    utter.lang = "en-US";
    const voices = synthRef.current.getVoices();
    const preferred = voices.find((v) => v.name.includes("Google") || v.name.includes("Samantha") || v.name.includes("Daniel"));
    if (preferred) utter.voice = preferred;
    setSpeaking(true);
    utter.onend = () => setSpeaking(false);
    synthRef.current.speak(utter);
  };

  const startListening = () => {
    if (!("webkitSpeechRecognition" in window) && !("SpeechRecognition" in window)) {
      setError("Speech recognition not supported. Please type your answer.");
      return;
    }
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = "en-US";

    let finalTranscript = answer;
    recognition.onresult = (e: any) => {
      let interim = "";
      for (let i = e.resultIndex; i < e.results.length; i++) {
        if (e.results[i].isFinal) {
          finalTranscript += e.results[i][0].transcript + " ";
        } else {
          interim += e.results[i][0].transcript;
        }
      }
      setAnswer(finalTranscript + interim);
    };
    recognition.onerror = () => setListening(false);
    recognition.onend = () => setListening(false);
    recognition.start();
    recognitionRef.current = recognition;
    setListening(true);
  };

  const stopListening = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
      recognitionRef.current = null;
    }
    setListening(false);
  };

  const handleSubmitAnswer = async () => {
    if (!answer.trim()) return;
    setSubmitting(true);
    setError(null);
    stopListening();
    synthRef.current?.cancel();

    try {
      const res = await apiFetch(`/ai-interview/${interviewId}/answer`, {
        method: "POST",
        body: JSON.stringify({ answer: answer.trim(), exchange_id: exchangeId }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error);

      setAiResponse(data.ai_response);

      if (data.status === "completed") {
        speak(data.ai_response);
        setFinished(true);
      } else {
        speak(data.ai_response + " ... " + data.question);
        setCurrentQ(data.current_question);
        setQuestion(data.question);
        setCategory(data.category);
        setExchangeId(data.exchange_id);
        setAnswer("");
      }
    } catch (e: any) {
      setError(e.message);
    }
    setSubmitting(false);
  };

  const handleEvaluate = async () => {
    setEvaluating(true);
    setError(null);
    try {
      const res = await apiFetch(`/ai-interview/${interviewId}/evaluate`, { method: "POST" });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error);
      onNavigate("ai_results", { interviewId });
    } catch (e: any) {
      setError(e.message);
      setEvaluating(false);
    }
  };

  const handleEndEarly = async () => {
    try {
      await apiFetch(`/ai-interview/${interviewId}/end`, { method: "POST" });
      setFinished(true);
    } catch (e: any) {
      setError(e.message);
    }
  };

  const categoryColors: Record<string, string> = {
    technical: "bg-blue-500/20 text-blue-300",
    behavioral: "bg-green-500/20 text-green-300",
    situational: "bg-amber-500/20 text-amber-300",
    project: "bg-purple-500/20 text-purple-300",
  };

  if (loading) return <LoadingSpinner />;
  if (evaluating)
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-12 h-12 text-indigo-400 mx-auto mb-4 animate-spin" />
          <p className="text-white text-lg font-medium">AI is evaluating your answers...</p>
          <p className="text-slate-400 text-sm mt-2">This may take a minute</p>
        </div>
      </div>
    );

  if (finished)
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="glass rounded-2xl p-8 text-center max-w-md">
          <div className="w-16 h-16 rounded-full bg-emerald-600/20 flex items-center justify-center mx-auto mb-4">
            <Check className="w-8 h-8 text-emerald-400" />
          </div>
          <h2 className="text-xl font-bold text-white mb-2">Interview Complete!</h2>
          <p className="text-slate-400 text-sm mb-6">Your answers have been recorded. Get your AI evaluation now.</p>
          <div className="flex gap-3 justify-center">
            <button
              onClick={handleEvaluate}
              className="px-6 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-sm font-medium transition-all"
            >
              Get AI Evaluation
            </button>
            <button
              onClick={() => onNavigate("ai_interview")}
              className="px-6 py-2.5 bg-slate-700 hover:bg-slate-600 text-white rounded-xl text-sm font-medium transition-all"
            >
              Back
            </button>
          </div>
        </div>
      </div>
    );

  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="min-h-screen flex flex-col">
      {/* Top bar */}
      <div className="glass-strong border-b border-slate-800/50 px-6 py-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className={`w-3 h-3 rounded-full ${speaking ? "bg-emerald-400 animate-pulse" : "bg-slate-600"}`} />
          <span className="text-white text-sm font-medium">AI Interviewer: Alex</span>
          <span className={`px-2 py-0.5 rounded-full text-xs ${categoryColors[category] || "bg-slate-500/20 text-slate-300"}`}>
            {category}
          </span>
        </div>
        <div className="flex items-center gap-4">
          <span className="text-slate-400 text-sm">
            Question {currentQ + 1} / {totalQ}
          </span>
          <div className="w-32 h-1.5 bg-slate-800 rounded-full overflow-hidden">
            <div className="h-full bg-indigo-500 rounded-full transition-all" style={{ width: `${((currentQ + 1) / totalQ) * 100}%` }} />
          </div>
          <button onClick={handleEndEarly} className="text-red-400 hover:text-red-300 text-xs flex items-center gap-1">
            <XCircle className="w-3.5 h-3.5" />
            End Interview
          </button>
        </div>
      </div>

      {/* Main area */}
      <div className="flex-1 flex flex-col max-w-3xl mx-auto w-full px-4 py-8">
        {error && (
          <div className="bg-red-500/10 border border-red-500/30 text-red-300 px-4 py-2 rounded-xl text-sm mb-4">{error}</div>
        )}

        {/* AI Response */}
        {(aiResponse || greeting) && (
          <div className="mb-6 flex gap-3">
            <div className="w-8 h-8 rounded-full bg-indigo-600/30 flex-shrink-0 flex items-center justify-center">
              <svg className="w-4 h-4 text-indigo-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9.75 3.104v5.714a2.25 2.25 0 01-.659 1.591L5 14.5M9.75 3.104c-.251.023-.501.05-.75.082m.75-.082a24.301 24.301 0 014.5 0m0 0v5.714c0 .597.237 1.17.659 1.591L19.8 15.3"
                />
              </svg>
            </div>
            <div className="glass-strong rounded-2xl rounded-tl-sm px-4 py-3 max-w-lg">
              <p className="text-slate-300 text-sm">{aiResponse || greeting}</p>
            </div>
          </div>
        )}

        {/* Current Question */}
        <div className="mb-6 flex gap-3">
          <div className="w-8 h-8 rounded-full bg-indigo-600/30 flex-shrink-0 flex items-center justify-center">
            <span className="text-indigo-300 text-xs font-bold">Q</span>
          </div>
          <div className="glass rounded-2xl rounded-tl-sm px-5 py-4 max-w-lg glow">
            <p className="text-white text-sm leading-relaxed">{question}</p>
          </div>
        </div>

        {/* Answer Area */}
        <div className="mt-auto">
          <div className="glass rounded-2xl p-4">
            <textarea
              value={answer}
              onChange={(e) => setAnswer(e.target.value)}
              placeholder={listening ? "Listening... speak your answer" : "Type your answer or click the mic to speak..."}
              className="w-full bg-transparent text-white text-sm placeholder-slate-600 resize-none focus:outline-none"
              rows={4}
            />
            <div className="flex items-center justify-between mt-3 pt-3 border-t border-slate-800/50">
              <div className="flex items-center gap-3">
                {/* Mic Button */}
                <button
                  onClick={listening ? stopListening : startListening}
                  className={`w-10 h-10 rounded-full flex items-center justify-center transition-all ${
                    listening ? "bg-red-500 hover:bg-red-400 animate-pulse" : "bg-slate-700 hover:bg-slate-600"
                  }`}
                >
                  <Mic className="w-5 h-5 text-white" />
                </button>
                {listening && <span className="text-red-400 text-xs animate-pulse">Recording...</span>}
                {/* Speaker button to replay question */}
                <button
                  onClick={() => speak(question)}
                  className="w-10 h-10 rounded-full bg-slate-700 hover:bg-slate-600 flex items-center justify-center transition-all"
                  title="Replay question"
                >
                  <Volume2 className="w-5 h-5 text-white" />
                </button>
              </div>
              <button
                onClick={handleSubmitAnswer}
                disabled={submitting || !answer.trim()}
                className={`px-6 py-2.5 rounded-xl text-sm font-medium transition-all flex items-center gap-2 ${
                  submitting || !answer.trim() ? "bg-slate-700 text-slate-500" : "bg-indigo-600 hover:bg-indigo-500 text-white"
                }`}
              >
                {submitting ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" /> Processing...
                  </>
                ) : (
                  <>
                    Submit Answer <ArrowRight className="w-4 h-4" />
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
