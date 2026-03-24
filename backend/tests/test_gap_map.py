"""Tests for Gap Map Engine — Sprint 1"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from gap_map import generate_gap_map


# ─── Basic Gap Map Generation ───

def test_gap_map_identifies_strength_areas():
    gap_map, err = generate_gap_map(
        ["Python", "Flask", "PostgreSQL", "Docker"],
        "backend", "senior"
    )
    assert err is None
    assert len(gap_map["strengths"]) > 0

def test_gap_map_identifies_gap_areas():
    gap_map, err = generate_gap_map(
        ["Python"],
        "backend", "senior"
    )
    assert err is None
    assert len(gap_map["gaps"]) > 0

def test_gap_map_identifies_cross_cutting_concerns():
    gap_map, err = generate_gap_map(
        ["Python"],
        "backend", "senior"
    )
    assert err is None
    assert len(gap_map["cross_cutting"]) > 0

def test_gap_map_empty_tech_stack_all_gaps():
    gap_map, err = generate_gap_map([], "backend", "senior")
    assert err is None
    assert gap_map["covered_demands"] == 0
    assert gap_map["gap_demands"] > 0
    assert gap_map["coverage_percent"] == 0

def test_gap_map_returns_role_specific_demands():
    gap_map, err = generate_gap_map(["React"], "frontend", "mid")
    assert err is None
    assert gap_map["role"] == "frontend"
    assert gap_map["level"] == "mid"

def test_gap_map_coverage_percent():
    gap_map, err = generate_gap_map(
        ["Python", "Flask", "SQL", "Docker", "System Design", "REST API"],
        "backend", "junior"
    )
    assert err is None
    assert 0 <= gap_map["coverage_percent"] <= 100

def test_gap_map_python_backend_has_frontend_gap():
    gap_map, err = generate_gap_map(
        ["Python", "Flask", "SQL"],
        "fullstack", "mid"
    )
    assert err is None
    gap_skills = [g["skill"] for g in gap_map["gaps"]]
    # Fullstack should show frontend gaps for a Python-only dev
    assert any("React" in s or "Frontend" in s or "State" in s for s in gap_skills)

def test_gap_map_invalid_role():
    gap_map, err = generate_gap_map(["Python"], "janitor", "senior")
    assert gap_map is None
    assert err is not None

def test_gap_map_level_affects_demand_depth():
    gap_junior, _ = generate_gap_map(["Python"], "backend", "junior")
    gap_senior, _ = generate_gap_map(["Python"], "backend", "senior")
    # Senior should have more total demands than junior
    assert gap_senior["total_demands"] >= gap_junior["total_demands"]

def test_gap_map_high_priority_for_core_skills():
    gap_map, _ = generate_gap_map([], "backend", "senior")
    high_priority = [g for g in gap_map["gaps"] if g["priority"] == "high"]
    assert len(high_priority) > 0
