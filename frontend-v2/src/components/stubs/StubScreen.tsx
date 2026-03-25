interface StubScreenProps {
  name: string;
  onNavigate?: (screen: string) => void;
}

export default function StubScreen({ name, onNavigate }: StubScreenProps) {
  return (
    <div className="max-w-2xl mx-auto p-6 text-center animate-fade-in">
      <div className="glass rounded-xl p-8">
        <div className="w-14 h-14 rounded-2xl bg-indigo-500/20 mx-auto mb-4 flex items-center justify-center">
          <svg className="w-7 h-7 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M11.42 15.17l-5.386 3.162A1.042 1.042 0 015 17.472V6.528c0-.798.885-1.27 1.534-.84l5.386 3.163M15.42 15.17l5.386 3.162A1.042 1.042 0 0021.84 17.472V6.528c0-.798-.885-1.27-1.534-.84L15.42 12.012"
            />
          </svg>
        </div>
        <h2 className="text-xl font-bold mb-2">{name}</h2>
        <p className="text-slate-400 text-sm mb-4">Coming soon -- being migrated to Vite + TypeScript</p>
        {onNavigate && (
          <button
            onClick={() => onNavigate("dashboard")}
            className="px-5 py-2 rounded-xl text-sm font-medium bg-indigo-600 hover:bg-indigo-500 text-white transition-all"
          >
            Back to Dashboard
          </button>
        )}
      </div>
    </div>
  );
}
