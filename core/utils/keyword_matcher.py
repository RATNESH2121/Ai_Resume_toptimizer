"""
ATS Keyword Matching Utility.
Uses simple TF-IDF-like keyword extraction and overlap scoring.
"""

import re
from collections import Counter


# Common English stop words to filter out
STOP_WORDS = {
    'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
    'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
    'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
    'would', 'could', 'should', 'may', 'might', 'shall', 'can', 'need',
    'that', 'this', 'these', 'those', 'it', 'its', 'we', 'our', 'you',
    'your', 'they', 'their', 'he', 'she', 'him', 'her', 'i', 'my', 'me',
    'not', 'no', 'nor', 'so', 'yet', 'both', 'either', 'neither',
    'each', 'few', 'more', 'most', 'other', 'some', 'such',
    'than', 'then', 'when', 'where', 'which', 'who', 'whom', 'how', 'what',
    'all', 'any', 'both', 'about', 'above', 'after', 'before', 'between',
    'into', 'through', 'during', 'including', 'until', 'while', 'although',
    'because', 'since', 'unless', 'however', 'therefore', 'etc', 'via',
    'must', 'also', 'well', 'work', 'role', 'team', 'using', 'use', 'used',
    'strong', 'good', 'great', 'able', 'make', 'help', 'new', 'year', 'years',
    'experience', 'knowledge', 'skills', 'ability', 'understanding', 'required',
    'looking', 'seeking', 'candidate', 'position', 'join', 'company',
}

# Tech keywords that MUST NOT be filtered
TECH_KEYWORDS = {
    'python', 'java', 'javascript', 'js', 'typescript', 'ts', 'react', 'angular',
    'vue', 'nodejs', 'node', 'django', 'flask', 'fastapi', 'spring', 'express',
    'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch',
    'docker', 'kubernetes', 'aws', 'gcp', 'azure', 'git', 'ci/cd', 'jenkins',
    'linux', 'rest', 'api', 'html', 'css', 'sass', 'graphql', 'kafka',
    'tensorflow', 'pytorch', 'scikit', 'pandas', 'numpy', 'ml', 'ai', 'llm',
    'c++', 'c#', 'golang', 'go', 'rust', 'swift', 'kotlin', 'ruby', 'php',
    'microservices', 'agile', 'scrum', 'devops', 'backend', 'frontend',
    'fullstack', 'full-stack', 'mobile', 'android', 'ios', 'flutter', 'react-native',
    'firebase', 'supabase', 'vercel', 'heroku', 'nginx', 'apache',
    'oauth', 'jwt', 'rest', 'grpc', 'websocket', 'dsa', 'algorithms',
}


def clean_and_tokenize(text):
    """Clean text and extract meaningful tokens."""
    text = text.lower()
    # Keep alphanumeric, spaces, hyphens, slashes for things like ci/cd
    text = re.sub(r'[^\w\s\-\/\+#]', ' ', text)
    tokens = text.split()
    return tokens


def extract_keywords(text, top_n=50):
    """
    Extract top keywords from text.
    Tech keywords always included if found.
    """
    tokens = clean_and_tokenize(text)

    # Collect all words
    all_words = []
    for token in tokens:
        token = token.strip('-').strip('/')
        if len(token) > 1:
            all_words.append(token)

    # Count frequencies
    freq = Counter(all_words)

    # Build keyword set:
    # 1. Always include tech keywords found in text
    keywords = set()
    for word in all_words:
        if word in TECH_KEYWORDS:
            keywords.add(word)

    # 2. Add top frequent non-stop words
    for word, count in freq.most_common(top_n + 50):
        if word not in STOP_WORDS and len(word) > 2 and len(keywords) < top_n:
            keywords.add(word)

    return keywords


def compute_keyword_match(jd_text, resume_text):
    """
    Compare JD keywords vs Resume keywords.
    Returns dict with match percent, matched, missing keywords.
    """
    jd_keywords = extract_keywords(jd_text, top_n=60)
    resume_keywords = extract_keywords(resume_text, top_n=80)

    # Filter JD keywords to meaningful ones (exclude very generic)
    jd_important = {kw for kw in jd_keywords if len(kw) > 2}

    matched = jd_important & resume_keywords
    missing = jd_important - resume_keywords

    if not jd_important:
        match_percent = 50
    else:
        match_percent = int((len(matched) / len(jd_important)) * 100)
        match_percent = min(match_percent, 100)

    # Prioritize tech keywords in missing list
    missing_tech = sorted([kw for kw in missing if kw in TECH_KEYWORDS])
    missing_other = sorted([kw for kw in missing if kw not in TECH_KEYWORDS])
    missing_sorted = missing_tech + missing_other

    return {
        "match_percent": match_percent,
        "matched_keywords": sorted(list(matched))[:20],
        "missing_keywords": missing_sorted[:15],
        "jd_keyword_count": len(jd_important),
        "resume_keyword_count": len(resume_keywords),
    }
