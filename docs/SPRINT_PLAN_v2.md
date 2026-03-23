# GrowthPath v2.0 — Sprint Plan
# FAANG Mock Interview Simulator

**Team:** Renu (Lead) + Anand (Dev)
**Sprint Duration:** 2 weeks each
**Total Sprints:** 8 sprints (16 weeks)
**POC Scope:** Google + Apple | Quick Assessment + Full Mock | Comfort Mode

---

## Existing Codebase Audit

### Reusable As-Is
| Feature | Status | Files |
|---------|--------|-------|
| Auth (register, login, JWT, password change) | ✅ Ready | app.py, storage.py |
| Profile management | ✅ Ready | app.py |
| Voice recording + 3 transcription engines | ✅ Ready | transcriber.py, frontend |
| LLM integration (Claude/OpenAI/Gemini) | ✅ Ready | llm_service.py |
| Resume parsing (PDF/DOCX) | ✅ Ready | resume_parser.py |
| PostgreSQL/SQLite storage layer | ✅ Ready | storage.py |
| Frontend SPA (React 18 + Tailwind) | ✅ Ready | index.html |

### Reusable with Modification
| Feature | What Changes | Files |
|---------|-------------|-------|
| Registration flow | Add company/role/level selection | app.py, index.html |
| Dashboard | Replace with ELO display, scorecard, gap map, action-first hero | index.html |
| Learning engine | Add gap-based generation + weakness reordering | learning_engine.py |
| Answer scoring | Add Thinking Process (60%) + Accuracy (40%) dual rating | scorer.py |
| Session management | Refactor for 5-round mock interview structure | app.py, storage.py |
| Daily quota | Replace with 1 mock/day + unlimited practice | app.py |
| Question bank | Replace with AI-generated daily questions + company profiles | question_bank.py |

### Build New
| Feature | Description |
|---------|-------------|
| Mock Interview Engine | 5-round FAANG structure, timer, round transitions |
| AI Interviewer Persona | Conversational system prompts, company personality |
| Dynamic Probe Trees | Branching follow-ups, 5 levels, answer quality classification |
| ELO Rating System | ELO calculation, sub-ELO per round, company hiring bars |
| Hiring Committee Simulation | 3 interviewers, HIRE/NO HIRE, veto logic |
| Rubric Reveal | Post-question evaluation checklist |
| Gap Map | Role demands vs current skills visualization |
| Quick Assessment | 5-10 question diagnostic, ELO assignment |
| Real-time Voice Conversation | WebSocket voice streaming with VAD |
| Company Profiles | Google + Apple question weights, rubrics, personas |

---

## Sprint Breakdown

---

### Sprint 1 (Weeks 1-2): Foundation — Registration, Company Profiles, ELO System

**Goal:** User registers with target company/role/level → system assigns starting ELO → gap map generated

**Renu (Backend):**
| Task | Est. Hours | Priority |
|------|-----------|----------|
| Extend user model: add target_company, target_role, target_level fields | 3h | P0 |
| Create company profiles data structure (Google + Apple): round weights, scoring rubrics, persona prompts | 6h | P0 |
| Build ELO rating module: starting ELO by level, adjustment formula, sub-ELO per round type | 8h | P0 |
| Create ELO storage: elo_ratings table (overall + per-round-type), elo_history table | 4h | P0 |
| Build gap map engine: map target role demands vs current tech stack, identify strength/gap/cross-cutting areas | 6h | P0 |
| Create company hiring bar configuration (Google L5=1800, Apple L5=1750, etc.) | 2h | P0 |
| Update /api/auth/register to accept company/role/level | 2h | P0 |
| New endpoint: GET /api/elo — return current ELO, sub-ELOs, company bar, gap | 3h | P0 |
| New endpoint: GET /api/gap-map — return role demands vs current proficiency | 3h | P0 |

