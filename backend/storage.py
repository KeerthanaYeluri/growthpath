"""
PostgreSQL-based persistent storage.
Drop-in replacement for the old JSON storage — same function signatures.
Reads DATABASE_URL from environment (provided by Render).
Falls back to SQLite for local development.
"""

import json
import os
import uuid
import hashlib
from datetime import datetime, date
from contextlib import contextmanager

DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL:
    import psycopg2
    import psycopg2.extras
    USE_PG = True
else:
    import sqlite3
    USE_PG = False

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
SQLITE_PATH = os.path.join(DATA_DIR, "growthpath.db")


def _ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


@contextmanager
def _get_db():
    """Get a database connection."""
    if USE_PG:
        conn = psycopg2.connect(DATABASE_URL)
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    else:
        _ensure_data_dir()
        conn = sqlite3.connect(SQLITE_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()


def _execute(conn, sql, params=None):
    """Execute SQL with correct placeholder style."""
    if USE_PG:
        sql = sql.replace("?", "%s")
        sql = sql.replace("INSERT OR REPLACE", "INSERT")
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    else:
        cur = conn.cursor()
    cur.execute(sql, params or ())
    return cur


def _fetchone(conn, sql, params=None):
    """Fetch one row as dict."""
    cur = _execute(conn, sql, params)
    row = cur.fetchone()
    if row is None:
        return None
    if USE_PG:
        return dict(row)
    return dict(row)


def _fetchall(conn, sql, params=None):
    """Fetch all rows as list of dicts."""
    cur = _execute(conn, sql, params)
    rows = cur.fetchall()
    if USE_PG:
        return [dict(r) for r in rows]
    return [dict(r) for r in rows]


def _hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def _gen_id():
    return str(uuid.uuid4())[:8]


def _json_field(value):
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False)
    return value


def _parse_json_field(value):
    if value is None:
        return value
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return value


