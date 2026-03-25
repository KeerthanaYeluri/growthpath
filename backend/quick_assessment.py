"""
Quick Assessment Engine - GrowthPath v2.0
Generates 5-10 diagnostic questions for new users,
scores answers, assigns starting ELO, and generates
learning path from failures.
"""

import random
from datetime import datetime, timezone
from company_profiles import (
    get_company_profile, get_role_demands, ROUND_TYPES,
    LEVEL_TO_BAR_KEY, HIRING_BARS,
)
from elo_rating import (
    create_initial_elo, calculate_session_elo_change,
    calculate_sub_elo_changes, check_interview_ready,
)
from dual_scorer import dual_score, classify_answer_quality

# ──────────────────────────────────────────────
# Question Archetype Patterns
# ──────────────────────────────────────────────

ARCHETYPE_PATTERNS = {
    "system_design": [
        "Scalability Trade-offs", "Data Modeling", "API Design",
        "Caching Strategy", "Message Queues", "Load Balancing", "Database Selection",
    ],
    "coding": [
        "Arrays/Strings", "Trees/Graphs", "Dynamic Programming",
        "Sliding Window", "Binary Search", "Recursion/Backtracking", "Sorting",
    ],
    "behavioral": [
        "Conflict Resolution", "Failure/Recovery", "Leadership/Influence",
        "Ambiguity Handling", "Ownership", "Collaboration",
    ],
    "domain": {
        "backend": ["REST API Design", "Database Optimization", "Concurrency", "Microservices Architecture"],
        "frontend": ["Component Architecture", "State Management", "Performance Optimization", "Responsive Design"],
        "fullstack": ["Full Stack Architecture", "API Integration", "Deployment Pipeline", "Database Design"],
        "devops_sre": ["CI/CD Pipeline", "Container Orchestration", "Monitoring Strategy", "Incident Response"],
        "data_engineer": ["Data Pipeline Design", "Data Modeling", "Stream Processing", "Data Quality"],
        "ml_engineer": ["Model Training Pipeline", "Feature Engineering", "Model Serving", "Experiment Design"],
        "mobile": ["Mobile Architecture", "Offline Storage", "Performance Optimization", "UI Patterns"],
        "platform": ["Platform Architecture", "SDK Design", "Multi-tenancy", "Service Reliability"],
    },
}

# ──────────────────────────────────────────────
# Quick Assessment Question Templates
# ──────────────────────────────────────────────

