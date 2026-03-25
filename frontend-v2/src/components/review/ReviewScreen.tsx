import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { ClipboardList, ArrowLeft, Star } from "lucide-react";
import { apiFetch } from "@/lib/api";
import LoadingSpinner from "@/components/common/LoadingSpinner";

function Stars({ rating }: { rating: number }) {
  return (
    <div className="flex gap-0.5">
      {[1, 2, 3, 4, 5].map((i) => (
        <Star key={i} className={`w-3.5 h-3.5 ${i <= rating ? "text-amber-400 fill-amber-400" : "text-slate-700"}`} />
      ))}
    </div>
  );
}

interface ReviewScreenProps {
  onNavigate: (screen: string, params?: any) => void;
}

export default function ReviewScreen({ onNavigate }: ReviewScreenProps) {
  const [reviews, setReviews] = useState<any[]>([]);
  const [assessments, setAssessments] = useState<any[]>([]);
  const [selectedTopicResults, setSelectedTopicResults] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([apiFetch("/review/items").then((r) => r.json()), apiFetch("/learning/plan").then((r) => (r.ok ? r.json() : { topics: [] }))])
      .then(([revs, plan]) => {
        setReviews(revs);
        const completed = (plan.topics || []).filter((t: any) => t.status === "completed");
        setAssessments(completed);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  const viewAssessmentResults = async (topicId: string) => {
    const res = await apiFetch(`/review/topic/${topicId}/assessment`);
    const data = await res.json();
    setSelectedTopicResults(data);
  };

  if (loading) return <LoadingSpinner />;

  if (selectedTopicResults) {
    return (
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="max-w-3xl mx-auto p-4 md:p-6">
        <button
          onClick={() => setSelectedTopicResults(null)}
          className="text-slate-400 hover:text-white text-xs mb-4 inline-flex items-center gap-1"
        >
          <ArrowLeft className="w-3 h-3" />
          Back to Review
        </button>
        <h2 className="text-xl font-bold mb-4">Assessment Results</h2>
        <div className="space-y-3">
          {(selectedTopicResults.results || []).map((r: any, i: number) => (
            <div key={i} className="glass rounded-xl p-4">
              <p className="text-slate-300 text-sm font-medium mb-2">{r.question_text}</p>
              <div className="grid grid-cols-2 gap-3 mb-2">
                <div>
                  <p className="text-slate-500 text-xs mb-1">Your Answer</p>
                  <p className="text-slate-400 text-sm bg-slate-800/30 rounded-lg p-2">{r.user_answer || "-- skipped --"}</p>
                </div>
                <div>
                  <p className="text-emerald-400 text-xs mb-1">Correct Answer</p>
                  <p className="text-slate-300 text-sm bg-emerald-500/5 rounded-lg p-2">{r.correct_answer}</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <Stars rating={r.rating} />
                <span
                  className={`text-sm font-bold ${
                    r.score?.total_score >= 70 ? "text-emerald-400" : r.score?.total_score >= 40 ? "text-amber-400" : "text-red-400"
                  }`}
                >
                  {r.score?.total_score || 0}/100
                </span>
                {r.show_answer_used && <span className="text-amber-400 text-[10px]">Used Show Answer</span>}
              </div>
            </div>
          ))}
        </div>
      </motion.div>
    );
  }

  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="max-w-3xl mx-auto p-4 md:p-6">
      <h1 className="text-2xl font-bold mb-6 flex items-center gap-2">
        <ClipboardList className="w-6 h-6 text-indigo-400" />
        Review & Revisit
      </h1>

      {/* Marked for review */}
      {reviews.length > 0 && (
        <div className="mb-6">
          <h3 className="text-white text-sm font-semibold mb-3 uppercase tracking-wider">Marked for Review</h3>
          <div className="space-y-2">
            {reviews.map((r: any, i: number) => (
              <div
                key={i}
                className="glass rounded-xl p-4 flex items-center justify-between cursor-pointer hover:bg-white/[0.02]"
                onClick={() => onNavigate("learning", { topicId: r.topic_id })}
              >
                <div>
                  <p className="text-white text-sm font-medium">{r.topic_title}</p>
                  <p className="text-slate-500 text-xs">
                    {r.interest_area}
                    {r.dimension ? ` | ${r.dimension}` : ""}
                  </p>
                </div>
                <span className="text-indigo-400 text-xs">Revisit</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Completed topics */}
      <div>
        <h3 className="text-white text-sm font-semibold mb-3 uppercase tracking-wider">Completed Topics</h3>
        {assessments.length === 0 ? (
          <div className="glass rounded-xl p-6 text-center">
            <p className="text-slate-500 text-sm">No completed topics yet</p>
          </div>
        ) : (
          <div className="space-y-2">
            {assessments.map((t: any) => (
              <div key={t.topic_id} className="glass rounded-xl p-4 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Stars rating={t.assessment_rating} />
                  <div>
                    <p className="text-white text-sm font-medium">{t.title}</p>
                    <p className="text-slate-500 text-xs">{t.interest_area}</p>
                  </div>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => onNavigate("learning", { topicId: t.topic_id })}
                    className="px-3 py-1.5 rounded-lg text-xs text-slate-400 hover:text-white hover:bg-slate-800/50 transition-all"
                  >
                    Content
                  </button>
                  <button
                    onClick={() => viewAssessmentResults(t.topic_id)}
                    className="px-3 py-1.5 rounded-lg text-xs text-indigo-400 hover:text-indigo-300 hover:bg-indigo-600/10 transition-all"
                  >
                    Results
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </motion.div>
  );
}
