import { useState, useEffect, useRef } from "react";
import { motion } from "framer-motion";
import { Upload, Trash2, Loader2, AlertTriangle } from "lucide-react";
import { apiFetch, API } from "@/lib/api";
import { getToken, getUser } from "@/lib/auth";
import LoadingSpinner from "@/components/common/LoadingSpinner";

function CreateInterviewForm({
  resumes,
  userInterests,
  creating,
  onSubmit,
}: {
  resumes: any[];
  userInterests: string[];
  creating: boolean;
  onSubmit: (resumeId: string, interestArea: string) => void;
}) {
  const [selectedResume, setSelectedResume] = useState(resumes[0]?.id || "");
  const [selectedInterest, setSelectedInterest] = useState(userInterests[0] || "");
  const [allInterests, setAllInterests] = useState<string[]>([]);

  useEffect(() => {
    fetch(`${API}/config/interest-areas`)
      .then((r) => r.json())
      .then(setAllInterests)
      .catch(() => {});
  }, []);

  return (
    <div className="flex flex-wrap items-end gap-4">
      <div className="flex-1 min-w-[200px]">
        <label className="text-slate-400 text-xs mb-1 block">Resume</label>
        <select
          value={selectedResume}
          onChange={(e) => setSelectedResume(e.target.value)}
          className="w-full bg-slate-800/50 border border-slate-700/50 rounded-lg px-3 py-2 text-white text-sm"
        >
          {resumes.map((r: any) => (
            <option key={r.id} value={r.id}>
              {r.filename}
            </option>
          ))}
        </select>
      </div>
      <div className="flex-1 min-w-[200px]">
        <label className="text-slate-400 text-xs mb-1 block">Interest Area (questions will focus on this)</label>
        <select
          value={selectedInterest}
          onChange={(e) => setSelectedInterest(e.target.value)}
          className="w-full bg-slate-800/50 border border-slate-700/50 rounded-lg px-3 py-2 text-white text-sm"
        >
          {(allInterests.length > 0 ? allInterests : userInterests).map((i) => (
            <option key={i} value={i}>
              {i}
            </option>
          ))}
        </select>
      </div>
      <button
        onClick={() => onSubmit(selectedResume, selectedInterest)}
        disabled={creating || !selectedResume}
        className={`px-6 py-2.5 rounded-xl font-medium text-sm transition-all ${
          creating ? "bg-slate-700 text-slate-400" : "bg-emerald-600 hover:bg-emerald-500 text-white"
        }`}
      >
        {creating ? (
          <span className="flex items-center gap-2">
            <Loader2 className="w-4 h-4 animate-spin" />
            Generating Questions...
          </span>
        ) : (
          "Create Interview"
        )}
      </button>
    </div>
  );
}

interface AIInterviewHubProps {
  onNavigate: (screen: string, params?: any) => void;
}

