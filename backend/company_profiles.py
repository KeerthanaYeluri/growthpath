"""
Company Profiles Module - GrowthPath v2.0
Defines FAANG company interview structures, scoring rubrics, hiring bars,
and AI interviewer persona prompts for Google and Apple (POC).
"""

# ──────────────────────────────────────────────
# Round Types
# ──────────────────────────────────────────────

ROUND_TYPES = [
    "phone_screen",
    "system_design",
    "behavioral",
    "domain_specific",
    "bar_raiser",
]

ROUND_LABELS = {
    "phone_screen": "Phone Screen",
    "system_design": "System Design",
    "behavioral": "Behavioral",
    "domain_specific": "Domain-Specific",
    "bar_raiser": "Bar Raiser",
}

ROUND_ANSWER_MODES = {
    "phone_screen": "code",
    "system_design": "voice",
    "behavioral": "voice",
    "domain_specific": "hybrid",
    "bar_raiser": "voice",
}

# Time allocation for 30-minute mock (in minutes)
ROUND_TIME_ALLOCATION = {
    "phone_screen": 15,
    "system_design": 25,
    "behavioral": 20,
    "domain_specific": 25,
    "bar_raiser": 20,
}

# ──────────────────────────────────────────────
# Hiring Bars (ELO thresholds per company + level)
# ──────────────────────────────────────────────

HIRING_BARS = {
    "google": {
        "L3": 1400,
        "L4": 1600,
        "L5": 1800,
        "L6": 2000,
    },
    "apple": {
        "L3": 1350,
        "L4": 1550,
        "L5": 1750,
        "L6": 1950,
    },
}

# ──────────────────────────────────────────────
# Starting ELO by level
# ──────────────────────────────────────────────

STARTING_ELO = {
    "junior": 1000,    # L3-L4
    "mid": 1200,       # L4-L5
    "senior": 1400,    # L5-L6
    "staff": 1600,     # L6-L7
}

# Map level labels to hiring bar keys
LEVEL_TO_BAR_KEY = {
    "junior": "L3",
    "mid": "L4",
    "senior": "L5",
    "staff": "L6",
}

# ──────────────────────────────────────────────
# Supported Values
# ──────────────────────────────────────────────

SUPPORTED_COMPANIES = ["google", "apple"]

SUPPORTED_ROLES = [
    "backend",
    "frontend",
    "fullstack",
    "devops_sre",
    "data_engineer",
    "ml_engineer",
    "mobile",
    "platform",
    "qa_sdet",
]

SUPPORTED_LEVELS = ["junior", "mid", "senior", "staff"]

ROLE_LABELS = {
    "backend": "Backend Engineer",
    "frontend": "Frontend Engineer",
    "fullstack": "Full Stack Engineer",
    "devops_sre": "DevOps / SRE",
    "data_engineer": "Data Engineer",
    "ml_engineer": "ML Engineer",
    "mobile": "Mobile Engineer",
    "platform": "Platform Engineer",
    "qa_sdet": "QA / SDET",
}

LEVEL_LABELS = {
    "junior": "Junior (L3-L4)",
    "mid": "Mid (L4-L5)",
    "senior": "Senior (L5-L6)",
    "staff": "Staff+ (L6-L7)",
}

# ──────────────────────────────────────────────
# Company Profiles
# ──────────────────────────────────────────────

