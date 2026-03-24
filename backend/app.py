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
from resume_parser import extract_text, validate_resume_file
import llm_service
from company_profiles import (
    SUPPORTED_COMPANIES, SUPPORTED_ROLES, SUPPORTED_LEVELS,
    ROLE_LABELS, LEVEL_LABELS, COMPANY_PROFILES,
    validate_registration_fields, get_company_profile, get_hiring_bar,
    get_starting_elo, get_round_config,
)
from elo_rating import create_initial_elo, check_interview_ready, get_readiness_label
from gap_map import generate_gap_map
from quick_assessment import generate_quick_assessment, score_assessment, compute_elo_from_assessment
from dual_scorer import dual_score, classify_answer_quality

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")

app = Flask(__name__, static_folder=FRONTEND_DIR)
CORS(app)

JWT_SECRET = os.environ.get("JWT_SECRET", "growthpath-secret-key-change-in-production")
JWT_EXPIRY = 86400  # 24 hours

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
CONTENT_DIR = os.path.join(DATA_DIR, "content")
RECORDINGS_DIR = os.path.join(DATA_DIR, "recordings")
UPLOADS_DIR = os.path.join(DATA_DIR, "uploads")
os.makedirs(RECORDINGS_DIR, exist_ok=True)
os.makedirs(UPLOADS_DIR, exist_ok=True)


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
    target_company = data.get("target_company", "").strip()
    target_role = data.get("target_role", "").strip()
    target_level = data.get("target_level", "").strip()

    if not full_name or not email:
        return jsonify({"error": "Name and email are required"}), 400

    # v2: Validate company/role/level if provided
    if target_company or target_role or target_level:
        if not target_company or not target_role or not target_level:
            return jsonify({"error": "target_company, target_role, and target_level are all required"}), 400
        validation_err = validate_registration_fields(target_company, target_role, target_level)
        if validation_err:
            return jsonify({"error": validation_err}), 400

    user, error = storage.register_user(
        full_name, email, tech_stack, interest_areas, hours_per_day,
        target_company=target_company, target_role=target_role, target_level=target_level,
    )
    if error:
        return jsonify({"error": error}), 409

    # Auto-generate learning plan on registration
    plan, plan_error = learning_engine.generate_learning_plan(user["user_id"])

    # v2: Initialize ELO ratings if target is set
    elo_data = None
    gap_map_data = None
    if target_company and target_role and target_level:
        starting_elo, _ = get_starting_elo(target_level)
        if starting_elo:
            elo_state = create_initial_elo(target_level)
            storage.save_elo_ratings(user["user_id"], elo_state["overall"], elo_state["sub_elos"])
            storage.add_elo_history(
                user["user_id"], None, "registration",
                0, elo_state["overall"], elo_state["overall"],
            )
            elo_data = check_interview_ready(elo_state["overall"], target_company, target_level)

        # Generate gap map
        gap_map_data, _ = generate_gap_map(tech_stack, target_role, target_level)

    token = create_token(user["user_id"], user["email"])
    return jsonify({
        "user_id": user["user_id"],
        "email": user["email"],
        "full_name": user["full_name"],
        "password": "welcome@123",
        "is_first_login": True,
        "token": token,
        "has_plan": plan is not None,
        "target_company": target_company,
        "target_role": target_role,
        "target_level": target_level,
        "elo": elo_data,
        "gap_map": gap_map_data,
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


@app.route("/api/config/companies", methods=["GET"])
def get_companies():
    """Return supported companies with their profiles."""
    return jsonify({
        "companies": SUPPORTED_COMPANIES,
        "profiles": {c: {"name": COMPANY_PROFILES[c]["name"], "description": COMPANY_PROFILES[c]["description"]}
                     for c in SUPPORTED_COMPANIES},
    })


@app.route("/api/config/roles", methods=["GET"])
def get_roles():
    """Return supported roles with labels."""
    return jsonify({"roles": SUPPORTED_ROLES, "labels": ROLE_LABELS})


@app.route("/api/config/levels", methods=["GET"])
def get_levels():
    """Return supported levels with labels."""
    return jsonify({"levels": SUPPORTED_LEVELS, "labels": LEVEL_LABELS})


# ─── ELO & Gap Map (v2) ───

@app.route("/api/elo", methods=["GET"])
@auth_required
def get_elo():
    """Get current ELO ratings, hiring bar, and readiness."""
    user = storage.get_user(g.user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    elo_data = storage.get_elo_ratings(g.user_id)
    if not elo_data:
        return jsonify({"error": "No ELO data. Complete registration with target company/role/level."}), 404

    readiness = check_interview_ready(
        elo_data["overall"],
        user.get("target_company", "google"),
        user.get("target_level", "senior"),
    )

    return jsonify({
        "overall": elo_data["overall"],
        "sub_elos": elo_data["sub_elos"],
        "readiness": readiness,
        "updated_at": elo_data["updated_at"],
    })


@app.route("/api/elo/history", methods=["GET"])
@auth_required
def get_elo_history():
    """Get ELO history for trend graph."""
    limit = request.args.get("limit", 50, type=int)
    history = storage.get_elo_history(g.user_id, limit=limit)
    return jsonify({"history": history})


@app.route("/api/gap-map", methods=["GET"])
@auth_required
def get_gap_map():
    """Get gap map: target role demands vs current tech stack."""
    user = storage.get_user(g.user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    target_role = user.get("target_role")
    target_level = user.get("target_level")
    tech_stack = user.get("tech_stack", [])

    if not target_role or not target_level:
        return jsonify({"error": "No target role/level set. Update profile first."}), 400

    gap_map_data, err = generate_gap_map(tech_stack, target_role, target_level)
    if err:
        return jsonify({"error": err}), 400

    return jsonify(gap_map_data)


@app.route("/api/company-profile/<company>", methods=["GET"])
def get_company_profile_endpoint(company):
    """Get full company profile with round config."""
    profile, err = get_company_profile(company)
    if err:
        return jsonify({"error": err}), 404

    rounds, _ = get_round_config(company)

    return jsonify({
        "name": profile["name"],
        "description": profile["description"],
        "round_weights": profile["round_weights"],
        "critical_rounds": profile["critical_rounds"],
        "rounds": rounds,
    })


# ─── Quick Assessment (v2 Sprint 2) ───

@app.route("/api/quick-assessment/start", methods=["POST"])
@auth_required
def start_quick_assessment():
    """Start a Quick Assessment for new users (Interview First flow)."""
    user = storage.get_user(g.user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    company = user.get("target_company", "google")
    role = user.get("target_role", "backend")
    level = user.get("target_level", "senior")

    if not company or not role or not level:
        return jsonify({"error": "Set target company/role/level in profile first"}), 400

    assessment = generate_quick_assessment(company, role, level)

    # Store as a session
    session_id = storage.create_session(
        g.user_id,
        f"Quick Assessment - {company.title()} {role}",
        assessment["questions"],
        f"quick_assessment_{company}_{role}",
    )
    if isinstance(session_id, dict):
        sid = session_id.get("session_id", session_id.get("id"))
    else:
        sid = session_id

    # Return safe questions (no keywords/rubric)
    safe_questions = [{
        "id": q["id"],
        "question": q["question"],
        "pattern": q["pattern"],
        "difficulty": q["difficulty"],
        "round_type": q["round_type"],
        "answer_mode": q["answer_mode"],
    } for q in assessment["questions"]]

    return jsonify({
        "session_id": sid,
        "questions": safe_questions,
        "total_questions": assessment["total_questions"],
        "company": company,
        "role": role,
        "level": level,
    })


@app.route("/api/quick-assessment/submit", methods=["POST"])
@auth_required
def submit_quick_assessment():
    """Submit all answers for a Quick Assessment and get results + ELO update."""
    data = request.json
    session_id = data.get("session_id")
    answers = data.get("answers", [])  # [{question_id, answer_text}]

    if not session_id or not answers:
        return jsonify({"error": "session_id and answers are required"}), 400

    # Get session with full questions
    session = storage.get_session(session_id)
    if not session:
        return jsonify({"error": "Session not found"}), 404

    questions = session.get("questions", [])
    if not questions:
        return jsonify({"error": "No questions found in session"}), 400

    # Score all answers
    results = score_assessment(answers, questions)

    # Get current ELO
    user = storage.get_user(g.user_id)
    elo_data = storage.get_elo_ratings(g.user_id)

    if elo_data:
        current_elo = elo_data["overall"]
        sub_elos = elo_data["sub_elos"]
    else:
        from company_profiles import get_starting_elo as _get_starting_elo
        level = user.get("target_level", "senior")
        starting, _ = _get_starting_elo(level)
        current_elo = starting or 1200
        sub_elos = {rt: current_elo for rt in ["phone_screen", "system_design", "behavioral", "domain_specific", "bar_raiser"]}

    # Compute new ELO
    elo_result = compute_elo_from_assessment(current_elo, sub_elos, results)

    # Save updated ELO
    new_overall = elo_result["overall"]["new_elo"]
    new_sub_elos = {}
    for rt, change in elo_result["sub_elos"].items():
        new_sub_elos[rt] = change["new_elo"]
    # Keep unchanged sub-ELOs
    for rt in sub_elos:
        if rt not in new_sub_elos:
            new_sub_elos[rt] = sub_elos[rt]

    storage.save_elo_ratings(g.user_id, new_overall, new_sub_elos)
    storage.add_elo_history(
        g.user_id, session_id, "quick_assessment",
        current_elo, new_overall, elo_result["overall"]["delta"],
        {rt: c["delta"] for rt, c in elo_result["sub_elos"].items()},
    )

    # Generate learning path from failures
    path_generated = False
    if results["weak_patterns"]:
        plan, _ = learning_engine.generate_learning_plan(g.user_id)
        path_generated = plan is not None

    # Finish session with scorecard
    scorecard = {
        "overall_score": results["overall_score"],
        "per_round": results["per_round"],
        "pattern_scores": results["pattern_scores"],
        "weak_patterns": results["weak_patterns"],
        "strong_patterns": results["strong_patterns"],
        "recommended_focus": results["recommended_focus"],
        "elo_before": current_elo,
        "elo_after": new_overall,
        "elo_delta": elo_result["overall"]["delta"],
    }
    storage.finish_session(session_id, scorecard)

    # Check readiness
    company = user.get("target_company", "google")
    level = user.get("target_level", "senior")
    readiness = check_interview_ready(new_overall, company, level)

    return jsonify({
        "results": results,
        "elo": {
            "before": current_elo,
            "after": new_overall,
            "delta": elo_result["overall"]["delta"],
            "sub_elo_changes": {rt: c for rt, c in elo_result["sub_elos"].items()},
        },
        "readiness": readiness,
        "path_generated": path_generated,
        "scorecard": scorecard,
    })


@app.route("/api/quick-assessment/results/<session_id>", methods=["GET"])
@auth_required
def get_quick_assessment_results(session_id):
    """Get results of a completed Quick Assessment."""
    session = storage.get_session(session_id)
    if not session:
        return jsonify({"error": "Session not found"}), 404
    if session.get("user_id") != g.user_id:
        return jsonify({"error": "Access denied"}), 403

    return jsonify({
        "session_id": session_id,
        "scorecard": session.get("scorecard"),
        "status": session.get("status"),
        "start_time": session.get("start_time"),
        "end_time": session.get("end_time"),
    })


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


# ─── JD-Based Interview ───

@app.route("/api/session/start-jd", methods=["POST"])
@auth_optional
def start_session_jd():
    """Start an interview session with LLM-generated questions from a job description."""
    data = request.json
    name = data.get("candidate_name", "").strip()
    job_description = data.get("job_description", "").strip()

    if not name or not job_description:
        return jsonify({"error": "Name and job description are required"}), 400

    if len(job_description) < 50:
        return jsonify({"error": "Please provide a more detailed job description (at least 50 characters)"}), 400

    try:
        questions, provider = llm_service.generate_questions_from_jd(job_description, num_questions=15)

        # Ensure proper format
        for i, q in enumerate(questions):
            q["id"] = i + 1
            if "keywords" not in q:
                q["keywords"] = []
            if "model_answer" not in q:
                q["model_answer"] = "No model answer available."
            if "topic" not in q:
                q["topic"] = "General"
            if "difficulty" not in q:
                q["difficulty"] = "Medium"

    except Exception as e:
        print(f"[JD Interview] LLM error: {e}")
        return jsonify({"error": f"Failed to generate questions: {str(e)}"}), 500

    # Extract a short job title from the JD (first line or first 50 chars)
    job_title = job_description.split("\n")[0][:60].strip()
    if not job_title:
        job_title = "JD-Based Interview"

    user_id = g.user_id or "anonymous"
    session = storage.create_session(user_id, job_title, questions, "JD-Based")

    print(f"[JD Session] {name} | {len(questions)} Qs via {provider} | User: {user_id}")

    return jsonify({
        "session_id": session["session_id"],
        "candidate_name": name,
        "job_title": job_title,
        "role_name": "JD-Based",
        "total_questions": len(questions),
        "llm_provider": provider,
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


# ═══════════════════════════════════════════════════
# Phase 2: AI Voice Interview Engine
# ═══════════════════════════════════════════════════


# ─── Resume Upload & Parsing ───

@app.route("/api/resume/upload", methods=["POST"])
@auth_required
def upload_resume():
    """Upload and parse a resume (PDF/DOCX/TXT)."""
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if not file.filename:
        return jsonify({"error": "No file selected"}), 400

    # Validate file
    file.seek(0, 2)
    file_size = file.tell()
    file.seek(0)
    valid, error = validate_resume_file(file.filename, file_size)
    if not valid:
        return jsonify({"error": error}), 400

    # Save file temporarily
    import uuid
    safe_name = f"{uuid.uuid4().hex[:8]}_{file.filename}"
    file_path = os.path.join(UPLOADS_DIR, safe_name)
    file.save(file_path)

    try:
        # Extract text
        raw_text = extract_text(file_path)
        if not raw_text or len(raw_text) < 50:
            return jsonify({"error": "Could not extract enough text from resume. Try a different format."}), 400

        # Parse with LLM
        user = storage.get_user(g.user_id)
        interest = user.get("interest_areas", ["General"])[0] if user else "General"

        try:
            parsed_data, provider = llm_service.analyze_resume(raw_text, interest)
        except Exception as e:
            # Save with raw text only if LLM fails
            parsed_data = {"skills": [], "experience_years": 0, "experience_level": "mid",
                          "projects": [], "education": [], "strengths": [], "gaps_for_role": [],
                          "summary": "Resume uploaded but AI parsing unavailable.", "parse_error": str(e)}
            provider = "none"

        # Delete old resumes (single resume per user)
        old_resumes = storage.get_user_resumes(g.user_id)
        for old in old_resumes:
            storage.delete_resume(old["id"])

        # Save to DB
        resume = storage.save_resume(g.user_id, file.filename, raw_text, parsed_data)
        resume["llm_provider"] = provider

        return jsonify(resume), 201

    finally:
        # Clean up temp file
        if os.path.exists(file_path):
            os.remove(file_path)


@app.route("/api/resume/<resume_id>", methods=["GET"])
@auth_required
def get_resume(resume_id):
    """Get a parsed resume."""
    resume = storage.get_resume(resume_id)
    if not resume:
        return jsonify({"error": "Resume not found"}), 404
    if resume["user_id"] != g.user_id:
        return jsonify({"error": "Unauthorized"}), 403
    return jsonify(resume)


@app.route("/api/resume/<resume_id>", methods=["DELETE"])
@auth_required
def delete_resume(resume_id):
    """Delete a resume."""
    resume = storage.get_resume(resume_id)
    if not resume:
        return jsonify({"error": "Resume not found"}), 404
    if resume["user_id"] != g.user_id:
        return jsonify({"error": "Unauthorized"}), 403
    storage.delete_resume(resume_id)
    return jsonify({"message": "Resume deleted"})


@app.route("/api/resume/list", methods=["GET"])
@auth_required
def list_resumes():
    """Get all resumes for the current user."""
    resumes = storage.get_user_resumes(g.user_id)
    return jsonify(resumes)


# ─── AI Interview: Create & Question Generation ───

@app.route("/api/ai-interview/create", methods=["POST"])
@auth_required
def create_ai_interview():
    """Create AI interview: parses resume + generates role-specific questions."""
    data = request.get_json()
    resume_id = data.get("resume_id")
    job_role = data.get("job_role", "")
    interest_area = data.get("interest_area", "")

    if not resume_id:
        return jsonify({"error": "resume_id is required"}), 400

    resume = storage.get_resume(resume_id)
    if not resume:
        return jsonify({"error": "Resume not found"}), 404

    # Use user's interest areas if not specified
    if not interest_area:
        user = storage.get_user(g.user_id)
        interest_area = user.get("interest_areas", ["General"])[0] if user else "General"

    if not job_role:
        job_role = f"{interest_area} Engineer"

    # Generate questions using LLM
    try:
        questions, provider = llm_service.generate_interview_questions(
            resume["parsed_data"], job_role, interest_area, num_questions=15)
    except Exception as e:
        return jsonify({"error": f"Failed to generate questions: {str(e)}"}), 500

    # Create interview session
    interview = storage.create_ai_interview(
        g.user_id, resume_id, job_role, interest_area, questions, provider)

    return jsonify(interview), 201


@app.route("/api/ai-interview/<interview_id>", methods=["GET"])
@auth_required
def get_ai_interview(interview_id):
    """Get AI interview details."""
    interview = storage.get_ai_interview(interview_id)
    if not interview:
        return jsonify({"error": "Interview not found"}), 404
    if interview["user_id"] != g.user_id:
        return jsonify({"error": "Unauthorized"}), 403
    return jsonify(interview)


@app.route("/api/ai-interview/list", methods=["GET"])
@auth_required
def list_ai_interviews():
    """List all AI interviews for current user."""
    interviews = storage.get_user_ai_interviews(g.user_id)
    return jsonify(interviews)


# ─── AI Interview: Conduct Interview ───

@app.route("/api/ai-interview/<interview_id>/start", methods=["POST"])
@auth_required
def start_ai_interview(interview_id):
    """Start the interview — returns the first question."""
    interview = storage.get_ai_interview(interview_id)
    if not interview:
        return jsonify({"error": "Interview not found"}), 404
    if interview["user_id"] != g.user_id:
        return jsonify({"error": "Unauthorized"}), 403
    if interview["status"] not in ("pending", "in_progress"):
        return jsonify({"error": "Interview already completed"}), 400

    storage.update_ai_interview_status(interview_id, "in_progress")

    questions = interview["questions"]
    if not questions:
        return jsonify({"error": "No questions available"}), 500

    first_q = questions[0]

    # Save the first exchange (question only, no answer yet)
    exchange = storage.save_exchange(
        interview_id, 0, first_q["question"], first_q.get("category", "technical"),
        first_q.get("difficulty", "medium"),
        first_q.get("expected_topics", []), first_q.get("ideal_answer_points", []))

    return jsonify({
        "interview_id": interview_id,
        "status": "in_progress",
        "current_question": 0,
        "total_questions": len(questions),
        "question": first_q["question"],
        "category": first_q.get("category", "technical"),
        "exchange_id": exchange["id"],
        "greeting": f"Hello! I'm Alex, and I'll be conducting your {interview['interest_area']} interview today. Let's get started with the first question.",
    })


@app.route("/api/ai-interview/<interview_id>/answer", methods=["POST"])
@auth_required
def submit_ai_answer(interview_id):
    """Submit answer for current question, get next question or finish."""
    interview = storage.get_ai_interview(interview_id)
    if not interview:
        return jsonify({"error": "Interview not found"}), 404
    if interview["status"] != "in_progress":
        return jsonify({"error": "Interview not in progress"}), 400

    data = request.get_json()
    answer_text = data.get("answer", "")
    exchange_id = data.get("exchange_id")
    answer_duration = data.get("duration_sec", 0)

    if not answer_text:
        return jsonify({"error": "Answer is required"}), 400

    # Get current exchanges to determine position
    exchanges = storage.get_interview_exchanges(interview_id)
    current_idx = len(exchanges) - 1
    questions = interview["questions"]

    # Generate AI acknowledgment
    try:
        conversation_history = []
        for ex in exchanges:
            conversation_history.append({"role": "assistant", "content": ex["question_text"]})
            if ex.get("answer_text"):
                conversation_history.append({"role": "user", "content": ex["answer_text"]})

        context = {
            "job_role": interview["job_role"],
            "interest_area": interview["interest_area"],
            "conversation_history": conversation_history,
        }
        ai_response, _ = llm_service.generate_conversational_response(
            context, answer_text, current_idx, len(questions))
    except Exception:
        ai_response = "Thank you for that answer. Let's move on."

    # Update exchange with answer
    if exchange_id:
        storage.update_exchange_answer(exchange_id, answer_text, answer_duration,
                                       ai_acknowledgment=ai_response)

    # Check if there are more questions
    next_idx = current_idx + 1
    if next_idx < len(questions):
        next_q = questions[next_idx]
        # Save next exchange
        next_exchange = storage.save_exchange(
            interview_id, next_idx, next_q["question"], next_q.get("category", "technical"),
            next_q.get("difficulty", "medium"),
            next_q.get("expected_topics", []), next_q.get("ideal_answer_points", []))

        return jsonify({
            "status": "in_progress",
            "current_question": next_idx,
            "total_questions": len(questions),
            "ai_response": ai_response,
            "question": next_q["question"],
            "category": next_q.get("category", "technical"),
            "exchange_id": next_exchange["id"],
        })
    else:
        # Interview complete
        storage.update_ai_interview_status(interview_id, "completed")
        return jsonify({
            "status": "completed",
            "ai_response": ai_response + " That concludes our interview. Thank you for your time! Your results will be available shortly.",
            "total_questions": len(questions),
            "message": "Interview completed! You can now request evaluation.",
        })


@app.route("/api/ai-interview/<interview_id>/end", methods=["POST"])
@auth_required
def end_ai_interview(interview_id):
    """End interview early."""
    interview = storage.get_ai_interview(interview_id)
    if not interview:
        return jsonify({"error": "Interview not found"}), 404
    if interview["status"] != "in_progress":
        return jsonify({"error": "Interview not in progress"}), 400

    storage.update_ai_interview_status(interview_id, "completed")
    return jsonify({"status": "completed", "message": "Interview ended."})


# ─── AI Interview: Evaluation ───

@app.route("/api/ai-interview/<interview_id>/evaluate", methods=["POST"])
@auth_required
def evaluate_ai_interview(interview_id):
    """Evaluate all answers in the interview using LLM."""
    interview = storage.get_ai_interview(interview_id)
    if not interview:
        return jsonify({"error": "Interview not found"}), 404
    if interview["status"] not in ("completed", "evaluated"):
        return jsonify({"error": "Interview must be completed first"}), 400

    resume = storage.get_resume(interview["resume_id"])
    resume_summary = resume["parsed_data"].get("summary", "") if resume else ""

    exchanges = storage.get_interview_exchanges(interview_id)
    evaluated_exchanges = []

    for ex in exchanges:
        if not ex.get("answer_text"):
            continue
        try:
            scores, _ = llm_service.evaluate_answer(
                ex["question_text"], ex["answer_text"], ex.get("question_category", "technical"),
                ex.get("expected_topics", []), ex.get("ideal_answer_points", []),
                resume_summary)
            storage.save_evaluation(interview_id, ex["id"], scores)
            evaluated_exchanges.append({
                "question": ex["question_text"],
                "category": ex.get("question_category"),
                "answer": ex["answer_text"],
                "scores": scores,
            })
        except Exception as e:
            evaluated_exchanges.append({
                "question": ex["question_text"],
                "error": str(e),
            })

    # Generate overall summary
    try:
        summary_data = {
            "job_role": interview["job_role"],
            "interest_area": interview["interest_area"],
            "experience_level": resume["parsed_data"].get("experience_level", "mid") if resume else "mid",
            "exchanges": evaluated_exchanges,
        }
        result, _ = llm_service.generate_interview_summary(summary_data)
        storage.save_interview_result(interview_id, result)
        storage.update_ai_interview_status(interview_id, "evaluated")
    except Exception as e:
        result = {"error": str(e), "overall_score": 0}

    return jsonify({
        "interview_id": interview_id,
        "status": "evaluated",
        "per_answer": evaluated_exchanges,
        "overall": result,
    })


@app.route("/api/ai-interview/<interview_id>/results", methods=["GET"])
@auth_required
def get_ai_interview_results(interview_id):
    """Get full interview results with evaluations."""
    interview = storage.get_ai_interview(interview_id)
    if not interview:
        return jsonify({"error": "Interview not found"}), 404

    exchanges = storage.get_interview_exchanges(interview_id)
    evaluations = storage.get_interview_evaluations(interview_id)
    result = storage.get_interview_result(interview_id)

    # Map evaluations to exchanges
    eval_map = {e["exchange_id"]: e for e in evaluations}
    transcript = []
    for ex in exchanges:
        transcript.append({
            "sequence": ex["sequence_num"],
            "question": ex["question_text"],
            "category": ex.get("question_category"),
            "answer": ex.get("answer_text", ""),
            "ai_response": ex.get("ai_acknowledgment", ""),
            "evaluation": eval_map.get(ex["id"]),
        })

    return jsonify({
        "interview": interview,
        "transcript": transcript,
        "result": result,
    })


@app.route("/api/ai-interview/<interview_id>/transcript", methods=["GET"])
@auth_required
def get_transcript(interview_id):
    """Get interview transcript."""
    interview = storage.get_ai_interview(interview_id)
    if not interview:
        return jsonify({"error": "Interview not found"}), 404

    exchanges = storage.get_interview_exchanges(interview_id)
    transcript = []
    for ex in exchanges:
        transcript.append({
            "sequence": ex["sequence_num"],
            "question": ex["question_text"],
            "answer": ex.get("answer_text", ""),
            "ai_response": ex.get("ai_acknowledgment", ""),
            "timestamp": ex.get("timestamp"),
        })

    return jsonify({
        "interview_id": interview_id,
        "job_role": interview["job_role"],
        "interest_area": interview["interest_area"],
        "transcript": transcript,
    })


# ─── HR Dashboard ───

@app.route("/api/hr/register", methods=["POST"])
def hr_register():
    """Register HR user."""
    data = request.get_json()
    email = data.get("email", "")
    password = data.get("password", "")
    full_name = data.get("full_name", "")
    company = data.get("company", "")

    if not all([email, password, full_name]):
        return jsonify({"error": "email, password, and full_name are required"}), 400

    hr, error = storage.register_hr_user(email, password, full_name, company)
    if error:
        return jsonify({"error": error}), 409
    return jsonify(hr), 201


@app.route("/api/hr/login", methods=["POST"])
def hr_login():
    """HR user login."""
    data = request.get_json()
    hr, error = storage.login_hr_user(data.get("email", ""), data.get("password", ""))
    if error:
        return jsonify({"error": error}), 401
    token = create_token(hr["id"], hr["email"])
    return jsonify({"token": token, "user": hr})


@app.route("/api/hr/candidates", methods=["GET"])
@auth_required
def hr_get_candidates():
    """Get all candidates with interview results."""
    candidates = storage.get_all_candidates_with_results()
    return jsonify(candidates)


@app.route("/api/hr/interview/<interview_id>/results", methods=["GET"])
@auth_required
def hr_get_interview_results(interview_id):
    """Get specific interview results (HR view)."""
    interview = storage.get_ai_interview(interview_id)
    if not interview:
        return jsonify({"error": "Interview not found"}), 404

    exchanges = storage.get_interview_exchanges(interview_id)
    evaluations = storage.get_interview_evaluations(interview_id)
    result = storage.get_interview_result(interview_id)
    resume = storage.get_resume(interview.get("resume_id", ""))

    eval_map = {e["exchange_id"]: e for e in evaluations}
    transcript = []
    for ex in exchanges:
        transcript.append({
            "sequence": ex["sequence_num"],
            "question": ex["question_text"],
            "category": ex.get("question_category"),
            "answer": ex.get("answer_text", ""),
            "evaluation": eval_map.get(ex["id"]),
        })

    return jsonify({
        "interview": interview,
        "resume": resume,
        "transcript": transcript,
        "result": result,
    })


# ─── LLM Config ───

@app.route("/api/config/llm-status", methods=["GET"])
def llm_status():
    """Check which LLM providers are configured."""
    providers = llm_service._get_available_providers()
    return jsonify({
        "available_providers": providers,
        "claude": "claude" in providers,
        "openai": "openai" in providers,
        "gemini": "gemini" in providers,
        "any_available": len(providers) > 0,
    })


@app.route("/")
def serve_frontend():
    return send_from_directory(FRONTEND_DIR, "index.html")


if __name__ == "__main__":
    print("=" * 50)
    print("  GrowthPath - Backend + Frontend")
    print("  Auth: JWT | Storage: PostgreSQL/SQLite")
    print("  Open http://localhost:5000 in your browser")
    print("=" * 50)
    app.run(debug=True, port=5000)
