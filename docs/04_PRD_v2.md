# Product Requirements Document (PRD)
# GrowthPath v2.0 — FAANG-Level Mock Interview & Adaptive Learning Platform

## 1. Overview
GrowthPath is a web-based FAANG-level mock interview simulator and adaptive learning platform. Users select a target company and role+level (e.g., Google L5 Backend Engineer), then immediately take a Quick Assessment to establish their starting ELO rating. The system identifies weakness patterns, dynamically generates a learning path from failures, and continuously reorders it based on mock interview performance. The core loop: **Interview → Identify Weaknesses → Learn → Interview Again → Repeat until Interview Ready.**

**Core Value Proposition:** Practice the way FAANG actually interviews — structured rounds, AI interviewer personas with real-time voice conversation, time pressure, ELO-based progress tracking, and weakness-driven learning path adaptation.

**POC Scope:** This is a Proof of Concept. Launch with Google + Apple only, Quick Assessment + Comfort Mode, free tier. No budget for paid LLM APIs — use Claude (free tier/local) or open-source alternatives.

## 2. Goals
| ID | Goal |
|----|------|
| G1 | FAANG-structured mock interviews with 5 real interview rounds (Phone Screen, System Design, Behavioral, Domain-Specific, Bar Raiser) |
| G2 | Company-specific interview profiles (POC: Google + Apple) |
| G3 | Target role + level selection (Junior L3-L4, Mid L4-L5, Senior L5-L6, Staff+ L6-L7) |
| G4 | AI Interviewer Persona — real-time voice conversation that pushes back, probes deeper, and gives hints with score penalty |
| G5 | Dual rating system: Thinking Process (60%) + Accuracy (40%) per answer |
| G6 | Dynamic follow-up probe trees — 5 levels deep, branching difficulty based on answer quality |
| G7 | Hybrid answer mode — auto-selects voice/text/code based on question type, with mid-answer switching |
| G8 | Weakness-driven learning path reordering — weak areas jump to top after each mock |
| G9 | Question archetype pattern tracking — mastery of recurring FAANG patterns, not just topics |
| G10 | Three assessment modes: Comfort, Interview, Pressure |
| G11 | ELO rating system with company-specific hiring bar thresholds |
| G12 | Interview First, Learn Second — throw users into mock immediately, generate learning path from failures |
| G13 | Hiring Committee Simulation — post-mock HIRE/NO HIRE verdict from 3 simulated interviewers |
| G14 | Rubric Reveal — show exactly what interviewer was evaluating after each question |
| G15 | Real-time voice conversation with AI interviewer + full transcript saved for review |
| G16 | Resume exactly where user stopped |
| G17 | Revisit and review any completed section at any time |

## 3. Non-Goals (v2.0)
| ID | Non-Goal |
|----|----------|
| NG1 | Not a certification platform |
| NG2 | No live instructor/mentorship |
| NG3 | No collaborative/group learning |
| NG4 | No third-party LMS integration |
| NG5 | No native mobile apps (web-responsive only) |
| NG6 | No video/visual content — text/code only for v2.0 |
| NG7 | No paid infrastructure — POC runs free/local |

## 4. Functional Requirements

### 4.1 Registration & Onboarding
| ID | Requirement | Priority |
|----|-------------|----------|
| FR-01 | User registers with: full name, email, current tech stack, interest areas, hours/day | P0 |
| FR-02 | **Target company selection:** Google, Apple (POC). Future: Meta, Amazon, Netflix, FAANG-like, Fortune 500, Startup | P0 |
| FR-03 | **Target role selection:** Backend, Frontend, Full Stack, DevOps/SRE, Data Engineer, ML Engineer, Mobile, Platform | P0 |
| FR-04 | **Target level selection:** Junior (L3-L4), Mid (L4-L5), Senior (L5-L6), Staff+ (L6-L7) | P0 |
| FR-05 | System generates credentials: email as username, default password welcome@123 | P0 |
| FR-06 | System generates **gap map**: target role demands vs current tech stack coverage | P0 |
| FR-07 | Force password change on first login | P0 |
| FR-08 | **Interview First flow:** After registration, immediately route to Quick Assessment — NO upfront learning | P0 |
| FR-09 | System generates personalized learning plan FROM Quick Assessment failures + gap analysis | P0 |
| FR-10 | Tech stack input as multi-select or free-text tags | P1 |
| FR-11 | Interest areas: predefined list + custom entries | P1 |
| FR-12 | **2-minute FAANG interview walkthrough** for users who've never done a FAANG interview (interactive animated preview of round-by-round format) | P1 |

### 4.2 Authentication
| ID | Requirement | Priority |
|----|-------------|----------|
| FR-15 | JWT-based login with token refresh | P0 |
| FR-16 | is_first_login flag triggers password change prompt | P0 |
| FR-17 | Password stored as bcrypt hash | P0 |
| FR-18 | Rate limiting on login endpoint (prevent brute force) | P1 |
| FR-19 | Logout / token invalidation | P0 |

