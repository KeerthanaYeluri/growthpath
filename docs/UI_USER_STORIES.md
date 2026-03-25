# GrowthPath v2.0 — UI User Stories Tracker
# Frontend-v2 (React 18 + Vite + Tailwind)

**Last Updated:** 2026-03-25
**Frontend:** `interview/frontend-v2/src/components/`

---

## Sprint 1: Foundation — Registration, Company Profiles, ELO System

### US-UI-1.1: Registration Screen with Company/Role/Level Selection
- **File:** `auth/RegisterScreen.tsx`
- **Status:** Done
- **Acceptance Criteria:**
  - [x] Company selector (Google / Apple)
  - [x] Role picker (SDE, SDET, DevOps, etc.)
  - [x] Level picker (L3, L4, L5, L6)
  - [x] Tech stack multi-select
  - [x] Interest areas multi-select
  - [x] Hours per day input
  - [x] Full name and email fields
  - [x] Form validation and error display

### US-UI-1.1b: Registration Auto-Login and Clean Auth Handoff
- **File:** `App.tsx`, `auth/RegisterScreen.tsx`
- **Status:** Done
- **Acceptance Criteria:**
  - [x] On registration success, clear previous user's auth data (token + cached user)
  - [x] Auto-login with new user's token (no manual re-login needed)
  - [x] New user's target_company/role/level correctly passed to subsequent screens
  - [x] Quick Assessment after password change generates role-specific questions (not previous user's)
  - [x] Works for all roles: QA/SDET, DevOps, Backend, Frontend, etc.

### US-UI-1.2: ELO Display Component
- **File:** `dashboard/DashboardScreen.tsx`
- **Status:** Done
- **Acceptance Criteria:**
  - [x] Current ELO score display
  - [x] Target hiring bar display
  - [x] ELO gap calculation
  - [x] Progress ring / visual indicator
  - [x] Sub-ELO breakdown per round type

### US-UI-1.3: Gap Map Component
- **File:** `dashboard/DashboardScreen.tsx`
- **Status:** Done
- **Acceptance Criteria:**
  - [x] Visual display of role demands vs current skills
  - [x] Strength vs gap identification
  - [x] Priority levels for gaps

### US-UI-1.4: Dashboard Redesign — Action-First Hero
- **File:** `dashboard/DashboardScreen.tsx`
- **Status:** Done
- **Acceptance Criteria:**
  - [x] Welcome hero section with target company, role, and level
  - [x] ELO rating prominent display
  - [x] Gap map integration
  - [x] Learning path timeline
  - [x] Mock interview history chart
  - [x] Quick actions (Resume Learning, Start Mock)

### US-UI-1.5: Navigation Update
- **File:** `common/NavBar.tsx`
- **Status:** Done
- **Acceptance Criteria:**
  - [x] Sticky navigation bar
  - [x] Nav items: Dashboard, Learn, Interview, History, Review, Profile
  - [x] Active screen highlighting
  - [x] User name display
  - [x] Logout button
  - [x] Responsive (icons on mobile, labels on desktop)

---

## Sprint 2: Quick Assessment — Interview First Experience

### US-UI-2.1: Quick Assessment Screen
- **File:** `assessment/QuickAssessmentScreen.tsx`
- **Status:** Done
- **Acceptance Criteria:**
  - [x] Question display
  - [x] Hybrid answer mode (text + voice)
  - [x] Timer per question
  - [x] Progress indicator
  - [x] Submit and navigation controls

### US-UI-2.2: Post-Assessment Results Screen
- **File:** `assessment/QuickAssessmentScreen.tsx` (results view)
- **Status:** Done
- **Acceptance Criteria:**
  - [x] ELO assigned display
  - [x] Round scores breakdown
  - [x] Weakness identification
  - [x] Redirect to Dashboard

### US-UI-2.3: Auto-Redirect Flow
- **File:** `App.tsx`
- **Status:** Done
- **Acceptance Criteria:**
  - [x] Register -> Quick Assessment -> Results -> Dashboard auto-flow
  - [x] Detect users with target company who haven't taken assessment

### US-UI-2.4: Dashboard Update — Quick Assessment Results
- **File:** `dashboard/DashboardScreen.tsx`
- **Status:** Done
- **Acceptance Criteria:**
  - [x] Show Quick Assessment results on dashboard
  - [x] Learning path from assessment weaknesses
  - [x] "Start Full Mock" CTA button

### US-UI-2.5: Learning Path Recalibration on Quick Assessment
- **File:** `backend/app.py` (submit_quick_assessment endpoint)
- **Status:** Done
- **Acceptance Criteria:**
  - [x] On every Quick Assessment submission, regenerate learning plan from current profile
  - [x] Reorder learning path based on weak patterns identified in assessment
  - [x] Weak topics move to the top of the learning path
  - [x] Works on retakes (not just the first assessment)
  - [x] ELO recalibrates on every attempt
  - [x] Dashboard reflects updated learning path after assessment

### US-UI-2.6: Quick Assessment Section on Dashboard
- **File:** `dashboard/DashboardScreen.tsx`
- **Status:** Done
- **Acceptance Criteria:**
  - [x] Shows "Quick Assessment Required" banner for users who haven't taken it
  - [x] Shows "Quick Assessment Completed" with score, attempt count for users who have taken it
  - [x] "Retake Assessment" button always visible after first attempt
  - [x] "Start Assessment" button for new users
  - [x] Visible for all users with a target company set

### US-UI-2.8: Role-Specific Question Generation
- **File:** `backend/quick_assessment.py`, `backend/mock_engine.py`
- **Status:** Done
- **Acceptance Criteria:**
  - [x] Each role has 10+ domain-specific questions (easy → medium → hard)
  - [x] Roles covered: Backend, Frontend, Fullstack, DevOps/SRE, Data Engineer, ML Engineer, Mobile, Platform, QA/SDET
  - [x] Quick Assessment generates questions matching user's selected role
  - [x] Mock Interview domain round generates role-specific questions
  - [x] Questions progress from basics to advanced within each role
  - [x] LLM fallback generates additional questions when pool is insufficient
  - [x] New user registration → password change → assessment uses correct role (no stale data)

### US-UI-2.10: Role-Focused Quick Assessment Question Distribution
- **File:** `backend/quick_assessment.py` (generate_quick_assessment function)
- **Status:** Done
- **Bug:** Quick Assessment was 3 coding + 1 design + 2 behavioral + 1 domain = mostly generic questions regardless of role
- **Fix:** Rebalanced to 5-6 domain-specific + 2 coding + 1 design + 1 behavioral = majority role-specific
- **Acceptance Criteria:**
  - [x] 5-6 out of 10 questions are domain-specific (role-focused)
  - [x] Domain questions span easy → medium → hard difficulty
  - [x] DevOps user gets Docker, Kubernetes, CI/CD, monitoring questions
  - [x] Backend user gets REST API, SQL, caching, microservices questions
  - [x] QA/SDET user gets testing, Playwright, Selenium, API testing questions
  - [x] Frontend user gets DOM, React, state management, SSR questions
  - [x] All other roles get their respective domain questions
  - [x] Questions shuffled so domain isn't always first

### US-UI-2.11: FAANG Intro Walkthrough (P1)
- **Status:** Not Started
- **Acceptance Criteria:**
  - [ ] 2-min animated overview for newcomers
  - [ ] Skip option

---

## Sprint 3: Mock Interview Engine — 5-Round Structure

### US-UI-3.1: Mock Interview Screen — 5-Round Layout
- **File:** `mock/MockInterviewScreen.tsx`
- **Status:** Done
- **Acceptance Criteria:**
  - [x] 5-round layout (Phone Screen, System Design, Behavioral, Domain, Bar Raiser)
  - [x] Round indicator showing current round
  - [x] Active round display

### US-UI-3.2: Round Timer Component
- **File:** `mock/MockInterviewScreen.tsx`
- **Status:** Done
- **Acceptance Criteria:**
  - [x] Countdown timer per round
  - [x] Visual warning at 20% time remaining
  - [x] Auto-advance on time expiry

### US-UI-3.3: Round Transition UI
- **File:** `mock/MockInterviewScreen.tsx`
- **Status:** Done
- **Acceptance Criteria:**
  - [x] "Round N Complete -> Moving to next round..." transition
  - [x] Smooth animated transition

### US-UI-3.4: Hybrid Answer Mode Per Round
- **File:** `mock/MockInterviewScreen.tsx`
- **Status:** Done
- **Acceptance Criteria:**
  - [x] Text input for coding rounds
  - [x] Voice input for behavioral rounds
  - [x] Hybrid (text + voice) for domain rounds
  - [x] Auto-switch based on round type

### US-UI-3.5: Code Editor Component (P0)
- **File:** `mock/MockInterviewScreen.tsx`
- **Status:** Partial — uses textarea, not Monaco/CodeMirror
- **Acceptance Criteria:**
  - [x] Code input area for Phone Screen round
  - [ ] Syntax highlighting (Monaco or CodeMirror)
  - [ ] Language selection

### US-UI-3.6: Mid-Answer Voice-to-Text Switching
- **File:** `mock/MockInterviewScreen.tsx`
- **Status:** Done
- **Acceptance Criteria:**
  - [x] Switch between voice and text mid-answer

---

## Sprint 4: AI Interviewer Persona + Dynamic Probe Trees

### US-UI-4.1: Conversation UI — Real-Time Transcript
- **File:** `mock/MockInterviewScreen.tsx`
- **Status:** Done
- **Acceptance Criteria:**
  - [x] Real-time transcript display
  - [x] AI speaking indicator
  - [x] User speaking indicator
  - [x] Conversation history display

### US-UI-4.2: WebSocket Client for Voice Streaming
- **Status:** Partial — HTTP-based conversation API used instead of WebSocket
- **Acceptance Criteria:**
  - [ ] WebSocket voice streaming client
  - [x] Voice input via HTTP API fallback

### US-UI-4.3: Hint Button
- **File:** `mock/MockInterviewScreen.tsx`
- **Status:** Done
- **Acceptance Criteria:**
  - [x] "Get Hint" button
  - [x] Penalty warning before hint
  - [x] Hint delivery in conversation

### US-UI-4.4: Probe Depth Indicator (P1)
- **File:** `mock/MockInterviewScreen.tsx`
- **Status:** Done
- **Acceptance Criteria:**
  - [x] Visual indicator showing current depth level (1-5)
  - [x] Depth tracking display

### US-UI-4.5: Mic Quality Indicator
- **File:** `interview/HomeScreen.tsx`
- **Status:** Done
- **Acceptance Criteria:**
  - [x] Pre-interview microphone permission check
  - [x] Mic status indicator

### US-UI-4.6: Custom Technical Vocabulary Display (P1)
- **Status:** Not Started
- **Acceptance Criteria:**
  - [ ] Show recognized tech terms during transcription

---

## Sprint 5: Scoring, ELO Update, Rubric Reveal

### US-UI-5.1: Scorecard Screen — Round-by-Round
- **File:** `mock/MockResultsView.tsx`
- **Status:** Done
- **Acceptance Criteria:**
  - [x] Round-by-round scores
  - [x] Thinking vs Accuracy breakdown
  - [x] ELO change display

### US-UI-5.2: Rubric Reveal Component
- **File:** `mock/MockResultsView.tsx`
- **Status:** Done
- **Acceptance Criteria:**
  - [x] Expandable per-question rubric checklist
  - [x] Covered / missed items display
  - [x] Link missed items to learning content

### US-UI-5.3: ELO Change Animation
- **File:** `mock/MockResultsView.tsx`, `dashboard/DashboardScreen.tsx`
- **Status:** Done
- **Acceptance Criteria:**
  - [x] "ELO 1350 -> 1420 (+70)" animated counter
  - [x] Visual ELO delta display

### US-UI-5.4: Pattern Mastery Grid
- **File:** `dashboard/DashboardScreen.tsx`
- **Status:** Partial
- **Acceptance Criteria:**
  - [x] Pattern mastery display on dashboard
  - [ ] Full heat map visualization of archetype patterns

### US-UI-5.5: Dashboard Update — ELO Trend Graph
- **File:** `dashboard/DashboardScreen.tsx`
- **Status:** Done
- **Acceptance Criteria:**
  - [x] ELO trend graph (mock history chart)
  - [x] Pattern mastery tracker

### US-UI-5.6: Rubric-to-Learning Links
- **File:** `mock/MockResultsView.tsx`
- **Status:** Done
- **Acceptance Criteria:**
  - [x] "Learn about X ->" links from missed rubric items

---

## Sprint 6: Hiring Committee + Path Reordering

### US-UI-6.1: Hiring Committee Screen
- **File:** `mock/MockResultsView.tsx`
- **Status:** Done
- **Acceptance Criteria:**
  - [x] 3 interviewer cards with name/title
  - [x] HIRE / NO HIRE badge per interviewer
  - [x] Quoted reasoning from each interviewer
  - [x] Final committee verdict

### US-UI-6.2: Committee Verdict Animation
- **File:** `mock/MockResultsView.tsx`
- **Status:** Done
- **Acceptance Criteria:**
  - [x] Final decision display with visual emphasis
  - [x] Animated verdict reveal

### US-UI-6.3: Path Reorder Notification
- **File:** `mock/MockResultsView.tsx`
- **Status:** Done
- **Acceptance Criteria:**
  - [x] "Learning path updated based on mock results" notification
  - [x] Before/after comparison of path order

### US-UI-6.4: Drag-and-Drop Path Reordering
- **File:** `learning/LearningScreen.tsx`
- **Status:** Partial
- **Acceptance Criteria:**
  - [x] Manual reorder API integration
  - [ ] Full drag-and-drop UI interaction

### US-UI-6.5: Learning Screen — Focus Area Badges
- **File:** `learning/LearningScreen.tsx`
- **Status:** Done
- **Acceptance Criteria:**
  - [x] "Focus Area" badges on weak topics
  - [x] Reordered path display

### US-UI-6.6: "Retake Mock" CTA
- **File:** `mock/MockResultsView.tsx`
- **Status:** Done
- **Acceptance Criteria:**
  - [x] "Retake Mock" button after NO HIRE verdict

---

## Sprint 7: Learning Content + AI Generation + Review

### US-UI-7.1: Learning Screen — AI-Generated Content
- **File:** `learning/LearningScreen.tsx`
- **Status:** Done
- **Acceptance Criteria:**
  - [x] Display AI-generated content
  - [x] 4 learning dimensions (Interview, Implementation, Examples, Best Practices)
  - [x] Markdown rendering
  - [x] Bookmark functionality
  - [x] Mark as complete per dimension
  - [x] Mark for review

### US-UI-7.2: Mock Replay Screen
- **File:** `mock/MockResultsView.tsx`
- **Status:** Done
- **Acceptance Criteria:**
  - [x] Step-through replay with transcript
  - [x] Scores and rubric at each step

### US-UI-7.3: Score Comparison View
- **File:** `dashboard/DashboardScreen.tsx`
- **Status:** Done
- **Acceptance Criteria:**
  - [x] Mock interview history chart (last 5 attempts)
  - [x] ELO delta per attempt

### US-UI-7.4: Interview Ready Celebration (P1)
- **File:** `dashboard/DashboardScreen.tsx`
- **Status:** Done
- **Acceptance Criteria:**
  - [x] Celebration banner when ELO >= hiring bar
  - [ ] Confetti animation
  - [ ] Download prep summary PDF

### US-UI-7.5: "Days Until Ready" Widget (P1)
- **Status:** Not Started
- **Acceptance Criteria:**
  - [ ] Dashboard widget showing estimated days based on ELO trajectory

### US-UI-7.6: Session History — ELO Change Per Session
- **File:** `history/SessionHistoryScreen.tsx`
- **Status:** Done
- **Acceptance Criteria:**
  - [x] All completed sessions listed
  - [x] Score, date, role, time taken per session

---

## Sprint 8: Polish, Testing, Rate Cards, Launch Prep

### US-UI-8.1: Rate Cards Page
- **File:** `pricing/RateCardsScreen.tsx`
- **Status:** Done
- **Acceptance Criteria:**
  - [x] Free / Pro / Team / Enterprise tiers
  - [x] Feature comparison
  - [x] "Most Popular" badge
  - [x] Display only (no payment integration)

### US-UI-8.2: Loading States & UX Polish
- **Files:** All screens
- **Status:** Done
- **Acceptance Criteria:**
  - [x] LoadingSpinner component
  - [x] ErrorBanner component
  - [x] Loading states on API calls

### US-UI-8.3: Dark Theme Consistency
- **Status:** Done
- **Acceptance Criteria:**
  - [x] bg-slate-950 base
  - [x] Glassmorphism card system (GlassCard components)
  - [x] Consistent dark theme across all screens

### US-UI-8.4: Mobile Responsive Polish (P1)
- **Status:** Partial
- **Acceptance Criteria:**
  - [x] NavBar responsive (icons on mobile)
  - [x] Grid layouts responsive
  - [ ] Full mobile testing pass

### US-UI-8.5: Accessibility Pass (P1)
- **Status:** Not Started
- **Acceptance Criteria:**
  - [ ] Screen reader compatibility
  - [ ] Keyboard navigation
  - [ ] Voice UI accessibility

### US-UI-8.6: Cross-Browser Testing
- **Status:** Not Started
- **Acceptance Criteria:**
  - [ ] Chrome tested
  - [ ] Edge tested (voice API compatibility)

---

## Phase 2: AI Voice Interview (Resume-Based)

### US-UI-P2.1: AI Interview Hub — Resume Upload
- **File:** `ai-interview/AIInterviewHub.tsx`
- **Status:** Done
- **Acceptance Criteria:**
  - [x] Resume upload (PDF/DOCX/TXT)
  - [x] Resume display with parsed skills, experience, years
  - [x] Create interview from resume
  - [x] Interview management (Pending/In Progress/Completed/Evaluated)

### US-UI-P2.2: AI Interview Room — Conversational Interview
- **File:** `ai-interview/AIInterviewRoom.tsx`
- **Status:** Done
- **Acceptance Criteria:**
  - [x] Conversational AI interviewer ("Alex")
  - [x] Question categories (technical, behavioral, situational, project)
  - [x] Real-time speech recognition with mic button
  - [x] Type or speak answers
  - [x] AI responses with follow-up questions
  - [x] Progress indicator (question X / total)

### US-UI-P2.3: AI Interview Results
- **File:** `ai-interview/AIResultsScreen.tsx`
- **Status:** Done
- **Acceptance Criteria:**
  - [x] Overall score and hiring recommendation (Strong Hire/Hire/Maybe/Not Recommended)
  - [x] Category scores (relevance, depth, communication, examples)
  - [x] Summary feedback
  - [x] Strengths and improvement areas
  - [x] Full transcript with per-question evaluations

---

## Common UI Components

| Component | File | Status |
|-----------|------|--------|
| GlassCard system | `ui/glass-card.tsx` | Done |
| LoadingSpinner | `common/LoadingSpinner.tsx` | Done |
| ErrorBanner | `common/ErrorBanner.tsx` | Done |
| NavBar | `common/NavBar.tsx` | Done |
| MicButton | `common/MicButton.tsx` | Done |
| WaveIndicator | `common/WaveIndicator.tsx` | Done |
| TopicBadge | `common/TopicBadge.tsx` | Done |
| Stars (rating) | `common/Stars.tsx` | Done |
| EnginePicker | `common/EnginePicker.tsx` | Done |

---

## Summary

| Sprint | Total UI Stories | Done | Partial | Not Started |
|--------|-----------------|------|---------|-------------|
| S1 | 6 | 6 | 0 | 0 |
| S2 | 8 | 7 | 0 | 1 (P1) |
| S3 | 6 | 5 | 1 | 0 |
| S4 | 6 | 4 | 1 | 1 (P1) |
| S5 | 6 | 5 | 1 | 0 |
| S6 | 6 | 5 | 1 | 0 |
| S7 | 6 | 4 | 0 | 2 (P1) |
| S8 | 6 | 3 | 1 | 2 (P1) |
| Phase 2 | 3 | 3 | 0 | 0 |
| **Total** | **53** | **42** | **5** | **6** |

**Overall UI Completion: ~88% (all P0 stories done)**

### Remaining Items (mostly P1):
- US-UI-2.7: FAANG intro walkthrough animation
- US-UI-3.5: Monaco/CodeMirror code editor (using textarea currently)
- US-UI-4.2: WebSocket voice streaming (using HTTP fallback)
- US-UI-4.6: Custom technical vocabulary display
- US-UI-5.4: Full pattern mastery heat map
- US-UI-6.4: Drag-and-drop path reordering
- US-UI-7.4: Confetti animation + PDF download
- US-UI-7.5: "Days Until Ready" estimator widget
- US-UI-8.4: Full mobile testing pass
- US-UI-8.5: Accessibility pass
- US-UI-8.6: Cross-browser testing