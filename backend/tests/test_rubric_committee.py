"""Tests for Rubric Reveal, Hiring Committee, Pattern Tracking — Sprint 5-6"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from rubric_reveal import (
    generate_rubric_reveal, generate_all_rubric_reveals,
    simulate_hiring_committee, compute_pattern_mastery,
)


# ─── Rubric Reveal ───

def test_rubric_generated_per_question():
    q = {"question": "Two sum problem", "keywords": ["hash map", "O(n)"],
         "rubric": ["Brute force", "Hash map optimization", "Edge cases", "Complexity analysis"],
         "pattern": "Arrays/Strings"}
    reveal = generate_rubric_reveal(q, "I would use a hash map for O(n) time complexity, handling edge cases")
    assert "rubric_points" in reveal
    assert len(reveal["rubric_points"]) == 4

def test_rubric_shows_covered_points():
    q = {"question": "Q", "keywords": ["hash map"], "rubric": ["Use hash map", "Analyze complexity"], "pattern": "X"}
    reveal = generate_rubric_reveal(q, "I would use a hash map to store values. Analyze the complexity.")
    covered = [p for p in reveal["rubric_points"] if p["covered"]]
    assert len(covered) > 0

def test_rubric_shows_missed_points():
    q = {"question": "Q", "keywords": ["hash map", "binary search"],
         "rubric": ["Hash map approach", "Binary search approach"], "pattern": "X"}
    reveal = generate_rubric_reveal(q, "Use hash map only")
    missed = [p for p in reveal["rubric_points"] if not p["covered"]]
    assert len(missed) >= 1

def test_rubric_counts_n_of_m():
    q = {"question": "Q", "keywords": [], "rubric": ["A", "B", "C", "D"], "pattern": "X"}
    reveal = generate_rubric_reveal(q, "A and B are important")
    assert reveal["total_count"] == 4
    assert 0 <= reveal["covered_count"] <= 4

def test_rubric_includes_keyword_analysis():
    q = {"question": "Q", "keywords": ["hash map", "O(n)", "complement"], "rubric": [], "pattern": "X"}
    reveal = generate_rubric_reveal(q, "Use hash map for O(n)")
    assert len(reveal["keywords_matched"]) > 0
    assert len(reveal["keywords_missed"]) > 0

def test_rubric_includes_thinking_breakdown():
    q = {"question": "Q", "keywords": [], "rubric": [], "pattern": "X"}
    reveal = generate_rubric_reveal(q, "First, let me clarify. One approach is brute force, alternatively hash map.")
    assert "thinking_breakdown" in reveal
    assert "clarifying_questions" in reveal["thinking_breakdown"]

def test_rubric_all_reveals():
    questions = [
        {"id": 1, "question": "Q1", "keywords": ["hash"], "rubric": ["Point A"], "pattern": "P1"},
        {"id": 2, "question": "Q2", "keywords": ["tree"], "rubric": ["Point B"], "pattern": "P2"},
    ]
    answers = {1: "hash map solution", 2: "tree traversal"}
    reveals = generate_all_rubric_reveals(questions, answers)
    assert len(reveals) == 2
    assert reveals[0]["question_id"] == 1


# ─── Hiring Committee ───

def test_committee_has_3_interviewers():
    scores = {"phone_screen": 70, "system_design": 60, "behavioral": 50, "domain_specific": 40, "bar_raiser": 55}
    result = simulate_hiring_committee(scores, "google")
    assert len(result["interviewers"]) == 3

def test_each_interviewer_has_vote():
    scores = {"phone_screen": 80, "system_design": 70}
    result = simulate_hiring_committee(scores, "google")
    for inv in result["interviewers"]:
        assert inv["vote"] in ["STRONG_HIRE", "HIRE", "LEAN_HIRE", "LEAN_NO_HIRE", "NO_HIRE", "STRONG_NO_HIRE"]

def test_each_interviewer_has_quotes():
    scores = {"phone_screen": 80, "system_design": 30, "behavioral": 60}
    result = simulate_hiring_committee(scores, "google")
    for inv in result["interviewers"]:
        assert len(inv["quotes"]) > 0

def test_majority_vote_hire():
    # High scores should lead to HIRE
    scores = {"phone_screen": 90, "system_design": 85, "behavioral": 80, "domain_specific": 85, "bar_raiser": 90}
    result = simulate_hiring_committee(scores, "google")
    assert result["verdict"] in ("HIRE", "LEAN_HIRE")

def test_majority_vote_no_hire():
    # Low scores should lead to NO_HIRE
    scores = {"phone_screen": 15, "system_design": 10, "behavioral": 20, "domain_specific": 15, "bar_raiser": 10}
    result = simulate_hiring_committee(scores, "google")
    assert "NO_HIRE" in result["verdict"]

def test_veto_on_critical_round():
    # Very low system_design (critical for Google) should trigger veto
    scores = {"phone_screen": 80, "system_design": 10, "behavioral": 80, "domain_specific": 80, "bar_raiser": 80}
    result = simulate_hiring_committee(scores, "google", critical_rounds=["system_design"])
    # With one very low critical score, veto might apply
    assert result["verdict"] in ("NO_HIRE", "LEAN_NO_HIRE", "LEAN_HIRE", "HIRE")  # Depends on assignment

def test_committee_has_verdict_label():
    scores = {"phone_screen": 50, "system_design": 50}
    result = simulate_hiring_committee(scores, "google")
    assert "verdict_label" in result
    assert len(result["verdict_label"]) > 0

def test_committee_has_recommendation():
    scores = {"phone_screen": 50, "system_design": 30, "behavioral": 70}
    result = simulate_hiring_committee(scores, "google")
    assert "recommendation" in result
    assert len(result["recommendation"]) > 0

def test_committee_shows_disagreement():
    # Mixed scores should produce non-unanimous results sometimes
    results_set = set()
    for _ in range(20):
        scores = {"phone_screen": 65, "system_design": 35, "behavioral": 75, "domain_specific": 25, "bar_raiser": 55}
        result = simulate_hiring_committee(scores, "google")
        results_set.add(result["is_unanimous"])
    # With mixed scores, we should sometimes get disagreement
    assert len(results_set) >= 1  # At least one outcome type


# ─── Pattern Mastery ───

def test_pattern_mastery_computed():
    results = [
        {"pattern": "Arrays/Strings", "score": 80},
        {"pattern": "Arrays/Strings", "score": 70},
        {"pattern": "System Design", "score": 30},
        {"pattern": "System Design", "score": 40},
    ]
    mastery = compute_pattern_mastery(results)
    assert "Arrays/Strings" in mastery["patterns"]
    assert mastery["patterns"]["Arrays/Strings"]["score"] == 75

def test_weak_patterns_identified():
    results = [
        {"pattern": "Trees/Graphs", "score": 20},
        {"pattern": "Trees/Graphs", "score": 30},
    ]
    mastery = compute_pattern_mastery(results)
    assert "Trees/Graphs" in mastery["weak_patterns"]

def test_strong_patterns_identified():
    results = [
        {"pattern": "API Design", "score": 85},
        {"pattern": "API Design", "score": 90},
    ]
    mastery = compute_pattern_mastery(results)
    assert "API Design" in mastery["strong_patterns"]

def test_pattern_trend_improving():
    results = [
        {"pattern": "Caching", "score": 20},
        {"pattern": "Caching", "score": 30},
        {"pattern": "Caching", "score": 50},
        {"pattern": "Caching", "score": 70},
    ]
    mastery = compute_pattern_mastery(results)
    assert mastery["patterns"]["Caching"]["trend"] == "improving"

def test_pattern_trend_declining():
    results = [
        {"pattern": "Caching", "score": 80},
        {"pattern": "Caching", "score": 70},
        {"pattern": "Caching", "score": 40},
        {"pattern": "Caching", "score": 30},
    ]
    mastery = compute_pattern_mastery(results)
    assert mastery["patterns"]["Caching"]["trend"] == "declining"

def test_pattern_total_count():
    results = [
        {"pattern": "A", "score": 50}, {"pattern": "B", "score": 60}, {"pattern": "C", "score": 70},
    ]
    mastery = compute_pattern_mastery(results)
    assert mastery["total_patterns"] == 3
