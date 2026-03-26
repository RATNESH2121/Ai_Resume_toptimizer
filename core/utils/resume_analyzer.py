"""
Resume & JD Section Parser.
Extracts structured data from raw resume and JD text.
"""

import re


# ─── TECH SKILLS TAXONOMY ─────────────────────────────────────────────────────
# 400+ skills organized into categories for accurate matching
SKILLS_TAXONOMY = {
    "languages": {
        "python", "java", "javascript", "js", "typescript", "ts", "c", "c++", "c#",
        "csharp", "golang", "go", "rust", "ruby", "php", "swift", "kotlin", "r",
        "scala", "perl", "matlab", "dart", "elixir", "haskell", "lua", "bash",
        "shell", "powershell", "groovy", "clojure", "f#", "ocaml", "vba", "cobol",
        "fortran", "assembly", "solidity", "move",
    },
    "frontend": {
        "react", "reactjs", "react.js", "angular", "angularjs", "vue", "vuejs",
        "vue.js", "nextjs", "next.js", "nuxtjs", "svelte", "html", "html5", "css",
        "css3", "sass", "scss", "less", "tailwind", "bootstrap", "material-ui",
        "mui", "antd", "chakra", "jquery", "redux", "zustand", "mobx", "webpack",
        "vite", "parcel", "babel", "eslint", "prettier", "storybook", "figma",
        "webgl", "three.js", "d3", "d3.js",
    },
    "backend": {
        "nodejs", "node.js", "node", "express", "expressjs", "django", "flask",
        "fastapi", "spring", "springboot", "spring boot", "laravel", "rails",
        "ruby on rails", "asp.net", "dotnet", ".net", "nestjs", "nest.js",
        "graphql", "rest", "restful", "grpc", "websocket", "soap", "microservices",
        "serverless", "lambda", "gin", "fiber", "actix", "rocket", "phoenix",
        "celery", "rabbitmq", "kafka", "redis", "nginx", "apache", "gunicorn",
    },
    "databases": {
        "sql", "mysql", "postgresql", "postgres", "sqlite", "mongodb", "mongo",
        "redis", "elasticsearch", "cassandra", "dynamodb", "firebase", "firestore",
        "supabase", "oracle", "mssql", "sql server", "mariadb", "cockroachdb",
        "neo4j", "influxdb", "prometheus", "pinecone", "chroma", "qdrant",
        "bigquery", "snowflake", "redshift", "hive", "spark sql",
    },
    "devops_cloud": {
        "docker", "kubernetes", "k8s", "aws", "amazon web services", "gcp",
        "google cloud", "azure", "heroku", "vercel", "netlify", "digitalocean",
        "ci/cd", "jenkins", "github actions", "gitlab ci", "circleci", "travis",
        "terraform", "ansible", "chef", "puppet", "vagrant", "helm", "istio",
        "linux", "ubuntu", "centos", "bash scripting", "prometheus", "grafana",
        "elk", "datadog", "new relic", "cloudwatch", "s3", "ec2", "rds",
        "lambda", "cloudfront", "load balancer", "vpc",
    },
    "ai_ml": {
        "machine learning", "ml", "deep learning", "dl", "artificial intelligence",
        "ai", "neural networks", "nlp", "natural language processing", "computer vision",
        "cv", "tensorflow", "pytorch", "keras", "scikit-learn", "sklearn", "pandas",
        "numpy", "matplotlib", "seaborn", "hugging face", "transformers", "bert",
        "gpt", "llm", "langchain", "rag", "vector database", "openai", "gemini",
        "reinforcement learning", "object detection", "yolo", "cnn", "rnn", "lstm",
        "attention", "fine-tuning", "prompt engineering", "mlops", "mlflow",
        "kubeflow", "sagemaker", "vertex ai", "opencv", "scipy", "xgboost",
    },
    "mobile": {
        "android", "ios", "react native", "flutter", "dart", "swift", "kotlin",
        "xamarin", "ionic", "cordova", "expo", "firebase", "xcode", "android studio",
    },
    "tools_practices": {
        "git", "github", "gitlab", "bitbucket", "jira", "confluence", "trello",
        "agile", "scrum", "kanban", "devops", "tdd", "bdd", "unit testing",
        "integration testing", "selenium", "cypress", "jest", "pytest", "junit",
        "postman", "swagger", "openapi", "figma", "adobe xd", "linux", "unix",
        "ssh", "vim", "vscode", "intellij", "eclipse",
    },
    "data_engineering": {
        "apache spark", "spark", "hadoop", "kafka", "airflow", "dbt", "etl",
        "data pipeline", "data warehouse", "data lake", "snowflake", "bigquery",
        "tableau", "power bi", "looker", "metabase", "pandas", "pyspark", "flink",
    },
    "security": {
        "cybersecurity", "penetration testing", "pentest", "owasp", "sso",
        "oauth", "jwt", "ldap", "ssl", "tls", "encryption", "firewall", "vpn",
        "iam", "rbac", "zero trust", "siem",
    },
    "blockchain": {
        "blockchain", "ethereum", "solidity", "web3", "nft", "defi", "smart contracts",
        "hyperledger", "truffle", "hardhat",
    },
}