COMPANY_PROFILES = {
    "google": {
        "name": "Google",
        "description": "Heavy system design + coding, 'Googleyness' behavioral, any language",
        "round_weights": {
            "phone_screen": 20,
            "system_design": 30,
            "behavioral": 15,
            "domain_specific": 20,
            "bar_raiser": 15,
        },
        "critical_rounds": ["system_design"],
        "round_config": {
            "phone_screen": {
                "focus": "Algorithmic coding, data structures, problem solving",
                "question_count": 2,
                "probe_depth": 2,
                "key_traits": ["code quality", "optimal solution", "edge cases"],
            },
            "system_design": {
                "focus": "Large-scale distributed systems, scalability, trade-offs — basics to advanced",
                "question_count": 10,
                "probe_depth": 3,
                "key_traits": ["scalability thinking", "trade-off articulation", "component design"],
            },
            "behavioral": {
                "focus": "Googleyness — collaboration, intellectual humility, comfort with ambiguity — basics to advanced",
                "question_count": 10,
                "probe_depth": 2,
                "key_traits": ["collaboration", "humility", "ambiguity handling"],
            },
            "domain_specific": {
                "focus": "Role-specific technical depth from fundamentals to advanced — any programming language",
                "question_count": 10,
                "probe_depth": 2,
                "key_traits": ["technical depth", "real-world application", "best practices"],
            },
            "bar_raiser": {
                "focus": "Cross-functional thinking, ambiguity handling, big-picture impact — basics to advanced",
                "question_count": 10,
                "probe_depth": 2,
                "key_traits": ["cross-functional impact", "ambiguity navigation", "leadership"],
            },
        },
        "persona_prompt": (
            "You are a senior Google software engineer conducting an interview. "
            "You are technically rigorous but approachable. You value clear thinking "
            "over perfect answers. You probe deeply on system design trade-offs and "
            "expect candidates to consider scalability from the start. You appreciate "
            "when candidates ask clarifying questions and think out loud. You embody "
            "'Googleyness' — intellectual humility, collaboration, and comfort with "
            "ambiguity. If a candidate gives a shallow answer, you push for depth: "
            "'That's a good start, but how would you handle this at Google scale?' "
            "You never reveal the answer directly but guide through probing questions."
        ),
        "scoring_rubric": {
            "clarifying_questions": 15,
            "multiple_approaches": 15,
            "tradeoff_awareness": 15,
            "structured_communication": 15,
            "correctness": 20,
            "completeness": 20,
        },
    },
    "apple": {
        "name": "Apple",
        "description": "Design thinking + domain depth, attention to detail, user experience focus",
        "round_weights": {
            "phone_screen": 20,
            "system_design": 20,
            "behavioral": 25,
            "domain_specific": 25,
            "bar_raiser": 10,
        },
        "critical_rounds": ["behavioral", "domain_specific"],
        "round_config": {
            "phone_screen": {
                "focus": "Clean code, design sense, attention to detail",
                "question_count": 2,
                "probe_depth": 2,
                "key_traits": ["code elegance", "design awareness", "edge case handling"],
            },
            "system_design": {
                "focus": "Design-driven architecture, user experience at the system level — basics to advanced",
                "question_count": 10,
                "probe_depth": 3,
                "key_traits": ["design thinking", "user-centric architecture", "attention to detail"],
            },
            "behavioral": {
                "focus": "Craftsmanship, innovation, 'Think Different' mentality — basics to advanced",
                "question_count": 10,
                "probe_depth": 2,
                "key_traits": ["craftsmanship", "innovation mindset", "attention to quality"],
            },
            "domain_specific": {
                "focus": "Role depth + design quality, Apple ecosystem awareness — basics to advanced",
                "question_count": 10,
                "probe_depth": 2,
                "key_traits": ["domain expertise", "design quality", "ecosystem understanding"],
            },
            "bar_raiser": {
                "focus": "Innovation showcase, 'Think Different' mindset, user empathy — basics to advanced",
                "question_count": 10,
                "probe_depth": 2,
                "key_traits": ["innovation", "user empathy", "creative problem solving"],
            },
        },
        "persona_prompt": (
            "You are a senior Apple engineer conducting an interview. You have an "
            "obsessive attention to detail and expect the same from candidates. You "
            "value craftsmanship — elegant solutions over brute force. You care deeply "
            "about user experience even in backend systems. You embody Apple's 'Think "
            "Different' culture and look for candidates who challenge conventional "
            "approaches. You probe on design decisions: 'Why did you choose that "
            "approach? What would the user experience be?' You appreciate candidates "
            "who consider the end-to-end experience, not just the technical solution. "
            "You never reveal answers but guide with design-focused questions."
        ),
        "scoring_rubric": {
            "clarifying_questions": 10,
            "multiple_approaches": 15,
            "tradeoff_awareness": 15,
            "structured_communication": 20,
            "correctness": 20,
            "completeness": 20,
        },
    },
}

