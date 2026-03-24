"""
Rubric Reveal + Hiring Committee + Pattern Tracking - GrowthPath v2.0 (Sprint 5-6)
Post-question rubric reveal, hiring committee simulation,
and archetype pattern mastery tracking.
"""

import random
from dual_scorer import dual_score
from company_profiles import get_company_profile, ROUND_LABELS

# ──────────────────────────────────────────────
# Rubric Reveal
# ──────────────────────────────────────────────

def generate_rubric_reveal(question, answer_text):
    """Generate rubric reveal showing what interviewer was evaluating.

    Returns:
        {
            'question': str,
            'rubric_points': [{'point': str, 'covered': bool}, ...],
            'covered_count': int,
            'total_count': int,
            'keywords_matched': [],
            'keywords_missed': [],
            'thinking_breakdown': {},
            'accuracy_breakdown': {},
        }
    """
    rubric_points = question.get("rubric", [])
    keywords = question.get("keywords", [])

    score_result = dual_score(answer_text, expected_keywords=keywords, rubric_points=rubric_points)

    covered = score_result["accuracy"]["covered_points"]
    missed = score_result["accuracy"]["missed_points"]

    point_results = []
    for point in rubric_points:
        point_results.append({
            "point": point,
            "covered": point in covered,
        })

    return {
        "question": question.get("question", ""),
        "pattern": question.get("pattern", ""),
        "rubric_points": point_results,
        "covered_count": len(covered),
        "total_count": len(rubric_points),
        "keywords_matched": score_result["accuracy"]["matched_keywords"],
        "keywords_missed": score_result["accuracy"]["missed_keywords"],
        "thinking_breakdown": score_result["thinking"],
        "accuracy_breakdown": {
            "correctness": score_result["accuracy"]["correctness"],
            "completeness": score_result["accuracy"]["completeness"],
        },
        "total_score": score_result["total_score"],
        "rating": score_result["rating"],
    }


def generate_all_rubric_reveals(questions, answers_map):
    """Generate rubric reveals for all questions.

    Args:
        questions: List of question dicts
        answers_map: Dict of {question_id: answer_text}

    Returns:
        List of rubric reveal dicts
    """
    reveals = []
    for q in questions:
        answer = answers_map.get(q.get("id"), "")
        reveal = generate_rubric_reveal(q, answer)
        reveal["question_id"] = q.get("id")
        reveals.append(reveal)
    return reveals


# ──────────────────────────────────────────────
# Hiring Committee Simulation
# ──────────────────────────────────────────────

INTERVIEWER_NAMES = [
    {"name": "Alex Chen", "title": "Senior Staff Engineer"},
    {"name": "Sarah Mitchell", "title": "Engineering Manager"},
    {"name": "Raj Patel", "title": "Principal Engineer"},
    {"name": "Emily Rodriguez", "title": "Tech Lead"},
    {"name": "David Kim", "title": "Distinguished Engineer"},
    {"name": "Lisa Zhang", "title": "Senior Engineering Manager"},
]

VOTE_OPTIONS = ["STRONG_HIRE", "HIRE", "LEAN_HIRE", "LEAN_NO_HIRE", "NO_HIRE", "STRONG_NO_HIRE"]

POSITIVE_QUOTES = [
    "demonstrated strong {trait} during the {round} round",
    "showed excellent depth when discussing {topic}",
    "clearly articulated trade-offs in their approach",
    "asked great clarifying questions before diving in",
    "structured their response very well",
    "showed maturity in handling the follow-up probes",
]

NEGATIVE_QUOTES = [
    "struggled with {topic} fundamentals in the {round} round",
    "didn't consider scalability in their design",
    "jumped to coding without planning",
    "missed key trade-offs in their approach",
    "gave surface-level answers without depth",
    "couldn't articulate their reasoning clearly",
    "needed multiple hints to make progress",
]


def _generate_vote(round_score, is_critical):
    """Generate a committee vote based on round score."""
    if round_score >= 80:
        return random.choice(["STRONG_HIRE", "HIRE"])
    elif round_score >= 60:
        return random.choice(["HIRE", "LEAN_HIRE"])
    elif round_score >= 45:
        return "LEAN_HIRE" if not is_critical else "LEAN_NO_HIRE"
    elif round_score >= 30:
        return "LEAN_NO_HIRE"
    else:
        return random.choice(["NO_HIRE", "STRONG_NO_HIRE"])


def _generate_quote(round_score, round_type, pattern=""):
    """Generate an interviewer quote about the candidate."""
    round_label = ROUND_LABELS.get(round_type, round_type)

    if round_score >= 60:
        template = random.choice(POSITIVE_QUOTES)
        traits = ["problem-solving", "technical depth", "communication", "design thinking", "analytical skills"]
        return "Candidate " + template.format(
            trait=random.choice(traits), round=round_label, topic=pattern or round_label
        )
    else:
        template = random.choice(NEGATIVE_QUOTES)
        return "Candidate " + template.format(
            round=round_label, topic=pattern or round_label
        )


