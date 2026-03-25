"""
LLM Service — Supports Claude, OpenAI, and Gemini with automatic fallback.
Reads API keys from environment variables.
"""

import os
import json
import re

# Load .env file if present
_env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
if os.path.exists(_env_path):
    with open(_env_path) as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith("#") and "=" in _line:
                _key, _val = _line.split("=", 1)
                os.environ.setdefault(_key.strip(), _val.strip())

# API keys from environment
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")


def _get_available_providers():
    """Return list of available LLM providers based on API keys."""
    providers = []
    if ANTHROPIC_API_KEY:
        providers.append("claude")
    if OPENAI_API_KEY:
        providers.append("openai")
    if GEMINI_API_KEY:
        providers.append("gemini")
    return providers


def _call_claude(messages, system_prompt=None, max_tokens=4096):
    """Call Anthropic Claude API."""
    import anthropic
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    kwargs = {
        "model": "claude-sonnet-4-20250514",
        "max_tokens": max_tokens,
        "messages": messages,
    }
    if system_prompt:
        kwargs["system"] = system_prompt

    response = client.messages.create(**kwargs)
    return response.content[0].text


def _call_openai(messages, system_prompt=None, max_tokens=4096):
    """Call OpenAI GPT API."""
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)

    formatted = []
    if system_prompt:
        formatted.append({"role": "system", "content": system_prompt})
    for m in messages:
        formatted.append({"role": m["role"], "content": m["content"]})

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=formatted,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content


def _call_gemini(messages, system_prompt=None, max_tokens=4096):
    """Call Google Gemini API."""
    import google.generativeai as genai
    genai.configure(api_key=GEMINI_API_KEY)

    model = genai.GenerativeModel("gemini-2.0-flash")

    prompt_parts = []
    if system_prompt:
        prompt_parts.append(system_prompt + "\n\n")
    for m in messages:
        role = "User" if m["role"] == "user" else "Assistant"
        prompt_parts.append(f"{role}: {m['content']}\n")

    response = model.generate_content("".join(prompt_parts))
    return response.text


def call_llm(messages, system_prompt=None, max_tokens=4096, preferred_provider=None):
    """
    Call LLM with automatic fallback.
    Returns (response_text, provider_used) or raises if all fail.
    """
    providers = _get_available_providers()
    if not providers:
        raise RuntimeError("No LLM API keys configured. Set ANTHROPIC_API_KEY, OPENAI_API_KEY, or GEMINI_API_KEY.")

    # Put preferred provider first
    if preferred_provider and preferred_provider in providers:
        providers.remove(preferred_provider)
        providers.insert(0, preferred_provider)

    errors = []
    for provider in providers:
        try:
            if provider == "claude":
                text = _call_claude(messages, system_prompt, max_tokens)
            elif provider == "openai":
                text = _call_openai(messages, system_prompt, max_tokens)
            elif provider == "gemini":
                text = _call_gemini(messages, system_prompt, max_tokens)
            else:
                continue
            return text, provider
        except Exception as e:
            errors.append(f"{provider}: {str(e)}")
            continue

    raise RuntimeError(f"All LLM providers failed: {'; '.join(errors)}")


def call_llm_json(messages, system_prompt=None, max_tokens=4096, preferred_provider=None):
    """
    Call LLM and parse response as JSON.
    Handles markdown code blocks in response.
    """
    text, provider = call_llm(messages, system_prompt, max_tokens, preferred_provider)

    # Strip markdown code blocks if present
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r'^```(?:json)?\s*\n?', '', text)
        text = re.sub(r'\n?```\s*$', '', text)

    try:
        return json.loads(text), provider
    except json.JSONDecodeError:
        # Try to find JSON in the response
        match = re.search(r'[\[{].*[\]}]', text, re.DOTALL)
        if match:
            return json.loads(match.group()), provider
        raise ValueError(f"Could not parse LLM response as JSON: {text[:200]}")


# ─── JD-Based Question Generation ───

