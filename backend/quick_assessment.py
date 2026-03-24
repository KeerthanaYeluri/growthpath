"""
Quick Assessment Engine - GrowthPath v2.0
Generates 5-10 diagnostic questions for new users,
scores answers, assigns starting ELO, and generates
learning path from failures.
"""

import random
from datetime import datetime, timezone
from company_profiles import (
    get_company_profile, get_role_demands, ROUND_TYPES,
    LEVEL_TO_BAR_KEY, HIRING_BARS,
)
from elo_rating import (
    create_initial_elo, calculate_session_elo_change,
    calculate_sub_elo_changes, check_interview_ready,
)
from dual_scorer import dual_score, classify_answer_quality

# ──────────────────────────────────────────────
# Question Archetype Patterns
# ──────────────────────────────────────────────

ARCHETYPE_PATTERNS = {
    "system_design": [
        "Scalability Trade-offs", "Data Modeling", "API Design",
        "Caching Strategy", "Message Queues", "Load Balancing", "Database Selection",
    ],
    "coding": [
        "Arrays/Strings", "Trees/Graphs", "Dynamic Programming",
        "Sliding Window", "Binary Search", "Recursion/Backtracking", "Sorting",
    ],
    "behavioral": [
        "Conflict Resolution", "Failure/Recovery", "Leadership/Influence",
        "Ambiguity Handling", "Ownership", "Collaboration",
    ],
    "domain": {
        "backend": ["REST API Design", "Database Optimization", "Concurrency", "Microservices Architecture"],
        "frontend": ["Component Architecture", "State Management", "Performance Optimization", "Responsive Design"],
        "fullstack": ["Full Stack Architecture", "API Integration", "Deployment Pipeline", "Database Design"],
        "devops_sre": ["CI/CD Pipeline", "Container Orchestration", "Monitoring Strategy", "Incident Response"],
        "data_engineer": ["Data Pipeline Design", "Data Modeling", "Stream Processing", "Data Quality"],
        "ml_engineer": ["Model Training Pipeline", "Feature Engineering", "Model Serving", "Experiment Design"],
        "mobile": ["Mobile Architecture", "Offline Storage", "Performance Optimization", "UI Patterns"],
        "platform": ["Platform Architecture", "SDK Design", "Multi-tenancy", "Service Reliability"],
    },
}

# ──────────────────────────────────────────────
# Quick Assessment Question Templates
# ──────────────────────────────────────────────

