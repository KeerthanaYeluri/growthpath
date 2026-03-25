import { Mic, Square, Clock } from "lucide-react";

interface MicButtonProps {
  listening: boolean;
  processing: boolean;
  onStart: () => void;
  onStop: () => void;
}

export default function MicButton({ listening, processing, onStart, onStop }: MicButtonProps) {
  return (
    <button
      onClick={listening ? onStop : onStart}
      disabled={processing}
      className={`relative w-16 h-16 rounded-full flex items-center justify-center transition-all duration-300 ${
        processing
          ? "bg-amber-500 shadow-lg shadow-amber-500/30 animate-pulse"
          : listening
          ? "bg-red-500 hover:bg-red-400 shadow-lg shadow-red-500/30"
          : "bg-indigo-600 hover:bg-indigo-500 shadow-lg shadow-indigo-500/20"
      }`}
    >
      {listening && !processing && <div className="absolute inset-0 rounded-full bg-red-500/30 pulse-ring"></div>}
      <span className="relative z-10">
        {processing ? (
          <Clock className="w-7 h-7 text-white" />
        ) : listening ? (
          <Square className="w-7 h-7 text-white" />
        ) : (
          <Mic className="w-7 h-7 text-white" />
        )}
      </span>
    </button>
  );
}
