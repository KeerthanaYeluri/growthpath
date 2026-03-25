import { useState, useEffect, useRef } from "react";
import { motion } from "framer-motion";
import { BookOpen, Check, ArrowLeft, Bookmark, ChevronLeft, ChevronRight, Star } from "lucide-react";
import { apiFetch } from "@/lib/api";
import { marked } from "marked";
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

interface LearningScreenProps {
  initialTopicId?: string;
  onNavigate: (screen: string, params?: any) => void;
}

export default function LearningScreen({ initialTopicId, onNavigate }: LearningScreenProps) {
  const [plan, setPlan] = useState<any>(null);
  const [selectedTopic, setSelectedTopic] = useState<any>(null);
  const [topicContent, setTopicContent] = useState<any>(null);
  const [activeDim, setActiveDim] = useState("interview");
  const [dimContent, setDimContent] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [loadingContent, setLoadingContent] = useState(false);
  const contentRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    apiFetch("/learning/plan")
      .then((r) => (r.ok ? r.json() : null))
      .then((p) => {
        setPlan(p);
        setLoading(false);
        if (initialTopicId && p) {
          const topic = p.topics.find((t: any) => t.topic_id === initialTopicId);
          if (topic) loadTopic(topic);
        }
      })
      .catch(() => setLoading(false));
  }, []);

  const loadTopic = async (topic: any) => {
    setSelectedTopic(topic);
    setTopicContent(null);
    setDimContent(null);
    try {
      const res = await apiFetch(`/learning/topic/${topic.topic_id}/content`);
      if (res.ok) {
        const data = await res.json();
        setTopicContent(data);
        loadDimension(topic.topic_id, "interview");
      } else {
        setTopicContent({ dimensions: {}, title: topic.title, noContent: true });
      }
    } catch {
      setTopicContent({ dimensions: {}, title: topic.title, noContent: true });
    }
  };

  const loadDimension = async (topicId: string, dim: string) => {
    setActiveDim(dim);
    setDimContent(null);
    setLoadingContent(true);
    try {
      const res = await apiFetch(`/learning/topic/${topicId}/content?dimension=${dim}`);
      if (res.ok) {
        const data = await res.json();
        setDimContent(data);
        if (data.bookmark && contentRef.current) {
          setTimeout(() => {
            if (contentRef.current) contentRef.current.scrollTop = (data.bookmark.scroll_pct / 100) * contentRef.current.scrollHeight;
          }, 100);
        }
      }
    } catch {}
    setLoadingContent(false);
  };

  const handleSaveBookmark = async () => {
    if (!selectedTopic || !contentRef.current) return;
    const scrollPct = (contentRef.current.scrollTop / contentRef.current.scrollHeight) * 100;
    await apiFetch(`/learning/topic/${selectedTopic.topic_id}/bookmark`, {
      method: "POST",
      body: JSON.stringify({ dimension: activeDim, position: contentRef.current.scrollTop, scroll_pct: scrollPct }),
    });
  };

  const handleCompleteDimension = async () => {
    if (!selectedTopic) return;
    await apiFetch(`/learning/topic/${selectedTopic.topic_id}/dimension/${activeDim}/complete`, { method: "POST" });
    const res = await apiFetch("/learning/plan");
    if (res.ok) {
      const p = await res.json();
      setPlan(p);
      const updated = p.topics.find((t: any) => t.topic_id === selectedTopic.topic_id);
      if (updated) setSelectedTopic(updated);
    }
    loadTopic(selectedTopic);
  };

  const handleMarkReview = async () => {
    if (!selectedTopic) return;
    await apiFetch(`/learning/topic/${selectedTopic.topic_id}/review`, {
      method: "POST",
      body: JSON.stringify({ dimension: activeDim }),
    });
  };

  if (loading) return <LoadingSpinner />;
  if (!plan)
    return (
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="max-w-2xl mx-auto p-6 text-center">
        <div className="glass rounded-xl p-8">
          <p className="text-slate-400 mb-4">No learning plan found. Go to Profile to set up your interests and generate a plan.</p>
          <button onClick={() => onNavigate("profile")} className="px-5 py-2 rounded-xl text-sm font-medium bg-indigo-600 text-white">
            Go to Profile
          </button>
        </div>
      </motion.div>
    );

  // Topic list view
  if (!selectedTopic) {
    return (
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="max-w-4xl mx-auto p-4 md:p-6">
        <h1 className="text-2xl font-bold mb-2 flex items-center gap-2">
          <BookOpen className="w-6 h-6 text-indigo-400" />
          Learning Path
        </h1>
        <p className="text-slate-500 text-sm mb-6">
          {plan.topics.filter((t: any) => t.status === "completed").length}/{plan.topics.length} topics completed | Target:{" "}
          {plan.expected_completion}
        </p>
        <div className="space-y-2">
          {plan.topics.map((topic: any, i: number) => {
            const dimsDone = topic.dimensions_completed ? topic.dimensions_completed.length : 0;
            const statusColors: Record<string, string> = {
              completed: "border-emerald-500/30 bg-emerald-500/5",
              content_complete: "border-blue-500/30 bg-blue-500/5",
              in_progress: "border-amber-500/30 bg-amber-500/5",
              not_started: "border-slate-700/30",
            };
            return (
              <div
                key={topic.topic_id}
                onClick={() => loadTopic(topic)}
                className={`glass rounded-xl p-4 cursor-pointer hover:bg-white/[0.02] transition-all border ${statusColors[topic.status] || ""}`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <span className="text-slate-600 text-xs w-5">{i + 1}</span>
                    <div
                      className={`w-3 h-3 rounded-full ${
                        topic.status === "completed"
                          ? "bg-emerald-400"
                          : topic.status === "in_progress"
                          ? "bg-amber-400"
                          : topic.status === "content_complete"
                          ? "bg-blue-400"
                          : "bg-slate-700"
                      }`}
                    ></div>
                    <div>
                      <p className="text-white text-sm font-medium">{topic.title}</p>
                      <p className="text-slate-500 text-xs">
                        {topic.interest_area} | {topic.estimated_hours}h est.
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-slate-600 text-xs">{dimsDone}/4 dims</span>
                    {topic.assessment_rating && <Stars rating={topic.assessment_rating} />}
                    <span className="text-slate-600 text-xs">{topic.revised_end_date}</span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </motion.div>
    );
  }

  // Topic detail view with content
  const dimensions = ["interview", "deep_dive", "best_practices", "tips_tricks"];
  const dimLabels: Record<string, string> = {
    interview: "Interview Prep",
    deep_dive: "Deep Dive",
    best_practices: "Best Practices",
    tips_tricks: "Tips & Tricks",
  };
  const allDimsComplete = selectedTopic.dimensions_completed && selectedTopic.dimensions_completed.length >= 4;

  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="max-w-4xl mx-auto p-4 md:p-6">
      {/* Back + Title */}
      <div className="flex items-center gap-3 mb-4">
        <button
          onClick={() => {
            setSelectedTopic(null);
            setTopicContent(null);
            setDimContent(null);
          }}
          className="px-3 py-1.5 rounded-lg text-xs text-slate-400 hover:text-white hover:bg-slate-800/50 transition-all flex items-center gap-1"
        >
          <ArrowLeft className="w-3 h-3" />
          Back
        </button>
        <div>
          <h1 className="text-xl font-bold">{selectedTopic.title}</h1>
          <p className="text-slate-500 text-xs">
            {selectedTopic.interest_area} | {selectedTopic.estimated_hours}h estimated
          </p>
        </div>
      </div>

      {/* Dimension Tabs */}
      <div className="flex gap-2 mb-4 overflow-x-auto">
        {dimensions.map((dim) => {
          const isComplete = selectedTopic.dimensions_completed && selectedTopic.dimensions_completed.includes(dim);
          return (
            <button
              key={dim}
              onClick={() => loadDimension(selectedTopic.topic_id, dim)}
              className={`px-4 py-2 rounded-xl text-xs font-medium whitespace-nowrap transition-all flex items-center gap-1.5 ${
                activeDim === dim ? "bg-indigo-600/30 border border-indigo-500/40 text-indigo-300" : "glass text-slate-400 hover:text-slate-300"
              }`}
            >
              {isComplete && <Check className="w-3 h-3 text-emerald-400" />}
              {dimLabels[dim]}
            </button>
          );
        })}
      </div>

      {/* Content Area */}
      {topicContent?.noContent ? (
        <div className="glass rounded-xl p-8 text-center">
          <p className="text-slate-500">Content coming soon for this topic.</p>
          <p className="text-slate-600 text-xs mt-2">{selectedTopic.description}</p>
        </div>
      ) : loadingContent ? (
        <LoadingSpinner />
      ) : dimContent ? (
        <div className="glass rounded-xl overflow-hidden">
          <div
            ref={contentRef}
            className="p-6 max-h-[60vh] overflow-y-auto md-content"
            onScroll={handleSaveBookmark}
            dangerouslySetInnerHTML={{ __html: marked.parse(dimContent.content || "") as string }}
          ></div>
          <div className="border-t border-slate-700/30 px-6 py-3 flex items-center justify-between">
            <div className="flex gap-2">
              <button
                onClick={handleCompleteDimension}
                className="px-4 py-2 rounded-xl text-xs font-medium bg-emerald-600/20 text-emerald-400 hover:bg-emerald-600/30 border border-emerald-500/20 transition-all flex items-center gap-1"
              >
                <Check className="w-3 h-3" />
                Mark Complete
              </button>
              <button
                onClick={handleMarkReview}
                className="px-4 py-2 rounded-xl text-xs font-medium bg-amber-600/20 text-amber-400 hover:bg-amber-600/30 border border-amber-500/20 transition-all flex items-center gap-1"
              >
                <Bookmark className="w-3 h-3" />
                Mark for Review
              </button>
            </div>
            <div className="flex gap-2">
              {activeDim !== "interview" && (
                <button
                  onClick={() => loadDimension(selectedTopic.topic_id, dimensions[dimensions.indexOf(activeDim) - 1])}
                  className="px-3 py-1.5 rounded-lg text-xs text-slate-400 hover:text-white transition-all flex items-center gap-1"
                >
                  <ChevronLeft className="w-3 h-3" />
                  Prev
                </button>
              )}
              {activeDim !== "tips_tricks" && (
                <button
                  onClick={() => loadDimension(selectedTopic.topic_id, dimensions[dimensions.indexOf(activeDim) + 1])}
                  className="px-3 py-1.5 rounded-lg text-xs text-indigo-400 hover:text-indigo-300 transition-all flex items-center gap-1"
                >
                  Next
                  <ChevronRight className="w-3 h-3" />
                </button>
              )}
            </div>
          </div>
        </div>
      ) : null}

      {/* Assessment trigger */}
      {allDimsComplete && selectedTopic.status !== "completed" && (
        <div className="mt-4 glass rounded-xl p-5 border border-indigo-500/20 text-center fade-in">
          <p className="text-indigo-300 text-sm font-medium mb-2">All 4 dimensions complete!</p>
          <p className="text-slate-500 text-xs mb-3">Take the 5-question assessment to earn your topic rating.</p>
          <button
            onClick={() => onNavigate("assessment", { topicId: selectedTopic.topic_id, topicTitle: selectedTopic.title })}
            className="px-6 py-2.5 rounded-xl text-sm font-medium bg-indigo-600 hover:bg-indigo-500 text-white transition-all"
          >
            Start Assessment
          </button>
        </div>
      )}
    </motion.div>
  );
}
