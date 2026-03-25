import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { User, Save, RefreshCw } from "lucide-react";
import { apiFetch } from "@/lib/api";
import { API } from "@/lib/api";
import LoadingSpinner from "@/components/common/LoadingSpinner";

interface ProfileScreenProps {
  onNavigate: (screen: string, params?: any) => void;
}

export default function ProfileScreen({ onNavigate }: ProfileScreenProps) {
  const [profile, setProfile] = useState<any>(null);
  const [editing, setEditing] = useState(false);
  const [form, setForm] = useState<any>({});
  const [techOptions, setTechOptions] = useState<string[]>([]);
  const [interestOptions, setInterestOptions] = useState<string[]>([]);
  const [saving, setSaving] = useState(false);
  const [msg, setMsg] = useState("");

  useEffect(() => {
    apiFetch("/auth/profile")
      .then((r) => r.json())
      .then((p) => {
        setProfile(p);
        setForm(p);
      });
    fetch(`${API}/config/tech-stacks`)
      .then((r) => r.json())
      .then(setTechOptions)
      .catch(() => {});
    fetch(`${API}/config/interest-areas`)
      .then((r) => r.json())
      .then(setInterestOptions)
      .catch(() => {});
  }, []);

  const toggleTag = (field: string, item: string) => {
    setForm((prev: any) => ({
      ...prev,
      [field]: prev[field].includes(item) ? prev[field].filter((i: string) => i !== item) : [...prev[field], item],
    }));
  };

  const handleSave = async () => {
    setSaving(true);
    setMsg("");
    try {
      const res = await apiFetch("/auth/profile", { method: "PUT", body: JSON.stringify(form) });
      const data = await res.json();
      if (res.ok) {
        setProfile(data);
        setEditing(false);
        setMsg("Profile updated!");
        setTimeout(() => setMsg(""), 3000);
      }
    } catch {}
    setSaving(false);
  };

  if (!profile) return <LoadingSpinner />;

  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="max-w-2xl mx-auto p-4 md:p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Profile</h1>
        {!editing ? (
          <button
            onClick={() => setEditing(true)}
            className="px-4 py-2 rounded-xl text-sm font-medium bg-indigo-600/20 text-indigo-400 hover:bg-indigo-600/30 transition-all"
          >
            Edit
          </button>
        ) : (
          <div className="flex gap-2">
            <button
              onClick={() => {
                setEditing(false);
                setForm(profile);
              }}
              className="px-4 py-2 rounded-xl text-sm text-slate-400 hover:text-slate-300"
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              disabled={saving}
              className="px-4 py-2 rounded-xl text-sm font-medium bg-indigo-600 text-white hover:bg-indigo-500 disabled:opacity-50 flex items-center gap-1.5"
            >
              <Save className="w-3.5 h-3.5" />
              {saving ? "Saving..." : "Save"}
            </button>
          </div>
        )}
      </div>
      {msg && (
        <div className="bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 px-4 py-2 rounded-xl text-sm mb-4">
          {msg}
        </div>
      )}
      <div className="glass rounded-xl p-6 space-y-5">
        <div>
          <label className="block text-slate-400 text-xs font-medium mb-1.5 uppercase tracking-wider">Name</label>
          {editing ? (
            <input
              type="text"
              value={form.full_name || ""}
              onChange={(e) => setForm({ ...form, full_name: e.target.value })}
              className="w-full bg-slate-800/60 border border-slate-700/50 rounded-xl px-4 py-2.5 text-white text-sm"
            />
          ) : (
            <p className="text-white text-sm">{profile.full_name}</p>
          )}
        </div>
        <div>
          <label className="block text-slate-400 text-xs font-medium mb-1.5 uppercase tracking-wider">Email</label>
          <p className="text-slate-400 text-sm">{profile.email}</p>
        </div>
        <div>
          <label className="block text-slate-400 text-xs font-medium mb-2 uppercase tracking-wider">Tech Stack</label>
          {editing ? (
            <div className="flex flex-wrap gap-1.5">
              {techOptions.map((t) => (
                <button
                  key={t}
                  onClick={() => toggleTag("tech_stack", t)}
                  className={`tag-pill ${
                    (form.tech_stack || []).includes(t)
                      ? "bg-indigo-600/30 border border-indigo-500/40 text-indigo-300"
                      : "bg-slate-800/60 border border-slate-700/40 text-slate-500 hover:text-slate-300"
                  }`}
                >
                  {t}
                </button>
              ))}
            </div>
          ) : (
            <div className="flex flex-wrap gap-1.5">
              {(profile.tech_stack || []).map((t: string) => (
                <span key={t} className="tag-pill bg-indigo-600/20 text-indigo-300">
                  {t}
                </span>
              ))}
            </div>
          )}
        </div>
        <div>
          <label className="block text-slate-400 text-xs font-medium mb-2 uppercase tracking-wider">Interest Areas</label>
          {editing ? (
            <div className="flex flex-wrap gap-1.5">
              {interestOptions.map((t) => (
                <button
                  key={t}
                  onClick={() => toggleTag("interest_areas", t)}
                  className={`tag-pill ${
                    (form.interest_areas || []).includes(t)
                      ? "bg-emerald-600/30 border border-emerald-500/40 text-emerald-300"
                      : "bg-slate-800/60 border border-slate-700/40 text-slate-500 hover:text-slate-300"
                  }`}
                >
                  {t}
                </button>
              ))}
            </div>
          ) : (
            <div className="flex flex-wrap gap-1.5">
              {(profile.interest_areas || []).map((t: string) => (
                <span key={t} className="tag-pill bg-emerald-600/20 text-emerald-300">
                  {t}
                </span>
              ))}
            </div>
          )}
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-slate-400 text-xs font-medium mb-1.5 uppercase tracking-wider">Hours/Day</label>
            {editing ? (
              <input
                type="range"
                min="0.5"
                max="8"
                step="0.5"
                value={form.hours_per_day || 2}
                onChange={(e) => setForm({ ...form, hours_per_day: parseFloat(e.target.value) })}
                className="w-full accent-indigo-500"
              />
            ) : null}
            <p className="text-white text-sm">{(editing ? form.hours_per_day : profile.hours_per_day) || 2} hours</p>
          </div>
          <div>
            <label className="block text-slate-400 text-xs font-medium mb-1.5 uppercase tracking-wider">
              Daily Question Limit
            </label>
            {editing ? (
              <input
                type="number"
                min="15"
                max="30"
                value={form.daily_limit || 20}
                onChange={(e) => setForm({ ...form, daily_limit: parseInt(e.target.value) })}
                className="w-full bg-slate-800/60 border border-slate-700/50 rounded-xl px-4 py-2 text-white text-sm"
              />
            ) : (
              <p className="text-white text-sm">{profile.daily_limit || 20} questions</p>
            )}
          </div>
        </div>
      </div>
      <div className="mt-4 glass rounded-xl p-4">
        <button
          onClick={async () => {
            const res = await apiFetch("/learning/generate-plan", { method: "POST" });
            if (res.ok) {
              setMsg("Learning plan regenerated!");
              setTimeout(() => setMsg(""), 3000);
            }
          }}
          className="px-5 py-2 rounded-xl text-sm font-medium bg-emerald-600/20 text-emerald-400 hover:bg-emerald-600/30 border border-emerald-500/20 transition-all flex items-center gap-1.5"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          Regenerate Learning Plan
        </button>
      </div>
    </motion.div>
  );
}
