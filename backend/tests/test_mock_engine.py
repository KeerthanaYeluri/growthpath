"""Tests for Mock Interview Engine — Sprint 3"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from mock_engine import (
    generate_mock_interview, get_all_questions_flat,
    MOCK_DURATION_MINUTES, ROUND_TYPES,
)
from company_profiles import ROUND_TIME_ALLOCATION, ROUND_ANSWER_MODES


# ─── Round Structure ───

def test_mock_creates_5_rounds():
    mock = generate_mock_interview("google", "backend", "senior")
    assert len(mock["rounds"]) == 5

def test_round_1_is_phone_screen():
    mock = generate_mock_interview("google", "backend", "senior")
    assert mock["rounds"][0]["round_type"] == "phone_screen"

def test_round_2_is_system_design():
    mock = generate_mock_interview("google", "backend", "senior")
    assert mock["rounds"][1]["round_type"] == "system_design"

def test_round_3_is_behavioral():
    mock = generate_mock_interview("google", "backend", "senior")
    assert mock["rounds"][2]["round_type"] == "behavioral"

def test_round_4_is_domain_specific():
    mock = generate_mock_interview("google", "backend", "senior")
    assert mock["rounds"][3]["round_type"] == "domain_specific"

def test_round_5_is_bar_raiser():
    mock = generate_mock_interview("google", "backend", "senior")
    assert mock["rounds"][4]["round_type"] == "bar_raiser"


# ─── Time Allocation ───

def test_total_duration_is_30_minutes():
    mock = generate_mock_interview("google", "backend", "senior")
    assert mock["total_time_minutes"] == 30

def test_round_time_allocation_sums_to_30():
    total = sum(ROUND_TIME_ALLOCATION.values())
    assert total == 30

def test_phone_screen_gets_10_minutes():
    assert ROUND_TIME_ALLOCATION["phone_screen"] == 10

def test_system_design_gets_8_minutes():
    assert ROUND_TIME_ALLOCATION["system_design"] == 8

def test_behavioral_gets_5_minutes():
    assert ROUND_TIME_ALLOCATION["behavioral"] == 5

def test_domain_gets_4_minutes():
    assert ROUND_TIME_ALLOCATION["domain_specific"] == 4

def test_bar_raiser_gets_3_minutes():
    assert ROUND_TIME_ALLOCATION["bar_raiser"] == 3


# ─── Question Generation ───

def test_each_round_has_questions():
    mock = generate_mock_interview("google", "backend", "senior")
    for rnd in mock["rounds"]:
        assert len(rnd["questions"]) > 0, f"{rnd['round_type']} has no questions"

def test_total_questions_positive():
    mock = generate_mock_interview("google", "backend", "senior")
    assert mock["total_questions"] > 0

def test_questions_have_required_fields():
    mock = generate_mock_interview("google", "backend", "senior")
    for rnd in mock["rounds"]:
        for q in rnd["questions"]:
            assert "id" in q
            assert "question" in q
            assert "pattern" in q
            assert "difficulty" in q
            assert "round_type" in q
            assert "answer_mode" in q

def test_no_duplicate_question_ids():
    mock = generate_mock_interview("google", "backend", "senior")
    all_qs = get_all_questions_flat(mock)
    ids = [q["id"] for q in all_qs]
    assert len(ids) == len(set(ids))

def test_flat_questions_matches_total():
    mock = generate_mock_interview("google", "backend", "senior")
    flat = get_all_questions_flat(mock)
    assert len(flat) == mock["total_questions"]


# ─── Answer Modes ───

def test_phone_screen_mode_is_code():
    mock = generate_mock_interview("google", "backend", "senior")
    rnd = mock["rounds"][0]
    assert rnd["answer_mode"] == "code"
    for q in rnd["questions"]:
        assert q["answer_mode"] == "code"

def test_system_design_mode_is_voice():
    mock = generate_mock_interview("google", "backend", "senior")
    rnd = mock["rounds"][1]
    assert rnd["answer_mode"] == "voice"

def test_behavioral_mode_is_voice():
    mock = generate_mock_interview("google", "backend", "senior")
    rnd = mock["rounds"][2]
    assert rnd["answer_mode"] == "voice"

def test_domain_mode_is_hybrid():
    mock = generate_mock_interview("google", "backend", "senior")
    rnd = mock["rounds"][3]
    assert rnd["answer_mode"] == "hybrid"

def test_bar_raiser_mode_is_voice():
    mock = generate_mock_interview("google", "backend", "senior")
    rnd = mock["rounds"][4]
    assert rnd["answer_mode"] == "voice"


# ─── Company Specifics ───

def test_google_mock_has_company_data():
    mock = generate_mock_interview("google", "backend", "senior")
    assert mock["company"] == "google"
    assert mock["role"] == "backend"
    assert mock["level"] == "senior"

def test_apple_mock_generates_successfully():
    mock = generate_mock_interview("apple", "frontend", "mid")
    assert len(mock["rounds"]) == 5
    assert mock["company"] == "apple"

def test_rounds_have_weight():
    mock = generate_mock_interview("google", "backend", "senior")
    for rnd in mock["rounds"]:
        assert "weight" in rnd
        assert rnd["weight"] > 0

def test_rounds_have_critical_flag():
    mock = generate_mock_interview("google", "backend", "senior")
    critical_rounds = [r for r in mock["rounds"] if r["is_critical"]]
    assert len(critical_rounds) > 0  # Google has system_design as critical


# ─── Different Roles ───

def test_different_roles_produce_different_domain_questions():
    backend = generate_mock_interview("google", "backend", "senior")
    frontend = generate_mock_interview("google", "frontend", "senior")
    backend_domain = backend["rounds"][3]["questions"]
    frontend_domain = frontend["rounds"][3]["questions"]
    # At least the domain questions should differ
    backend_texts = set(q["question"] for q in backend_domain)
    frontend_texts = set(q["question"] for q in frontend_domain)
    assert backend_texts != frontend_texts