### 4.3 Dashboard
| ID | Requirement | Priority |
|----|-------------|----------|
| FR-20 | **Action-first hero section:** Primary CTA = "Start Mock Interview" or "Continue Learning: [weak area]" | P0 |
| FR-21 | **ELO rating display:** Current ELO, target company hiring bar ELO, gap to close | P0 |
| FR-22 | **Round-by-round scorecard** from latest mock interview (Phone Screen, System Design, Behavioral, Domain, Bar Raiser) | P0 |
| FR-23 | **Gap map visualization:** target role demands vs current proficiency | P0 |
| FR-24 | **Pattern mastery tracker:** recurring FAANG archetype patterns with strength/weakness indicators | P0 |
| FR-25 | Highlight weak areas in red with "Focus Area" badges | P0 |
| FR-26 | "Resume Learning" button — continues from last position | P0 |
| FR-27 | "Start Mock Interview" button — launches interview simulation | P0 |
| FR-28 | "Targeted Round Practice" button — drill a specific weak round | P0 |
| FR-29 | Full overview section below hero: performance trends, mode comparisons, time stats | P1 |
| FR-30 | Show performance comparison: Comfort Mode vs Interview Mode vs Pressure Mode scores | P1 |
| FR-31 | Show ELO trend over time (graph) | P1 |
| FR-32 | **"Days Until Interview Ready"** estimate based on current pace and improvement trajectory | P1 |

### 4.4 Mock Interview Engine (Core Feature)

#### 4.4.1 Interview Structure
| ID | Requirement | Priority |
|----|-------------|----------|
| FR-100 | **5-round FAANG interview structure** per full mock session | P0 |
| FR-101 | **Round 1 — Phone Screen** (10 min for 30-min mock): 2-3 coding/problem-solving questions. Answer mode: Text/Code editor | P0 |
| FR-102 | **Round 2 — System Design** (8 min for 30-min mock): 1 deep architecture problem with follow-up probes. Answer mode: Voice + Diagram | P0 |
| FR-103 | **Round 3 — Behavioral** (5 min for 30-min mock): 2-3 STAR-method questions. Answer mode: Voice | P0 |
| FR-104 | **Round 4 — Domain-Specific** (4 min for 30-min mock): Role-specific depth questions. Answer mode: Hybrid (auto-selected per question) | P0 |
| FR-105 | **Round 5 — Bar Raiser** (3 min for 30-min mock): Cross-functional curveball questions. Answer mode: Voice | P0 |
| FR-106 | **Total mock interview duration: 30 minutes** (configurable) | P0 |
| FR-107 | Each round timed with visible countdown timer | P0 |
| FR-108 | Running out of time reduces round rating even if answers are good | P0 |
| FR-109 | **AI-generated questions daily** — no two mock interviews are ever identical | P0 |

#### 4.4.2 AI Interviewer Persona
| ID | Requirement | Priority |
|----|-------------|----------|
| FR-110 | **Real-time voice conversation** — AI interviewer responds conversationally, not static Q&A | P0 |
| FR-111 | Interviewer personality matches company culture (tough Google, design-focused Apple) | P0 |
| FR-112 | Interviewer pushes back on answers: "interesting, but have you considered..." | P0 |
| FR-113 | Interviewer gives hints when user is stuck (with score penalty for needing hints) | P0 |
| FR-114 | Interviewer asks clarifying follow-ups to probe depth | P0 |
| FR-115 | **Full conversation transcript saved** for post-interview review | P0 |
| FR-116 | **Single LLM handles all company personas** via system prompt engineering (no fine-tuned models) | P0 |
| FR-117 | **Guardrail system prompts** prevent AI from giving away answers through follow-up probes | P0 |
| FR-118 | **Technical accuracy validation layer** — cross-check AI responses against verified answer rubric before delivering | P1 |
| FR-119 | Interviewer says "that's not quite right" for partial answers to test resilience | P1 |

#### 4.4.3 Dynamic Follow-Up Probe Trees
| ID | Requirement | Priority |
|----|-------------|----------|
| FR-120 | Follow-up probes branch based on answer quality (3 tracks: strong, average, weak) | P0 |
| FR-121 | **Strong answer** → harder follow-up: "Now scale it to 100M users" | P0 |
| FR-122 | **Average answer** → guiding probe: "What data structure would help here?" | P0 |
| FR-123 | **Weak answer** → simpler redirect: "Let's start simpler — what components do you need?" | P0 |
| FR-124 | **5 levels deep** for probe trees | P0 |
| FR-125 | ELO points based on depth reached in probe tree (deeper = more points) | P0 |
| FR-126 | **AI-generated probe trees** — system generates branching paths dynamically | P0 |
| FR-127 | **Answer quality classification:** Keyword matching + semantic similarity scoring against rubric. Strong ≥70%, Average 40-69%, Weak <40% | P0 |
| FR-128 | **Daily question regeneration** — fresh probe trees generated each day to prevent memorization | P0 |
| FR-129 | System Design questions accept **any valid design** — evaluate against principles (scalability, trade-offs, fault tolerance) not specific architectures | P0 |