**Anand (Frontend):**
| Task | Est. Hours | Priority |
|------|-----------|----------|
| Update RegisterScreen: add company selector (Google/Apple), role picker, level picker | 6h | P0 |
| Build GapMapComponent: visual display of role demands vs current skills | 6h | P0 |
| Build ELODisplayComponent: current ELO, target bar, gap, progress ring | 4h | P0 |
| Redesign DashboardScreen: action-first hero section with ELO + gap map | 6h | P0 |
| Update navigation for new flow | 2h | P0 |

**Sprint 1 Deliverable:** User registers → selects Google L5 Backend → sees starting ELO 1200 → sees gap map → dashboard shows "ELO 1200 / Google bar 1800 / Gap: 600"

---

### Sprint 2 (Weeks 3-4): Quick Assessment — Interview First Experience

**Goal:** New user immediately takes Quick Assessment after registration → gets ELO assignment → learning path generated from failures

**Renu (Backend):**
| Task | Est. Hours | Priority |
|------|-----------|----------|
| Build Quick Assessment engine: 5-10 questions, Phone Screen format, company-specific | 8h | P0 |
| AI question generation for Quick Assessment (Claude/LLM, company-aware) | 6h | P0 |
| Build answer quality classifier: keyword matching + semantic similarity (Strong ≥70%, Average 40-69%, Weak <40%) | 6h | P0 |
| Dual rating scorer: Thinking Process (60%) + Accuracy (40%) with sub-scores | 6h | P0 |
| ELO assignment from Quick Assessment results | 4h | P0 |
| Generate learning path FROM assessment failures (not from registration data alone) | 6h | P0 |
| New endpoints: POST /api/quick-assessment/start, POST /api/quick-assessment/submit, GET /api/quick-assessment/results | 4h | P0 |
| Tag each question with archetype pattern (Scalability Trade-offs, Trees/Graphs, etc.) | 3h | P0 |

**Anand (Frontend):**
| Task | Est. Hours | Priority |
|------|-----------|----------|
| Build QuickAssessmentScreen: question display, hybrid answer mode (text + voice), timer | 8h | P0 |
| Build post-assessment ResultsScreen: ELO assigned, round scores, weakness identified | 6h | P0 |
| Auto-redirect flow: Register → Quick Assessment → Results → Dashboard | 4h | P0 |
| Build FAANG intro walkthrough (2-min animated overview for newcomers) | 4h | P1 |
| Update DashboardScreen: show Quick Assessment results, learning path, "Start Full Mock" CTA | 4h | P0 |

**Sprint 2 Deliverable:** Register → immediately take Quick Assessment → "You're at ELO 1350. Google L5 bar: 1800." → learning path generated from weaknesses

---

### Sprint 3 (Weeks 5-6): Mock Interview Engine — 5-Round Structure

**Goal:** User takes a full 30-minute FAANG mock interview with all 5 rounds, timed, with round transitions

**Renu (Backend):**
| Task | Est. Hours | Priority |
|------|-----------|----------|
| Build mock interview session model: 5 rounds, status tracking, timer state | 6h | P0 |
| Build round configuration engine: time allocation per round for 30-min total | 4h | P0 |
| AI question generation per round type (Phone Screen=coding, System Design=architecture, Behavioral=STAR, Domain=role-specific, Bar Raiser=cross-functional) | 10h | P0 |
| Daily question regeneration system (fresh questions each day) | 4h | P0 |
| Round transition logic: auto-advance when time expires or user completes | 4h | P0 |
| Mock interview state persistence (resume on disconnect) | 4h | P0 |
| Enforce 1 full mock per day + unlimited targeted practice | 3h | P0 |
| New endpoints: POST /api/mock/start, GET /api/mock/{id}/round/{n}, POST /api/mock/{id}/next-round, POST /api/mock/{id}/end | 6h | P0 |
| New endpoint: POST /api/practice/start (targeted single-round practice) | 3h | P0 |

