"""Tests for ELO Rating Module — Sprint 1"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from elo_rating import (
    calculate_elo_change,
    calculate_session_elo_change,
    calculate_sub_elo_changes,
    create_initial_elo,
    get_readiness_label,
    check_interview_ready,
    ELO_FLOOR,
    K_FACTOR_FULL_MOCK,
    K_FACTOR_TARGETED_PRACTICE,
)


# ─── Starting ELO ───

def test_starting_elo_junior_returns_1000():
    elo = create_initial_elo("junior")
    assert elo["overall"] == 1000

def test_starting_elo_mid_returns_1200():
    elo = create_initial_elo("mid")
    assert elo["overall"] == 1200

def test_starting_elo_senior_returns_1400():
    elo = create_initial_elo("senior")
    assert elo["overall"] == 1400

def test_starting_elo_staff_returns_1600():
    elo = create_initial_elo("staff")
    assert elo["overall"] == 1600

def test_starting_elo_creates_sub_elos():
    elo = create_initial_elo("mid")
    assert "sub_elos" in elo
    assert elo["sub_elos"]["phone_screen"] == 1200
    assert elo["sub_elos"]["system_design"] == 1200
    assert elo["sub_elos"]["behavioral"] == 1200
    assert elo["sub_elos"]["domain_specific"] == 1200
    assert elo["sub_elos"]["bar_raiser"] == 1200


# ─── ELO Calculation ───

def test_elo_gain_strong_answer_hard_question():
    new_elo, delta = calculate_elo_change(1200, "hard", 90)
    assert delta > 0
    assert new_elo > 1200

def test_elo_gain_average_answer_matching_question():
    new_elo, delta = calculate_elo_change(1500, "medium", 50)
    # At matching difficulty, 50% score ≈ expected, small change
    assert abs(delta) <= 10

def test_elo_loss_weak_answer_easy_question():
    new_elo, delta = calculate_elo_change(1500, "easy", 20)
    assert delta < 0
    assert new_elo < 1500

def test_elo_no_negative():
    new_elo, delta = calculate_elo_change(ELO_FLOOR + 5, "hard", 0)
    assert new_elo >= ELO_FLOOR

def test_elo_adjustment_range():
    # Strong answer on hard question — should gain
    _, delta_gain = calculate_elo_change(1200, "hard", 95, K_FACTOR_FULL_MOCK)
    assert 5 <= delta_gain <= 50

    # Weak answer on easy question — should lose
    _, delta_loss = calculate_elo_change(1500, "easy", 10, K_FACTOR_FULL_MOCK)
    assert -40 <= delta_loss <= -5


# ─── Sub-ELO ───

def test_sub_elo_coding_updates_independently():
    sub_elos = {"phone_screen": 1200, "system_design": 1200, "behavioral": 1200,
                "domain_specific": 1200, "bar_raiser": 1200}
    answers = [{"difficulty": "medium", "score_percent": 90, "round_type": "phone_screen"}]
    changes = calculate_sub_elo_changes(sub_elos, answers)
    assert "phone_screen" in changes
    assert changes["phone_screen"]["delta"] > 0
    assert "system_design" not in changes  # Untouched

def test_sub_elo_system_design_updates_independently():
    sub_elos = {"phone_screen": 1200, "system_design": 1200, "behavioral": 1200,
                "domain_specific": 1200, "bar_raiser": 1200}
    answers = [{"difficulty": "hard", "score_percent": 80, "round_type": "system_design"}]
    changes = calculate_sub_elo_changes(sub_elos, answers)
    assert "system_design" in changes
    assert changes["system_design"]["delta"] > 0


# ─── Targeted Practice Multiplier ───

def test_targeted_practice_elo_multiplier_0_25x():
    # Full mock K-factor = 32, targeted = 8 (0.25x)
    _, delta_full = calculate_elo_change(1200, "medium", 80, K_FACTOR_FULL_MOCK)
    _, delta_targeted = calculate_elo_change(1200, "medium", 80, K_FACTOR_TARGETED_PRACTICE)
    assert abs(delta_targeted) < abs(delta_full)
    # The ratio should be approximately 0.25
    if delta_full != 0:
        ratio = abs(delta_targeted) / abs(delta_full)
        assert 0.2 <= ratio <= 0.3

def test_full_mock_elo_multiplier_1x():
    result = calculate_session_elo_change(1200, [
        {"difficulty": "medium", "score_percent": 70, "round_type": "phone_screen"},
    ], session_type="full_mock")
    assert result["delta"] != 0  # Should have some change


# ─── Session ELO Change ───

def test_session_elo_change_multiple_answers():
    answers = [
        {"difficulty": "easy", "score_percent": 90, "round_type": "phone_screen"},
        {"difficulty": "medium", "score_percent": 70, "round_type": "system_design"},
        {"difficulty": "hard", "score_percent": 50, "round_type": "behavioral"},
    ]
    result = calculate_session_elo_change(1200, answers, "full_mock")
    assert "new_elo" in result
    assert "delta" in result
    assert "per_answer" in result
    assert len(result["per_answer"]) == 3


# ─── Readiness Labels ───

def test_readiness_label_not_ready():
    label = get_readiness_label(1100)
    assert label["label"] == "Not Ready"

def test_readiness_label_getting_there():
    label = get_readiness_label(1300)
    assert label["label"] == "Getting There"

def test_readiness_label_almost_ready():
    label = get_readiness_label(1600)
    assert label["label"] == "Almost Ready"

def test_readiness_label_ready():
    label = get_readiness_label(1800)
    assert label["label"] == "Ready"

def test_readiness_label_interview_ready():
    label = get_readiness_label(1950)
    assert label["label"] == "Interview Ready"


# ─── Interview Ready Check ───

def test_interview_ready_check_not_ready():
    result = check_interview_ready(1400, "google", "senior")
    assert result["is_ready"] is False
    assert result["hiring_bar"] == 1800
    assert result["gap"] == 400

def test_interview_ready_check_ready():
    result = check_interview_ready(1850, "google", "senior")
    assert result["is_ready"] is True
    assert result["gap"] == 0

def test_interview_ready_apple():
    result = check_interview_ready(1750, "apple", "senior")
    assert result["is_ready"] is True
    assert result["hiring_bar"] == 1750