#### 4.4.4 Company-Specific Profiles (POC: Google + Apple)
| ID | Requirement | Priority |
|----|-------------|----------|
| FR-130 | Different question mix and weighting per company | P0 |
| FR-131 | **Google:** Heavy system design + coding, "Googleyness" behavioral, any language | P0 |
| FR-132 | **Apple:** Design thinking + domain depth, attention to detail, user experience focus | P0 |
| FR-133 | Company-specific scoring rubrics (what each company values most) | P0 |
| FR-134 | **Amazon:** Leadership Principles dominate every round, operational excellence focus | P2 (future) |
| FR-135 | **Meta:** Product sense + coding speed, move-fast culture | P2 (future) |
| FR-136 | **Netflix:** Culture fit + senior-level autonomy questions | P2 (future) |
| FR-137 | **FAANG-like** (Uber, Stripe, Airbnb): Adapted profiles | P2 (future) |
| FR-138 | **Fortune 500 / Startup:** Broader formats | P2 (future) |

#### 4.4.5 Rubric Reveal (Post-Question Feedback)
| ID | Requirement | Priority |
|----|-------------|----------|
| FR-250 | After each question, show **exactly what the interviewer was evaluating** | P0 |
| FR-251 | Show checklist: "Interviewer was looking for: (1) X, (2) Y, (3) Z. You covered N of M." | P0 |
| FR-252 | Link each missed rubric item to specific learning content (just-in-time learning) | P0 |
| FR-253 | Rubric reveal available in review/replay mode | P0 |

#### 4.4.6 Hiring Committee Simulation (Post-Mock)
| ID | Requirement | Priority |
|----|-------------|----------|
| FR-260 | **3 simulated interviewers** on the hiring committee | P0 |
| FR-261 | Each interviewer gives HIRE / LEAN HIRE / LEAN NO HIRE / NO HIRE per round they "conducted" | P0 |
| FR-262 | **Show disagreement between interviewers** — makes it realistic (e.g., "2 HIRE, 1 NO HIRE → LEAN HIRE") | P0 |
| FR-263 | **Majority vote with veto power** — single strong NO HIRE on a critical round = overall NO HIRE | P0 |
| FR-264 | Each interviewer quotes specific moments from the mock to justify their decision | P0 |
| FR-265 | Committee uses distinct interviewer names/titles and references real evaluation criteria | P0 |
| FR-266 | Final committee verdict: HIRE / NO HIRE with specific improvement recommendations | P0 |

### 4.5 Assessment Modes
| ID | Requirement | Priority |
|----|-------------|----------|
| FR-140 | **Comfort Mode:** No timer, hints available, relaxed learning (default for new users) | P0 |
| FR-141 | **Interview Mode:** Timed rounds, no free hints, AI interviewer active, scores are final | P0 |
| FR-142 | **Pressure Mode:** Interview Mode PLUS curveballs, deliberate silence, "that's not right" pushback, rapid-fire follow-ups | P1 |
| FR-143 | Pressure Mode unlocked after completing at least 2 Full Mock Interviews | P1 |
| FR-144 | Performance comparison across all 3 modes on dashboard | P1 |
| FR-145 | **Pressure Drop metric:** percentage score difference between Comfort and Pressure modes | P1 |

### 4.6 Interview Session Modes (Product Tiers)
| ID | Requirement | Priority |
|----|-------------|----------|
| FR-150 | **Quick Assessment (MVP):** 5-10 questions, single round (Phone Screen), instant ELO assignment + path generation. First experience for all new users | P0 |
| FR-151 | **Full Mock Interview:** All 5 rounds, 30 min, full scorecard + hiring committee simulation | P0 |
| FR-152 | **Targeted Round Practice:** User picks one weak round, 15-20 min focused drill, adaptive difficulty | P0 |
| FR-153 | **Pressure Test:** Full Mock + Pressure Mode, unlockable advanced challenge | P1 |
| FR-154 | **1 full mock per day limit + unlimited targeted practice rounds** (replaces daily question quota) | P0 |

### 4.7 Hybrid Answer Mode
| ID | Requirement | Priority |
|----|-------------|----------|
| FR-160 | System auto-selects answer input mode based on question type (user does NOT choose) | P0 |
| FR-161 | **Text/Code editor** for: coding problems, algorithm questions, phone screen coding | P0 |
| FR-162 | **Voice recording** for: behavioral questions, bar raiser, system design explanation | P0 |
| FR-163 | **Hybrid (both available)** for: domain-specific questions (some need code, some need explanation) | P0 |
| FR-164 | **Mid-answer switching:** User can switch from voice to text mid-answer (e.g., switch to code editor for writing code during voice explanation) | P0 |
| FR-165 | Record voice answer using browser MediaRecorder API | P0 |
| FR-166 | Playback recorded answer before submission | P0 |
| FR-167 | Re-record if not satisfied (before submit) | P0 |
| FR-168 | Submit voice + generate transcript via Whisper/Vosk | P0 |
| FR-169 | Store voice recording in object storage (compressed opus, auto-purge after 30 days, keep transcripts permanently) | P0 |
| FR-170-voice | Choose speech engine: Browser (online), Whisper (local), Vosk (local) | P0 |