def init_db():
    """Create all tables if they don't exist."""
    with _get_db() as conn:
        if USE_PG:
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    full_name TEXT NOT NULL,
                    tech_stack TEXT DEFAULT '[]',
                    interest_areas TEXT DEFAULT '[]',
                    hours_per_day REAL DEFAULT 2.0,
                    daily_limit INTEGER DEFAULT 20,
                    is_first_login INTEGER DEFAULT 1,
                    created_at TEXT,
                    last_active_at TEXT,
                    updated_at TEXT
                );
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    job_title TEXT,
                    role_name TEXT,
                    questions TEXT DEFAULT '[]',
                    answers TEXT DEFAULT '[]',
                    start_time TEXT,
                    end_time TEXT,
                    scorecard TEXT,
                    current_question INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'in_progress'
                );
                CREATE TABLE IF NOT EXISTS progress (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    topic TEXT,
                    dimension TEXT,
                    status TEXT DEFAULT 'not_started',
                    last_position TEXT,
                    time_spent_hours REAL DEFAULT 0,
                    target_date TEXT,
                    actual_completed TEXT,
                    created_at TEXT,
                    updated_at TEXT
                );
                CREATE TABLE IF NOT EXISTS assessments (
                    assessment_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    session_id TEXT,
                    question_id TEXT,
                    topic TEXT,
                    question_text TEXT,
                    user_answer_text TEXT,
                    voice_recording_url TEXT,
                    correct_answer TEXT,
                    total_score REAL DEFAULT 0,
                    rating REAL DEFAULT 0,
                    score_details TEXT,
                    answered_at TEXT
                );
                CREATE TABLE IF NOT EXISTS quotas (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    date TEXT,
                    questions_attempted INTEGER DEFAULT 0,
                    daily_limit INTEGER DEFAULT 20,
                    limit_reached_at TEXT
                );
                CREATE TABLE IF NOT EXISTS learning_plans (
                    user_id TEXT PRIMARY KEY,
                    plan TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS bookmarks (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    topic_id TEXT,
                    dimension TEXT,
                    position TEXT,
                    scroll_pct REAL DEFAULT 0,
                    saved_at TEXT
                );
                CREATE TABLE IF NOT EXISTS topic_assessments (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    topic_id TEXT,
                    question_id TEXT,
                    question_text TEXT,
                    user_answer TEXT,
                    correct_answer TEXT,
                    score REAL DEFAULT 0,
                    rating REAL DEFAULT 0,
                    show_answer_used INTEGER DEFAULT 0,
                    answered_at TEXT
                );
                CREATE TABLE IF NOT EXISTS reviews (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    topic_id TEXT,
                    dimension TEXT,
                    marked_at TEXT
                );
            """)
        else:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    full_name TEXT NOT NULL,
                    tech_stack TEXT DEFAULT '[]',
                    interest_areas TEXT DEFAULT '[]',
                    hours_per_day REAL DEFAULT 2.0,
                    daily_limit INTEGER DEFAULT 20,
                    is_first_login INTEGER DEFAULT 1,
                    created_at TEXT,
                    last_active_at TEXT,
                    updated_at TEXT
                );
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    job_title TEXT,
                    role_name TEXT,
                    questions TEXT DEFAULT '[]',
                    answers TEXT DEFAULT '[]',
                    start_time TEXT,
                    end_time TEXT,
                    scorecard TEXT,
                    current_question INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'in_progress'
                );
                CREATE TABLE IF NOT EXISTS progress (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    topic TEXT,
                    dimension TEXT,
                    status TEXT DEFAULT 'not_started',
                    last_position TEXT,
                    time_spent_hours REAL DEFAULT 0,
                    target_date TEXT,
                    actual_completed TEXT,
                    created_at TEXT,
                    updated_at TEXT
                );
                CREATE TABLE IF NOT EXISTS assessments (
                    assessment_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    session_id TEXT,
                    question_id TEXT,
                    topic TEXT,
                    question_text TEXT,
                    user_answer_text TEXT,
                    voice_recording_url TEXT,
                    correct_answer TEXT,
                    total_score REAL DEFAULT 0,
                    rating REAL DEFAULT 0,
                    score_details TEXT,
                    answered_at TEXT
                );
                CREATE TABLE IF NOT EXISTS quotas (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    date TEXT,
                    questions_attempted INTEGER DEFAULT 0,
                    daily_limit INTEGER DEFAULT 20,
                    limit_reached_at TEXT
                );
                CREATE TABLE IF NOT EXISTS learning_plans (
                    user_id TEXT PRIMARY KEY,
                    plan TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS bookmarks (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    topic_id TEXT,
                    dimension TEXT,
                    position TEXT,
                    scroll_pct REAL DEFAULT 0,
                    saved_at TEXT
                );
                CREATE TABLE IF NOT EXISTS topic_assessments (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    topic_id TEXT,
                    question_id TEXT,
                    question_text TEXT,
                    user_answer TEXT,
                    correct_answer TEXT,
                    score REAL DEFAULT 0,
                    rating REAL DEFAULT 0,
                    show_answer_used INTEGER DEFAULT 0,
                    answered_at TEXT
                );
                CREATE TABLE IF NOT EXISTS reviews (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    topic_id TEXT,
                    dimension TEXT,
                    marked_at TEXT
                );
            """)


# Initialize on import
init_db()


# ─── Users ───

def register_user(full_name, email, tech_stack, interest_areas, hours_per_day):
    """Register a new user. Returns user dict with generated credentials."""
    with _get_db() as conn:
        row = _fetchone(conn, "SELECT * FROM users WHERE LOWER(email) = LOWER(?)", (email,))
        if row:
            return None, "Email already registered"

        user_id = _gen_id()
        default_password = "welcome@123"
        now = datetime.now().isoformat()

        if isinstance(tech_stack, str):
            tech_stack = [s.strip() for s in tech_stack.split(",")]
        if isinstance(interest_areas, str):
            interest_areas = [s.strip() for s in interest_areas.split(",")]

        _execute(conn,
            """INSERT INTO users (user_id, email, password_hash, full_name, tech_stack,
               interest_areas, hours_per_day, is_first_login, created_at, last_active_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?, ?)""",
            (user_id, email.lower(), _hash_password(default_password), full_name,
             _json_field(tech_stack), _json_field(interest_areas),
             float(hours_per_day), now, now))

        user = {
            "user_id": user_id,
            "email": email.lower(),
            "password_hash": _hash_password(default_password),
            "full_name": full_name,
            "tech_stack": tech_stack,
            "interest_areas": interest_areas,
            "hours_per_day": float(hours_per_day),
            "is_first_login": True,
            "created_at": now,
            "last_active_at": now,
        }
        return user, None