QUESTION_TEMPLATES = {
    "phone_screen": {
        "coding": [
            {
                "question": "Given an array of integers, find two numbers that add up to a specific target. Explain your approach and its time complexity.",
                "keywords": ["hash map", "hash table", "dictionary", "O(n)", "two pass", "complement", "time complexity"],
                "rubric": ["Identify brute force O(n^2)", "Optimize with hash map", "Handle edge cases", "Analyze time/space complexity"],
                "pattern": "Arrays/Strings",
                "difficulty": "medium",
            },
            {
                "question": "How would you detect if a linked list has a cycle? Describe multiple approaches.",
                "keywords": ["fast pointer", "slow pointer", "Floyd", "hash set", "O(1) space", "tortoise", "hare"],
                "rubric": ["Hash set approach", "Two-pointer (Floyd's) approach", "Compare time/space trade-offs", "Edge cases"],
                "pattern": "Arrays/Strings",
                "difficulty": "medium",
            },
            {
                "question": "Explain how you would reverse a binary tree. What's the time and space complexity?",
                "keywords": ["recursive", "iterative", "queue", "BFS", "DFS", "O(n)", "swap", "left", "right"],
                "rubric": ["Recursive approach", "Iterative approach", "Time complexity O(n)", "Space complexity analysis"],
                "pattern": "Trees/Graphs",
                "difficulty": "easy",
            },
            {
                "question": "Given a string, find the longest substring without repeating characters. Walk through your approach.",
                "keywords": ["sliding window", "hash map", "set", "two pointers", "O(n)", "substring"],
                "rubric": ["Identify sliding window pattern", "Track character positions", "Handle window shrinking", "Optimal O(n) solution"],
                "pattern": "Sliding Window",
                "difficulty": "medium",
            },
            {
                "question": "Implement a function to check if a string is a valid palindrome, considering only alphanumeric characters. What's your approach?",
                "keywords": ["two pointers", "alphanumeric", "case insensitive", "O(n)", "O(1) space", "reverse"],
                "rubric": ["Two-pointer approach", "Handle non-alphanumeric chars", "Case handling", "Time/space analysis"],
                "pattern": "Arrays/Strings",
                "difficulty": "easy",
            },
        ],
    },
    "system_design": {
        "architecture": [
            {
                "question": "Design a URL shortening service like bit.ly. How would you handle high traffic?",
                "keywords": ["hash", "base62", "database", "cache", "redirect", "301", "302", "scalability", "sharding"],
                "rubric": ["Generate short URLs (hashing/encoding)", "Database design", "Read-heavy optimization (cache)", "Scalability considerations"],
                "pattern": "Scalability Trade-offs",
                "difficulty": "medium",
            },
            {
                "question": "How would you design a rate limiter for an API? Discuss different algorithms.",
                "keywords": ["token bucket", "sliding window", "fixed window", "leaky bucket", "distributed", "Redis", "rate limit"],
                "rubric": ["Multiple algorithms", "Trade-offs between approaches", "Distributed rate limiting", "Implementation considerations"],
                "pattern": "API Design",
                "difficulty": "medium",
            },
            {
                "question": "Design a notification system that can handle millions of users. What components would you need?",
                "keywords": ["message queue", "Kafka", "push notification", "email", "SMS", "priority", "retry", "template"],
                "rubric": ["Component breakdown", "Message queue for decoupling", "Multiple channels", "Scalability/reliability"],
                "pattern": "Message Queues",
                "difficulty": "hard",
            },
        ],
    },
    "behavioral": {
        "star": [
            {
                "question": "Tell me about a time you had to make a technical decision with incomplete information. How did you handle it?",
                "keywords": ["ambiguity", "decision", "data", "risk", "stakeholder", "outcome", "learned"],
                "rubric": ["Clear situation/context", "Actions taken despite ambiguity", "Decision framework used", "Outcome and learnings"],
                "pattern": "Ambiguity Handling",
                "difficulty": "medium",
            },
            {
                "question": "Describe a situation where you disagreed with a teammate's technical approach. What happened?",
                "keywords": ["disagree", "approach", "discussion", "compromise", "data", "evidence", "resolved", "team"],
                "rubric": ["Specific situation described", "How disagreement was communicated", "Resolution approach", "Outcome and relationship impact"],
                "pattern": "Conflict Resolution",
                "difficulty": "medium",
            },
            {
                "question": "Tell me about a project where things didn't go as planned. What did you learn?",
                "keywords": ["failure", "mistake", "learned", "improved", "process", "change", "postmortem", "recovery"],
                "rubric": ["Honest about failure", "Root cause identified", "Actions taken to recover", "Lessons applied going forward"],
                "pattern": "Failure/Recovery",
                "difficulty": "medium",
            },
        ],
    },
    "domain_specific": {
        "backend": [
            {
                "question": "Explain the differences between SQL and NoSQL databases. When would you choose one over the other?",
                "keywords": ["relational", "document", "schema", "ACID", "BASE", "scalability", "joins", "denormalization"],
                "rubric": ["Key differences explained", "Use cases for each", "Trade-offs identified", "Real-world examples"],
                "pattern": "Database Selection",
                "difficulty": "medium",
            },
        ],
        "frontend": [
            {
                "question": "Explain the virtual DOM and how it improves performance in React. What are its limitations?",
                "keywords": ["virtual DOM", "reconciliation", "diffing", "real DOM", "batch updates", "fiber", "performance"],
                "rubric": ["Virtual DOM concept", "Diffing algorithm", "Performance benefits", "Limitations and alternatives"],
                "pattern": "Component Architecture",
                "difficulty": "medium",
            },
        ],
        "fullstack": [
            {
                "question": "How would you design an authentication system for a web application? Discuss tokens vs sessions.",
                "keywords": ["JWT", "session", "cookie", "token", "OAuth", "refresh token", "stateless", "XSS", "CSRF"],
                "rubric": ["Token vs session comparison", "Security considerations", "Implementation approach", "Trade-offs"],
                "pattern": "Full Stack Architecture",
                "difficulty": "medium",
            },
        ],
        "devops_sre": [
            {
                "question": "Explain the difference between containers and virtual machines. When would you use each?",
                "keywords": ["Docker", "container", "VM", "hypervisor", "kernel", "isolation", "overhead", "portability"],
                "rubric": ["Architecture differences", "Resource overhead comparison", "Use cases", "Security considerations"],
                "pattern": "Container Orchestration",
                "difficulty": "medium",
            },
        ],
        "data_engineer": [
            {
                "question": "Explain the difference between batch and stream processing. When would you use each?",
                "keywords": ["batch", "stream", "real-time", "latency", "throughput", "Kafka", "Spark", "Flink"],
                "rubric": ["Processing model differences", "Latency vs throughput trade-offs", "Use cases", "Technology choices"],
                "pattern": "Stream Processing",
                "difficulty": "medium",
            },
        ],
        "ml_engineer": [
            {
                "question": "Explain overfitting and underfitting. How do you detect and prevent them?",
                "keywords": ["overfitting", "underfitting", "regularization", "cross-validation", "bias", "variance", "dropout"],
                "rubric": ["Define both concepts", "Detection methods", "Prevention techniques", "Bias-variance trade-off"],
                "pattern": "Model Training Pipeline",
                "difficulty": "medium",
            },
        ],
        "mobile": [
            {
                "question": "How do you handle offline functionality in a mobile app? Discuss data synchronization strategies.",
                "keywords": ["offline", "cache", "sync", "conflict resolution", "local storage", "SQLite", "queue"],
                "rubric": ["Offline storage approach", "Sync strategy", "Conflict resolution", "User experience considerations"],
                "pattern": "Offline Storage",
                "difficulty": "medium",
            },
        ],
        "platform": [
            {
                "question": "How would you design an API that needs to support backward compatibility across multiple versions?",
                "keywords": ["versioning", "backward compatible", "deprecation", "migration", "contract", "breaking change"],
                "rubric": ["Versioning strategy", "Backward compatibility approach", "Deprecation process", "Client migration plan"],
                "pattern": "SDK Design",
                "difficulty": "medium",
            },
        ],
    },
}