### 4.8 ELO Rating System (Replaces flat 1-5 rating)

#### 4.8.1 ELO Mechanics
| ID | Requirement | Priority |
|----|-------------|----------|
| FR-300 | **Starting ELO varies by self-reported experience:** Junior=1000, Mid=1200, Senior=1400, Staff+=1600 | P0 |
| FR-301 | ELO adjusts up/down based on question difficulty vs user performance | P0 |
| FR-302 | **Overall ELO + sub-ELO per round type** (Coding ELO, System Design ELO, Behavioral ELO, Domain ELO) | P0 |
| FR-303 | Full Mock Interviews give **full ELO movement** (1x multiplier) | P0 |
| FR-304 | Targeted Practice rounds give **reduced ELO gains** (0.25x multiplier) to prevent gaming | P0 |
| FR-305 | **Retake encouragement:** After ELO drop, show motivational message + "Retake to improve" CTA, not just a declining number | P0 |

#### 4.8.2 Company-Specific Hiring Bars
| ID | Requirement | Priority |
|----|-------------|----------|
| FR-310 | **Google hiring bar:** L3=1400, L4=1600, L5=1800, L6=2000 | P0 |
| FR-311 | **Apple hiring bar:** L3=1350, L4=1550, L5=1750, L6=1950 | P0 |
| FR-312 | Dashboard shows: "You're at ELO [X]. [Company] [Level] bar: [Y]. Gap: [Z] points." | P0 |
| FR-313 | Hiring bars calibrated from user data after beta (initial values are estimates) | P1 |
| FR-314 | **Amazon/Meta/Netflix/Startup bars** added when those company profiles launch | P2 (future) |

#### 4.8.3 Per-Answer Rating (feeds into ELO calculation)
| ID | Requirement | Priority |
|----|-------------|----------|
| FR-170 | **Thinking Process Score (60% weight):** How user arrived at the answer | P0 |
| FR-171 | Thinking sub-scores: Asked clarifying questions (+), Considered multiple approaches (+), Identified trade-offs (+), Jumped to coding without planning (-) | P0 |
| FR-172 | **Accuracy Score (40% weight):** Correctness of final answer | P0 |
| FR-173 | Combined score feeds into ELO adjustment formula | P0 |

#### 4.8.4 Per-Round Rating
| ID | Requirement | Priority |
|----|-------------|----------|
| FR-175 | Rating per round = weighted average of answer ratings in that round | P0 |
| FR-176 | **Time-management rating** per round (separate dimension): on-time bonus, overtime penalty | P0 |
| FR-177 | Probe depth rating: how deep user went in follow-up probe trees (5 levels) | P0 |
| FR-178 | Hint usage penalty: each hint reduces round score | P0 |

#### 4.8.5 Overall Readiness (ELO-based)
| ELO Range | Label | Meaning |
|-----------|-------|---------|
| < 1200 | Not Ready | Significant gaps across multiple rounds |
| 1200 - 1500 | Getting There | Foundations present but major areas need work |
| 1500 - 1750 | Almost Ready | Strong in most areas, specific weaknesses to address |
| 1750 - 1900 | Ready | Consistently strong, minor polish needed |
| 1900+ | Interview Ready | Ready to schedule the real interview |

### 4.9 Question Archetype Pattern Tracking
| ID | Requirement | Priority |
|----|-------------|----------|
| FR-185 | Every question tagged with archetype pattern (e.g., "Scalability Trade-offs", "Conflict Resolution", "Tree/Graph Problems") | P0 |
| FR-186 | Track mastery per archetype pattern across all mock interviews | P0 |
| FR-187 | Pattern mastery visualization on dashboard | P0 |
| FR-188 | Learning path prioritizes weak archetype patterns, not just weak topics | P0 |

### 4.10 Learning Path & Content

#### 4.10.1 Gap-Based Learning Path
| ID | Requirement | Priority |
|----|-------------|----------|
| FR-190 | **Interview First:** Learning plan generated FROM Quick Assessment failures + gap analysis — no upfront study | P0 |
| FR-191 | Learning path covers: existing expertise (validate/deepen) + gap areas (stretch/grow) + cross-cutting concerns (every role needs) | P0 |
| FR-192 | Each topic has 4 content dimensions: Interview Prep, Deep Dive, Best Practices, Tips & Tricks | P0 |
| FR-193 | **AI-generated content** — all learning materials generated by AI | P0 |
| FR-194 | **Content depth varies by level:** L3 content is fundamentals-heavy, L6 content is architecture/strategy-heavy | P0 |
| FR-195 | **Company-specific content sourced from open sources** (Glassdoor, Blind, LeetCode discussions) for Amazon LP stories, Google Googleyness, etc. | P1 |
| FR-196 | Content displayed as Markdown/HTML with code examples (text/code only, no video) | P0 |
| FR-197 | Session bookmarking — save exact position (last_position JSONB) | P0 |
| FR-198 | Resume from last position on next login | P0 |

