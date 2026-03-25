import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Check, X, Crown, Zap, Users, Building2, ArrowRight } from "lucide-react";
import { GlassCard, GlassCardHeader, GlassCardTitle, GlassCardContent, GlassCardFooter } from "@/components/ui/glass-card";
import { cn } from "@/lib/utils";
import { API } from "@/lib/api";
import LoadingSpinner from "@/components/common/LoadingSpinner";

interface RateCardsScreenProps {
  onNavigate: (screen: string) => void;
}

const tierIcons: Record<string, React.ReactNode> = {
  Free: <Zap className="w-5 h-5 text-slate-400" />,
  Pro: <Crown className="w-5 h-5 text-amber-400" />,
  Team: <Users className="w-5 h-5 text-cyan-400" />,
  Enterprise: <Building2 className="w-5 h-5 text-purple-400" />,
};

const stagger = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.12, delayChildren: 0.2 },
  },
};

const cardUp = {
  hidden: { opacity: 0, y: 40 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.5, ease: "easeOut" } },
};

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
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
      className="max-w-5xl mx-auto p-4 md:p-6"
    >
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="text-center mb-8"
      >
        <h1 className="text-3xl font-bold mb-2">Pricing Plans</h1>
        <p className="text-slate-400 text-sm">Choose the plan that fits your interview preparation needs</p>
        <p className="text-amber-400 text-xs mt-2">Currently in POC -- all features are free!</p>
      </motion.div>

      <motion.div
        variants={stagger}
        initial="hidden"
        animate="visible"
        className="grid md:grid-cols-4 gap-4"
      >
        {tiers.map((tier: any, i: number) => (
          <motion.div
            key={i}
            variants={cardUp}
            whileHover={{ y: -4, transition: { duration: 0.2 } }}
          >
            <GlassCard
              className={cn(
                "p-0 h-full flex flex-col relative",
                tier.highlighted && "border-2 border-indigo-500/50 glow"
              )}
            >
              {/* Highlighted gradient border shimmer */}
              {tier.highlighted && (
                <motion.div
                  className="absolute -top-3 left-1/2 -translate-x-1/2 z-10"
                  animate={{ scale: [1, 1.05, 1] }}
                  transition={{ duration: 2, repeat: Infinity }}
                >
                  <span className="px-3 py-0.5 rounded-full bg-gradient-to-r from-indigo-600 to-purple-600 text-white text-[10px] font-semibold shadow-lg shadow-indigo-500/30">
                    MOST POPULAR
                  </span>
                </motion.div>
              )}

              <GlassCardHeader className="pt-5">
                <GlassCardTitle className="flex items-center gap-2 text-lg">
                  {tierIcons[tier.name] || <Zap className="w-5 h-5 text-slate-400" />}
                  {tier.name}
                </GlassCardTitle>
              </GlassCardHeader>

              <GlassCardContent className="flex-1 flex flex-col">
                <div className="mb-1">
                  <span className="text-3xl font-black text-indigo-400">{tier.price}</span>
                  <span className="text-slate-500 text-sm">{tier.period}</span>
                </div>
                <p className="text-slate-400 text-xs mb-4">{tier.description}</p>

                <div className="flex-1 space-y-1.5 mb-4">
                  {tier.features.map((f: string, j: number) => (
                    <motion.div
                      key={j}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.4 + i * 0.12 + j * 0.04 }}
                      className="flex items-start gap-2"
                    >
                      <Check className="w-3.5 h-3.5 text-emerald-400 mt-0.5 flex-shrink-0" />
                      <span className="text-slate-300 text-xs">{f}</span>
                    </motion.div>
                  ))}
                  {(tier.limitations || []).map((l: string, j: number) => (
                    <motion.div
                      key={`l${j}`}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.4 + i * 0.12 + (tier.features.length + j) * 0.04 }}
                      className="flex items-start gap-2"
                    >
                      <X className="w-3.5 h-3.5 text-slate-600 mt-0.5 flex-shrink-0" />
                      <span className="text-slate-500 text-xs">{l}</span>
                    </motion.div>
                  ))}
                </div>
              </GlassCardContent>

              <GlassCardFooter>
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.97 }}
                  className={cn(
                    "w-full py-2.5 rounded-xl text-sm font-semibold transition-all flex items-center justify-center gap-1.5",
                    tier.highlighted
                      ? "bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white shadow-lg shadow-indigo-500/20"
                      : "bg-slate-800/60 hover:bg-slate-700/60 text-slate-300 border border-slate-700/50"
                  )}
                >
                  {tier.cta}
                  {tier.highlighted && <ArrowRight className="w-4 h-4" />}
                </motion.button>
              </GlassCardFooter>
            </GlassCard>
          </motion.div>
        ))}
      </motion.div>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.8 }}
        className="text-center mt-6"
      >
        <button onClick={() => onNavigate("dashboard")} className="text-slate-500 hover:text-slate-300 text-sm transition-colors">
          Back to Dashboard
        </button>
      </motion.div>
    </motion.div>
  );
}
