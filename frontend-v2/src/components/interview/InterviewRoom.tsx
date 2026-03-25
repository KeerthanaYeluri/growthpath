import { useState, useEffect, useRef } from "react";
import { motion } from "framer-motion";
import { Clock, Volume2, VolumeX, Sparkles } from "lucide-react";
import { API } from "@/lib/api";
import { authHeaders } from "@/lib/api";
import { getToken } from "@/lib/auth";
import { useTimer } from "@/hooks/useTimer";
import { useBrowserSpeech } from "@/hooks/useBrowserSpeech";
import { useLocalSpeech } from "@/hooks/useLocalSpeech";
import { useAudioRecorder } from "@/hooks/useAudioRecorder";
import MicButton from "@/components/common/MicButton";
import WaveIndicator from "@/components/common/WaveIndicator";
import TopicBadge from "@/components/common/TopicBadge";

function CameraPreview() {
  const [time, setTime] = useState(new Date());
  useEffect(() => {
    const t = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(t);
  }, []);
  return (
    <div className="fixed bottom-5 right-5 z-50">
      <div className="glass rounded-xl overflow-hidden w-40 shadow-2xl">
        <div className="bg-slate-800/80 h-24 flex items-center justify-center relative">
          <div className="text-center">
            <div className="w-9 h-9 rounded-full bg-slate-700 mx-auto mb-1 flex items-center justify-center">
              <svg className="w-4 h-4 text-slate-500" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd" />
              </svg>
            </div>
            <p className="text-slate-500 text-[10px]">Camera Feed</p>
          </div>
          <div className="absolute top-1.5 left-2 flex items-center gap-1">
            <div className="w-1.5 h-1.5 rounded-full bg-red-500 animate-pulse"></div>
            <span className="text-red-400 text-[8px] font-medium">REC</span>
          </div>
        </div>
        <div className="px-2 py-1 flex items-center justify-between bg-slate-900/50">
          <span className="text-slate-500 text-[9px]">LIVE</span>
          <span className="text-slate-400 text-[9px] font-mono">{time.toLocaleTimeString()}</span>
        </div>
      </div>
    </div>
  );
}

interface InterviewRoomProps {
  sessionId: string;
  questions: any[];
  engine: string;
  onFinish: Function;
}

