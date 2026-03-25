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
MAX_MOCKS_PER_DAY = 5
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
    {
        "question": "What is a load balancer? Explain different load balancing strategies.",
        "keywords": ["round robin", "least connections", "IP hash", "health check", "reverse proxy", "L4", "L7"],
        "rubric": ["Basic definition", "Multiple strategies explained", "Health checks", "L4 vs L7"],
        "pattern": "Scalability Trade-offs", "difficulty": "easy",
    },
    {
        "question": "Explain the difference between horizontal and vertical scaling. When would you choose one over the other?",
        "keywords": ["horizontal", "vertical", "scale out", "scale up", "stateless", "cost", "limits"],
        "rubric": ["Clear definitions", "Trade-offs", "Use cases for each", "Stateless requirement for horizontal"],
        "pattern": "Scalability Trade-offs", "difficulty": "easy",
    },
    {
        "question": "What is a CDN and how does it improve performance? Design a simple CDN architecture.",
        "keywords": ["CDN", "edge server", "caching", "latency", "origin server", "TTL", "invalidation", "geographic"],
        "rubric": ["CDN purpose", "Edge caching concept", "Cache invalidation", "Geographic distribution"],
        "pattern": "Caching Strategy", "difficulty": "easy",
    },
    {
        "question": "Design a rate limiter for an API. What algorithms would you consider?",
        "keywords": ["token bucket", "sliding window", "fixed window", "leaky bucket", "distributed", "Redis"],
        "rubric": ["At least 2 algorithms", "Distributed considerations", "Storage choice", "Edge cases"],
        "pattern": "API Design", "difficulty": "medium",
    },
    {
        "question": "Design a notification system that supports email, SMS, and push notifications at scale.",
        "keywords": ["queue", "priority", "template", "retry", "rate limit", "preference", "async", "dead letter"],
        "rubric": ["Multi-channel architecture", "Queue-based processing", "Retry mechanism", "User preferences"],
        "pattern": "Message Queues", "difficulty": "medium",
    },
    {
        "question": "Design a URL shortener like bit.ly. How would you handle billions of URLs?",
        "keywords": ["hash", "base62", "database", "redirect", "analytics", "collision", "cache", "sharding"],
        "rubric": ["URL encoding scheme", "Storage and retrieval", "Collision handling", "Analytics"],
        "pattern": "Data Modeling", "difficulty": "medium",
    },
    {
        "question": "What is the CAP theorem? Explain with real-world examples of systems that choose different trade-offs.",
        "keywords": ["consistency", "availability", "partition tolerance", "CP", "AP", "eventual consistency", "strong consistency"],
        "rubric": ["Clear CAP explanation", "Real examples", "Trade-off reasoning", "Eventual vs strong consistency"],
        "pattern": "Distributed Systems", "difficulty": "medium",
    },
    {
        "question": "Design a real-time analytics dashboard that processes millions of events per second.",
        "keywords": ["streaming", "Kafka", "aggregation", "time window", "real-time", "batch", "lambda architecture"],
        "rubric": ["Data ingestion pipeline", "Real-time processing", "Aggregation strategy", "Dashboard serving layer"],
        "pattern": "Scalability Trade-offs", "difficulty": "hard",
    },
    {
        "question": "Design a distributed task scheduler that can handle millions of scheduled jobs reliably.",
        "keywords": ["scheduling", "cron", "distributed", "consistency", "leader election", "retry", "idempotent"],
        "rubric": ["Scheduling mechanism", "Distribution strategy", "Failure handling", "Idempotency"],
        "pattern": "Distributed Systems", "difficulty": "hard",
    },
]

