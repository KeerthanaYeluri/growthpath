# Architecture Document — GrowthPath v2.0

## System Overview

```
                    ┌─────────────────┐
                    │   React + TW    │
                    │   Frontend      │
                    │   (Port 3000)   │
                    └────────┬────────┘
                             │ REST API
                    ┌────────▼────────┐
                    │   API Gateway   │
                    │   (Flask)       │
                    │   (Port 5000)   │
                    └────────┬────────┘
            ┌────────┬───────┼───────┬────────┐
            ▼        ▼       ▼       ▼        ▼
       ┌────────┐┌────────┐┌────────┐┌────────┐┌────────┐
       │  Auth  ││Learning││Assess- ││Schedule││ Voice  │
       │Service ││ Path   ││ ment   ││ Engine ││Storage │
       └────┬───┘└───┬────┘└───┬────┘└───┬────┘└───┬────┘
            │        │         │         │         │
            └────────┴─────────┴─────────┘         │
                         │                         │
                    ┌────▼────┐              ┌─────▼─────┐
                    │PostgreSQL│              │  Object   │
                    │/SQLite  │              │  Storage  │
                    └─────────┘              │(Local/S3) │
                                             └───────────┘
```

## Backend Services (Python/Flask)

### 1. Auth Service
- User registration (email, tech stack, interests, hours/day)
- Credential generation (email as username, default password: welcome@123)
- JWT authentication with token refresh
- Forced password change on first login
- Session management

### 2. Learning Path Engine
- Generates personalized learning plan from tech stack + interests
- Determines topic ordering, content depth, estimated timeline
- 4-dimension content delivery per topic:
  - Interview Preparation
  - Deep Dive
  - Best Practices
  - Tips & Tricks
- Resume from last position (session bookmarking)

### 3. Assessment Service
- 5 questions per topic
- Answer-first-then-validate methodology
- Voice recording upload + playback
- Rating computation (1-5 per answer)
- Daily question quota enforcement (15-30/day, configurable)
- Correct answer shown after submission

### 4. Scheduling Engine
- Calculates target dates from hours/day availability
- Dynamic recalculation on session completion
- Auto-extends deadlines when user falls behind
- Preserves dates when user is ahead of schedule

### 5. Voice Storage
- Voice recordings stored in object storage (local filesystem or S3)
- Lifecycle: Record → Playback → Submit → Store → Auto-purge
- WAV/WebM format support
- Local transcription via Whisper/Vosk

## Project Structure
```
growthpath/
  backend/
    app.py                    # Flask app, routes, API gateway
    auth.py                   # Registration, login, JWT, password
    learning_engine.py        # Learning path generation, content
    assessment.py             # Questions, scoring, ratings
    scheduler.py              # Target dates, adaptive scheduling
    transcriber.py            # Whisper/Vosk speech-to-text
    question_bank.py          # Role-based question bank
    models.py                 # SQLAlchemy data models
    database.py               # DB connection, migrations
    config.py                 # App configuration
    requirements.txt
    voice_recordings/         # Local voice storage
  frontend/
    index.html                # React + Tailwind SPA
    (or src/ for full React project)
  docs/
    01_BRIEF.md
    02_MARKET_AND_PERSONAS.md
    03_ARCHITECTURE.md
    04_PRD.md
    Design_Doc.docx
```

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/auth/register | Register with tech stack, interests, hours/day |
| POST | /api/auth/login | Login, returns JWT. Flags first login |
| PUT | /api/auth/password | Change password (mandatory on first login) |

### Learning Path
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/learning/plan | Fetch user's complete learning plan |
| GET | /api/learning/resume | Get last position to resume learning |
| GET | /api/learning/topic/{id}/content | Fetch topic content by dimension |
| POST | /api/learning/topic/{id}/review | Mark topic for re-review |

### Progress & Scheduling
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/progress/dashboard | Overall progress %, dates, delays |
| PUT | /api/progress/topic/{id} | Update progress (save position, time) |
| GET | /api/progress/schedule | Get revised schedule with extensions |

### Assessment
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/assessment/topic/{id}/questions | Fetch 5 questions (403 if quota exhausted) |
| POST | /api/assessment/topic/{id}/submit | Submit answer (text + voice). 429 if cap reached |
| GET | /api/assessment/topic/{id}/results | Get results, correct answers, rating |
| POST | /api/assessment/voice/upload | Upload voice recording |
| GET | /api/assessment/voice/{id} | Stream voice recording |
| GET | /api/assessment/ratings | Overall rating summary |
| GET | /api/assessment/quota | Today's quota status |
| PUT | /api/assessment/quota/configure | Set daily limit (15-30) |

### Transcription (existing)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/transcribe | Full audio transcription |
| POST | /api/transcribe/stream | Chunked streaming transcription |

## Data Models

