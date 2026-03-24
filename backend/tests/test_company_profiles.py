"""Tests for Company Profiles Module — Sprint 1"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from company_profiles import (
    get_company_profile, get_hiring_bar, get_starting_elo,
    get_role_demands, get_round_config, validate_registration_fields,
    SUPPORTED_COMPANIES, SUPPORTED_ROLES, SUPPORTED_LEVELS,
    ROUND_TYPES, HIRING_BARS,
)


# ─── Company Profile Existence ───

def test_google_profile_exists():
    profile, err = get_company_profile("google")
    assert err is None
    assert profile is not None
    assert profile["name"] == "Google"

def test_apple_profile_exists():
    profile, err = get_company_profile("apple")
    assert err is None
    assert profile is not None
    assert profile["name"] == "Apple"

def test_invalid_company_returns_error():
    profile, err = get_company_profile("microsoft")
    assert profile is None
    assert "Unsupported" in err


# ─── Round Structure ───

def test_google_profile_has_all_5_rounds():
    profile, _ = get_company_profile("google")
    for rt in ROUND_TYPES:
        assert rt in profile["round_config"]

def test_apple_profile_has_all_5_rounds():
    profile, _ = get_company_profile("apple")
    for rt in ROUND_TYPES:
        assert rt in profile["round_config"]

def test_google_round_weights_sum_to_100():
    profile, _ = get_company_profile("google")
    total = sum(profile["round_weights"].values())
    assert total == 100

def test_apple_round_weights_sum_to_100():
    profile, _ = get_company_profile("apple")
    total = sum(profile["round_weights"].values())
    assert total == 100


# ─── Hiring Bars ───

def test_google_hiring_bar_l3_is_1400():
    bar, _ = get_hiring_bar("google", "junior")
    assert bar == 1400

def test_google_hiring_bar_l4_is_1600():
    bar, _ = get_hiring_bar("google", "mid")
    assert bar == 1600

def test_google_hiring_bar_l5_is_1800():
    bar, _ = get_hiring_bar("google", "senior")
    assert bar == 1800

def test_google_hiring_bar_l6_is_2000():
    bar, _ = get_hiring_bar("google", "staff")
    assert bar == 2000

def test_apple_hiring_bar_l3_is_1350():
    bar, _ = get_hiring_bar("apple", "junior")
    assert bar == 1350

def test_apple_hiring_bar_l5_is_1750():
    bar, _ = get_hiring_bar("apple", "senior")
    assert bar == 1750

def test_invalid_company_hiring_bar():
    bar, err = get_hiring_bar("netflix", "senior")
    assert bar is None
    assert err is not None

def test_invalid_level_hiring_bar():
    bar, err = get_hiring_bar("google", "intern")
    assert bar is None
    assert err is not None


# ─── Starting ELO ───

def test_starting_elo_junior():
    elo, _ = get_starting_elo("junior")
    assert elo == 1000

def test_starting_elo_senior():
    elo, _ = get_starting_elo("senior")
    assert elo == 1400

def test_starting_elo_invalid():
    elo, err = get_starting_elo("intern")
    assert elo is None
    assert err is not None


# ─── Persona Prompts ───

def test_google_persona_prompt_contains_googleyness():
    profile, _ = get_company_profile("google")
    assert "Googleyness" in profile["persona_prompt"]

def test_apple_persona_prompt_contains_design_thinking():
    profile, _ = get_company_profile("apple")
    assert "Think Different" in profile["persona_prompt"]


# ─── Round Config ───

def test_google_system_design_weight_is_highest():
    profile, _ = get_company_profile("google")
    weights = profile["round_weights"]
    assert weights["system_design"] == max(weights.values())

def test_round_config_returns_all_rounds():
    rounds, err = get_round_config("google")
    assert err is None
    assert len(rounds) == 5


# ─── Role Demands ───

def test_role_demands_backend_exists():
    demands, err = get_role_demands("backend", "senior")
    assert err is None
    assert len(demands["core_skills"]) > 0
    assert len(demands["level_skills"]) > 0

def test_role_demands_invalid_role():
    demands, err = get_role_demands("janitor", "senior")
    assert demands is None
    assert err is not None


# ─── Registration Validation ───

def test_valid_registration():
    err = validate_registration_fields("google", "backend", "senior")
    assert err is None

def test_invalid_company_registration():
    err = validate_registration_fields("netflix", "backend", "senior")
    assert err is not None

def test_invalid_role_registration():
    err = validate_registration_fields("google", "janitor", "senior")
    assert err is not None

def test_invalid_level_registration():
    err = validate_registration_fields("google", "backend", "intern")
    assert err is not None
