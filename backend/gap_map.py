"""
Gap Map Engine - GrowthPath v2.0
Maps target role demands vs current tech stack to identify
strength areas, gap areas, and cross-cutting concerns.
"""

from company_profiles import get_role_demands

# ──────────────────────────────────────────────
# Skill Normalization (fuzzy matching)
# ──────────────────────────────────────────────

# Maps common user-entered skills to canonical skill names
SKILL_ALIASES = {
    # Languages
    "python": "Python", "py": "Python", "python3": "Python",
    "javascript": "JavaScript", "js": "JavaScript", "es6": "JavaScript",
    "typescript": "TypeScript", "ts": "TypeScript",
    "java": "Java",
    "go": "Go", "golang": "Go",
    "rust": "Rust",
    "c++": "C++", "cpp": "C++",
    "c#": "C#", "csharp": "C#",
    "ruby": "Ruby",
    "swift": "Swift",
    "kotlin": "Kotlin",
    "scala": "Scala",
    "sql": "SQL", "mysql": "SQL", "postgresql": "SQL", "postgres": "SQL",

    # Frameworks & Tools
    "react": "React", "reactjs": "React", "react.js": "React",
    "vue": "Vue", "vuejs": "Vue", "vue.js": "Vue",
    "angular": "Angular", "angularjs": "Angular",
    "node": "Node.js", "nodejs": "Node.js", "node.js": "Node.js",
    "flask": "Flask", "django": "Django", "fastapi": "FastAPI",
    "spring": "Spring", "spring boot": "Spring",
    "express": "Express", "expressjs": "Express",

    # Databases
    "mongodb": "MongoDB", "mongo": "MongoDB",
    "redis": "Redis",
    "dynamodb": "DynamoDB",
    "cassandra": "Cassandra",
    "elasticsearch": "Elasticsearch", "elastic": "Elasticsearch",

    # DevOps / Cloud
    "docker": "Docker",
    "kubernetes": "Kubernetes", "k8s": "Kubernetes",
    "aws": "AWS", "amazon web services": "AWS",
    "gcp": "GCP", "google cloud": "GCP",
    "azure": "Azure",
    "terraform": "Terraform",
    "ci/cd": "CI/CD", "cicd": "CI/CD", "jenkins": "CI/CD", "github actions": "CI/CD",

    # Data / ML
    "spark": "Apache Spark", "pyspark": "Apache Spark",
    "kafka": "Kafka", "apache kafka": "Kafka",
    "airflow": "Airflow", "apache airflow": "Airflow",
    "tensorflow": "TensorFlow", "tf": "TensorFlow",
    "pytorch": "PyTorch", "torch": "PyTorch",
    "pandas": "Pandas", "numpy": "NumPy",

    # Testing
    "pytest": "Pytest", "unittest": "Python Testing",
    "jest": "Jest", "mocha": "Mocha",
    "selenium": "Selenium", "playwright": "Playwright",
    "cypress": "Cypress",

    # Concepts
    "rest": "REST APIs", "rest api": "REST APIs", "restful": "REST APIs",
    "graphql": "GraphQL",
    "grpc": "gRPC",
    "microservices": "Microservices",
    "system design": "System Design",
    "data structures": "Data Structures & Algorithms", "dsa": "Data Structures & Algorithms",
    "algorithms": "Data Structures & Algorithms",
}

# Maps canonical skills to demand categories they satisfy
SKILL_TO_DEMAND_MAP = {
    # Backend core
    "Python": ["Language Fundamentals", "Python/Scala", "Python (NumPy/Pandas/Scikit-learn)"],
    "Java": ["Language Fundamentals"],
    "Go": ["Language Fundamentals", "Backend Framework (Node/Python/Go)"],
    "Node.js": ["Backend Framework (Node/Python/Go)"],
    "Flask": ["Backend Framework (Node/Python/Go)"],
    "Django": ["Backend Framework (Node/Python/Go)"],
    "FastAPI": ["Backend Framework (Node/Python/Go)"],
    "Spring": ["Language Fundamentals"],

    # Frontend
    "React": ["Frontend Framework (React/Vue)", "React/Vue/Angular", "JavaScript/TypeScript"],
    "Vue": ["Frontend Framework (React/Vue)", "React/Vue/Angular"],
    "Angular": ["React/Vue/Angular"],
    "JavaScript": ["JavaScript/TypeScript"],
    "TypeScript": ["JavaScript/TypeScript"],

    # Databases
    "SQL": ["Database Design", "SQL & Data Modeling", "Basic SQL", "Database Design (SQL/NoSQL)"],
    "MongoDB": ["Database Design (SQL/NoSQL)"],
    "Redis": ["Caching Strategies"],
    "DynamoDB": ["Database Design (SQL/NoSQL)", "Cloud Data Services"],
    "Elasticsearch": ["Database Design (SQL/NoSQL)"],

    # System Design
    "System Design": ["System Design", "Distributed Systems"],
    "Microservices": ["Microservices", "System Design"],
    "Data Structures & Algorithms": ["Data Structures & Algorithms"],

    # APIs
    "REST APIs": ["API Design (REST/GraphQL)", "API & SDK Design"],
    "GraphQL": ["API Design (REST/GraphQL)"],
    "gRPC": ["API Design (REST/GraphQL)"],

    # DevOps
    "Docker": ["Docker & Containerization"],
    "Kubernetes": ["Kubernetes"],
    "AWS": ["Cloud Platforms (AWS/GCP)", "Cloud Data Services"],
    "GCP": ["Cloud Platforms (AWS/GCP)", "Cloud Data Services"],
    "Azure": ["Cloud Platforms (AWS/GCP)"],
    "Terraform": ["Infrastructure as Code (Terraform/Pulumi)"],
    "CI/CD": ["CI/CD", "CI/CD Pipelines"],

    # Data
    "Apache Spark": ["Apache Spark/Beam"],
    "Kafka": ["Streaming (Kafka/Kinesis)", "Message Queues"],
    "Airflow": ["Pipeline Orchestration (Airflow)"],
    "Pandas": ["Python (NumPy/Pandas/Scikit-learn)"],
    "NumPy": ["Python (NumPy/Pandas/Scikit-learn)"],

    # ML
    "TensorFlow": ["Deep Learning (PyTorch/TensorFlow)"],
    "PyTorch": ["Deep Learning (PyTorch/TensorFlow)"],

    # Testing
    "Pytest": ["Testing Basics", "Testing (Jest/Cypress)"],
    "Jest": ["Testing (Jest/Cypress)"],
    "Selenium": ["Testing Basics"],
    "Playwright": ["Testing Basics", "Testing (Jest/Cypress)"],
    "Cypress": ["Testing (Jest/Cypress)"],
}


