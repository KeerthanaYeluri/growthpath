"""
Role-based question bank generator.
Generates 30 questions based on selected job role:
  - 1 Self Introduction
  - 24 Technical questions (Easy → Medium → Hard progression)
  - 5 HR / Behavioral questions
"""

# ─── HR Questions (Common for ALL roles) ───
HR_QUESTIONS = [
    {
        "topic": "HR",
        "difficulty": "Easy",
        "question": "Tell me about yourself and walk me through your resume.",
        "keywords": ["experience", "years", "project", "team", "skills", "role", "company", "worked", "responsible", "technology"],
        "model_answer": "I'm a professional with X years of experience in [domain]. I've worked at [companies] where I was responsible for [key responsibilities]. My key skills include [technical skills]. I'm passionate about [area] and looking for opportunities to grow in [target area]. In my current role, I lead/contribute to [specific projects]."
    },
    {
        "topic": "HR",
        "difficulty": "Easy",
        "question": "Why are you looking for a change? What motivates you to leave your current role?",
        "keywords": ["growth", "opportunity", "challenge", "learn", "career", "role", "impact", "technology", "culture", "team"],
        "model_answer": "I'm looking for new challenges and growth opportunities. While I've learned a lot in my current role, I feel I've reached a plateau. I want to work on more complex projects, learn new technologies, and have a greater impact. Your company's work in [area] aligns with my career goals. I'm not running away from something, I'm running toward a better opportunity."
    },
    {
        "topic": "HR",
        "difficulty": "Medium",
        "question": "What is your biggest strength and your biggest weakness? Give examples.",
        "keywords": ["strength", "weakness", "improve", "example", "feedback", "work", "team", "learn", "overcome", "aware"],
        "model_answer": "My biggest strength is problem-solving — I break complex issues into smaller parts and tackle them systematically. For example, [specific example]. My weakness is that I sometimes spend too much time perfecting things. I've been working on this by setting time limits and prioritizing 'good enough' for non-critical tasks. I believe in continuous self-improvement and actively seek feedback."
    },
    {
        "topic": "HR",
        "difficulty": "Medium",
        "question": "Describe a conflict you had with a team member. How did you resolve it?",
        "keywords": ["conflict", "team", "communicate", "listen", "understand", "resolve", "compromise", "perspective", "outcome", "professional"],
        "model_answer": "In a previous project, a developer and I disagreed on the testing approach. They felt unit tests were sufficient, while I believed integration tests were needed. I scheduled a 1-on-1, listened to their concerns (time constraints), shared data showing bugs that only integration tests would catch, and we compromised — we added integration tests for critical flows only. The outcome was better coverage without excessive time investment. I learned that understanding the other person's constraints is key to resolving conflicts."
    },
    {
        "topic": "HR",
        "difficulty": "Medium",
        "question": "Where do you see yourself in 5 years? What are your long-term career goals?",
        "keywords": ["goal", "grow", "lead", "expert", "team", "mentor", "architect", "contribute", "learn", "impact"],
        "model_answer": "In 5 years, I see myself as a senior/lead professional who not only excels technically but also mentors junior team members. I want to grow into a role where I can influence architecture decisions and drive best practices across the team. I plan to deepen my expertise in [domain] while also developing leadership skills. I believe in continuous learning and want to contribute to the community through blogs or talks."
    },
    {
        "topic": "HR",
        "difficulty": "Hard",
        "question": "Tell me about a time you failed at something. What did you learn from it?",
        "keywords": ["fail", "mistake", "learn", "improve", "responsibility", "action", "outcome", "change", "process", "growth"],
        "model_answer": "Early in my career, I deployed a code change without adequate testing that caused a production issue. I took full responsibility, worked with the team to fix it immediately, and then led the effort to implement a proper CI/CD pipeline with automated tests and staging environments. The lesson: shortcuts never pay off. I now advocate for proper testing and review processes. This failure made me a much stronger professional."
    },
    {
        "topic": "HR",
        "difficulty": "Easy",
        "question": "What do you know about our company? Why do you want to work here?",
        "keywords": ["company", "product", "culture", "mission", "team", "technology", "growth", "value", "impact", "excited"],
        "model_answer": "I've researched your company and I'm impressed by [specific product/mission/achievement]. Your focus on [area] aligns with my interests. I admire your engineering culture — from what I've read on your tech blog and Glassdoor, the team values [collaboration/innovation/quality]. I believe my skills in [relevant skills] would contribute to your [specific team/project], and I'd grow significantly working alongside your talented team."
    },
    {
        "topic": "HR",
        "difficulty": "Medium",
        "question": "How do you handle pressure and tight deadlines? Give a real example.",
        "keywords": ["pressure", "deadline", "prioritize", "calm", "plan", "communicate", "deliver", "stress", "manage", "team"],
        "model_answer": "I thrive under pressure by staying organized. When facing a tight deadline, I first break the work into tasks, prioritize by impact, and communicate with stakeholders about what's realistic. Example: Before a major release, we discovered critical bugs 2 days before launch. I created a priority matrix, assigned bugs to team members based on expertise, we worked focused hours (not just long hours), and delivered on time. The key is staying calm, communicating clearly, and focusing on what matters most."
    },
    {
        "topic": "HR",
        "difficulty": "Hard",
        "question": "If you had two job offers — one with higher pay and one with better learning opportunities — which would you choose and why?",
        "keywords": ["growth", "learn", "money", "career", "long-term", "value", "opportunity", "balance", "invest", "decision"],
        "model_answer": "I would lean toward the learning opportunity, as long as the compensation is fair. In my experience, skills and knowledge compound over time — investing in growth early leads to much better outcomes (including financial) in the long run. Of course, I need to meet my financial obligations, so it's not purely idealistic. The ideal is a role that offers both — competitive compensation AND growth. But if forced to choose, I'd pick the role that makes me a better professional."
    },
    {
        "topic": "HR",
        "difficulty": "Easy",
        "question": "Do you have any questions for us?",
        "keywords": ["team", "culture", "project", "growth", "technology", "process", "challenge", "roadmap", "mentor", "expect"],
        "model_answer": "Yes! 1) What does a typical day look like for this role? 2) What are the biggest challenges the team is currently facing? 3) How does the team handle knowledge sharing and mentorship? 4) What does the career growth path look like for this position? 5) What technologies or tools is the team planning to adopt in the near future? These questions show genuine interest and help me understand if the role is the right fit."
    }
]

# ─── Role-Specific Technical Questions ───

