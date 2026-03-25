interface TopicBadgeProps {
  topic: string;
  difficulty?: string;
}

const colors: Record<string, string> = {
  Introduction: "bg-blue-500/20 text-blue-300",
  Python: "bg-yellow-500/20 text-yellow-300",
  Pytest: "bg-green-500/20 text-green-300",
  Playwright: "bg-purple-500/20 text-purple-300",
  Java: "bg-orange-500/20 text-orange-300",
  Selenium: "bg-emerald-500/20 text-emerald-300",
  "API Testing": "bg-cyan-500/20 text-cyan-300",
  "UI Testing": "bg-pink-500/20 text-pink-300",
  Locust: "bg-lime-500/20 text-lime-300",
  "Manual Testing": "bg-amber-500/20 text-amber-300",
  Behavioral: "bg-violet-500/20 text-violet-300",
  HR: "bg-rose-500/20 text-rose-300",
};

const diffColors: Record<string, string> = {
  Easy: "text-green-400",
  Medium: "text-yellow-400",
  Hard: "text-red-400",
};

export default function TopicBadge({ topic, difficulty }: TopicBadgeProps) {
  return (
    <div className="flex items-center gap-2">
      <span className={`px-3 py-1 rounded-full text-xs font-semibold ${colors[topic] || "bg-slate-500/20 text-slate-300"}`}>
        {topic}
      </span>
      {difficulty && <span className={`text-xs font-medium ${diffColors[difficulty] || ""}`}>{difficulty}</span>}
    </div>
  );
}
