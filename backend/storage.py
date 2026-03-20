"""
JSON-based persistent storage.
All data stored in /data folder as JSON files.
Designed for easy future migration to MongoDB (same document structure).

Files:
  data/users.json           - All user accounts
  data/sessions.json        - Active learning sessions
  data/progress.json        - User progress per topic
  data/assessments.json     - Assessment answers & ratings
  data/quotas.json          - Daily question quotas
  data/learning_plans.json  - Personalized learning plans
  data/bookmarks.json       - Content bookmarks / resume positions
  data/topic_assessments.json - Topic-specific 5-question assessment results
  data/reviews.json         - Marked-for-review items
"""

import json
import os
import uuid
import hashlib
import time
from datetime import datetime, date

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def _ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def _load(filename):
    """Load a JSON file. Returns empty dict if not found or corrupt."""
    _ensure_data_dir()
    filepath = os.path.join(DATA_DIR, filename)
    if not os.path.exists(filepath):
        return {}
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, ValueError):
        return {}


def _save(filename, data):
    """Save data to a JSON file."""
    _ensure_data_dir()
    filepath = os.path.join(DATA_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)


def _hash_password(password):
    """Simple hash for password. Use bcrypt in production."""
    return hashlib.sha256(password.encode()).hexdigest()


def _gen_id():
    return str(uuid.uuid4())[:8]


# ─── Users ───

def register_user(full_name, email, tech_stack, interest_areas, hours_per_day):
    """Register a new user. Returns user dict with generated credentials."""
    users = _load("users.json")

    # Check if email already exists
    for uid, user in users.items():
        if user["email"].lower() == email.lower():
            return None, "Email already registered"

    user_id = _gen_id()
    default_password = "welcome@123"

    user = {
        "user_id": user_id,
        "email": email.lower(),
        "password_hash": _hash_password(default_password),
        "full_name": full_name,
        "tech_stack": tech_stack if isinstance(tech_stack, list) else [s.strip() for s in tech_stack.split(",")],
        "interest_areas": interest_areas if isinstance(interest_areas, list) else [s.strip() for s in interest_areas.split(",")],
        "hours_per_day": float(hours_per_day),
        "is_first_login": True,
        "created_at": datetime.now().isoformat(),
        "last_active_at": datetime.now().isoformat(),
    }

    users[user_id] = user
    _save("users.json", users)

    return user, None


def login_user(email, password):
    """Authenticate user. Returns user dict or None."""
    users = _load("users.json")

    for uid, user in users.items():
        if user["email"].lower() == email.lower():
            if user["password_hash"] == _hash_password(password):
                user["last_active_at"] = datetime.now().isoformat()
                _save("users.json", users)
                return user, None
            else:
                return None, "Invalid password"

    return None, "User not found"


def change_password(user_id, new_password):
    """Change user's password and clear first_login flag."""
    users = _load("users.json")
    if user_id not in users:
        return False, "User not found"

    users[user_id]["password_hash"] = _hash_password(new_password)
    users[user_id]["is_first_login"] = False
    _save("users.json", users)
    return True, None


def get_user(user_id):
    """Get user by ID."""
    users = _load("users.json")
    return users.get(user_id)


def update_user_activity(user_id):
    """Update last_active_at timestamp."""
    users = _load("users.json")
    if user_id in users:
        users[user_id]["last_active_at"] = datetime.now().isoformat()
        _save("users.json", users)


# ─── Learning Sessions ───

def create_session(user_id, job_title, questions, role_name):
    """Create a new interview/learning session."""
    sessions = _load("sessions.json")

    session_id = _gen_id()
    session = {
        "session_id": session_id,
        "user_id": user_id,
        "job_title": job_title,
        "role_name": role_name,
        "questions": questions,
        "answers": [],
        "start_time": datetime.now().isoformat(),
        "end_time": None,
        "scorecard": None,
        "current_question": 0,
        "status": "in_progress",
    }

    sessions[session_id] = session
    _save("sessions.json", sessions)
    return session


def get_session(session_id):
    """Get session by ID."""
    sessions = _load("sessions.json")
    return sessions.get(session_id)


def update_session(session_id, updates):
    """Update session fields."""
    sessions = _load("sessions.json")
    if session_id not in sessions:
        return None
    sessions[session_id].update(updates)
    _save("sessions.json", sessions)
    return sessions[session_id]


def add_answer(session_id, answer):
    """Add an answer to a session."""
    sessions = _load("sessions.json")
    if session_id not in sessions:
        return None
    sessions[session_id]["answers"].append(answer)
    sessions[session_id]["current_question"] = len(sessions[session_id]["answers"])
    _save("sessions.json", sessions)
    return sessions[session_id]


def finish_session(session_id, scorecard):
    """Mark session as completed with scorecard."""
    sessions = _load("sessions.json")
    if session_id not in sessions:
        return None
    sessions[session_id]["end_time"] = datetime.now().isoformat()
    sessions[session_id]["scorecard"] = scorecard
    sessions[session_id]["status"] = "completed"
    _save("sessions.json", sessions)
    return sessions[session_id]