export default function AIInterviewHub({ onNavigate }: AIInterviewHubProps) {
  const [resumes, setResumes] = useState<any[]>([]);
  const [interviews, setInterviews] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [creating, setCreating] = useState(false);
  const [llmStatus, setLlmStatus] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);
  const user = getUser();

  useEffect(() => {
    loadData();
    fetch(`${API}/config/llm-status`)
      .then((r) => r.json())
      .then(setLlmStatus)
      .catch(() => {});
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [rRes, iRes] = await Promise.all([apiFetch("/resume/list"), apiFetch("/ai-interview/list")]);
      setResumes(await rRes.json());
      setInterviews(await iRes.json());
    } catch (e) {
      setError("Failed to load data");
    }
    setLoading(false);
  };

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    setError(null);
    setSuccess(null);
    const formData = new FormData();
    formData.append("file", file);
    try {
      const res = await fetch(`${API}/resume/upload`, {
        method: "POST",
        headers: { Authorization: `Bearer ${getToken()}` },
        body: formData,
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error);
      setSuccess("Resume uploaded and parsed successfully!");
      loadData();
    } catch (e: any) {
      setError(e.message);
    }
    setUploading(false);
    if (fileRef.current) fileRef.current.value = "";
  };

  const handleCreateInterview = async (resumeId: string, interestArea: string) => {
    setCreating(true);
    setError(null);
    try {
      const res = await apiFetch("/ai-interview/create", {
        method: "POST",
        body: JSON.stringify({ resume_id: resumeId, interest_area: interestArea }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error);
      setSuccess("Interview created! Click 'Start' to begin.");
      loadData();
    } catch (e: any) {
      setError(e.message);
    }
    setCreating(false);
  };

  const statusColors: Record<string, string> = {
    pending: "text-yellow-400 bg-yellow-400/10",
    in_progress: "text-blue-400 bg-blue-400/10",
    completed: "text-green-400 bg-green-400/10",
    evaluated: "text-purple-400 bg-purple-400/10",
  };

  if (loading) return <LoadingSpinner />;

  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="max-w-5xl mx-auto px-4 py-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-white mb-2">AI Voice Interview</h1>
        <p className="text-slate-400 text-sm">
          Upload your resume, get AI-generated questions based on your interest area, and practice with an AI interviewer.
        </p>
      </div>

      {/* LLM Status Banner */}
      {llmStatus && !llmStatus.any_available && (
        <div className="glass border-amber-500/30 bg-amber-500/10 rounded-xl p-4 mb-6">
          <p className="text-amber-300 text-sm font-medium flex items-center gap-2">
            <AlertTriangle className="w-4 h-4" />
            No LLM API keys configured
          </p>
          <p className="text-amber-400/70 text-xs mt-1">
            Set ANTHROPIC_API_KEY, OPENAI_API_KEY, or GEMINI_API_KEY environment variable to enable AI features.
          </p>
        </div>
      )}

      {error && (
        <div className="bg-red-500/10 border border-red-500/30 text-red-300 px-4 py-3 rounded-xl text-sm mb-4">
          {error}
          <button onClick={() => setError(null)} className="ml-3 text-red-400">
            &times;
          </button>
        </div>
      )}
      {success && (
        <div className="bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 px-4 py-3 rounded-xl text-sm mb-4">
          {success}
          <button onClick={() => setSuccess(null)} className="ml-3 text-emerald-400">
            &times;
          </button>
        </div>
      )}

      {/* Step 1: Upload Resume */}
      <div className="glass rounded-2xl p-6 mb-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-8 h-8 rounded-full bg-indigo-600/30 flex items-center justify-center text-indigo-300 font-bold text-sm">1</div>
          <h2 className="text-lg font-semibold text-white">Upload Resume</h2>
        </div>
        <div className="flex items-center gap-4">
          <label
            className={`cursor-pointer px-5 py-2.5 rounded-xl font-medium text-sm transition-all ${
              uploading ? "bg-slate-700 text-slate-400" : "bg-indigo-600 hover:bg-indigo-500 text-white"
            }`}
          >
            {uploading ? (
              <span className="flex items-center gap-2">
                <Loader2 className="w-4 h-4 animate-spin" />
                Parsing...
              </span>
            ) : (
              <span className="flex items-center gap-2">
                <Upload className="w-4 h-4" />
                {resumes.length > 0 ? "Replace Resume" : "Upload PDF / DOCX"}
              </span>
            )}
            <input ref={fileRef} type="file" accept=".pdf,.docx,.doc,.txt" onChange={handleUpload} className="hidden" disabled={uploading} />
          </label>
          <span className="text-slate-500 text-xs">
            {resumes.length > 0 ? "Uploading a new resume will replace the existing one" : "Supported: PDF, DOCX, TXT (max 5MB)"}
          </span>
        </div>

        {/* Uploaded Resumes */}
        {resumes.length > 0 && (
          <div className="mt-4 space-y-2">
            {resumes.map((r: any) => (
              <div key={r.id} className="glass-strong rounded-xl p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-white text-sm font-medium">{r.filename}</p>
                    <p className="text-slate-500 text-xs mt-1">
                      {r.parsed_data?.skills?.slice(0, 5).join(", ") || "No skills detected"}
                      {r.parsed_data?.skills?.length > 5 && ` +${r.parsed_data.skills.length - 5} more`}
                    </p>
                    <p className="text-slate-600 text-xs mt-0.5">
                      {r.parsed_data?.experience_level || "?"} level | {r.parsed_data?.experience_years || 0} yrs exp
                    </p>
                  </div>
                  <div className="flex items-center gap-3">
                    <p className="text-slate-600 text-xs">{new Date(r.uploaded_at).toLocaleDateString()}</p>
                    <button
                      onClick={async () => {
                        if (!confirm("Delete this resume?")) return;
                        try {
                          await apiFetch(`/resume/${r.id}`, { method: "DELETE" });
                          loadData();
                        } catch (e) {
                          setError("Failed to delete");
                        }
                      }}
                      className="text-red-400/50 hover:text-red-400 transition-colors"
                      title="Delete resume"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Step 2: Create Interview */}
      {resumes.length > 0 && (
        <div className="glass rounded-2xl p-6 mb-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-8 h-8 rounded-full bg-emerald-600/30 flex items-center justify-center text-emerald-300 font-bold text-sm">
              2
            </div>
            <h2 className="text-lg font-semibold text-white">Start AI Interview</h2>
          </div>
          <p className="text-slate-400 text-sm mb-4">Select a resume and your interest area to generate personalized interview questions.</p>

          <CreateInterviewForm
            resumes={resumes}
            userInterests={user?.interest_areas || []}
            creating={creating}
            onSubmit={handleCreateInterview}
          />
        </div>
      )}

      {/* Step 3: Your Interviews */}
      {interviews.length > 0 && (
        <div className="glass rounded-2xl p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-8 h-8 rounded-full bg-purple-600/30 flex items-center justify-center text-purple-300 font-bold text-sm">
              3
            </div>
            <h2 className="text-lg font-semibold text-white">Your Interviews</h2>
          </div>
          <div className="space-y-3">
            {interviews.map((iv: any) => (
              <div key={iv.id} className="glass-strong rounded-xl p-4 flex items-center justify-between">
                <div>
                  <div className="flex items-center gap-2">
                    <p className="text-white text-sm font-medium">{iv.interest_area} Interview</p>
                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${statusColors[iv.status] || "text-slate-400 bg-slate-400/10"}`}>
                      {iv.status}
                    </span>
                  </div>
                  <p className="text-slate-500 text-xs mt-1">
                    {iv.total_questions} questions | {iv.job_role}
                  </p>
                  <p className="text-slate-600 text-xs">{new Date(iv.created_at).toLocaleDateString()}</p>
                </div>
                <div className="flex gap-2">
                  {iv.status === "pending" && (
                    <button
                      onClick={() => onNavigate("ai_interview_room", { interviewId: iv.id })}
                      className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-medium transition-all"
                    >
                      Start
                    </button>
                  )}
                  {iv.status === "in_progress" && (
                    <button
                      onClick={() => onNavigate("ai_interview_room", { interviewId: iv.id })}
                      className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-xs font-medium transition-all"
                    >
                      Resume
                    </button>
                  )}
                  {iv.status === "completed" && (
                    <button
                      onClick={() => onNavigate("ai_interview_room", { interviewId: iv.id, evaluate: true })}
                      className="px-4 py-2 bg-amber-600 hover:bg-amber-500 text-white rounded-lg text-xs font-medium transition-all"
                    >
                      Evaluate
                    </button>
                  )}
                  {iv.status === "evaluated" && (
                    <button
                      onClick={() => onNavigate("ai_results", { interviewId: iv.id })}
                      className="px-4 py-2 bg-purple-600 hover:bg-purple-500 text-white rounded-lg text-xs font-medium transition-all"
                    >
                      View Results
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </motion.div>
  );
}