EXTRA_BEHAVIORAL_QUESTIONS = [
    {
        "question": "Tell me about yourself and your experience. What brings you to this role?",
        "keywords": ["background", "experience", "motivation", "career", "skills", "growth"],
        "rubric": ["Clear narrative", "Relevant experience highlighted", "Motivation for role", "Concise delivery"],
        "pattern": "Collaboration", "difficulty": "easy",
    },
    {
        "question": "Describe a project you're most proud of. What was your specific contribution?",
        "keywords": ["project", "contribution", "impact", "technical", "team", "result", "challenge"],
        "rubric": ["Specific project details", "Individual contribution clear", "Impact measured", "Lessons learned"],
        "pattern": "Ownership", "difficulty": "easy",
    },
    {
        "question": "How do you handle disagreements with team members on technical approaches?",
        "keywords": ["disagreement", "compromise", "data", "listen", "respect", "consensus", "trade-off"],
        "rubric": ["Respectful approach", "Data-driven resolution", "Willingness to compromise", "Outcome focused"],
        "pattern": "Collaboration", "difficulty": "easy",
    },
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
    {
        "question": "Tell me about a time you received critical feedback. How did you respond?",
        "keywords": ["feedback", "growth", "improvement", "self-awareness", "action", "change"],
        "rubric": ["Specific feedback situation", "Emotional maturity", "Actions taken", "Growth demonstrated"],
        "pattern": "Failure/Recovery", "difficulty": "medium",
    },
    {
        "question": "Describe a situation where you had to work with a difficult team member. How did you handle it?",
        "keywords": ["conflict", "empathy", "communication", "resolution", "professional", "outcome"],
        "rubric": ["Specific situation", "Empathetic approach", "Resolution strategy", "Professional outcome"],
        "pattern": "Collaboration", "difficulty": "medium",
    },
    {
        "question": "Tell me about a time you identified a problem that nobody else noticed. What did you do about it?",
        "keywords": ["proactive", "initiative", "problem", "solution", "impact", "ownership"],
        "rubric": ["Problem identification", "Initiative taken", "Solution implemented", "Impact measured"],
        "pattern": "Ownership", "difficulty": "medium",
    },
    {
        "question": "How do you stay current with technology trends? Give an example where learning something new helped your team.",
        "keywords": ["learning", "technology", "growth", "applied", "team benefit", "curiosity"],
        "rubric": ["Learning approach", "Specific example", "Application to work", "Team benefit"],
        "pattern": "Collaboration", "difficulty": "easy",
    },
    {
        "question": "Describe the most complex cross-team project you've worked on. How did you ensure alignment across teams?",
        "keywords": ["cross-team", "alignment", "communication", "stakeholder", "coordination", "dependency"],
        "rubric": ["Project complexity", "Cross-team coordination", "Communication strategy", "Outcome"],
        "pattern": "Leadership/Influence", "difficulty": "hard",
    },
    {
        "question": "Tell me about a time you had to make a decision with incomplete information. How did you approach it?",
        "keywords": ["ambiguity", "decision", "risk", "data", "judgment", "iterate", "outcome"],
        "rubric": ["Ambiguity handling", "Decision framework", "Risk assessment", "Iteration mindset"],
        "pattern": "Ownership", "difficulty": "hard",
    },
]

