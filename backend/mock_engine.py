"""
Mock Interview Engine - GrowthPath v2.0 (Sprint 3)
Manages 5-round FAANG mock interview sessions with timer,
round transitions, hybrid answer modes, and daily limits.
"""

import random
from datetime import datetime, timezone, date
from company_profiles import (
    get_company_profile, get_round_config, ROUND_TYPES,
    ROUND_LABELS, ROUND_ANSWER_MODES, ROUND_TIME_ALLOCATION,
)
from quick_assessment import QUESTION_TEMPLATES, ARCHETYPE_PATTERNS
import storage

# ──────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────

MOCK_DURATION_MINUTES = 30
MAX_MOCKS_PER_DAY = 1
UNLIMITED_PRACTICE = True  # Targeted practice has no daily cap

# ──────────────────────────────────────────────
# Question Pool (extends quick_assessment templates)
# ──────────────────────────────────────────────

EXTRA_CODING_QUESTIONS = [
    {
        "question": "Implement a function to merge two sorted arrays into one sorted array. What's the optimal approach?",
        "keywords": ["merge", "two pointers", "sorted", "O(n+m)", "in-place"],
        "rubric": ["Two-pointer approach", "Handle unequal lengths", "Time complexity O(n+m)", "Space analysis"],
        "pattern": "Arrays/Strings", "difficulty": "easy",
    },
    {
        "question": "How would you implement a LRU (Least Recently Used) cache? Discuss the data structures needed.",
        "keywords": ["hash map", "doubly linked list", "O(1)", "get", "put", "eviction", "capacity"],
        "rubric": ["Hash map + linked list combo", "O(1) get and put", "Eviction policy", "Edge cases"],
        "pattern": "Arrays/Strings", "difficulty": "hard",
    },
    {
        "question": "Given a binary tree, find the maximum depth. Explain both recursive and iterative approaches.",
        "keywords": ["recursive", "BFS", "DFS", "queue", "stack", "O(n)", "height", "depth"],
        "rubric": ["Recursive DFS approach", "Iterative BFS approach", "Time/space comparison", "Edge cases"],
        "pattern": "Trees/Graphs", "difficulty": "easy",
    },
    {
        "question": "Explain how you would find the kth largest element in an unsorted array. Compare different approaches.",
        "keywords": ["quickselect", "heap", "min-heap", "partition", "O(n)", "O(n log k)", "sorting"],
        "rubric": ["Sorting approach O(n log n)", "Heap approach O(n log k)", "Quickselect O(n) average", "Trade-off analysis"],
        "pattern": "Sorting", "difficulty": "medium",
    },
    {
        "question": "Design an algorithm to detect if a graph contains a cycle. Discuss directed and undirected cases.",
        "keywords": ["DFS", "visited", "back edge", "union find", "topological sort", "directed", "undirected"],
        "rubric": ["DFS with coloring for directed", "Union-Find for undirected", "Time complexity", "Edge cases"],
        "pattern": "Trees/Graphs", "difficulty": "medium",
    },
]

EXTRA_DESIGN_QUESTIONS = [
    {
        "question": "Design a chat messaging system like WhatsApp. How would you handle real-time delivery and offline messages?",
        "keywords": ["WebSocket", "message queue", "push notification", "offline", "read receipt", "encryption", "database"],
        "rubric": ["Real-time delivery mechanism", "Offline message storage", "Message ordering", "Scalability"],
        "pattern": "Message Queues", "difficulty": "hard",
    },
    {
        "question": "Design a distributed cache system. How would you handle cache invalidation and consistency?",
        "keywords": ["consistent hashing", "replication", "invalidation", "TTL", "write-through", "write-back", "eviction"],
        "rubric": ["Caching strategy", "Invalidation approaches", "Consistency model", "Failure handling"],
        "pattern": "Caching Strategy", "difficulty": "hard",
    },
    {
        "question": "Design a search autocomplete system. How would you make it fast and relevant?",
        "keywords": ["trie", "prefix tree", "ranking", "cache", "top-k", "frequency", "personalization"],
        "rubric": ["Trie data structure", "Ranking algorithm", "Caching layer", "Scalability considerations"],
        "pattern": "Data Modeling", "difficulty": "medium",
    },
]

