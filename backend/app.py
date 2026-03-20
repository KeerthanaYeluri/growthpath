import json
import os
import jwt
import time
from functools import wraps
from flask import Flask, jsonify, request, g, send_from_directory
from flask_cors import CORS
from scorer import score_answer, generate_scorecard
from transcriber import transcribe_whisper, transcribe_vosk
from question_bank import get_questions_for_role, get_role_for_interests, ROLE_QUESTIONS
from topic_catalog import TECH_STACK_OPTIONS, INTEREST_AREAS_OPTIONS, get_topic_by_id
from topic_questions import get_topic_questions
import storage
import learning_engine
import scheduler

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")

app = Flask(__name__, static_folder=FRONTEND_DIR)
CORS(app)

JWT_SECRET = os.environ.get("JWT_SECRET", "growthpath-secret-key-change-in-production")
JWT_EXPIRY = 86400  # 24 hours

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
CONTENT_DIR = os.path.join(DATA_DIR, "content")
RECORDINGS_DIR = os.path.join(DATA_DIR, "recordings")
os.makedirs(RECORDINGS_DIR, exist_ok=True)


# ─── Auth Helpers ───

def create_token(user_id, email):
    payload = {"user_id": user_id, "email": email, "exp": int(time.time()) + JWT_EXPIRY}
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


def auth_required(f):
    """Decorator to require JWT auth. Sets g.user_id."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        if not token:
            return jsonify({"error": "Token required"}), 401
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            g.user_id = payload["user_id"]
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        return f(*args, **kwargs)
    return decorated


def auth_optional(f):
    """Decorator for optional auth. Sets g.user_id or None."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        g.user_id = None
        if token:
            try:
                payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
                g.user_id = payload["user_id"]
            except Exception:
                pass
        return f(*args, **kwargs)
    return decorated


# ─── Auth Endpoints ───

@app.route("/api/auth/register", methods=["POST"])
def register():
    data = request.json
    full_name = data.get("full_name", "").strip()
    email = data.get("email", "").strip()
    tech_stack = data.get("tech_stack", [])
    interest_areas = data.get("interest_areas", [])
    hours_per_day = data.get("hours_per_day", 2)

    if not full_name or not email:
        return jsonify({"error": "Name and email are required"}), 400

    user, error = storage.register_user(full_name, email, tech_stack, interest_areas, hours_per_day)
    if error:
        return jsonify({"error": error}), 409

    # Auto-generate learning plan on registration
    plan, plan_error = learning_engine.generate_learning_plan(user["user_id"])

    token = create_token(user["user_id"], user["email"])
    return jsonify({
        "user_id": user["user_id"],
        "email": user["email"],
        "full_name": user["full_name"],
        "password": "welcome@123",
        "is_first_login": True,
        "token": token,
        "has_plan": plan is not None,
        "message": "Registration successful. Default password: welcome@123",
    })


@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email", "").strip()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    user, error = storage.login_user(email, password)
    if error:
        return jsonify({"error": error}), 401

    token = create_token(user["user_id"], user["email"])
    return jsonify({
        "user_id": user["user_id"],
        "email": user["email"],
        "full_name": user["full_name"],
        "is_first_login": user.get("is_first_login", False),
        "token": token,
    })


