import { motion } from "framer-motion";
import {
  LayoutDashboard,
  BookOpen,
  Mic,
  Clock,
  ClipboardCheck,
  UserCircle,
  LogOut,
} from "lucide-react";

interface NavBarProps {
  screen: string;
  onNavigate: (screen: string) => void;
  onLogout: () => void;
  userName: string;
}

const items = [
  { id: "dashboard", label: "Dashboard", icon: LayoutDashboard },
  { id: "learning", label: "Learn", icon: BookOpen },
  { id: "interview", label: "Interview", icon: Mic },
  { id: "history", label: "History", icon: Clock },
  { id: "review", label: "Review", icon: ClipboardCheck },
  { id: "profile", label: "Profile", icon: UserCircle },
];

export default function NavBar({ screen, onNavigate, onLogout, userName }: NavBarProps) {
  return (
    <nav className="glass-strong border-b border-slate-800/50 px-4 py-2 flex items-center justify-between sticky top-0 z-40">
      <div className="flex items-center gap-1">
        <span className="bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent font-bold text-sm mr-3">
          GrowthPath
        </span>
        {items.map((item) => {
          const Icon = item.icon;
          const isActive = screen === item.id;
          return (
            <motion.button
              key={item.id}
              onClick={() => onNavigate(item.id)}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className={`relative flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                isActive
                  ? "text-indigo-300"
                  : "text-slate-500 hover:text-slate-300 hover:bg-slate-800/50"
              }`}
            >
              <Icon className="w-3.5 h-3.5" />
              <span className="hidden md:inline">{item.label}</span>
              {isActive && (
                <motion.div
                  layoutId="nav-active-indicator"
                  className="absolute inset-0 bg-indigo-600/20 rounded-lg -z-10"
                  transition={{ type: "spring", stiffness: 380, damping: 30 }}
                />
              )}
            </motion.button>
          );
        })}
      </div>
      <div className="flex items-center gap-3">
        <span className="text-slate-500 text-xs">{userName}</span>
        <motion.button
          onClick={onLogout}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className="flex items-center gap-1 text-slate-500 hover:text-red-400 text-xs transition-colors"
        >
          <LogOut className="w-3.5 h-3.5" />
          <span className="hidden md:inline">Logout</span>
        </motion.button>
      </div>
    </nav>
  );
}