def _normalize_skills(tech_stack):
    """Normalize user-entered tech stack to canonical skill names."""
    normalized = set()
    for skill in tech_stack:
        key = skill.strip().lower()
        canonical = SKILL_ALIASES.get(key, skill.strip())
        normalized.add(canonical)
    return normalized


def _get_satisfied_demands(normalized_skills):
    """Get the set of demand categories that the user's skills satisfy."""
    satisfied = set()
    for skill in normalized_skills:
        mapped = SKILL_TO_DEMAND_MAP.get(skill, [])
        satisfied.update(mapped)
        # Also do fuzzy match — if skill name contains demand keyword
        satisfied.add(skill)
    return satisfied


def generate_gap_map(tech_stack, role, level):
    """Generate a gap map showing strengths, gaps, and cross-cutting concerns.

    Args:
        tech_stack: List of user-entered skills (strings)
        role: Target role (e.g., 'backend')
        level: Target level (e.g., 'senior')

    Returns:
        (gap_map_dict, error)

    gap_map_dict:
        {
            'role': str,
            'level': str,
            'strengths': [{'skill': str, 'matched_by': [str]}],
            'gaps': [{'skill': str, 'priority': 'high'|'medium'|'low'}],
            'cross_cutting': [{'skill': str, 'status': 'strength'|'gap'}],
            'coverage_percent': float,
            'total_demands': int,
            'covered_demands': int,
            'gap_demands': int,
        }
    """
    demands, err = get_role_demands(role, level)
    if err:
        return None, err

    normalized_skills = _normalize_skills(tech_stack)
    satisfied = _get_satisfied_demands(normalized_skills)

    # Classify core + level skills
    all_required = demands["core_skills"] + demands["level_skills"]
    strengths = []
    gaps = []

    for skill in all_required:
        # Check if any user skill matches this demand
        skill_lower = skill.lower()
        matched_by = []

        for user_skill in normalized_skills:
            user_lower = user_skill.lower()
            # Direct match or partial match
            if user_lower in skill_lower or skill_lower in user_lower:
                matched_by.append(user_skill)
            # Check via mapping
            mapped_demands = SKILL_TO_DEMAND_MAP.get(user_skill, [])
            if skill in mapped_demands:
                if user_skill not in matched_by:
                    matched_by.append(user_skill)

        # Also check if skill itself is in satisfied set
        if skill in satisfied and not matched_by:
            matched_by.append(skill)

        if matched_by:
            strengths.append({"skill": skill, "matched_by": list(set(matched_by))})
        else:
            # Priority based on position in demands
            if skill in demands["core_skills"]:
                priority = "high"
            else:
                priority = "medium"
            gaps.append({"skill": skill, "priority": priority})

    # Classify cross-cutting concerns
    cross_cutting = []
    for skill in demands["cross_cutting"]:
        skill_lower = skill.lower()
        is_strength = False
        for user_skill in normalized_skills:
            if user_skill.lower() in skill_lower or skill_lower in user_skill.lower():
                is_strength = True
                break
        cross_cutting.append({"skill": skill, "status": "strength" if is_strength else "gap"})

    total = len(all_required)
    covered = len(strengths)
    coverage = round((covered / total * 100), 1) if total > 0 else 0

    return {
        "role": role,
        "level": level,
        "role_label": demands.get("role", role),
        "strengths": strengths,
        "gaps": sorted(gaps, key=lambda g: 0 if g["priority"] == "high" else 1),
        "cross_cutting": cross_cutting,
        "coverage_percent": coverage,
        "total_demands": total,
        "covered_demands": covered,
        "gap_demands": len(gaps),
    }, None
