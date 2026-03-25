export default function LoadingSpinner() {
  return (
    <div className="flex items-center justify-center py-12">
      <div className="flex gap-1.5">
        <div className="w-2 h-2 rounded-full bg-indigo-400 thinking-dot"></div>
        <div className="w-2 h-2 rounded-full bg-indigo-400 thinking-dot"></div>
        <div className="w-2 h-2 rounded-full bg-indigo-400 thinking-dot"></div>
      </div>
    </div>
  );
}
