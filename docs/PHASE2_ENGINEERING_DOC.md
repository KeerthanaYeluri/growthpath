# GrowthPath Phase 2 — AI-Powered Voice Interview Engine

## Engineering Document v1.0

---

## 1. Vision

Transform GrowthPath from a text-based learning platform into a **real-time AI voice interview simulator** where candidates upload their resume, an AI interviewer asks personalized questions via voice, candidates respond naturally, and an evaluation engine scores performance — all visible on an HR dashboard.

---

## 2. High-Level Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│  Frontend    │────▶│  Flask API   │────▶│  LLM Service    │
│  (React)     │◀────│  (Backend)   │◀────│  (GPT/Claude)   │
└─────┬───────┘     └──────┬───────┘     └─────────────────┘
      │                    │
      │  WebSocket/        │
      │  Audio Stream      │
      ▼                    ▼
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│  Web Speech  │     │  PostgreSQL  │     │  Resume Parser  │
│  API (STT/   │     │  Database    │     │  (PDF Extract)  │
│  TTS)        │     └──────────────┘     └─────────────────┘
└─────────────┘
```

---

## 3. Feature Breakdown

### F1: Resume Upload & Parsing
- Upload PDF/DOCX resume via frontend
- Extract text content (skills, experience, projects, education)
- Store parsed resume data in DB
- Feed resume context to LLM for personalized questions

### F2: LLM-Powered Question Generation
- Send resume + job role to LLM
- Generate 10-15 personalized interview questions
- Questions categorized: Technical, Behavioral, Situational, Project-based
- Difficulty adapts based on candidate's experience level
- Follow-up questions generated based on candidate's answers

### F3: Voice Interview — AI Asks Questions (TTS)
- Convert LLM-generated questions to speech
- Option A: Browser Web Speech API (free, no API cost)
- Option B: Cloud TTS (OpenAI TTS / ElevenLabs) for natural voice
- Interviewer persona: professional, encouraging, natural pauses

### F4: Candidate Voice Answer (STT)
- Capture candidate's voice response via microphone
- Option A: Browser Web Speech API (free, real-time)
- Option B: Whisper API for higher accuracy
- Real-time transcript display while speaking
- Silence detection to know when candidate is done

### F5: Conversational AI Interviewer
- LLM maintains conversation context (full interview history)
- Natural follow-up questions ("Can you elaborate on that?")
- Acknowledgment responses ("That's interesting, let me ask about...")
- Handles "I don't know" gracefully
- Time management (keeps interview within target duration)

### F6: Transcript Capture & Storage
- Full interview transcript saved (question + answer pairs)
- Timestamps for each exchange
- Audio recordings stored (optional)
- Transcript downloadable as PDF

### F7: AI Evaluation Engine
- Each answer scored on multiple dimensions:
  - **Relevance** (0-10): Does answer address the question?
  - **Depth** (0-10): Technical depth and specificity
  - **Communication** (0-10): Clarity, structure, confidence
  - **Examples** (0-10): Real-world examples provided?
- Overall score calculated
- Strengths & weaknesses identified
- Improvement suggestions per answer
- Comparison against ideal answer

### F8: HR Dashboard
- View all candidates and their interview results
- Filter by: role, score range, date, status
- Candidate profile: resume + transcript + scores
- Side-by-side candidate comparison
- Export reports (PDF/CSV)
- Interview scheduling (future)

---

## 4. Data Models (New Tables)

```sql
-- Uploaded resumes
CREATE TABLE resumes (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    filename TEXT,
    raw_text TEXT,
    parsed_data JSONB,        -- {skills, experience, education, projects}
    uploaded_at TIMESTAMP
);

-- AI Interview sessions
CREATE TABLE ai_interviews (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    resume_id TEXT REFERENCES resumes(id),
    job_role TEXT,
    status TEXT DEFAULT 'pending',  -- pending, in_progress, completed, evaluated
    target_duration_min INTEGER DEFAULT 30,
    actual_duration_min REAL,
    total_questions INTEGER DEFAULT 0,
    llm_model TEXT,
    created_at TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP
);

-- Individual Q&A exchanges
CREATE TABLE interview_exchanges (
    id TEXT PRIMARY KEY,
    interview_id TEXT REFERENCES ai_interviews(id),
    sequence_num INTEGER,
    question_text TEXT,
    question_category TEXT,      -- technical, behavioral, situational, project
    answer_text TEXT,
    answer_audio_url TEXT,
    answer_duration_sec REAL,
    ai_acknowledgment TEXT,      -- what AI said before next question
    timestamp TIMESTAMP
);