EXTRA_BEHAVIORAL_QUESTIONS = [
    {
        "question": "Tell me about a time you had to lead a project without formal authority. How did you influence others?",
        "keywords": ["influence", "leadership", "stakeholder", "consensus", "alignment", "outcome"],
        "rubric": ["Specific situation", "Leadership without authority", "Influence tactics", "Measurable outcome"],
        "pattern": "Leadership/Influence", "difficulty": "medium",
    },
    {
        "question": "Describe a time you had to deliver something with a very tight deadline. How did you prioritize?",
        "keywords": ["deadline", "prioritize", "scope", "trade-off", "communicate", "deliver", "MVP"],
        "rubric": ["Situation with real pressure", "Prioritization framework", "Communication with stakeholders", "Outcome"],
        "pattern": "Ownership", "difficulty": "medium",
    },
    {
        "question": "Tell me about a technical decision you made that you later regretted. What did you learn?",
        "keywords": ["decision", "regret", "learned", "mistake", "retrospective", "improved", "process"],
        "rubric": ["Honest about regret", "Root cause of bad decision", "What was learned", "How it changed future decisions"],
        "pattern": "Failure/Recovery", "difficulty": "medium",
    },
]

BAR_RAISER_QUESTIONS = [
    {
        "question": "If you could redesign your current team's development process from scratch, what would you change and why?",
        "keywords": ["process", "improvement", "agile", "efficiency", "culture", "tooling", "feedback"],
        "rubric": ["Identifies real problems", "Proposes concrete changes", "Considers team dynamics", "Shows big-picture thinking"],
        "pattern": "Leadership/Influence", "difficulty": "hard",
    },
    {
        "question": "How would you mentor a junior engineer who is technically capable but struggles with communication in code reviews?",
        "keywords": ["mentor", "communication", "code review", "feedback", "growth", "empathy", "coaching"],
        "rubric": ["Empathetic approach", "Specific coaching tactics", "Sets expectations clearly", "Measures improvement"],
        "pattern": "Collaboration", "difficulty": "medium",
    },
    {
        "question": "You discover a critical security vulnerability in production. Walk me through your first 60 minutes.",
        "keywords": ["incident", "triage", "communication", "fix", "rollback", "postmortem", "stakeholder"],
        "rubric": ["Immediate triage steps", "Communication plan", "Fix vs rollback decision", "Postmortem mindset"],
        "pattern": "Ownership", "difficulty": "hard",
    },
]


def _get_all_coding_questions():
    return QUESTION_TEMPLATES["phone_screen"]["coding"] + EXTRA_CODING_QUESTIONS

def _get_all_design_questions():
    return QUESTION_TEMPLATES["system_design"]["architecture"] + EXTRA_DESIGN_QUESTIONS

def _get_all_behavioral_questions():
    return QUESTION_TEMPLATES["behavioral"]["star"] + EXTRA_BEHAVIORAL_QUESTIONS

def _get_domain_questions(role):
    return QUESTION_TEMPLATES["domain_specific"].get(role.lower(), [])


# ──────────────────────────────────────────────
# Mock Interview Generation
# ──────────────────────────────────────────────

def generate_mock_interview(company, role, level):
    """Generate a full 5-round mock interview.

    Returns:
        {
            'rounds': [
                {
                    'round_number': 1-5,
                    'round_type': str,
                    'label': str,
                    'answer_mode': str,
                    'time_minutes': int,
                    'questions': [{id, question, keywords, rubric, pattern, difficulty}, ...]
                }, ...
            ],
            'total_questions': int,
            'total_time_minutes': int,
            'company': str,
            'role': str,
            'level': str,
        }
    """
    rounds = []
    q_id = 1
    total_questions = 0

    profile, _ = get_company_profile(company)
    round_config = profile["round_config"] if profile else {}

    for i, round_type in enumerate(ROUND_TYPES):
        rc = round_config.get(round_type, {})
        q_count = rc.get("question_count", 2)
        round_qs = []

        if round_type == "phone_screen":
            pool = _get_all_coding_questions()
            random.shuffle(pool)
            for q in pool[:q_count]:
                round_qs.append({**q, "id": q_id, "round_type": round_type, "answer_mode": "code"})
                q_id += 1

        elif round_type == "system_design":
            pool = _get_all_design_questions()
            random.shuffle(pool)
            for q in pool[:q_count]:
                round_qs.append({**q, "id": q_id, "round_type": round_type, "answer_mode": "voice"})
                q_id += 1

        elif round_type == "behavioral":
            pool = _get_all_behavioral_questions()
            random.shuffle(pool)
            for q in pool[:q_count]:
                round_qs.append({**q, "id": q_id, "round_type": round_type, "answer_mode": "voice"})
                q_id += 1

        elif round_type == "domain_specific":
            pool = _get_domain_questions(role)
            if pool:
                random.shuffle(pool)
                for q in pool[:q_count]:
                    round_qs.append({**q, "id": q_id, "round_type": round_type, "answer_mode": "hybrid"})
                    q_id += 1
            # Pad with coding if not enough domain questions
            if len(round_qs) < q_count:
                extra = _get_all_coding_questions()
                random.shuffle(extra)
                for q in extra[:q_count - len(round_qs)]:
                    round_qs.append({**q, "id": q_id, "round_type": round_type, "answer_mode": "hybrid"})
                    q_id += 1

        elif round_type == "bar_raiser":
            pool = list(BAR_RAISER_QUESTIONS)
            random.shuffle(pool)
            for q in pool[:q_count]:
                round_qs.append({**q, "id": q_id, "round_type": round_type, "answer_mode": "voice"})
                q_id += 1

        total_questions += len(round_qs)
        rounds.append({
            "round_number": i + 1,
            "round_type": round_type,
            "label": ROUND_LABELS[round_type],
            "answer_mode": ROUND_ANSWER_MODES[round_type],
            "time_minutes": ROUND_TIME_ALLOCATION[round_type],
            "weight": profile["round_weights"][round_type] if profile else 20,
            "is_critical": round_type in (profile.get("critical_rounds", []) if profile else []),
            "questions": round_qs,
        })

    return {
        "rounds": rounds,
        "total_questions": total_questions,
        "total_time_minutes": MOCK_DURATION_MINUTES,
        "company": company,
        "role": role,
        "level": level,
    }


