import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Mic, Loader2 } from "lucide-react";
import { apiFetch } from "@/lib/api";
import EnginePicker from "@/components/common/EnginePicker";

interface HomeScreenProps {
  onStart: Function;
  onStartJD: Function;
  user: any;
}

export default function HomeScreen({ onStart, onStartJD, user }: HomeScreenProps) {
  const [name, setName] = useState(user?.full_name || "");
  const [jobTitle, setJobTitle] = useState("");
  const [jobDescription, setJobDescription] = useState("");
  const [micOk, setMicOk] = useState<boolean | null>(null);
  const [engine, setEngine] = useState("whisper");
  const [detectedRole, setDetectedRole] = useState<any>(null);
  const [mode, setMode] = useState("jd");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    (async () => {
      try {
        const s = await navigator.mediaDevices.getUserMedia({ audio: true });
        s.getTracks().forEach((t) => t.stop());
        setMicOk(true);
      } catch {
        setMicOk(false);
      }
    })();
    apiFetch("/interview/detect-role")
      .then((r) => r.json())
      .then((data) => {
        if (data.role_name) {
          setDetectedRole(data);
          setJobTitle(data.role_name);
        }
      })
      .catch(() => {});
  }, []);

  const handleStartJD = async () => {
    if (!name.trim() || !jobDescription.trim() || !micOk) return;
    setLoading(true);
    await onStartJD(name.trim(), jobDescription.trim(), engine);
    setLoading(false);
  };

  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="max-w-lg mx-auto p-4 md:p-6">
      <div className="glass-strong rounded-2xl p-8 glow">
        <div className="text-center mb-6">
          <div className="w-14 h-14 rounded-2xl bg-indigo-500/20 mx-auto mb-3 flex items-center justify-center">
            <Mic className="w-7 h-7 text-indigo-400" />
          </div>
          <h1 className="text-2xl font-bold mb-1">AI Interview Booth</h1>
          <p className="text-slate-400 text-sm">Voice-powered technical interview simulator</p>
        </div>

        {/* Mode Toggle */}
        <div className="flex bg-slate-800/60 rounded-xl p-1 mb-4">
          <button
            onClick={() => setMode("jd")}
            className={`flex-1 py-2 rounded-lg text-xs font-semibold transition-all ${
              mode === "jd" ? "bg-indigo-600 text-white shadow" : "text-slate-400 hover:text-slate-300"
            }`}
          >
            Job Description (AI)
          </button>
          <button
            onClick={() => setMode("role")}
            className={`flex-1 py-2 rounded-lg text-xs font-semibold transition-all ${
              mode === "role" ? "bg-indigo-600 text-white shadow" : "text-slate-400 hover:text-slate-300"
            }`}
          >
            Quick Role-Based
          </button>
        </div>

        {detectedRole && mode === "role" && (
          <div className="bg-indigo-500/10 border border-indigo-500/20 rounded-xl px-4 py-2.5 mb-3 fade-in">
            <p className="text-indigo-300 text-xs font-medium">Auto-detected from your profile:</p>
            <p className="text-indigo-400 text-sm font-semibold">{detectedRole.role_name}</p>
            <p className="text-slate-500 text-[10px]">Based on interests: {detectedRole.interests.join(", ")}</p>
          </div>
        )}

        <div className="space-y-3">
          <div>
            <label className="block text-slate-400 text-xs font-medium mb-1.5 uppercase tracking-wider">Your Name</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Enter your full name"
              className="w-full bg-slate-800/60 border border-slate-700/50 rounded-xl px-4 py-2.5 text-white text-sm placeholder-slate-600 focus:border-indigo-500/50 transition-all"
            />
          </div>

          {mode === "jd" ? (
            <div>
              <label className="block text-slate-400 text-xs font-medium mb-1.5 uppercase tracking-wider">Paste Job Description</label>
              <textarea
                value={jobDescription}
                onChange={(e) => setJobDescription(e.target.value)}
                placeholder="Paste the full job description here... AI will generate tailored interview questions based on the required skills, responsibilities, and qualifications mentioned."
                rows={6}
                className="w-full bg-slate-800/60 border border-slate-700/50 rounded-xl px-4 py-2.5 text-white text-sm placeholder-slate-600 focus:border-indigo-500/50 transition-all resize-none"
              />
              <p className="text-slate-600 text-[10px] mt-1">
                {jobDescription.length} chars {jobDescription.length < 50 && jobDescription.length > 0 ? "(min 50 required)" : ""}
              </p>
            </div>
          ) : (
            <div>
              <label className="block text-slate-400 text-xs font-medium mb-1.5 uppercase tracking-wider">
                Target Job Title / Role
              </label>
              <input
                type="text"
                value={jobTitle}
                onChange={(e) => setJobTitle(e.target.value)}
                placeholder="e.g. SDET, DevOps Engineer"
                className="w-full bg-slate-800/60 border border-slate-700/50 rounded-xl px-4 py-2.5 text-white text-sm placeholder-slate-600 focus:border-indigo-500/50 transition-all"
              />
              <p className="text-slate-600 text-[10px] mt-1">Uses pre-built question bank (no AI needed)</p>
            </div>
          )}

          <div>
            <label className="block text-slate-400 text-xs font-medium mb-2 uppercase tracking-wider">Speech Engine</label>
            <EnginePicker engine={engine} onChange={setEngine} />
          </div>
          <div
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm ${
              micOk === true
                ? "bg-emerald-500/10 text-emerald-400"
                : micOk === false
                ? "bg-red-500/10 text-red-400"
                : "bg-slate-800/50 text-slate-400"
            }`}
          >
            <div
              className={`w-2 h-2 rounded-full ${
                micOk === true ? "bg-emerald-400" : micOk === false ? "bg-red-400" : "bg-slate-500"
              }`}
            ></div>
            {micOk === true
              ? "Microphone ready (recording required)"
              : micOk === false
              ? "Microphone access required for interview"
              : "Checking microphone..."}
          </div>

          {mode === "jd" ? (
            <button
              onClick={handleStartJD}
              disabled={!name.trim() || jobDescription.length < 50 || !micOk || loading}
              className="w-full py-3 rounded-xl font-semibold text-sm transition-all disabled:bg-slate-800 disabled:text-slate-600 disabled:cursor-not-allowed bg-indigo-600 hover:bg-indigo-500 text-white shadow-lg shadow-indigo-500/20"
            >
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <Loader2 className="w-4 h-4 animate-spin" />
                  AI is preparing your interview...
                </span>
              ) : (
                "Start AI Interview"
              )}
            </button>
          ) : (
            <button
              onClick={() => name.trim() && jobTitle.trim() && micOk && onStart(name.trim(), jobTitle.trim(), engine)}
              disabled={!name.trim() || !jobTitle.trim() || !micOk}
              className="w-full py-3 rounded-xl font-semibold text-sm transition-all disabled:bg-slate-800 disabled:text-slate-600 disabled:cursor-not-allowed bg-indigo-600 hover:bg-indigo-500 text-white shadow-lg shadow-indigo-500/20"
            >
              Start Interview
            </button>
          )}
        </div>
        <div className="mt-4 grid grid-cols-3 gap-2 text-center">
          <div className="glass rounded-lg py-2">
            <p className="text-indigo-400 text-lg font-bold">{mode === "jd" ? "15" : "30"}</p>
            <p className="text-slate-500 text-[10px]">Questions</p>
          </div>
          <div className="glass rounded-lg py-2">
            <p className="text-indigo-400 text-lg font-bold">{mode === "jd" ? "AI" : "10"}</p>
            <p className="text-slate-500 text-[10px]">{mode === "jd" ? "Generated" : "Topics"}</p>
          </div>
          <div className="glass rounded-lg py-2">
            <p className="text-indigo-400 text-lg font-bold">{mode === "jd" ? "~30m" : "~1h"}</p>
            <p className="text-slate-500 text-[10px]">Duration</p>
          </div>
        </div>
        {mode === "jd" && (
          <div className="mt-3 bg-indigo-500/10 border border-indigo-500/20 rounded-xl px-4 py-3">
            <p className="text-indigo-300 text-xs font-medium mb-1">How it works:</p>
            <ul className="text-slate-400 text-[11px] space-y-0.5">
              <li>1. Paste any job description</li>
              <li>2. AI generates tailored interview questions</li>
              <li>3. Questions are read aloud by voice</li>
              <li>4. Answer with your microphone</li>
              <li>5. Get detailed scoring and feedback</li>
            </ul>
          </div>
        )}
      </div>
    </motion.div>
  );
}