def extract_all_skills(text):
    """Extract all skills from text using taxonomy."""
    text_lower = text.lower()
    found = {}
    for category, skills in SKILLS_TAXONOMY.items():
        matched = []
        for skill in skills:
            # Use word boundary matching
            pattern = r'(?<![a-zA-Z0-9\-\.])' + re.escape(skill) + r'(?![a-zA-Z0-9\-\.])'
            if re.search(pattern, text_lower):
                matched.append(skill)
        if matched:
            found[category] = matched
    return found


def get_flat_skills(text):
    """Return flat set of all skills found in text.""" 
    all_cats = extract_all_skills(text)
    flat = set()
    for skills in all_cats.values():
        flat.update(skills)
    return flat


# ─── RESUME SECTION PARSER ────────────────────────────────────────────────────

SECTION_PATTERNS = {
    "summary": re.compile(
        r'(summary|objective|profile|about me|career objective|professional summary)',
        re.I
    ),
    "skills": re.compile(
        r'(skills|technical skills|core competencies|technologies|tech stack|competencies)',
        re.I
    ),
    "experience": re.compile(
        r'(experience|work experience|employment|work history|professional experience|internship)',
        re.I
    ),
    "projects": re.compile(
        r'(projects?|personal projects?|academic projects?|key projects?)',
        re.I
    ),
    "education": re.compile(
        r'(education|academic|qualifications?|degree)',
        re.I
    ),
    "certifications": re.compile(
        r'(certifications?|certificates?|courses?|training|licenses?)',
        re.I
    ),
    "achievements": re.compile(
        r'(achievements?|awards?|honors?|accomplishments?)',
        re.I
    ),
}


def parse_resume_sections(text):
    """Parse resume into named sections."""
    lines = text.split('\n')
    sections = {}
    current_section = "header"
    buffer = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            buffer.append('')
            continue

        matched_section = None
        for name, pattern in SECTION_PATTERNS.items():
            if pattern.match(stripped) or (len(stripped) < 50 and pattern.search(stripped)):
                matched_section = name
                break

        if matched_section and len(stripped) < 60:
            sections[current_section] = '\n'.join(buffer).strip()
            current_section = matched_section
            buffer = []
        else:
            buffer.append(line)

    sections[current_section] = '\n'.join(buffer).strip()

    # Clean up empty sections
    sections = {k: v for k, v in sections.items() if len(v) > 10}
    return sections


def extract_years_of_experience(text):
    """Try to extract years of total experience from resume."""
    patterns = [
        r'(\d+)\+?\s*years?\s+(?:of\s+)?(?:professional\s+)?experience',
        r'experience\s+of\s+(\d+)\+?\s*years?',
    ]
    for pat in patterns:
        match = re.search(pat, text.lower())
        if match:
            return int(match.group(1))

    # Count job entries as a proxy
    job_entries = len(re.findall(r'\b(20\d{2})\b', text))
    if job_entries >= 6:
        return 3
    elif job_entries >= 4:
        return 2
    elif job_entries >= 2:
        return 1
    return 0


def has_quantified_achievements(text):
    """Check if resume has numerical/quantified bullet points."""
    patterns = [
        r'\d+%',           # percentages
        r'\d+x\b',         # multiples
        r'\$[\d,]+',       # dollar amounts
        r'\d[\d,]+\s*(users|customers|requests|records|lines)',  # scale
        r'(?:reduced|improved|increased|decreased|optimized)\s+by\s+\d+',
    ]
    count = 0
    for pat in patterns:
        count += len(re.findall(pat, text.lower()))
    return count