def get_all_questions_flat(mock_data):
    """Extract all questions from rounds as a flat list (for storage)."""
    all_qs = []
    for rnd in mock_data["rounds"]:
        all_qs.extend(rnd["questions"])
    return all_qs


# ──────────────────────────────────────────────
# Daily Mock Limit
# ──────────────────────────────────────────────

def can_start_mock(user_id):
    """Check if user can start a new full mock interview today.
    Returns (allowed, reason).
    """
    sessions = storage.get_user_sessions(user_id)
    today = date.today().isoformat()

    mock_count_today = 0
    for s in sessions:
        role_name = s.get("role_name", "")
        start = s.get("start_time", "")
        if role_name.startswith("mock_") and start.startswith(today):
            mock_count_today += 1

    if mock_count_today >= MAX_MOCKS_PER_DAY:
        return False, "You've used your daily mock interview. Come back tomorrow! Unlimited targeted practice is still available."

    return True, None


def can_start_practice(user_id):
    """Targeted practice is always allowed."""
    return True, None


# ──────────────────────────────────────────────
# Mock Session State
# ──────────────────────────────────────────────

def create_mock_session(user_id, company, role, level, session_type="full_mock"):
    """Create a mock interview session and store it.

    Returns:
        (session_data, error)
    """
    if session_type == "full_mock":
        allowed, reason = can_start_mock(user_id)
        if not allowed:
            return None, reason

    mock_data = generate_mock_interview(company, role, level)
    all_questions = get_all_questions_flat(mock_data)

    role_name = f"mock_{company}_{role}_{session_type}"
    job_title = f"{'Full Mock' if session_type == 'full_mock' else 'Targeted Practice'} - {company.title()} {role.replace('_', ' ').title()}"

    session = storage.create_session(user_id, job_title, all_questions, role_name)

    # Get session_id from returned data
    if isinstance(session, dict):
        sid = session.get("session_id", session.get("id"))
    else:
        sid = session

    return {
        "session_id": sid,
        "mock_data": mock_data,
        "session_type": session_type,
    }, None


def create_targeted_practice(user_id, company, role, level, target_round):
    """Create a single-round targeted practice session.

    Args:
        target_round: One of ROUND_TYPES to practice

    Returns:
        (session_data, error)
    """
    if target_round not in ROUND_TYPES:
        return None, f"Invalid round type: {target_round}. Choose from: {', '.join(ROUND_TYPES)}"

    mock_data = generate_mock_interview(company, role, level)

    # Keep only the target round
    target_round_data = None
    for rnd in mock_data["rounds"]:
        if rnd["round_type"] == target_round:
            target_round_data = rnd
            break

    if not target_round_data:
        return None, f"Could not generate questions for round: {target_round}"

    all_questions = target_round_data["questions"]
    role_name = f"practice_{company}_{target_round}"
    job_title = f"Targeted Practice - {ROUND_LABELS[target_round]} ({company.title()})"

    session = storage.create_session(user_id, job_title, all_questions, role_name)
    if isinstance(session, dict):
        sid = session.get("session_id", session.get("id"))
    else:
        sid = session

    return {
        "session_id": sid,
        "round": target_round_data,
        "session_type": "targeted_practice",
        "total_questions": len(all_questions),
        "time_minutes": ROUND_TIME_ALLOCATION.get(target_round, 10),
    }, None