def login_user(email, password):
    """Authenticate user. Returns user dict or None."""
    with _get_db() as conn:
        row = _fetchone(conn, "SELECT * FROM users WHERE LOWER(email) = LOWER(?)", (email,))
        if not row:
            return None, "User not found"

        user = dict(row)
        if user["password_hash"] != _hash_password(password):
            return None, "Invalid password"

        _execute(conn, "UPDATE users SET last_active_at = ? WHERE user_id = ?",
                 (datetime.now().isoformat(), user["user_id"]))

        user["tech_stack"] = _parse_json_field(user["tech_stack"])
        user["interest_areas"] = _parse_json_field(user["interest_areas"])
        user["is_first_login"] = bool(user["is_first_login"])
        return user, None


def change_password(user_id, new_password):
    """Change user's password and clear first_login flag."""
    with _get_db() as conn:
        row = _fetchone(conn, "SELECT * FROM users WHERE user_id = ?", (user_id,))
        if not row:
            return False, "User not found"
        _execute(conn, "UPDATE users SET password_hash = ?, is_first_login = 0 WHERE user_id = ?",
                 (_hash_password(new_password), user_id))
        return True, None


def get_user(user_id):
    """Get user by ID."""
    with _get_db() as conn:
        row = _fetchone(conn, "SELECT * FROM users WHERE user_id = ?", (user_id,))
        if not row:
            return None
        user = dict(row)
        user["tech_stack"] = _parse_json_field(user["tech_stack"])
        user["interest_areas"] = _parse_json_field(user["interest_areas"])
        user["is_first_login"] = bool(user["is_first_login"])
        return user


def update_user_activity(user_id):
    """Update last_active_at timestamp."""
    with _get_db() as conn:
        _execute(conn, "UPDATE users SET last_active_at = ? WHERE user_id = ?",
                 (datetime.now().isoformat(), user_id))


# ─── Learning Sessions ───

def create_session(user_id, job_title, questions, role_name):
    """Create a new interview/learning session."""
    session_id = _gen_id()
    now = datetime.now().isoformat()

    session = {
        "session_id": session_id,
        "user_id": user_id,
        "job_title": job_title,
        "role_name": role_name,
        "questions": questions,
        "answers": [],
        "start_time": now,
        "end_time": None,
        "scorecard": None,
        "current_question": 0,
        "status": "in_progress",
    }

    with _get_db() as conn:
        _execute(conn,
            """INSERT INTO sessions (session_id, user_id, job_title, role_name, questions,
               answers, start_time, current_question, status)
               VALUES (?, ?, ?, ?, ?, ?, ?, 0, 'in_progress')""",
            (session_id, user_id, job_title, role_name,
             _json_field(questions), '[]', now))
    return session


def get_session(session_id):
    """Get session by ID."""
    with _get_db() as conn:
        row = _fetchone(conn, "SELECT * FROM sessions WHERE session_id = ?", (session_id,))
        if not row:
            return None
        s = dict(row)
        s["questions"] = _parse_json_field(s["questions"])
        s["answers"] = _parse_json_field(s["answers"])
        s["scorecard"] = _parse_json_field(s["scorecard"])
        return s


def update_session(session_id, updates):
    """Update session fields."""
    session = get_session(session_id)
    if not session:
        return None

    session.update(updates)
    with _get_db() as conn:
        _execute(conn,
            """UPDATE sessions SET job_title=?, role_name=?, questions=?, answers=?,
               start_time=?, end_time=?, scorecard=?, current_question=?, status=?
               WHERE session_id=?""",
            (session["job_title"], session["role_name"],
             _json_field(session["questions"]), _json_field(session["answers"]),
             session["start_time"], session.get("end_time"),
             _json_field(session.get("scorecard")), session["current_question"],
             session["status"], session_id))
    return session


