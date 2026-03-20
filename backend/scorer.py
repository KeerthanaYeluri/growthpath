def score_answer(transcript, question):
    """Score a single answer based on keywords, length, and relevance."""
    if not transcript or not transcript.strip():
        return {
            "keyword_score": 0,
            "detail_score": 0,
            "relevance_score": 0,
            "total_score": 0,
            "matched_keywords": [],
            "feedback": "No answer provided. Try to give a detailed response.",
        }

    text = transcript.lower()
    words = text.split()
    word_count = len(words)

    # 1. Keyword match (40%)
    keywords = [k.lower() for k in question["keywords"]]
    matched = [k for k in keywords if k in text]
    keyword_ratio = len(matched) / len(keywords) if keywords else 0
    keyword_score = min(keyword_ratio * 100, 100) * 0.4

    # 2. Detail / Length (30%)
    if word_count >= 150:
        detail_score = 100 * 0.3
    elif word_count >= 80:
        detail_score = 75 * 0.3
    elif word_count >= 40:
        detail_score = 50 * 0.3
    elif word_count >= 15:
        detail_score = 30 * 0.3
    else:
        detail_score = 10 * 0.3

    # 3. Relevance (20%) - based on topic-related keywords being present
    topic_keywords = {
        "Python": ["python", "code", "function", "class", "variable", "module", "import"],
        "Pytest": ["pytest", "test", "fixture", "assert", "conftest", "parametrize"],
        "Playwright": ["playwright", "browser", "page", "locator", "click", "selector"],
        "Java": ["java", "class", "object", "method", "interface", "extends"],
        "Selenium": ["selenium", "webdriver", "element", "driver", "browser", "locator"],
        "API Testing": ["api", "request", "response", "endpoint", "status", "json", "rest"],
        "UI Testing": ["ui", "user", "interface", "visual", "layout", "component", "css"],
        "Locust": ["locust", "load", "performance", "user", "request", "swarm"],
        "Manual Testing": ["test", "case", "bug", "defect", "requirement", "coverage"],
        "Behavioral": ["team", "project", "challenge", "result", "learned", "improved"],
        "Introduction": ["experience", "background", "work", "project", "skill"],
    }
    topic = question.get("topic", "")
    topic_words = topic_keywords.get(topic, [])
    topic_matched = sum(1 for tw in topic_words if tw in text)
    relevance_ratio = min(topic_matched / max(len(topic_words), 1), 1.0)
    relevance_score = relevance_ratio * 100 * 0.2

    # 4. Completeness (10%) - multiple points covered
    completeness_score = min(len(matched) / max(len(keywords) * 0.5, 1), 1.0) * 100 * 0.1

    total = round(keyword_score + detail_score + relevance_score + completeness_score)
    total = min(total, 100)

    # Generate feedback
    if total >= 80:
        feedback = "Excellent answer! You covered the key concepts thoroughly."
    elif total >= 60:
        feedback = "Good answer. Consider adding more specific details and examples."
    elif total >= 40:
        feedback = "Decent attempt. Try to include more technical keywords and elaborate further."
    else:
        feedback = "Needs improvement. Focus on covering the core concepts with specific examples."

    # Deep dive analysis
    missed_keywords = [k for k in keywords if k not in text]

    return {
        "keyword_score": round(keyword_score / 0.4),
        "detail_score": round(detail_score / 0.3),
        "relevance_score": round(relevance_ratio * 100),
        "total_score": total,
        "matched_keywords": matched,
        "missed_keywords": missed_keywords,
        "word_count": word_count,
        "feedback": feedback,
    }


def generate_scorecard(answers, questions):
    """Generate the full scorecard from all answers."""
    topic_scores = {}
    topic_counts = {}
    total_score = 0

    for ans in answers:
        qid = ans["question_id"]
        question = next((q for q in questions if q["id"] == qid), None)
        if not question:
            continue
        topic = question["topic"]
        score = ans["score"]["total_score"]
        total_score += score
        topic_scores[topic] = topic_scores.get(topic, 0) + score
        topic_counts[topic] = topic_counts.get(topic, 0) + 1

    # Average per topic
    for topic in topic_scores:
        topic_scores[topic] = round(topic_scores[topic] / topic_counts[topic])

    overall = round(total_score / len(answers)) if answers else 0

    # Determine strengths (top 3 topics)
    sorted_topics = sorted(topic_scores.items(), key=lambda x: x[1], reverse=True)
    strengths = []
    for topic, score in sorted_topics[:3]:
        if score >= 50:
            strengths.append(f"Strong knowledge in {topic} ({score}/100)")
    if not strengths:
        strengths = ["Shows willingness to attempt all questions"]

    # Determine improvements (bottom 3 topics)
    improvements = []
    for topic, score in sorted_topics[-3:]:
        if score < 70:
            improvements.append(f"Deepen your understanding of {topic} ({score}/100)")
    if not improvements:
        improvements = ["Continue practicing to maintain your strong performance"]

    return {
        "overall_score": overall,
        "total_questions": len(answers),
        "topic_scores": topic_scores,
        "strengths": strengths,
        "improvements": improvements,
    }