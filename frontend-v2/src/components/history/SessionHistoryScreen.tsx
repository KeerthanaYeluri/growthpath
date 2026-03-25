import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Clock, Star } from "lucide-react";
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

export default function SessionHistoryScreen() {
  const [history, setHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiFetch("/session/history")
      .then((r) => r.json())
      .then((h) => {
        setHistory(h);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  if (loading) return <LoadingSpinner />;

  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="max-w-3xl mx-auto p-4 md:p-6">
      <h1 className="text-2xl font-bold mb-6 flex items-center gap-2">
        <Clock className="w-6 h-6 text-indigo-400" />
        Session History
      </h1>
      {history.length === 0 ? (
        <div className="glass rounded-xl p-8 text-center">
          <p className="text-slate-500">No completed sessions yet</p>
        </div>
      ) : (
        <div className="space-y-3">
          {history.map((s: any) => (
            <div
              key={s.session_id}
              className="glass rounded-xl p-4 flex items-center justify-between hover:bg-white/[0.02] transition-colors"
            >
              <div>
                <p className="text-white text-sm font-medium">{s.role_name}</p>
                <p className="text-slate-500 text-xs">
                  {s.job_title} | {new Date(s.date).toLocaleDateString()}
                </p>
              </div>
              <div className="flex items-center gap-4">
                <div className="text-right">
                  <p
                    className={`text-lg font-bold ${
                      s.overall_score >= 75 ? "text-emerald-400" : s.overall_score >= 50 ? "text-amber-400" : "text-red-400"
                    }`}
                  >
                    {s.overall_score}/100
                  </p>
                  <p className="text-slate-600 text-xs">
                    {s.total_questions} Qs | {s.time_taken}
                  </p>
                </div>
                <Stars rating={Math.round(s.overall_score / 20)} />
              </div>
            </div>
          ))}
        </div>
      )}
    </motion.div>
  );
}