# ──────────────────────────────────────────────
# Role Demand Maps (what each role requires)
# ──────────────────────────────────────────────

ROLE_DEMANDS = {
    "backend": {
        "core_skills": [
            "Data Structures & Algorithms",
            "System Design",
            "API Design (REST/GraphQL)",
            "Database Design (SQL/NoSQL)",
            "Concurrency & Multithreading",
            "Caching Strategies",
            "Message Queues",
        ],
        "level_additions": {
            "junior": ["Language Fundamentals", "Basic SQL", "Testing Basics"],
            "mid": ["Microservices", "CI/CD", "Performance Optimization"],
            "senior": ["Distributed Systems", "Technical Leadership", "Architecture Patterns", "Mentoring"],
            "staff": ["System Architecture", "Cross-Team Influence", "Technical Strategy", "Org-Level Impact"],
        },
        "cross_cutting": ["Communication", "Problem Solving", "Code Review", "Documentation"],
    },
    "frontend": {
        "core_skills": [
            "JavaScript/TypeScript",
            "React/Vue/Angular",
            "HTML/CSS/Responsive Design",
            "Browser APIs & Performance",
            "State Management",
            "Component Architecture",
            "Accessibility (a11y)",
        ],
        "level_additions": {
            "junior": ["CSS Fundamentals", "Basic React", "DOM Manipulation"],
            "mid": ["Advanced React Patterns", "Build Tools (Webpack/Vite)", "Testing (Jest/Cypress)"],
            "senior": ["Performance Optimization", "Design Systems", "Micro-Frontends", "Technical Leadership"],
            "staff": ["Frontend Architecture", "Cross-Team Standards", "Web Platform Strategy"],
        },
        "cross_cutting": ["UX Thinking", "Cross-Browser Compatibility", "SEO Basics", "Communication"],
    },
    "fullstack": {
        "core_skills": [
            "Frontend Framework (React/Vue)",
            "Backend Framework (Node/Python/Go)",
            "Database Design",
            "API Design",
            "Authentication & Authorization",
            "Deployment & DevOps Basics",
            "System Design",
        ],
        "level_additions": {
            "junior": ["HTML/CSS/JS Fundamentals", "Basic CRUD APIs", "SQL Basics"],
            "mid": ["Advanced State Management", "Caching", "CI/CD", "Testing"],
            "senior": ["Architecture Patterns", "Performance at Scale", "Technical Leadership", "Security"],
            "staff": ["Platform Architecture", "Cross-Team Systems", "Technical Strategy"],
        },
        "cross_cutting": ["Communication", "Problem Solving", "UX Thinking", "Documentation"],
    },
    "devops_sre": {
        "core_skills": [
            "Linux/Unix Administration",
            "Docker & Containerization",
            "Kubernetes",
            "CI/CD Pipelines",
            "Infrastructure as Code (Terraform/Pulumi)",
            "Monitoring & Observability",
            "Incident Response",
        ],
        "level_additions": {
            "junior": ["Shell Scripting", "Basic Networking", "Git/Version Control"],
            "mid": ["Cloud Platforms (AWS/GCP)", "Service Mesh", "Log Aggregation"],
            "senior": ["Reliability Engineering", "Capacity Planning", "Chaos Engineering", "SLO/SLI Design"],
            "staff": ["Platform Strategy", "Multi-Cloud Architecture", "Org-Wide Reliability"],
        },
        "cross_cutting": ["Automation Mindset", "Security Basics", "Communication", "On-Call Best Practices"],
    },
    "data_engineer": {
        "core_skills": [
            "SQL & Data Modeling",
            "ETL/ELT Pipelines",
            "Data Warehousing",
            "Apache Spark/Beam",
            "Streaming (Kafka/Kinesis)",
            "Python/Scala",
            "Cloud Data Services",
        ],
        "level_additions": {
            "junior": ["SQL Fundamentals", "Python Basics", "Data Formats (JSON/Parquet)"],
            "mid": ["Pipeline Orchestration (Airflow)", "Data Quality", "Performance Tuning"],
            "senior": ["Data Architecture", "Real-Time Systems", "Data Governance", "Technical Leadership"],
            "staff": ["Enterprise Data Strategy", "Cross-Org Data Platforms", "ML Platform Integration"],
        },
        "cross_cutting": ["Data Privacy", "Statistical Thinking", "Communication", "Documentation"],
    },
    "ml_engineer": {
        "core_skills": [
            "Machine Learning Fundamentals",
            "Python (NumPy/Pandas/Scikit-learn)",
            "Deep Learning (PyTorch/TensorFlow)",
            "Feature Engineering",
            "Model Training & Evaluation",
            "ML System Design",
            "Data Pipelines for ML",
        ],
        "level_additions": {
            "junior": ["Linear Algebra", "Statistics", "Basic Model Training"],
            "mid": ["MLOps", "Experiment Tracking", "Model Serving", "A/B Testing"],
            "senior": ["ML Architecture", "Research-to-Production", "Technical Leadership", "Novel Approaches"],
            "staff": ["ML Strategy", "Cross-Org ML Platforms", "Industry Research Direction"],
        },
        "cross_cutting": ["Statistical Rigor", "Ethical AI", "Communication", "Experimentation Culture"],
    },
    "mobile": {
        "core_skills": [
            "iOS (Swift) or Android (Kotlin)",
            "Mobile Architecture (MVVM/MVI)",
            "UI/UX Mobile Patterns",
            "Networking & APIs",
            "Local Storage & Caching",
            "Performance Optimization",
            "App Lifecycle Management",
        ],
        "level_additions": {
            "junior": ["Language Fundamentals", "Basic UI Components", "Navigation Patterns"],
            "mid": ["Advanced UI", "Background Processing", "Testing", "CI/CD for Mobile"],
            "senior": ["App Architecture", "Cross-Platform Strategy", "Performance at Scale", "Technical Leadership"],
            "staff": ["Mobile Platform Strategy", "Cross-Org Mobile Standards", "SDK Design"],
        },
        "cross_cutting": ["UX Sensitivity", "Accessibility", "Battery/Memory Awareness", "Communication"],
    },
    "platform": {
        "core_skills": [
            "Distributed Systems",
            "API & SDK Design",
            "Infrastructure Architecture",
            "Performance & Reliability",
            "Developer Experience (DX)",
            "Service Mesh & Networking",
            "Security Fundamentals",
        ],
        "level_additions": {
            "junior": ["Networking Basics", "Linux Fundamentals", "Basic Distributed Concepts"],
            "mid": ["Platform Services", "Observability", "Capacity Planning"],
            "senior": ["Platform Architecture", "Multi-Tenancy", "Technical Leadership", "SLO Design"],
            "staff": ["Platform Strategy", "Cross-Org Infrastructure", "Technical Vision"],
        },
        "cross_cutting": ["Developer Empathy", "Documentation", "Communication", "Reliability Thinking"],
    },
    "qa_sdet": {
        "core_skills": [
            "Test Strategy & Planning",
            "Test Automation Frameworks (Selenium/Playwright/Cypress)",
            "API Testing (REST/GraphQL)",
            "Programming (Python/Java/JavaScript)",
            "CI/CD Integration for Testing",
            "Performance Testing (JMeter/Locust/k6)",
            "Data Structures & Algorithms",
        ],
        "level_additions": {
            "junior": ["Manual Testing Fundamentals", "Basic Scripting", "Bug Reporting", "Test Case Writing"],
            "mid": ["Advanced Automation", "Contract Testing", "Mobile Testing", "Test Data Management"],
            "senior": ["Test Architecture", "Quality Strategy", "Chaos Testing", "Technical Leadership", "Shift-Left Testing"],
            "staff": ["Org-Wide Quality Strategy", "Test Infrastructure Platforms", "Cross-Team Quality Standards"],
        },
        "cross_cutting": ["Attention to Detail", "Root Cause Analysis", "Communication", "Risk Assessment"],
    },
}