@app.route("/api/auth/password", methods=["PUT"])
@auth_required
def change_password():
    data = request.json
    new_password = data.get("new_password", "")
    if len(new_password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    ok, error = storage.change_password(g.user_id, new_password)
    if not ok:
        return jsonify({"error": error}), 400
    return jsonify({"message": "Password changed successfully"})


# ─── Profile (Sprint 2) ───

@app.route("/api/auth/profile", methods=["GET"])
@auth_required
def get_profile():
    profile = storage.get_user_profile(g.user_id)
    if not profile:
        return jsonify({"error": "User not found"}), 404
    return jsonify(profile)


@app.route("/api/auth/profile", methods=["PUT"])
@auth_required
def update_profile():
    data = request.json
    user, error = storage.update_user_profile(g.user_id, data)
    if error:
        return jsonify({"error": error}), 400

    # Regenerate learning plan if interests changed
    if "interest_areas" in data:
        learning_engine.generate_learning_plan(g.user_id)

    profile = storage.get_user_profile(g.user_id)
    return jsonify(profile)


# ─── Config Lists (Sprint 1) ───

@app.route("/api/config/tech-stacks", methods=["GET"])
def get_tech_stacks():
    return jsonify(TECH_STACK_OPTIONS)


@app.route("/api/config/interest-areas", methods=["GET"])
def get_interest_areas():
    return jsonify(INTEREST_AREAS_OPTIONS)


# ─── Dashboard ───

@app.route("/api/dashboard", methods=["GET"])
@auth_required
def dashboard():
    data = storage.get_enhanced_dashboard_data(g.user_id)
    if not data:
        return jsonify({"error": "User not found"}), 404
    return jsonify(data)


# ─── Interview Role Detection ───

@app.route("/api/interview/detect-role", methods=["GET"])
@auth_required
def detect_interview_role():
    """Detect best interview role from user's profile interests."""
    user = storage.get_user(g.user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    interests = user.get("interest_areas", [])
    role_key = get_role_for_interests(interests)
    role_data = ROLE_QUESTIONS.get(role_key, ROLE_QUESTIONS.get("default"))

    return jsonify({
        "role_key": role_key,
        "role_name": role_data["name"],
        "interests": interests,
        "total_questions": 30,
    })


# ─── Session & Questions ───

@app.route("/api/session/start", methods=["POST"])
@auth_optional
def start_session():
    import random
    data = request.json
    name = data.get("candidate_name", "").strip()
    job_title = data.get("job_title", "").strip()

    if not name or not job_title:
        return jsonify({"error": "Name and job title are required"}), 400

    # Generate role-based questions
    questions, role_name = get_questions_for_role(job_title)

    # Shuffle questions within difficulty groups to avoid repetition across sessions
    # Keep Q1 (intro) fixed, shuffle the rest
    if len(questions) > 1:
        intro = questions[0]
        rest = questions[1:]
        random.shuffle(rest)
        questions = [intro] + rest

    # If authenticated, try to avoid recently asked questions
    user_id = g.user_id or "anonymous"
    if user_id != "anonymous":
        recent_sessions = storage.get_user_sessions(user_id)
        recent_qids = set()
        # Collect question IDs from last 3 sessions
        for s in sorted(recent_sessions, key=lambda x: x.get("start_time", ""), reverse=True)[:3]:
            for q in s.get("questions", []):
                recent_qids.add(q.get("question", ""))

        # Prefer questions not recently asked (keep intro)
        if recent_qids and len(questions) > 1:
            intro = questions[0]
            unseen = [q for q in questions[1:] if q.get("question", "") not in recent_qids]
            seen = [q for q in questions[1:] if q.get("question", "") in recent_qids]
            # Put unseen first, seen at the end
            reordered = unseen + seen
            # Re-assign IDs
            questions = [intro]
            for i, q in enumerate(reordered):
                q_copy = dict(q)
                q_copy["id"] = i + 2
                questions.append(q_copy)

    session = storage.create_session(user_id, job_title, questions, role_name)

    print(f"[Session] {name} | Role: {role_name} | {len(questions)} Qs | User: {user_id}")

    return jsonify({
        "session_id": session["session_id"],
        "candidate_name": name,
        "job_title": job_title,
        "role_name": role_name,
        "total_questions": len(questions),
    })


@app.route("/api/questions", methods=["GET"])
def get_questions():
    session_id = request.args.get("session_id", "")
    session = storage.get_session(session_id) if session_id else None

    if session:
        questions = session["questions"]
    else:
        questions, _ = get_questions_for_role("general")

    safe_questions = [{
        "id": q["id"], "topic": q["topic"],
        "difficulty": q["difficulty"], "question": q["question"],
    } for q in questions]
    return jsonify(safe_questions)


@app.route("/api/question/<int:question_id>/answer", methods=["GET"])
def get_model_answer(question_id):
    session_id = request.args.get("session_id", "")
    session = storage.get_session(session_id) if session_id else None
    questions = session["questions"] if session else []

    question = next((q for q in questions if q["id"] == question_id), None)
    if not question:
        return jsonify({"error": "Question not found"}), 404
    return jsonify({
        "question_id": question_id,
        "model_answer": question.get("model_answer", "No model answer available."),
    })


@app.route("/api/answer/submit", methods=["POST"])
@auth_optional
def submit_answer():
    data = request.json
    session_id = data.get("session_id")
    question_id = data.get("question_id")
    transcript = data.get("transcript", "")

    session = storage.get_session(session_id)
    if not session:
        return jsonify({"error": "Invalid session"}), 404

    questions = session["questions"]
    question = next((q for q in questions if q["id"] == question_id), None)
    if not question:
        return jsonify({"error": "Invalid question"}), 404

    # Check daily quota if authenticated
    user_id = g.user_id or session.get("user_id", "anonymous")
    if user_id != "anonymous":
        allowed, quota = storage.increment_quota(user_id)
        if not allowed:
            return jsonify({
                "error": "Daily question limit reached. Come back tomorrow!",
                "quota": quota,
            }), 429

    score = score_answer(transcript, question)

    # Calculate rating (1-5)
    total = score["total_score"]
    rating = 5 if total >= 81 else 4 if total >= 61 else 3 if total >= 41 else 2 if total >= 21 else 1

    answer_record = {
        "question_id": question_id,
        "topic": question["topic"],
        "transcript": transcript,
        "score": score,
        "rating": rating,
    }

    # Save to session
    storage.add_answer(session_id, answer_record)

    # Save to assessments (persistent)
    if user_id != "anonymous":
        storage.save_assessment(
            user_id=user_id,
            session_id=session_id,
            question_id=question_id,
            topic=question["topic"],
            question_text=question["question"],
            user_answer=transcript,
            correct_answer=question.get("model_answer", ""),
            score=score,
            rating=rating,
        )

    return jsonify({
        "question_id": question_id,
        "score": score,
        "rating": rating,
    })


@app.route("/api/session/finish", methods=["POST"])
@auth_optional
def finish_session_endpoint():
    data = request.json
    session_id = data.get("session_id")
    time_taken = data.get("time_taken", "N/A")

    session = storage.get_session(session_id)
    if not session:
        return jsonify({"error": "Invalid session"}), 404

    questions = session["questions"]
    answers = session["answers"]

    scorecard = generate_scorecard(answers, questions)
    scorecard["time_taken"] = time_taken
    scorecard["candidate_name"] = data.get("candidate_name", "")
    scorecard["job_title"] = session["job_title"]
    scorecard["role_name"] = session["role_name"]

    # Save scorecard
    storage.finish_session(session_id, scorecard)

    # Build per-question review
    question_review = []
    for ans in answers:
        q = next((q for q in questions if q["id"] == ans["question_id"]), None)
        question_review.append({
            "question_id": ans["question_id"],
            "topic": ans["topic"],
            "question_text": q["question"] if q else "",
            "transcript": ans["transcript"],
            "score": ans["score"],
            "rating": ans.get("rating", 0),
            "model_answer": q.get("model_answer", "") if q else "",
        })

    return jsonify({
        "scorecard": scorecard,
        "question_review": question_review,
    })


# ─── Resume & History ───

@app.route("/api/session/resume", methods=["GET"])
@auth_required
def resume_session():
    session = storage.get_resumable_session(g.user_id)
    if not session:
        return jsonify({"has_session": False})

    return jsonify({
        "has_session": True,
        "session_id": session["session_id"],
        "job_title": session["job_title"],
        "role_name": session["role_name"],
        "current_question": session["current_question"],
        "total_questions": len(session["questions"]),
        "start_time": session["start_time"],
    })


@app.route("/api/session/history", methods=["GET"])
@auth_required
def session_history():
    sessions = storage.get_user_sessions(g.user_id)
    completed = [s for s in sessions if s["status"] == "completed"]

    history = []
    for s in sorted(completed, key=lambda x: x.get("end_time", ""), reverse=True):
        sc = s.get("scorecard", {})
        history.append({
            "session_id": s["session_id"],
            "role_name": s["role_name"],
            "job_title": s["job_title"],
            "overall_score": sc.get("overall_score", 0),
            "total_questions": sc.get("total_questions", 0),
            "time_taken": sc.get("time_taken", "N/A"),
            "date": s.get("end_time", s.get("start_time", "")),
        })

    return jsonify(history)


# ─── Quota ───

@app.route("/api/quota", methods=["GET"])
@auth_required
def get_quota():
    quota = storage.get_daily_quota(g.user_id)
    return jsonify(quota)


@app.route("/api/quota/configure", methods=["PUT"])
@auth_required
def configure_quota():
    data = request.json
    limit = data.get("daily_limit", 20)
    new_limit = storage.configure_quota(g.user_id, limit)
    return jsonify({"daily_limit": new_limit})


# ─── Ratings ───

@app.route("/api/ratings", methods=["GET"])
@auth_required
def get_ratings():
    summary = storage.get_ratings_summary(g.user_id)
    return jsonify(summary)


# ─── Learning Plan (Sprint 3) ───

@app.route("/api/learning/generate-plan", methods=["POST"])
@auth_required
def generate_plan():
    plan, error = learning_engine.generate_learning_plan(g.user_id)
    if error:
        return jsonify({"error": error}), 400
    return jsonify(plan)


@app.route("/api/learning/plan", methods=["GET"])
@auth_required
def get_plan():
    plan = storage.get_learning_plan(g.user_id)
    if not plan:
        return jsonify({"error": "No learning plan found. Generate one first."}), 404
    return jsonify(plan)


# ─── Content (Sprint 4) ───

@app.route("/api/learning/topic/<topic_id>/content", methods=["GET"])
@auth_required
def get_topic_content(topic_id):
    dimension = request.args.get("dimension", None)

    # Load content JSON file
    content_path = os.path.join(CONTENT_DIR, f"{topic_id}.json")
    if not os.path.exists(content_path):
        return jsonify({"error": "Content not found for this topic"}), 404

    with open(content_path, "r", encoding="utf-8") as f:
        content_data = json.load(f)

    if dimension:
        dim_content = content_data.get("dimensions", {}).get(dimension)
        if not dim_content:
            return jsonify({"error": f"Dimension '{dimension}' not found"}), 404
        # Include bookmark if exists
        bookmark = storage.get_bookmark(g.user_id, topic_id, dimension)
        return jsonify({
            "topic_id": topic_id,
            "dimension": dimension,
            "title": dim_content.get("title", ""),
            "content": dim_content.get("content", ""),
            "bookmark": bookmark,
        })

    # Return all dimensions (metadata only, not full content)
    dimensions_meta = {}
    for dim_key, dim_val in content_data.get("dimensions", {}).items():
        bookmark = storage.get_bookmark(g.user_id, topic_id, dim_key)
        progress_entry = storage.get_user_progress(g.user_id)
        dim_progress_key = f"{g.user_id}_{topic_id}_{dim_key}"
        dim_status = progress_entry.get(dim_progress_key, {}).get("status", "not_started")
        dimensions_meta[dim_key] = {
            "title": dim_val.get("title", ""),
            "has_bookmark": bookmark is not None,
            "status": dim_status,
        }

    topic_info = get_topic_by_id(topic_id)
    return jsonify({
        "topic_id": topic_id,
        "title": content_data.get("title", topic_info["title"] if topic_info else topic_id),
        "dimensions": dimensions_meta,
    })


@app.route("/api/learning/topic/<topic_id>/bookmark", methods=["POST"])
@auth_required
def save_content_bookmark(topic_id):
    data = request.json
    dimension = data.get("dimension", "")
    position = data.get("position", 0)
    scroll_pct = data.get("scroll_pct", 0)

    bookmark = storage.save_bookmark(g.user_id, topic_id, dimension, position, scroll_pct)
    return jsonify(bookmark)


@app.route("/api/learning/topic/<topic_id>/dimension/<dimension>/complete", methods=["POST"])
@auth_required
def complete_dimension(topic_id, dimension):
    # Update progress
    storage.update_progress(g.user_id, topic_id, dimension, "completed")
    # Update learning plan
    plan = learning_engine.mark_dimension_complete(g.user_id, topic_id, dimension)
    # Trigger schedule recalculation
    scheduler.recalculate_schedule(g.user_id)
    return jsonify({"message": "Dimension marked complete", "topic_id": topic_id, "dimension": dimension})


@app.route("/api/learning/topic/<topic_id>/review", methods=["POST"])
@auth_required
def mark_topic_review(topic_id):
    data = request.json or {}
    dimension = data.get("dimension", None)
    storage.mark_for_review(g.user_id, topic_id, dimension)
    return jsonify({"message": "Marked for review"})


@app.route("/api/learning/topic/<topic_id>/review", methods=["DELETE"])
@auth_required
def unmark_topic_review(topic_id):
    data = request.json or {}
    dimension = data.get("dimension", None)
    storage.unmark_for_review(g.user_id, topic_id, dimension)
    return jsonify({"message": "Removed from review"})


# ─── Topic Assessment (Sprint 5) ───

@app.route("/api/assessment/topic/<topic_id>/questions", methods=["GET"])
@auth_required
def get_assessment_questions(topic_id):
    # Check quota
    quota = storage.get_daily_quota(g.user_id)
    if quota["questions_attempted"] >= quota["daily_limit"]:
        return jsonify({
            "error": "Daily question limit reached. Come back tomorrow!",
            "quota": quota,
        }), 429

    questions = get_topic_questions(topic_id)
    if not questions:
        return jsonify({"error": "No assessment questions for this topic"}), 404

    # Return questions without answers
    safe_questions = [{
        "id": q["id"],
        "question": q["question"],
    } for q in questions]

    return jsonify({
        "topic_id": topic_id,
        "questions": safe_questions,
        "total": len(safe_questions),
    })


@app.route("/api/assessment/topic/<topic_id>/submit", methods=["POST"])
@auth_required
def submit_topic_assessment(topic_id):
    data = request.json
    question_id = data.get("question_id", "")
    user_answer = data.get("answer", "")
    show_answer_used = data.get("show_answer_used", False)

    # Find the question
    questions = get_topic_questions(topic_id)
    question = next((q for q in questions if q["id"] == question_id), None)
    if not question:
        return jsonify({"error": "Question not found"}), 404

    # Check and increment quota
    allowed, quota = storage.increment_quota(g.user_id)
    if not allowed:
        return jsonify({
            "error": "Daily question limit reached. Come back tomorrow!",
            "quota": quota,
        }), 429

    # Score the answer
    score = score_answer(user_answer, question)

    # Apply 50% penalty if Show Answer was used
    if show_answer_used:
        score["total_score"] = max(0, score["total_score"] // 2)
        score["penalty_applied"] = "50% for viewing answer"

    total = score["total_score"]
    rating = 5 if total >= 81 else 4 if total >= 61 else 3 if total >= 41 else 2 if total >= 21 else 1

    # Save assessment
    storage.save_topic_assessment(
        user_id=g.user_id,
        topic_id=topic_id,
        question_id=question_id,
        question_text=question["question"],
        user_answer=user_answer,
        correct_answer=question.get("model_answer", ""),
        score=score,
        rating=rating,
        show_answer_used=show_answer_used,
    )

    return jsonify({
        "question_id": question_id,
        "score": score,
        "rating": rating,
        "correct_answer": question.get("model_answer", ""),
    })


@app.route("/api/assessment/topic/<topic_id>/show-answer", methods=["POST"])
@auth_required
def show_topic_answer(topic_id):
    """Get the model answer for a topic assessment question (applies 50% penalty)."""
    data = request.json
    question_id = data.get("question_id", "")

    questions = get_topic_questions(topic_id)
    question = next((q for q in questions if q["id"] == question_id), None)
    if not question:
        return jsonify({"error": "Question not found"}), 404

    return jsonify({
        "question_id": question_id,
        "model_answer": question.get("model_answer", ""),
        "penalty_warning": "Using Show Answer applies a 50% score penalty.",
    })


@app.route("/api/assessment/topic/<topic_id>/complete", methods=["POST"])
@auth_required
def complete_topic_assessment(topic_id):
    """Mark topic assessment as complete and calculate final topic rating."""
    results = storage.get_topic_assessment_results(g.user_id, topic_id)
    if not results:
        return jsonify({"error": "No assessment results found"}), 404

    avg_score = sum(r.get("score", {}).get("total_score", 0) if isinstance(r.get("score"), dict) else 0 for r in results) / len(results)
    avg_rating = sum(r.get("rating", 0) for r in results) / len(results)
    final_rating = round(avg_rating)

    # Mark topic as completed in learning plan
    learning_engine.mark_topic_assessed(g.user_id, topic_id, round(avg_score), final_rating)
    # Recalculate schedule
    scheduler.recalculate_schedule(g.user_id)

    return jsonify({
        "topic_id": topic_id,
        "average_score": round(avg_score),
        "average_rating": round(avg_rating, 1),
        "final_rating": final_rating,
        "questions_answered": len(results),
    })


@app.route("/api/assessment/topic/<topic_id>/results", methods=["GET"])
@auth_required
def get_assessment_results(topic_id):
    results = storage.get_topic_assessment_results(g.user_id, topic_id)
    return jsonify({
        "topic_id": topic_id,
        "results": results,
        "total": len(results),
    })


# ─── Schedule (Sprint 6) ───

@app.route("/api/progress/schedule", methods=["GET"])
@auth_required
def get_schedule():
    statuses = scheduler.get_schedule_status(g.user_id)
    plan = storage.get_learning_plan(g.user_id)
    return jsonify({
        "schedule": statuses,
        "expected_completion": plan.get("expected_completion") if plan else None,
    })


# ─── Review (Sprint 7) ───

@app.route("/api/review/items", methods=["GET"])
@auth_required
def get_review_items():
    items = storage.get_review_items(g.user_id)
    # Enrich with topic info
    enriched = []
    for item in items:
        topic_info = get_topic_by_id(item["topic_id"])
        enriched.append({
            **item,
            "topic_title": topic_info["title"] if topic_info else item["topic_id"],
            "interest_area": topic_info["interest_area"] if topic_info else "",
        })
    return jsonify(enriched)


@app.route("/api/review/topic/<topic_id>/assessment", methods=["GET"])
@auth_required
def review_topic_assessment(topic_id):
    """View previous assessment results (read-only review mode)."""
    results = storage.get_topic_assessment_results(g.user_id, topic_id)
    return jsonify({
        "topic_id": topic_id,
        "results": results,
        "total": len(results),
        "review_mode": True,
    })


# ─── Transcription ───

@app.route("/api/transcribe", methods=["POST"])
def transcribe():
    if "audio" not in request.files:
        return jsonify({"error": "No audio file"}), 400
    engine = request.form.get("engine", "whisper")
    audio_bytes = request.files["audio"].read()
    if len(audio_bytes) < 100:
        return jsonify({"transcript": "", "engine": engine})
    try:
        transcript = transcribe_vosk(audio_bytes) if engine == "vosk" else transcribe_whisper(audio_bytes)
        return jsonify({"transcript": transcript, "engine": engine})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/transcribe/stream", methods=["POST"])
def transcribe_stream():
    if "audio" not in request.files:
        return jsonify({"error": "No audio"}), 400
    engine = request.form.get("engine", "whisper")
    audio_bytes = request.files["audio"].read()
    is_final = request.form.get("is_final", "false") == "true"
    if len(audio_bytes) < 100:
        return jsonify({"transcript": "", "is_final": is_final})
    try:
        transcript = transcribe_vosk(audio_bytes) if engine == "vosk" else transcribe_whisper(audio_bytes)
        return jsonify({"transcript": transcript, "is_final": is_final, "engine": engine})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ─── Recordings ───

@app.route("/api/recording/upload", methods=["POST"])
@auth_required
def upload_recording():
    """Upload a voice recording for a session question."""
    if "audio" not in request.files:
        return jsonify({"error": "No audio file"}), 400

    session_id = request.form.get("session_id", "")
    question_id = request.form.get("question_id", "")
    if not session_id or not question_id:
        return jsonify({"error": "session_id and question_id required"}), 400

    audio_file = request.files["audio"]
    # Save as: recordings/{user_id}_{session_id}_{question_id}.webm
    filename = f"{g.user_id}_{session_id}_{question_id}.webm"
    filepath = os.path.join(RECORDINGS_DIR, filename)
    audio_file.save(filepath)

    return jsonify({
        "filename": filename,
        "url": f"/api/recording/{filename}",
    })


@app.route("/api/recording/<filename>", methods=["GET"])
def serve_recording(filename):
    """Serve a recording file."""
    return send_from_directory(RECORDINGS_DIR, filename)


@app.route("/api/recording/list/<session_id>", methods=["GET"])
@auth_required
def list_recordings(session_id):
    """List all recordings for a session."""
    prefix = f"{g.user_id}_{session_id}_"
    recordings = {}
    if os.path.exists(RECORDINGS_DIR):
        for f in os.listdir(RECORDINGS_DIR):
            if f.startswith(prefix) and f.endswith(".webm"):
                qid = f.replace(prefix, "").replace(".webm", "")
                recordings[qid] = f"/api/recording/{f}"
    return jsonify(recordings)


@app.route("/")
def serve_frontend():
    return send_from_directory(FRONTEND_DIR, "index.html")


if __name__ == "__main__":
    print("=" * 50)
    print("  GrowthPath - Backend + Frontend")
    print("  Auth: JWT | Storage: JSON files (data/)")
    print("  Open http://localhost:5000 in your browser")
    print("=" * 50)
    app.run(debug=True, port=5000)