#### 4.10.2 Dynamic Path Reordering
| ID | Requirement | Priority |
|----|-------------|----------|
| FR-200 | After each mock interview, learning path **reorders by weakness** — weak areas move up 2-3 positions (gentle nudge, not full reshuffle) | P0 |
| FR-201 | Reordering based on archetype pattern weakness, not just topic weakness | P0 |
| FR-202 | **Company-specific weighting:** 70% company-specific priorities, 30% general improvement | P0 |
| FR-203 | Preserve completed topics, only reorder remaining topics | P0 |
| FR-204 | **Completed topics resurface** if user scores below 50% on related patterns in 2+ consecutive mocks | P0 |
| FR-205 | **User can override** reordering — manual drag-and-drop to rearrange their path | P0 |
| FR-206 | Show before/after path comparison: "Your path was updated based on mock interview results" | P1 |
| FR-207 | **Target company change handling:** Soft regeneration — keep completed topics, reweight remaining path + add company-specific gaps | P1 |

#### 4.10.3 Adaptive Scheduling
| ID | Requirement | Priority |
|----|-------------|----------|
| FR-210 | Calculate initial target dates from hours/day and topic estimated_hours | P0 |
| FR-211 | Recalculate on each session completion | P0 |
| FR-212 | Auto-extend deadlines when user is behind schedule | P0 |
| FR-213 | Preserve original dates when user is ahead | P0 |
| FR-214 | Show delay indicators on dashboard (red highlight) | P0 |
| FR-215 | Show original vs revised date comparison | P1 |

#### 4.10.4 Content Freshness
| ID | Requirement | Priority |
|----|-------------|----------|
| FR-230 | **AI regenerates question bank daily** — fresh questions every day | P0 |
| FR-231 | **Weekly content refresh** using latest interview reports from public sources (Glassdoor, Blind, LeetCode discuss) | P1 |

### 4.11 Real-Time Voice Conversation
| ID | Requirement | Priority |
|----|-------------|----------|
| FR-240 | **Real-time voice streaming** between user and AI interviewer via WebSocket | P0 |
| FR-241 | **Voice Activity Detection (VAD):** AI waits for 1.5s silence before responding (prevents crosstalk) | P0 |
| FR-242 | **Speech-to-text latency:** Keep under 2 seconds for natural conversation feel | P0 |
| FR-243 | **Custom technical vocabulary** loaded into speech engine for accurate transcription (Kubernetes, PostgreSQL, B-tree, etc.) | P0 |
| FR-244 | **Mic quality indicator** shown pre-interview. Warn if poor quality, suggest fixes. Poor mic does NOT affect score | P0 |
| FR-245 | Full conversation transcript saved for post-interview review and replay | P0 |

### 4.12 Review & Revisit
| ID | Requirement | Priority |
|----|-------------|----------|
| FR-220 | User can revisit any completed section at any time | P0 |
| FR-221 | **Replay any past mock interview** with full transcript, scorecard, rubric reveals, and AI feedback | P0 |
| FR-222 | Review mode doesn't affect progress or ELO | P0 |
| FR-223 | Show previous assessment results when revisiting | P1 |
| FR-224 | Compare mock interview scores over time (attempt 1 vs attempt 2 vs attempt 3) | P1 |
| FR-225 | **"Interview Ready" celebration:** Confetti + congratulations + downloadable prep summary PDF + option to keep practicing | P1 |

## 5. Non-Functional Requirements
| ID | Requirement |
|----|-------------|
| NFR-01 | Works on Chrome and Edge (Web Speech API support) |
| NFR-02 | Dark theme (bg-slate-950) with glassmorphism cards |
| NFR-03 | Responsive design (desktop-first, mobile-friendly) |
| NFR-04 | API responses < 200ms (p95) |
| NFR-05 | Voice upload/download < 2 seconds |
| NFR-06 | Backend on port 5000, Frontend on port 3000 or static file |
| NFR-07 | JWT token expiry: 24 hours with refresh |
| NFR-08 | Password: bcrypt with salt rounds >= 12 |
| NFR-09 | Structured JSON logging for all services |
| NFR-10 | 99.9% availability target (production) |
| NFR-11 | Support 10,000 concurrent users initially |
| NFR-12 | **Mock interview session state preserved on disconnect** — save state and resume, never restart |
| NFR-13 | **AI interviewer response latency < 3 seconds** |
| NFR-14 | **WebSocket for voice conversation**, REST for everything else |
| NFR-15 | Voice stored as compressed opus, auto-purge audio after 30 days, keep transcripts permanently |