# ──────────────────────────────────────────────
# Public API Functions
# ──────────────────────────────────────────────

def get_company_profile(company):
    """Get full company profile. Returns (profile, error)."""
    company = company.lower()
    if company not in COMPANY_PROFILES:
        return None, f"Unsupported company: {company}. Supported: {', '.join(SUPPORTED_COMPANIES)}"
    return COMPANY_PROFILES[company], None


def get_hiring_bar(company, level):
    """Get ELO hiring bar for company + level. Returns (bar, error)."""
    company = company.lower()
    level = level.lower()
    if company not in HIRING_BARS:
        return None, f"Unsupported company: {company}"
    bar_key = LEVEL_TO_BAR_KEY.get(level)
    if not bar_key or bar_key not in HIRING_BARS[company]:
        return None, f"Unsupported level: {level}"
    return HIRING_BARS[company][bar_key], None


def get_starting_elo(level):
    """Get starting ELO for a level. Returns (elo, error)."""
    level = level.lower()
    if level not in STARTING_ELO:
        return None, f"Unsupported level: {level}. Supported: {', '.join(SUPPORTED_LEVELS)}"
    return STARTING_ELO[level], None


def get_role_demands(role, level):
    """Get skill demands for a role + level. Returns (demands, error)."""
    role = role.lower()
    level = level.lower()
    if role not in ROLE_DEMANDS:
        return None, f"Unsupported role: {role}. Supported: {', '.join(SUPPORTED_ROLES)}"
    if level not in SUPPORTED_LEVELS:
        return None, f"Unsupported level: {level}"

    role_data = ROLE_DEMANDS[role]
    level_skills = role_data["level_additions"].get(level, [])

    return {
        "role": role,
        "level": level,
        "core_skills": role_data["core_skills"],
        "level_skills": level_skills,
        "cross_cutting": role_data["cross_cutting"],
        "all_skills": role_data["core_skills"] + level_skills + role_data["cross_cutting"],
    }, None


