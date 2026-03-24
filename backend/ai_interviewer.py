"""
AI Interviewer Module - GrowthPath v2.0 (Sprint 4)
Conversational AI interviewer with company-specific personas,
dynamic probe trees (5 levels), hint system, and guardrails.
"""

import json
from company_profiles import get_company_profile, ROUND_LABELS
from dual_scorer import dual_score, classify_answer_quality
from llm_service import call_llm, _get_available_providers

# ──────────────────────────────────────────────
# Guardrail System Prompt
# ──────────────────────────────────────────────

GUARDRAIL_PROMPT = """
CRITICAL RULES — NEVER VIOLATE:
1. NEVER reveal the correct answer or solution directly
2. NEVER say "the answer is..." or "you should have said..."
3. When giving hints, guide with questions, not statements
4. If the candidate's answer is wrong, say "interesting approach" or "have you considered..." — do NOT correct them
5. You may acknowledge good points but do NOT confirm if the overall answer is correct
6. When probing deeper, ask follow-up questions that LEAD the candidate toward the answer without giving it away
7. Keep responses under 3 sentences unless explaining a follow-up question
"""

# ──────────────────────────────────────────────
# Probe Tree Generation
# ──────────────────────────────────────────────

PROBE_TEMPLATES = {
    "strong": {
        1: "Excellent point. Now, how would you handle this at {scale}?",
        2: "Good thinking. What if the requirements changed to {twist}?",
        3: "Strong. Can you discuss the failure modes and how you'd mitigate them?",
        4: "Impressive depth. How would you monitor this in production?",
        5: "Outstanding. How would you explain this trade-off decision to a non-technical stakeholder?",
    },
    "average": {
        1: "That's a reasonable start. Can you elaborate on {aspect}?",
        2: "I see where you're going. What data structure would be most efficient here?",
        3: "Interesting. Have you considered the trade-offs between your approach and {alternative}?",
        4: "Getting closer. What about edge cases like {edge_case}?",
        5: "Good foundation. How would you optimize this for production scale?",
    },
    "weak": {
        1: "Let's take a step back. What are the core components you'd need?",
        2: "No worries. Can you think about what problem we're really trying to solve here?",
        3: "Let me rephrase — if you had to break this into smaller pieces, where would you start?",
        4: "That's okay. What do you know about {related_concept} that might help here?",
        5: "Let's simplify. If you had just one user, how would you build this?",
    },
}

SCALE_OPTIONS = [
    "10 million users", "100x the current traffic", "global distribution across 5 regions",
    "99.99% uptime", "sub-100ms latency", "handling 1 billion events per day",
]

TWIST_OPTIONS = [
    "real-time instead of batch processing", "multi-tenant architecture",
    "the data is eventually consistent", "you need to support offline mode",
    "the team has only 2 engineers to maintain this",
]

EDGE_CASES = [
    "empty input", "concurrent modifications", "network partitions",
    "data corruption", "clock skew across servers", "out of memory scenarios",
]

ALTERNATIVE_OPTIONS = [
    "a simpler monolithic approach", "using a message queue instead",
    "caching at the CDN level", "eventual consistency vs strong consistency",
    "a NoSQL database instead", "a serverless architecture",
]

RELATED_CONCEPTS = [
    "hash tables", "distributed systems", "CAP theorem",
    "load balancing", "database indexing", "caching strategies",
]


def _fill_template(template, **kwargs):
    """Fill probe template with random contextual values."""
    import random
    result = template
    if "{scale}" in result:
        result = result.replace("{scale}", random.choice(SCALE_OPTIONS))
    if "{twist}" in result:
        result = result.replace("{twist}", random.choice(TWIST_OPTIONS))
    if "{edge_case}" in result:
        result = result.replace("{edge_case}", random.choice(EDGE_CASES))
    if "{alternative}" in result:
        result = result.replace("{alternative}", random.choice(ALTERNATIVE_OPTIONS))
    if "{related_concept}" in result:
        result = result.replace("{related_concept}", random.choice(RELATED_CONCEPTS))
    if "{aspect}" in result:
        result = result.replace("{aspect}", kwargs.get("aspect", "the implementation details"))
    return result


def generate_probe(quality, depth_level, question_context=""):
    """Generate a follow-up probe based on answer quality and current depth.

    Args:
        quality: 'strong', 'average', or 'weak'
        depth_level: 1-5 (current probe depth)
        question_context: Original question for context

    Returns:
        str: The probe question
    """
    depth = min(depth_level, 5)
    templates = PROBE_TEMPLATES.get(quality, PROBE_TEMPLATES["average"])
    template = templates.get(depth, templates[1])
    return _fill_template(template)


# ──────────────────────────────────────────────
# AI Interviewer Conversation
# ──────────────────────────────────────────────

def build_interviewer_system_prompt(company, round_type, question_context):
    """Build the full system prompt for the AI interviewer."""
    profile, _ = get_company_profile(company)
    persona = profile["persona_prompt"] if profile else "You are a professional technical interviewer."
    round_label = ROUND_LABELS.get(round_type, round_type)

    return f"""{persona}

You are currently conducting the {round_label} round.

{GUARDRAIL_PROMPT}

INTERVIEW CONTEXT:
- Question being discussed: {question_context}
- Your role: Push the candidate to demonstrate depth of knowledge
- Acknowledge their points briefly, then probe deeper
- If they seem stuck, provide a gentle nudge (not the answer)
- Keep the conversation flowing naturally
"""