**Anand (Frontend):**
| Task | Est. Hours | Priority |
|------|-----------|----------|
| Build MockInterviewScreen: 5-round layout, round indicator, active round display | 8h | P0 |
| Build round timer component: countdown per round, visual warning at 20% time remaining | 4h | P0 |
| Build round transition UI: "Round 1 Complete → Moving to System Design..." | 4h | P0 |
| Hybrid answer mode per round: auto-switch between code editor (Phone Screen), voice (Behavioral/Bar Raiser), hybrid (Domain) | 8h | P0 |
| Build code editor component for Phone Screen round (Monaco or CodeMirror) | 6h | P0 |
| Mid-answer voice-to-text switching UI | 3h | P0 |

**Sprint 3 Deliverable:** Full 30-min mock interview → 5 rounds → timed → hybrid answer modes → questions generated per round type

---

### Sprint 4 (Weeks 7-8): AI Interviewer Persona + Dynamic Probe Trees

**Goal:** AI interviewer conducts real-time conversational interview with branching follow-up probes, 5 levels deep

**Renu (Backend):**
| Task | Est. Hours | Priority |
|------|-----------|----------|
| Build AI interviewer system prompts: company-specific persona (Google tough, Apple design-focused) | 6h | P0 |
| Build conversational interview engine: maintain context, follow-up logic, acknowledgments | 8h | P0 |
| Build probe tree generator: AI creates branching paths (strong/average/weak tracks) | 8h | P0 |
| Answer quality classifier integration: route to correct probe branch in real-time | 4h | P0 |
| Guardrail system: prevent AI from leaking answers in follow-ups | 4h | P0 |
| Hint system: user requests hint → score penalty applied → hint delivered | 3h | P0 |
| Probe depth tracking: record how deep user went (Level 1-5) per question | 3h | P0 |
| WebSocket endpoint for real-time voice conversation: /ws/mock/{id} | 6h | P0 |
| Voice Activity Detection (VAD): 1.5s silence → AI responds | 4h | P0 |

**Anand (Frontend):**
| Task | Est. Hours | Priority |
|------|-----------|----------|
| Build ConversationUI: real-time transcript display, AI speaking indicator, user speaking indicator | 8h | P0 |
| WebSocket client for voice streaming | 6h | P0 |
| Build hint button: "Get Hint" with penalty warning | 3h | P0 |
| Build probe depth indicator: visual breadcrumb showing current depth level | 3h | P1 |
| Mic quality indicator: pre-interview check with suggestions | 3h | P0 |
| Custom technical vocabulary display: show recognized tech terms during transcription | 2h | P1 |

**Sprint 4 Deliverable:** AI interviewer conducts conversational interview → probes deeper based on answer quality → 5 levels → full transcript saved

---

### Sprint 5 (Weeks 9-10): Scoring, ELO Update, Rubric Reveal

**Goal:** After mock interview, compute multi-dimensional scores, adjust ELO, show rubric reveal per question

**Renu (Backend):**
| Task | Est. Hours | Priority |
|------|-----------|----------|
| Build multi-dimensional scoring engine: Thinking (60%) + Accuracy (40%) with 4 sub-scores each | 6h | P0 |
| Build per-round scoring: answer quality + probe depth + time management + hint penalty | 4h | P0 |
| Build ELO adjustment engine: calculate ELO delta based on question difficulty vs performance | 6h | P0 |
| Sub-ELO updates per round type (Coding ELO, Design ELO, Behavioral ELO) | 3h | P0 |
| Targeted practice ELO multiplier (0.25x) | 2h | P0 |
| Build rubric reveal generator: "Interviewer was looking for: (1) X, (2) Y. You covered N of M." | 6h | P0 |
| Link missed rubric items to specific learning content | 4h | P0 |
| Build archetype pattern scoring: track mastery per pattern across all mocks | 4h | P0 |
| New endpoints: GET /api/mock/{id}/scorecard, GET /api/mock/{id}/rubric/{question_id}, GET /api/patterns | 4h | P0 |
| ELO history endpoint: GET /api/elo/history (for trend graph) | 2h | P0 |

