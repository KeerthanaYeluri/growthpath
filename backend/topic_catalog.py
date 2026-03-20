"""
Master topic catalog for GrowthPath learning paths.
Each interest area maps to a sequence of topics with estimated hours.
Topics have 4 content dimensions: Interview, Deep Dive, Best Practices, Tips & Tricks.
"""

TECH_STACK_OPTIONS = [
    "Python", "Java", "JavaScript", "TypeScript", "C#", "Go", "Ruby",
    "Selenium", "Playwright", "Cypress", "Appium",
    "Pytest", "JUnit", "TestNG", "Jest", "Mocha",
    "REST API", "GraphQL", "gRPC",
    "Docker", "Kubernetes", "Jenkins", "GitHub Actions",
    "AWS", "Azure", "GCP",
    "SQL", "MongoDB", "PostgreSQL", "Redis",
    "React", "Angular", "Vue.js", "Node.js",
    "Git", "Linux", "CI/CD",
]

INTEREST_AREAS_OPTIONS = [
    "Playwright", "API Testing", "Performance Testing", "Security Testing",
    "DevOps", "Cloud Computing", "Frontend Development", "Backend Development",
    "Mobile Testing", "Data Engineering", "Machine Learning", "System Design",
]

# Topic catalog: interest_area -> list of topics in learning sequence
TOPIC_CATALOG = {
    "Playwright": [
        {"topic_id": "pw-intro", "title": "Introduction to Playwright", "estimated_hours": 3, "sequence": 1,
         "description": "Setup, architecture, browser contexts, first test"},
        {"topic_id": "pw-selectors", "title": "Selectors & Locators", "estimated_hours": 4, "sequence": 2,
         "description": "CSS, XPath, text, role-based, and custom selectors"},
        {"topic_id": "pw-actions", "title": "Actions & Assertions", "estimated_hours": 4, "sequence": 3,
         "description": "Click, fill, check, select, assertions, auto-waiting"},
        {"topic_id": "pw-advanced", "title": "Advanced Interactions", "estimated_hours": 5, "sequence": 4,
         "description": "File uploads, dialogs, frames, multiple pages, network interception"},
        {"topic_id": "pw-pom", "title": "Page Object Model", "estimated_hours": 4, "sequence": 5,
         "description": "POM design pattern, fixtures, reusable components"},
        {"topic_id": "pw-api", "title": "API Testing with Playwright", "estimated_hours": 3, "sequence": 6,
         "description": "Request context, API assertions, mocking APIs"},
        {"topic_id": "pw-ci", "title": "CI/CD Integration", "estimated_hours": 3, "sequence": 7,
         "description": "Docker, GitHub Actions, parallel execution, reporting"},
    ],
    "API Testing": [
        {"topic_id": "api-fundamentals", "title": "REST API Fundamentals", "estimated_hours": 3, "sequence": 1,
         "description": "HTTP methods, status codes, headers, request/response"},
        {"topic_id": "api-tools", "title": "API Testing Tools", "estimated_hours": 4, "sequence": 2,
         "description": "Postman, requests library, API clients"},
        {"topic_id": "api-auth", "title": "Authentication & Authorization", "estimated_hours": 4, "sequence": 3,
         "description": "OAuth, JWT, API keys, session management"},
        {"topic_id": "api-validation", "title": "Response Validation", "estimated_hours": 3, "sequence": 4,
         "description": "JSON schema validation, assertions, data integrity"},
        {"topic_id": "api-automation", "title": "API Test Automation", "estimated_hours": 5, "sequence": 5,
         "description": "Framework design, pytest integration, data-driven tests"},
        {"topic_id": "api-advanced", "title": "Advanced API Testing", "estimated_hours": 4, "sequence": 6,
         "description": "GraphQL, gRPC, WebSocket, contract testing"},
    ],
    "Performance Testing": [
        {"topic_id": "perf-intro", "title": "Performance Testing Fundamentals", "estimated_hours": 3, "sequence": 1,
         "description": "Load, stress, endurance, spike testing concepts"},
        {"topic_id": "perf-locust", "title": "Locust Framework", "estimated_hours": 5, "sequence": 2,
         "description": "Locustfiles, users, tasks, events, distributed testing"},
        {"topic_id": "perf-jmeter", "title": "JMeter Basics", "estimated_hours": 4, "sequence": 3,
         "description": "Test plans, thread groups, samplers, listeners"},
        {"topic_id": "perf-analysis", "title": "Performance Analysis", "estimated_hours": 4, "sequence": 4,
         "description": "Metrics, bottlenecks, profiling, reporting"},
        {"topic_id": "perf-ci", "title": "Performance in CI/CD", "estimated_hours": 3, "sequence": 5,
         "description": "Automated performance gates, trend tracking"},
    ],
    "Security Testing": [
        {"topic_id": "sec-intro", "title": "Security Testing Fundamentals", "estimated_hours": 3, "sequence": 1,
         "description": "OWASP Top 10, threat modeling, security mindset"},
        {"topic_id": "sec-web", "title": "Web Application Security", "estimated_hours": 5, "sequence": 2,
         "description": "XSS, CSRF, SQL injection, SSRF, authentication flaws"},
        {"topic_id": "sec-api", "title": "API Security Testing", "estimated_hours": 4, "sequence": 3,
         "description": "Broken auth, injection, mass assignment, rate limiting"},
        {"topic_id": "sec-tools", "title": "Security Testing Tools", "estimated_hours": 4, "sequence": 4,
         "description": "OWASP ZAP, Burp Suite, static analysis tools"},
    ],
    "DevOps": [
        {"topic_id": "devops-intro", "title": "DevOps Fundamentals", "estimated_hours": 3, "sequence": 1,
         "description": "Culture, practices, CI/CD concepts, automation"},
        {"topic_id": "devops-docker", "title": "Docker & Containers", "estimated_hours": 5, "sequence": 2,
         "description": "Dockerfile, images, containers, compose, networking"},
        {"topic_id": "devops-k8s", "title": "Kubernetes Basics", "estimated_hours": 6, "sequence": 3,
         "description": "Pods, deployments, services, config maps, ingress"},
        {"topic_id": "devops-cicd", "title": "CI/CD Pipelines", "estimated_hours": 5, "sequence": 4,
         "description": "Jenkins, GitHub Actions, GitLab CI, pipeline design"},
        {"topic_id": "devops-iac", "title": "Infrastructure as Code", "estimated_hours": 5, "sequence": 5,
         "description": "Terraform, Ansible, CloudFormation basics"},
        {"topic_id": "devops-monitoring", "title": "Monitoring & Observability", "estimated_hours": 4, "sequence": 6,
         "description": "Prometheus, Grafana, ELK, alerting strategies"},
    ],
    "Cloud Computing": [
        {"topic_id": "cloud-intro", "title": "Cloud Fundamentals", "estimated_hours": 3, "sequence": 1,
         "description": "IaaS, PaaS, SaaS, cloud models, shared responsibility"},
        {"topic_id": "cloud-compute", "title": "Compute Services", "estimated_hours": 4, "sequence": 2,
         "description": "EC2, Lambda, container services, auto-scaling"},
        {"topic_id": "cloud-storage", "title": "Storage & Databases", "estimated_hours": 4, "sequence": 3,
         "description": "S3, RDS, DynamoDB, caching, CDN"},
        {"topic_id": "cloud-networking", "title": "Cloud Networking", "estimated_hours": 4, "sequence": 4,
         "description": "VPC, subnets, security groups, load balancers"},
        {"topic_id": "cloud-security", "title": "Cloud Security", "estimated_hours": 3, "sequence": 5,
         "description": "IAM, encryption, compliance, best practices"},
    ],
    "Frontend Development": [
        {"topic_id": "fe-html-css", "title": "HTML & CSS Modern", "estimated_hours": 4, "sequence": 1,
         "description": "Semantic HTML, Flexbox, Grid, responsive design"},
        {"topic_id": "fe-js", "title": "JavaScript ES6+", "estimated_hours": 5, "sequence": 2,
         "description": "Arrow functions, destructuring, promises, async/await"},
        {"topic_id": "fe-react", "title": "React Fundamentals", "estimated_hours": 6, "sequence": 3,
         "description": "Components, hooks, state, props, lifecycle"},
        {"topic_id": "fe-state", "title": "State Management", "estimated_hours": 4, "sequence": 4,
         "description": "Context API, Redux, Zustand, data flow patterns"},
        {"topic_id": "fe-testing", "title": "Frontend Testing", "estimated_hours": 4, "sequence": 5,
         "description": "Jest, React Testing Library, integration tests"},
    ],
    "Backend Development": [
        {"topic_id": "be-python", "title": "Python for Backend", "estimated_hours": 4, "sequence": 1,
         "description": "Flask/FastAPI, routing, middleware, error handling"},
        {"topic_id": "be-databases", "title": "Database Design", "estimated_hours": 5, "sequence": 2,
         "description": "SQL, NoSQL, ORM, migrations, indexing"},
        {"topic_id": "be-api-design", "title": "API Design Patterns", "estimated_hours": 4, "sequence": 3,
         "description": "RESTful design, versioning, pagination, error handling"},
        {"topic_id": "be-auth", "title": "Authentication Systems", "estimated_hours": 4, "sequence": 4,
         "description": "JWT, OAuth2, session management, RBAC"},
        {"topic_id": "be-scaling", "title": "Scaling & Performance", "estimated_hours": 5, "sequence": 5,
         "description": "Caching, queues, load balancing, microservices"},
    ],
    "Mobile Testing": [
        {"topic_id": "mob-intro", "title": "Mobile Testing Fundamentals", "estimated_hours": 3, "sequence": 1,
         "description": "iOS vs Android, emulators, device farms"},
        {"topic_id": "mob-appium", "title": "Appium Framework", "estimated_hours": 5, "sequence": 2,
         "description": "Setup, capabilities, locators, gestures"},
        {"topic_id": "mob-patterns", "title": "Mobile Test Patterns", "estimated_hours": 4, "sequence": 3,
         "description": "Screen objects, test data, cross-platform strategies"},
        {"topic_id": "mob-ci", "title": "Mobile CI/CD", "estimated_hours": 3, "sequence": 4,
         "description": "Cloud device farms, parallel execution, reporting"},
    ],
    "Data Engineering": [
        {"topic_id": "de-intro", "title": "Data Engineering Fundamentals", "estimated_hours": 3, "sequence": 1,
         "description": "ETL, data pipelines, data warehousing concepts"},
        {"topic_id": "de-sql", "title": "Advanced SQL", "estimated_hours": 5, "sequence": 2,
         "description": "Window functions, CTEs, query optimization"},
        {"topic_id": "de-python", "title": "Python for Data", "estimated_hours": 4, "sequence": 3,
         "description": "Pandas, NumPy, data transformation, cleaning"},
        {"topic_id": "de-pipelines", "title": "Data Pipelines", "estimated_hours": 5, "sequence": 4,
         "description": "Airflow, Spark basics, streaming concepts"},
    ],
    "Machine Learning": [
        {"topic_id": "ml-intro", "title": "ML Fundamentals", "estimated_hours": 4, "sequence": 1,
         "description": "Supervised/unsupervised learning, evaluation metrics"},
        {"topic_id": "ml-python", "title": "Python for ML", "estimated_hours": 5, "sequence": 2,
         "description": "Scikit-learn, feature engineering, model selection"},
        {"topic_id": "ml-deep", "title": "Deep Learning Basics", "estimated_hours": 6, "sequence": 3,
         "description": "Neural networks, CNNs, RNNs, transfer learning"},
        {"topic_id": "ml-deploy", "title": "ML Deployment", "estimated_hours": 4, "sequence": 4,
         "description": "Model serving, APIs, monitoring, MLOps basics"},
    ],
    "System Design": [
        {"topic_id": "sd-intro", "title": "System Design Fundamentals", "estimated_hours": 4, "sequence": 1,
         "description": "Scalability, availability, consistency, trade-offs"},
        {"topic_id": "sd-components", "title": "System Components", "estimated_hours": 5, "sequence": 2,
         "description": "Load balancers, caches, queues, databases, CDNs"},
        {"topic_id": "sd-patterns", "title": "Design Patterns", "estimated_hours": 5, "sequence": 3,
         "description": "Microservices, event-driven, CQRS, saga pattern"},
        {"topic_id": "sd-practice", "title": "Design Practice", "estimated_hours": 6, "sequence": 4,
         "description": "URL shortener, chat system, notification service"},
    ],
}


def get_topics_for_interest(interest_area):
    """Get all topics for an interest area, ordered by sequence."""
    topics = TOPIC_CATALOG.get(interest_area, [])
    return sorted(topics, key=lambda t: t["sequence"])


def get_all_topics_for_interests(interest_areas):
    """Get combined topic list for multiple interest areas."""
    all_topics = []
    for area in interest_areas:
        topics = get_topics_for_interest(area)
        for t in topics:
            t_copy = dict(t)
            t_copy["interest_area"] = area
            all_topics.append(t_copy)
    return all_topics


def get_topic_by_id(topic_id):
    """Find a topic by its ID across all interest areas."""
    for area, topics in TOPIC_CATALOG.items():
        for t in topics:
            if t["topic_id"] == topic_id:
                result = dict(t)
                result["interest_area"] = area
                return result
    return None


def get_total_hours(interest_areas):
    """Calculate total estimated hours for given interest areas."""
    total = 0
    for area in interest_areas:
        for t in TOPIC_CATALOG.get(area, []):
            total += t["estimated_hours"]
    return total
