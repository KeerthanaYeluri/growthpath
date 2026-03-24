"""Tests for Quick Assessment Engine — Sprint 2"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from quick_assessment import generate_quick_assessment, score_assessment, compute_elo_from_assessment


# ─── Question Generation ───

def test_generates_7_to_8_questions():
    assessment = generate_quick_assessment("google", "backend", "senior")
    assert 7 <= assessment["total_questions"] <= 8

def test_questions_are_phone_screen_format():
    assessment = generate_quick_assessment("google", "backend", "senior")
    round_types = [q["round_type"] for q in assessment["questions"]]
    assert "phone_screen" in round_types

def test_questions_tagged_with_archetype_pattern():
    assessment = generate_quick_assessment("google", "backend", "senior")
    for q in assessment["questions"]:
        assert "pattern" in q
        assert q["pattern"] != ""

def test_questions_match_target_company():
    assessment = generate_quick_assessment("apple", "frontend", "mid")
    assert assessment["company"] == "apple"
    assert assessment["role"] == "frontend"

def test_no_duplicate_question_ids():
    assessment = generate_quick_assessment("google", "backend", "senior")
    ids = [q["id"] for q in assessment["questions"]]
    assert len(ids) == len(set(ids))

def test_questions_cover_multiple_round_types():
    assessment = generate_quick_assessment("google", "backend", "senior")
    round_types = set(q["round_type"] for q in assessment["questions"])
    assert len(round_types) >= 3  # At least coding, design, behavioral

def test_questions_have_answer_mode():
    assessment = generate_quick_assessment("google", "backend", "senior")
    for q in assessment["questions"]:
        assert q["answer_mode"] in ("code", "voice", "hybrid")

def test_questions_have_difficulty():
    assessment = generate_quick_assessment("google", "backend", "senior")
    for q in assessment["questions"]:
        assert q["difficulty"] in ("easy", "medium", "hard")


# ─── Scoring ───

def test_score_assessment_returns_overall():
    assessment = generate_quick_assessment("google", "backend", "senior")
    answers = [{"question_id": q["id"], "answer_text": "I would use a hash map for O(n) time complexity."} for q in assessment["questions"]]
    results = score_assessment(answers, assessment["questions"])
    assert "overall_score" in results
    assert 0 <= results["overall_score"] <= 100

def test_score_assessment_per_question():
    assessment = generate_quick_assessment("google", "backend", "senior")
    answers = [{"question_id": q["id"], "answer_text": "Let me think about this. First I would clarify requirements."} for q in assessment["questions"]]
    results = score_assessment(answers, assessment["questions"])
    assert len(results["per_question"]) == len(assessment["questions"])
    for pq in results["per_question"]:
        assert "score" in pq
        assert "quality" in pq
        assert pq["quality"] in ("strong", "average", "weak")

def test_score_assessment_per_round():
    assessment = generate_quick_assessment("google", "backend", "senior")
    answers = [{"question_id": q["id"], "answer_text": "Some answer here with hash map and O(n)."} for q in assessment["questions"]]
    results = score_assessment(answers, assessment["questions"])
    assert "per_round" in results
    assert len(results["per_round"]) > 0

def test_score_assessment_identifies_weak_patterns():
    assessment = generate_quick_assessment("google", "backend", "senior")
    # Give empty answers to get weak scores
    answers = [{"question_id": q["id"], "answer_text": "I don't know"} for q in assessment["questions"]]
    results = score_assessment(answers, assessment["questions"])
    assert "weak_patterns" in results

def test_score_assessment_recommends_focus():
    assessment = generate_quick_assessment("google", "backend", "senior")
    answers = [{"question_id": q["id"], "answer_text": "not sure"} for q in assessment["questions"]]
    results = score_assessment(answers, assessment["questions"])
    assert "recommended_focus" in results
    assert len(results["recommended_focus"]) > 0


# ─── ELO Computation ───

def test_elo_computed_from_assessment():
    assessment = generate_quick_assessment("google", "backend", "senior")
    answers = [{"question_id": q["id"], "answer_text": "Good answer with hash map and O(n) time complexity. Let me clarify the requirements first."} for q in assessment["questions"]]
    results = score_assessment(answers, assessment["questions"])

    elo_result = compute_elo_from_assessment(
        1400,
        {"phone_screen": 1400, "system_design": 1400, "behavioral": 1400, "domain_specific": 1400, "bar_raiser": 1400},
        results,
    )
    assert "overall" in elo_result
    assert "sub_elos" in elo_result
    assert elo_result["overall"]["new_elo"] > 0

def test_elo_changes_after_weak_assessment():
    assessment = generate_quick_assessment("google", "backend", "senior")
    answers = [{"question_id": q["id"], "answer_text": "no idea"} for q in assessment["questions"]]
    results = score_assessment(answers, assessment["questions"])

    elo_result = compute_elo_from_assessment(
        1400,
        {"phone_screen": 1400, "system_design": 1400, "behavioral": 1400, "domain_specific": 1400, "bar_raiser": 1400},
        results,
    )
    # Should decrease after weak answers
    assert elo_result["overall"]["delta"] < 0

def test_different_roles_generate_different_domain_questions():
    backend = generate_quick_assessment("google", "backend", "senior")
    frontend = generate_quick_assessment("google", "frontend", "senior")
    backend_qs = set(q["question"] for q in backend["questions"])
    frontend_qs = set(q["question"] for q in frontend["questions"])
    # Should have at least some different questions (domain-specific ones)
    assert backend_qs != frontend_qs
