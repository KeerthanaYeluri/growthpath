# Product Requirements Document (PRD)
# GrowthPath v2.0 — Adaptive, Personalized Technical Learning Platform

## 1. Overview
GrowthPath is a web-based adaptive learning platform that generates personalized learning paths based on a user's current tech stack, interest areas, and daily availability. It delivers multi-dimensional content (Interview Prep, Deep Dive, Best Practices, Tips & Tricks), voice-based assessments with 5 questions per topic, adaptive scheduling, and detailed progress tracking.

## 2. Goals (from Design Doc)
| ID | Goal |
|----|------|
| G1 | Personalized learning path based on tech stack and interest areas |
| G2 | Multi-dimensional growth: interview prep, deep dive, best practices, tips & tricks |
| G3 | 5 questions/topic assessment with answer-first-then-validate. Daily cap: 15-30 questions |
| G4 | Voice-based answer recording with playback, review, and submission |
| G5 | Adaptive target dates that extend when learner falls behind |
| G6 | Resume exactly where user stopped |
| G7 | Rating system based on assessment performance (1-5 per answer) |
| G8 | Revisit and review any completed section at any time |

## 3. Non-Goals (v2.0)
| ID | Non-Goal |
|----|----------|
| NG1 | Not a certification platform |
| NG2 | No live instructor/mentorship |
| NG3 | No collaborative/group learning |
| NG4 | No third-party LMS integration |
| NG5 | No native mobile apps (web-responsive only) |

## 4. Functional Requirements

### 4.1 Registration & Onboarding
| ID | Requirement | Priority |
|----|-------------|----------|
| FR-01 | User registers with: full name, email, current tech stack, interest areas, hours/day | P0 |
| FR-02 | System generates credentials: email as username, default password welcome@123 | P0 |
| FR-03 | System generates personalized learning plan with target dates | P0 |
| FR-04 | Force password change on first login | P0 |
| FR-05 | Tech stack input as multi-select or free-text tags | P1 |
| FR-06 | Interest areas: predefined list + custom entries | P1 |

### 4.2 Authentication
| ID | Requirement | Priority |
|----|-------------|----------|
| FR-10 | JWT-based login with token refresh | P0 |
| FR-11 | is_first_login flag triggers password change prompt | P0 |
| FR-12 | Password stored as bcrypt hash | P0 |
| FR-13 | Rate limiting on login endpoint (prevent brute force) | P1 |
| FR-14 | Logout / token invalidation | P0 |

### 4.3 Dashboard
| ID | Requirement | Priority |
|----|-------------|----------|
| FR-20 | Show overall progress percentage | P0 |
| FR-21 | Show target dates per topic with visual timeline | P0 |
| FR-22 | Highlight delayed topics in red | P0 |
| FR-23 | "Resume Learning" button — continues from last position | P0 |
| FR-24 | Show daily question quota status (X/Y questions used) | P0 |
| FR-25 | Show rating summary across all topics | P1 |
| FR-26 | Show time spent per topic | P1 |

### 4.4 Learning Path & Content
| ID | Requirement | Priority |
|----|-------------|----------|
| FR-30 | Generate learning plan from tech stack + interests | P0 |
| FR-31 | Each topic has 4 content dimensions: Interview Prep, Deep Dive, Best Practices, Tips & Tricks | P0 |
| FR-32 | Content displayed as Markdown/HTML with code examples | P0 |
| FR-33 | User progresses through dimensions sequentially within each topic | P0 |
| FR-34 | Session bookmarking — save exact position (last_position JSONB) | P0 |
| FR-35 | Resume from last position on next login | P0 |
| FR-36 | Topics ordered by logical learning sequence | P0 |
| FR-37 | Display estimated hours remaining for each topic | P1 |
| FR-38 | "Mark for Review" option on any completed section | P1 |

