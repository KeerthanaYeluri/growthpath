"""Tests for Path Reordering, Replay, Interview Ready — Sprint 7"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from path_reorder import (
    _topic_matches_pattern, reorder_learning_path,
    check_resurface_topics, get_score_comparison,
    check_and_celebrate,
)
import storage


# ─── Pattern to Topic Matching ───

def test_topic_matches_system_design_pattern():
    topic = {"title": "System Design Fundamentals", "interest_area": "System Design"}
    assert _topic_matches_pattern(topic, "Scalability Trade-offs")

def test_topic_matches_database_pattern():
    topic = {"title": "Database Design with PostgreSQL", "interest_area": "Backend"}
    assert _topic_matches_pattern(topic, "Data Modeling")

def test_topic_does_not_match_unrelated():
    topic = {"title": "CSS Flexbox Layout", "interest_area": "Frontend Styling"}
    assert not _topic_matches_pattern(topic, "Scalability Trade-offs")

def test_topic_matches_behavioral_pattern():
    topic = {"title": "Behavioral Interview Prep", "interest_area": "Communication"}
    assert _topic_matches_pattern(topic, "Conflict Resolution")

def test_topic_matches_algorithm_pattern():
    topic = {"title": "Data Structures and Algorithms", "interest_area": "Coding"}
    assert _topic_matches_pattern(topic, "Arrays/Strings")


# ─── Path Reordering ───

def test_reorder_with_no_plan_returns_error():
    plan, err = reorder_learning_path("nonexistent_user", ["Scalability Trade-offs"])
    assert plan is None

def test_reorder_with_empty_patterns_no_change():
    # Create a test user with a plan
    user, _ = storage.register_user("Test Reorder", "reorder@test.com", ["Python"], ["System Design"], 2,
                                     target_company="google", target_role="backend", target_level="senior")
    if not user:
        return  # Skip if user exists

    plan_data = {
        "user_id": user["user_id"],
        "topics": [
            {"topic_id": "t1", "title": "Topic 1", "interest_area": "A", "status": "not_started"},
            {"topic_id": "t2", "title": "Topic 2", "interest_area": "B", "status": "not_started"},
        ],
    }
    storage.save_learning_plan(user["user_id"], plan_data)

    plan, changes = reorder_learning_path(user["user_id"], [])
    assert len(changes) == 0


# ─── Resurface Topics ───

def test_resurface_below_threshold():
    result = check_resurface_topics(
        "nonexistent_user",
        {"Scalability Trade-offs": [40, 30]},
        threshold=50, consecutive_required=2
    )
    # No plan found, so empty
    assert isinstance(result, list)


# ─── Score Comparison ───

def test_score_comparison_returns_list():
    result = get_score_comparison("nonexistent_user", limit=5)
    assert isinstance(result, list)


# ─── Interview Ready ───

def test_check_and_celebrate_no_user():
    result = check_and_celebrate("nonexistent_user")
    assert result is None

def test_check_and_celebrate_with_user():
    # Use a user that has ELO data
    user, _ = storage.register_user("Ready Test", "ready@test.com", ["Python"], ["Backend"], 2,
                                     target_company="google", target_role="backend", target_level="senior")
    if not user:
        return

    # Save ELO at hiring bar
    storage.save_elo_ratings(user["user_id"], 1800, {
        "phone_screen": 1800, "system_design": 1800,
        "behavioral": 1800, "domain_specific": 1800, "bar_raiser": 1800,
    })
    storage.add_elo_history(user["user_id"], None, "test", 1400, 1800, 400)

    result = check_and_celebrate(user["user_id"])
    assert result is not None
    assert result["is_ready"] is True
    assert result["celebrate"] is True  # First time at bar
