"""Tests for AI Interviewer Module — Sprint 4"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ai_interviewer import (
    generate_probe, build_interviewer_system_prompt,
    create_conversation_state, process_candidate_response,
    get_conversation_summary, generate_ai_response,
    _generate_hint, PROBE_TEMPLATES,
)


# ─── Probe Generation ───

def test_probe_tree_has_5_levels():
    for quality in ["strong", "average", "weak"]:
        templates = PROBE_TEMPLATES[quality]
        assert len(templates) == 5

def test_probe_tree_branches_on_strong_answer():
    probe = generate_probe("strong", 1)
    assert len(probe) > 0
    # Strong probes should escalate difficulty
    assert any(word in probe.lower() for word in ["scale", "failure", "production", "monitor", "handle", "excellent", "good", "strong", "impressive", "outstanding", "change", "stakeholder"])

def test_probe_tree_branches_on_average_answer():
    probe = generate_probe("average", 1)
    assert len(probe) > 0

def test_probe_tree_branches_on_weak_answer():
    probe = generate_probe("weak", 1)
    assert len(probe) > 0
    # Weak probes should simplify
    assert any(word in probe.lower() for word in ["step back", "simplify", "break", "smaller", "core", "start", "rephrase", "know"])

def test_probe_depth_1_to_5_all_generate():
    for depth in range(1, 6):
        for quality in ["strong", "average", "weak"]:
            probe = generate_probe(quality, depth)
            assert len(probe) > 10, f"Probe too short for {quality} depth {depth}"

def test_probe_depth_capped_at_5():
    probe = generate_probe("strong", 10)  # Beyond max
    assert len(probe) > 0  # Should still generate (capped at 5)


# ─── System Prompt ───

def test_google_persona_prompt_loads():
    prompt = build_interviewer_system_prompt("google", "system_design", "Design a URL shortener")
    assert "Google" in prompt or "Googleyness" in prompt
    assert "System Design" in prompt
    assert "NEVER reveal" in prompt

def test_apple_persona_prompt_loads():
    prompt = build_interviewer_system_prompt("apple", "behavioral", "Tell me about a conflict")
    assert "Apple" in prompt or "Think Different" in prompt
    assert "Behavioral" in prompt

def test_guardrails_present_in_prompt():
    prompt = build_interviewer_system_prompt("google", "phone_screen", "Two sum problem")
    assert "NEVER reveal the correct answer" in prompt
    assert "NEVER say" in prompt


# ─── Conversation State ───

def test_create_conversation_state():
    q = {"id": 1, "question": "Design a URL shortener", "round_type": "system_design"}
    state = create_conversation_state(q, "system_design", "google")
    assert state["probe_depth"] == 0
    assert state["max_depth"] == 5
    assert state["hints_used"] == 0
    assert state["is_complete"] is False
    assert len(state["history"]) == 1  # Initial interviewer message

def test_process_candidate_response_adds_to_history():
    q = {"id": 1, "question": "Two sum problem", "round_type": "phone_screen"}
    state = create_conversation_state(q, "phone_screen", "google")

    state, result = process_candidate_response(state, "I would use a hash map for O(n) time")
    # Should have: interviewer opening + candidate answer + interviewer follow-up
    assert len(state["history"]) == 3
    assert state["history"][1]["role"] == "candidate"
    assert state["history"][2]["role"] == "interviewer"
    assert result["probe_depth"] >= 1

def test_process_candidate_response_returns_quality():
    q = {"id": 1, "question": "Two sum problem", "round_type": "phone_screen"}
    state = create_conversation_state(q, "phone_screen", "google")

    state, result = process_candidate_response(state, "I don't know")
    assert result["quality"] in ("strong", "average", "weak")

def test_hint_increments_counter():
    q = {"id": 1, "question": "Design a cache", "round_type": "system_design"}
    state = create_conversation_state(q, "system_design", "google")

    state, result = process_candidate_response(state, "I'm stuck", hint_requested=True)
    assert state["hints_used"] == 1
    assert result["is_hint"] is True

def test_conversation_completes_at_max_depth():
    q = {"id": 1, "question": "Test question", "round_type": "phone_screen"}
    state = create_conversation_state(q, "phone_screen", "google")

    for i in range(5):
        state, _ = process_candidate_response(state, f"Answer {i+1} with some content about hash maps and O(n)")

    assert state["is_complete"] is True
    assert state["probe_depth"] == 5


# ─── Conversation Summary ───

def test_conversation_summary():
    q = {"id": 1, "question": "Design a URL shortener", "round_type": "system_design"}
    state = create_conversation_state(q, "system_design", "google")
    state, _ = process_candidate_response(state, "Use hashing and a database")
    state, _ = process_candidate_response(state, "Add caching with Redis for read-heavy traffic")

    summary = get_conversation_summary(state)
    assert summary["probe_depth_reached"] >= 1
    assert summary["exchange_count"] == 2
    assert summary["average_score"] >= 0
    assert len(summary["transcript"]) >= 4  # interviewer + candidate + interviewer + candidate + interviewer


# ─── Hint Generation ───

def test_hint_for_weak_answer():
    hint = _generate_hint("weak", "Design a URL shortener")
    assert len(hint) > 10
    # Hint should not contain the answer
    assert "hash" not in hint.lower() or "think" in hint.lower()

def test_hint_for_strong_answer():
    hint = _generate_hint("strong", "Design a cache")
    assert len(hint) > 10

def test_hints_vary():
    hints = set()
    for _ in range(10):
        hint = _generate_hint("average", "Some question")
        hints.add(hint)
    assert len(hints) >= 2  # Should have some variety


# ─── AI Response (template fallback) ───

def test_ai_response_without_llm():
    """Test that AI response works even without LLM API keys."""
    result = generate_ai_response(
        company="google",
        round_type="phone_screen",
        question="Two sum problem",
        conversation_history=[{"role": "interviewer", "content": "Two sum problem"}],
        candidate_answer="Use brute force with nested loops",
    )
    assert "response" in result
    assert "quality" in result
    assert "probe_depth" in result
    assert len(result["response"]) > 0

def test_ai_response_hint_mode():
    result = generate_ai_response(
        company="google",
        round_type="system_design",
        question="Design a rate limiter",
        conversation_history=[],
        candidate_answer="I'm not sure where to start",
        hint_requested=True,
    )
    assert result["is_hint"] is True
    assert len(result["response"]) > 0
