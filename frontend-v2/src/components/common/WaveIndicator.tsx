interface WaveIndicatorProps {
  listening: boolean;
}

export default function WaveIndicator({ listening }: WaveIndicatorProps) {
  if (!listening) return null;
  return (
    <div className="flex items-end gap-1 h-8">
      {[0, 1, 2, 3, 4, 5, 6].map((i) => (
        <div
          key={i}
          className="w-1 bg-indigo-400 rounded-full mic-wave"
          style={{ animationDelay: `${i * 0.12}s`, height: "12px" }}
        ></div>
      ))}
    </div>
  );
}