def get_user_sessions(user_id):
    """Get all sessions for a user (for history/resume)."""
    sessions = _load("sessions.json")
    return [s for s in sessions.values() if s.get("user_id") == user_id]


def get_resumable_session(user_id):
    """Get the last in-progress session for resume."""
    user_sessions = get_user_sessions(user_id)
    in_progress = [s for s in user_sessions if s["status"] == "in_progress"]
    if in_progress:
        return sorted(in_progress, key=lambda s: s["start_time"], reverse=True)[0]
    return None


# ─── Progress Tracking ───

def update_progress(user_id, topic, dimension, status, position=None, time_spent=0):
    """Update user's progress on a topic."""
    progress = _load("progress.json")

    key = f"{user_id}_{topic}_{dimension}"
    entry = progress.get(key, {
        "user_id": user_id,
        "topic": topic,
        "dimension": dimension,
        "status": "not_started",
        "last_position": None,
        "time_spent_hours": 0,
        "target_date": None,
        "actual_completed": None,
        "created_at": datetime.now().isoformat(),
    })

    entry["status"] = status
    if position is not None:
        entry["last_position"] = position
    entry["time_spent_hours"] += time_spent
    entry["updated_at"] = datetime.now().isoformat()

    if status == "completed":
        entry["actual_completed"] = datetime.now().isoformat()

    progress[key] = entry
    _save("progress.json", progress)
    return entry


def get_user_progress(user_id):
    """Get all progress entries for a user."""
    progress = _load("progress.json")
    return {k: v for k, v in progress.items() if v.get("user_id") == user_id}


def get_dashboard_data(user_id):
    """Get dashboard summary for a user."""
    user = get_user(user_id)
    if not user:
        return None

    sessions = get_user_sessions(user_id)
    completed = [s for s in sessions if s["status"] == "completed"]
    in_progress = get_resumable_session(user_id)

    # Calculate stats
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

    # Average per topic
    for topic in topic_scores:
        topic_scores[topic] = round(sum(topic_scores[topic]) / len(topic_scores[topic]))

    # Quota
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
    quotas = _load("quotas.json")
    today = date.today().isoformat()
    key = f"{user_id}_{today}"

    if key not in quotas:
        # Check user's configured limit
        user = get_user(user_id)
        daily_limit = 20  # default
        if user:
            daily_limit = user.get("daily_limit", 20)

        quotas[key] = {
            "user_id": user_id,
            "date": today,
            "questions_attempted": 0,
            "daily_limit": min(max(daily_limit, 15), 30),  # clamp 15-30
            "limit_reached_at": None,
        }
        _save("quotas.json", quotas)

    return quotas[key]


def increment_quota(user_id):
    """Increment today's question count. Returns (allowed, quota)."""
    quotas = _load("quotas.json")
    today = date.today().isoformat()
    key = f"{user_id}_{today}"

    quota = get_daily_quota(user_id)  # ensures it exists
    quotas = _load("quotas.json")  # reload after get_daily_quota may have saved

    if quota["questions_attempted"] >= quota["daily_limit"]:
        return False, quota

    quotas[key]["questions_attempted"] += 1

    if quotas[key]["questions_attempted"] >= quotas[key]["daily_limit"]:
        quotas[key]["limit_reached_at"] = datetime.now().isoformat()

    _save("quotas.json", quotas)
    return True, quotas[key]


def configure_quota(user_id, daily_limit):
    """Set user's preferred daily limit (15-30)."""
    daily_limit = min(max(int(daily_limit), 15), 30)
    users = _load("users.json")
    if user_id in users:
        users[user_id]["daily_limit"] = daily_limit
        _save("users.json", users)
    return daily_limit


# ─── Assessment Results Storage ───

def save_assessment(user_id, session_id, question_id, topic, question_text,
                    user_answer, correct_answer, score, rating, voice_url=None):
    """Save individual assessment result."""
    assessments = _load("assessments.json")

    assessment_id = _gen_id()
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
        "answered_at": datetime.now().isoformat(),
    }

    assessments[assessment_id] = entry
    _save("assessments.json", assessments)
    return entry


def get_user_assessments(user_id, topic=None):
    """Get all assessments for a user, optionally filtered by topic."""
    assessments = _load("assessments.json")
    results = [a for a in assessments.values() if a.get("user_id") == user_id]
    if topic:
        results = [a for a in results if a.get("topic") == topic]
    return sorted(results, key=lambda a: a.get("answered_at", ""), reverse=True)


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
    """Update user profile fields (name, tech_stack, interests, hours, daily_limit)."""
    users = _load("users.json")
    if user_id not in users:
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
            users[user_id][key] = value

    users[user_id]["updated_at"] = datetime.now().isoformat()
    _save("users.json", users)
    return users[user_id], None


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
    plans = _load("learning_plans.json")
    plans[user_id] = plan
    _save("learning_plans.json", plans)
    return plan


def get_learning_plan(user_id):
    """Get a user's learning plan."""
    plans = _load("learning_plans.json")
    return plans.get(user_id)


def delete_learning_plan(user_id):
    """Delete a user's learning plan (for regeneration)."""
    plans = _load("learning_plans.json")
    if user_id in plans:
        del plans[user_id]
        _save("learning_plans.json", plans)