ROLE_QUESTIONS = {
    "sdet": {
        "name": "SDET / QA Automation Engineer",
        "topics": [
            # Python (3)
            {"topic": "Python", "difficulty": "Easy", "question": "What are the key differences between a list and a tuple in Python? When would you use one over the other?",
             "keywords": ["mutable", "immutable", "list", "tuple", "ordered", "index", "performance", "hashable", "change", "modify"],
             "model_answer": "A list is mutable — you can add, remove, or change elements after creation. A tuple is immutable — once created, it cannot be modified. Lists use square brackets [], tuples use parentheses (). Tuples are faster and use less memory because of their immutability. Use lists when you need to modify data (e.g., collecting test results). Use tuples for fixed data that shouldn't change (e.g., database connection configs). Tuples can also be used as dictionary keys since they're hashable, while lists cannot."},
            {"topic": "Python", "difficulty": "Medium", "question": "Explain decorators in Python. Can you give an example of how you've used them in your testing framework?",
             "keywords": ["decorator", "wrapper", "function", "@", "reusable", "logging", "retry", "fixture", "annotation", "higher-order"],
             "model_answer": "A decorator is a function that takes another function as input, adds some behavior, and returns a modified function — without changing the original function's code. It uses the @ syntax. For example, @pytest.mark.parametrize runs a test with multiple inputs. I've created custom decorators like @retry(max_attempts=3) that automatically retries a flaky test, and @log_execution that logs start/end time. Decorators help keep code DRY by extracting cross-cutting concerns."},
            {"topic": "Python", "difficulty": "Hard", "question": "Explain how Python's GIL works. How does it affect multi-threaded test execution, and what alternatives do you use?",
             "keywords": ["GIL", "thread", "multiprocessing", "concurrency", "parallel", "lock", "CPU", "I/O", "asyncio", "subprocess"],
             "model_answer": "The GIL is a mutex in CPython that allows only one thread to execute Python bytecode at a time. For I/O-bound tasks (like browser waits, API calls), threads work fine. For CPU-heavy tasks, use multiprocessing. pytest-xdist uses subprocess-based parallelism to bypass GIL entirely. asyncio is another alternative for concurrent I/O."},
            # Pytest (3)
            {"topic": "Pytest", "difficulty": "Easy", "question": "What is Pytest and why do you prefer it over unittest? What are its main advantages?",
             "keywords": ["fixture", "assert", "plugin", "parametrize", "discover", "simple", "marker", "conftest", "verbose", "readable"],
             "model_answer": "Pytest is a Python testing framework. Advantages over unittest: simple assert statements, powerful fixtures with scopes, parametrize decorator, auto-discovery, rich plugin ecosystem, conftest.py for shared fixtures, better error messages with assertion introspection."},
            {"topic": "Pytest", "difficulty": "Medium", "question": "Explain Pytest fixtures in detail. What are fixture scopes, and how do you use conftest.py?",
             "keywords": ["fixture", "scope", "session", "module", "function", "conftest", "yield", "setup", "teardown", "autouse", "shared"],
             "model_answer": "Fixtures are reusable setup/teardown functions. Scopes: 'function' (default) runs per test, 'class' per class, 'module' per file, 'session' once for entire suite. Use yield for setup + teardown. conftest.py defines shared fixtures accessible to all tests without importing. autouse=True makes a fixture run automatically."},
            {"topic": "Pytest", "difficulty": "Hard", "question": "How do you implement parallel test execution in Pytest with pytest-xdist? How do you handle shared state?",
             "keywords": ["xdist", "parallel", "worker", "-n", "distributed", "isolation", "fixture", "scope", "session", "lock", "tmp_path"],
             "model_answer": "pytest-xdist enables parallel execution using multiple processes. 'pytest -n auto' uses all CPU cores. Each worker is independent — session-scoped fixtures run once PER worker. Use FileLock for one-time setup. Tests must be fully isolated — no shared state, no ordering dependencies."},
            # Playwright (3)
            {"topic": "Playwright", "difficulty": "Easy", "question": "What is Playwright and how does it compare to Selenium? Key advantages?",
             "keywords": ["browser", "chromium", "firefox", "webkit", "auto-wait", "selector", "headless", "fast", "reliable", "cross-browser"],
             "model_answer": "Playwright by Microsoft supports Chromium, Firefox, WebKit. Advantages: auto-waiting, built-in assertions with retry, network interception, multiple browser contexts, trace viewer, native iframe/shadow DOM support, faster execution via DevTools Protocol."},
            {"topic": "Playwright", "difficulty": "Medium", "question": "Explain Playwright's auto-waiting mechanism and how you use locators effectively.",
             "keywords": ["auto-wait", "locator", "get_by_role", "get_by_text", "visible", "attached", "enabled", "timeout", "retry", "actionability"],
             "model_answer": "Playwright auto-waits before every action — element must be attached, visible, stable, enabled, not obscured. Prefer user-facing locators: get_by_role('button', name='Submit'), get_by_text('Login'). Locators are lazy and auto-retry on DOM changes. Custom timeout: locator.click(timeout=10000)."},
            {"topic": "Playwright", "difficulty": "Hard", "question": "How do you implement API mocking and network interception in Playwright?",
             "keywords": ["route", "mock", "intercept", "fulfill", "abort", "request", "response", "API", "network", "handler"],
             "model_answer": "Use page.route() to intercept requests. Actions: fulfill (return mock response), abort (block), continue (modify). Example: page.route('**/api/users', lambda route: route.fulfill(status=500, body='Error')) to test error handling without breaking real API."},
            # Selenium (3)
            {"topic": "Selenium", "difficulty": "Easy", "question": "Explain the Selenium WebDriver architecture. How does a command travel from test code to browser?",
             "keywords": ["WebDriver", "browser", "driver", "HTTP", "JSON", "wire", "protocol", "ChromeDriver", "server", "client"],
             "model_answer": "Selenium uses client-server architecture with W3C WebDriver Protocol. Flow: test code creates command → client library converts to HTTP request → browser driver (ChromeDriver) translates to native commands → browser executes → response travels back."},
            {"topic": "Selenium", "difficulty": "Medium", "question": "What are implicit, explicit, and fluent waits in Selenium? When to use each?",
             "keywords": ["implicit", "explicit", "fluent", "WebDriverWait", "ExpectedConditions", "timeout", "polling", "visibility", "clickable"],
             "model_answer": "Implicit: global, applies to all lookups. Explicit: WebDriverWait with ExpectedConditions for specific elements. Fluent: custom polling interval + exception ignoring. Best practice: avoid implicit waits, use explicit waits. Never mix both."},
            {"topic": "Selenium", "difficulty": "Hard", "question": "How do you design a robust POM framework? How to handle StaleElementReferenceException?",
             "keywords": ["POM", "page object", "stale", "element", "retry", "dynamic", "locator", "encapsulation", "base page", "wrapper"],
             "model_answer": "BasePage class with common utilities, each page as separate class with private locators and public methods. For StaleElementException: wrap actions in retry method that re-locates elements, use By objects instead of storing element references, use explicit waits before interacting."},
            # API Testing (3)
            {"topic": "API Testing", "difficulty": "Easy", "question": "What are HTTP methods? Explain the difference between PUT and PATCH.",
             "keywords": ["GET", "POST", "PUT", "PATCH", "DELETE", "idempotent", "update", "partial", "full", "resource", "REST"],
             "model_answer": "GET (retrieve), POST (create), PUT (full replace), PATCH (partial update), DELETE (remove). PUT replaces entire resource — send all fields. PATCH updates only specified fields. PUT is idempotent."},
            {"topic": "API Testing", "difficulty": "Medium", "question": "How do you validate API responses beyond status codes?",
             "keywords": ["status", "body", "schema", "header", "response time", "JSON", "validation", "contract", "field", "assertion"],
             "model_answer": "Validate: response body values, JSON schema structure, headers (Content-Type, CORS), response time (SLA), pagination, error format, null handling, data integrity. Use assert libraries and schema validators."},
            {"topic": "API Testing", "difficulty": "Hard", "question": "How do you test API authentication/authorization? Explain OAuth2 token handling in tests.",
             "keywords": ["OAuth", "token", "bearer", "refresh", "authorization", "role", "permission", "JWT", "401", "403"],
             "model_answer": "Test 401 for missing/invalid tokens, token expiry and refresh flow, role-based access (admin vs viewer). Use session-scoped fixtures to authenticate once. Decode JWT to verify claims. Test resource-level permissions."},
            # Locust (2)
            {"topic": "Locust", "difficulty": "Easy", "question": "What is Locust? How does it differ from JMeter?",
             "keywords": ["Locust", "Python", "performance", "load", "JMeter", "code", "scalable", "distributed", "lightweight"],
             "model_answer": "Locust is a Python-based load testing tool. Tests written in code (not XML/GUI), uses coroutines (lighter than JMeter's threads), easy distributed testing, built-in web UI. Better if team knows Python."},
            {"topic": "Locust", "difficulty": "Medium", "question": "How do you write a Locust test? Explain HttpUser, @task, and wait_time.",
             "keywords": ["HttpUser", "task", "@task", "wait_time", "between", "host", "on_start", "client", "weight"],
             "model_answer": "class MyUser(HttpUser), host = target URL, wait_time = between(1, 3) for think time, @task marks user actions, @task(3) for higher weight, on_start() for login/setup, self.client.get/post for requests."},
            # Manual Testing (2)
            {"topic": "Manual Testing", "difficulty": "Easy", "question": "What's the difference between smoke, sanity, and regression testing?",
             "keywords": ["smoke", "sanity", "regression", "build", "critical", "subset", "full", "release", "deploy"],
             "model_answer": "Smoke: quick check of critical features after new build. Sanity: focused check on specific fix/change. Regression: comprehensive re-run of all tests before release. Order: Smoke → Sanity → Regression."},
            {"topic": "Manual Testing", "difficulty": "Medium", "question": "How do you write effective test cases? What techniques ensure coverage?",
             "keywords": ["test case", "steps", "expected", "coverage", "boundary", "equivalence", "partition", "traceability"],
             "model_answer": "Good test case: clear title, preconditions, steps, expected results. Techniques: Equivalence Partitioning, Boundary Value Analysis, Decision Tables, Requirements Traceability Matrix. Each test should have one clear objective."},
        ]
    },

    "devops": {
        "name": "DevOps Engineer",
        "topics": [
            {"topic": "Linux", "difficulty": "Easy", "question": "What are the most commonly used Linux commands for troubleshooting? Explain any 5 with examples.",
             "keywords": ["top", "ps", "grep", "tail", "df", "du", "netstat", "chmod", "curl", "ssh", "logs"],
             "model_answer": "top — monitor CPU/memory usage in real-time. ps aux — list running processes. grep — search text patterns in files/logs. tail -f — follow log files in real-time. df -h — check disk space. Others: netstat for network connections, chmod for permissions, curl for API testing."},
            {"topic": "Linux", "difficulty": "Medium", "question": "Explain Linux file permissions. What does chmod 755 mean? How do you troubleshoot permission denied errors?",
             "keywords": ["chmod", "permission", "read", "write", "execute", "owner", "group", "other", "755", "rwx", "chown"],
             "model_answer": "Linux permissions: rwx (read=4, write=2, execute=1) for owner, group, others. chmod 755 = owner has rwx (7), group has r-x (5), others have r-x (5). Troubleshoot: check ls -la, verify ownership with chown, check parent directory permissions, use namei -l for full path permissions."},
            {"topic": "Linux", "difficulty": "Hard", "question": "How do you diagnose and fix a Linux server running out of memory or high CPU usage?",
             "keywords": ["top", "htop", "free", "vmstat", "OOM", "swap", "process", "kill", "memory leak", "strace", "perf"],
             "model_answer": "Diagnosis: top/htop for real-time CPU/memory, free -h for memory overview, vmstat for system stats, dmesg for OOM killer logs. Fix: identify the rogue process, check for memory leaks (valgrind), increase swap temporarily, optimize application code, set resource limits with ulimit/cgroups."},
            {"topic": "Docker", "difficulty": "Easy", "question": "What is Docker? Explain the difference between an image and a container.",
             "keywords": ["container", "image", "lightweight", "isolated", "Dockerfile", "layer", "registry", "run", "build", "virtual"],
             "model_answer": "Docker is a containerization platform that packages apps with dependencies into portable containers. Image = read-only template/blueprint (like a class). Container = running instance of an image (like an object). Images are built from Dockerfiles in layers. Containers are isolated, lightweight, and share the host OS kernel — unlike VMs which need full OS."},
            {"topic": "Docker", "difficulty": "Medium", "question": "How do you write an efficient Dockerfile? What are multi-stage builds?",
             "keywords": ["Dockerfile", "FROM", "RUN", "COPY", "layer", "cache", "multi-stage", "slim", "alpine", "minimize", "size"],
             "model_answer": "Efficient Dockerfile: use slim/alpine base images, combine RUN commands to reduce layers, use .dockerignore, order commands by change frequency (cache optimization), don't run as root. Multi-stage builds: use multiple FROM stages — build in one stage, copy only artifacts to final stage. Reduces image size dramatically."},
            {"topic": "Docker", "difficulty": "Hard", "question": "How do you debug a container that keeps crashing? Walk me through your approach.",
             "keywords": ["logs", "exec", "inspect", "restart", "health", "exit code", "OOM", "resource", "volume", "network"],
             "model_answer": "Steps: 1) docker logs <container> for app logs. 2) docker inspect for exit code and state. 3) Check exit codes (137=OOM killed, 1=app error). 4) docker exec -it to enter running container. 5) Check resource limits (docker stats). 6) Verify volume mounts and network. 7) Run container with --entrypoint /bin/sh to debug startup issues."},
            {"topic": "Kubernetes", "difficulty": "Easy", "question": "What is Kubernetes? Explain pods, services, and deployments.",
             "keywords": ["K8s", "pod", "service", "deployment", "container", "orchestration", "node", "cluster", "replica", "scale"],
             "model_answer": "Kubernetes orchestrates containerized applications. Pod = smallest unit, runs one or more containers. Service = stable network endpoint to access pods (ClusterIP, NodePort, LoadBalancer). Deployment = manages pod replicas, handles rolling updates and rollbacks. Cluster = master node(s) + worker nodes."},
            {"topic": "Kubernetes", "difficulty": "Medium", "question": "Explain Kubernetes networking. How do pods communicate with each other and the outside world?",
             "keywords": ["service", "ClusterIP", "NodePort", "LoadBalancer", "Ingress", "DNS", "pod", "network", "CNI", "port"],
             "model_answer": "Every pod gets a unique IP. Pod-to-pod: direct IP communication within cluster (flat network via CNI plugins). Services provide stable IPs: ClusterIP (internal), NodePort (external via node port), LoadBalancer (cloud LB). Ingress controller manages external HTTP routing with rules/paths. CoreDNS resolves service names."},
            {"topic": "Kubernetes", "difficulty": "Hard", "question": "How do you troubleshoot a pod stuck in CrashLoopBackOff? What steps do you follow?",
             "keywords": ["CrashLoopBackOff", "logs", "describe", "events", "restart", "probe", "resource", "config", "OOM", "debug"],
             "model_answer": "Steps: 1) kubectl describe pod — check Events section for errors. 2) kubectl logs pod — check app logs (add --previous for crashed container). 3) Check exit codes in container status. 4) Verify liveness/readiness probes aren't too aggressive. 5) Check resource limits (OOMKilled). 6) Verify ConfigMaps/Secrets are mounted correctly. 7) Check image pull issues. 8) kubectl exec for interactive debugging."},
            {"topic": "CI/CD", "difficulty": "Easy", "question": "What is CI/CD? Explain the difference between continuous integration, delivery, and deployment.",
             "keywords": ["CI", "CD", "integration", "delivery", "deployment", "pipeline", "automate", "build", "test", "deploy"],
             "model_answer": "CI (Continuous Integration): developers merge code frequently, automated build and tests run on every commit. CD (Continuous Delivery): code is always in deployable state, release to production is manual. CD (Continuous Deployment): every change that passes tests is automatically deployed to production. Pipeline stages: Code → Build → Test → Stage → Deploy."},
            {"topic": "CI/CD", "difficulty": "Medium", "question": "How do you design a CI/CD pipeline? What stages would you include and what tools would you use?",
             "keywords": ["pipeline", "Jenkins", "GitHub Actions", "GitLab", "build", "test", "deploy", "stage", "artifact", "notify"],
             "model_answer": "Stages: 1) Code checkout. 2) Lint/static analysis. 3) Build (compile/Docker build). 4) Unit tests. 5) Integration tests. 6) Security scan (SAST/DAST). 7) Build artifact/push to registry. 8) Deploy to staging. 9) E2E tests on staging. 10) Deploy to production (with approval gate). 11) Post-deploy smoke tests. Tools: Jenkins, GitHub Actions, GitLab CI, ArgoCD, SonarQube, Trivy."},
            {"topic": "CI/CD", "difficulty": "Hard", "question": "How do you implement zero-downtime deployments? Explain blue-green and canary strategies.",
             "keywords": ["blue-green", "canary", "rolling", "zero-downtime", "rollback", "traffic", "health", "strategy", "load balancer"],
             "model_answer": "Blue-Green: run two identical environments. Blue = current, Green = new version. Switch traffic from Blue to Green after testing. Instant rollback by switching back. Canary: gradually route a small percentage of traffic (5%, 25%, 50%, 100%) to new version. Monitor metrics at each step. Rollback if errors spike. Rolling update: replace instances one by one. All strategies need health checks and automated rollback triggers."},
            {"topic": "Terraform", "difficulty": "Easy", "question": "What is Infrastructure as Code? What is Terraform and why use it?",
             "keywords": ["IaC", "Terraform", "infrastructure", "code", "state", "provider", "plan", "apply", "declarative", "cloud"],
             "model_answer": "IaC manages infrastructure through code instead of manual processes. Terraform by HashiCorp is a declarative IaC tool — you define desired state, Terraform figures out how to achieve it. Benefits: version-controlled infra, reproducible environments, multi-cloud support (AWS, Azure, GCP), plan before apply, state management, modular and reusable."},
            {"topic": "Terraform", "difficulty": "Medium", "question": "Explain Terraform state. Why is it important and how do you manage state in a team?",
             "keywords": ["state", "backend", "S3", "lock", "remote", "plan", "drift", "terraform.tfstate", "workspace", "import"],
             "model_answer": "Terraform state maps your config to real resources. It's critical for knowing what exists and planning changes. For teams: use remote backend (S3 + DynamoDB for locking) to share state and prevent concurrent modifications. Never commit state files to git (contains secrets). Use workspaces for environment separation. Handle drift with terraform plan and import."},
            {"topic": "AWS", "difficulty": "Easy", "question": "Explain the core AWS services: EC2, S3, VPC, and IAM. When would you use each?",
             "keywords": ["EC2", "S3", "VPC", "IAM", "instance", "bucket", "network", "security", "role", "policy", "compute", "storage"],
             "model_answer": "EC2: virtual servers (compute). S3: object storage (files, backups, static websites). VPC: virtual private network (isolate resources, subnets, security groups). IAM: identity and access management (users, roles, policies, least privilege). EC2 for running apps, S3 for storage, VPC for network architecture, IAM for security."},
            {"topic": "AWS", "difficulty": "Medium", "question": "How do you secure an AWS environment? What are security best practices?",
             "keywords": ["IAM", "security group", "least privilege", "MFA", "encryption", "KMS", "VPC", "CloudTrail", "secrets", "audit"],
             "model_answer": "Best practices: least privilege IAM policies, enable MFA, use security groups (deny by default), encrypt data at rest (KMS) and in transit (TLS), use Secrets Manager for credentials, enable CloudTrail for audit logging, use VPC private subnets for internal services, regular security audits, no hardcoded credentials."},
            {"topic": "Monitoring", "difficulty": "Easy", "question": "What is monitoring and observability? What tools have you used?",
             "keywords": ["monitoring", "observability", "metrics", "logs", "traces", "Prometheus", "Grafana", "ELK", "alert", "dashboard"],
             "model_answer": "Monitoring: tracking system health via metrics, logs, alerts. Observability: understanding system internals from external outputs (metrics, logs, traces). Tools: Prometheus + Grafana for metrics/dashboards, ELK stack (Elasticsearch, Logstash, Kibana) for logs, Jaeger for distributed tracing, PagerDuty/OpsGenie for alerting."},
            {"topic": "Monitoring", "difficulty": "Medium", "question": "How do you set up effective alerting? How do you avoid alert fatigue?",
             "keywords": ["alert", "threshold", "SLA", "SLO", "severity", "runbook", "oncall", "noise", "actionable", "escalation"],
             "model_answer": "Effective alerting: alert on symptoms (user impact) not causes, set meaningful thresholds based on SLOs, categorize by severity (P1-P4), every alert must be actionable with a runbook, suppress duplicate alerts, use escalation policies. Avoid fatigue: review and tune alerts regularly, remove noisy alerts, consolidate related alerts, use dashboards for non-critical monitoring."},
            {"topic": "Git", "difficulty": "Easy", "question": "Explain Git branching strategies. What is GitFlow vs trunk-based development?",
             "keywords": ["branch", "merge", "GitFlow", "trunk", "feature", "release", "hotfix", "main", "PR", "review"],
             "model_answer": "GitFlow: separate branches for features, develop, release, hotfix, main. Good for release cycles. Trunk-based: everyone commits to main/trunk, use short-lived feature branches (<1 day), feature flags for incomplete work. Better for CI/CD. Most modern teams use trunk-based with PRs and automated testing."},
            {"topic": "Networking", "difficulty": "Medium", "question": "Explain DNS, load balancing, and reverse proxy. How do they work together?",
             "keywords": ["DNS", "load balancer", "reverse proxy", "Nginx", "HAProxy", "round robin", "health check", "SSL", "traffic"],
             "model_answer": "DNS resolves domain names to IP addresses. Load Balancer distributes traffic across multiple servers (algorithms: round-robin, least connections, IP hash). Reverse Proxy sits in front of servers — handles SSL termination, caching, compression. Together: DNS → Load Balancer → Reverse Proxy (Nginx) → Application servers. Tools: AWS ALB/NLB, Nginx, HAProxy."},
        ]
    },

    "python_developer": {
        "name": "Python Developer",
        "topics": [
            {"topic": "Python Core", "difficulty": "Easy", "question": "Explain mutable vs immutable data types in Python with examples.",
             "keywords": ["mutable", "immutable", "list", "tuple", "dict", "set", "string", "int", "modify", "copy"],
             "model_answer": "Immutable: int, float, string, tuple, frozenset — cannot be changed after creation. Mutable: list, dict, set — can be modified in place. Example: string concatenation creates a new object, list.append() modifies the same object. Important for: function arguments (mutable default trap), dictionary keys (must be immutable), thread safety."},
            {"topic": "Python Core", "difficulty": "Easy", "question": "What are *args and **kwargs in Python? When would you use them?",
             "keywords": ["args", "kwargs", "arguments", "positional", "keyword", "unpack", "flexible", "function", "dict", "tuple"],
             "model_answer": "*args collects extra positional arguments as a tuple. **kwargs collects extra keyword arguments as a dictionary. Use when you don't know how many arguments a function will receive. Common in decorators, wrapper functions, and when extending base classes. Example: def log(*args, **kwargs) can accept any combination of arguments."},
            {"topic": "Python Core", "difficulty": "Medium", "question": "Explain list comprehensions, generator expressions, and when to use each.",
             "keywords": ["comprehension", "generator", "yield", "lazy", "memory", "iterator", "list", "expression", "performance", "large"],
             "model_answer": "List comprehension: [x**2 for x in range(10)] — creates entire list in memory. Generator expression: (x**2 for x in range(10)) — lazy evaluation, produces values one at a time. Use generators for large datasets to save memory. List comprehensions when you need the full list. Generators support iteration but not indexing/len."},
            {"topic": "Python Core", "difficulty": "Medium", "question": "What is the difference between deep copy and shallow copy in Python?",
             "keywords": ["copy", "deep", "shallow", "reference", "nested", "object", "id", "independent", "mutable", "clone"],
             "model_answer": "Shallow copy (copy.copy or list.copy): creates new object but references same nested objects. Changes to nested objects affect both. Deep copy (copy.deepcopy): creates completely independent copy including all nested objects. Use deep copy when you have nested mutable objects (lists of lists, dicts of dicts) and need complete independence."},
            {"topic": "Python Core", "difficulty": "Hard", "question": "Explain Python's memory management. How does garbage collection work?",
             "keywords": ["reference", "counting", "garbage", "collector", "cycle", "gc", "memory", "del", "weak", "generation"],
             "model_answer": "Python uses reference counting as primary mechanism — each object tracks how many references point to it. When count reaches 0, memory is freed. Problem: circular references (A→B→A). Solution: generational garbage collector (gc module) detects and collects reference cycles. Three generations: new objects checked most frequently. Use weakref for caches to avoid preventing garbage collection."},
            {"topic": "Python Core", "difficulty": "Hard", "question": "What are metaclasses in Python? Give a practical use case.",
             "keywords": ["metaclass", "type", "class", "__new__", "__init__", "create", "singleton", "abstract", "validation", "ORM"],
             "model_answer": "Metaclasses are 'classes of classes' — they control class creation. type is the default metaclass. Use __new__ to modify class before creation, __init__ to modify after. Practical uses: Django ORM (ModelMetaclass creates table mappings), singleton pattern enforcement, API registration, automatic attribute validation. 99% of the time you don't need them — use decorators or class decorators instead."},
            {"topic": "OOP", "difficulty": "Easy", "question": "Explain the four pillars of OOP in Python with examples.",
             "keywords": ["encapsulation", "inheritance", "polymorphism", "abstraction", "class", "private", "override", "interface", "method"],
             "model_answer": "Encapsulation: bundling data and methods, using _ and __ for access control. Inheritance: class Child(Parent) reuses parent code. Polymorphism: same method name, different behavior (duck typing in Python). Abstraction: hiding complexity via abstract base classes (ABC). Python uses duck typing — 'if it quacks like a duck'."},
            {"topic": "OOP", "difficulty": "Medium", "question": "What are class methods, static methods, and instance methods? When to use each?",
             "keywords": ["classmethod", "staticmethod", "self", "cls", "instance", "factory", "utility", "decorator", "bound"],
             "model_answer": "Instance method: takes self, accesses instance data. Class method (@classmethod): takes cls, accesses class-level data, commonly used as factory methods (alternative constructors). Static method (@staticmethod): no self/cls, utility functions that belong to the class namespace but don't need instance/class data. Example: Date.from_string() as classmethod, Date.is_valid() as staticmethod."},
            {"topic": "Web/Flask", "difficulty": "Easy", "question": "What is Flask? How does it compare to Django? When would you choose one over the other?",
             "keywords": ["Flask", "Django", "micro", "framework", "route", "template", "ORM", "lightweight", "API", "REST"],
             "model_answer": "Flask is a micro-framework — minimal core, add extensions as needed. Django is a batteries-included framework with ORM, admin, auth built-in. Choose Flask for: APIs, microservices, small projects, when you want control. Choose Django for: full web apps, content sites, rapid prototyping with built-in features. Flask is lighter, Django is faster to build full apps."},
            {"topic": "Web/Flask", "difficulty": "Medium", "question": "How do you design and build a REST API in Python? What are best practices?",
             "keywords": ["REST", "API", "endpoint", "status code", "JSON", "versioning", "authentication", "pagination", "error", "CRUD"],
             "model_answer": "Best practices: use proper HTTP methods (GET/POST/PUT/DELETE), meaningful URLs (/api/v1/users), correct status codes (200, 201, 404, 500), JSON responses with consistent structure, pagination for lists, authentication (JWT/OAuth), input validation, error handling with proper messages, API versioning, rate limiting, documentation (Swagger/OpenAPI)."},
            {"topic": "Web/Flask", "difficulty": "Hard", "question": "How do you handle async programming in Python? Explain asyncio, aiohttp, and when to use them.",
             "keywords": ["async", "await", "asyncio", "coroutine", "event loop", "aiohttp", "concurrent", "I/O", "non-blocking", "task"],
             "model_answer": "asyncio provides event loop for concurrent I/O operations. async def creates coroutines, await pauses execution until result is ready. aiohttp is async HTTP client/server. Use async for I/O-bound tasks (API calls, database queries, file I/O) where you're waiting for responses. Don't use for CPU-bound tasks (use multiprocessing instead). gather() runs multiple coroutines concurrently."},
            {"topic": "Database", "difficulty": "Easy", "question": "What is the difference between SQL and NoSQL databases? When would you use each?",
             "keywords": ["SQL", "NoSQL", "relational", "document", "schema", "MongoDB", "PostgreSQL", "table", "collection", "scale"],
             "model_answer": "SQL: structured, relational tables with fixed schema, ACID transactions, joins. PostgreSQL, MySQL. Use for: structured data, complex queries, transactions. NoSQL: flexible schema, document/key-value/graph stores. MongoDB, Redis, DynamoDB. Use for: unstructured data, high scalability, rapid iteration, real-time apps. Choose based on data structure and query patterns."},
            {"topic": "Database", "difficulty": "Medium", "question": "Explain ORM in Python. What is SQLAlchemy and how do you use it?",
             "keywords": ["ORM", "SQLAlchemy", "model", "session", "query", "relationship", "migration", "Alembic", "database", "mapping"],
             "model_answer": "ORM maps Python classes to database tables — you work with objects instead of raw SQL. SQLAlchemy is the most popular Python ORM. Define models as classes, use Session for transactions, query with Python methods. Relationships (one-to-many, many-to-many) with relationship(). Alembic handles database migrations. Supports connection pooling and multiple database backends."},
            {"topic": "Testing", "difficulty": "Easy", "question": "How do you write unit tests in Python? What tools do you use?",
             "keywords": ["pytest", "unittest", "mock", "assert", "fixture", "coverage", "TDD", "test", "patch", "parametrize"],
             "model_answer": "Use pytest (preferred) or unittest. Write test functions starting with test_. Use assert for checks. Fixtures for setup/teardown. Mock external dependencies with unittest.mock.patch. Parametrize for multiple test cases. Measure coverage with pytest-cov. Follow AAA pattern: Arrange, Act, Assert. TDD: write test first, then code."},
            {"topic": "Testing", "difficulty": "Medium", "question": "What is mocking? When and how do you mock in Python tests?",
             "keywords": ["mock", "patch", "MagicMock", "side_effect", "return_value", "external", "API", "database", "isolation", "dependency"],
             "model_answer": "Mocking replaces real objects with fake ones in tests to isolate the code being tested. Use unittest.mock.patch to mock external dependencies (APIs, databases, file system). MagicMock creates mock objects. return_value sets what mock returns. side_effect for exceptions or dynamic behavior. Mock at the import location, not where it's defined. Don't over-mock — only mock external boundaries."},
            {"topic": "Data Structures", "difficulty": "Medium", "question": "Explain Python's dict implementation. What is time complexity for common operations?",
             "keywords": ["dict", "hash", "table", "O(1)", "collision", "key", "bucket", "resize", "hashable", "lookup"],
             "model_answer": "Python dict uses a hash table. Keys must be hashable. Hash function converts key to bucket index. Average case: get/set/delete are O(1). Worst case (many collisions): O(n). Dict auto-resizes when load factor exceeds threshold. Since Python 3.7, dicts maintain insertion order. Collisions handled via open addressing (probing)."},
            {"topic": "Data Structures", "difficulty": "Hard", "question": "Implement a LRU cache in Python. Explain your approach and time complexity.",
             "keywords": ["LRU", "cache", "OrderedDict", "doubly linked", "hash", "O(1)", "evict", "capacity", "functools", "lru_cache"],
             "model_answer": "Use collections.OrderedDict: get() moves to end (most recent), put() adds to end and evicts from front if over capacity. Both O(1). Or use @functools.lru_cache decorator for simple function caching. For production: use Redis. Manual implementation: doubly-linked list (O(1) removal) + hash map (O(1) lookup). head = least recent, tail = most recent."},
            {"topic": "Design Patterns", "difficulty": "Medium", "question": "Explain the Singleton, Factory, and Observer patterns. Give Python examples.",
             "keywords": ["singleton", "factory", "observer", "pattern", "design", "instance", "create", "decouple", "event", "notify"],
             "model_answer": "Singleton: only one instance of a class (use module-level variable or __new__). Example: database connection pool. Factory: creates objects without exposing creation logic (factory method returns different classes based on input). Observer: objects subscribe to events, get notified on changes (pub-sub). Example: event system where multiple handlers respond to state changes."},
            {"topic": "Performance", "difficulty": "Hard", "question": "How do you profile and optimize Python code? What tools do you use?",
             "keywords": ["profile", "cProfile", "memory", "optimize", "bottleneck", "time", "line_profiler", "memory_profiler", "benchmark", "cache"],
             "model_answer": "Profiling tools: cProfile for function-level timing, line_profiler for line-by-line analysis, memory_profiler for memory usage, py-spy for production profiling. Optimization: use built-in data structures (dict > list for lookups), avoid premature optimization, cache with lru_cache, use generators for large data, vectorize with numpy, move hot loops to C extensions (Cython), use multiprocessing for CPU-bound work. Always measure before optimizing."},
        ]
    },

    "frontend": {
        "name": "Frontend Developer",
        "topics": [
            {"topic": "HTML/CSS", "difficulty": "Easy", "question": "What is the difference between block and inline elements? Give examples.",
             "keywords": ["block", "inline", "div", "span", "width", "height", "flow", "display", "p", "a", "inline-block"],
             "model_answer": "Block elements: take full width, start on new line, accept width/height. Examples: div, p, h1-h6, section. Inline elements: take only needed width, don't break line, ignore width/height. Examples: span, a, strong, em. inline-block: inline flow but accepts width/height. Use CSS display property to change behavior."},
            {"topic": "HTML/CSS", "difficulty": "Medium", "question": "Explain CSS Flexbox and Grid. When would you use each?",
             "keywords": ["flexbox", "grid", "layout", "row", "column", "align", "justify", "responsive", "gap", "template"],
             "model_answer": "Flexbox: one-dimensional layout (row OR column). Great for: nav bars, centering, distributing space. Key properties: justify-content, align-items, flex-grow/shrink. Grid: two-dimensional layout (rows AND columns simultaneously). Great for: page layouts, card grids, complex arrangements. Key: grid-template-columns/rows, grid-area. Use Flexbox for components, Grid for page structure."},
            {"topic": "HTML/CSS", "difficulty": "Hard", "question": "How do you implement responsive design? Explain mobile-first approach and CSS strategies.",
             "keywords": ["responsive", "media query", "mobile-first", "breakpoint", "viewport", "rem", "em", "fluid", "clamp", "container"],
             "model_answer": "Mobile-first: design for small screens first, then enhance with media queries for larger screens. Use min-width media queries. Strategies: fluid typography with clamp(), relative units (rem, em, %), CSS Grid/Flexbox for layout, responsive images (srcset, picture element), container queries for component-level responsiveness. Breakpoints should match content needs, not device sizes."},
            {"topic": "JavaScript", "difficulty": "Easy", "question": "Explain var, let, and const. What is hoisting and scope in JavaScript?",
             "keywords": ["var", "let", "const", "hoisting", "scope", "block", "function", "temporal", "dead zone", "declaration"],
             "model_answer": "var: function-scoped, hoisted (initialized as undefined). let: block-scoped, hoisted but not initialized (temporal dead zone). const: block-scoped, must be initialized, reference can't be reassigned (but objects/arrays can be mutated). Best practice: use const by default, let when reassignment needed, avoid var. Hoisting moves declarations to top of scope during compilation."},
            {"topic": "JavaScript", "difficulty": "Medium", "question": "Explain closures, callbacks, and promises in JavaScript.",
             "keywords": ["closure", "callback", "promise", "async", "await", "scope", "then", "catch", "resolve", "reject"],
             "model_answer": "Closure: function that remembers variables from its outer scope even after outer function returns. Used for data privacy, callbacks. Callback: function passed as argument, called later (leads to callback hell). Promise: object representing eventual completion/failure. States: pending, fulfilled, rejected. .then()/.catch() for handling. async/await is syntactic sugar over promises — cleaner code, try/catch for errors."},
            {"topic": "JavaScript", "difficulty": "Hard", "question": "Explain the JavaScript event loop. How do microtasks and macrotasks work?",
             "keywords": ["event loop", "call stack", "callback queue", "microtask", "macrotask", "setTimeout", "Promise", "async", "browser", "single-threaded"],
             "model_answer": "JS is single-threaded. Event loop: 1) Execute call stack (synchronous code). 2) When stack is empty, process ALL microtasks (Promises, queueMicrotask). 3) Process one macrotask (setTimeout, setInterval, I/O). 4) Repeat. Microtasks have priority over macrotasks. This is why Promise.then() executes before setTimeout(0). Understanding this prevents common async bugs."},
            {"topic": "React", "difficulty": "Easy", "question": "What is React? Explain components, props, and state.",
             "keywords": ["React", "component", "props", "state", "JSX", "virtual DOM", "render", "functional", "hook", "reusable"],
             "model_answer": "React is a UI library for building component-based interfaces. Components are reusable UI pieces. Props: data passed from parent to child (read-only). State: data managed within a component (mutable via setState/useState). JSX = JavaScript XML syntax. Virtual DOM: React's in-memory representation — diffs and updates only changed parts of real DOM. Functional components with hooks are the modern approach."},
            {"topic": "React", "difficulty": "Medium", "question": "Explain React hooks: useState, useEffect, useContext, and custom hooks.",
             "keywords": ["useState", "useEffect", "useContext", "hook", "lifecycle", "side effect", "cleanup", "dependency", "custom", "reuse"],
             "model_answer": "useState: manage state in functional components, returns [value, setter]. useEffect: handle side effects (API calls, subscriptions) — runs after render, cleanup function, dependency array controls when it re-runs. useContext: consume context without prop drilling. Custom hooks: extract reusable stateful logic (useAuth, useFetch). Rules: only call hooks at top level, only in React functions."},
            {"topic": "React", "difficulty": "Hard", "question": "How do you optimize React performance? Explain memoization and rendering optimization.",
             "keywords": ["memo", "useMemo", "useCallback", "render", "virtual DOM", "lazy", "Suspense", "key", "profiler", "code splitting"],
             "model_answer": "React.memo: skip re-render if props unchanged. useMemo: cache expensive computations. useCallback: stable function references for child components. React.lazy + Suspense for code splitting. Proper key props in lists (not index). Avoid: creating objects/functions in render, unnecessary state lifts. Tools: React DevTools Profiler to identify bottlenecks. Virtualize long lists (react-window). Server-side rendering for initial load."},
            {"topic": "TypeScript", "difficulty": "Easy", "question": "What is TypeScript? Why use it over JavaScript?",
             "keywords": ["TypeScript", "type", "interface", "compile", "static", "JavaScript", "error", "IDE", "safety", "annotation"],
             "model_answer": "TypeScript is a superset of JavaScript that adds static types. Benefits: catch errors at compile time, better IDE support (autocomplete, refactoring), self-documenting code, interfaces for contracts, easier refactoring, better for large codebases and teams. TypeScript compiles to JavaScript — no runtime overhead. Gradually adoptable in existing JS projects."},
            {"topic": "TypeScript", "difficulty": "Medium", "question": "Explain TypeScript generics, union types, and utility types with examples.",
             "keywords": ["generic", "union", "Partial", "Pick", "Omit", "Record", "type", "interface", "constraint", "T"],
             "model_answer": "Generics: reusable code with type parameters. function identity<T>(arg: T): T. Union types: value can be one of several types (string | number). Utility types: Partial<T> makes all properties optional, Pick<T, K> selects specific properties, Omit<T, K> removes properties, Record<K, V> creates object type. These make code flexible yet type-safe."},
            {"topic": "Web APIs", "difficulty": "Easy", "question": "Explain REST APIs and how the browser communicates with a backend server.",
             "keywords": ["REST", "HTTP", "fetch", "AJAX", "JSON", "request", "response", "status", "header", "CORS"],
             "model_answer": "REST: architectural style for web APIs using HTTP methods. Browser uses fetch() or XMLHttpRequest to send HTTP requests. Request has: method, URL, headers, body. Response has: status code, headers, body (usually JSON). CORS: browser security mechanism — server must allow cross-origin requests via headers. Async communication using Promises/async-await."},
            {"topic": "Web APIs", "difficulty": "Medium", "question": "What is CORS? Why does it exist and how do you handle CORS errors?",
             "keywords": ["CORS", "origin", "preflight", "OPTIONS", "Access-Control", "header", "browser", "security", "proxy", "server"],
             "model_answer": "CORS (Cross-Origin Resource Sharing) is a browser security mechanism that blocks requests to different origins (domain/port/protocol). Purpose: prevent malicious sites from accessing your APIs. Preflight: browser sends OPTIONS request first for non-simple requests. Fix: server sets Access-Control-Allow-Origin header. During development: use proxy in dev server config. Never use Access-Control-Allow-Origin: * in production with credentials."},
            {"topic": "State Management", "difficulty": "Medium", "question": "Compare different React state management approaches: Context, Redux, and Zustand.",
             "keywords": ["Context", "Redux", "Zustand", "state", "store", "reducer", "action", "global", "provider", "selector"],
             "model_answer": "Context: built-in, good for low-frequency updates (theme, auth). Problem: all consumers re-render on any change. Redux: predictable state container with actions, reducers, store. Good for complex state logic, middleware, devtools. Boilerplate-heavy. Zustand: minimal, hook-based, no providers needed. Simple API, good performance with selectors. Choose based on complexity: Context for simple, Zustand for medium, Redux for complex."},
            {"topic": "Testing", "difficulty": "Easy", "question": "How do you test React components? What tools do you use?",
             "keywords": ["Jest", "React Testing Library", "render", "screen", "fireEvent", "mock", "snapshot", "component", "query", "user event"],
             "model_answer": "Use Jest as test runner + React Testing Library for component testing. Test user behavior, not implementation details. render() the component, query with screen.getByRole/getByText (prefer accessible queries), simulate interactions with fireEvent/userEvent, assert with expect(). Mock API calls with jest.mock or MSW (Mock Service Worker). Snapshot tests for UI regression but don't overuse."},
            {"topic": "Performance", "difficulty": "Hard", "question": "How do you measure and improve web performance? Explain Core Web Vitals.",
             "keywords": ["LCP", "FID", "CLS", "performance", "lighthouse", "lazy", "bundle", "CDN", "cache", "optimize"],
             "model_answer": "Core Web Vitals: LCP (Largest Contentful Paint < 2.5s) — loading speed. FID/INP (First Input Delay/Interaction to Next Paint < 200ms) — interactivity. CLS (Cumulative Layout Shift < 0.1) — visual stability. Optimization: code splitting, lazy loading images/components, CDN for static assets, proper caching headers, tree shaking, bundle analysis (webpack-bundle-analyzer), minimize main thread work, optimize images (WebP, responsive), preload critical resources. Measure with Lighthouse and real user monitoring."},
            {"topic": "Security", "difficulty": "Medium", "question": "What are common frontend security vulnerabilities? How do you prevent XSS and CSRF?",
             "keywords": ["XSS", "CSRF", "sanitize", "escape", "token", "cookie", "Content-Security-Policy", "inject", "script", "security"],
             "model_answer": "XSS (Cross-Site Scripting): injecting malicious scripts. Prevention: escape user input, use Content-Security-Policy header, React auto-escapes JSX (avoid dangerouslySetInnerHTML). CSRF (Cross-Site Request Forgery): tricking user's browser to make authenticated requests. Prevention: CSRF tokens, SameSite cookie attribute, check Origin/Referer headers. Other: use HTTPS, secure cookies (HttpOnly, Secure), validate input on server side too."},
            {"topic": "Build Tools", "difficulty": "Medium", "question": "Explain Webpack, Vite, and modern JavaScript build tools. What problems do they solve?",
             "keywords": ["Webpack", "Vite", "bundle", "module", "loader", "plugin", "HMR", "tree shaking", "transpile", "build"],
             "model_answer": "Build tools solve: module bundling (combine files), transpilation (JSX/TS → JS), optimization (minification, tree shaking), dev experience (HMR — hot module replacement). Webpack: most configurable, loaders for any file type, large plugin ecosystem. Slow cold starts. Vite: uses native ES modules in dev (instant HMR), Rollup for production builds. Much faster dev experience. Modern projects should prefer Vite. Both handle code splitting, asset optimization, and environment variables."},
        ]
    },

    "default": {
        "name": "General Software Engineer",
        "topics": [
            {"topic": "Programming", "difficulty": "Easy", "question": "What are the differences between compiled and interpreted languages? Give examples.",
             "keywords": ["compiled", "interpreted", "Java", "Python", "JavaScript", "machine code", "runtime", "performance", "bytecode", "JIT"],
             "model_answer": "Compiled languages (C, C++, Go): source code translated to machine code before execution. Faster runtime, slower development cycle. Interpreted languages (Python, JavaScript, Ruby): code executed line by line at runtime. Slower execution, faster development. Many modern languages use hybrid approach: Java compiles to bytecode → JVM interprets/JIT compiles. Python compiles to bytecode → CPython interprets."},
            {"topic": "Programming", "difficulty": "Medium", "question": "Explain SOLID principles. Why are they important in software design?",
             "keywords": ["SOLID", "single responsibility", "open closed", "liskov", "interface", "dependency", "inversion", "principle", "design", "maintainable"],
             "model_answer": "S: Single Responsibility — class should have one reason to change. O: Open/Closed — open for extension, closed for modification. L: Liskov Substitution — subtypes must be substitutable for base types. I: Interface Segregation — many specific interfaces better than one general. D: Dependency Inversion — depend on abstractions, not concretions. They make code maintainable, testable, and flexible."},
            {"topic": "Programming", "difficulty": "Hard", "question": "Explain design patterns you've used. When would you use Strategy vs Factory vs Observer?",
             "keywords": ["pattern", "strategy", "factory", "observer", "singleton", "design", "interface", "decouple", "flexibility", "create"],
             "model_answer": "Strategy: define family of algorithms, make them interchangeable. Use when: different ways to do the same thing (sorting, payment methods). Factory: create objects without specifying exact class. Use when: object creation is complex or varies based on input. Observer: publish-subscribe for event handling. Use when: multiple objects need to react to state changes. Each pattern solves a specific coupling/flexibility problem."},
            {"topic": "Data Structures", "difficulty": "Easy", "question": "Explain arrays, linked lists, stacks, and queues. When to use each?",
             "keywords": ["array", "linked list", "stack", "queue", "LIFO", "FIFO", "insert", "delete", "access", "O(1)", "O(n)"],
             "model_answer": "Array: contiguous memory, O(1) access by index, O(n) insert/delete. Use for random access. Linked List: nodes with pointers, O(1) insert/delete at known position, O(n) access. Use for frequent insertions. Stack (LIFO): push/pop from top. Use for: undo, recursion, parsing. Queue (FIFO): enqueue/dequeue. Use for: BFS, task scheduling, message processing."},
            {"topic": "Data Structures", "difficulty": "Medium", "question": "Explain hash tables. How do they achieve O(1) lookups? What are collisions?",
             "keywords": ["hash", "table", "O(1)", "collision", "bucket", "key", "value", "function", "chain", "open addressing"],
             "model_answer": "Hash table: maps keys to values using a hash function that converts keys to array indices. Average O(1) for get/set/delete. Collision: two keys hash to same index. Resolution: chaining (linked list at each bucket) or open addressing (probing for next empty slot). Load factor = items/buckets. Resize (rehash) when load factor too high. Good hash function distributes keys uniformly."},
            {"topic": "Data Structures", "difficulty": "Hard", "question": "Explain trees and graphs. What algorithms do you use for traversal and searching?",
             "keywords": ["tree", "graph", "BFS", "DFS", "binary", "BST", "traversal", "node", "edge", "inorder", "preorder", "Dijkstra"],
             "model_answer": "Tree: hierarchical, one root, no cycles. Binary tree: max 2 children. BST: left < root < right, O(log n) search. Traversals: inorder (sorted), preorder (copy), postorder (delete). Graph: nodes + edges, can have cycles. BFS: level-by-level using queue, shortest path in unweighted. DFS: deep-first using stack/recursion, cycle detection. Dijkstra: shortest path in weighted graph."},
            {"topic": "Databases", "difficulty": "Easy", "question": "What is the difference between SQL and NoSQL databases?",
             "keywords": ["SQL", "NoSQL", "relational", "document", "schema", "ACID", "scale", "join", "table", "flexible"],
             "model_answer": "SQL: relational, fixed schema, tables with rows/columns, ACID transactions, complex joins. PostgreSQL, MySQL. NoSQL: flexible schema, types include document (MongoDB), key-value (Redis), column (Cassandra), graph (Neo4j). Choose SQL for structured data and complex queries, NoSQL for flexibility and horizontal scaling."},
            {"topic": "Databases", "difficulty": "Medium", "question": "Explain database indexing. How do indexes improve query performance? What are the tradeoffs?",
             "keywords": ["index", "B-tree", "query", "performance", "scan", "lookup", "write", "overhead", "composite", "covering"],
             "model_answer": "Indexes are data structures (usually B-tree) that speed up data retrieval. Without index: full table scan O(n). With index: O(log n) lookup. Types: single column, composite (multiple columns), unique, covering (includes all query columns). Tradeoffs: faster reads, slower writes (index must be updated), extra storage space. Don't over-index — each index costs write performance."},
            {"topic": "System Design", "difficulty": "Easy", "question": "Explain client-server architecture. How does a web application work end to end?",
             "keywords": ["client", "server", "HTTP", "request", "response", "browser", "backend", "database", "DNS", "load balancer"],
             "model_answer": "User types URL → DNS resolves to IP → browser sends HTTP request → load balancer routes to server → server processes request (reads/writes database) → returns HTTP response → browser renders HTML/CSS/JS. Layers: Client (browser/app), CDN (static files), Load Balancer, Application Server(s), Cache (Redis), Database. Each layer can scale independently."},
            {"topic": "System Design", "difficulty": "Medium", "question": "What is caching? Explain different caching strategies and when to use them.",
             "keywords": ["cache", "Redis", "CDN", "TTL", "invalidation", "write-through", "write-back", "LRU", "hit", "miss"],
             "model_answer": "Caching stores frequently accessed data in fast storage. Strategies: Cache-aside (lazy load): check cache, miss → read DB, store in cache. Write-through: write to cache and DB simultaneously. Write-back: write to cache, async sync to DB. Levels: browser cache, CDN, application cache (Redis/Memcached), database query cache. TTL for expiration. Invalidation is the hard part — stale data vs performance."},
            {"topic": "System Design", "difficulty": "Hard", "question": "How would you design a URL shortener like bit.ly? Walk through the architecture.",
             "keywords": ["hash", "encode", "database", "redirect", "scale", "cache", "analytics", "unique", "base62", "distributed"],
             "model_answer": "Requirements: shorten URLs, redirect, analytics. Architecture: Generate short code (base62 encoding of auto-increment ID or hash), store mapping in database (short_code → original_url), redirect with 301/302. Scaling: cache popular URLs in Redis, use CDN for global redirects, shard database by short_code. Analytics: async logging to analytics pipeline. Handle collisions with retry. Rate limiting to prevent abuse."},
            {"topic": "API Design", "difficulty": "Easy", "question": "What is REST? Explain RESTful API principles and HTTP methods.",
             "keywords": ["REST", "HTTP", "GET", "POST", "PUT", "DELETE", "stateless", "resource", "endpoint", "status code"],
             "model_answer": "REST principles: stateless (each request contains all info), resource-based URLs (/users/123), standard HTTP methods (GET=read, POST=create, PUT=update, DELETE=remove), proper status codes (200 OK, 201 Created, 404 Not Found, 500 Error). Resources are nouns, methods are verbs. Use JSON for request/response bodies. Versioning via URL (/api/v1/) or headers."},
            {"topic": "API Design", "difficulty": "Medium", "question": "Compare REST, GraphQL, and gRPC. When would you choose each?",
             "keywords": ["REST", "GraphQL", "gRPC", "query", "schema", "protobuf", "HTTP", "over-fetching", "microservice", "real-time"],
             "model_answer": "REST: simple, cacheable, widely adopted. Problem: over/under-fetching, multiple round trips. GraphQL: client specifies exactly what data it needs in one query. Schema-based. Good for: complex UIs with varied data needs, mobile apps (bandwidth). gRPC: binary protocol (protobuf), HTTP/2, bi-directional streaming. Good for: microservice communication, low latency, real-time. Choose based on use case: REST for public APIs, GraphQL for flexible frontends, gRPC for internal services."},
            {"topic": "Git", "difficulty": "Easy", "question": "Explain Git basics: branching, merging, rebasing. What is your branching strategy?",
             "keywords": ["branch", "merge", "rebase", "conflict", "PR", "main", "feature", "commit", "history", "review"],
             "model_answer": "Branch: independent line of development. Merge: combines branches (creates merge commit, preserves history). Rebase: replays commits on top of another branch (linear history, cleaner). My strategy: feature branches from main, small commits, PR with code review, squash merge to main. Resolve conflicts by understanding both changes, not blindly accepting."},
            {"topic": "Git", "difficulty": "Medium", "question": "How do you resolve merge conflicts? What is cherry-pick and interactive rebase?",
             "keywords": ["conflict", "resolve", "cherry-pick", "rebase", "interactive", "squash", "amend", "stash", "reset", "reflog"],
             "model_answer": "Resolve conflicts: open conflicted files, understand both changes, manually merge, test, commit. Cherry-pick: apply specific commit to another branch (git cherry-pick <hash>). Interactive rebase (git rebase -i): reorder, squash, edit, or drop commits. Use for cleaning history before PR. git stash: temporarily save uncommitted changes. git reflog: recovery tool — shows all HEAD movements."},
            {"topic": "Security", "difficulty": "Medium", "question": "What are common web security vulnerabilities? How do you prevent SQL injection and XSS?",
             "keywords": ["SQL injection", "XSS", "CSRF", "OWASP", "sanitize", "parameterized", "escape", "HTTPS", "authentication", "encryption"],
             "model_answer": "OWASP Top 10: SQL Injection — use parameterized queries, never concatenate user input into SQL. XSS — escape/sanitize output, Content-Security-Policy headers. CSRF — anti-CSRF tokens, SameSite cookies. Others: broken authentication (use bcrypt, MFA), sensitive data exposure (HTTPS, encryption at rest), security misconfiguration. Defense in depth: validate input, sanitize output, principle of least privilege."},
            {"topic": "Agile", "difficulty": "Easy", "question": "What is Agile? Explain Scrum ceremonies: sprint planning, standup, retrospective.",
             "keywords": ["Agile", "Scrum", "sprint", "standup", "retrospective", "planning", "backlog", "velocity", "iteration", "team"],
             "model_answer": "Agile: iterative development with frequent delivery and feedback. Scrum ceremonies: Sprint Planning — select stories from backlog, estimate, commit. Daily Standup — 15 min sync (what I did, what I'll do, blockers). Sprint Review/Demo — show completed work to stakeholders. Retrospective — team reflects on process improvements. Sprints are typically 2 weeks. Product Owner manages backlog priorities."},
            {"topic": "Cloud", "difficulty": "Medium", "question": "Explain the differences between IaaS, PaaS, and SaaS with examples.",
             "keywords": ["IaaS", "PaaS", "SaaS", "cloud", "AWS", "Heroku", "Gmail", "EC2", "infrastructure", "managed"],
             "model_answer": "IaaS (Infrastructure as a Service): raw compute/storage/network. You manage: OS, runtime, app. Example: AWS EC2, Azure VMs. PaaS (Platform as a Service): managed platform — you just deploy code. Example: Heroku, Google App Engine, AWS Elastic Beanstalk. SaaS (Software as a Service): fully managed application. Example: Gmail, Slack, Salesforce. More managed = less control but less operational overhead."},
        ]
    },

    # ─── Security Testing ───
    "security_testing": {
        "name": "Security Testing Engineer",
        "topics": [
            {"topic": "OWASP", "difficulty": "Easy", "question": "What is the OWASP Top 10 and why is it important?",
             "keywords": ["OWASP", "top 10", "vulnerabilities", "web", "injection", "broken auth", "XSS", "security"],
             "model_answer": "OWASP Top 10 is a standard list of the most critical web application security risks. It includes Broken Access Control, Cryptographic Failures, Injection, Insecure Design, Security Misconfiguration, Vulnerable Components, Authentication Failures, Data Integrity Failures, Logging Failures, and SSRF."},
            {"topic": "OWASP", "difficulty": "Easy", "question": "Explain the CIA triad in information security.",
             "keywords": ["confidentiality", "integrity", "availability", "encryption", "access control", "security"],
             "model_answer": "CIA triad: Confidentiality (data accessible only to authorized users), Integrity (data hasn't been tampered with), Availability (systems accessible when needed). All security controls should address at least one."},
            {"topic": "Web Security", "difficulty": "Medium", "question": "Explain Cross-Site Scripting (XSS) and its types with examples.",
             "keywords": ["XSS", "reflected", "stored", "DOM", "script", "injection", "sanitize", "encode", "CSP"],
             "model_answer": "XSS injects malicious scripts into web pages. Reflected: payload in URL reflected back. Stored: payload saved in DB, displayed to all users. DOM-based: client-side JS processes untrusted data. Prevention: output encoding, CSP headers, input validation."},
            {"topic": "Web Security", "difficulty": "Medium", "question": "What is SQL injection and how do you prevent it?",
             "keywords": ["SQL", "injection", "parameterized", "prepared", "ORM", "input", "sanitize", "escape"],
             "model_answer": "SQL injection inserts malicious SQL through user input. Prevention: parameterized queries, ORMs, input validation, least privilege DB accounts. Example payload: ' OR 1=1 --"},
            {"topic": "Web Security", "difficulty": "Medium", "question": "Explain CSRF attacks and prevention mechanisms.",
             "keywords": ["CSRF", "token", "cross-site", "request forgery", "SameSite", "cookie", "origin"],
             "model_answer": "CSRF tricks authenticated users into submitting malicious requests using their cookies. Prevention: CSRF tokens, SameSite cookie attribute, checking Origin/Referer headers."},
            {"topic": "Web Security", "difficulty": "Hard", "question": "What is SSRF and how do you test for it?",
             "keywords": ["SSRF", "server", "internal", "request", "metadata", "cloud", "whitelist", "URL"],
             "model_answer": "SSRF tricks the server into making requests to internal resources. Can access cloud metadata endpoints, internal services. Prevention: whitelist allowed URLs, block private IPs, validate URL schemes."},
            {"topic": "API Security", "difficulty": "Medium", "question": "What are the OWASP API Security Top 10 risks?",
             "keywords": ["BOLA", "authentication", "excessive data", "rate limiting", "BFLA", "mass assignment"],
             "model_answer": "BOLA, Broken Authentication, Broken Object Property Level Auth, Unrestricted Resource Consumption, BFLA, Unrestricted Access to Sensitive Flows, SSRF, Security Misconfiguration, Improper Inventory, Unsafe API Consumption."},
            {"topic": "API Security", "difficulty": "Hard", "question": "How do you test for Broken Object Level Authorization (BOLA/IDOR)?",
             "keywords": ["BOLA", "IDOR", "authorization", "object", "ID", "access control", "horizontal"],
             "model_answer": "Authenticate as User A, note resource IDs, try accessing User B's resources by changing IDs. Test all CRUD operations. Automate by replacing object references. Verify server-side auth checks."},
            {"topic": "Security Tools", "difficulty": "Easy", "question": "How do you use OWASP ZAP for security testing?",
             "keywords": ["ZAP", "proxy", "spider", "scan", "active", "passive", "intercept", "automated"],
             "model_answer": "Configure browser proxy through ZAP, spider the app, run passive scan (analyzes traffic), run active scan (sends attack payloads), review alerts by risk level. Supports API scanning, authenticated scanning, CI/CD integration."},
            {"topic": "Security Tools", "difficulty": "Medium", "question": "Compare SAST, DAST, and IAST security testing approaches.",
             "keywords": ["SAST", "DAST", "IAST", "static", "dynamic", "interactive", "source code", "runtime"],
             "model_answer": "SAST: analyzes source code (white box), finds issues early. DAST: tests running apps from outside (black box). IAST: instruments the app during testing, combining both approaches for accuracy."},
            {"topic": "Security Tools", "difficulty": "Medium", "question": "How do you integrate security testing into CI/CD pipelines?",
             "keywords": ["DevSecOps", "pipeline", "shift left", "SAST", "DAST", "SCA", "gate", "automated"],
             "model_answer": "Pre-commit: secret scanning. Build: SAST scan, dependency check. Test: DAST baseline. Deploy gate: fail on critical findings. Production: continuous monitoring, WAF."},
            {"topic": "Security Testing", "difficulty": "Hard", "question": "What is threat modeling and how do you perform it?",
             "keywords": ["threat", "model", "STRIDE", "attack surface", "assets", "data flow", "mitigations"],
             "model_answer": "Identify threats: define scope/assets, create data flow diagrams, apply STRIDE framework, rate risks with DREAD, define mitigations. Done early in design phase."},
            {"topic": "Security Testing", "difficulty": "Easy", "question": "How do you test for broken authentication vulnerabilities?",
             "keywords": ["brute force", "session", "password", "MFA", "credential stuffing", "lockout", "token"],
             "model_answer": "Test brute force resistance, credential stuffing, session management, password policy, MFA bypass, token predictability, password reset flow, default credentials."},
            {"topic": "Security Testing", "difficulty": "Hard", "question": "How do you scan for vulnerable dependencies in a project?",
             "keywords": ["SCA", "CVE", "npm audit", "Snyk", "Dependabot", "vulnerability", "SBOM"],
             "model_answer": "Use SCA tools: npm audit, pip-audit, Snyk, Dependabot. Check against CVE databases. Run in CI/CD, block on critical CVEs, auto-update with Dependabot/Renovate."},
            {"topic": "Security Testing", "difficulty": "Medium", "question": "What security headers should web applications implement?",
             "keywords": ["CORS", "CSP", "HSTS", "X-Content-Type", "X-Frame-Options", "headers", "cache"],
             "model_answer": "Content-Security-Policy, Strict-Transport-Security (HSTS), X-Content-Type-Options: nosniff, X-Frame-Options, CORS headers, Cache-Control for sensitive data. Remove Server, X-Powered-By headers."},
            {"topic": "Encryption", "difficulty": "Medium", "question": "Explain the difference between symmetric and asymmetric encryption.",
             "keywords": ["symmetric", "asymmetric", "AES", "RSA", "public key", "private key", "TLS", "hash"],
             "model_answer": "Symmetric: same key for encrypt/decrypt (AES), fast, used for data. Asymmetric: public/private key pair (RSA), slower, used for key exchange and signatures. TLS uses both: asymmetric for handshake, symmetric for data transfer."},
            {"topic": "Encryption", "difficulty": "Hard", "question": "How does TLS/SSL work and what do you verify during security testing?",
             "keywords": ["TLS", "SSL", "certificate", "handshake", "cipher", "HTTPS", "pinning", "version"],
             "model_answer": "TLS handshake: client hello, server certificate, key exchange, encrypted session. Test: valid certificates, strong cipher suites, TLS 1.2+ only, certificate pinning, HSTS, no mixed content, proper redirect HTTP->HTTPS."},
            {"topic": "Penetration Testing", "difficulty": "Easy", "question": "What is penetration testing and how does it differ from vulnerability scanning?",
             "keywords": ["pentest", "vulnerability", "exploit", "manual", "automated", "scope", "report"],
             "model_answer": "Vulnerability scanning: automated tools identify known vulnerabilities. Penetration testing: manual + automated, attempts to exploit vulnerabilities, validates real risk, requires scope agreement. Pentest proves exploitability, vuln scanning finds potential issues."},
            {"topic": "Penetration Testing", "difficulty": "Hard", "question": "Describe your approach to testing authentication and session management.",
             "keywords": ["session", "cookie", "token", "fixation", "hijacking", "timeout", "logout", "concurrent"],
             "model_answer": "Test: session fixation, session hijacking, cookie security flags (Secure, HttpOnly, SameSite), session timeout, logout invalidation, concurrent sessions, token entropy, session regeneration after auth."},
        ]
    },

    # ─── Cloud Computing ───
    "cloud": {
        "name": "Cloud Engineer",
        "topics": [
            {"topic": "Cloud Fundamentals", "difficulty": "Easy", "question": "Explain IaaS, PaaS, and SaaS with examples.",
             "keywords": ["IaaS", "PaaS", "SaaS", "EC2", "Heroku", "cloud", "managed", "infrastructure"],
             "model_answer": "IaaS: raw compute/storage (AWS EC2, Azure VMs). PaaS: managed platform, deploy code only (Heroku, App Engine). SaaS: fully managed application (Gmail, Slack). More managed = less control but less operational overhead."},
            {"topic": "Cloud Fundamentals", "difficulty": "Easy", "question": "What is the shared responsibility model in cloud computing?",
             "keywords": ["shared responsibility", "provider", "customer", "security", "infrastructure", "data", "compliance"],
             "model_answer": "Cloud provider manages: physical infrastructure, hypervisor, network. Customer manages: OS patches, application security, data encryption, IAM, network configs. Division varies by service type (IaaS vs PaaS vs SaaS)."},
            {"topic": "AWS", "difficulty": "Medium", "question": "Explain key AWS compute services and when to use each.",
             "keywords": ["EC2", "Lambda", "ECS", "Fargate", "auto-scaling", "serverless", "container"],
             "model_answer": "EC2: full control VMs, use for custom setups. Lambda: serverless functions, use for event-driven, short tasks. ECS/Fargate: container orchestration, use for microservices. Auto Scaling groups for EC2, Lambda scales automatically."},
            {"topic": "AWS", "difficulty": "Medium", "question": "How do VPCs, subnets, and security groups work?",
             "keywords": ["VPC", "subnet", "public", "private", "security group", "NACL", "route table", "gateway"],
             "model_answer": "VPC: isolated virtual network. Subnets: segments within VPC (public with internet gateway, private without). Security Groups: stateful instance-level firewall. NACLs: stateless subnet-level firewall. Route tables control traffic flow."},
            {"topic": "AWS", "difficulty": "Hard", "question": "Explain AWS IAM best practices.",
             "keywords": ["IAM", "least privilege", "role", "policy", "MFA", "access key", "federation", "rotation"],
             "model_answer": "Least privilege access, use IAM roles over access keys, enable MFA, rotate credentials regularly, use AWS Organizations and SCPs, audit with CloudTrail, use policy conditions, avoid root account usage."},
            {"topic": "Cloud Storage", "difficulty": "Easy", "question": "Compare S3, EBS, and EFS storage services.",
             "keywords": ["S3", "EBS", "EFS", "object", "block", "file", "bucket", "volume"],
             "model_answer": "S3: object storage, unlimited, accessed via HTTP/API. EBS: block storage, attached to single EC2, like a hard drive. EFS: managed NFS file system, shared across multiple EC2 instances. Choose based on access pattern and sharing needs."},
            {"topic": "Cloud Storage", "difficulty": "Medium", "question": "How do you design a highly available architecture on AWS?",
             "keywords": ["multi-AZ", "load balancer", "auto-scaling", "RDS", "failover", "redundancy", "health check"],
             "model_answer": "Use multiple Availability Zones, Application Load Balancer for traffic distribution, Auto Scaling Groups, Multi-AZ RDS for database, S3 for durability, Route 53 for DNS failover, health checks at each layer."},
            {"topic": "Cloud Database", "difficulty": "Medium", "question": "When would you use RDS vs DynamoDB vs ElastiCache?",
             "keywords": ["RDS", "DynamoDB", "ElastiCache", "relational", "NoSQL", "cache", "Redis", "scaling"],
             "model_answer": "RDS: relational data, complex queries, ACID transactions. DynamoDB: key-value/document, massive scale, single-digit millisecond latency. ElastiCache (Redis/Memcached): caching layer, session store, real-time data. Choose based on data model and access patterns."},
            {"topic": "Cloud Security", "difficulty": "Medium", "question": "How do you manage secrets and encryption in the cloud?",
             "keywords": ["KMS", "Secrets Manager", "Parameter Store", "encryption", "at rest", "in transit", "vault"],
             "model_answer": "AWS KMS for encryption key management, Secrets Manager for rotating secrets, Parameter Store for config. Encrypt at rest (S3, EBS, RDS) and in transit (TLS). Never hardcode secrets, use IAM roles for access."},
            {"topic": "Cloud Security", "difficulty": "Hard", "question": "Explain cloud compliance and governance strategies.",
             "keywords": ["compliance", "governance", "audit", "CloudTrail", "Config", "GuardDuty", "SCPs", "tagging"],
             "model_answer": "AWS CloudTrail for API audit logs, AWS Config for resource compliance rules, GuardDuty for threat detection, SCPs for organization-wide restrictions, tagging policies for cost allocation, Security Hub for centralized security view. Map to compliance frameworks (SOC 2, HIPAA, PCI-DSS)."},
            {"topic": "Serverless", "difficulty": "Easy", "question": "What is serverless computing and its benefits?",
             "keywords": ["serverless", "Lambda", "event-driven", "pay-per-use", "scale", "no server", "function"],
             "model_answer": "Serverless: cloud provider manages infrastructure, you deploy functions. Benefits: no server management, auto-scaling, pay-per-execution, reduced operational cost. Trade-offs: cold starts, execution time limits, vendor lock-in."},
            {"topic": "Serverless", "difficulty": "Hard", "question": "How do you design event-driven architectures with serverless?",
             "keywords": ["event", "trigger", "SQS", "SNS", "EventBridge", "Step Functions", "async", "decoupled"],
             "model_answer": "Use events as triggers: S3 events -> Lambda, SQS/SNS for messaging, EventBridge for event routing, Step Functions for workflow orchestration, API Gateway for HTTP triggers. Design for idempotency, handle retries, use DLQs for failures."},
            {"topic": "Cloud Networking", "difficulty": "Medium", "question": "How do CDNs work and when should you use one?",
             "keywords": ["CDN", "CloudFront", "edge", "cache", "latency", "origin", "distribution"],
             "model_answer": "CDN distributes content to edge locations globally, reducing latency. Use for: static assets, API acceleration, video streaming, DDoS protection. Configure: cache behaviors, TTL, origin failover, custom error pages."},
            {"topic": "Cloud Cost", "difficulty": "Medium", "question": "How do you optimize cloud costs?",
             "keywords": ["cost", "reserved", "spot", "right-sizing", "monitoring", "tagging", "budget", "savings"],
             "model_answer": "Right-size instances, use Reserved/Savings Plans for predictable workloads, Spot instances for fault-tolerant tasks, auto-scaling to match demand, monitor with Cost Explorer, enforce tagging, set budget alerts, use S3 lifecycle policies."},
        ]
    },

    # ─── Mobile Testing ───
    "mobile_testing": {
        "name": "Mobile Testing Engineer",
        "topics": [
            {"topic": "Mobile Fundamentals", "difficulty": "Easy", "question": "What are the key differences between testing iOS and Android applications?",
             "keywords": ["iOS", "Android", "platform", "fragmentation", "emulator", "simulator", "store", "guidelines"],
             "model_answer": "Android: device fragmentation (many OEMs, screen sizes, OS versions), uses emulators, APK sideloading. iOS: limited devices, uses simulators, strict App Store guidelines, requires Mac for testing. Both need: real device testing, network condition testing, permission testing."},
            {"topic": "Mobile Fundamentals", "difficulty": "Medium", "question": "How do you set up a mobile test automation strategy?",
             "keywords": ["strategy", "framework", "device", "cloud", "parallel", "real device", "emulator", "CI"],
             "model_answer": "Choose framework (Appium, Espresso, XCUITest). Mix emulators (fast, CI) and real devices (accuracy). Use cloud device farms (BrowserStack, Sauce Labs) for coverage. Test on top devices by market share. Integrate into CI/CD. Cover: functional, performance, compatibility, accessibility."},
            {"topic": "Appium", "difficulty": "Easy", "question": "What is Appium and how does it work?",
             "keywords": ["Appium", "cross-platform", "WebDriver", "capabilities", "server", "client", "native", "hybrid"],
             "model_answer": "Appium is open-source cross-platform mobile test automation framework. Uses WebDriver protocol. Supports native, hybrid, mobile web apps. Doesn't require app modification. Server translates commands to platform-specific automation (UIAutomator2 for Android, XCUITest for iOS). Language-agnostic client libraries."},
            {"topic": "Appium", "difficulty": "Medium", "question": "Explain Appium desired capabilities and how to configure them.",
             "keywords": ["capabilities", "platformName", "deviceName", "app", "automationName", "appPackage", "bundleId"],
             "model_answer": "Desired capabilities configure the Appium session: platformName (Android/iOS), deviceName, app (path/URL), automationName (UiAutomator2/XCUITest), platformVersion, appPackage/appActivity (Android), bundleId (iOS). Additional: noReset, fullReset, autoGrantPermissions."},
            {"topic": "Appium", "difficulty": "Hard", "question": "How do you handle gestures and complex interactions in Appium?",
             "keywords": ["gesture", "swipe", "scroll", "tap", "long press", "W3C Actions", "TouchAction", "coordinates"],
             "model_answer": "Use W3C Actions API for complex gestures: swipe (press, wait, moveTo, release), scroll (find scrollable element, swipe direction), long press (press with duration), pinch/zoom (multi-touch). Calculate coordinates relative to element or screen. Use UiScrollable for Android scroll-to-element."},
            {"topic": "Mobile Testing", "difficulty": "Easy", "question": "What types of mobile testing should be performed?",
             "keywords": ["functional", "performance", "usability", "compatibility", "security", "network", "battery"],
             "model_answer": "Functional (features work), UI/Usability (responsive, intuitive), Compatibility (devices, OS versions), Performance (load time, memory, CPU), Network (offline, slow connection, switching), Security (data storage, auth), Battery consumption, Installation/Update, Interrupt testing (calls, notifications)."},
            {"topic": "Mobile Testing", "difficulty": "Medium", "question": "How do you test mobile apps under different network conditions?",
             "keywords": ["network", "throttle", "offline", "3G", "4G", "WiFi", "proxy", "Charles", "airplane"],
             "model_answer": "Use network throttling tools (Charles Proxy, Android emulator network settings), test on 2G/3G/4G/WiFi, test offline mode, test network switching, test request timeouts, use airplane mode, simulate packet loss. Verify: graceful degradation, cached data, retry mechanisms, error messages."},
            {"topic": "Mobile Testing", "difficulty": "Hard", "question": "How do you implement Page Object Model in Appium?",
             "keywords": ["POM", "page object", "locator", "reusable", "class", "abstraction", "maintainable"],
             "model_answer": "Create screen classes with locators (by accessibility ID, XPath, class). Methods represent user actions. Use base screen class for common methods (wait, swipe). Share locators between platforms using strategy pattern or separate platform-specific page objects. Use factory pattern for cross-platform page creation."},
            {"topic": "Mobile CI/CD", "difficulty": "Medium", "question": "How do you integrate mobile tests into CI/CD?",
             "keywords": ["CI", "pipeline", "emulator", "cloud", "parallel", "artifact", "build", "distribute"],
             "model_answer": "CI builds app (Gradle/Xcode), starts emulator or connects to cloud farm, runs tests in parallel, generates reports. Use: GitHub Actions with emulator action, Fastlane for build/distribute, BrowserStack/Sauce Labs for cloud execution, Allure for reporting. Distribute test builds via Firebase App Distribution."},
            {"topic": "Mobile Performance", "difficulty": "Hard", "question": "How do you test mobile app performance?",
             "keywords": ["performance", "memory", "CPU", "battery", "profiler", "ANR", "leak", "frame rate"],
             "model_answer": "Use platform profilers: Android Profiler (CPU, memory, network, battery), Xcode Instruments (Time Profiler, Leaks, Energy). Monitor: app launch time, frame rate (60fps target), memory leaks, CPU usage, battery drain, network bandwidth. Test: ANR on Android, UI thread blocking, large data sets, image loading performance."},
        ]
    },

    # ─── Data Engineering ───
    "data_engineering": {
        "name": "Data Engineer",
        "topics": [
            {"topic": "Data Fundamentals", "difficulty": "Easy", "question": "What is ETL and how does it differ from ELT?",
             "keywords": ["ETL", "ELT", "extract", "transform", "load", "pipeline", "warehouse", "data lake"],
             "model_answer": "ETL: Extract from sources, Transform in staging area, Load into target. ELT: Extract, Load into data lake/warehouse, Transform using warehouse compute power. ELT preferred with modern cloud warehouses (BigQuery, Snowflake, Redshift) as they have massive compute."},
            {"topic": "Data Fundamentals", "difficulty": "Medium", "question": "Explain data warehouse vs data lake vs data lakehouse.",
             "keywords": ["warehouse", "lake", "lakehouse", "structured", "schema", "raw", "ACID", "Delta Lake"],
             "model_answer": "Data Warehouse: structured data, schema-on-write, optimized for BI/analytics (Snowflake, Redshift). Data Lake: raw data in any format, schema-on-read, cheap storage (S3, ADLS). Data Lakehouse: combines both - open formats (Delta Lake, Iceberg) on lake storage with warehouse features (ACID, schema enforcement)."},
            {"topic": "SQL", "difficulty": "Easy", "question": "Explain window functions in SQL with examples.",
             "keywords": ["window", "OVER", "PARTITION BY", "ROW_NUMBER", "RANK", "LAG", "LEAD", "aggregate"],
             "model_answer": "Window functions compute across rows related to current row without grouping. ROW_NUMBER() OVER (PARTITION BY dept ORDER BY salary DESC) numbers rows per department. RANK for ranking with ties, LAG/LEAD for previous/next row values, running SUM/AVG with OVER clause."},
            {"topic": "SQL", "difficulty": "Medium", "question": "What are CTEs and how do you use them for complex queries?",
             "keywords": ["CTE", "WITH", "recursive", "readable", "subquery", "temporary", "modular"],
             "model_answer": "Common Table Expressions: WITH cte AS (SELECT ...) SELECT * FROM cte. Benefits: readable, reusable within query, recursive CTEs for hierarchies/graphs. Better than nested subqueries for complex logic. Recursive CTE: WITH RECURSIVE for tree traversal, generating series."},
            {"topic": "SQL", "difficulty": "Hard", "question": "How do you optimize slow SQL queries?",
             "keywords": ["index", "EXPLAIN", "plan", "join", "partition", "statistics", "covering", "N+1"],
             "model_answer": "Use EXPLAIN ANALYZE to understand query plan. Add indexes on WHERE/JOIN columns, use covering indexes, avoid SELECT *, partition large tables, update statistics, rewrite correlated subqueries as JOINs, use CTEs for readability, avoid N+1 queries, use query hints when needed."},
            {"topic": "Python Data", "difficulty": "Medium", "question": "How do you use Pandas for data transformation?",
             "keywords": ["Pandas", "DataFrame", "merge", "groupby", "apply", "vectorized", "memory", "chunk"],
             "model_answer": "DataFrame operations: read_csv/parquet, merge/join DataFrames, groupby for aggregation, apply for custom transforms, vectorized operations for performance. Handle large data: chunked reading, categorical dtypes, query() for filtering. Use pipe() for chaining transforms."},
            {"topic": "Python Data", "difficulty": "Hard", "question": "Compare Pandas, PySpark, and Polars for data processing.",
             "keywords": ["Pandas", "PySpark", "Polars", "distributed", "lazy", "single node", "performance", "scale"],
             "model_answer": "Pandas: single-node, eager, rich ecosystem, great for < 10GB. PySpark: distributed, lazy evaluation, handles petabytes, requires cluster. Polars: single-node, lazy/eager, Rust-based, very fast, modern API. Choose Pandas for small data, PySpark for big data clusters, Polars for fast single-node processing."},
            {"topic": "Data Pipelines", "difficulty": "Easy", "question": "What is Apache Airflow and how does it work?",
             "keywords": ["Airflow", "DAG", "task", "operator", "scheduler", "dependency", "orchestration", "workflow"],
             "model_answer": "Airflow is a workflow orchestration platform. DAGs define task dependencies as directed acyclic graphs. Operators execute tasks (PythonOperator, BashOperator, SQL operators). Scheduler triggers DAGs on schedule/events. Features: retry logic, monitoring UI, XCom for task communication, connections for external systems."},
            {"topic": "Data Pipelines", "difficulty": "Medium", "question": "How do you handle data quality in pipelines?",
             "keywords": ["quality", "validation", "schema", "completeness", "freshness", "Great Expectations", "test", "anomaly"],
             "model_answer": "Data quality checks: schema validation, null/completeness checks, uniqueness constraints, referential integrity, value range checks, freshness monitoring. Tools: Great Expectations, dbt tests, custom assertions. Implement: at ingestion, after transformation, before serving. Alert on failures, quarantine bad data."},
            {"topic": "Data Pipelines", "difficulty": "Hard", "question": "Explain batch vs stream processing and when to use each.",
             "keywords": ["batch", "stream", "Kafka", "Spark", "Flink", "real-time", "latency", "throughput"],
             "model_answer": "Batch: processes accumulated data periodically (hourly/daily), high throughput, higher latency. Stream: processes data as it arrives, low latency, continuous. Batch tools: Spark, Airflow. Stream tools: Kafka Streams, Flink, Spark Streaming. Use batch for analytics/reports, stream for real-time dashboards/alerts. Lambda/Kappa architecture combines both."},
        ]
    },

    # ─── Machine Learning ───
    "machine_learning": {
        "name": "ML Engineer",
        "topics": [
            {"topic": "ML Fundamentals", "difficulty": "Easy", "question": "Explain supervised vs unsupervised learning with examples.",
             "keywords": ["supervised", "unsupervised", "labeled", "classification", "regression", "clustering", "labeled data"],
             "model_answer": "Supervised: learns from labeled data. Classification (spam/not spam, image recognition), Regression (price prediction, temperature forecasting). Unsupervised: finds patterns in unlabeled data. Clustering (customer segmentation), Dimensionality reduction (PCA), Anomaly detection."},
            {"topic": "ML Fundamentals", "difficulty": "Medium", "question": "What is overfitting and how do you prevent it?",
             "keywords": ["overfitting", "regularization", "cross-validation", "dropout", "early stopping", "data augmentation"],
             "model_answer": "Overfitting: model performs well on training data but poorly on unseen data. Prevention: more training data, cross-validation, regularization (L1/L2), dropout (neural networks), early stopping, feature selection, ensemble methods, data augmentation, simpler model architecture."},
            {"topic": "ML Fundamentals", "difficulty": "Easy", "question": "What are common evaluation metrics for classification models?",
             "keywords": ["accuracy", "precision", "recall", "F1", "AUC", "ROC", "confusion matrix", "threshold"],
             "model_answer": "Accuracy: correct predictions / total. Precision: true positives / predicted positives. Recall: true positives / actual positives. F1: harmonic mean of precision and recall. AUC-ROC: model's ability to distinguish classes. Use confusion matrix to visualize. Choose metric based on business cost of false positives vs false negatives."},
            {"topic": "Feature Engineering", "difficulty": "Medium", "question": "What is feature engineering and why is it important?",
             "keywords": ["feature", "encoding", "scaling", "normalization", "one-hot", "interaction", "selection"],
             "model_answer": "Feature engineering creates/transforms input features to improve model performance. Techniques: encoding categoricals (one-hot, label), scaling numerics (StandardScaler, MinMaxScaler), creating interaction features, handling missing values, time-based features, text vectorization (TF-IDF). Good features > complex models."},
            {"topic": "Scikit-learn", "difficulty": "Medium", "question": "How do you build an ML pipeline with scikit-learn?",
             "keywords": ["Pipeline", "ColumnTransformer", "cross_val_score", "GridSearchCV", "fit", "predict", "preprocessor"],
             "model_answer": "Use sklearn Pipeline to chain preprocessing and model: ColumnTransformer for different column types, StandardScaler/OneHotEncoder for transforms, model at end. GridSearchCV for hyperparameter tuning with cross-validation. Pipeline prevents data leakage by fitting transforms on training data only."},
            {"topic": "Deep Learning", "difficulty": "Medium", "question": "Explain neural networks and backpropagation.",
             "keywords": ["neural network", "layer", "activation", "gradient", "backpropagation", "loss", "optimizer", "weights"],
             "model_answer": "Neural networks: layers of interconnected neurons with weights. Forward pass: input -> hidden layers (with activation functions like ReLU) -> output. Loss function measures error. Backpropagation: compute gradients of loss w.r.t. weights using chain rule, propagate backward. Optimizer (SGD, Adam) updates weights to minimize loss."},
            {"topic": "Deep Learning", "difficulty": "Hard", "question": "Compare CNNs and RNNs and their use cases.",
             "keywords": ["CNN", "RNN", "convolution", "recurrent", "LSTM", "image", "sequence", "transformer"],
             "model_answer": "CNNs: spatial hierarchies via convolution filters, used for images, video, spatial data. RNNs: sequential data via hidden state, used for text, time series. LSTM/GRU: solve vanishing gradient in RNNs. Transformers now replace RNNs for most sequence tasks with attention mechanism. CNNs for vision, Transformers for NLP/sequence."},
            {"topic": "MLOps", "difficulty": "Easy", "question": "What is MLOps and why is it important?",
             "keywords": ["MLOps", "deployment", "monitoring", "pipeline", "reproducibility", "versioning", "CI/CD"],
             "model_answer": "MLOps applies DevOps practices to ML: model versioning, experiment tracking, automated training pipelines, model serving/deployment, monitoring model performance, data/model drift detection. Tools: MLflow, Kubeflow, DVC, Weights & Biases. Ensures reproducibility, reliability, and scalability of ML systems."},
            {"topic": "MLOps", "difficulty": "Medium", "question": "How do you deploy and serve ML models?",
             "keywords": ["serving", "API", "Flask", "FastAPI", "container", "batch", "real-time", "edge"],
             "model_answer": "Real-time: REST API (Flask/FastAPI), containerized (Docker), Kubernetes for scaling. Batch: scheduled prediction jobs. Options: cloud ML services (SageMaker, Vertex AI), self-hosted (TorchServe, TF Serving), edge deployment (ONNX, TensorFlow Lite). Consider: latency requirements, model size, scaling needs."},
            {"topic": "MLOps", "difficulty": "Hard", "question": "How do you handle model drift and monitoring in production?",
             "keywords": ["drift", "monitoring", "data drift", "concept drift", "retrain", "alert", "distribution", "performance"],
             "model_answer": "Data drift: input distribution changes (monitor feature distributions with KL divergence, PSI). Concept drift: relationship between input and output changes (monitor prediction performance). Solutions: automated retraining triggers, shadow models, A/B testing, canary deployments. Tools: Evidently, WhyLabs, custom dashboards."},
        ]
    },

    # ─── System Design ───
    "system_design": {
        "name": "System Design Engineer",
        "topics": [
            {"topic": "Fundamentals", "difficulty": "Easy", "question": "Explain the CAP theorem and its implications.",
             "keywords": ["CAP", "consistency", "availability", "partition tolerance", "trade-off", "distributed"],
             "model_answer": "CAP theorem: distributed systems can guarantee only 2 of 3: Consistency (all nodes see same data), Availability (every request gets a response), Partition Tolerance (system works despite network partitions). Since network partitions are inevitable, choose CP (consistent, e.g., MongoDB) or AP (available, e.g., Cassandra)."},
            {"topic": "Fundamentals", "difficulty": "Easy", "question": "What is horizontal vs vertical scaling?",
             "keywords": ["horizontal", "vertical", "scale out", "scale up", "load balancer", "stateless", "partition"],
             "model_answer": "Vertical: add more power (CPU, RAM) to existing machine - simpler but has limits. Horizontal: add more machines - handles unlimited scale but requires load balancing, stateless design, data partitioning. Prefer horizontal for web services. Use both: vertical for databases, horizontal for application servers."},
            {"topic": "Components", "difficulty": "Medium", "question": "Explain load balancing strategies and algorithms.",
             "keywords": ["load balancer", "round robin", "least connections", "consistent hashing", "health check", "L4", "L7"],
             "model_answer": "Algorithms: Round Robin (equal distribution), Weighted RR (proportional), Least Connections (fewest active), IP Hash (sticky sessions), Consistent Hashing (minimize redistribution). L4: TCP/UDP level, fast. L7: HTTP level, content-based routing. Health checks ensure traffic goes to healthy instances."},
            {"topic": "Components", "difficulty": "Medium", "question": "How do caching strategies work? Compare write-through, write-back, and cache-aside.",
             "keywords": ["cache", "Redis", "write-through", "write-back", "cache-aside", "TTL", "eviction", "invalidation"],
             "model_answer": "Cache-aside: app checks cache first, on miss reads DB and populates cache. Write-through: writes go to cache and DB simultaneously. Write-back: writes to cache only, async sync to DB (risk of data loss). Cache eviction: LRU, LFU, TTL-based. Tools: Redis, Memcached. Consider: cache invalidation, thundering herd, cache warming."},
            {"topic": "Components", "difficulty": "Hard", "question": "Design a message queue system. When do you use queues vs pub/sub?",
             "keywords": ["queue", "pub/sub", "Kafka", "RabbitMQ", "SQS", "async", "decoupled", "consumer group"],
             "model_answer": "Queue (point-to-point): message consumed by one consumer, work distribution (SQS, RabbitMQ). Pub/Sub: message delivered to all subscribers, event broadcasting (SNS, Kafka topics). Kafka: distributed log, consumer groups, replay capability. Use queues for task processing, pub/sub for event notification, Kafka for event streaming/sourcing."},
            {"topic": "Databases", "difficulty": "Medium", "question": "When would you choose SQL vs NoSQL databases?",
             "keywords": ["SQL", "NoSQL", "relational", "document", "key-value", "ACID", "schema", "consistency"],
             "model_answer": "SQL: structured data, complex queries, ACID transactions, relationships (PostgreSQL, MySQL). NoSQL: flexible schema, horizontal scaling, high throughput. Types: Document (MongoDB), Key-Value (Redis, DynamoDB), Column (Cassandra), Graph (Neo4j). Choose SQL for financial data, NoSQL for user profiles, sessions, catalogs."},
            {"topic": "Databases", "difficulty": "Hard", "question": "Explain database sharding strategies and challenges.",
             "keywords": ["sharding", "partition", "hash", "range", "lookup", "cross-shard", "rebalancing", "hot spot"],
             "model_answer": "Sharding splits data across databases. Strategies: hash-based (even distribution, hard range queries), range-based (easy range queries, risk of hot spots), directory-based (flexible, lookup overhead). Challenges: cross-shard queries/joins, rebalancing when adding shards, maintaining consistency, distributed transactions."},
            {"topic": "Patterns", "difficulty": "Medium", "question": "Explain microservices architecture and its trade-offs.",
             "keywords": ["microservice", "monolith", "service", "API", "independent", "deployment", "complexity", "distributed"],
             "model_answer": "Microservices: small, independent services communicating via APIs. Benefits: independent deployment, tech diversity, team autonomy, fault isolation, scaling per service. Trade-offs: distributed system complexity, network latency, data consistency, operational overhead, debugging difficulty. Start with monolith, extract services when needed."},
            {"topic": "Patterns", "difficulty": "Hard", "question": "How do you handle distributed transactions?",
             "keywords": ["saga", "two-phase commit", "eventual consistency", "compensating", "outbox", "event sourcing"],
             "model_answer": "Two-Phase Commit (2PC): coordinator asks all to prepare, then commit - strong consistency but slow, blocking. Saga Pattern: sequence of local transactions with compensating actions for rollback - eventual consistency, better availability. Outbox Pattern: write event to outbox table in same transaction, publish asynchronously. Event Sourcing: store events as source of truth."},
            {"topic": "Practice", "difficulty": "Hard", "question": "Design a URL shortener system (like bit.ly).",
             "keywords": ["hash", "base62", "database", "redirect", "cache", "analytics", "scale", "collision"],
             "model_answer": "Requirements: shorten URL, redirect, analytics. Design: generate short code (base62 encoding of auto-increment ID or hash), store mapping in database (key-value), 301/302 redirect. Scale: cache popular URLs in Redis, read-heavy so replicate DB, use CDN. Handle: collision detection, custom aliases, expiration, analytics (clicks, referrers, geo)."},
        ]
    },

    # ─── Performance Testing (expanded) ───
    "performance_testing": {
        "name": "Performance Testing Engineer",
        "topics": [
            {"topic": "Performance Fundamentals", "difficulty": "Easy", "question": "What are the different types of performance testing?",
             "keywords": ["load", "stress", "endurance", "spike", "volume", "scalability", "baseline"],
             "model_answer": "Load: expected user load. Stress: beyond capacity. Endurance/soak: sustained load over time. Spike: sudden load increase. Volume: large data volumes. Scalability: how system scales with resources. Baseline: establish reference metrics."},
            {"topic": "Locust", "difficulty": "Medium", "question": "How does Locust work and what are its key concepts?",
             "keywords": ["user", "task", "wait time", "HttpUser", "distributed", "Python", "swarm"],
             "model_answer": "Locust defines User classes with tasks. Users have wait_time between tasks. Written in Python. Web UI shows real-time stats. Supports distributed testing via master/worker mode."},
            {"topic": "JMeter", "difficulty": "Easy", "question": "What are the core components of a JMeter test plan?",
             "keywords": ["thread group", "sampler", "listener", "assertion", "timer", "config"],
             "model_answer": "Thread Groups (virtual users), Samplers (send requests), Listeners (collect results), Assertions (validate responses), Timers (add delays), Config elements (set defaults), Logic Controllers (flow control)."},
            {"topic": "Metrics", "difficulty": "Medium", "question": "What are key performance metrics to monitor?",
             "keywords": ["response time", "throughput", "error rate", "percentile", "p95", "p99", "concurrent"],
             "model_answer": "Response time (avg, p50, p95, p99), throughput (RPS), error rate, concurrent users, CPU/memory utilization, network bandwidth, database query time. Focus on percentiles over averages."},
            {"topic": "Analysis", "difficulty": "Hard", "question": "How do you identify and resolve performance bottlenecks?",
             "keywords": ["profiling", "database", "CPU", "memory", "network", "APM", "bottleneck", "GC"],
             "model_answer": "Use APM tools for end-to-end tracing. Profile CPU, memory (heap dumps), database (slow query logs, EXPLAIN), network. Monitor resource utilization during load. Common bottlenecks: missing indexes, N+1 queries, memory leaks, connection pool exhaustion, GC pressure."},
        ]
    },
}