### Users
| Column | Type | Description |
|--------|------|-------------|
| user_id | UUID (PK) | Unique identifier |
| email | VARCHAR | Email = username |
| password_hash | VARCHAR | bcrypt hash (default: welcome@123) |
| full_name | VARCHAR | Display name |
| tech_stack | JSONB | Current technologies |
| interest_areas | JSONB | Areas to improve |
| hours_per_day | DECIMAL | Daily learning hours |
| is_first_login | BOOLEAN | Force password change |
| created_at | TIMESTAMP | Account creation |
| last_active_at | TIMESTAMP | Last activity |

### Learning Plans
| Column | Type | Description |
|--------|------|-------------|
| plan_id | UUID (PK) | Plan identifier |
| user_id | UUID (FK) | Reference to user |
| plan_config | JSONB | Topics, ordering, structure |
| start_date | DATE | Plan start |
| estimated_end_date | DATE | Original target |
| revised_end_date | DATE | Dynamically updated |
| status | ENUM | active, paused, completed |

### Topics
| Column | Type | Description |
|--------|------|-------------|
| topic_id | UUID (PK) | Topic identifier |
| interest_area | VARCHAR | Parent area |
| title | VARCHAR | Topic name |
| estimated_hours | DECIMAL | Hours to complete |
| sequence_order | INT | Order in learning path |

### Topic Content
| Column | Type | Description |
|--------|------|-------------|
| content_id | UUID (PK) | Content identifier |
| topic_id | UUID (FK) | Parent topic |
| dimension | ENUM | interview_prep, deep_dive, best_practices, tips_and_tricks |
| content_body | TEXT | Learning content (Markdown/HTML) |
| order_in_dimension | INT | Order within dimension |

### User Progress
| Column | Type | Description |
|--------|------|-------------|
| progress_id | UUID (PK) | Record ID |
| user_id | UUID (FK) | User reference |
| topic_id | UUID (FK) | Topic reference |
| dimension | ENUM | Current dimension |
| status | ENUM | not_started, in_progress, completed, reviewing |
| last_position | JSONB | Exact bookmark for resume |
| target_date | DATE | Expected completion |
| actual_completed | TIMESTAMP | When finished |
| time_spent_hours | DECIMAL | Actual time spent |

### Assessments
| Column | Type | Description |
|--------|------|-------------|
| assessment_id | UUID (PK) | Assessment identifier |
| user_id | UUID (FK) | User reference |
| topic_id | UUID (FK) | Topic reference |
| question_number | INT (1-5) | Question sequence |
| question_text | TEXT | The question |
| user_answer_text | TEXT | User's typed answer |
| voice_recording_url | VARCHAR | Voice file path/URL |
| correct_answer | TEXT | Validated correct answer |
| is_correct | BOOLEAN | Pass/fail |
| rating | INT (1-5) | Rating for this answer |
| answered_at | TIMESTAMP | Submission time |

### Daily Question Quota
| Column | Type | Description |
|--------|------|-------------|
| quota_id | UUID (PK) | Record ID |
| user_id | UUID (FK) | User reference |
| date | DATE | Calendar date |
| questions_attempted | INT | Questions answered today |
| daily_limit | INT | User's cap (15-30, default 20) |
| limit_reached_at | TIMESTAMP | When cap was hit |

### Entity Relationships
```
Users ──(1:1)──▶ Learning Plans
Users ──(1:N)──▶ User Progress
Users ──(1:N)──▶ Daily Question Quota
Topics ──(1:N)──▶ Topic Content (4 dimensions per topic)
Topics ──(1:N)──▶ Assessments (5 questions per topic per user)
User Progress ──(N:1)──▶ Topics
Assessments ──(N:1)──▶ Users
Assessments ──(N:1)──▶ Topics
```

## Cross-Cutting Concerns

### Security
- JWT authentication with token refresh
- bcrypt password hashing, forced change on first login
- TLS 1.3 in transit, encryption at rest for voice
- Input validation against SQL injection and XSS
- Rate limiting on login endpoints

### Scalability
- Initial: 10,000 concurrent users → target 100,000
- API responses < 200ms (p95)
- Voice upload/download < 2 seconds
- Read replicas for dashboard queries
- Object storage with lifecycle policies

### Observability
- Structured JSON logging
- Metrics: DAU, completion rate, avg rating, voice usage, schedule extensions
- Alerts on error rate > 1%, latency p95 > 500ms

## Deployment Options (Free)
| Option | Frontend | Backend | Database | Voice Storage |
|--------|----------|---------|----------|---------------|
| **Local** | HTML file | Flask on localhost | SQLite | Local filesystem |
| **Render.com** | Static site (free) | Flask web service (free) | PostgreSQL (free) | Local or S3 |
| **Vercel + Railway** | Vercel (free) | Railway Flask (free) | Railway PostgreSQL | Railway volume |
| **GitHub Pages + PythonAnywhere** | GitHub Pages (free) | PythonAnywhere (free) | MySQL (free) | PythonAnywhere files |
