import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Star, ChevronDown } from "lucide-react";
import { apiFetch } from "@/lib/api";

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

interface ResultsPageProps {
  scorecard: any;
  questionReview: any[];
  audioUrls: any;
  onRestart: () => void;
  sessionId: string;
}

export default function ResultsPage({ scorecard, questionReview, audioUrls: localAudioUrls, onRestart, sessionId }: ResultsPageProps) {
  const [animScore, setAnimScore] = useState(0);
  const [expandedQ, setExpandedQ] = useState<number | null>(null);
  const [serverAudioUrls, setServerAudioUrls] = useState<Record<string, string>>({});
  const score = scorecard.overall_score;

  const audioUrls = { ...serverAudioUrls, ...localAudioUrls };

  useEffect(() => {
    if (sessionId) {
      apiFetch(`/recording/list/${sessionId}`)
        .then((r) => r.json())
        .then((data) => {
          setServerAudioUrls(data);
        })
        .catch(() => {});
    }
  }, [sessionId]);

  useEffect(() => {
    if (score === 0) return;
    let s = 0;
    const step = Math.max(1500 / score, 10);
    const t = setInterval(() => {
      s++;
      setAnimScore(s);
      if (s >= score) clearInterval(t);
    }, step);
    return () => clearInterval(t);
  }, [score]);

  const scoreColor = score >= 75 ? "text-emerald-400" : score >= 50 ? "text-amber-400" : "text-red-400";
  const scoreBg =
    score >= 75 ? "from-emerald-500/20 to-emerald-500/5" : score >= 50 ? "from-amber-500/20 to-amber-500/5" : "from-red-500/20 to-red-500/5";
  const topicEntries = Object.entries(scorecard.topic_scores || {}).sort((a: any, b: any) => b[1] - a[1]);

  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="min-h-screen p-4 md:p-8">
      <div className="max-w-3xl mx-auto">
        <div className="text-center mb-8">
          <p className="text-indigo-400 text-xs font-semibold uppercase tracking-widest mb-2">Interview Complete</p>
          <h1 className="text-3xl font-bold mb-1">Your Scorecard</h1>
          <p className="text-slate-500 text-sm">
            {scorecard.candidate_name} | {scorecard.job_title} | {scorecard.time_taken}
          </p>
        </div>
        <div className={`glass-strong rounded-2xl p-8 text-center mb-6 ${score >= 75 ? "glow-green" : "glow"}`}>
          <div className={`inline-flex items-center justify-center w-36 h-36 rounded-full bg-gradient-to-b ${scoreBg} mb-4`}>
            <div>
              <span className={`text-5xl font-black ${scoreColor}`}>{animScore}</span>
              <span className="text-slate-500 text-xl font-medium">/100</span>
            </div>
          </div>
          <div className="flex justify-center mt-2">
            <Stars rating={Math.round(score / 20)} size="lg" />
          </div>
        </div>
        <div className="glass rounded-2xl p-6 mb-6">
          <h3 className="text-white text-sm font-semibold mb-4 uppercase tracking-wider">Topic Breakdown</h3>
          <div className="space-y-3">
            {topicEntries.map(([topic, s]: any) => (
              <div key={topic} className="flex items-center gap-3">
                <span className="text-slate-400 text-xs w-28 truncate">{topic}</span>
                <div className="flex-1 bg-slate-800/50 rounded-full h-2.5">
                  <div
                    className={`h-2.5 rounded-full transition-all duration-1000 ${
                      s >= 75 ? "bg-emerald-500" : s >= 50 ? "bg-amber-500" : "bg-red-500"
                    }`}
                    style={{ width: `${s}%` }}
                  ></div>
                </div>
                <span className="text-slate-400 text-xs font-mono w-10 text-right">{s}/100</span>
              </div>
            ))}
          </div>
        </div>
        <div className="grid md:grid-cols-2 gap-4 mb-6">
          <div className="glass rounded-2xl p-6">
            <h3 className="text-emerald-400 text-sm font-semibold mb-3 uppercase tracking-wider">Strengths</h3>
            <ul className="space-y-2">
              {(scorecard.strengths || []).map((s: string, i: number) => (
                <li key={i} className="flex items-start gap-2">
                  <span className="text-emerald-500 mt-0.5">&#8226;</span>
                  <span className="text-slate-300 text-sm">{s}</span>
                </li>
              ))}
            </ul>
          </div>
          <div className="glass rounded-2xl p-6">
            <h3 className="text-amber-400 text-sm font-semibold mb-3 uppercase tracking-wider">Improvements</h3>
            <ul className="space-y-2">
              {(scorecard.improvements || []).map((s: string, i: number) => (
                <li key={i} className="flex items-start gap-2">
                  <span className="text-amber-500 font-bold mt-0.5">{i + 1}.</span>
                  <span className="text-slate-300 text-sm">{s}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
        <div className="glass rounded-2xl overflow-hidden mb-6">
          <div className="px-6 py-4 border-b border-slate-700/30">
            <h3 className="text-white text-sm font-semibold uppercase tracking-wider">Deep Dive Review</h3>
            <p className="text-slate-500 text-xs mt-1">Click any question to see full analysis</p>
          </div>
          <div className="divide-y divide-slate-700/20 max-h-[700px] overflow-y-auto">
            {(questionReview || []).map((qr: any, i: number) => {
              const isOpen = expandedQ === i;
              const sc = qr.score;
              return (
                <div key={i}>
                  <button
                    onClick={() => setExpandedQ(isOpen ? null : i)}
                    className="w-full px-6 py-3.5 flex items-center justify-between hover:bg-white/[0.02] transition-colors text-left"
                  >
                    <div className="flex items-center gap-3">
                      <span className="text-indigo-400 text-xs font-bold w-7">Q{i + 1}</span>
                      <span className="text-slate-500 text-xs w-24">{qr.topic}</span>
                      <span className="text-slate-300 text-sm truncate max-w-[300px]">{qr.question_text.substring(0, 60)}...</span>
                    </div>
                    <div className="flex items-center gap-3">
                      {audioUrls[qr.question_id] && <span className="text-slate-600 text-[10px]">REC</span>}
                      <span
                        className={`text-xs font-bold px-2 py-1 rounded-lg ${
                          sc.total_score >= 70
                            ? "bg-emerald-500/20 text-emerald-400"
                            : sc.total_score >= 40
                            ? "bg-amber-500/20 text-amber-400"
                            : "bg-red-500/20 text-red-400"
                        }`}
                      >
                        {sc.total_score}/100
                      </span>
                      <ChevronDown className={`w-4 h-4 text-slate-500 transition-transform ${isOpen ? "rotate-180" : ""}`} />
                    </div>
                  </button>
                  {isOpen && (
                    <div className="px-6 pb-5 fade-in">
                      <p className="text-slate-300 text-sm mb-3 font-medium">{qr.question_text}</p>
                      {audioUrls[qr.question_id] && (
                        <div className="mb-3">
                          <p className="text-slate-500 text-xs mb-1 uppercase tracking-wider">Your Recording</p>
                          <audio
                            controls
                            src={audioUrls[qr.question_id]}
                            className="w-full h-8 opacity-70"
                            style={{ filter: "invert(1)" }}
                          ></audio>
                        </div>
                      )}
                      <div className="mb-3">
                        <p className="text-slate-500 text-xs mb-1 uppercase tracking-wider">Your Answer</p>
                        <p className="text-slate-400 text-sm italic bg-slate-800/30 rounded-xl p-3">
                          {qr.transcript ? `"${qr.transcript}"` : "-- Skipped --"}
                        </p>
                      </div>
                      {qr.model_answer && (
                        <div className="mb-3">
                          <p className="text-emerald-400 text-xs mb-1 uppercase tracking-wider">Expected Answer</p>
                          <p className="text-slate-300 text-sm bg-emerald-500/5 border border-emerald-500/10 rounded-xl p-3">
                            {qr.model_answer}
                          </p>
                        </div>
                      )}
                      <div className="grid grid-cols-3 gap-2 mb-3">
                        <div className="bg-slate-800/30 rounded-lg p-2 text-center">
                          <p className="text-slate-500 text-[10px] uppercase">Keywords</p>
                          <p className="text-white text-sm font-bold">{sc.keyword_score}%</p>
                        </div>
                        <div className="bg-slate-800/30 rounded-lg p-2 text-center">
                          <p className="text-slate-500 text-[10px] uppercase">Detail</p>
                          <p className="text-white text-sm font-bold">{sc.detail_score}%</p>
                        </div>
                        <div className="bg-slate-800/30 rounded-lg p-2 text-center">
                          <p className="text-slate-500 text-[10px] uppercase">Relevance</p>
                          <p className="text-white text-sm font-bold">{sc.relevance_score}%</p>
                        </div>
                      </div>
                      <div className="flex flex-wrap gap-1.5 mb-2">
                        {(sc.matched_keywords || []).map((k: string, j: number) => (
                          <span key={j} className="px-2 py-0.5 rounded-full text-[10px] bg-emerald-500/20 text-emerald-400">
                            {k}
                          </span>
                        ))}
                        {(sc.missed_keywords || []).map((k: string, j: number) => (
                          <span key={j} className="px-2 py-0.5 rounded-full text-[10px] bg-red-500/20 text-red-400 line-through">
                            {k}
                          </span>
                        ))}
                      </div>
                      <p className="text-slate-400 text-xs">{sc.feedback}</p>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
        <div className="text-center pb-8">
          <button
            onClick={onRestart}
            className="px-10 py-3.5 rounded-xl font-semibold text-sm bg-indigo-600 hover:bg-indigo-500 text-white shadow-lg shadow-indigo-500/20 transition-all"
          >
            Back to Dashboard
          </button>
        </div>
      </div>
    </motion.div>
  );
}