**Anand (Frontend):**
| Task | Est. Hours | Priority |
|------|-----------|----------|
| Build ScorecardScreen: round-by-round scores, Thinking vs Accuracy breakdown, ELO change display | 8h | P0 |
| Build RubricRevealComponent: expandable per-question rubric checklist with ✅/❌ per item | 6h | P0 |
| Build ELO change animation: "ELO 1350 → 1420 (+70)" with animated counter | 3h | P0 |
| Build PatternMasteryGrid: archetype patterns with strength/weakness heat map | 6h | P0 |
| Update Dashboard: ELO trend graph, pattern mastery tracker | 4h | P0 |
| Link rubric misses to learning content ("Learn about Caching Strategy →") | 3h | P0 |

**Sprint 5 Deliverable:** Mock complete → full scorecard → rubric reveal per question → ELO updated → pattern mastery tracked

---

### Sprint 6 (Weeks 11-12): Hiring Committee + Path Reordering

**Goal:** Post-mock hiring committee simulation with HIRE/NO HIRE verdicts, learning path reorders by weakness

**Renu (Backend):**
| Task | Est. Hours | Priority |
|------|-----------|----------|
| Build hiring committee engine: 3 interviewers, each evaluates their assigned rounds | 6h | P0 |
| Committee decision logic: majority vote with veto power on critical rounds | 4h | P0 |
| Generate interviewer quotes: reference specific moments from mock transcript | 6h | P0 |
| Committee verdict + specific improvement recommendations | 3h | P0 |
| Build path reordering engine: gentle nudge (move weak areas up 2-3 positions) | 6h | P0 |
| Company-specific reorder weighting: 70% company priorities, 30% general improvement | 3h | P0 |
| Resurface completed topics if score drops <50% on related patterns in 2+ mocks | 3h | P0 |
| User override: allow manual path reordering (drag-and-drop API) | 3h | P0 |
| Target company change handler: soft regeneration (keep progress, reweight + add gaps) | 4h | P1 |
| New endpoints: GET /api/mock/{id}/committee, POST /api/learning/reorder, PUT /api/learning/manual-reorder | 4h | P0 |

**Anand (Frontend):**
| Task | Est. Hours | Priority |
|------|-----------|----------|
| Build HiringCommitteeScreen: 3 interviewer cards, each with photo/name/title, HIRE/NO HIRE badge, quoted reasoning | 8h | P0 |
| Committee verdict display: final decision with animation | 4h | P0 |
| Build PathReorderNotification: "Your learning path was updated based on mock results" with before/after comparison | 4h | P0 |
| Build drag-and-drop path reordering (user override) | 6h | P0 |
| Update LearningScreen: show reordered path, "Focus Area" badges on weak topics | 3h | P0 |
| "Retake Mock" CTA after NO HIRE verdict | 2h | P0 |

**Sprint 6 Deliverable:** Mock ends → hiring committee deliberates → HIRE/NO HIRE → learning path reorders → user sees what to work on

---

### Sprint 7 (Weeks 13-14): Learning Content + AI Generation + Review

**Goal:** AI-generated learning content at level-appropriate depth, review/replay system, Interview Ready celebration

**Renu (Backend):**
| Task | Est. Hours | Priority |
|------|-----------|----------|
| Build AI content generator: generate learning content per topic, 4 dimensions, level-specific depth | 8h | P0 |
| Level-specific content templates: L3 fundamentals, L5 architecture, L6 strategy | 4h | P0 |
| Weekly content refresh engine: pull from public sources (Glassdoor, Blind patterns) | 4h | P1 |
| Build mock replay system: store full conversation, allow step-through replay | 4h | P0 |
| Score comparison across attempts: attempt 1 vs 2 vs 3 | 3h | P0 |
| "Interview Ready" detection: ELO ≥ company hiring bar | 2h | P0 |
| Generate prep summary PDF for Interview Ready users | 4h | P1 |
| "Days Until Interview Ready" estimator: based on ELO trajectory | 3h | P1 |
| New endpoints: POST /api/content/generate/{topic}, GET /api/mock/{id}/replay, GET /api/readiness | 4h | P0 |