QUESTION_TEMPLATES = {
    "phone_screen": {
        "coding": [
            {
                "question": "Given an array of integers, find two numbers that add up to a specific target. Explain your approach and its time complexity.",
                "keywords": ["hash map", "hash table", "dictionary", "O(n)", "two pass", "complement", "time complexity"],
                "rubric": ["Identify brute force O(n^2)", "Optimize with hash map", "Handle edge cases", "Analyze time/space complexity"],
                "pattern": "Arrays/Strings",
                "difficulty": "medium",
            },
            {
                "question": "How would you detect if a linked list has a cycle? Describe multiple approaches.",
                "keywords": ["fast pointer", "slow pointer", "Floyd", "hash set", "O(1) space", "tortoise", "hare"],
                "rubric": ["Hash set approach", "Two-pointer (Floyd's) approach", "Compare time/space trade-offs", "Edge cases"],
                "pattern": "Arrays/Strings",
                "difficulty": "medium",
            },
            {
                "question": "Explain how you would reverse a binary tree. What's the time and space complexity?",
                "keywords": ["recursive", "iterative", "queue", "BFS", "DFS", "O(n)", "swap", "left", "right"],
                "rubric": ["Recursive approach", "Iterative approach", "Time complexity O(n)", "Space complexity analysis"],
                "pattern": "Trees/Graphs",
                "difficulty": "easy",
            },
            {
                "question": "Given a string, find the longest substring without repeating characters. Walk through your approach.",
                "keywords": ["sliding window", "hash map", "set", "two pointers", "O(n)", "substring"],
                "rubric": ["Identify sliding window pattern", "Track character positions", "Handle window shrinking", "Optimal O(n) solution"],
                "pattern": "Sliding Window",
                "difficulty": "medium",
            },
            {
                "question": "Implement a function to check if a string is a valid palindrome, considering only alphanumeric characters. What's your approach?",
                "keywords": ["two pointers", "alphanumeric", "case insensitive", "O(n)", "O(1) space", "reverse"],
                "rubric": ["Two-pointer approach", "Handle non-alphanumeric chars", "Case handling", "Time/space analysis"],
                "pattern": "Arrays/Strings",
                "difficulty": "easy",
            },
        ],
    },
    "system_design": {
        "architecture": [
            {
                "question": "Design a URL shortening service like bit.ly. How would you handle high traffic?",
                "keywords": ["hash", "base62", "database", "cache", "redirect", "301", "302", "scalability", "sharding"],
                "rubric": ["Generate short URLs (hashing/encoding)", "Database design", "Read-heavy optimization (cache)", "Scalability considerations"],
                "pattern": "Scalability Trade-offs",
                "difficulty": "medium",
            },
            {
                "question": "How would you design a rate limiter for an API? Discuss different algorithms.",
                "keywords": ["token bucket", "sliding window", "fixed window", "leaky bucket", "distributed", "Redis", "rate limit"],
                "rubric": ["Multiple algorithms", "Trade-offs between approaches", "Distributed rate limiting", "Implementation considerations"],
                "pattern": "API Design",
                "difficulty": "medium",
            },
            {
                "question": "Design a notification system that can handle millions of users. What components would you need?",
                "keywords": ["message queue", "Kafka", "push notification", "email", "SMS", "priority", "retry", "template"],
                "rubric": ["Component breakdown", "Message queue for decoupling", "Multiple channels", "Scalability/reliability"],
                "pattern": "Message Queues",
                "difficulty": "hard",
            },
        ],
    },
    "behavioral": {
        "star": [
            {
                "question": "Tell me about a time you had to make a technical decision with incomplete information. How did you handle it?",
                "keywords": ["ambiguity", "decision", "data", "risk", "stakeholder", "outcome", "learned"],
                "rubric": ["Clear situation/context", "Actions taken despite ambiguity", "Decision framework used", "Outcome and learnings"],
                "pattern": "Ambiguity Handling",
                "difficulty": "medium",
            },
            {
                "question": "Describe a situation where you disagreed with a teammate's technical approach. What happened?",
                "keywords": ["disagree", "approach", "discussion", "compromise", "data", "evidence", "resolved", "team"],
                "rubric": ["Specific situation described", "How disagreement was communicated", "Resolution approach", "Outcome and relationship impact"],
                "pattern": "Conflict Resolution",
                "difficulty": "medium",
            },
            {
                "question": "Tell me about a project where things didn't go as planned. What did you learn?",
                "keywords": ["failure", "mistake", "learned", "improved", "process", "change", "postmortem", "recovery"],
                "rubric": ["Honest about failure", "Root cause identified", "Actions taken to recover", "Lessons applied going forward"],
                "pattern": "Failure/Recovery",
                "difficulty": "medium",
            },
        ],
    },
    "domain_specific": {
        "backend": [
            {
                "question": "What is a REST API? Explain the key principles and HTTP methods.",
                "keywords": ["REST", "HTTP", "GET", "POST", "PUT", "DELETE", "stateless", "resource", "endpoint"],
                "rubric": ["REST principles", "HTTP methods", "Statelessness", "Resource-based design"],
                "pattern": "API Design", "difficulty": "easy",
            },
            {
                "question": "Explain the difference between SQL and NoSQL databases. When would you choose one over the other?",
                "keywords": ["relational", "document", "schema", "ACID", "BASE", "scalability", "joins", "denormalization"],
                "rubric": ["Key differences explained", "Use cases for each", "Trade-offs identified", "Real-world examples"],
                "pattern": "Database Selection", "difficulty": "easy",
            },
            {
                "question": "What is an ORM? Explain its benefits and drawbacks with examples.",
                "keywords": ["ORM", "object relational mapping", "SQLAlchemy", "Hibernate", "N+1", "migration", "query"],
                "rubric": ["ORM concept", "Benefits", "N+1 problem", "When to use raw SQL"],
                "pattern": "Database Selection", "difficulty": "easy",
            },
            {
                "question": "Explain authentication vs authorization. How would you implement JWT-based auth?",
                "keywords": ["authentication", "authorization", "JWT", "token", "refresh", "middleware", "RBAC", "OAuth"],
                "rubric": ["Clear distinction", "JWT structure", "Token lifecycle", "Security considerations"],
                "pattern": "Security", "difficulty": "medium",
            },
            {
                "question": "What are microservices? Compare with monolithic architecture and explain when to use each.",
                "keywords": ["microservices", "monolith", "decoupled", "API gateway", "service discovery", "latency", "deployment"],
                "rubric": ["Architecture comparison", "Trade-offs", "Communication patterns", "When to migrate"],
                "pattern": "Architecture Patterns", "difficulty": "medium",
            },
            {
                "question": "Explain database indexing. How do indexes work and when can they hurt performance?",
                "keywords": ["index", "B-tree", "hash", "composite", "query plan", "write overhead", "selectivity"],
                "rubric": ["Index types", "How they speed reads", "Write overhead", "When not to index"],
                "pattern": "Database Selection", "difficulty": "medium",
            },
            {
                "question": "What is caching? Explain cache invalidation strategies and tools like Redis.",
                "keywords": ["cache", "Redis", "TTL", "LRU", "write-through", "cache-aside", "invalidation", "consistency"],
                "rubric": ["Caching purpose", "Invalidation strategies", "Redis use cases", "Consistency challenges"],
                "pattern": "Caching Strategy", "difficulty": "medium",
            },
            {
                "question": "Explain concurrency and multithreading. How do you handle race conditions?",
                "keywords": ["thread", "process", "mutex", "lock", "deadlock", "race condition", "async", "semaphore"],
                "rubric": ["Concurrency concepts", "Race condition handling", "Lock mechanisms", "Async patterns"],
                "pattern": "Concurrency", "difficulty": "medium",
            },
            {
                "question": "What is message queuing? Explain when and how to use Kafka, RabbitMQ, or SQS.",
                "keywords": ["queue", "Kafka", "RabbitMQ", "async", "producer", "consumer", "dead letter", "at-least-once"],
                "rubric": ["Queue concepts", "Tool comparison", "Delivery guarantees", "Use cases"],
                "pattern": "Message Queues", "difficulty": "hard",
            },
            {
                "question": "Design a rate-limited, idempotent payment processing API. What patterns would you use?",
                "keywords": ["idempotent", "rate limit", "retry", "transaction", "saga", "eventual consistency", "webhook"],
                "rubric": ["Idempotency design", "Rate limiting approach", "Transaction handling", "Error recovery"],
                "pattern": "API Design", "difficulty": "hard",
            },
            {
                "question": "Explain the CQRS and Event Sourcing patterns. When would you use them?",
                "keywords": ["CQRS", "event sourcing", "read model", "write model", "event store", "projection", "eventual consistency"],
                "rubric": ["Pattern definitions", "When to use", "Trade-offs", "Implementation challenges"],
                "pattern": "Architecture Patterns", "difficulty": "hard",
            },
            {
                "question": "How would you design a database migration strategy for a high-traffic production system with zero downtime?",
                "keywords": ["migration", "zero downtime", "backward compatible", "dual write", "shadow", "rollback", "blue-green"],
                "rubric": ["Migration strategy", "Backward compatibility", "Rollback plan", "Testing approach"],
                "pattern": "Database Selection", "difficulty": "hard",
            },
        ],
        "frontend": [
            {
                "question": "What is the DOM? Explain how browsers render a web page.",
                "keywords": ["DOM", "render tree", "CSSOM", "layout", "paint", "reflow", "repaint"],
                "rubric": ["DOM explanation", "Rendering pipeline", "Reflow vs repaint", "Performance impact"],
                "pattern": "Browser Fundamentals", "difficulty": "easy",
            },
            {
                "question": "Explain CSS Flexbox and Grid. When would you use one over the other?",
                "keywords": ["flexbox", "grid", "layout", "responsive", "axis", "gap", "template", "align"],
                "rubric": ["Flexbox basics", "Grid basics", "Use cases for each", "Responsive design"],
                "pattern": "CSS Layout", "difficulty": "easy",
            },
            {
                "question": "What is the virtual DOM and how does it improve performance in React?",
                "keywords": ["virtual DOM", "reconciliation", "diffing", "real DOM", "batch updates", "fiber", "performance"],
                "rubric": ["Virtual DOM concept", "Diffing algorithm", "Performance benefits", "Limitations"],
                "pattern": "Component Architecture", "difficulty": "easy",
            },
            {
                "question": "Explain React hooks. What are useState, useEffect, and useRef? When do you use each?",
                "keywords": ["useState", "useEffect", "useRef", "hook", "lifecycle", "side effect", "closure", "dependency"],
                "rubric": ["Hook basics", "useEffect lifecycle", "Dependency array", "Common pitfalls"],
                "pattern": "Component Architecture", "difficulty": "medium",
            },
            {
                "question": "What is state management? Compare Context API, Redux, and Zustand.",
                "keywords": ["state", "Redux", "Context", "Zustand", "global state", "store", "action", "reducer"],
                "rubric": ["State management need", "Tool comparison", "Trade-offs", "When to use each"],
                "pattern": "State Management", "difficulty": "medium",
            },
            {
                "question": "Explain web accessibility (a11y). What are ARIA roles and how do you test for accessibility?",
                "keywords": ["a11y", "ARIA", "screen reader", "semantic HTML", "keyboard navigation", "contrast", "WCAG"],
                "rubric": ["A11y importance", "ARIA usage", "Testing tools", "Common issues"],
                "pattern": "Accessibility", "difficulty": "medium",
            },
            {
                "question": "How would you optimize the performance of a React application? Explain key techniques.",
                "keywords": ["memo", "useMemo", "useCallback", "lazy loading", "code splitting", "bundle size", "profiler"],
                "rubric": ["Memoization techniques", "Code splitting", "Bundle optimization", "Measuring performance"],
                "pattern": "Performance", "difficulty": "medium",
            },
            {
                "question": "What is server-side rendering (SSR)? Compare SSR, CSR, and SSG with examples.",
                "keywords": ["SSR", "CSR", "SSG", "Next.js", "hydration", "SEO", "TTFB", "ISR"],
                "rubric": ["Rendering strategies", "Trade-offs", "SEO impact", "Framework examples"],
                "pattern": "Architecture", "difficulty": "hard",
            },
            {
                "question": "Explain micro-frontends. How would you design a micro-frontend architecture?",
                "keywords": ["micro-frontend", "module federation", "iframe", "web components", "routing", "shared state"],
                "rubric": ["Concept explained", "Implementation approaches", "Communication patterns", "Trade-offs"],
                "pattern": "Architecture", "difficulty": "hard",
            },
            {
                "question": "How do you handle authentication and security in a single-page application?",
                "keywords": ["XSS", "CSRF", "JWT", "httpOnly", "CORS", "CSP", "sanitize", "token storage"],
                "rubric": ["XSS prevention", "Token storage", "CORS setup", "Security headers"],
                "pattern": "Security", "difficulty": "hard",
            },
        ],
        "fullstack": [
            {
                "question": "Explain the client-server architecture. How does a web request flow from browser to database and back?",
                "keywords": ["client", "server", "HTTP", "DNS", "request", "response", "TCP", "database"],
                "rubric": ["Request flow", "DNS resolution", "Server processing", "Response lifecycle"],
                "pattern": "Full Stack Architecture", "difficulty": "easy",
            },
            {
                "question": "What is MVC? Explain with an example of how a full-stack app is structured.",
                "keywords": ["MVC", "model", "view", "controller", "separation", "routing", "template"],
                "rubric": ["MVC components", "Separation of concerns", "Practical example", "Alternatives"],
                "pattern": "Full Stack Architecture", "difficulty": "easy",
            },
            {
                "question": "How would you design an authentication system for a web application? Discuss tokens vs sessions.",
                "keywords": ["JWT", "session", "cookie", "token", "OAuth", "refresh token", "stateless", "XSS", "CSRF"],
                "rubric": ["Token vs session comparison", "Security considerations", "Implementation approach", "Trade-offs"],
                "pattern": "Full Stack Architecture", "difficulty": "medium",
            },
            {
                "question": "Explain how you would set up a full-stack project with React frontend and Node/Python backend. What tools do you use?",
                "keywords": ["React", "API", "CORS", "proxy", "build", "deploy", "environment", "testing"],
                "rubric": ["Project structure", "API communication", "Development workflow", "Deployment strategy"],
                "pattern": "Full Stack Architecture", "difficulty": "medium",
            },
            {
                "question": "What is GraphQL? Compare it with REST and explain when you would choose one over the other.",
                "keywords": ["GraphQL", "REST", "query", "mutation", "schema", "over-fetching", "resolver", "subscription"],
                "rubric": ["GraphQL basics", "REST comparison", "Trade-offs", "Use cases"],
                "pattern": "API Design", "difficulty": "medium",
            },
            {
                "question": "How do you handle real-time features in a full-stack app? Compare WebSockets, SSE, and polling.",
                "keywords": ["WebSocket", "SSE", "polling", "real-time", "bidirectional", "connection", "scalability"],
                "rubric": ["Technology comparison", "Use cases", "Scalability concerns", "Implementation approach"],
                "pattern": "Full Stack Architecture", "difficulty": "medium",
            },
            {
                "question": "Explain database transactions and ACID properties. How do you handle them in a web application?",
                "keywords": ["ACID", "transaction", "atomicity", "consistency", "isolation", "durability", "rollback"],
                "rubric": ["ACID explained", "Transaction management", "Isolation levels", "Error handling"],
                "pattern": "Database", "difficulty": "medium",
            },
            {
                "question": "How would you design and implement a file upload system that handles large files reliably?",
                "keywords": ["multipart", "chunked", "S3", "presigned URL", "progress", "retry", "validation", "virus scan"],
                "rubric": ["Upload strategy", "Large file handling", "Storage choice", "Security validation"],
                "pattern": "Full Stack Architecture", "difficulty": "hard",
            },
            {
                "question": "Design a full-stack e-commerce checkout flow. Cover frontend, API, payment processing, and error handling.",
                "keywords": ["checkout", "payment", "cart", "idempotent", "inventory", "webhook", "retry", "UX"],
                "rubric": ["End-to-end flow", "Payment integration", "Error handling", "UX considerations"],
                "pattern": "Full Stack Architecture", "difficulty": "hard",
            },
            {
                "question": "How would you implement a multi-tenant SaaS application? Discuss database strategies and isolation.",
                "keywords": ["multi-tenant", "SaaS", "shared database", "schema per tenant", "isolation", "billing", "security"],
                "rubric": ["Tenancy models", "Data isolation", "Security approach", "Scaling considerations"],
                "pattern": "Architecture", "difficulty": "hard",
            },
        ],
        "devops_sre": [
            {
                "question": "What is DevOps? Explain the key principles and how it differs from traditional software development.",
                "keywords": ["automation", "CI/CD", "collaboration", "infrastructure as code", "monitoring", "culture", "feedback loop"],
                "rubric": ["Core principles", "Cultural aspect", "Technical practices", "Benefits explained"],
                "pattern": "DevOps Fundamentals", "difficulty": "easy",
            },
            {
                "question": "Explain the difference between containers and virtual machines. When would you use each?",
                "keywords": ["Docker", "container", "VM", "hypervisor", "kernel", "isolation", "overhead", "portability"],
                "rubric": ["Architecture differences", "Resource overhead comparison", "Use cases", "Security considerations"],
                "pattern": "Container Orchestration", "difficulty": "easy",
            },
            {
                "question": "What is Docker? Explain images, containers, volumes, and networking basics.",
                "keywords": ["image", "container", "Dockerfile", "volume", "network", "registry", "layer", "build"],
                "rubric": ["Image vs container", "Dockerfile basics", "Volume persistence", "Networking modes"],
                "pattern": "Container Orchestration", "difficulty": "easy",
            },
            {
                "question": "What is a CI/CD pipeline? Explain the stages and why each stage is important.",
                "keywords": ["build", "test", "deploy", "continuous integration", "continuous delivery", "automation", "artifact", "gate"],
                "rubric": ["Stage definitions", "Automation benefits", "Quality gates", "Deployment strategies"],
                "pattern": "CI/CD Pipelines", "difficulty": "easy",
            },
            {
                "question": "Explain Kubernetes architecture. What are pods, services, deployments, and namespaces?",
                "keywords": ["pod", "service", "deployment", "namespace", "node", "cluster", "control plane", "kubelet"],
                "rubric": ["Core components", "Pod lifecycle", "Service networking", "Deployment strategies"],
                "pattern": "Container Orchestration", "difficulty": "medium",
            },
            {
                "question": "What is Infrastructure as Code (IaC)? Compare Terraform and Ansible.",
                "keywords": ["IaC", "Terraform", "Ansible", "declarative", "imperative", "state", "idempotent", "provider"],
                "rubric": ["IaC concept", "Declarative vs imperative", "Tool comparison", "State management"],
                "pattern": "Infrastructure as Code", "difficulty": "medium",
            },
            {
                "question": "Explain monitoring and observability. What are the three pillars and what tools would you use?",
                "keywords": ["logs", "metrics", "traces", "Prometheus", "Grafana", "ELK", "alerting", "SLO", "SLI"],
                "rubric": ["Three pillars", "Tool choices", "Alerting strategy", "SLO/SLI concepts"],
                "pattern": "Monitoring & Observability", "difficulty": "medium",
            },
            {
                "question": "How would you implement a zero-downtime deployment? Explain blue-green and canary strategies.",
                "keywords": ["blue-green", "canary", "rolling update", "rollback", "health check", "load balancer", "traffic shifting"],
                "rubric": ["Multiple strategies", "Rollback mechanism", "Health checking", "Traffic management"],
                "pattern": "CI/CD Pipelines", "difficulty": "medium",
            },
            {
                "question": "What are SLOs, SLIs, and SLAs? How do you define and monitor them for a production service?",
                "keywords": ["SLO", "SLI", "SLA", "error budget", "availability", "latency", "reliability", "alert"],
                "rubric": ["Clear definitions", "How to measure", "Error budget concept", "Actionable alerts"],
                "pattern": "Monitoring & Observability", "difficulty": "medium",
            },
            {
                "question": "Explain incident management. Walk through how you would handle a production outage from detection to postmortem.",
                "keywords": ["incident", "triage", "severity", "communication", "mitigation", "postmortem", "blameless", "runbook"],
                "rubric": ["Detection to resolution", "Communication plan", "Severity classification", "Blameless postmortem"],
                "pattern": "Incident Response", "difficulty": "hard",
            },
            {
                "question": "Design a highly available and scalable CI/CD pipeline for a microservices architecture with 50+ services.",
                "keywords": ["microservices", "pipeline", "parallel", "artifact", "registry", "GitOps", "ArgoCD", "dependency"],
                "rubric": ["Pipeline architecture", "Parallelism", "Artifact management", "Dependency handling"],
                "pattern": "CI/CD Pipelines", "difficulty": "hard",
            },
            {
                "question": "What is chaos engineering? How would you implement it and what tools would you use?",
                "keywords": ["chaos", "resilience", "fault injection", "Chaos Monkey", "Litmus", "game day", "blast radius", "hypothesis"],
                "rubric": ["Concept explained", "Tool knowledge", "Experiment design", "Blast radius management"],
                "pattern": "Reliability Engineering", "difficulty": "hard",
            },
            {
                "question": "How would you design a multi-region disaster recovery strategy? Explain RPO and RTO.",
                "keywords": ["disaster recovery", "RPO", "RTO", "multi-region", "failover", "replication", "backup", "active-active"],
                "rubric": ["RPO/RTO definitions", "DR strategies", "Failover mechanisms", "Testing approach"],
                "pattern": "Reliability Engineering", "difficulty": "hard",
            },
        ],
        "data_engineer": [
            {
                "question": "What is ETL? Explain the Extract, Transform, Load process with a real example.",
                "keywords": ["ETL", "extract", "transform", "load", "pipeline", "data warehouse", "staging"],
                "rubric": ["ETL stages", "Real example", "Tool choices", "Error handling"],
                "pattern": "Data Pipelines", "difficulty": "easy",
            },
            {
                "question": "Explain the difference between a data warehouse and a data lake. When would you use each?",
                "keywords": ["warehouse", "data lake", "schema", "structured", "unstructured", "analytics", "cost"],
                "rubric": ["Clear definitions", "Use cases", "Schema differences", "Cost considerations"],
                "pattern": "Data Architecture", "difficulty": "easy",
            },
            {
                "question": "What is SQL? Write a query to find the top 5 customers by total order amount.",
                "keywords": ["SQL", "JOIN", "GROUP BY", "ORDER BY", "aggregate", "subquery", "index"],
                "rubric": ["Correct query", "Join usage", "Aggregation", "Performance awareness"],
                "pattern": "SQL", "difficulty": "easy",
            },
            {
                "question": "Explain the difference between batch and stream processing. When would you use each?",
                "keywords": ["batch", "stream", "real-time", "latency", "throughput", "Kafka", "Spark", "Flink"],
                "rubric": ["Processing model differences", "Latency vs throughput", "Use cases", "Technology choices"],
                "pattern": "Stream Processing", "difficulty": "medium",
            },
            {
                "question": "What is Apache Kafka? Explain topics, partitions, consumer groups, and offset management.",
                "keywords": ["Kafka", "topic", "partition", "consumer group", "offset", "broker", "replication"],
                "rubric": ["Core concepts", "Partitioning", "Consumer groups", "Offset management"],
                "pattern": "Stream Processing", "difficulty": "medium",
            },
            {
                "question": "Explain data modeling techniques. What are star schema and snowflake schema?",
                "keywords": ["star schema", "snowflake", "fact table", "dimension", "normalization", "denormalization"],
                "rubric": ["Schema types", "Fact vs dimension", "Trade-offs", "Use cases"],
                "pattern": "Data Modeling", "difficulty": "medium",
            },
            {
                "question": "What is Apache Spark? Explain RDDs, DataFrames, and when to use Spark over MapReduce.",
                "keywords": ["Spark", "RDD", "DataFrame", "lazy evaluation", "partition", "shuffle", "in-memory"],
                "rubric": ["Spark architecture", "RDD vs DataFrame", "Lazy evaluation", "Performance benefits"],
                "pattern": "Big Data Processing", "difficulty": "medium",
            },
            {
                "question": "How do you ensure data quality in a pipeline? What tests and validations would you implement?",
                "keywords": ["data quality", "validation", "schema check", "null", "duplicate", "freshness", "Great Expectations"],
                "rubric": ["Quality dimensions", "Validation types", "Tool knowledge", "Monitoring approach"],
                "pattern": "Data Quality", "difficulty": "medium",
            },
            {
                "question": "Design a data pipeline that ingests clickstream data from a website and makes it available for analytics.",
                "keywords": ["clickstream", "ingestion", "Kafka", "Spark", "warehouse", "partitioning", "schema evolution"],
                "rubric": ["Pipeline architecture", "Ingestion strategy", "Storage design", "Query optimization"],
                "pattern": "Data Pipelines", "difficulty": "hard",
            },
            {
                "question": "Explain data partitioning and bucketing. How do they improve query performance in large datasets?",
                "keywords": ["partition", "bucket", "Hive", "predicate pushdown", "scan", "skew", "cardinality"],
                "rubric": ["Partitioning strategy", "Bucketing concept", "Performance impact", "Skew handling"],
                "pattern": "Data Architecture", "difficulty": "hard",
            },
        ],
        "ml_engineer": [
            {
                "question": "What is machine learning? Explain supervised, unsupervised, and reinforcement learning with examples.",
                "keywords": ["supervised", "unsupervised", "reinforcement", "classification", "regression", "clustering", "label"],
                "rubric": ["Three types explained", "Examples for each", "Use cases", "Key differences"],
                "pattern": "ML Fundamentals", "difficulty": "easy",
            },
            {
                "question": "Explain the bias-variance trade-off. How does it affect model performance?",
                "keywords": ["bias", "variance", "trade-off", "overfitting", "underfitting", "complexity", "generalization"],
                "rubric": ["Clear explanation", "Relationship to fitting", "Visual understanding", "Practical impact"],
                "pattern": "ML Fundamentals", "difficulty": "easy",
            },
            {
                "question": "What are common evaluation metrics for classification? Explain precision, recall, F1, and AUC.",
                "keywords": ["precision", "recall", "F1", "AUC", "ROC", "confusion matrix", "threshold"],
                "rubric": ["Metric definitions", "When to use each", "Trade-offs", "Threshold impact"],
                "pattern": "Model Evaluation", "difficulty": "easy",
            },
            {
                "question": "Explain overfitting and underfitting. How do you detect and prevent them?",
                "keywords": ["overfitting", "underfitting", "regularization", "cross-validation", "bias", "variance", "dropout"],
                "rubric": ["Define both concepts", "Detection methods", "Prevention techniques", "Bias-variance trade-off"],
                "pattern": "Model Training Pipeline", "difficulty": "medium",
            },
            {
                "question": "Explain feature engineering. What techniques do you use to create useful features from raw data?",
                "keywords": ["feature", "encoding", "scaling", "one-hot", "embedding", "missing values", "feature selection"],
                "rubric": ["Techniques listed", "Encoding methods", "Handling missing data", "Feature selection"],
                "pattern": "Feature Engineering", "difficulty": "medium",
            },
            {
                "question": "What is a neural network? Explain layers, activation functions, and backpropagation.",
                "keywords": ["neural network", "layer", "activation", "ReLU", "sigmoid", "backpropagation", "gradient", "loss"],
                "rubric": ["Network architecture", "Activation functions", "Backpropagation", "Training process"],
                "pattern": "Deep Learning", "difficulty": "medium",
            },
            {
                "question": "Explain MLOps. How do you deploy, monitor, and maintain ML models in production?",
                "keywords": ["MLOps", "deployment", "serving", "monitoring", "drift", "retraining", "pipeline", "CI/CD"],
                "rubric": ["Deployment strategies", "Monitoring for drift", "Retraining triggers", "Pipeline automation"],
                "pattern": "Model Serving", "difficulty": "medium",
            },
            {
                "question": "What is transfer learning? Explain when and how to use pre-trained models.",
                "keywords": ["transfer learning", "pre-trained", "fine-tune", "BERT", "ResNet", "frozen layers", "domain adaptation"],
                "rubric": ["Concept explained", "When to use", "Fine-tuning approach", "Practical examples"],
                "pattern": "Deep Learning", "difficulty": "hard",
            },
            {
                "question": "Design an ML system to detect fraudulent transactions in real-time. What's your approach?",
                "keywords": ["fraud", "real-time", "feature store", "model serving", "threshold", "false positive", "ensemble"],
                "rubric": ["System architecture", "Feature engineering", "Real-time serving", "Evaluation approach"],
                "pattern": "ML System Design", "difficulty": "hard",
            },
            {
                "question": "Explain A/B testing for ML models. How do you decide if a new model is better than the existing one?",
                "keywords": ["A/B test", "statistical significance", "sample size", "metric", "guardrail", "rollout", "confidence"],
                "rubric": ["Testing methodology", "Statistical rigor", "Metric selection", "Rollout strategy"],
                "pattern": "Experiment Design", "difficulty": "hard",
            },
        ],
        "mobile": [
            {
                "question": "What is the mobile app lifecycle? Explain the different states an app goes through.",
                "keywords": ["lifecycle", "foreground", "background", "suspended", "terminated", "launch", "state"],
                "rubric": ["Lifecycle states", "State transitions", "Background handling", "Memory management"],
                "pattern": "Mobile Architecture", "difficulty": "easy",
            },
            {
                "question": "Explain the difference between native, hybrid, and cross-platform mobile development.",
                "keywords": ["native", "hybrid", "cross-platform", "React Native", "Flutter", "performance", "UI"],
                "rubric": ["Three approaches", "Performance comparison", "Use cases", "Trade-offs"],
                "pattern": "Mobile Architecture", "difficulty": "easy",
            },
            {
                "question": "How do you store data locally in a mobile app? Compare different storage options.",
                "keywords": ["SQLite", "SharedPreferences", "UserDefaults", "Realm", "file storage", "keychain", "encryption"],
                "rubric": ["Storage options", "When to use each", "Security considerations", "Performance"],
                "pattern": "Offline Storage", "difficulty": "easy",
            },
            {
                "question": "How do you handle offline functionality in a mobile app? Discuss data synchronization strategies.",
                "keywords": ["offline", "cache", "sync", "conflict resolution", "local storage", "SQLite", "queue"],
                "rubric": ["Offline storage approach", "Sync strategy", "Conflict resolution", "User experience"],
                "pattern": "Offline Storage", "difficulty": "medium",
            },
            {
                "question": "Explain mobile UI patterns. What are navigation patterns and how do you choose between them?",
                "keywords": ["tab bar", "drawer", "stack", "modal", "navigation", "deep link", "gesture"],
                "rubric": ["Navigation patterns", "Platform conventions", "Deep linking", "User experience"],
                "pattern": "UI Patterns", "difficulty": "medium",
            },
            {
                "question": "How do you optimize mobile app performance? Discuss memory, battery, and network optimization.",
                "keywords": ["memory", "battery", "network", "lazy loading", "image caching", "profiling", "background"],
                "rubric": ["Memory management", "Battery optimization", "Network efficiency", "Profiling tools"],
                "pattern": "Performance Optimization", "difficulty": "medium",
            },
            {
                "question": "What is mobile testing? Explain how you would test a mobile app across different devices.",
                "keywords": ["unit test", "UI test", "device farm", "emulator", "real device", "regression", "accessibility"],
                "rubric": ["Testing levels", "Device strategy", "Automation approach", "CI/CD integration"],
                "pattern": "Mobile Testing", "difficulty": "medium",
            },
            {
                "question": "How do you handle push notifications in a mobile app? Explain the architecture.",
                "keywords": ["push notification", "FCM", "APNs", "token", "topic", "silent push", "permission"],
                "rubric": ["Notification architecture", "Token management", "Permission handling", "Delivery reliability"],
                "pattern": "Mobile Architecture", "difficulty": "hard",
            },
            {
                "question": "Design a mobile app that works seamlessly offline and syncs when connectivity returns.",
                "keywords": ["offline-first", "CRDT", "queue", "conflict resolution", "delta sync", "retry"],
                "rubric": ["Offline-first design", "Sync strategy", "Conflict resolution", "UX during sync"],
                "pattern": "Offline Storage", "difficulty": "hard",
            },
            {
                "question": "How would you architect a mobile app for a million+ daily active users?",
                "keywords": ["architecture", "MVVM", "clean architecture", "modular", "dependency injection", "scalable"],
                "rubric": ["Architecture pattern", "Modularity", "Scalability", "Testability"],
                "pattern": "Mobile Architecture", "difficulty": "hard",
            },
        ],
        "platform": [
            {
                "question": "What is an API? Explain REST, GraphQL, and gRPC. When would you choose each?",
                "keywords": ["API", "REST", "GraphQL", "gRPC", "protocol buffer", "HTTP", "contract"],
                "rubric": ["API types", "Comparison", "Use cases", "Trade-offs"],
                "pattern": "API Design", "difficulty": "easy",
            },
            {
                "question": "What is a distributed system? Explain the key challenges of building distributed systems.",
                "keywords": ["distributed", "network partition", "consistency", "availability", "latency", "failure"],
                "rubric": ["Definition", "Key challenges", "CAP theorem", "Practical examples"],
                "pattern": "Distributed Systems", "difficulty": "easy",
            },
            {
                "question": "Explain DNS and how domain name resolution works step by step.",
                "keywords": ["DNS", "resolver", "root server", "TLD", "A record", "CNAME", "TTL", "cache"],
                "rubric": ["Resolution steps", "Record types", "Caching", "Performance impact"],
                "pattern": "Networking", "difficulty": "easy",
            },
            {
                "question": "How would you design an API that supports backward compatibility across multiple versions?",
                "keywords": ["versioning", "backward compatible", "deprecation", "migration", "contract", "breaking change"],
                "rubric": ["Versioning strategy", "Backward compatibility", "Deprecation process", "Migration plan"],
                "pattern": "SDK Design", "difficulty": "medium",
            },
            {
                "question": "Explain service mesh. What is Istio/Envoy and when would you use a service mesh?",
                "keywords": ["service mesh", "Istio", "Envoy", "sidecar", "mTLS", "traffic management", "observability"],
                "rubric": ["Service mesh concept", "Sidecar pattern", "Traffic management", "When to use"],
                "pattern": "Service Mesh", "difficulty": "medium",
            },
            {
                "question": "What is a developer platform? How would you measure developer experience (DX)?",
                "keywords": ["developer platform", "DX", "SDK", "documentation", "onboarding", "feedback", "metrics"],
                "rubric": ["Platform definition", "DX metrics", "Onboarding experience", "Feedback loops"],
                "pattern": "Developer Experience", "difficulty": "medium",
            },
            {
                "question": "Explain multi-tenancy. How would you design a platform that serves multiple teams/customers?",
                "keywords": ["multi-tenancy", "isolation", "quota", "noisy neighbor", "resource limits", "namespace"],
                "rubric": ["Tenancy models", "Isolation strategies", "Resource management", "Security"],
                "pattern": "Platform Architecture", "difficulty": "medium",
            },
            {
                "question": "How would you design a rate limiting and quota system for a platform API?",
                "keywords": ["rate limit", "quota", "token bucket", "sliding window", "distributed", "fairness"],
                "rubric": ["Algorithm choice", "Distributed considerations", "Fairness", "User experience"],
                "pattern": "API Design", "difficulty": "hard",
            },
            {
                "question": "Design an internal platform that enables teams to deploy services with one command.",
                "keywords": ["platform", "self-service", "abstraction", "template", "guardrails", "automation"],
                "rubric": ["Platform architecture", "Self-service design", "Guardrails", "Extensibility"],
                "pattern": "Platform Architecture", "difficulty": "hard",
            },
            {
                "question": "How would you design an SDK for a distributed tracing system? What API would you expose?",
                "keywords": ["SDK", "tracing", "span", "context propagation", "OpenTelemetry", "sampling", "overhead"],
                "rubric": ["API design", "Context propagation", "Performance overhead", "Ease of adoption"],
                "pattern": "SDK Design", "difficulty": "hard",
            },
        ],
        "qa_sdet": [
            {
                "question": "What is the testing pyramid? Explain the different levels and their purpose.",
                "keywords": ["unit", "integration", "e2e", "pyramid", "cost", "speed", "coverage", "maintenance"],
                "rubric": ["Three levels explained", "Cost vs speed trade-off", "Coverage strategy", "Practical examples"],
                "pattern": "Test Strategy", "difficulty": "easy",
            },
            {
                "question": "Explain the difference between manual testing and automation testing. When would you choose one over the other?",
                "keywords": ["manual", "automation", "exploratory", "regression", "ROI", "maintenance", "repeatability"],
                "rubric": ["Clear distinction", "When to automate", "When manual is better", "ROI considerations"],
                "pattern": "Test Strategy", "difficulty": "easy",
            },
            {
                "question": "What are the different types of software testing? Give examples of when you would use each.",
                "keywords": ["functional", "non-functional", "smoke", "regression", "performance", "security", "usability"],
                "rubric": ["Multiple types listed", "Use cases for each", "Practical examples", "Priority understanding"],
                "pattern": "Test Strategy", "difficulty": "easy",
            },
            {
                "question": "How do you write a good test case? What makes a test case effective?",
                "keywords": ["precondition", "steps", "expected result", "independent", "repeatable", "clear", "atomic"],
                "rubric": ["Test case structure", "Independence", "Clear expected results", "Edge case coverage"],
                "pattern": "Test Strategy", "difficulty": "easy",
            },
            {
                "question": "What is Selenium? Explain its architecture and how it interacts with browsers.",
                "keywords": ["WebDriver", "browser driver", "HTTP", "JSON wire protocol", "element", "locator", "grid"],
                "rubric": ["Architecture explained", "WebDriver role", "Browser interaction", "Grid concept"],
                "pattern": "Test Automation", "difficulty": "medium",
            },
            {
                "question": "What is Playwright and how does it differ from Selenium? When would you choose one over the other?",
                "keywords": ["Playwright", "Selenium", "auto-wait", "browser context", "multi-browser", "speed", "modern"],
                "rubric": ["Key differences", "Auto-wait mechanism", "Performance comparison", "Use case recommendations"],
                "pattern": "Test Automation", "difficulty": "medium",
            },
            {
                "question": "Explain the Page Object Model design pattern. Why is it important in test automation?",
                "keywords": ["POM", "page object", "encapsulation", "maintainability", "reusability", "separation of concerns"],
                "rubric": ["Pattern explained", "Benefits listed", "Maintainability impact", "Example structure"],
                "pattern": "Test Automation", "difficulty": "medium",
            },
            {
                "question": "How would you design an API test suite for a REST API? What would you test?",
                "keywords": ["status code", "response body", "headers", "authentication", "edge cases", "contract", "schema"],
                "rubric": ["Test categories", "Status code validation", "Schema validation", "Negative testing"],
                "pattern": "API Testing", "difficulty": "medium",
            },
            {
                "question": "What is CI/CD and how does test automation fit into the pipeline?",
                "keywords": ["continuous integration", "continuous delivery", "pipeline", "trigger", "gates", "parallel", "reporting"],
                "rubric": ["CI/CD explained", "Test stages in pipeline", "Quality gates", "Reporting and feedback"],
                "pattern": "CI/CD Integration", "difficulty": "medium",
            },
            {
                "question": "How do you handle flaky tests? What strategies do you use to identify and fix them?",
                "keywords": ["flaky", "retry", "wait", "isolation", "race condition", "root cause", "quarantine"],
                "rubric": ["Definition of flaky", "Root cause analysis", "Fix strategies", "Prevention approaches"],
                "pattern": "Test Automation", "difficulty": "medium",
            },
            {
                "question": "Design a test automation framework from scratch for a web application. What components would you include?",
                "keywords": ["framework", "page object", "reporting", "config", "data-driven", "logging", "parallel", "reusable"],
                "rubric": ["Framework layers", "Design patterns used", "Reporting mechanism", "Scalability considerations"],
                "pattern": "Test Automation", "difficulty": "hard",
            },
            {
                "question": "How would you approach performance testing for a web application? What tools and metrics would you use?",
                "keywords": ["load test", "stress test", "JMeter", "k6", "Locust", "response time", "throughput", "bottleneck"],
                "rubric": ["Test types explained", "Tool selection", "Key metrics", "Bottleneck identification"],
                "pattern": "Performance Testing", "difficulty": "hard",
            },
            {
                "question": "Explain shift-left testing. How would you implement it in an organization that currently tests only at the end?",
                "keywords": ["shift-left", "early testing", "unit test", "code review", "static analysis", "TDD", "culture"],
                "rubric": ["Concept explained", "Implementation plan", "Cultural change", "Measurable benefits"],
                "pattern": "Test Strategy", "difficulty": "hard",
            },
        ],
    },
}


