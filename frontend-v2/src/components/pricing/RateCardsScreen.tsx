import { useState, useEffect } from "react";
import { API } from "@/lib/api";
import LoadingSpinner from "@/components/common/LoadingSpinner";

interface RateCardsScreenProps {
  onNavigate: (screen: string) => void;
}

export default function RateCardsScreen({ onNavigate }: RateCardsScreenProps) {
  const [tiers, setTiers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API}/rate-cards`)
      .then((r) => r.json())
      .then((data) => {
        setTiers(data.tiers || []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  if (loading) return <LoadingSpinner />;

  return (
    <div className="max-w-5xl mx-auto p-4 md:p-6 animate-fade-in">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold mb-2">Pricing Plans</h1>
        <p className="text-slate-400 text-sm">Choose the plan that fits your interview preparation needs</p>
        <p className="text-amber-400 text-xs mt-2">Currently in POC -- all features are free!</p>
      </div>
      <div className="grid md:grid-cols-4 gap-4">
        {tiers.map((tier: any, i: number) => (
          <div
            key={i}
            className={`glass rounded-2xl p-5 flex flex-col ${tier.highlighted ? "border-2 border-indigo-500/50 glow relative" : ""}`}
          >
            {tier.highlighted && (
              <span className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-0.5 rounded-full bg-indigo-600 text-white text-[10px] font-semibold">
                MOST POPULAR
              </span>
            )}
            <h3 className="text-lg font-bold text-white">{tier.name}</h3>
            <div className="mt-2 mb-1">
              <span className="text-3xl font-black text-indigo-400">{tier.price}</span>
              <span className="text-slate-500 text-sm">{tier.period}</span>
            </div>
            <p className="text-slate-400 text-xs mb-4">{tier.description}</p>
            <div className="flex-1 space-y-1.5 mb-4">
              {tier.features.map((f: string, j: number) => (
                <div key={j} className="flex items-start gap-2">
                  <span className="text-emerald-400 text-xs mt-0.5">+</span>
                  <span className="text-slate-300 text-xs">{f}</span>
                </div>
              ))}
              {(tier.limitations || []).map((l: string, j: number) => (
                <div key={`l${j}`} className="flex items-start gap-2">
                  <span className="text-slate-600 text-xs mt-0.5">-</span>
                  <span className="text-slate-500 text-xs">{l}</span>
                </div>
              ))}
            </div>
            <button
              className={`w-full py-2.5 rounded-xl text-sm font-semibold transition-all ${tier.highlighted ? "bg-indigo-600 hover:bg-indigo-500 text-white" : "bg-slate-800/60 hover:bg-slate-700/60 text-slate-300 border border-slate-700/50"}`}
            >
              {tier.cta}
            </button>
          </div>
        ))}
      </div>
      <div className="text-center mt-6">
        <button onClick={() => onNavigate("dashboard")} className="text-slate-500 hover:text-slate-300 text-sm">
          Back to Dashboard
        </button>
      </div>
    </div>
  );
}