export default function InterviewRoom({ sessionId, questions, engine, onFinish }: InterviewRoomProps) {
  const [currentQ, setCurrentQ] = useState(0);
  const [thinking, setThinking] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [showAnswer, setShowAnswer] = useState(false);
  const [modelAnswer, setModelAnswer] = useState("");
  const [loadingAnswer, setLoadingAnswer] = useState(false);
  const [audioUrls, setAudioUrls] = useState<Record<string, string>>({});
  const [voiceEnabled, setVoiceEnabled] = useState(true);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const synthRef = useRef(window.speechSynthesis);
  const timer = useTimer();
  const recorder = useAudioRecorder();
  const browserSpeech = useBrowserSpeech();
  const localSpeech = useLocalSpeech(engine);
  const speech = engine === "browser" ? browserSpeech : localSpeech;
  const [editableTranscript, setEditableTranscript] = useState("");
  const prevQRef = useRef(0);

  const speakQuestion = (text: string) => {
    if (!voiceEnabled || !window.speechSynthesis) return;
    synthRef.current.cancel();
    const utter = new SpeechSynthesisUtterance(text);
    utter.rate = 0.95;
    utter.pitch = 1.0;
    utter.volume = 1.0;
    const voices = synthRef.current.getVoices();
    const preferred = voices.find((v) => v.name.includes("Google") || v.name.includes("Microsoft") || v.name.includes("Samantha"));
    if (preferred) utter.voice = preferred;
    utter.onstart = () => setIsSpeaking(true);
    utter.onend = () => setIsSpeaking(false);
    utter.onerror = () => setIsSpeaking(false);
    synthRef.current.speak(utter);
  };

  useEffect(() => {
    timer.start();
  }, []);
  useEffect(() => {
    setEditableTranscript(speech.transcript);
  }, [speech.transcript]);
  useEffect(() => {
    if (currentQ !== prevQRef.current) {
      speech.reset();
      setEditableTranscript("");
      setShowAnswer(false);
      setModelAnswer("");
      prevQRef.current = currentQ;
    }
    if (questions[currentQ]) {
      setTimeout(() => speakQuestion(questions[currentQ].question), 500);
    }
    return () => {
      synthRef.current.cancel();
    };
  }, [currentQ]);

  useEffect(() => {
    const t = setTimeout(() => {
      if (questions[0]) speakQuestion("Welcome to your interview. Let's begin. " + questions[0].question);
    }, 1000);
    return () => {
      clearTimeout(t);
      synthRef.current.cancel();
    };
  }, []);

  const question = questions[currentQ];
  const progress = ((currentQ + 1) / questions.length) * 100;

  const audioBlobsRef = useRef<Record<string, Blob>>({});
  const handleMicStart = () => {
    speech.startListening();
    recorder.startRecording();
  };
  const handleMicStop = async () => {
    speech.stopListening();
    const url = await recorder.stopRecording();
    if (url) {
      setAudioUrls((prev) => ({ ...prev, [question.id]: url }));
      try {
        const resp = await fetch(url);
        const blob = await resp.blob();
        audioBlobsRef.current[question.id] = blob;
      } catch (e) {
        console.error("Blob save error:", e);
      }
    }
  };

  const uploadRecording = async (questionId: string) => {
    const blob = audioBlobsRef.current[questionId];
    if (!blob) return;
    try {
      const formData = new FormData();
      formData.append("audio", blob, "recording.webm");
      formData.append("session_id", sessionId);
      formData.append("question_id", String(questionId));
      const token = getToken();
      await fetch(`${API}/recording/upload`, {
        method: "POST",
        headers: token ? { Authorization: `Bearer ${token}` } : {},
        body: formData,
      });
    } catch (e) {
      console.error("Upload error:", e);
    }
  };

  const handleShowAnswer = async () => {
    if (showAnswer) {
      setShowAnswer(false);
      return;
    }
    setLoadingAnswer(true);
    try {
      const res = await fetch(`${API}/question/${question.id}/answer?session_id=${sessionId}`);
      const data = await res.json();
      setModelAnswer(data.model_answer);
      setShowAnswer(true);
    } catch (e) {
      console.error(e);
    }
    setLoadingAnswer(false);
  };

  const handleSubmit = async () => {
    if (submitting || thinking) return;
    if (speech.listening) await handleMicStop();
    setSubmitting(true);
    try {
      await uploadRecording(question.id);
      await fetch(`${API}/answer/submit`, {
        method: "POST",
        headers: authHeaders(),
        body: JSON.stringify({ session_id: sessionId, question_id: question.id, transcript: editableTranscript }),
      });
    } catch (e) {
      console.error(e);
    }
    setSubmitting(false);
    setThinking(true);
    setTimeout(() => {
      setThinking(false);
      if (currentQ < questions.length - 1) setCurrentQ(currentQ + 1);
      else {
        timer.stop();
        onFinish(timer.format(), audioUrls);
      }
    }, 2000);
  };

  const handleSkip = () => {
    if (speech.listening) {
      speech.stopListening();
      recorder.stopRecording();
    }
    fetch(`${API}/answer/submit`, {
      method: "POST",
      headers: authHeaders(),
      body: JSON.stringify({ session_id: sessionId, question_id: question.id, transcript: "" }),
    }).catch(() => {});
    setThinking(true);
    setTimeout(() => {
      setThinking(false);
      if (currentQ < questions.length - 1) setCurrentQ(currentQ + 1);
      else {
        timer.stop();
        onFinish(timer.format(), audioUrls);
      }
    }, 1500);
  };

  const isProcessing = speech.processing || false;
  const isListening = speech.listening;

  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="min-h-screen flex flex-col p-4 md:p-6">
      <CameraPreview />
      <div className="glass rounded-xl px-5 py-3 flex items-center justify-between mb-4">
        <div className="flex items-center gap-4">
          <TopicBadge topic={question.topic} difficulty={question.difficulty} />
          <span className="text-indigo-400 text-sm font-semibold">
            Q {currentQ + 1}/{questions.length}
          </span>
        </div>
        <div className="flex items-center gap-4">
          <span className="text-slate-500 text-xs px-2 py-1 rounded-lg bg-slate-800/50">{engine}</span>
          <div className="flex items-center gap-2">
            <Clock className="w-4 h-4 text-slate-400" />
            <span className="text-white font-mono text-sm font-medium">{timer.format()}</span>
          </div>
        </div>
      </div>
      <div className="w-full bg-slate-800/50 rounded-full h-1 mb-6">
        <div
          className="bg-gradient-to-r from-indigo-500 to-purple-500 h-1 rounded-full transition-all duration-700"
          style={{ width: `${progress}%` }}
        ></div>
      </div>
      <div className="flex-1 max-w-3xl w-full mx-auto flex flex-col">
        <div className="glass-strong rounded-2xl p-6 mb-4 glow fade-in" key={currentQ}>
          <div className="flex items-start gap-4">
            <div className="w-11 h-11 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex-shrink-0 flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <div className="flex-1">
              <div className="flex items-center justify-between mb-2">
                <p className="text-indigo-400 text-xs font-semibold uppercase tracking-wider">AI Interviewer</p>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => speakQuestion(question.question)}
                    className="w-8 h-8 rounded-full bg-slate-700 hover:bg-slate-600 flex items-center justify-center transition-all"
                    title="Replay question"
                  >
                    <Volume2 className={`w-4 h-4 ${isSpeaking ? "text-indigo-400 animate-pulse" : "text-slate-400"}`} />
                  </button>
                  <button
                    onClick={() => {
                      setVoiceEnabled(!voiceEnabled);
                      if (voiceEnabled) synthRef.current.cancel();
                    }}
                    className={`w-8 h-8 rounded-full flex items-center justify-center transition-all ${
                      voiceEnabled ? "bg-indigo-600/30 text-indigo-400" : "bg-slate-700 text-slate-500"
                    }`}
                    title={voiceEnabled ? "Mute voice" : "Unmute voice"}
                  >
                    {voiceEnabled ? <Volume2 className="w-4 h-4" /> : <VolumeX className="w-4 h-4" />}
                  </button>
                </div>
              </div>
              {thinking ? (
                <div className="flex items-center gap-1.5 py-2">
                  <div className="w-2 h-2 rounded-full bg-indigo-400 thinking-dot"></div>
                  <div className="w-2 h-2 rounded-full bg-indigo-400 thinking-dot"></div>
                  <div className="w-2 h-2 rounded-full bg-indigo-400 thinking-dot"></div>
                  <span className="text-slate-500 text-sm ml-2">Processing...</span>
                </div>
              ) : (
                <p className="text-slate-200 text-base leading-relaxed">{question.question}</p>
              )}
            </div>
          </div>
        </div>
        {showAnswer && (
          <div className="glass rounded-2xl p-5 mb-4 border border-emerald-500/20 fade-in">
            <p className="text-emerald-400 text-xs font-semibold mb-2 uppercase tracking-wider">Model Answer</p>
            <p className="text-slate-300 text-sm leading-relaxed">{modelAnswer}</p>
          </div>
        )}
        <div className="flex-1 flex flex-col">
          <div className="flex items-center justify-center gap-6 mb-4">
            <MicButton listening={isListening} processing={isProcessing} onStart={handleMicStart} onStop={handleMicStop} />
            <WaveIndicator listening={isListening} />
            <div className="text-left">
              <p
                className={`text-sm font-medium ${
                  isProcessing
                    ? "text-amber-400"
                    : isListening
                    ? "text-red-400"
                    : audioUrls[question.id]
                    ? "text-emerald-400"
                    : "text-slate-400"
                }`}
              >
                {isProcessing
                  ? "Transcribing..."
                  : isListening
                  ? "Listening... speak now"
                  : audioUrls[question.id]
                  ? "Recording saved"
                  : "Record your answer (required)"}
              </p>
              {!audioUrls[question.id] && !isListening && (
                <p className="text-amber-400/70 text-[10px]">Voice recording is mandatory</p>
              )}
            </div>
          </div>
          {audioUrls[question.id] && !isListening && (
            <div className="flex items-center justify-center mb-3">
              <audio controls src={audioUrls[question.id]} className="h-8 opacity-70" style={{ filter: "invert(1)" }}></audio>
            </div>
          )}
          <div className="glass rounded-2xl p-1 flex-1 flex flex-col mb-4 relative">
            {isProcessing && (
              <div className="absolute top-2 right-3 flex items-center gap-1.5">
                <div className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse"></div>
                <span className="text-amber-400 text-[10px] font-medium">PROCESSING</span>
              </div>
            )}
            <textarea
              value={editableTranscript}
              onChange={(e) => setEditableTranscript(e.target.value)}
              disabled={thinking}
              placeholder={
                isListening
                  ? "Speak now..."
                  : audioUrls[question.id]
                  ? "Edit your transcript if needed..."
                  : "Record your answer first, then edit the transcript here."
              }
              className="flex-1 min-h-[120px] bg-transparent rounded-xl px-5 py-4 text-white placeholder-slate-600 resize-none text-sm leading-relaxed disabled:opacity-40"
            />
          </div>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <p className="text-slate-600 text-xs">{editableTranscript.split(/\s+/).filter(Boolean).length} words</p>
              <button
                onClick={handleShowAnswer}
                disabled={loadingAnswer}
                className="px-4 py-2 rounded-xl text-xs font-medium bg-emerald-600/20 text-emerald-400 hover:bg-emerald-600/30 border border-emerald-500/20 transition-all disabled:opacity-50"
              >
                {loadingAnswer ? "Loading..." : showAnswer ? "Hide Answer" : "Show Answer"}
              </button>
            </div>
            <div className="flex items-center gap-3">
              <button
                onClick={handleSkip}
                disabled={thinking || submitting}
                className="px-5 py-2.5 rounded-xl text-sm font-medium text-slate-400 hover:text-slate-300 hover:bg-slate-800/50 transition-all disabled:opacity-30"
              >
                Skip
              </button>
              <button
                onClick={handleSubmit}
                disabled={thinking || submitting || !editableTranscript.trim() || !audioUrls[question.id]}
                title={!audioUrls[question.id] ? "Record your answer first" : ""}
                className="px-8 py-3 rounded-xl font-semibold text-sm transition-all disabled:bg-slate-800 disabled:text-slate-600 disabled:cursor-not-allowed bg-indigo-600 hover:bg-indigo-500 text-white shadow-lg shadow-indigo-500/20"
              >
                {submitting
                  ? "Submitting..."
                  : !audioUrls[question.id]
                  ? "Record First"
                  : currentQ === questions.length - 1
                  ? "Finish"
                  : "Submit"}
              </button>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
