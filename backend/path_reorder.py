"""
Learning Path Reordering + Mock Replay + Interview Ready - GrowthPath v2.0 (Sprint 7)
Weakness-driven path reordering, mock replay system,
and Interview Ready detection with celebration.
"""

import storage
from company_profiles import get_company_profile, ROUND_LABELS
from elo_rating import check_interview_ready

# ──────────────────────────────────────────────
# Weakness-Driven Path Reordering
# ──────────────────────────────────────────────

# Maps archetype patterns to relevant learning topic keywords
PATTERN_TO_TOPIC_MAP = {
    "Scalability Trade-offs": ["system design", "distributed", "architecture", "scalab"],
    "Data Modeling": ["database", "sql", "data model", "schema"],
    "API Design": ["api", "rest", "graphql", "endpoint"],
    "Caching Strategy": ["cache", "redis", "cdn", "performance"],
    "Message Queues": ["queue", "kafka", "event", "async", "messaging"],
    "Load Balancing": ["load balanc", "nginx", "scaling", "distributed"],
    "Database Selection": ["database", "sql", "nosql", "postgres", "mongo"],
    "Arrays/Strings": ["data structure", "algorithm", "array", "string", "coding"],
    "Trees/Graphs": ["tree", "graph", "traversal", "bfs", "dfs"],
    "Dynamic Programming": ["dynamic programming", "dp", "algorithm", "optimization"],
    "Sliding Window": ["sliding window", "array", "algorithm", "substring"],
    "Binary Search": ["binary search", "search", "algorithm", "sorted"],
    "Recursion/Backtracking": ["recursion", "backtrack", "algorithm"],
    "Sorting": ["sort", "algorithm", "merge", "quick"],
    "Conflict Resolution": ["behavioral", "conflict", "communication", "team"],
    "Failure/Recovery": ["behavioral", "failure", "postmortem", "incident"],
    "Leadership/Influence": ["leadership", "influence", "mentor", "lead"],
    "Ambiguity Handling": ["behavioral", "ambiguity", "decision", "uncertain"],
    "Ownership": ["ownership", "initiative", "responsibility"],
    "Collaboration": ["collaboration", "team", "cross-functional"],
}


def _topic_matches_pattern(topic, pattern):
    """Check if a learning topic is related to a weak pattern."""
    title_lower = (topic.get("title", "") + " " + topic.get("interest_area", "")).lower()
    keywords = PATTERN_TO_TOPIC_MAP.get(pattern, [])
    return any(kw in title_lower for kw in keywords)


def reorder_learning_path(user_id, weak_patterns, company=None, max_nudge=3):
    """Reorder learning path by pushing weak areas up (gentle nudge).

    Args:
        user_id: User ID
        weak_patterns: List of weak archetype pattern names
        company: Target company for weighting (70% company, 30% general)
        max_nudge: Max positions to move a topic up (default 3)

    Returns:
        (reordered_plan, changes) or (None, error)
    """
    plan = storage.get_learning_plan(user_id)
    if not plan:
        return None, "No learning plan found"

    topics = plan.get("topics", [])
    if not topics:
        return None, "Empty learning plan"

    # Separate completed from remaining
    completed = [t for t in topics if t.get("status") == "completed"]
    remaining = [t for t in topics if t.get("status") != "completed"]

    if not remaining or not weak_patterns:
        return plan, []

    # Score each remaining topic by weakness relevance
    for topic in remaining:
        relevance = 0
        for pattern in weak_patterns:
            if _topic_matches_pattern(topic, pattern):
                relevance += 1
        topic["_weakness_relevance"] = relevance

    # Company weighting
    if company:
        profile, _ = get_company_profile(company)
        if profile:
            critical = profile.get("critical_rounds", [])
            for topic in remaining:
                title_lower = (topic.get("title", "") + " " + topic.get("interest_area", "")).lower()
                for rt in critical:
                    round_keywords = PATTERN_TO_TOPIC_MAP.get(
                        {"system_design": "Scalability Trade-offs", "behavioral": "Conflict Resolution",
                         "domain_specific": "API Design"}.get(rt, ""), [])
                    if any(kw in title_lower for kw in round_keywords):
                        topic["_weakness_relevance"] += 2  # Company critical boost

    # Gentle nudge: sort by relevance but cap movement at max_nudge positions
    changes = []
    original_order = [t.get("topic_id") for t in remaining]

    # Sort remaining by relevance (higher = earlier), preserving relative order for ties
    remaining_sorted = sorted(remaining, key=lambda t: -t.get("_weakness_relevance", 0))

    # Cap movement: no topic moves more than max_nudge positions up
    final_order = list(remaining)
    for topic in remaining_sorted:
        if topic["_weakness_relevance"] > 0:
            current_idx = final_order.index(topic)
            new_idx = max(0, current_idx - max_nudge)
            if new_idx < current_idx:
                final_order.remove(topic)
                final_order.insert(new_idx, topic)
                changes.append({
                    "topic_id": topic.get("topic_id"),
                    "title": topic.get("title"),
                    "moved_from": current_idx + len(completed) + 1,
                    "moved_to": new_idx + len(completed) + 1,
                    "reason": f"Weak pattern: {', '.join(p for p in weak_patterns if _topic_matches_pattern(topic, p))}",
                })

    # Clean up temp fields
    for t in final_order:
        t.pop("_weakness_relevance", None)

    # Rebuild plan
    plan["topics"] = completed + final_order
    storage.save_learning_plan(user_id, plan)

    return plan, changes