ACTION_VERBS = {
    'built', 'developed', 'designed', 'implemented', 'created', 'led', 'managed',
    'optimized', 'improved', 'reduced', 'increased', 'automated', 'deployed',
    'integrated', 'architected', 'engineered', 'launched', 'shipped', 'delivered',
    'collaborated', 'mentored', 'analyzed', 'researched', 'spearheaded', 'drove',
}


def count_action_verbs(text):
    """Count strong action verbs in resume."""
    words = set(re.findall(r'\b[a-z]+ed\b|\b[a-z]+\b', text.lower()))
    return len(words & ACTION_VERBS)


# ─── JD PARSER ────────────────────────────────────────────────────────────────

EXPERIENCE_LEVEL_PATTERNS = {
    "junior": re.compile(r'\b(junior|entry.level|fresher|0-2|1-2|0-1|recent graduate)\b', re.I),
    "mid": re.compile(r'\b(mid.level|2-4|2-5|3-5|intermediate|mid\s+senior)\b', re.I),
    "senior": re.compile(r'\b(senior|5\+|6\+|7\+|lead|principal|staff|sr\.?)\b', re.I),
}

ROLE_KEYWORDS = {
    "Full Stack Developer": ["full stack", "fullstack", "full-stack", "mern", "mean", "lamp"],
    "Frontend Developer": ["frontend", "front-end", "ui developer", "react developer", "angular developer"],
    "Backend Developer": ["backend", "back-end", "server-side", "api developer"],
    "DevOps Engineer": ["devops", "sre", "site reliability", "platform engineer", "infrastructure"],
    "Data Scientist": ["data scientist", "machine learning engineer", "ml engineer", "data science"],
    "Data Engineer": ["data engineer", "etl", "data pipeline", "data warehouse"],
    "AI/ML Engineer": ["ai engineer", "ml engineer", "nlp engineer", "deep learning"],
    "Android Developer": ["android developer", "android engineer"],
    "iOS Developer": ["ios developer", "swift developer"],
    "Mobile Developer": ["mobile developer", "react native", "flutter developer"],
    "Cloud Engineer": ["cloud engineer", "aws engineer", "azure engineer", "gcp"],
    "QA Engineer": ["qa engineer", "quality assurance", "test engineer", "sdet"],
    "Security Engineer": ["security engineer", "cybersecurity", "penetration tester"],
    "Blockchain Developer": ["blockchain developer", "solidity developer", "web3"],
}


def detect_role(jd_text):
    """Detect job role from JD."""
    jd_lower = jd_text.lower()
    for role, keywords in ROLE_KEYWORDS.items():
        for kw in keywords:
            if kw in jd_lower:
                return role
    return "Software Developer"


def detect_experience_level(jd_text):
    """Detect experience level expected from JD."""
    for level, pattern in EXPERIENCE_LEVEL_PATTERNS.items():
        if pattern.search(jd_text):
            return level
    return "mid"


def extract_jd_requirements(jd_text):
    """
    Extract structured requirements from JD.
    Returns: {required_skills, preferred_skills, experience_level, role, responsibilities}
    """
    jd_skills = get_flat_skills(jd_text)
    jd_section_skills = extract_all_skills(jd_text)

    # Split required vs preferred
    required_section = re.split(r'(?i)preferred|nice.to.have|good.to.have|bonus|plus', jd_text)[0]
    preferred_section = jd_text[len(required_section):]

    required_skills = get_flat_skills(required_section)
    preferred_skills = get_flat_skills(preferred_section) - required_skills

    return {
        "role": detect_role(jd_text),
        "experience_level": detect_experience_level(jd_text),
        "required_skills": required_skills,
        "preferred_skills": preferred_skills,
        "all_skills": jd_skills,
        "skills_by_category": jd_section_skills,
    }


# ─── ADVANCED SCORING ENGINE ──────────────────────────────────────────────────