def generate_quick_assessment(company, role, level):
    """Generate 8 questions for Quick Assessment.

    Returns:
        {
            'questions': [{id, question, keywords, rubric, pattern, difficulty, round_type, answer_mode}, ...],
            'total_questions': int,
            'company': str,
            'role': str,
            'level': str,
        }
    """
    questions = []
    q_id = 1

    # 3 coding questions (Phone Screen)
    coding_qs = list(QUESTION_TEMPLATES["phone_screen"]["coding"])
    random.shuffle(coding_qs)
    for q in coding_qs[:3]:
        questions.append({**q, "id": q_id, "round_type": "phone_screen", "answer_mode": "code"})
        q_id += 1

    # 1 system design question
    design_qs = list(QUESTION_TEMPLATES["system_design"]["architecture"])
    random.shuffle(design_qs)
    questions.append({**design_qs[0], "id": q_id, "round_type": "system_design", "answer_mode": "voice"})
    q_id += 1

    # 2 behavioral questions
    behavioral_qs = list(QUESTION_TEMPLATES["behavioral"]["star"])
    random.shuffle(behavioral_qs)
    for q in behavioral_qs[:2]:
        questions.append({**q, "id": q_id, "round_type": "behavioral", "answer_mode": "voice"})
        q_id += 1

    # 2 domain-specific questions
    role_key = role.lower()
    domain_qs = QUESTION_TEMPLATES["domain_specific"].get(role_key, [])
    if domain_qs:
        questions.append({**domain_qs[0], "id": q_id, "round_type": "domain_specific", "answer_mode": "hybrid"})
        q_id += 1

    # Add one more from coding if we need to reach 8
    remaining_coding = [q for q in coding_qs[3:] if q not in questions]
    if remaining_coding:
        questions.append({**remaining_coding[0], "id": q_id, "round_type": "phone_screen", "answer_mode": "code"})
        q_id += 1

    # Ensure we have at least 7 questions
    while len(questions) < 7:
        extra = random.choice(coding_qs)
        questions.append({**extra, "id": q_id, "round_type": "phone_screen", "answer_mode": "code"})
        q_id += 1

    return {
        "questions": questions[:8],
        "total_questions": len(questions[:8]),
        "company": company,
        "role": role,
        "level": level,
    }