def generate_quick_assessment(company, role, level):
    """Generate 10 questions for Quick Assessment — heavily role-focused.

    Distribution:
    - 5 domain-specific questions (role-focused, easy → hard)
    - 2 coding questions (Phone Screen)
    - 1 system design question
    - 1 behavioral question
    - 1 bar raiser / general question

    Returns:
        {
            'questions': [{id, question, keywords, rubric, pattern, difficulty, round_type, answer_mode}, ...],
            'total_questions': int,
            'company': str,
            'role': str,
            'level': str,
        }
    """
    questions = []
    q_id = 1

    # 5 domain-specific questions (role-focused — the core of the assessment)
    role_key = role.lower()
    domain_qs = list(QUESTION_TEMPLATES["domain_specific"].get(role_key, []))
    random.shuffle(domain_qs)
    # Try to pick a mix of difficulties
    easy = [q for q in domain_qs if q.get("difficulty") == "easy"]
    medium = [q for q in domain_qs if q.get("difficulty") == "medium"]
    hard = [q for q in domain_qs if q.get("difficulty") == "hard"]
    domain_picked = []
    for pool in [easy[:2], medium[:2], hard[:1]]:
        domain_picked.extend(pool)
    # Fill remaining from shuffled pool if not enough
    remaining_domain = [q for q in domain_qs if q not in domain_picked]
    while len(domain_picked) < 5 and remaining_domain:
        domain_picked.append(remaining_domain.pop(0))
    for q in domain_picked[:5]:
        questions.append({**q, "id": q_id, "round_type": "domain_specific", "answer_mode": "hybrid"})
        q_id += 1

    # 2 coding questions (Phone Screen)
    coding_qs = list(QUESTION_TEMPLATES["phone_screen"]["coding"])
    random.shuffle(coding_qs)
    for q in coding_qs[:2]:
        questions.append({**q, "id": q_id, "round_type": "phone_screen", "answer_mode": "code"})
        q_id += 1

    # 1 system design question
    design_qs = list(QUESTION_TEMPLATES["system_design"]["architecture"])
    random.shuffle(design_qs)
    questions.append({**design_qs[0], "id": q_id, "round_type": "system_design", "answer_mode": "voice"})
    q_id += 1

    # 1 behavioral question
    behavioral_qs = list(QUESTION_TEMPLATES["behavioral"]["star"])
    random.shuffle(behavioral_qs)
    questions.append({**behavioral_qs[0], "id": q_id, "round_type": "behavioral", "answer_mode": "voice"})
    q_id += 1

    # 1 more domain question if available, else behavioral
    extra_domain = [q for q in domain_qs if q not in domain_picked]
    if extra_domain:
        questions.append({**extra_domain[0], "id": q_id, "round_type": "domain_specific", "answer_mode": "hybrid"})
    elif len(behavioral_qs) > 1:
        questions.append({**behavioral_qs[1], "id": q_id, "round_type": "behavioral", "answer_mode": "voice"})
    q_id += 1

    # Shuffle all questions so domain isn't always first
    random.shuffle(questions)
    # Re-assign IDs after shuffle
    for i, q in enumerate(questions):
        q["id"] = i + 1

    return {
        "questions": questions[:10],
        "total_questions": len(questions[:10]),
        "company": company,
        "role": role,
        "level": level,
    }


