interface ErrorBannerProps {
  error: string;
  onDismiss?: () => void;
}

export default function ErrorBanner({ error, onDismiss }: ErrorBannerProps) {
  if (!error) return null;

  return (
    <div className="bg-red-500/10 border border-red-500/20 text-red-400 px-4 py-2 rounded-xl text-sm mb-4 flex items-center justify-between">
      <span>{error}</span>
      {onDismiss && (
        <button onClick={onDismiss} className="ml-4 text-red-400 hover:text-red-300">
          &times;
        </button>
      )}
    </div>
  );
}