def add_answer(session_id, answer):
    """Add an answer to a session."""
    session = get_session(session_id)
    if not session:
        return None

    session["answers"].append(answer)
    session["current_question"] = len(session["answers"])

    with _get_db() as conn:
        _execute(conn, "UPDATE sessions SET answers=?, current_question=? WHERE session_id=?",
                 (_json_field(session["answers"]), session["current_question"], session_id))
    return session


def finish_session(session_id, scorecard):
    """Mark session as completed with scorecard."""
    session = get_session(session_id)
    if not session:
        return None

    now = datetime.now().isoformat()
    with _get_db() as conn:
        _execute(conn,
            "UPDATE sessions SET end_time=?, scorecard=?, status='completed' WHERE session_id=?",
            (now, _json_field(scorecard), session_id))

    session["end_time"] = now
    session["scorecard"] = scorecard
    session["status"] = "completed"
    return session


def get_user_sessions(user_id):
    """Get all sessions for a user."""
    with _get_db() as conn:
        rows = _fetchall(conn, "SELECT * FROM sessions WHERE user_id = ?", (user_id,))
        for s in rows:
            s["questions"] = _parse_json_field(s["questions"])
            s["answers"] = _parse_json_field(s["answers"])
            s["scorecard"] = _parse_json_field(s["scorecard"])
        return rows


def get_resumable_session(user_id):
    """Get the last in-progress session for resume."""
    with _get_db() as conn:
        row = _fetchone(conn,
            "SELECT * FROM sessions WHERE user_id = ? AND status = 'in_progress' ORDER BY start_time DESC LIMIT 1",
            (user_id,))
        if not row:
            return None
        s = dict(row)
        s["questions"] = _parse_json_field(s["questions"])
        s["answers"] = _parse_json_field(s["answers"])
        s["scorecard"] = _parse_json_field(s["scorecard"])
        return s


# ─── Progress Tracking ───