BAR_RAISER_QUESTIONS = [
    {
        "question": "What does quality mean to you in software engineering?",
        "keywords": ["quality", "testing", "reliability", "user experience", "maintainability", "standards"],
        "rubric": ["Clear definition", "Multiple quality dimensions", "User perspective", "Practical examples"],
        "pattern": "Ownership", "difficulty": "easy",
    },
    {
        "question": "How do you balance speed of delivery with quality? Give a real example.",
        "keywords": ["speed", "quality", "trade-off", "MVP", "technical debt", "iterate", "pragmatic"],
        "rubric": ["Acknowledges trade-off", "Real example", "Decision framework", "Long-term thinking"],
        "pattern": "Ownership", "difficulty": "easy",
    },
    {
        "question": "How would you mentor a junior engineer who is technically capable but struggles with communication in code reviews?",
        "keywords": ["mentor", "communication", "code review", "feedback", "growth", "empathy", "coaching"],
        "rubric": ["Empathetic approach", "Specific coaching tactics", "Sets expectations clearly", "Measures improvement"],
        "pattern": "Collaboration", "difficulty": "medium",
    },
    {
        "question": "Describe how you would introduce a new testing practice or tool to a team that is resistant to change.",
        "keywords": ["change management", "adoption", "demonstrate value", "incremental", "buy-in", "metrics"],
        "rubric": ["Change management approach", "Value demonstration", "Incremental adoption", "Measuring success"],
        "pattern": "Leadership/Influence", "difficulty": "medium",
    },
    {
        "question": "You discover a critical security vulnerability in production. Walk me through your first 60 minutes.",
        "keywords": ["incident", "triage", "communication", "fix", "rollback", "postmortem", "stakeholder"],
        "rubric": ["Immediate triage steps", "Communication plan", "Fix vs rollback decision", "Postmortem mindset"],
        "pattern": "Ownership", "difficulty": "hard",
    },
    {
        "question": "If you could redesign your current team's development process from scratch, what would you change and why?",
        "keywords": ["process", "improvement", "agile", "efficiency", "culture", "tooling", "feedback"],
        "rubric": ["Identifies real problems", "Proposes concrete changes", "Considers team dynamics", "Shows big-picture thinking"],
        "pattern": "Leadership/Influence", "difficulty": "hard",
    },
    {
        "question": "How do you evaluate whether to build a tool in-house vs using a third-party solution?",
        "keywords": ["build vs buy", "cost", "maintenance", "customization", "vendor lock-in", "team capacity"],
        "rubric": ["Evaluation framework", "Cost analysis", "Long-term maintenance", "Risk assessment"],
        "pattern": "Ownership", "difficulty": "medium",
    },
    {
        "question": "Describe a time when you had to push back on a product requirement because of technical concerns. How did you handle it?",
        "keywords": ["pushback", "technical", "product", "communication", "alternative", "compromise"],
        "rubric": ["Clear technical concern", "Respectful communication", "Alternative proposed", "Outcome"],
        "pattern": "Leadership/Influence", "difficulty": "medium",
    },
    {
        "question": "How would you design an on-call rotation that keeps the team healthy while ensuring reliability?",
        "keywords": ["on-call", "rotation", "burnout", "runbook", "escalation", "SLA", "work-life balance"],
        "rubric": ["Fair rotation", "Burnout prevention", "Runbook importance", "Escalation paths"],
        "pattern": "Collaboration", "difficulty": "medium",
    },
    {
        "question": "You join a team with very poor test coverage and frequent production incidents. What's your 90-day plan?",
        "keywords": ["test coverage", "incidents", "prioritize", "quick wins", "culture", "automation", "metrics"],
        "rubric": ["Assessment approach", "Quick wins identified", "Long-term strategy", "Cultural change"],
        "pattern": "Ownership", "difficulty": "hard",
    },
    {
        "question": "How do you measure the success of an engineering team beyond just shipping features?",
        "keywords": ["metrics", "quality", "velocity", "satisfaction", "reliability", "tech debt", "learning"],
        "rubric": ["Multiple metrics", "Quality indicators", "Team health", "Balanced view"],
        "pattern": "Leadership/Influence", "difficulty": "hard",
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

def _get_all_bar_raiser_questions():
    return list(BAR_RAISER_QUESTIONS)


def _generate_llm_questions(round_type, role, company, level, count, existing_questions):
    """Use LLM to generate fresh questions for a round type."""
    try:
        from llm_service import call_llm, _get_available_providers
        if not _get_available_providers():
            return []

        existing_text = "\n".join([f"- {q['question']}" for q in existing_questions[:5]])

        prompt = f"""Generate {count} unique interview questions for a {company.title()} {role.replace('_', ' ')} ({level}) candidate.
Round type: {round_type.replace('_', ' ').title()}

These questions should progress from basic/easy to advanced/hard difficulty.
DO NOT repeat these existing questions:
{existing_text}

Return ONLY a JSON array of objects, each with:
- "question": the question text
- "keywords": array of 5-7 key terms expected in a good answer
- "rubric": array of 4 evaluation criteria
- "pattern": a category label
- "difficulty": "easy", "medium", or "hard"

Return valid JSON only, no markdown formatting."""

        response = call_llm(
            [{"role": "user", "content": prompt}],
            system_prompt="You are an expert technical interviewer. Generate diverse, realistic interview questions.",
            max_tokens=3000,
        )

        import json
        # Try to parse JSON from response
        text = response.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0]
        questions = json.loads(text)
        if isinstance(questions, list):
            return questions[:count]
    except Exception:
        pass
    return []


def _pad_questions_with_llm(pool, q_count, round_type, role, company, level, answer_mode):
    """Get questions from pool, use LLM to generate more if pool is too small."""
    random.shuffle(pool)
    questions = pool[:q_count]

    # If we don't have enough, try LLM
    if len(questions) < q_count:
        llm_qs = _generate_llm_questions(
            round_type, role, company, level,
            q_count - len(questions), questions,
        )
        questions.extend(llm_qs)

    return questions


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
        answer_mode = ROUND_ANSWER_MODES[round_type]
        round_qs = []

        # Get question pool based on round type
        if round_type == "phone_screen":
            pool = _get_all_coding_questions()
        elif round_type == "system_design":
            pool = _get_all_design_questions()
        elif round_type == "behavioral":
            pool = _get_all_behavioral_questions()
        elif round_type == "domain_specific":
            pool = _get_domain_questions(role)
        elif round_type == "bar_raiser":
            pool = _get_all_bar_raiser_questions()
        else:
            pool = []

        # Get questions from pool + LLM if needed
        questions = _pad_questions_with_llm(pool, q_count, round_type, role, company, level, answer_mode)

        for q in questions:
            round_qs.append({**q, "id": q_id, "round_type": round_type, "answer_mode": answer_mode})
            q_id += 1

        total_questions += len(round_qs)
        rounds.append({
            "round_number": i + 1,
            "round_type": round_type,
            "label": ROUND_LABELS[round_type],
            "answer_mode": answer_mode,
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
    Returns (allowed, reason). Currently unlimited for testing.
    """
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