**Anand (Frontend):**
| Task | Est. Hours | Priority |
|------|-----------|----------|
| Update LearningScreen: display AI-generated content, level indicator | 4h | P0 |
| Build MockReplayScreen: step-through replay with transcript, scores, rubric at each step | 6h | P0 |
| Build score comparison view: side-by-side attempts with trend arrows | 4h | P0 |
| Build InterviewReadyScreen: confetti animation, congratulations, download PDF, keep practicing option | 4h | P1 |
| "Days Until Ready" widget on dashboard | 3h | P1 |
| Update SessionHistoryScreen: show all mocks with ELO change per session | 3h | P0 |

**Sprint 7 Deliverable:** Full learning loop working → AI-generated content → replay past mocks → Interview Ready celebration when ELO hits bar

---

### Sprint 8 (Weeks 15-16): Polish, Testing, Rate Cards, Launch Prep

**Goal:** End-to-end testing, performance optimization, rate cards page, production deployment

**Renu (Backend):**
| Task | Est. Hours | Priority |
|------|-----------|----------|
| End-to-end integration testing: register → quick assessment → learn → mock → committee → reorder → repeat | 8h | P0 |
| Unit tests: ELO calculation, probe tree logic, scoring, path reordering (85%+ coverage) | 8h | P0 |
| AI interviewer quality testing: persona consistency, guardrail effectiveness | 4h | P0 |
| Performance optimization: LLM response caching, query optimization | 4h | P0 |
| Error handling & edge cases: disconnects, timeouts, empty answers, LLM failures | 4h | P0 |
| Security audit: JWT, input sanitization, rate limiting | 3h | P0 |
| Database migrations for production PostgreSQL | 2h | P0 |
| Deployment config: Render/Railway setup | 3h | P0 |
| Bug fix buffer | 6h | P0 |

**Anand (Frontend):**
| Task | Est. Hours | Priority |
|------|-----------|----------|
| Build RateCardsPage: Free / Pro / Team / Enterprise tiers (display only, no payment) | 4h | P0 |
| E2E browser testing: full mock interview journey including voice | 6h | P0 |
| Cross-browser testing: Chrome + Edge (voice API compatibility) | 3h | P0 |
| Mobile responsive polish (desktop-first, mobile-friendly) | 4h | P1 |
| Loading states & UX polish across all screens | 4h | P0 |
| Accessibility pass: screen reader, keyboard navigation, voice UI | 3h | P1 |
| Dark theme consistency check (bg-slate-950 + glassmorphism) | 2h | P0 |
| Bug fix buffer | 6h | P0 |

**Sprint 8 Deliverable:** Production-ready POC deployed → Google + Apple profiles → full loop working → rate cards visible

---

## Sprint Summary

| Sprint | Weeks | Focus | Renu (Backend) | Anand (Frontend) | Key Deliverable |
|--------|-------|-------|----------------|-------------------|-----------------|
| S1 | 1-2 | Foundation | Company profiles, ELO system, gap map | Registration revamp, dashboard redesign | Register with company/role → ELO assigned → gap map |
| S2 | 3-4 | Quick Assessment | Assessment engine, dual rating, path from failures | Assessment screen, results, auto-redirect flow | Interview First → Quick Assessment → ELO → learning path |
| S3 | 5-6 | Mock Engine | 5-round structure, AI questions, timer, state mgmt | Mock interview UI, round transitions, code editor | Full 30-min mock with 5 rounds + hybrid answer modes |
| S4 | 7-8 | AI Interviewer | Conversational AI, probe trees, WebSocket, VAD | Conversation UI, voice streaming, hint system | AI interviewer conducts real-time interview with probes |
| S5 | 9-10 | Scoring & ELO | Multi-dim scoring, ELO engine, rubric, patterns | Scorecard, rubric reveal, ELO animation, pattern grid | Full scorecard → ELO updated → rubric revealed |
| S6 | 11-12 | Committee + Path | Hiring committee, path reordering, user override | Committee screen, path notification, drag-and-drop | Committee HIRE/NO HIRE → path reorders by weakness |
| S7 | 13-14 | Content + Review | AI content gen, replay system, readiness detection | Learning screen, replay, comparison, celebration | AI content → mock replay → Interview Ready detection |
| S8 | 15-16 | Polish + Launch | Testing, security, performance, deployment | Rate cards, E2E tests, responsive, accessibility | Production-ready POC deployed |