# ─── Content Bookmarks ───

def save_bookmark(user_id, topic_id, dimension, position, scroll_pct=0):
    """Save bookmark position for a topic+dimension."""
    bookmarks = _load("bookmarks.json")
    key = f"{user_id}_{topic_id}_{dimension}"
    bookmarks[key] = {
        "user_id": user_id,
        "topic_id": topic_id,
        "dimension": dimension,
        "position": position,
        "scroll_pct": scroll_pct,
        "saved_at": datetime.now().isoformat(),
    }
    _save("bookmarks.json", bookmarks)
    return bookmarks[key]


def get_bookmark(user_id, topic_id, dimension):
    """Get bookmark for a specific topic+dimension."""
    bookmarks = _load("bookmarks.json")
    key = f"{user_id}_{topic_id}_{dimension}"
    return bookmarks.get(key)


def get_user_bookmarks(user_id):
    """Get all bookmarks for a user."""
    bookmarks = _load("bookmarks.json")
    return {k: v for k, v in bookmarks.items() if v.get("user_id") == user_id}


# ─── Topic Assessment Results ───

def save_topic_assessment(user_id, topic_id, question_id, question_text,
                          user_answer, correct_answer, score, rating,
                          show_answer_used=False):
    """Save a topic assessment answer."""
    assessments = _load("topic_assessments.json")
    key = f"{user_id}_{topic_id}_{question_id}"
    assessments[key] = {
        "user_id": user_id,
        "topic_id": topic_id,
        "question_id": question_id,
        "question_text": question_text,
        "user_answer": user_answer,
        "correct_answer": correct_answer,
        "score": score,
        "rating": rating,
        "show_answer_used": show_answer_used,
        "answered_at": datetime.now().isoformat(),
    }
    _save("topic_assessments.json", assessments)
    return assessments[key]


def get_topic_assessment_results(user_id, topic_id):
    """Get all assessment results for a user's topic."""
    assessments = _load("topic_assessments.json")
    results = [v for v in assessments.values()
               if v.get("user_id") == user_id and v.get("topic_id") == topic_id]
    return sorted(results, key=lambda a: a.get("answered_at", ""))


def get_all_topic_assessments(user_id):
    """Get all topic assessment results for a user."""
    assessments = _load("topic_assessments.json")
    results = [v for v in assessments.values() if v.get("user_id") == user_id]
    return results


# ─── Review Items ───

def mark_for_review(user_id, topic_id, dimension=None):
    """Mark a topic or dimension for later review."""
    reviews = _load("reviews.json")
    key = f"{user_id}_{topic_id}" + (f"_{dimension}" if dimension else "")
    reviews[key] = {
        "user_id": user_id,
        "topic_id": topic_id,
        "dimension": dimension,
        "marked_at": datetime.now().isoformat(),
    }
    _save("reviews.json", reviews)
    return reviews[key]


def unmark_for_review(user_id, topic_id, dimension=None):
    """Remove review mark."""
    reviews = _load("reviews.json")
    key = f"{user_id}_{topic_id}" + (f"_{dimension}" if dimension else "")
    if key in reviews:
        del reviews[key]
        _save("reviews.json", reviews)


def get_review_items(user_id):
    """Get all items marked for review."""
    reviews = _load("reviews.json")
    return [v for v in reviews.values() if v.get("user_id") == user_id]


# ─── Enhanced Dashboard ───

def get_enhanced_dashboard_data(user_id):
    """Get comprehensive dashboard data including learning plan progress."""
    base_data = get_dashboard_data(user_id)
    if not base_data:
        return None

    # Add learning plan progress
    plan = get_learning_plan(user_id)
    plan_progress = {"progress_pct": 0, "completed": 0, "in_progress": 0, "total": 0}
    next_topic = None
    plan_timeline = []

    if plan:
        topics = plan.get("topics", [])
        completed = sum(1 for t in topics if t["status"] == "completed")
        in_progress = sum(1 for t in topics if t["status"] in ("in_progress", "content_complete"))
        total = len(topics)
        pct = round((completed + in_progress * 0.5) / total * 100) if total > 0 else 0
        plan_progress = {
            "progress_pct": pct,
            "completed": completed,
            "in_progress": in_progress,
            "total": total,
            "expected_completion": plan.get("expected_completion"),
        }

        # Find next topic
        for t in topics:
            if t["status"] != "completed":
                next_topic = {
                    "topic_id": t["topic_id"],
                    "title": t["title"],
                    "interest_area": t["interest_area"],
                    "status": t["status"],
                }
                break

        # Timeline summary
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

    # Per-topic ratings from assessments
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

    # Overall proficiency
    all_ratings = [a.get("rating", 0) for a in all_assessments]
    overall_proficiency = round(sum(all_ratings) / len(all_ratings), 1) if all_ratings else 0

    base_data["plan_progress"] = plan_progress
    base_data["next_topic"] = next_topic
    base_data["plan_timeline"] = plan_timeline
    base_data["per_topic_ratings"] = per_topic_ratings
    base_data["overall_proficiency"] = overall_proficiency

    return base_data