def simulate_hiring_committee(round_scores, company, critical_rounds=None):
    """Simulate a 3-person hiring committee deliberation.

    Args:
        round_scores: Dict of {round_type: score}
        company: Target company
        critical_rounds: List of critical round types

    Returns:
        {
            'interviewers': [
                {
                    'name': str, 'title': str,
                    'assigned_rounds': [str],
                    'vote': str,
                    'reasoning': str,
                    'quotes': [str],
                }, ...
            ],
            'verdict': 'HIRE'|'NO_HIRE'|'LEAN_HIRE'|'LEAN_NO_HIRE',
            'verdict_label': str,
            'is_unanimous': bool,
            'veto_applied': bool,
            'recommendation': str,
        }
    """
    profile, _ = get_company_profile(company)
    if not critical_rounds:
        critical_rounds = profile.get("critical_rounds", []) if profile else []

    # Select 3 interviewers
    selected = random.sample(INTERVIEWER_NAMES, 3)

    # Assign rounds to interviewers
    all_rounds = list(round_scores.keys())
    random.shuffle(all_rounds)

    assignments = [[], [], []]
    for i, rt in enumerate(all_rounds):
        assignments[i % 3].append(rt)

    interviewers = []
    votes = []

    for i, interviewer in enumerate(selected):
        assigned = assignments[i]
        if not assigned:
            assigned = [random.choice(all_rounds)]

        # Average score of assigned rounds
        avg_score = round(sum(round_scores.get(rt, 50) for rt in assigned) / len(assigned))

        # Check if any assigned round is critical
        has_critical = any(rt in critical_rounds for rt in assigned)

        vote = _generate_vote(avg_score, has_critical)
        votes.append(vote)

        # Generate quotes
        quotes = []
        for rt in assigned:
            score = round_scores.get(rt, 50)
            quotes.append(_generate_quote(score, rt))

        # Reasoning
        if "HIRE" in vote and "NO" not in vote:
            reasoning = f"Based on the {', '.join(ROUND_LABELS.get(r, r) for r in assigned)} round{'s' if len(assigned)>1 else ''}, I believe this candidate meets the bar."
        else:
            weak_rounds = [ROUND_LABELS.get(r, r) for r in assigned if round_scores.get(r, 50) < 50]
            reasoning = f"I have concerns about performance in {', '.join(weak_rounds) if weak_rounds else 'the assigned rounds'}."

        interviewers.append({
            "name": interviewer["name"],
            "title": interviewer["title"],
            "assigned_rounds": assigned,
            "assigned_round_labels": [ROUND_LABELS.get(r, r) for r in assigned],
            "vote": vote,
            "score": avg_score,
            "reasoning": reasoning,
            "quotes": quotes,
        })

    # Committee decision
    hire_votes = sum(1 for v in votes if "HIRE" in v and "NO" not in v)
    no_hire_votes = sum(1 for v in votes if "NO_HIRE" in v or "NO" in v)

    # Veto check: strong NO_HIRE on a critical round
    veto_applied = False
    for inv in interviewers:
        if inv["vote"] in ("STRONG_NO_HIRE", "NO_HIRE"):
            if any(rt in critical_rounds for rt in inv["assigned_rounds"]):
                veto_applied = True
                break

    # Determine verdict
    if veto_applied:
        verdict = "NO_HIRE"
        verdict_label = "NO HIRE (Veto on critical round)"
    elif hire_votes >= 2:
        verdict = "HIRE" if hire_votes == 3 else "LEAN_HIRE"
        verdict_label = "STRONG HIRE" if hire_votes == 3 else "LEAN HIRE"
    elif no_hire_votes >= 2:
        verdict = "NO_HIRE" if no_hire_votes == 3 else "LEAN_NO_HIRE"
        verdict_label = "STRONG NO HIRE" if no_hire_votes == 3 else "LEAN NO HIRE"
    else:
        verdict = "LEAN_HIRE" if hire_votes > no_hire_votes else "LEAN_NO_HIRE"
        verdict_label = "LEAN HIRE (split decision)" if hire_votes > no_hire_votes else "LEAN NO HIRE (split decision)"

    # Recommendation
    weak_areas = [ROUND_LABELS.get(rt, rt) for rt, s in round_scores.items() if s < 50]
    if verdict in ("HIRE", "LEAN_HIRE"):
        recommendation = "Candidate shows readiness. " + (f"Minor improvement needed in: {', '.join(weak_areas)}." if weak_areas else "Strong across all rounds.")
    else:
        recommendation = f"Focus on improving: {', '.join(weak_areas)}." if weak_areas else "Need stronger performance across all rounds."

    return {
        "interviewers": interviewers,
        "verdict": verdict,
        "verdict_label": verdict_label,
        "is_unanimous": len(set(votes)) == 1,
        "veto_applied": veto_applied,
        "recommendation": recommendation,
        "hire_votes": hire_votes,
        "no_hire_votes": no_hire_votes,
    }


# ──────────────────────────────────────────────
# Pattern Mastery Tracking
# ──────────────────────────────────────────────

def compute_pattern_mastery(all_question_results):
    """Compute mastery per archetype pattern from question results.

    Args:
        all_question_results: List of {pattern, score, ...} from assessments

    Returns:
        {
            'patterns': {pattern_name: {'score': avg, 'count': n, 'trend': 'improving'|'declining'|'stable'}},
            'weak_patterns': [patterns with score < 50],
            'strong_patterns': [patterns with score >= 70],
            'total_patterns': int,
        }
    """
    by_pattern = {}
    for r in all_question_results:
        pattern = r.get("pattern", "Unknown")
        by_pattern.setdefault(pattern, []).append(r.get("score", 0))

    patterns = {}
    weak = []
    strong = []

    for pattern, scores in by_pattern.items():
        avg = round(sum(scores) / len(scores))
        # Trend: compare first half to second half
        if len(scores) >= 4:
            mid = len(scores) // 2
            first_half = sum(scores[:mid]) / mid
            second_half = sum(scores[mid:]) / (len(scores) - mid)
            if second_half > first_half + 5:
                trend = "improving"
            elif second_half < first_half - 5:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "stable"

        patterns[pattern] = {"score": avg, "count": len(scores), "trend": trend}

        if avg < 50:
            weak.append(pattern)
        if avg >= 70:
            strong.append(pattern)

    return {
        "patterns": patterns,
        "weak_patterns": sorted(weak),
        "strong_patterns": sorted(strong),
        "total_patterns": len(patterns),
    }