def score_assessment(answers, questions):
    """Score all answers from a Quick Assessment.

    Args:
        answers: List of {question_id, answer_text}
        questions: List of question dicts from generate_quick_assessment

    Returns:
        {
            'overall_score': 0-100,
            'per_question': [{question_id, score, thinking, accuracy, quality, pattern, round_type}, ...],
            'per_round': {round_type: avg_score},
            'weak_patterns': [pattern names with score < 50],
            'strong_patterns': [pattern names with score >= 70],
            'recommended_focus': [top 3 weak areas],
        }
    """
    q_map = {q["id"]: q for q in questions}
    per_question = []
    round_scores = {}
    pattern_scores = {}

    for answer in answers:
        qid = answer.get("question_id")
        q = q_map.get(qid)
        if not q:
            continue

        result = dual_score(
            answer.get("answer_text", ""),
            expected_keywords=q.get("keywords", []),
            rubric_points=q.get("rubric", []),
        )

        quality = classify_answer_quality(result["total_score"])
        pattern = q.get("pattern", "Unknown")
        round_type = q.get("round_type", "phone_screen")

        per_question.append({
            "question_id": qid,
            "question": q.get("question", ""),
            "score": result["total_score"],
            "rating": result["rating"],
            "thinking": result["thinking"],
            "accuracy": result["accuracy"],
            "quality": quality,
            "pattern": pattern,
            "round_type": round_type,
            "difficulty": q.get("difficulty", "medium"),
        })

        # Aggregate by round
        round_scores.setdefault(round_type, []).append(result["total_score"])

        # Aggregate by pattern
        pattern_scores.setdefault(pattern, []).append(result["total_score"])

    # Calculate averages
    overall = round(sum(r["score"] for r in per_question) / len(per_question)) if per_question else 0
    per_round = {rt: round(sum(scores) / len(scores)) for rt, scores in round_scores.items()}

    # Identify weak and strong patterns
    pattern_avgs = {p: round(sum(s) / len(s)) for p, s in pattern_scores.items()}
    weak = [p for p, avg in sorted(pattern_avgs.items(), key=lambda x: x[1]) if avg < 50]
    strong = [p for p, avg in sorted(pattern_avgs.items(), key=lambda x: -x[1]) if avg >= 70]

    return {
        "overall_score": overall,
        "per_question": per_question,
        "per_round": per_round,
        "pattern_scores": pattern_avgs,
        "weak_patterns": weak,
        "strong_patterns": strong,
        "recommended_focus": weak[:3] if weak else list(pattern_avgs.keys())[:3],
    }


def compute_elo_from_assessment(current_elo, sub_elos, assessment_results):
    """Compute new ELO from Quick Assessment results.

    Args:
        current_elo: Starting overall ELO
        sub_elos: Dict of {round_type: elo}
        assessment_results: Output from score_assessment()

    Returns:
        {
            'overall': {new_elo, delta},
            'sub_elos': {round_type: {new_elo, delta}},
        }
    """
    # Build answer list for ELO calculation
    answers_for_elo = []
    for pq in assessment_results["per_question"]:
        answers_for_elo.append({
            "difficulty": pq.get("difficulty", "medium"),
            "score_percent": pq["score"],
            "round_type": pq["round_type"],
        })

    overall_result = calculate_session_elo_change(
        current_elo, answers_for_elo, session_type="quick_assessment"
    )

    sub_result = calculate_sub_elo_changes(
        sub_elos, answers_for_elo, session_type="quick_assessment"
    )

    return {
        "overall": {"new_elo": overall_result["new_elo"], "delta": overall_result["delta"]},
        "sub_elos": sub_result,
    }
