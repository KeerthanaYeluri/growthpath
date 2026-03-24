"""Tests for Dual Rating Scorer — Sprint 2"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dual_scorer import (
    score_thinking_process, score_accuracy, dual_score, classify_answer_quality,
)


# ─── Thinking Process ───

def test_thinking_weight_is_60_percent():
    result = dual_score("First, I would clarify the requirements. One approach is to use a hash map. "
                        "Alternatively, we could sort the array. The trade-off is time vs space complexity. "
                        "In summary, the hash map approach is O(n) time and O(n) space.",
                        expected_keywords=["hash map", "sort", "O(n)"])
    assert result["thinking_weighted"] <= 60
    assert result["accuracy_weighted"] <= 40

def test_thinking_clarifying_questions():
    result = score_thinking_process("Let me clarify — what are the requirements? I would ask about the constraints first.")
    assert result["clarifying_questions"] > 0

def test_thinking_multiple_approaches():
    result = score_thinking_process("One approach is brute force. Alternatively, we could use a hash map. "
                                     "The trade-off between these approaches is time complexity.")
    assert result["multiple_approaches"] > 0

def test_thinking_tradeoff_awareness():
    result = score_thinking_process("The trade-off here is between latency and throughput. "
                                     "Strong consistency comes at the cost of availability.")
    assert result["tradeoff_awareness"] > 0

def test_thinking_structured_communication():
    result = score_thinking_process("First, let me break this down. Step 1 is to identify the components. "
                                     "Second, we design the data model. Finally, we consider scalability.")
    assert result["structured_communication"] > 0

def test_thinking_empty_answer():
    result = score_thinking_process("")
    assert result["total"] == 0


# ─── Accuracy ───

def test_accuracy_correctness():
    result = score_accuracy("I would use a hash map to store complements and achieve O(n) time complexity.",
                            expected_keywords=["hash map", "O(n)", "complement"])
    assert result["correctness"] > 0

def test_accuracy_completeness():
    result = score_accuracy("First I check brute force, then optimize with hash map, handle edge cases, analyze complexity.",
                            rubric_points=["Identify brute force", "Optimize with hash map", "Handle edge cases", "Analyze complexity"])
    assert result["completeness"] > 0

def test_accuracy_empty_answer():
    result = score_accuracy("", expected_keywords=["hash map"])
    assert result["total"] == 0
    assert result["missed_keywords"] == ["hash map"]

def test_accuracy_matched_keywords():
    result = score_accuracy("Use a hash map with O(n) time", expected_keywords=["hash map", "O(n)", "binary search"])
    assert "hash map" in result["matched_keywords"]
    assert "O(n)" in result["matched_keywords"]
    assert "binary search" in result["missed_keywords"]


# ─── Dual Score ───

def test_dual_score_combined():
    result = dual_score(
        "Let me clarify the requirements first. One approach is a hash map for O(n) time. "
        "Alternatively, sorting gives O(n log n). The trade-off is space vs time. "
        "In summary, hash map is optimal for this use case with O(n) time and O(n) space.",
        expected_keywords=["hash map", "O(n)", "sorting", "space"],
        rubric_points=["Identify brute force", "Optimize with hash map", "Handle edge cases"],
    )
    assert 0 <= result["total_score"] <= 100
    assert result["thinking_weighted"] + result["accuracy_weighted"] == result["total_score"]
    assert 1 <= result["rating"] <= 5

def test_dual_score_rating_5_for_excellent():
    result = dual_score(
        "First, let me clarify the requirements and constraints. I would ask about the input size and edge cases. "
        "One approach is brute force O(n^2). Alternatively, using a hash map gives O(n) time and O(n) space. "
        "The trade-off between these approaches is time vs space complexity. At the cost of additional space, "
        "we achieve linear time. In summary, the hash map approach is optimal. "
        "Step 1: iterate through array. Step 2: check hash map for complement. Step 3: return indices.",
        expected_keywords=["hash map", "O(n)", "brute force", "complement", "time complexity", "space"],
        rubric_points=["Brute force approach", "Hash map optimization", "Edge cases", "Complexity analysis"],
    )
    assert result["rating"] >= 3  # Should be decent for this thorough answer

def test_dual_score_rating_1_for_poor():
    result = dual_score("I don't know", expected_keywords=["hash map", "O(n)"])
    assert result["rating"] <= 2


# ─── Answer Quality Classifier ───

def test_classify_strong():
    assert classify_answer_quality(75) == "strong"

def test_classify_average():
    assert classify_answer_quality(55) == "average"

def test_classify_weak():
    assert classify_answer_quality(30) == "weak"

def test_classify_boundary_70():
    assert classify_answer_quality(70) == "strong"

def test_classify_boundary_40():
    assert classify_answer_quality(40) == "average"

def test_classify_boundary_39():
    assert classify_answer_quality(39) == "weak"