-- AI Evaluation scores
CREATE TABLE evaluations (
    id TEXT PRIMARY KEY,
    interview_id TEXT REFERENCES ai_interviews(id),
    exchange_id TEXT REFERENCES interview_exchanges(id),
    relevance_score REAL,
    depth_score REAL,
    communication_score REAL,
    examples_score REAL,
    total_score REAL,
    strengths TEXT,
    weaknesses TEXT,
    suggestions TEXT,
    ideal_answer TEXT
);

-- Overall interview results
CREATE TABLE interview_results (
    id TEXT PRIMARY KEY,
    interview_id TEXT REFERENCES ai_interviews(id),
    overall_score REAL,
    category_scores JSONB,       -- {technical: 8.5, behavioral: 7.0, ...}
    top_strengths JSONB,         -- ["strong system design", ...]
    improvement_areas JSONB,     -- ["needs more examples", ...]
    recommendation TEXT,         -- "strong_hire", "hire", "maybe", "no_hire"
    summary TEXT,                -- LLM-generated interview summary
    evaluated_at TIMESTAMP
);

-- HR users (separate from candidates)
CREATE TABLE hr_users (
    id TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT,
    company TEXT,
    role TEXT DEFAULT 'hr',      -- hr, admin, viewer
    created_at TIMESTAMP
);
```

---

## 5. API Endpoints (New)

### Resume
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/resume/upload` | Upload and parse resume |
| GET | `/api/resume/{id}` | Get parsed resume data |
| GET | `/api/resume/user/{user_id}` | Get user's resumes |

### AI Interview
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/interview/create` | Create interview (resume + role) |
| POST | `/api/interview/{id}/start` | Start interview, get first question |
| POST | `/api/interview/{id}/answer` | Submit answer, get next question |
| POST | `/api/interview/{id}/end` | End interview early |
| GET | `/api/interview/{id}` | Get interview details |
| GET | `/api/interview/{id}/transcript` | Get full transcript |
| GET | `/api/interview/{id}/transcript/pdf` | Download transcript as PDF |

### Evaluation
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/interview/{id}/evaluate` | Trigger AI evaluation |
| GET | `/api/interview/{id}/results` | Get evaluation results |

### HR Dashboard
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/hr/login` | HR user login |
| GET | `/api/hr/candidates` | List all candidates |
| GET | `/api/hr/candidate/{id}` | Candidate detail + scores |
| GET | `/api/hr/interviews` | All interviews with filters |
| GET | `/api/hr/compare` | Compare candidates side-by-side |
| GET | `/api/hr/export/{format}` | Export report (PDF/CSV) |

### Voice (WebSocket)
| Type | Endpoint | Description |
|------|----------|-------------|
| WS | `/ws/interview/{id}` | Real-time voice interview stream |

---

## 6. LLM Integration Design

### Prompts Structure

**Resume Analysis Prompt:**
```
You are an expert technical recruiter. Analyze this resume and extract:
- Key technical skills (with proficiency level)
- Years of experience
- Notable projects
- Education level
- Strengths and potential gaps for the role: {job_role}

Resume: {resume_text}
```

**Question Generation Prompt:**
```
You are a senior technical interviewer for the role: {job_role}.
Based on this candidate's resume: {parsed_resume}

Generate {n} interview questions:
- 40% Technical (based on their listed skills)
- 25% Behavioral (STAR format expected)
- 20% Situational (role-specific scenarios)
- 15% Project deep-dive (based on their projects)

Difficulty: {beginner|intermediate|senior} based on their experience.
Return as JSON array with category and difficulty per question.
```

**Conversational Interviewer Prompt (System):**
```
You are a professional interviewer named Alex conducting a {job_role} interview.
- Be warm but professional
- Ask one question at a time
- Listen to the full answer before responding
- Give brief acknowledgment before next question
- Ask follow-up if answer is vague or interesting
- Keep track of time ({duration} minutes total)
- Do NOT reveal scores or evaluation during interview
- If candidate says "I don't know", gently move on

Candidate resume context: {parsed_resume}
Questions to cover: {question_list}
```

**Evaluation Prompt:**
```
You are an expert interview evaluator. Score this answer:

Question: {question}
Category: {category}
Expected level: {difficulty}
Candidate's answer: {answer}
Candidate's resume context: {resume_summary}

