import { useState, useEffect } from "react";
import { getToken, setToken, clearAuth, getUser, setUser } from "@/lib/auth";
import { authHeaders, API } from "@/lib/api";

// Common
import LoadingSpinner from "@/components/common/LoadingSpinner";
import NavBar from "@/components/common/NavBar";

// Auth
import LoginScreen from "@/components/auth/LoginScreen";
import RegisterScreen from "@/components/auth/RegisterScreen";
import ChangePasswordScreen from "@/components/auth/ChangePasswordScreen";

// Assessment
import QuickAssessmentScreen from "@/components/assessment/QuickAssessmentScreen";

// Mock
import MockInterviewScreen from "@/components/mock/MockInterviewScreen";

// Pricing
import RateCardsScreen from "@/components/pricing/RateCardsScreen";

// Dashboard
import DashboardScreen from "@/components/dashboard/DashboardScreen";

// Stubs for screens being migrated
import StubScreen from "@/components/stubs/StubScreen";

export default function App() {
  const [authState, setAuthState] = useState("checking"); // checking, login, register, change_password, quick_assessment, authenticated
  const [screen, setScreen] = useState("dashboard");
  const [screenParams, setScreenParams] = useState<any>({});
  const [user, setUserState] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  // Interview state
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [questions, setQuestions] = useState<any[]>([]);
  const [engine, setEngine] = useState("whisper");
  const [scorecard, setScorecard] = useState<any>(null);
  const [questionReview, setQuestionReview] = useState<any[]>([]);
  const [audioUrls, setAudioUrls] = useState<Record<string, string>>({});

  useEffect(() => {
    const token = getToken();
    const savedUser = getUser();
    if (token && savedUser) {
      setUserState(savedUser);
      if (savedUser.is_first_login) setAuthState("change_password");
      else setAuthState("authenticated");
    } else {
      setAuthState("login");
    }
  }, []);

  const handleLogin = (data: any) => {
    setToken(data.token);
    setUser(data);
    setUserState(data);
    if (data.is_first_login) {
      setAuthState("change_password");
    } else {
      setAuthState("authenticated");
      setScreen("dashboard");
    }
  };

  const handleRegister = (_data: any) => {
    // After registration, go to login
    setAuthState("login");
  };

  const handlePasswordChanged = () => {
    const u = getUser();
    if (u) {
      u.is_first_login = false;
      setUser(u);
      setUserState(u);
    }
    // v2: Route to Quick Assessment if user has target company set
    if (u && u.target_company) {
      setAuthState("quick_assessment");
    } else {
      setAuthState("authenticated");
      setScreen("dashboard");
    }
  };

  const handleQuickAssessmentComplete = (_results: any) => {
    setAuthState("authenticated");
    setScreen("dashboard");
  };

  const handleLogout = () => {
    clearAuth();
    setAuthState("login");
    setUserState(null);
    setScreen("dashboard");
    setSessionId(null);
    setQuestions([]);
    setScorecard(null);
    setQuestionReview([]);
  };

  const navigate = (target: string, params: any = {}) => {
    setScreenParams(params);
    setScreen(target);
    setError(null);
  };

  // Interview handlers
  const handleStartInterview = async (name: string, jobTitle: string, selectedEngine: string) => {
    setError(null);
    setEngine(selectedEngine);
    try {
      const res = await fetch(`${API}/session/start`, {
        method: "POST",
        headers: authHeaders(),
        body: JSON.stringify({ candidate_name: name, job_title: jobTitle }),
      });
      const data = await res.json();
      setSessionId(data.session_id);
      const qRes = await fetch(`${API}/questions?session_id=${data.session_id}`, { headers: authHeaders() });
      const qData = await qRes.json();
      setQuestions(qData);
      setScreen("interview_room");
    } catch {
      setError("Cannot connect to backend.");
    }
  };

  const handleStartJDInterview = async (name: string, jobDescription: string, selectedEngine: string) => {
    setError(null);
    setEngine(selectedEngine);
    try {
      const res = await fetch(`${API}/session/start-jd`, {
        method: "POST",
        headers: authHeaders(),
        body: JSON.stringify({ candidate_name: name, job_description: jobDescription }),
      });
      const data = await res.json();
      if (!res.ok) {
        setError(data.error || "Failed to generate questions");
        return;
      }
      setSessionId(data.session_id);
      const qRes = await fetch(`${API}/questions?session_id=${data.session_id}`, { headers: authHeaders() });
      const qData = await qRes.json();
      setQuestions(qData);
      setScreen("interview_room");
    } catch {
      setError("Cannot connect to backend. Make sure an LLM API key is configured.");
    }
  };

  const handleFinishInterview = async (timeTaken: string, recordedAudioUrls: Record<string, string>) => {
    setAudioUrls(recordedAudioUrls || {});
    try {
      const res = await fetch(`${API}/session/finish`, {
        method: "POST",
        headers: authHeaders(),
        body: JSON.stringify({ session_id: sessionId, time_taken: timeTaken }),
      });
      const data = await res.json();
      setScorecard(data.scorecard);
      setQuestionReview(data.question_review);
      setScreen("results");
    } catch {
      setError("Failed to get results.");
    }
  };

  if (authState === "checking") return <LoadingSpinner />;
  if (authState === "login")
    return <LoginScreen onLogin={handleLogin} onSwitchToRegister={() => setAuthState("register")} />;
  if (authState === "register")
    return <RegisterScreen onRegister={handleRegister} onSwitchToLogin={() => setAuthState("login")} />;
  if (authState === "change_password") return <ChangePasswordScreen onComplete={handlePasswordChanged} />;
  if (authState === "quick_assessment")
    return (
      <QuickAssessmentScreen
        onComplete={handleQuickAssessmentComplete}
        onSkip={() => {
          setAuthState("authenticated");
          setScreen("dashboard");
        }}
      />
    );

  // Authenticated app
  const showNav = !["interview_room", "results", "ai_interview_room", "mock_interview"].includes(screen);

  return (
    <div className="relative min-h-screen">
      {showNav && <NavBar screen={screen} onNavigate={navigate} onLogout={handleLogout} userName={user?.full_name || ""} />}
      {error && (
        <div className="fixed top-14 left-1/2 -translate-x-1/2 z-50 bg-red-500/20 border border-red-500/30 text-red-300 px-6 py-3 rounded-xl text-sm animate-fade-in">
          {error}
          <button onClick={() => setError(null)} className="ml-4 text-red-400 hover:text-red-300">
            &times;
          </button>
        </div>
      )}

      {screen === "dashboard" && <DashboardScreen onNavigate={navigate} />}
      {screen === "profile" && <StubScreen name="Profile" onNavigate={navigate} />}
      {screen === "history" && <StubScreen name="Session History" onNavigate={navigate} />}
      {screen === "learning" && <StubScreen name="Learning Screen" onNavigate={navigate} />}
      {screen === "assessment" && <StubScreen name="Topic Assessment" onNavigate={navigate} />}
      {screen === "review" && <StubScreen name="Review & Revisit" onNavigate={navigate} />}
      {screen === "interview" && <StubScreen name="AI Interview Booth (HomeScreen)" onNavigate={navigate} />}
      {screen === "interview_room" && <StubScreen name="Interview Room" onNavigate={navigate} />}
      {screen === "results" && <StubScreen name="Results Page" onNavigate={navigate} />}
      {screen === "ai_interview" && <StubScreen name="AI Interview Hub" onNavigate={navigate} />}
      {screen === "ai_interview_room" && <StubScreen name="AI Interview Room" onNavigate={navigate} />}
      {screen === "ai_results" && <StubScreen name="AI Results Screen" onNavigate={navigate} />}
      {screen === "mock_interview" && <MockInterviewScreen onComplete={(r: any) => navigate("dashboard")} onNavigate={navigate} />}
      {screen === "pricing" && <RateCardsScreen onNavigate={navigate} />}
    </div>
  );
}