# ─── Interest Area to Role Mapping ───
INTEREST_TO_ROLE = {
    "Playwright": "sdet",
    "API Testing": "sdet",
    "Performance Testing": "performance_testing",
    "Security Testing": "security_testing",
    "DevOps": "devops",
    "Cloud Computing": "cloud",
    "Frontend Development": "frontend",
    "Backend Development": "python_developer",
    "Mobile Testing": "mobile_testing",
    "Data Engineering": "data_engineering",
    "Machine Learning": "machine_learning",
    "System Design": "system_design",
}


def get_role_for_interests(interest_areas):
    """Map user's interest areas to the best matching role key."""
    if not interest_areas:
        return "default"

    # Count role votes from interests
    role_votes = {}
    for interest in interest_areas:
        role_key = INTEREST_TO_ROLE.get(interest, "default")
        role_votes[role_key] = role_votes.get(role_key, 0) + 1

    # Return the most voted role
    return max(role_votes, key=role_votes.get)


def get_questions_for_role(job_title):
    """Generate 30 questions based on role: 1 intro + 20 technical + 5 HR + 4 more technical."""
    job_lower = job_title.lower()

    # Match role
    if any(k in job_lower for k in ["sdet", "qa", "test", "quality", "automation"]):
        role_key = "sdet"
    elif any(k in job_lower for k in ["devops", "sre", "infrastructure", "platform", "cloud engineer"]):
        role_key = "devops"
    elif any(k in job_lower for k in ["security", "pentest", "appsec", "infosec"]):
        role_key = "security_testing"
    elif any(k in job_lower for k in ["cloud", "aws", "azure", "gcp"]):
        role_key = "cloud"
    elif any(k in job_lower for k in ["data engineer", "etl", "pipeline", "data"]):
        role_key = "data_engineering"
    elif any(k in job_lower for k in ["machine learning", "ml", "ai", "deep learning"]):
        role_key = "machine_learning"
    elif any(k in job_lower for k in ["system design", "architect", "principal"]):
        role_key = "system_design"
    elif any(k in job_lower for k in ["mobile", "appium", "ios", "android"]):
        role_key = "mobile_testing"
    elif any(k in job_lower for k in ["performance", "load test", "jmeter", "locust"]):
        role_key = "performance_testing"
    elif any(k in job_lower for k in ["python", "backend", "django", "flask", "fastapi"]):
        role_key = "python_developer"
    elif any(k in job_lower for k in ["frontend", "react", "angular", "vue", "ui developer", "web developer", "javascript"]):
        role_key = "frontend"
    else:
        role_key = "default"

    role = ROLE_QUESTIONS[role_key]
    technical = role["topics"]

    # Build 30 questions:
    # Q1: Self Introduction (from HR)
    # Q2-Q21: Technical (20 questions, Easy → Hard)
    # Q22-Q26: HR questions
    # Q27-Q30: More technical (hard)
    questions = []
    qid = 1

    # 1. Self Intro
    intro = HR_QUESTIONS[0].copy()
    intro["id"] = qid
    intro["max_score"] = 100
    questions.append(intro)
    qid += 1

    # Sort technical by difficulty
    easy = [q for q in technical if q["difficulty"] == "Easy"]
    medium = [q for q in technical if q["difficulty"] == "Medium"]
    hard = [q for q in technical if q["difficulty"] == "Hard"]

    # 2-11: Easy + Medium technical
    for q in easy[:5]:
        entry = q.copy()
        entry["id"] = qid
        entry["max_score"] = 100
        questions.append(entry)
        qid += 1

    for q in medium[:5]:
        entry = q.copy()
        entry["id"] = qid
        entry["max_score"] = 100
        questions.append(entry)
        qid += 1

    # 12-16: More Medium + Hard technical
    for q in medium[5:8]:
        entry = q.copy()
        entry["id"] = qid
        entry["max_score"] = 100
        questions.append(entry)
        qid += 1

    for q in hard[:2]:
        entry = q.copy()
        entry["id"] = qid
        entry["max_score"] = 100
        questions.append(entry)
        qid += 1

    # 17-21: Remaining technical
    remaining = medium[8:] + hard[2:] + easy[5:]
    for q in remaining[:5]:
        entry = q.copy()
        entry["id"] = qid
        entry["max_score"] = 100
        questions.append(entry)
        qid += 1

    # 22-26: HR Questions (skip intro, already used)
    for q in HR_QUESTIONS[1:6]:
        entry = q.copy()
        entry["id"] = qid
        entry["max_score"] = 100
        questions.append(entry)
        qid += 1

    # 27-30: More HR + remaining technical
    for q in HR_QUESTIONS[6:10]:
        entry = q.copy()
        entry["id"] = qid
        entry["max_score"] = 100
        questions.append(entry)
        qid += 1

    # Ensure exactly 30
    while len(questions) < 30:
        entry = HR_QUESTIONS[-1].copy()
        entry["id"] = qid
        entry["max_score"] = 100
        questions.append(entry)
        qid += 1

    return questions[:30], role["name"]