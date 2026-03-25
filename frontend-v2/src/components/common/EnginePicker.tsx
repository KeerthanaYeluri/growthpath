import { motion } from "framer-motion";
import { Globe, Target, Zap } from "lucide-react";

interface EnginePickerProps {
  engine: string;
  onChange: (engine: string) => void;
}

const engines = [
  { id: "browser", label: "Browser", desc: "Online, real-time", Icon: Globe },
  { id: "whisper", label: "Whisper", desc: "Local, best accuracy", Icon: Target },
  { id: "vosk", label: "Vosk", desc: "Local, exact words", Icon: Zap },
];

export default function EnginePicker({ engine, onChange }: EnginePickerProps) {
  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="flex gap-2">
      {engines.map((e) => (
        <button
          key={e.id}
          onClick={() => onChange(e.id)}
          className={`flex-1 px-3 py-2.5 rounded-xl text-xs font-medium transition-all ${
            engine === e.id
              ? "bg-indigo-600/30 border border-indigo-500/40 text-indigo-300"
              : "glass text-slate-400 hover:text-slate-300"
          }`}
        >
          <span className="block mb-0.5">
            <e.Icon className="w-4 h-4 mx-auto" />
          </span>
          <span className="block font-semibold">{e.label}</span>
          <span className="block text-[10px] opacity-60">{e.desc}</span>
        </button>
      ))}
    </motion.div>
  );
}