def generate_questions_from_jd(job_description, num_questions=15):
    """Generate interview questions based on a job description."""

    system = """You are a senior technical interviewer. Generate interview questions based on the job description provided.
Return ONLY a valid JSON array, no other text."""

    prompt = f"""Based on this job description, generate {num_questions} interview questions that would be asked in a real interview for this role.

Job Description:
{job_description}

Question Distribution:
- 1 Introduction question ("Tell me about yourself and how your experience relates to this role")
- 40% Technical questions specific to the skills/technologies mentioned in the JD
- 25% Behavioral questions (STAR format expected)
- 20% Situational/scenario questions related to the role
- 15% Domain/project-based questions

Difficulty progression: Start with Easy, progress to Medium, end with Hard.

Return JSON array:
[
    {{
        "id": 1,
        "topic": "Introduction",
        "difficulty": "Easy",
        "question": "the question text",
        "keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5", "keyword6", "keyword7", "keyword8", "keyword9", "keyword10"],
        "model_answer": "A comprehensive model answer (3-5 sentences)"
    }}
]

IMPORTANT: Each question MUST have exactly these fields: id, topic, difficulty, question, keywords (array of 10 strings), model_answer (string)."""

    return call_llm_json(
        [{"role": "user", "content": prompt}],
        system_prompt=system,
        max_tokens=8000,
    )


# ─── Interview-Specific Prompts ───

def analyze_resume(resume_text, job_role):
    """Analyze resume and extract structured data."""
    system = """You are an expert technical recruiter. Analyze resumes accurately.
Return ONLY valid JSON, no other text."""

    prompt = f"""Analyze this resume for the role: {job_role}

Resume:
{resume_text}

Return JSON:
{{
    "skills": ["skill1", "skill2", ...],
    "experience_years": <number>,
    "experience_level": "fresher|junior|mid|senior",
    "projects": [
        {{"name": "...", "description": "...", "technologies": ["..."]}}
    ],
    "education": [{{"degree": "...", "institution": "...", "year": "..."}}],
    "strengths": ["strength1", "strength2"],
    "gaps_for_role": ["gap1", "gap2"],
    "summary": "2-3 sentence summary"
}}"""

    return call_llm_json(
        [{"role": "user", "content": prompt}],
        system_prompt=system,
    )


def generate_interview_questions(parsed_resume, job_role, interest_area, num_questions=15):
    """Generate role-specific interview questions based on resume and interest area."""

    # Map interest areas to specific technical domains
    domain_context = {
        "DevOps": "CI/CD pipelines, Docker, Kubernetes, Infrastructure as Code (Terraform/Ansible), monitoring (Prometheus/Grafana), cloud platforms (AWS/Azure/GCP), Linux administration, scripting, GitOps",
        "API Testing": "REST API testing, API automation (Postman/RestAssured), HTTP methods, status codes, authentication (OAuth/JWT), API validation, contract testing, performance testing of APIs",
        "Playwright": "Playwright test automation, browser testing, selectors, page objects, test fixtures, parallel execution, API testing with Playwright, CI/CD integration",
        "Performance Testing": "JMeter, Locust, Gatling, load testing, stress testing, performance monitoring, bottleneck identification, capacity planning, APM tools",
        "Security Testing": "OWASP Top 10, penetration testing, vulnerability scanning, SAST/DAST, security headers, SQL injection, XSS, authentication security, security tools (Burp Suite/ZAP)",
        "Cloud Computing": "AWS/Azure/GCP services, cloud architecture, serverless, containers, networking, IAM, cost optimization, high availability, disaster recovery",
        "Frontend Development": "React/Angular/Vue, HTML/CSS/JavaScript, responsive design, state management, testing (Jest/Cypress), performance optimization, accessibility",
        "Backend Development": "API design, databases, microservices, authentication, caching, message queues, system design, scalability, error handling",
        "Mobile Testing": "Mobile test automation, Appium, device testing, responsive testing, mobile-specific bugs, app performance, iOS/Android differences",
        "Data Engineering": "ETL pipelines, data warehousing, SQL, Python, Spark, Airflow, data modeling, data quality, streaming (Kafka)",
        "Machine Learning": "ML algorithms, Python, TensorFlow/PyTorch, model training, evaluation metrics, feature engineering, MLOps, data preprocessing",
        "System Design": "Distributed systems, scalability, load balancing, caching, database design, microservices, message queues, CAP theorem",
    }

    domain = domain_context.get(interest_area, interest_area)

    system = """You are a senior technical interviewer. Generate personalized interview questions.
Return ONLY valid JSON array, no other text."""

    prompt = f"""Generate {num_questions} interview questions for this candidate.

Role: {job_role}
Domain Focus: {interest_area}
Domain Topics: {domain}

Candidate Resume Summary:
- Skills: {json.dumps(parsed_resume.get('skills', []))}
- Experience: {parsed_resume.get('experience_years', 0)} years ({parsed_resume.get('experience_level', 'mid')})
- Projects: {json.dumps(parsed_resume.get('projects', []))}

Question Distribution:
- 40% Technical questions specific to {interest_area} ({domain})
- 25% Behavioral questions (STAR format expected)
- 20% Situational/scenario questions related to {interest_area}
- 15% Project deep-dive questions based on their resume projects

Difficulty should match their experience level: {parsed_resume.get('experience_level', 'mid')}

Return JSON array:
[
    {{
        "id": 1,
        "question": "the question text",
        "category": "technical|behavioral|situational|project",
        "difficulty": "easy|medium|hard",
        "domain": "{interest_area}",
        "expected_topics": ["topic1", "topic2"],
        "ideal_answer_points": ["key point 1", "key point 2", "key point 3"]
    }}
]"""

    return call_llm_json(
        [{"role": "user", "content": prompt}],
        system_prompt=system,
    )


