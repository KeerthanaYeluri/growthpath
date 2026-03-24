"""
ELO Rating Module - GrowthPath v2.0
Handles ELO calculation, sub-ELO per round type, history tracking,
and readiness detection against company hiring bars.
"""

import math
from company_profiles import STARTING_ELO, HIRING_BARS, LEVEL_TO_BAR_KEY, ROUND_TYPES

# ──────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────

# K-factor controls how much ELO changes per assessment
K_FACTOR_FULL_MOCK = 32          # Standard chess K-factor
K_FACTOR_QUICK_ASSESSMENT = 40   # Higher for initial calibration
K_FACTOR_TARGETED_PRACTICE = 8   # 0.25x of full mock (32 * 0.25)

# ELO floor — never goes below this
ELO_FLOOR = 100

# Question difficulty mapped to expected ELO
DIFFICULTY_ELO_MAP = {
    "easy": 1200,
    "medium": 1500,
    "hard": 1800,
    "expert": 2100,
}

# Readiness labels
READINESS_LABELS = [
    (1200, "Not Ready", "Significant gaps across multiple rounds"),
    (1500, "Getting There", "Foundations present but major areas need work"),
    (1750, "Almost Ready", "Strong in most areas, specific weaknesses to address"),
    (1900, "Ready", "Consistently strong, minor polish needed"),
    (float("inf"), "Interview Ready", "Ready to schedule the real interview"),
]


# ──────────────────────────────────────────────
# ELO Calculation
# ──────────────────────────────────────────────

def calculate_expected_score(player_elo, opponent_elo):
    """Calculate expected score using standard ELO formula.
    Returns probability (0-1) that player wins."""
    return 1.0 / (1.0 + math.pow(10, (opponent_elo - player_elo) / 400.0))


def calculate_elo_change(current_elo, question_difficulty, score_percent, k_factor=K_FACTOR_FULL_MOCK):
    """Calculate ELO change for a single answer.

    Args:
        current_elo: User's current ELO
        question_difficulty: 'easy', 'medium', 'hard', 'expert'
        score_percent: Answer quality score 0-100 (from dual rating)
        k_factor: K-factor (varies by session type)

    Returns:
        (new_elo, delta) tuple
    """
    opponent_elo = DIFFICULTY_ELO_MAP.get(question_difficulty, 1500)
    expected = calculate_expected_score(current_elo, opponent_elo)

    # Normalize score to 0-1
    actual = score_percent / 100.0

    # ELO delta
    delta = round(k_factor * (actual - expected))

    new_elo = max(ELO_FLOOR, current_elo + delta)
    return new_elo, delta


def calculate_session_elo_change(current_elo, answers, session_type="full_mock"):
    """Calculate total ELO change for a session (multiple answers).

    Args:
        current_elo: User's current overall ELO
        answers: List of dicts with {difficulty, score_percent, round_type}
        session_type: 'full_mock', 'quick_assessment', 'targeted_practice'

    Returns:
        {
            'new_elo': int,
            'delta': int,
            'per_answer': [{'difficulty': str, 'score': float, 'delta': int}, ...]
        }
    """
    k_factor = {
        "full_mock": K_FACTOR_FULL_MOCK,
        "quick_assessment": K_FACTOR_QUICK_ASSESSMENT,
        "targeted_practice": K_FACTOR_TARGETED_PRACTICE,
    }.get(session_type, K_FACTOR_FULL_MOCK)

    running_elo = current_elo
    per_answer = []

    for answer in answers:
        new_elo, delta = calculate_elo_change(
            running_elo,
            answer.get("difficulty", "medium"),
            answer.get("score_percent", 50),
            k_factor,
        )
        per_answer.append({
            "difficulty": answer.get("difficulty", "medium"),
            "score": answer.get("score_percent", 50),
            "delta": delta,
            "round_type": answer.get("round_type"),
        })
        running_elo = new_elo

    total_delta = running_elo - current_elo

    return {
        "new_elo": running_elo,
        "delta": total_delta,
        "per_answer": per_answer,
    }


def calculate_sub_elo_changes(sub_elos, answers, session_type="full_mock"):
    """Calculate ELO changes per round type (sub-ELOs).

    Args:
        sub_elos: Dict of {round_type: current_elo}
        answers: List of dicts with {difficulty, score_percent, round_type}
        session_type: Session type for K-factor

    Returns:
        Dict of {round_type: {'new_elo': int, 'delta': int}}
    """
    k_factor = {
        "full_mock": K_FACTOR_FULL_MOCK,
        "quick_assessment": K_FACTOR_QUICK_ASSESSMENT,
        "targeted_practice": K_FACTOR_TARGETED_PRACTICE,
    }.get(session_type, K_FACTOR_FULL_MOCK)

    changes = {}

    # Group answers by round type
    by_round = {}
    for answer in answers:
        rt = answer.get("round_type")
        if rt:
            by_round.setdefault(rt, []).append(answer)

    for round_type, round_answers in by_round.items():
        current = sub_elos.get(round_type, 1200)
        running = current

        for answer in round_answers:
            new_elo, _ = calculate_elo_change(
                running,
                answer.get("difficulty", "medium"),
                answer.get("score_percent", 50),
                k_factor,
            )
            running = new_elo

        changes[round_type] = {
            "new_elo": running,
            "delta": running - current,
        }

    return changes


# ──────────────────────────────────────────────
# ELO State Management
# ──────────────────────────────────────────────

def create_initial_elo(level):
    """Create initial ELO state for a new user.

    Args:
        level: 'junior', 'mid', 'senior', 'staff'

    Returns:
        {
            'overall': int,
            'sub_elos': {round_type: int for each round},
            'history': []
        }
    """
    starting = STARTING_ELO.get(level.lower(), 1200)

    return {
        "overall": starting,
        "sub_elos": {rt: starting for rt in ROUND_TYPES},
        "history": [],
    }


def get_readiness_label(elo):
    """Get readiness label for an ELO score.

    Returns:
        {'label': str, 'description': str}
    """
    for threshold, label, desc in READINESS_LABELS:
        if elo < threshold:
            return {"label": label, "description": desc}
    return {"label": "Interview Ready", "description": "Ready to schedule the real interview"}


def check_interview_ready(elo, company, level):
    """Check if user's ELO meets the hiring bar.

    Returns:
        {
            'is_ready': bool,
            'current_elo': int,
            'hiring_bar': int,
            'gap': int,
            'readiness': {'label': str, 'description': str}
        }
    """
    company = company.lower()
    level = level.lower()

    bar_key = LEVEL_TO_BAR_KEY.get(level, "L5")
    hiring_bar = HIRING_BARS.get(company, {}).get(bar_key, 1800)

    gap = max(0, hiring_bar - elo)
    readiness = get_readiness_label(elo)

    return {
        "is_ready": elo >= hiring_bar,
        "current_elo": elo,
        "hiring_bar": hiring_bar,
        "gap": gap,
        "readiness": readiness,
    }


def build_elo_history_entry(session_id, session_type, old_elo, new_elo, delta, round_deltas=None):
    """Create an ELO history entry for recording.

    Returns:
        Dict ready to be stored in elo_history
    """
    from datetime import datetime, timezone

    return {
        "session_id": session_id,
        "session_type": session_type,
        "old_elo": old_elo,
        "new_elo": new_elo,
        "delta": delta,
        "round_deltas": round_deltas or {},
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
