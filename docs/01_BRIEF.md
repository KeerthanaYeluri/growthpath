# Project Brief - GrowthPath (formerly AI Interview Booth)

## Vision
Build **GrowthPath** — an adaptive, personalized technical learning platform that takes a professional's current tech stack, areas of interest, and daily availability, then generates a personalized learning journey with multi-dimensional content, voice-based assessments, adaptive scheduling, and detailed progress tracking.

## Problem Statement
- Professionals lack structured, personalized learning paths
- Existing platforms offer generic courses without considering current skill level
- No voice-based practice for interview preparation
- Rigid deadlines cause frustration and abandonment
- No multi-dimensional skill growth (interview prep + deep dive + best practices + tips)
- No way to resume exactly where you left off

## Target Users
- QA Engineers / SDETs preparing for interviews and upskilling
- Software Engineers transitioning between stacks or roles
- DevOps / Frontend / Backend engineers wanting structured learning
- Fresh graduates building professional skills

## Core Value Proposition
- **Personalized**: Learning path based on YOUR tech stack and goals
- **Multi-dimensional**: 4 content types per topic (Interview, Deep Dive, Best Practices, Tips & Tricks)
- **Voice-first**: Record and playback answers, just like a real interview
- **Adaptive**: Deadlines extend automatically when life gets in the way
- **Resumable**: Pick up exactly where you left off
- **Assessed**: 5 questions per topic with answer-first-then-validate methodology

## Success Metrics
- User completes at least 1 full topic (all 4 dimensions + assessment)
- Average assessment rating >= 3/5
- 70%+ users resume after their first session
- Voice recording used by 50%+ of users
- Daily question cap prevents cognitive overload

## Tech Stack
- **Backend**: Python (Flask) — Auth, Learning Path Engine, Assessment, Scheduling
- **Frontend**: React + Tailwind CSS — Dashboard, Learning Modules, Voice UI
- **Database**: PostgreSQL (Users, Plans, Progress, Assessments) — or SQLite for local
- **Speech**: Web Speech API (online) + Faster-Whisper / Vosk (local)
- **Storage**: Local filesystem or S3 for voice recordings
- **Auth**: JWT-based token authentication

## Evolution from AI Interview Booth
| Feature | Interview Booth (v1) | GrowthPath (v2) |
|---------|---------------------|-----------------|
| Questions | 30 per session | 5 per topic, unlimited topics |
| Learning | None | 4-dimension content per topic |
| Users | Anonymous | Registration + Auth + Profiles |
| Progress | Single session | Persistent, resumable |
| Scheduling | None | Adaptive target dates |
| Assessment | Keyword scoring | Answer-first-then-validate + rating |
| Daily Limit | None | 15-30 questions/day cap |
| Voice | Record + playback | Record + playback + review + storage |
| Data | In-memory | Database (PostgreSQL/SQLite) |