def score_assessment(answers, questions):
    """Score all answers from a Quick Assessment.

    Args:
        answers: List of {question_id, answer_text}
        questions: List of question dicts from generate_quick_assessment

    Returns:
        {
            'overall_score': 0-100,
            'per_question': [{question_id, score, thinking, accuracy, quality, pattern, round_type}, ...],
            'per_round': {round_type: avg_score},
            'weak_patterns': [pattern names with score < 50],
            'strong_patterns': [pattern names with score >= 70],
            'recommended_focus': [top 3 weak areas],
        }
    """
    q_map = {q["id"]: q for q in questions}
    per_question = []
    round_scores = {}
    pattern_scores = {}

    for answer in answers:
        qid = answer.get("question_id")
        q = q_map.get(qid)
        if not q:
            continue

        result = dual_score(
            answer.get("answer_text", ""),
            expected_keywords=q.get("keywords", []),
            rubric_points=q.get("rubric", []),
        )

        quality = classify_answer_quality(result["total_score"])
        pattern = q.get("pattern", "Unknown")
        round_type = q.get("round_type", "phone_screen")

        per_question.append({
            "question_id": qid,
            "question": q.get("question", ""),
            "score": result["total_score"],
            "rating": result["rating"],
            "thinking": result["thinking"],
            "accuracy": result["accuracy"],
            "quality": quality,
            "pattern": pattern,
            "round_type": round_type,
            "difficulty": q.get("difficulty", "medium"),
        })

        # Aggregate by round
        round_scores.setdefault(round_type, []).append(result["total_score"])

        # Aggregate by pattern
        pattern_scores.setdefault(pattern, []).append(result["total_score"])

    # Calculate averages
    overall = round(sum(r["score"] for r in per_question) / len(per_question)) if per_question else 0
    per_round = {rt: round(sum(scores) / len(scores)) for rt, scores in round_scores.items()}

    # Identify weak and strong patterns
    pattern_avgs = {p: round(sum(s) / len(s)) for p, s in pattern_scores.items()}
    weak = [p for p, avg in sorted(pattern_avgs.items(), key=lambda x: x[1]) if avg < 50]
    strong = [p for p, avg in sorted(pattern_avgs.items(), key=lambda x: -x[1]) if avg >= 70]

    return {
        "overall_score": overall,
        "per_question": per_question,
        "per_round": per_round,
        "pattern_scores": pattern_avgs,
        "weak_patterns": weak,
        "strong_patterns": strong,
        "recommended_focus": weak[:3] if weak else list(pattern_avgs.keys())[:3],
    }


def compute_elo_from_assessment(current_elo, sub_elos, assessment_results):
    """Compute new ELO from Quick Assessment results.

    Args:
        current_elo: Starting overall ELO
        sub_elos: Dict of {round_type: elo}
        assessment_results: Output from score_assessment()

    Returns:
        {
            'overall': {new_elo, delta},
            'sub_elos': {round_type: {new_elo, delta}},
        }
    """
    # Build answer list for ELO calculation
    answers_for_elo = []
    for pq in assessment_results["per_question"]:
        answers_for_elo.append({
            "difficulty": pq.get("difficulty", "medium"),
            "score_percent": pq["score"],
            "round_type": pq["round_type"],
        })

    overall_result = calculate_session_elo_change(
        current_elo, answers_for_elo, session_type="quick_assessment"
    )

    sub_result = calculate_sub_elo_changes(
        sub_elos, answers_for_elo, session_type="quick_assessment"
    )

    return {
        "overall": {"new_elo": overall_result["new_elo"], "delta": overall_result["delta"]},
        "sub_elos": sub_result,
    }