def generate_ai_response(company, round_type, question, conversation_history,
                          candidate_answer, hint_requested=False):
    """Generate an AI interviewer response to a candidate's answer.

    Args:
        company: Target company for persona
        round_type: Current round type
        question: The interview question being discussed
        conversation_history: List of {role, content} messages
        candidate_answer: The candidate's latest answer
        hint_requested: Whether the candidate asked for a hint

    Returns:
        {
            'response': str,
            'quality': 'strong'|'average'|'weak',
            'probe_depth': int,
            'is_hint': bool,
            'used_llm': bool,
        }
    """
    # Score the answer
    score_result = dual_score(candidate_answer)
    quality = classify_answer_quality(score_result["total_score"])

    # Calculate probe depth from conversation history
    probe_depth = len([m for m in conversation_history if m.get("role") == "interviewer"]) + 1
    probe_depth = min(probe_depth, 5)

    # Try LLM-based response first
    providers = _get_available_providers()
    if providers:
        try:
            response = _generate_llm_response(
                company, round_type, question, conversation_history,
                candidate_answer, quality, probe_depth, hint_requested,
            )
            return {
                "response": response,
                "quality": quality,
                "score": score_result["total_score"],
                "probe_depth": probe_depth,
                "is_hint": hint_requested,
                "used_llm": True,
            }
        except Exception:
            pass  # Fall through to template-based

    # Template-based fallback
    if hint_requested:
        response = _generate_hint(quality, question)
    else:
        response = generate_probe(quality, probe_depth, question)

    return {
        "response": response,
        "quality": quality,
        "score": score_result["total_score"],
        "probe_depth": probe_depth,
        "is_hint": hint_requested,
        "used_llm": False,
    }


def _generate_llm_response(company, round_type, question, history,
                             answer, quality, depth, hint_requested):
    """Generate response using LLM."""
    system_prompt = build_interviewer_system_prompt(company, round_type, question)

    messages = []
    for msg in history[-6:]:  # Keep last 6 messages for context
        role = "assistant" if msg.get("role") == "interviewer" else "user"
        messages.append({"role": role, "content": msg["content"]})

    # Add current answer
    if hint_requested:
        messages.append({
            "role": "user",
            "content": f"[Candidate requested a hint]\nCandidate's current answer: {answer}\n\nProvide a helpful nudge WITHOUT revealing the answer. Guide them with a question.",
        })
    else:
        messages.append({
            "role": "user",
            "content": f"Candidate's answer: {answer}\n\nYour assessment: answer quality is {quality}. Probe depth level: {depth}/5. Respond as the interviewer — acknowledge briefly, then ask a follow-up probe appropriate for the quality level.",
        })

    response = call_llm(messages, system_prompt=system_prompt, max_tokens=300)
    return response


def _generate_hint(quality, question):
    """Generate a hint without revealing the answer."""
    hints = {
        "weak": [
            "Think about what data structures could help organize this problem.",
            "Consider breaking the problem into smaller sub-problems first.",
            "What are the inputs and expected outputs? Start from there.",
            "Think about the simplest possible solution first, even if it's not optimal.",
        ],
        "average": [
            "You're on the right track. Think about what's the bottleneck in your current approach.",
            "Good direction. Consider what happens at the boundaries — very large or very small inputs.",
            "Solid start. What if you thought about this from a different angle — maybe top-down instead of bottom-up?",
        ],
        "strong": [
            "You're doing well. Consider the operational aspects — how would you monitor this in production?",
            "Strong approach. Think about how this would behave under failure conditions.",
            "Good analysis. What trade-offs are you making with this choice?",
        ],
    }

    import random
    hint_list = hints.get(quality, hints["average"])
    return random.choice(hint_list)


# ──────────────────────────────────────────────
# Conversation State Management
# ──────────────────────────────────────────────

def create_conversation_state(question, round_type, company):
    """Create initial conversation state for a question."""
    return {
        "question": question,
        "round_type": round_type,
        "company": company,
        "history": [
            {"role": "interviewer", "content": question.get("question", "")},
        ],
        "probe_depth": 0,
        "max_depth": 5,
        "hints_used": 0,
        "scores": [],
        "is_complete": False,
    }


def process_candidate_response(state, answer_text, hint_requested=False):
    """Process a candidate's response and generate AI interviewer follow-up.

    Args:
        state: Conversation state dict
        answer_text: Candidate's answer text
        hint_requested: Whether candidate wants a hint

    Returns:
        Updated state with AI response added
    """
    # Add candidate's answer to history
    state["history"].append({"role": "candidate", "content": answer_text})

    if hint_requested:
        state["hints_used"] += 1

    # Generate AI response
    result = generate_ai_response(
        company=state["company"],
        round_type=state["round_type"],
        question=state["question"].get("question", ""),
        conversation_history=state["history"],
        candidate_answer=answer_text,
        hint_requested=hint_requested,
    )

    # Add AI response to history
    state["history"].append({"role": "interviewer", "content": result["response"]})
    state["probe_depth"] = result["probe_depth"]
    state["scores"].append(result["score"])

    # Check if we've reached max depth
    if state["probe_depth"] >= state["max_depth"]:
        state["is_complete"] = True

    return state, result


def get_conversation_summary(state):
    """Get a summary of the conversation for scoring."""
    return {
        "question": state["question"].get("question", ""),
        "round_type": state["round_type"],
        "probe_depth_reached": state["probe_depth"],
        "max_depth": state["max_depth"],
        "hints_used": state["hints_used"],
        "exchange_count": len([m for m in state["history"] if m["role"] == "candidate"]),
        "average_score": round(sum(state["scores"]) / len(state["scores"])) if state["scores"] else 0,
        "transcript": state["history"],
    }