## 6. User Flow (Interview First)
```
REGISTRATION
  │  Full Name, Email, Tech Stack, Interest Areas, Hours/Day
  │  + Target Company (Google/Apple), Target Role, Target Level
  ▼
FIRST LOGIN
  │  Force password change
  ▼
FAANG INTRO (optional, for newcomers)
  │  2-minute animated walkthrough: "Here's what a FAANG interview looks like"
  ▼
QUICK ASSESSMENT (Immediate — no upfront learning)
  │  5-10 questions, Phone Screen format, Comfort Mode
  │  Establishes starting ELO rating
  │  Identifies initial weakness patterns
  ▼
GAP ANALYSIS + PATH GENERATION
  │  System maps: Target Role Demands vs Assessment Results vs Tech Stack
  │  Generates learning path FROM failures (weakest areas first)
  │  Shows: "You're at ELO 1350. Google L5 bar: 1800. Gap: 450 points."
  ▼
DASHBOARD (Action-First)
  │  Hero: "Continue Learning: System Design" or "Start Mock Interview"
  │  ELO Score, Round Scorecard, Gap Map, Pattern Mastery
  │  Days Until Interview Ready estimate
  ▼
CORE LOOP (Repeat until Interview Ready):
  │
  ├─ LEARN (weak areas first, 4 dimensions per topic)
  │    Interview Prep → Deep Dive → Best Practices → Tips & Tricks
  │    Resumes from exact last position
  │
  ├─ MOCK INTERVIEW (30 min, 5 rounds)
  │    1. Phone Screen (Text/Code)
  │    2. System Design (Voice + Diagram)
  │    3. Behavioral (Voice)
  │    4. Domain-Specific (Hybrid)
  │    5. Bar Raiser (Voice)
  │    Real-time voice conversation with AI interviewer
  │    Dynamic probe trees (5 levels deep)
  │    Modes: Comfort | Interview | Pressure
  │
  ├─ SCORECARD + RUBRIC REVEAL
  │    Round-by-round scores + what interviewer was looking for
  │    Thinking (60%) vs Accuracy (40%) breakdown
  │    ELO adjustment shown
  │
  ├─ HIRING COMMITTEE SIMULATION
  │    3 interviewers: HIRE / NO HIRE per round
  │    Majority vote with veto power
  │    Specific improvement recommendations
  │
  ├─ PATH REORDER
  │    Weakest areas nudged up 2-3 positions
  │    Pattern-based + company-weighted (70/30)
  │
  └─ TARGETED PRACTICE (optional, unlimited)
       Pick one weak round, 15-20 min drill
       0.25x ELO multiplier (prevents gaming)
  ▼
INTERVIEW READY (ELO ≥ Company Hiring Bar)
  │  Confetti celebration + "You're ready!"
  │  Downloadable prep summary PDF
  │  Option to keep practicing or switch target company
```

## 7. Interview Round Details

### 7.1 Round Configuration by Company (POC)
| Round | Google | Apple |
|-------|--------|-------|
| Phone Screen | Coding (any lang), algorithmic focus | Coding + design sense, attention to detail |
| System Design | Heavy weight, scale focus, trade-off articulation | Design-driven architecture, user experience focus |
| Behavioral | "Googleyness", collaboration, intellectual humility | Design thinking, innovation, craftsmanship |
| Domain | Role-specific depth, any language | Role + design quality, Apple ecosystem awareness |
| Bar Raiser | Cross-functional, ambiguity handling | Innovation showcase, "think different" mentality |

### 7.2 Question Archetype Patterns
| Category | Archetypes |
|----------|-----------|
| System Design | Scalability Trade-offs, Data Modeling, API Design, Caching Strategy, Message Queues, Load Balancing, Database Selection |
| Coding | Arrays/Strings, Trees/Graphs, Dynamic Programming, Sliding Window, Binary Search, Recursion/Backtracking, Sorting |
| Behavioral | Conflict Resolution, Failure/Recovery, Leadership/Influence, Ambiguity Handling, Customer Obsession, Ownership, Bias for Action |
| Domain | Depends on selected role — backend, frontend, ML, DevOps, etc. |

## 8. Scoring & Rating

### 8.1 Per-Answer Rating
| Component | Weight | Description |
|-----------|--------|-------------|
| **Thinking Process** | **60%** | |
| - Clarifying Questions | 15% | Did user ask clarifying questions before answering? |
| - Multiple Approaches | 15% | Did user consider more than one approach? |
| - Trade-off Awareness | 15% | Did user identify and articulate trade-offs? |
| - Structured Communication | 15% | Did user communicate clearly and systematically? |
| **Accuracy** | **40%** | |
| - Correctness | 20% | Is the final answer correct? |
| - Completeness | 20% | Does the answer cover all expected points? |

### 8.2 Per-Round Rating
| Component | Description |
|-----------|-------------|
| Answer Quality | Weighted average of answer ratings in the round |
| Probe Depth | How deep user went in follow-up probe trees (Level 1-5) |
| Time Management | On-time bonus / overtime penalty |
| Hint Usage | Penalty for each hint requested |

### 8.3 ELO Adjustment Formula
- **Win** (strong answer on hard question) → ELO +30 to +50
- **Draw** (average answer on matching-difficulty question) → ELO +5 to +15
- **Loss** (weak answer on easy question) → ELO -20 to -40
- Targeted Practice rounds: all adjustments × 0.25

