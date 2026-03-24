"""
Dual Rating Scorer - GrowthPath v2.0
Implements Thinking Process (60%) + Accuracy (40%) scoring.
Replaces flat keyword-match scoring from v1.
"""

import re

# ──────────────────────────────────────────────
# Thinking Process Indicators (60% total)
# ──────────────────────────────────────────────

CLARIFYING_PATTERNS = [
    r"(?:let me|i would|i\'d)\s+(?:clarify|ask|confirm|understand)",
    r"(?:what|how|which|does|is|are|can)\s+.{5,}\?",
    r"(?:assuming|assumption|if we assume|let\'s assume)",
    r"(?:requirements?|constraints?|scope|specifications?)",
    r"(?:before .{3,}, (?:let me|i\'d|i want to))",
    r"(?:first,?\s+i(?:\'d| would)\s+(?:want to|need to|like to)\s+understand)",
]

MULTIPLE_APPROACH_PATTERNS = [
    r"(?:one approach|another approach|alternatively|option \d|approach \d)",
    r"(?:we could (?:also|either)|there are (?:several|multiple|different))",
    r"(?:trade.?off|pros? and cons?|advantages? (?:and|vs) disadvantages?)",
    r"(?:compared to|versus|vs\.?|on the other hand)",
    r"(?:first option|second option|plan [ab]|solution [12])",
    r"(?:brute force .{3,} then .{3,} optimize)",
]

TRADEOFF_PATTERNS = [
    r"(?:trade.?off|trade off|tradeoff)",
    r"(?:(?:but|however|although|while)\s+(?:this|it|that)\s+(?:comes with|has|means|sacrifices))",
    r"(?:at the (?:cost|expense) of|sacrifice|compromise)",
    r"(?:scalab|latency|throughput|consistency|availability|partition tolerance)",
    r"(?:time complexity|space complexity|big[- ]?o)",
    r"(?:read.heavy|write.heavy|eventual.consistency|strong.consistency)",
    r"(?:monolith|microservice|serverless).{3,}(?:advantage|disadvantage|trade)",
]

STRUCTURED_COMM_PATTERNS = [
    r"(?:first(?:ly)?|second(?:ly)?|third(?:ly)?|finally|in summary|to summarize|in conclusion)",
    r"(?:step \d|phase \d|stage \d)",
    r"(?:the (?:key|main|important|critical) (?:point|thing|aspect|factor)s?\s+(?:are|is|include))",
    r"(?:let me (?:break|walk|explain|outline|structure))",
    r"(?:at a high level|the overall approach|the architecture)",
    r"(?:to begin|moving on|next,?\s+)",
]


def _count_pattern_matches(text, patterns):
    """Count how many distinct patterns match in text."""
    text_lower = text.lower()
    count = 0
    for pattern in patterns:
        if re.search(pattern, text_lower):
            count += 1
    return count


def score_thinking_process(answer_text):
    """Score the thinking process of an answer (0-100).

    Returns:
        {
            'total': 0-100,
            'clarifying_questions': 0-100,
            'multiple_approaches': 0-100,
            'tradeoff_awareness': 0-100,
            'structured_communication': 0-100,
        }
    """
    if not answer_text or len(answer_text.strip()) < 10:
        return {"total": 0, "clarifying_questions": 0, "multiple_approaches": 0,
                "tradeoff_awareness": 0, "structured_communication": 0}

    text = answer_text.strip()

    # Clarifying questions (0-100)
    cq_matches = _count_pattern_matches(text, CLARIFYING_PATTERNS)
    cq_score = min(100, cq_matches * 35)

    # Multiple approaches (0-100)
    ma_matches = _count_pattern_matches(text, MULTIPLE_APPROACH_PATTERNS)
    ma_score = min(100, ma_matches * 30)

    # Trade-off awareness (0-100)
    to_matches = _count_pattern_matches(text, TRADEOFF_PATTERNS)
    to_score = min(100, to_matches * 30)

    # Structured communication (0-100)
    sc_matches = _count_pattern_matches(text, STRUCTURED_COMM_PATTERNS)
    sc_score = min(100, sc_matches * 25)

    # Total: equal weight (each 25% of thinking total)
    total = round((cq_score + ma_score + to_score + sc_score) / 4)

    return {
        "total": total,
        "clarifying_questions": cq_score,
        "multiple_approaches": ma_score,
        "tradeoff_awareness": to_score,
        "structured_communication": sc_score,
    }