def update_progress(user_id, topic, dimension, status, position=None, time_spent=0):
    """Update user's progress on a topic."""
    key = f"{user_id}_{topic}_{dimension}"
    now = datetime.now().isoformat()

    with _get_db() as conn:
        row = _fetchone(conn, "SELECT * FROM progress WHERE id = ?", (key,))
        if row:
            entry = dict(row)
            new_time = entry["time_spent_hours"] + time_spent
            new_pos = position if position is not None else entry["last_position"]
            actual = now if status == "completed" else entry["actual_completed"]
            _execute(conn,
                """UPDATE progress SET status=?, last_position=?, time_spent_hours=?,
                   actual_completed=?, updated_at=? WHERE id=?""",
                (status, new_pos, new_time, actual, now, key))
            entry.update({"status": status, "last_position": new_pos,
                         "time_spent_hours": new_time, "actual_completed": actual, "updated_at": now})
            return entry
        else:
            actual = now if status == "completed" else None
            _execute(conn,
                """INSERT INTO progress (id, user_id, topic, dimension, status, last_position,
                   time_spent_hours, actual_completed, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (key, user_id, topic, dimension, status, position, time_spent, actual, now, now))
            return {
                "user_id": user_id, "topic": topic, "dimension": dimension,
                "status": status, "last_position": position,
                "time_spent_hours": time_spent, "target_date": None,
                "actual_completed": actual, "created_at": now, "updated_at": now,
            }


def get_user_progress(user_id):
    """Get all progress entries for a user."""
    with _get_db() as conn:
        rows = _fetchall(conn, "SELECT * FROM progress WHERE user_id = ?", (user_id,))
        return {r["id"]: r for r in rows}


def get_dashboard_data(user_id):
    """Get dashboard summary for a user."""
    user = get_user(user_id)
    if not user:
        return None

    sessions = get_user_sessions(user_id)
    completed = [s for s in sessions if s["status"] == "completed"]
    in_progress = get_resumable_session(user_id)

    total_score = 0
    total_sessions = len(completed)
    topic_scores = {}

    for s in completed:
        sc = s.get("scorecard", {})
        if sc:
            total_score += sc.get("overall_score", 0)
            for topic, score in sc.get("topic_scores", {}).items():
                if topic not in topic_scores:
                    topic_scores[topic] = []
                topic_scores[topic].append(score)

    avg_score = round(total_score / total_sessions) if total_sessions > 0 else 0

    for topic in topic_scores:
        topic_scores[topic] = round(sum(topic_scores[topic]) / len(topic_scores[topic]))

    quota = get_daily_quota(user_id)

    return {
        "user": {
            "full_name": user["full_name"],
            "email": user["email"],
            "tech_stack": user["tech_stack"],
            "interest_areas": user["interest_areas"],
            "hours_per_day": user["hours_per_day"],
        },
        "stats": {
            "total_sessions": total_sessions,
            "average_score": avg_score,
            "topic_scores": topic_scores,
        },
        "has_resumable_session": in_progress is not None,
        "resumable_session_id": in_progress["session_id"] if in_progress else None,
        "quota": quota,
    }


# ─── Daily Question Quota ───

def get_daily_quota(user_id):
    """Get today's quota for a user."""
    today = date.today().isoformat()
    key = f"{user_id}_{today}"

    with _get_db() as conn:
        row = _fetchone(conn, "SELECT * FROM quotas WHERE id = ?", (key,))
        if row:
            return dict(row)

        user = get_user(user_id)
        daily_limit = 20
        if user:
            daily_limit = user.get("daily_limit", 20)
        daily_limit = min(max(daily_limit, 15), 30)

        quota = {
            "id": key,
            "user_id": user_id,
            "date": today,
            "questions_attempted": 0,
            "daily_limit": daily_limit,
            "limit_reached_at": None,
        }
        _execute(conn,
            "INSERT INTO quotas (id, user_id, date, questions_attempted, daily_limit) VALUES (?, ?, ?, 0, ?)",
            (key, user_id, today, daily_limit))
        return quota


def increment_quota(user_id):
    """Increment today's question count. Returns (allowed, quota)."""
    quota = get_daily_quota(user_id)
    key = quota["id"]

    if quota["questions_attempted"] >= quota["daily_limit"]:
        return False, quota

    with _get_db() as conn:
        new_count = quota["questions_attempted"] + 1
        limit_reached = None
        if new_count >= quota["daily_limit"]:
            limit_reached = datetime.now().isoformat()

        _execute(conn, "UPDATE quotas SET questions_attempted=?, limit_reached_at=? WHERE id=?",
                 (new_count, limit_reached, key))

        quota["questions_attempted"] = new_count
        quota["limit_reached_at"] = limit_reached
        return True, quota


def configure_quota(user_id, daily_limit):
    """Set user's preferred daily limit (15-30)."""
    daily_limit = min(max(int(daily_limit), 15), 30)
    with _get_db() as conn:
        _execute(conn, "UPDATE users SET daily_limit = ? WHERE user_id = ?", (daily_limit, user_id))
    return daily_limit


# ─── Assessment Results Storage ───

def save_assessment(user_id, session_id, question_id, topic, question_text,
                    user_answer, correct_answer, score, rating, voice_url=None):
    """Save individual assessment result."""
    assessment_id = _gen_id()
    now = datetime.now().isoformat()

    entry = {
        "assessment_id": assessment_id,
        "user_id": user_id,
        "session_id": session_id,
        "question_id": question_id,
        "topic": topic,
        "question_text": question_text,
        "user_answer_text": user_answer,
        "voice_recording_url": voice_url,
        "correct_answer": correct_answer,
        "total_score": score.get("total_score", 0),
        "rating": rating,
        "score_details": score,
        "answered_at": now,
    }

    with _get_db() as conn:
        _execute(conn,
            """INSERT INTO assessments (assessment_id, user_id, session_id, question_id, topic,
               question_text, user_answer_text, voice_recording_url, correct_answer,
               total_score, rating, score_details, answered_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (assessment_id, user_id, session_id, question_id, topic, question_text,
             user_answer, voice_url, correct_answer,
             score.get("total_score", 0), rating, _json_field(score), now))

    return entry


def get_user_assessments(user_id, topic=None):
    """Get all assessments for a user, optionally filtered by topic."""
    with _get_db() as conn:
        if topic:
            rows = _fetchall(conn,
                "SELECT * FROM assessments WHERE user_id = ? AND topic = ? ORDER BY answered_at DESC",
                (user_id, topic))
        else:
            rows = _fetchall(conn,
                "SELECT * FROM assessments WHERE user_id = ? ORDER BY answered_at DESC",
                (user_id,))

        for a in rows:
            a["score_details"] = _parse_json_field(a["score_details"])
        return rows


def get_ratings_summary(user_id):
    """Get rating summary across all topics."""
    assessments = get_user_assessments(user_id)
    topic_ratings = {}

    for a in assessments:
        topic = a.get("topic", "Unknown")
        if topic not in topic_ratings:
            topic_ratings[topic] = []
        topic_ratings[topic].append(a.get("rating", 0))

    summary = {}
    for topic, ratings in topic_ratings.items():
        summary[topic] = {
            "average_rating": round(sum(ratings) / len(ratings), 1),
            "total_questions": len(ratings),
            "ratings": ratings,
        }

    overall = []
    for r in topic_ratings.values():
        overall.extend(r)

    return {
        "overall_rating": round(sum(overall) / len(overall), 1) if overall else 0,
        "total_assessed": len(overall),
        "per_topic": summary,
    }


# ─── User Profile ───

def update_user_profile(user_id, updates):
    """Update user profile fields."""
    user = get_user(user_id)
    if not user:
        return None, "User not found"

    allowed_fields = ["full_name", "tech_stack", "interest_areas", "hours_per_day", "daily_limit"]
    for key, value in updates.items():
        if key in allowed_fields:
            if key == "tech_stack" and isinstance(value, str):
                value = [s.strip() for s in value.split(",")]
            if key == "interest_areas" and isinstance(value, str):
                value = [s.strip() for s in value.split(",")]
            if key == "hours_per_day":
                value = max(0.5, min(float(value), 12))
            if key == "daily_limit":
                value = min(max(int(value), 15), 30)
            user[key] = value

    now = datetime.now().isoformat()
    with _get_db() as conn:
        _execute(conn,
            """UPDATE users SET full_name=?, tech_stack=?, interest_areas=?, hours_per_day=?,
               daily_limit=?, updated_at=? WHERE user_id=?""",
            (user["full_name"], _json_field(user["tech_stack"]),
             _json_field(user["interest_areas"]), user["hours_per_day"],
             user.get("daily_limit", 20), now, user_id))

    return user, None


def get_user_profile(user_id):
    """Get user profile data (safe fields only)."""
    user = get_user(user_id)
    if not user:
        return None
    return {
        "user_id": user["user_id"],
        "full_name": user["full_name"],
        "email": user["email"],
        "tech_stack": user.get("tech_stack", []),
        "interest_areas": user.get("interest_areas", []),
        "hours_per_day": user.get("hours_per_day", 2),
        "daily_limit": user.get("daily_limit", 20),
        "created_at": user.get("created_at"),
        "is_first_login": user.get("is_first_login", False),
    }


# ─── Learning Plans ───

def save_learning_plan(user_id, plan):
    """Save or update a user's learning plan."""
    with _get_db() as conn:
        if USE_PG:
            _execute(conn,
                """INSERT INTO learning_plans (user_id, plan) VALUES (?, ?)
                   ON CONFLICT (user_id) DO UPDATE SET plan = EXCLUDED.plan""",
                (user_id, _json_field(plan)))
        else:
            _execute(conn,
                "INSERT OR REPLACE INTO learning_plans (user_id, plan) VALUES (?, ?)",
                (user_id, _json_field(plan)))
    return plan


def get_learning_plan(user_id):
    """Get a user's learning plan."""
    with _get_db() as conn:
        row = _fetchone(conn, "SELECT plan FROM learning_plans WHERE user_id = ?", (user_id,))
        if not row:
            return None
        return _parse_json_field(row["plan"])


def delete_learning_plan(user_id):
    """Delete a user's learning plan."""
    with _get_db() as conn:
        _execute(conn, "DELETE FROM learning_plans WHERE user_id = ?", (user_id,))


# ─── Content Bookmarks ───

def save_bookmark(user_id, topic_id, dimension, position, scroll_pct=0):
    """Save bookmark position for a topic+dimension."""
    key = f"{user_id}_{topic_id}_{dimension}"
    now = datetime.now().isoformat()

    with _get_db() as conn:
        if USE_PG:
            _execute(conn,
                """INSERT INTO bookmarks (id, user_id, topic_id, dimension, position, scroll_pct, saved_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)
                   ON CONFLICT (id) DO UPDATE SET position=EXCLUDED.position, scroll_pct=EXCLUDED.scroll_pct, saved_at=EXCLUDED.saved_at""",
                (key, user_id, topic_id, dimension, position, scroll_pct, now))
        else:
            _execute(conn,
                "INSERT OR REPLACE INTO bookmarks (id, user_id, topic_id, dimension, position, scroll_pct, saved_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (key, user_id, topic_id, dimension, position, scroll_pct, now))

    return {
        "user_id": user_id, "topic_id": topic_id, "dimension": dimension,
        "position": position, "scroll_pct": scroll_pct, "saved_at": now,
    }


def get_bookmark(user_id, topic_id, dimension):
    """Get bookmark for a specific topic+dimension."""
    key = f"{user_id}_{topic_id}_{dimension}"
    with _get_db() as conn:
        return _fetchone(conn, "SELECT * FROM bookmarks WHERE id = ?", (key,))


def get_user_bookmarks(user_id):
    """Get all bookmarks for a user."""
    with _get_db() as conn:
        rows = _fetchall(conn, "SELECT * FROM bookmarks WHERE user_id = ?", (user_id,))
        return {r["id"]: r for r in rows}


# ─── Topic Assessment Results ───

def save_topic_assessment(user_id, topic_id, question_id, question_text,
                          user_answer, correct_answer, score, rating,
                          show_answer_used=False):
    """Save a topic assessment answer."""
    key = f"{user_id}_{topic_id}_{question_id}"
    now = datetime.now().isoformat()

    with _get_db() as conn:
        if USE_PG:
            _execute(conn,
                """INSERT INTO topic_assessments (id, user_id, topic_id, question_id,
                   question_text, user_answer, correct_answer, score, rating, show_answer_used, answered_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                   ON CONFLICT (id) DO UPDATE SET user_answer=EXCLUDED.user_answer, score=EXCLUDED.score,
                   rating=EXCLUDED.rating, show_answer_used=EXCLUDED.show_answer_used, answered_at=EXCLUDED.answered_at""",
                (key, user_id, topic_id, question_id, question_text, user_answer,
                 correct_answer, score, rating, int(show_answer_used), now))
        else:
            _execute(conn,
                """INSERT OR REPLACE INTO topic_assessments (id, user_id, topic_id, question_id,
                   question_text, user_answer, correct_answer, score, rating, show_answer_used, answered_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (key, user_id, topic_id, question_id, question_text, user_answer,
                 correct_answer, score, rating, int(show_answer_used), now))

    return {
        "user_id": user_id, "topic_id": topic_id, "question_id": question_id,
        "question_text": question_text, "user_answer": user_answer,
        "correct_answer": correct_answer, "score": score, "rating": rating,
        "show_answer_used": show_answer_used, "answered_at": now,
    }


def get_topic_assessment_results(user_id, topic_id):
    """Get all assessment results for a user's topic."""
    with _get_db() as conn:
        rows = _fetchall(conn,
            "SELECT * FROM topic_assessments WHERE user_id = ? AND topic_id = ? ORDER BY answered_at",
            (user_id, topic_id))
        for r in rows:
            r["show_answer_used"] = bool(r["show_answer_used"])
        return rows


def get_all_topic_assessments(user_id):
    """Get all topic assessment results for a user."""
    with _get_db() as conn:
        rows = _fetchall(conn, "SELECT * FROM topic_assessments WHERE user_id = ?", (user_id,))
        for r in rows:
            r["show_answer_used"] = bool(r["show_answer_used"])
        return rows


# ─── Review Items ───

def mark_for_review(user_id, topic_id, dimension=None):
    """Mark a topic or dimension for later review."""
    key = f"{user_id}_{topic_id}" + (f"_{dimension}" if dimension else "")
    now = datetime.now().isoformat()

    with _get_db() as conn:
        if USE_PG:
            _execute(conn,
                """INSERT INTO reviews (id, user_id, topic_id, dimension, marked_at)
                   VALUES (?, ?, ?, ?, ?)
                   ON CONFLICT (id) DO UPDATE SET marked_at=EXCLUDED.marked_at""",
                (key, user_id, topic_id, dimension, now))
        else:
            _execute(conn,
                "INSERT OR REPLACE INTO reviews (id, user_id, topic_id, dimension, marked_at) VALUES (?, ?, ?, ?, ?)",
                (key, user_id, topic_id, dimension, now))

    return {"user_id": user_id, "topic_id": topic_id, "dimension": dimension, "marked_at": now}


def unmark_for_review(user_id, topic_id, dimension=None):
    """Remove review mark."""
    key = f"{user_id}_{topic_id}" + (f"_{dimension}" if dimension else "")
    with _get_db() as conn:
        _execute(conn, "DELETE FROM reviews WHERE id = ?", (key,))


def get_review_items(user_id):
    """Get all items marked for review."""
    with _get_db() as conn:
        return _fetchall(conn, "SELECT * FROM reviews WHERE user_id = ?", (user_id,))


# ─── Enhanced Dashboard ───

def get_enhanced_dashboard_data(user_id):
    """Get comprehensive dashboard data including learning plan progress."""
    base_data = get_dashboard_data(user_id)
    if not base_data:
        return None

    plan = get_learning_plan(user_id)
    plan_progress = {"progress_pct": 0, "completed": 0, "in_progress": 0, "total": 0}
    next_topic = None
    plan_timeline = []

    if plan:
        topics = plan.get("topics", [])
        completed = sum(1 for t in topics if t["status"] == "completed")
        in_prog = sum(1 for t in topics if t["status"] in ("in_progress", "content_complete"))
        total = len(topics)
        pct = round((completed + in_prog * 0.5) / total * 100) if total > 0 else 0
        plan_progress = {
            "progress_pct": pct,
            "completed": completed,
            "in_progress": in_prog,
            "total": total,
            "expected_completion": plan.get("expected_completion"),
        }

        for t in topics:
            if t["status"] != "completed":
                next_topic = {
                    "topic_id": t["topic_id"],
                    "title": t["title"],
                    "interest_area": t["interest_area"],
                    "status": t["status"],
                }
                break

        for t in topics:
            plan_timeline.append({
                "topic_id": t["topic_id"],
                "title": t["title"],
                "interest_area": t["interest_area"],
                "status": t["status"],
                "original_end_date": t.get("original_end_date"),
                "revised_end_date": t.get("revised_end_date"),
                "assessment_rating": t.get("assessment_rating"),
            })

    per_topic_ratings = {}
    all_assessments = get_all_topic_assessments(user_id)
    for a in all_assessments:
        tid = a.get("topic_id", "")
        if tid not in per_topic_ratings:
            per_topic_ratings[tid] = []
        per_topic_ratings[tid].append(a.get("rating", 0))

    for tid in per_topic_ratings:
        ratings = per_topic_ratings[tid]
        per_topic_ratings[tid] = {
            "avg_rating": round(sum(ratings) / len(ratings), 1),
            "count": len(ratings),
        }

    all_ratings = [a.get("rating", 0) for a in all_assessments]
    overall_proficiency = round(sum(all_ratings) / len(all_ratings), 1) if all_ratings else 0

    base_data["plan_progress"] = plan_progress
    base_data["next_topic"] = next_topic
    base_data["plan_timeline"] = plan_timeline
    base_data["per_topic_ratings"] = per_topic_ratings
    base_data["overall_proficiency"] = overall_proficiency

    return base_data