def check_resurface_topics(user_id, pattern_scores, threshold=50, consecutive_required=2):
    """Check if completed topics should resurface due to declining pattern scores.

    Returns:
        List of topic_ids that should be resurfaced
    """
    plan = storage.get_learning_plan(user_id)
    if not plan:
        return []

    completed = [t for t in plan.get("topics", []) if t.get("status") == "completed"]
    resurface = []

    for topic in completed:
        for pattern, scores in pattern_scores.items():
            if not _topic_matches_pattern(topic, pattern):
                continue
            # Check if last N scores are below threshold
            if len(scores) >= consecutive_required:
                recent = scores[-consecutive_required:]
                if all(s < threshold for s in recent):
                    resurface.append(topic.get("topic_id"))
                    break

    return list(set(resurface))


# ──────────────────────────────────────────────
# Mock Replay
# ──────────────────────────────────────────────

def get_mock_replay(session_id):
    """Get full replay data for a completed mock interview.

    Returns:
        {
            'session': session data,
            'scorecard': scorecard,
            'questions': questions with answers,
            'is_replay': True (doesn't affect ELO),
        }
    """
    session = storage.get_session(session_id)
    if not session:
        return None, "Session not found"

    if session.get("status") != "completed":
        return None, "Session not yet completed"

    questions = session.get("questions", [])
    answers = session.get("answers", [])

    # Merge answers into questions
    answer_map = {}
    for a in answers:
        qid = a.get("question_id")
        if qid is not None:
            answer_map[qid] = a

    replay_questions = []
    for q in questions:
        qid = q.get("id")
        answer = answer_map.get(qid, {})
        replay_questions.append({
            "id": qid,
            "question": q.get("question", ""),
            "pattern": q.get("pattern", ""),
            "difficulty": q.get("difficulty", ""),
            "round_type": q.get("round_type", ""),
            "answer_text": answer.get("transcript", answer.get("answer_text", "")),
            "score": answer.get("score", 0),
            "rating": answer.get("rating", 0),
        })

    return {
        "session_id": session_id,
        "job_title": session.get("job_title", ""),
        "start_time": session.get("start_time"),
        "end_time": session.get("end_time"),
        "scorecard": session.get("scorecard", {}),
        "questions": replay_questions,
        "is_replay": True,
    }, None


def get_score_comparison(user_id, limit=10):
    """Get score comparison across recent mock attempts.

    Returns:
        List of {session_id, date, overall_score, elo_before, elo_after, elo_delta, per_round}
    """
    sessions = storage.get_user_sessions(user_id)

    comparisons = []
    for s in sessions:
        sc = s.get("scorecard")
        if not sc:
            continue
        role_name = s.get("role_name", "")
        if not role_name.startswith("mock_") and not role_name.startswith("quick_assessment"):
            continue

        comparisons.append({
            "session_id": s.get("session_id"),
            "date": s.get("end_time", s.get("start_time", "")),
            "job_title": s.get("job_title", ""),
            "overall_score": sc.get("overall_score", 0),
            "elo_before": sc.get("elo_before", 0),
            "elo_after": sc.get("elo_after", 0),
            "elo_delta": sc.get("elo_delta", 0),
            "per_round": sc.get("per_round", {}),
        })

    # Sort by date descending
    comparisons.sort(key=lambda c: c["date"], reverse=True)
    return comparisons[:limit]


# ──────────────────────────────────────────────
# Interview Ready Detection
# ──────────────────────────────────────────────

def check_and_celebrate(user_id):
    """Check if user has reached Interview Ready status.

    Returns:
        {
            'is_ready': bool,
            'elo': int,
            'hiring_bar': int,
            'company': str,
            'level': str,
            'celebrate': bool (True only the FIRST time they're ready),
        }
    """
    user = storage.get_user(user_id)
    if not user:
        return None

    elo_data = storage.get_elo_ratings(user_id)
    if not elo_data:
        return None

    company = user.get("target_company", "google")
    level = user.get("target_level", "senior")
    readiness = check_interview_ready(elo_data["overall"], company, level)

    # Check if this is the first time they're ready (check ELO history)
    celebrate = False
    if readiness["is_ready"]:
        history = storage.get_elo_history(user_id, limit=100)
        # If no previous entry had ELO >= hiring_bar, this is the first time
        past_ready = any(
            h.get("new_elo", 0) >= readiness["hiring_bar"]
            for h in history[1:]  # Skip the most recent (current)
        )
        celebrate = not past_ready

    return {
        "is_ready": readiness["is_ready"],
        "elo": elo_data["overall"],
        "hiring_bar": readiness["hiring_bar"],
        "gap": readiness["gap"],
        "company": company,
        "level": level,
        "readiness_label": readiness["readiness"]["label"],
        "celebrate": celebrate,
    }