Score on 4 dimensions (0-10 each):
1. Relevance - Does the answer address the question?
2. Depth - Technical depth and specificity
3. Communication - Clarity, structure, coherence
4. Examples - Real-world examples or concrete details

Also provide:
- strengths: what was good about this answer
- weaknesses: what was missing or could be improved
- suggestions: specific advice for improvement
- ideal_answer: a brief ideal answer for reference

Return as JSON.
```

---

## 7. Technology Choices

| Component | Technology | Why |
|-----------|-----------|-----|
| LLM | Claude API / OpenAI GPT-4 | Best quality for interview simulation |
| Speech-to-Text | Browser Web Speech API (Phase 1) → Whisper API (Phase 2) | Free first, upgrade later |
| Text-to-Speech | Browser Web Speech API (Phase 1) → OpenAI TTS (Phase 2) | Free first, natural voice later |
| Resume Parsing | PyPDF2 + python-docx | Extract text from PDF/DOCX |
| Real-time Comm | Flask-SocketIO | WebSocket for voice streaming |
| PDF Export | ReportLab or WeasyPrint | Generate transcript/report PDFs |
| Database | PostgreSQL (existing) | Already set up on Render |

---

## 8. Sprint Plan

### Sprint 1 (Week 1-2): Resume Upload & Question Generation
**Goal:** User uploads resume → AI generates personalized questions

| Task | Est. Hours | Priority |
|------|-----------|----------|
| Resume upload endpoint (PDF/DOCX) | 4h | P0 |
| PDF/DOCX text extraction | 4h | P0 |
| Resume parsing with LLM (skills, experience) | 6h | P0 |
| Resume data storage in PostgreSQL | 3h | P0 |
| LLM question generation from resume | 6h | P0 |
| Frontend: Resume upload UI | 4h | P0 |
| Frontend: Show parsed resume & generated questions | 4h | P0 |
| Database migrations (new tables) | 2h | P0 |
| Unit tests | 4h | P1 |

**Deliverable:** User uploads resume → sees AI-generated questions
**Sprint Total:** ~37 hours

---

### Sprint 2 (Week 3-4): Text-Based AI Interview
**Goal:** Full conversational interview in text (before adding voice)

| Task | Est. Hours | Priority |
|------|-----------|----------|
| Interview session creation & management | 4h | P0 |
| LLM conversational interviewer (chat mode) | 8h | P0 |
| Follow-up question logic | 4h | P0 |
| Interview state management (question flow) | 4h | P0 |
| Transcript capture & storage | 3h | P0 |
| Frontend: Interview chat UI | 6h | P0 |
| Frontend: Interview controls (start/pause/end) | 3h | P0 |
| Time management (interview duration) | 2h | P1 |
| "I don't know" handling | 2h | P1 |
| Unit tests | 4h | P1 |

**Deliverable:** Complete text-based AI interview with transcript
**Sprint Total:** ~40 hours

---

### Sprint 3 (Week 5-6): Voice Integration
**Goal:** Add voice input/output to the interview

| Task | Est. Hours | Priority |
|------|-----------|----------|
| Browser Speech-to-Text integration | 6h | P0 |
| Browser Text-to-Speech integration | 4h | P0 |
| Silence detection (answer complete) | 4h | P0 |
| Real-time transcript display | 4h | P0 |
| Microphone permission handling & UI | 3h | P0 |
| Audio recording & storage (optional) | 4h | P1 |
| Voice settings (speed, pitch, language) | 3h | P1 |
| Frontend: Voice interview UI (mic button, waveform) | 6h | P0 |
| Cross-browser testing | 4h | P1 |
| Fallback to text if voice unavailable | 2h | P1 |

**Deliverable:** Full voice-based AI interview experience
**Sprint Total:** ~40 hours

---

### Sprint 4 (Week 7-8): AI Evaluation Engine
**Goal:** Automatic scoring and feedback for each answer

| Task | Est. Hours | Priority |
|------|-----------|----------|
| Per-answer evaluation via LLM | 6h | P0 |
| Scoring dimensions (relevance, depth, comm, examples) | 4h | P0 |
| Overall interview scoring algorithm | 4h | P0 |
| Strengths & weaknesses identification | 3h | P0 |
| Improvement suggestions generation | 3h | P0 |
| Recommendation engine (hire/no-hire) | 3h | P0 |
| Interview summary generation | 3h | P0 |
| Evaluation results storage | 3h | P0 |
| Frontend: Results/scorecard page | 6h | P0 |
| Frontend: Per-answer feedback view | 4h | P0 |
| Unit tests | 4h | P1 |

**Deliverable:** Complete evaluation with scores, feedback, recommendations
**Sprint Total:** ~43 hours

---

### Sprint 5 (Week 9-10): HR Dashboard
**Goal:** HR users can view all candidates and results

| Task | Est. Hours | Priority |
|------|-----------|----------|
| HR user authentication (separate login) | 4h | P0 |
| Candidate listing with filters & search | 6h | P0 |
| Candidate detail page (resume + transcript + scores) | 6h | P0 |
| Side-by-side candidate comparison | 6h | P1 |
| Interview analytics (avg scores, trends) | 4h | P1 |
| Export to PDF | 6h | P1 |
| Export to CSV | 3h | P1 |
| Frontend: HR dashboard layout | 6h | P0 |
| Frontend: Filter/sort controls | 4h | P0 |
| Frontend: Comparison view | 4h | P1 |
| Role-based access control | 3h | P0 |

**Deliverable:** Fully functional HR dashboard
**Sprint Total:** ~52 hours

---

### Sprint 6 (Week 11-12): Polish, Testing & Deployment
**Goal:** Production-ready release

| Task | Est. Hours | Priority |
|------|-----------|----------|
| End-to-end testing (full interview flow) | 6h | P0 |
| Performance optimization (LLM response time) | 4h | P0 |
| Error handling & edge cases | 4h | P0 |
| Loading states & UX polish | 4h | P0 |
| Mobile responsive design | 4h | P1 |
| Rate limiting & API key management | 3h | P0 |
| Security audit (auth, data access) | 3h | P0 |
| Deployment & environment config | 3h | P0 |
| Documentation | 3h | P1 |
| Bug fixes buffer | 6h | P0 |

**Deliverable:** Production deployment on Render
**Sprint Total:** ~40 hours

---

## 9. Sprint Summary

| Sprint | Duration | Focus | Key Deliverable |
|--------|----------|-------|-----------------|
| Sprint 1 | Week 1-2 | Resume + Questions | Upload resume → AI questions |
| Sprint 2 | Week 3-4 | Text Interview | Chat-based AI interview |
| Sprint 3 | Week 5-6 | Voice Integration | Voice-based interview |
| Sprint 4 | Week 7-8 | Evaluation Engine | Scoring + feedback |
| Sprint 5 | Week 9-10 | HR Dashboard | Candidate management |
| Sprint 6 | Week 11-12 | Polish + Deploy | Production release |

**Total estimated effort:** ~252 hours across 12 weeks

---

## 10. LLM API Requirements

You will need ONE of these:
- **Claude API** (Anthropic) — recommended for quality
- **OpenAI GPT-4 API** — widely used, good quality
- **Google Gemini API** — free tier available

### Estimated API costs per interview (30 min, ~15 questions):
| Operation | Tokens | Cost (GPT-4) | Cost (Claude) |
|-----------|--------|---------------|---------------|
| Resume analysis | ~2K | $0.06 | $0.05 |
| Question generation | ~3K | $0.09 | $0.07 |
| 15 conversational turns | ~15K | $0.45 | $0.35 |
| Evaluation (15 answers) | ~10K | $0.30 | $0.25 |
| **Total per interview** | **~30K** | **~$0.90** | **~$0.72** |

---

## 11. Risk & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| LLM API costs | High at scale | Use caching, batch evaluation, cheaper models for simple tasks |
| Voice recognition accuracy | Poor answers captured wrong | Show real-time transcript, allow text correction |
| LLM hallucination | Wrong evaluation | Use structured prompts, human review option |
| Browser speech API inconsistency | Voice not working | Fallback to text mode, test across browsers |
| Latency (LLM response time) | Bad UX | Stream responses, show typing indicator, pre-fetch next question |
| Data privacy (resumes) | Legal risk | Encrypt at rest, clear retention policy, GDPR compliance |

---

## 12. Future Enhancements (Phase 3)

- Video interview (camera + facial expression analysis)
- Multiple interviewer personas (technical, HR, manager)
- Custom question banks per company
- Interview scheduling & calendar integration
- Candidate self-practice mode vs. HR-assigned mode
- AI-generated improvement learning paths based on interview results
- Multi-language support
- Integration with ATS (Applicant Tracking Systems)