---

## Critical Path (Blockers)

```
S1: ELO System + Company Profiles ──────────────────────┐
                                                         │
S2: Quick Assessment (depends on S1: ELO) ──────────────┤
                                                         │
S3: Mock Interview Engine (depends on S1: company profiles) ──┤
                                                              │
S4: AI Interviewer (depends on S3: mock engine) ──────────────┤
                                                              │
S5: Scoring + ELO Update (depends on S4: AI interviewer + S1: ELO) ──┤
                                                                      │
S6: Committee + Path Reorder (depends on S5: scoring) ────────────────┤
                                                                      │
S7: Content + Review (depends on S6: path reorder) ───────────────────┤
                                                                      │
S8: Polish + Launch (depends on all above) ───────────────────────────┘
```

**Note:** Sprints are sequential because each builds on the previous. However, Renu and Anand can work in parallel within each sprint (backend + frontend simultaneously).

---

## Task Assignment Strategy

| Who | Primary Focus | Secondary Focus |
|-----|--------------|-----------------|
| **Renu** | Backend engines (ELO, mock interview, AI interviewer, scoring, committee, path reorder) | API endpoints, data models, LLM prompt engineering |
| **Anand** | Frontend screens (registration, dashboard, mock interview UI, scorecard, committee, replay) | UX polish, voice integration, responsive design |

**Overlap areas (pair program):**
- WebSocket voice conversation (S4) — requires tight backend-frontend coordination
- Mock interview flow (S3) — round transitions need both sides in sync
- ELO display + calculation (S5) — must match exactly

---

## Definition of Done (per Sprint)

- [ ] All P0 tasks completed and tested
- [ ] Backend endpoints documented and working
- [ ] Frontend screens functional with real data (not mocked)
- [ ] No critical bugs in happy path
- [ ] Code committed to main branch
- [ ] Sprint demo to each other (Renu + Anand review)

---

## Risk Register

| Risk | Impact | Mitigation |
|------|--------|------------|
| LLM API costs exceed free tier | Can't generate questions/run AI interviewer | Use Gemini free tier as fallback, cache aggressively, pre-generate questions |
| Real-time voice conversation latency | Bad interview experience | Start with text-based conversation (S3), add voice in S4, fallback to text if voice fails |
| AI interviewer breaks character | Unrealistic interview | Extensive system prompt testing, add guardrail layer, human review of edge cases |
| ELO calibration is off | Inaccurate readiness prediction | Launch with estimated bars, collect data during beta, adjust based on user feedback |
| 30-min mock is too long for testing | Slow development/testing | Add "debug mode" with 5-min mocks (1 min per round) for development |
| Frontend monolith (2782-line index.html) | Hard to maintain | Modularize incrementally per sprint — extract components as they're built |

---

## MVP Launch Checklist (End of Sprint 8)

- [ ] User can register with Google/Apple + role + level
- [ ] Quick Assessment works and assigns starting ELO
- [ ] Learning path generated from assessment failures
- [ ] Full 30-min mock interview with 5 rounds
- [ ] AI interviewer converses naturally with company persona
- [ ] Dynamic probe trees branch on answer quality (5 levels)
- [ ] Hybrid answer mode (voice/text/code) auto-selected per round
- [ ] Multi-dimensional scoring (Thinking 60% + Accuracy 40%)
- [ ] ELO updates after each mock
- [ ] Rubric reveal per question
- [ ] Hiring committee simulation (3 interviewers)
- [ ] Learning path reorders by weakness
- [ ] Mock interview replay with transcript
- [ ] Score comparison over time
- [ ] Rate cards page (display only)
- [ ] Deployed and accessible