## 9. Product Tiers / Session Modes
| Mode | Duration | Rounds | Difficulty | Best For |
|------|----------|--------|-----------|----------|
| **Quick Assessment (MVP)** | 10-15 min | Phone Screen only | Fixed | New users, first experience, ELO assignment |
| Full Mock Interview | 30 min | All 5 rounds | Branching probe trees | Core experience, comprehensive eval |
| Targeted Round Practice | 15-20 min | Single selected round | Adaptive-up | Focused improvement on weak round |
| Pressure Test | 30 min | All 5 rounds + pressure | Branching + curveballs | Advanced users stress-testing readiness |

## 10. MVP Definition (POC Launch)
| Feature | Included in MVP? |
|---------|-----------------|
| Quick Assessment + Comfort Mode | YES |
| Google company profile | YES |
| Apple company profile | YES |
| Full Mock Interview (30 min) | YES |
| AI Interviewer (single LLM, prompt-based personas) | YES |
| ELO Rating System | YES |
| Gap Map + Learning Path Generation | YES |
| Dynamic Path Reordering | YES |
| Hybrid Answer Mode (voice/text/code) | YES |
| Rubric Reveal | YES |
| Hiring Committee Simulation | YES |
| Targeted Round Practice | Phase 2 |
| Pressure Mode | Phase 2 |
| Amazon/Meta/Netflix profiles | Phase 2 |
| Interview Ready celebration + PDF | Phase 2 |
| Days Until Ready estimate | Phase 2 |

## 11. Future Use Cases (Post-POC)
| Use Case | Description |
|----------|-------------|
| **Internal Team Assessment** | Companies assess their engineers for promotion readiness. Manager configures level bar, engineer takes mock, manager gets scorecard |
| **Bootcamp Graduation Gate** | Coding bootcamps use as final exam — students must hit minimum ELO before graduating |
| **Interviewer Training (Reverse Mode)** | User plays interviewer role. AI gives answers (good and bad). User rates, probes, decides HIRE/NO HIRE. Trains engineering managers |

## 12. Rate Cards (Free for POC, future pricing reference)
| Tier | Price | Includes |
|------|-------|----------|
| Free | $0 | 3 full mocks/month, unlimited Quick Assessments, 1 company profile, Comfort Mode |
| Pro | $19/month | Unlimited mocks, all company profiles, all modes, priority AI response, detailed analytics |
| Team | $49/user/month | Pro + team dashboards, promotion readiness reports, manager views |
| Enterprise | Custom | Team + custom company profiles, SSO, API access, bulk licensing |

## 13. Milestones
| Milestone | Description |
|-----------|-------------|
| M1 — Design Approved | Design doc reviewed, PRD v2 finalized |
| M2 — Core Backend & Data Model | User registration, gap analysis, ELO system, role/company profiles, learning path engine |
| M3 — Frontend — Registration & Dashboard | Registration with company/role/level, dashboard with ELO + scorecard + gap map |
| M4 — Mock Interview Engine | 5-round structure, question delivery, timer, round transitions (30 min format) |
| M5 — AI Interviewer Persona | Conversational AI with company-specific personality via single LLM |
| M6 — Real-Time Voice Conversation | WebSocket voice streaming, VAD, transcript generation |
| M7 — Dynamic Probe Trees | AI-generated branching questions, 5 levels deep, daily regeneration |
| M8 — Hybrid Answer Mode | Auto-select voice/text/code, mid-answer switching, voice recording |
| M9 — ELO Rating + Scoring | ELO mechanics, dual rating, round scores, hiring bar display |
| M10 — Rubric Reveal + Hiring Committee | Post-question rubric, 3-interviewer committee simulation |
| M11 — Pattern Tracking & Path Reordering | Archetype mastery, weakness-driven gentle reordering |
| M12 — Learning Module Engine | AI-generated content, 4 dimensions, level-appropriate depth, session bookmarking |
| M13 — Review & Replay | Mock interview replay with transcript, score comparison over time |
| M14 — Beta Launch | Internal beta with select users (Google + Apple profiles, Quick Assessment + Full Mock) |
| M15 — Production Launch | Public release |

## 14. Deployment (Free Options — POC)
| Platform | Cost | Limitations |
|----------|------|-------------|
| **Render.com** | Free | 750 hours/month, sleeps after 15 min inactive, free PostgreSQL |
| **Railway** | Free | $5 credit/month, PostgreSQL included |
| **Vercel + PythonAnywhere** | Free | Vercel for frontend, PythonAnywhere for Flask backend |
| **Local** | Free | SQLite, no hosting needed |

## 15. Testing Plan
| Test Type | Description |
|-----------|-------------|
| Unit Tests | Mock interview engine, probe tree logic, ELO calculation, path reordering. 85%+ coverage |
| Integration Tests | Full flows: register → quick assessment → ELO assignment → plan → mock → scorecard → committee → path reorder |
| Load Tests | 10,000 concurrent users simulation with active mock interviews |
| E2E Tests | Browser tests for full mock interview journey including real-time voice |
| AI Interviewer Tests | Response quality, persona consistency, probe depth accuracy, guardrail effectiveness |
| Voice Tests | VAD accuracy, transcription quality for technical terms, latency measurements |
| Accessibility | Screen reader compatibility, voice UI accessibility |
| Security | Auth endpoint penetration testing, JWT verification, input sanitization |