### 4.5 Assessment
| ID | Requirement | Priority |
|----|-------------|----------|
| FR-40 | 5 questions per topic | P0 |
| FR-41 | Answer-first-then-validate: user answers before seeing correct answer | P0 |
| FR-42 | Show detailed correct answer after each submission | P0 |
| FR-43 | Deep dive review after showing correct answer | P0 |
| FR-44 | Rating 1-5 per answer based on quality | P0 |
| FR-45 | Support both text and voice answers | P0 |
| FR-46 | Overall topic rating computed from 5 answer ratings | P0 |
| FR-47 | Show matched keywords, missed keywords, word count in review | P1 |
| FR-48 | "Show Answer" button during assessment (with score penalty) | P1 |

### 4.6 Daily Question Quota
| ID | Requirement | Priority |
|----|-------------|----------|
| FR-50 | Daily cap configurable between 15-30 questions (default: 20) | P0 |
| FR-51 | Check quota before serving each question | P0 |
| FR-52 | Show friendly "come back tomorrow" message when cap reached | P0 |
| FR-53 | Quota resets at midnight in user's local timezone | P0 |
| FR-54 | Distribute questions across active topics (5 per topic per day) | P1 |
| FR-55 | Show remaining quota on dashboard and assessment screen | P0 |

### 4.7 Voice Recording
| ID | Requirement | Priority |
|----|-------------|----------|
| FR-60 | Record voice answer using browser MediaRecorder API | P0 |
| FR-61 | Playback recorded answer before submission | P0 |
| FR-62 | Re-record if not satisfied (before submit) | P0 |
| FR-63 | Submit voice + generate transcript via Whisper/Vosk | P0 |
| FR-64 | Store voice recording in object storage | P0 |
| FR-65 | Playback voice in assessment review / deep dive | P0 |
| FR-66 | Auto-purge recordings after topic completion (configurable) | P2 |
| FR-67 | Choose speech engine: Browser (online), Whisper (local), Vosk (local) | P0 |

### 4.8 Adaptive Scheduling
| ID | Requirement | Priority |
|----|-------------|----------|
| FR-70 | Calculate initial target dates from hours/day and topic estimated_hours | P0 |
| FR-71 | Recalculate on each session completion | P0 |
| FR-72 | Auto-extend deadlines when user is behind schedule | P0 |
| FR-73 | Preserve original dates when user is ahead | P0 |
| FR-74 | Show delay indicators on dashboard (red highlight) | P0 |
| FR-75 | Show original vs revised date comparison | P1 |

### 4.9 Review & Revisit
| ID | Requirement | Priority |
|----|-------------|----------|
| FR-80 | User can revisit any completed section at any time | P0 |
| FR-81 | "Revisit this section?" prompt after completing a topic | P1 |
| FR-82 | Review mode doesn't affect progress or ratings | P0 |
| FR-83 | Show previous assessment results when revisiting | P1 |

### 4.10 Rating System
| ID | Requirement | Priority |
|----|-------------|----------|
| FR-90 | Rating 1-5 per question based on answer quality | P0 |
| FR-91 | Topic rating = average of 5 question ratings | P0 |
| FR-92 | Overall proficiency rating across all topics | P0 |
| FR-93 | Visual rating display (stars or progress bar) | P1 |
| FR-94 | Rating trend over time (improving/declining) | P2 |

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

## 6. User Flow
```
REGISTRATION
  │  Full Name, Email, Tech Stack, Interest Areas, Hours/Day
  ▼
SYSTEM GENERATES
  │  Username = email, Password = welcome@123
  │  Personalized Learning Plan with Target Dates
  ▼
FIRST LOGIN
  │  Force password change
  ▼
DASHBOARD
  │  Overall Progress %, Target Dates, Delays, Resume Button, Quota Status
  ▼
LEARNING MODULE (per topic, 4 dimensions)
  │  1. Interview Prep → 2. Deep Dive → 3. Best Practices → 4. Tips & Tricks
  │  Resumes from exact last position
  ▼
ASSESSMENT (5 questions per topic)
  │  Daily cap: 15-30 questions
  │  Show question → User answers (text/voice) → Submit → Show correct answer
  │  → Deep dive review → Rate 1-5 → Next question
  ▼
REVIEW (optional)
  │  Revisit any completed section
  ▼
NEXT TOPIC
  │  Repeat until all topics completed
  ▼
COMPLETION
  │  Overall rating, proficiency summary, learning report
```