# ──────────────────────────────────────────────
# Accuracy Score (40% total)
# ──────────────────────────────────────────────

def score_accuracy(answer_text, expected_keywords=None, rubric_points=None):
    """Score the accuracy of an answer (0-100).

    Args:
        answer_text: User's answer
        expected_keywords: List of expected technical keywords
        rubric_points: List of expected points to cover

    Returns:
        {
            'total': 0-100,
            'correctness': 0-100,
            'completeness': 0-100,
            'matched_keywords': [],
            'missed_keywords': [],
            'covered_points': [],
            'missed_points': [],
        }
    """
    if not answer_text or len(answer_text.strip()) < 10:
        return {"total": 0, "correctness": 0, "completeness": 0,
                "matched_keywords": [], "missed_keywords": expected_keywords or [],
                "covered_points": [], "missed_points": rubric_points or []}

    text_lower = answer_text.lower()
    words = set(re.findall(r'\b\w+\b', text_lower))

    # Keyword matching (correctness proxy)
    keywords = expected_keywords or []
    matched = []
    missed = []
    for kw in keywords:
        kw_lower = kw.lower()
        kw_words = set(re.findall(r'\b\w+\b', kw_lower))
        if kw_words.issubset(words) or kw_lower in text_lower:
            matched.append(kw)
        else:
            missed.append(kw)

    correctness = round((len(matched) / len(keywords)) * 100) if keywords else 50

    # Rubric point coverage (completeness)
    points = rubric_points or []
    covered = []
    missed_points = []
    for point in points:
        point_lower = point.lower()
        point_words = set(re.findall(r'\b\w+\b', point_lower))
        # Check if at least 40% of point's words appear in answer
        if point_words:
            overlap = len(point_words & words) / len(point_words)
            if overlap >= 0.4 or point_lower in text_lower:
                covered.append(point)
            else:
                missed_points.append(point)
        else:
            missed_points.append(point)

    completeness = round((len(covered) / len(points)) * 100) if points else _estimate_completeness(text_lower)

    total = round((correctness + completeness) / 2)

    return {
        "total": total,
        "correctness": correctness,
        "completeness": completeness,
        "matched_keywords": matched,
        "missed_keywords": missed,
        "covered_points": covered,
        "missed_points": missed_points,
    }


def _estimate_completeness(text):
    """Estimate completeness when no rubric points provided, based on answer depth."""
    word_count = len(text.split())
    if word_count >= 200:
        return 90
    elif word_count >= 120:
        return 75
    elif word_count >= 60:
        return 55
    elif word_count >= 30:
        return 35
    else:
        return 15


# ──────────────────────────────────────────────
# Dual Score Combiner
# ──────────────────────────────────────────────

def dual_score(answer_text, expected_keywords=None, rubric_points=None):
    """Compute the full dual score: Thinking (60%) + Accuracy (40%).

    Returns:
        {
            'total_score': 0-100,
            'thinking': {sub-scores},
            'accuracy': {sub-scores},
            'thinking_weighted': 0-60,
            'accuracy_weighted': 0-40,
            'rating': 1-5,
        }
    """
    thinking = score_thinking_process(answer_text)
    accuracy = score_accuracy(answer_text, expected_keywords, rubric_points)

    thinking_weighted = round(thinking["total"] * 0.6)
    accuracy_weighted = round(accuracy["total"] * 0.4)
    total = thinking_weighted + accuracy_weighted

    # Rating 1-5 from total score
    if total >= 80:
        rating = 5
    elif total >= 60:
        rating = 4
    elif total >= 40:
        rating = 3
    elif total >= 20:
        rating = 2
    else:
        rating = 1

    return {
        "total_score": total,
        "thinking": thinking,
        "accuracy": accuracy,
        "thinking_weighted": thinking_weighted,
        "accuracy_weighted": accuracy_weighted,
        "rating": rating,
    }


# ──────────────────────────────────────────────
# Answer Quality Classifier (for probe tree branching)
# ──────────────────────────────────────────────

def classify_answer_quality(score_percent):
    """Classify answer quality for probe tree branching.

    Returns: 'strong', 'average', or 'weak'
    """
    if score_percent >= 70:
        return "strong"
    elif score_percent >= 40:
        return "average"
    else:
        return "weak"