def compute_advanced_score(jd_text, resume_text):
    """
    Multi-dimensional scoring beyond simple keyword overlap.
    Returns detailed score with breakdown and specific gaps.
    """
    jd_reqs = extract_jd_requirements(jd_text)
    resume_sections = parse_resume_sections(resume_text)
    resume_skills = get_flat_skills(resume_text)
    resume_category_skills = extract_all_skills(resume_text)

    required_skills = jd_reqs["required_skills"]
    preferred_skills = jd_reqs["preferred_skills"]
    all_jd_skills = jd_reqs["all_skills"]

    # ── Skills Scoring (40 pts) ──────────────────────────────────────────── #
    if required_skills:
        required_matched = required_skills & resume_skills
        required_coverage = len(required_matched) / len(required_skills)
    else:
        required_matched = all_jd_skills & resume_skills
        required_coverage = len(required_matched) / max(len(all_jd_skills), 1)

    if preferred_skills:
        preferred_matched = preferred_skills & resume_skills
        preferred_coverage = len(preferred_matched) / len(preferred_skills)
    else:
        preferred_coverage = 0

    skills_score = min(int(required_coverage * 32 + preferred_coverage * 8), 40)

    # ── Experience Scoring (30 pts) ──────────────────────────────────────── #
    exp_score = 0
    has_experience_section = 'experience' in resume_sections or 'header' in resume_sections
    exp_text = resume_sections.get('experience', '') + resume_sections.get('header', '')

    # Check quantified achievements
    quant_count = has_quantified_achievements(resume_text)
    # Check action verbs
    action_count = count_action_verbs(resume_text)
    # Check years of experience
    years = extract_years_of_experience(resume_text)

    if has_experience_section:
        exp_score += 10  # has experience section
    exp_score += min(quant_count * 3, 10)  # up to 10 pts for quantified impact
    exp_score += min(action_count * 1, 5)   # up to 5 pts for action verbs
    exp_score += min(years * 2, 5)          # up to 5 pts for years
    exp_score = min(exp_score, 30)

    # ── ATS Keywords Scoring (20 pts) ────────────────────────────────────── #
    # Check category-by-category coverage
    jd_categories = jd_reqs["skills_by_category"]
    resume_categories = resume_category_skills

    category_scores = {}
    for cat, jd_cat_skills in jd_categories.items():
        resume_cat_skills = set(resume_categories.get(cat, []))
        jd_cat_set = set(jd_cat_skills)
        if jd_cat_set:
            coverage = len(jd_cat_set & resume_cat_skills) / len(jd_cat_set)
            category_scores[cat] = coverage

    avg_category_coverage = sum(category_scores.values()) / max(len(category_scores), 1)
    kw_score = min(int(avg_category_coverage * 20), 20)

    # ── Structure/Format Scoring (10 pts) ────────────────────────────────── #
    structure_score = 0
    has_summary = 'summary' in resume_sections
    has_skills = 'skills' in resume_sections
    has_projects = 'projects' in resume_sections
    has_education = 'education' in resume_sections

    if has_summary: structure_score += 3
    if has_skills: structure_score += 2
    if has_projects: structure_score += 2
    if has_education: structure_score += 2
    if quant_count > 0: structure_score += 1

    structure_score = min(structure_score, 10)

    # ── Total ATS Score ───────────────────────────────────────────────────── #
    total = skills_score + exp_score + kw_score + structure_score
    ats_score = round(total / 10, 1)

    # ── Compute Missing Skills (specific, not generic) ────────────────────── #
    missing_required = sorted(required_skills - resume_skills)
    missing_preferred = sorted(preferred_skills - resume_skills)
    missing_by_category = {}
    for cat, jd_cat_skills in jd_categories.items():
        resume_cat_skills = set(resume_categories.get(cat, []))
        missing = sorted(set(jd_cat_skills) - resume_cat_skills)
        if missing:
            missing_by_category[cat] = missing

    # ── Section Analysis ──────────────────────────────────────────────────── #
    section_analysis = {
        "has_summary": has_summary,
        "has_skills_section": has_skills,
        "has_experience": has_experience_section,
        "has_projects": has_projects,
        "has_education": has_education,
        "has_certifications": 'certifications' in resume_sections,
        "quantified_achievements_count": quant_count,
        "action_verbs_count": action_count,
        "years_of_experience": years,
    }

    match_percent = min(int((skills_score / 40) * 60 + (kw_score / 20) * 40), 100)

    return {
        "ats_score": ats_score,
        "match_percent": match_percent,
        "breakdown": {
            "skills_match": skills_score,
            "experience_relevance": exp_score,
            "keywords_ats": kw_score,
            "structure_format": structure_score,
        },
        "role_detected": jd_reqs["role"],
        "experience_level": jd_reqs["experience_level"],
        "required_skills_matched": sorted(required_matched) if required_skills else [],
        "required_skills_missing": missing_required[:15],
        "preferred_skills_missing": missing_preferred[:8],
        "missing_by_category": missing_by_category,
        "resume_skills_found": sorted(list(resume_skills))[:25],
        "section_analysis": section_analysis,
        "resume_sections": list(resume_sections.keys()),
        "category_scores": category_scores,
    }