## 7. Content Dimensions (per topic)
| Dimension | Purpose | Example (Pytest topic) |
|-----------|---------|----------------------|
| Interview Prep | Common interview questions + model answers | "Explain Pytest fixtures and scopes" |
| Deep Dive | Thorough conceptual understanding | How fixtures work internally, yield vs return |
| Best Practices | Industry standards and patterns | conftest.py organization, fixture naming conventions |
| Tips & Tricks | Quick wins and lesser-known features | parametrize tricks, custom markers, plugin tips |

## 8. Question Distribution
- **5 questions per topic** (fixed)
- **15-30 questions per day** (configurable, default 20)
- **If 4 active topics**: ~5 questions per topic per day
- **If topic done early**: remaining quota rolls to next topic
- **Assessment follows**: answer-first-then-validate methodology

## 9. Scoring & Rating
| Component | Weight | Description |
|-----------|--------|-------------|
| Keyword Match | 40% | Answer contains expected technical keywords |
| Detail/Length | 30% | Answer is sufficiently detailed |
| Relevance | 20% | Answer stays on topic |
| Completeness | 10% | Covers multiple expected points |
| **Rating** | 1-5 | Mapped from total score: 0-20=1, 21-40=2, 41-60=3, 61-80=4, 81-100=5 |

## 10. Milestones
| Milestone | Description |
|-----------|-------------|
| M1 — Design Approved | Design doc reviewed, PRD finalized |
| M2 — Core Backend & Data Model | User registration, learning path engine, progress tracking APIs |
| M3 — Frontend — Registration & Dashboard | Registration flow, login, dashboard with progress |
| M4 — Learning Module Engine | Multi-dimensional content delivery |
| M5 — Assessment & Voice Recording | 5-question assessments, voice record/playback, rating |
| M6 — Adaptive Scheduling Engine | Dynamic target date recalculation |
| M7 — Review & Revisit Features | Section replay, bookmarking, review mode |
| M8 — Beta Launch | Internal beta with select users |
| M9 — Production Launch | Public release |

## 11. Deployment (Free Options)
| Platform | Cost | Limitations |
|----------|------|-------------|
| **Render.com** | Free | 750 hours/month, sleeps after 15 min inactive, free PostgreSQL |
| **Railway** | Free | $5 credit/month, PostgreSQL included |
| **Vercel + PythonAnywhere** | Free | Vercel for frontend, PythonAnywhere for Flask backend |
| **Local** | Free | SQLite, no hosting needed |

## 12. Testing Plan
| Test Type | Description |
|-----------|-------------|
| Unit Tests | Learning path generation, schedule calculation, rating computation. 85%+ coverage |
| Integration Tests | Full flows: register → login → plan → content → assess → rating |
| Load Tests | 10,000 concurrent users simulation |
| E2E Tests | Browser tests for critical journeys including voice recording |
| Accessibility | Screen reader compatibility, voice UI accessibility |
| Security | Auth endpoint penetration testing, JWT verification, input sanitization |

## 13. Open Questions (from Design Doc)
1. Content Generation: Manual, AI-generated, or hybrid?
2. Voice-to-Text: Auto-validate via transcription or manual review?
3. Rating Algorithm: Binary correct/incorrect or partial credit?
4. Notifications: Email/push reminders for falling behind?
5. Gamification: Badges, streaks, leaderboards?
6. Multi-Language: English-only for v2.0?
7. Offline Mode: Download content + sync later?
8. Password Policy: Complexity requirements beyond forced change?

## 14. Out of Scope (v2.0)
- Industry-recognized certificates
- Live instructor sessions / mentorship
- Collaborative / group learning
- Third-party LMS integration (Coursera, Udemy)
- Native mobile apps (iOS/Android)
- AI-generated follow-up questions
- Cloud deployment (self-hosted for now)