def generate_conversational_response(interview_context, candidate_answer, current_question_idx, total_questions):
    """Generate interviewer's natural response and next question."""

    system = f"""You are a professional interviewer named Alex conducting a technical interview.
- Be warm but professional
- Give a brief 1-2 sentence acknowledgment of the candidate's answer
- Then smoothly transition to the next question
- If the answer was vague, ask ONE follow-up before moving on
- If the answer was good, acknowledge it positively
- Do NOT reveal scores or evaluation
- If candidate says "I don't know", say something encouraging and move on

Interview context:
- Role: {interview_context.get('job_role', 'Software Engineer')}
- Domain: {interview_context.get('interest_area', 'General')}
- Question {current_question_idx + 1} of {total_questions}
"""

    messages = interview_context.get("conversation_history", [])
    messages.append({"role": "user", "content": candidate_answer})

    text, provider = call_llm(messages, system_prompt=system, max_tokens=500)
    return text, provider


def evaluate_answer(question, answer, category, expected_topics, ideal_points, resume_summary):
    """Evaluate a single interview answer."""

    system = """You are an expert interview evaluator. Score answers accurately and fairly.
Return ONLY valid JSON, no other text."""

    prompt = f"""Evaluate this interview answer:

Question: {question}
Category: {category}
Expected topics: {json.dumps(expected_topics)}
Key points expected: {json.dumps(ideal_points)}

Candidate's answer: {answer}

Candidate background: {resume_summary}

Score on 4 dimensions (0-10 each):
1. relevance - Does the answer address the question?
2. depth - Technical depth and specificity
3. communication - Clarity, structure, coherence
4. examples - Real-world examples or concrete details

Return JSON:
{{
    "relevance": <0-10>,
    "depth": <0-10>,
    "communication": <0-10>,
    "examples": <0-10>,
    "total_score": <0-40>,
    "strengths": ["what was good"],
    "weaknesses": ["what was missing"],
    "suggestions": ["specific improvement advice"],
    "ideal_answer": "brief ideal answer (3-4 sentences)"
}}"""

    return call_llm_json(
        [{"role": "user", "content": prompt}],
        system_prompt=system,
    )


def generate_interview_summary(interview_data):
    """Generate overall interview summary and recommendation."""

    system = """You are a senior hiring manager reviewing interview results.
Return ONLY valid JSON, no other text."""

    prompt = f"""Review this complete interview and provide overall assessment:

Role: {interview_data.get('job_role', '')}
Domain: {interview_data.get('interest_area', '')}
Candidate experience: {interview_data.get('experience_level', '')}

Questions and scores:
{json.dumps(interview_data.get('exchanges', []), indent=2)}

Return JSON:
{{
    "overall_score": <0-100>,
    "category_scores": {{
        "technical": <0-100>,
        "behavioral": <0-100>,
        "situational": <0-100>,
        "project": <0-100>
    }},
    "top_strengths": ["strength1", "strength2", "strength3"],
    "improvement_areas": ["area1", "area2", "area3"],
    "recommendation": "strong_hire|hire|maybe|no_hire",
    "summary": "3-4 sentence overall assessment of the candidate"
}}"""

    return call_llm_json(
        [{"role": "user", "content": prompt}],
        system_prompt=system,
    )