def get_round_config(company):
    """Get round configuration for a company. Returns (config, error)."""
    company = company.lower()
    profile, err = get_company_profile(company)
    if err:
        return None, err

    rounds = []
    for round_type in ROUND_TYPES:
        rc = profile["round_config"][round_type]
        rounds.append({
            "round_type": round_type,
            "label": ROUND_LABELS[round_type],
            "answer_mode": ROUND_ANSWER_MODES[round_type],
            "time_minutes": ROUND_TIME_ALLOCATION[round_type],
            "weight": profile["round_weights"][round_type],
            "is_critical": round_type in profile["critical_rounds"],
            "focus": rc["focus"],
            "question_count": rc["question_count"],
            "probe_depth": rc["probe_depth"],
            "key_traits": rc["key_traits"],
        })

    return rounds, None


def validate_registration_fields(company, role, level):
    """Validate company/role/level selection. Returns error string or None."""
    if company.lower() not in SUPPORTED_COMPANIES:
        return f"Unsupported company: {company}. Choose from: {', '.join(SUPPORTED_COMPANIES)}"
    if role.lower() not in SUPPORTED_ROLES:
        return f"Unsupported role: {role}. Choose from: {', '.join(SUPPORTED_ROLES)}"
    if level.lower() not in SUPPORTED_LEVELS:
        return f"Unsupported level: {level}. Choose from: {', '.join(SUPPORTED_LEVELS)}"
    return None