## 16. Resolved Design Decisions (from Brainstorming)
| # | Decision | Resolution |
|---|----------|-----------|
| 1 | LLM for AI Interviewer | Claude (free tier) or open-source — no budget, POC only |
| 2 | Persona consistency | System prompt engineering with guardrails — single LLM handles all personas |
| 3 | Prevent answer leakage | Guardrail system prompts + probe templates that hint without revealing |
| 4 | AI hallucination handling | Technical accuracy validation layer — cross-check against verified rubric |
| 5 | Probe tree authoring | AI-generated, regenerated daily |
| 6 | Probe tree depth | 5 levels |
| 7 | Answer quality branching | Keyword matching + semantic similarity. Strong ≥70%, Average 40-69%, Weak <40% |
| 8 | Question freshness | Daily AI regeneration + weekly content refresh from open sources |
| 9 | Memorization prevention | Daily regeneration + randomized probe paths + varied framing |
| 10 | System Design evaluation | Accept any valid design — evaluate principles not specific architectures |
| 11 | Starting ELO | Varies by self-reported level: Junior=1000, Mid=1200, Senior=1400, Staff+=1600 |
| 12 | Hiring bar calibration | Estimated initially, data-driven after beta |
| 13 | ELO per round | Both overall + sub-ELO per round type |
| 14 | ELO gaming prevention | Targeted Practice = 0.25x ELO multiplier |
| 15 | ELO drop discouragement | Motivational messaging + retake CTA |
| 16 | Company-specific bars | Yes — Google=1800 L5, Apple=1750 L5, etc. |
| 17 | Voice latency | < 2 seconds for natural feel |
| 18 | Crosstalk handling | VAD — 1.5s silence detection before AI responds |
| 19 | Poor mic quality | Warning indicator, no score penalty |
| 20 | Technical transcription | Custom vocabulary list in speech engine |
| 21 | Mid-answer voice-to-text | Yes, allowed |
| 22 | Voice storage | Compressed opus, 30-day auto-purge audio, keep transcripts |
| 23 | Committee size | 3 interviewers |
| 24 | Committee disagreement | Yes, show realistic disagreement |
| 25 | Committee framework | Majority vote with veto power |
| 26 | Committee realism | Distinct names/titles, quote specific moments, reference real criteria |
| 27 | Path reorder aggressiveness | Gentle nudge — move up 2-3 positions max |
| 28 | User override reordering | Yes, manual drag-and-drop allowed |
| 29 | Company vs general weighting | 70% company-specific, 30% general |
| 30 | Resurface completed topics | Yes, if score drops <50% on related patterns in 2+ consecutive mocks |
| 31 | Change target company | Soft regeneration — keep progress, reweight + add gaps |
| 32 | Content source | AI-generated |
| 33 | Content freshness | Weekly AI refresh from public interview sources |
| 34 | Level-specific depth | Yes — L3 fundamentals, L6 architecture/strategy |
| 35 | Company-specific content | Open sources (Glassdoor, Blind, LeetCode) |
| 36 | Content format | Text/code only, no video for v2.0 |
| 37 | Mock duration | 30 minutes (not 90) |
| 38 | First experience | Quick Assessment (Interview First) |
| 39 | FAANG newbie onboarding | 2-minute interactive animated walkthrough |
| 40 | Dashboard priority | Action-first hero + full overview below |
| 41 | Interview Ready celebration | Confetti + congrats + downloadable PDF + keep practicing option |
| 42 | Voice infrastructure | WebSocket for voice, REST for everything else |
| 43 | Scaling | Queue-based architecture — solve after POC |
| 44 | Prediction validation | Track user-reported outcomes post-beta |
| 45 | FAANG employee partners | Post-launch, not for POC |
| 46 | Daily quota | Eliminated — replaced with 1 mock/day + unlimited targeted practice |
| 47 | Launch companies | Google + Apple |
| 48 | Monetization | Free for POC, rate cards shown for future reference |
| 49 | MVP scope | Quick Assessment + Google + Apple + Comfort Mode |

## 17. Open Questions (Remaining)
1. **Notifications:** Email/push reminders for falling behind?
2. **Gamification:** Badges, streaks, leaderboards, "interview readiness streak"?
3. **Multi-Language:** English-only for v2.0?
4. **Offline Mode:** Download content + sync later?
5. **Pressure Mode Calibration:** How to calibrate pressure intensity to avoid frustrating users?

## 18. Out of Scope (v2.0)
- Industry-recognized certificates
- Live instructor sessions / mentorship
- Collaborative / group learning (mock interview with another user)
- Third-party LMS integration (Coursera, Udemy)
- Native mobile apps (iOS/Android)
- Real-time collaborative whiteboarding for system design
- Video recording of user during mock interview
- Integration with actual job application platforms
- Video/visual content (text/code only)
- Paid infrastructure (POC runs free/local)
