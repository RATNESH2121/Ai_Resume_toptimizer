"""
AI Scoring Engine using Hugging Face Inference API.
Uses Mistral-7B-Instruct — one of the best free open-source LLMs.
Falls back to local keyword-only scoring if API call fails.
"""

import json
import re
import os
import requests
from .keyword_matcher import compute_keyword_match

HF_API_TOKEN = os.getenv('HF_API_TOKEN', '')

# Best free models on HF Inference API (ordered by preference)
HF_MODELS = [
    "mistralai/Mistral-7B-Instruct-v0.3",
    "HuggingFaceH4/zephyr-7b-beta",
    "mistralai/Mixtral-8x7B-Instruct-v0.1",
]

HF_API_URL = "https://api-inference.huggingface.co/models/{model}"


def _build_prompt(jd_text, resume_text):
    """Build clean instruction prompt for Mistral/Zephyr."""
    return f"""<s>[INST] You are an expert ATS resume analyzer and career coach.

Analyze the following Job Description and Resume, then return a JSON object ONLY. No explanation, no markdown, no code blocks — just raw JSON.

JOB DESCRIPTION:
{jd_text[:2500]}

CANDIDATE RESUME:
{resume_text[:2500]}

Return this exact JSON structure:
{{
  "ats_score": 6.5,
  "match_percent": 65,
  "breakdown": {{
    "skills_match": 25,
    "experience_relevance": 20,
    "keywords_ats": 13,
    "structure_format": 7
  }},
  "role_detected": "Full Stack Developer",
  "missing_keywords": ["Docker", "AWS", "CI/CD"],
  "strengths": [
    "Strong Python experience matching JD",
    "Relevant project experience in web development"
  ],
  "feedback": [
    "Add Docker and AWS to skills — both required in JD",
    "Rewrite bullet points with action verbs (Built, Developed, Optimized)",
    "Add a 3-4 line professional summary targeting this role",
    "Quantify impact — e.g. 'Reduced load time by 40%' not just 'Improved performance'"
  ],
  "optimized_resume": {{
    "name": "Candidate Name",
    "contact": "email@example.com | +91-XXXXXXXXXX | LinkedIn | GitHub",
    "summary": "Tailored 3-4 line professional summary for this specific JD and role",
    "skills": {{
      "languages": ["Python", "JavaScript"],
      "frameworks": ["React", "Django", "Node.js"],
      "tools": ["Docker", "Git", "AWS"],
      "databases": ["MySQL", "MongoDB"]
    }},
    "experience": [
      {{
        "title": "Software Developer",
        "company": "Company Name",
        "duration": "Jun 2023 - Present",
        "bullets": [
          "Built RESTful APIs with Django reducing response time by 30%",
          "Developed React frontend increasing user engagement by 25%"
        ]
      }}
    ],
    "projects": [
      {{
        "name": "Project Name",
        "tech": "Python, React, MySQL",
        "bullets": [
          "Developed full-stack app handling 1000+ concurrent users",
          "Implemented JWT authentication and role-based access"
        ]
      }}
    ],
    "education": "B.Tech Computer Science | University Name | 2026"
  }},
  "optimized_score": 8.5
}}

Rules:
- Keep candidate's REAL experience — only rephrase, never invent jobs
- Score breakdown totals: skills=40 max, experience=30 max, keywords=20 max, structure=10 max
- ats_score must be out of 10 with one decimal
- missing_keywords from JD that are absent in resume
- Return ONLY valid JSON [/INST]"""


def _call_hf_api(prompt, model):
    """Call HuggingFace Inference API for a given model."""
    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 1800,
            "temperature": 0.2,
            "return_full_text": False,
            "do_sample": True,
        },
    }
    url = HF_API_URL.format(model=model)
    resp = requests.post(url, headers=headers, json=payload, timeout=90)
    resp.raise_for_status()
    data = resp.json()

    # HF returns list of generated texts
    if isinstance(data, list) and data:
        return data[0].get("generated_text", "")
    return ""


def _extract_json(raw_text):
    """
    Try multiple strategies to extract valid JSON from model output.
    """
    # Strategy 1: Find JSON between first { and last }
    start = raw_text.find('{')
    end = raw_text.rfind('}')
    if start != -1 and end != -1 and end > start:
        candidate = raw_text[start:end+1]
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass

    # Strategy 2: Strip markdown code blocks
    cleaned = re.sub(r'```json\s*', '', raw_text)
    cleaned = re.sub(r'```\s*', '', cleaned)
    cleaned = cleaned.strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    return None


def analyze_resume(jd_text, resume_text):
    """
    Main function: Analyze JD + Resume via HuggingFace.
    Tries Mistral-7B-Instruct first, then fallbacks.
    """
    # Always run fast local keyword match
    keyword_data = compute_keyword_match(jd_text, resume_text)

    if not HF_API_TOKEN or HF_API_TOKEN == 'your_hf_token_here':
        return _fallback_analysis(jd_text, resume_text, keyword_data)

    prompt = _build_prompt(jd_text, resume_text)
    last_error = None

    for model in HF_MODELS:
        try:
            raw_text = _call_hf_api(prompt, model)
            if not raw_text:
                continue

            data = _extract_json(raw_text)
            if data:
                # Merge with local keyword data
                data['keyword_analysis'] = keyword_data

                # Set defaults for missing fields
                data.setdefault('ats_score', 5.0)
                data.setdefault('match_percent', keyword_data.get('match_percent', 50))
                data.setdefault('role_detected', 'Not detected')
                data.setdefault('missing_keywords', keyword_data.get('missing_keywords', []))
                data.setdefault('strengths', [])
                data.setdefault('feedback', ['Review your resume manually for improvements.'])
                data.setdefault('optimized_score', min(float(data['ats_score']) + 2.0, 10.0))
                data.setdefault('optimized_resume', None)

                return data

        except requests.exceptions.HTTPError as e:
            # 503 = model loading, try next
            last_error = str(e)
            continue
        except Exception as e:
            last_error = str(e)
            continue

    # All models failed — return local keyword-based analysis
    print(f"[ai_scorer] All HF models failed ({last_error}), using fallback.")
    return _fallback_analysis(jd_text, resume_text, keyword_data)


def _fallback_analysis(jd_text, resume_text, keyword_data):
    """Keyword-based fallback analysis when AI API is unavailable."""
    match_percent = keyword_data.get('match_percent', 50)
    ats_score = round(match_percent / 10, 1)
    missing = keyword_data.get('missing_keywords', [])

    feedback = [
        f"Add these missing keywords from JD: {', '.join(missing[:6])}" if missing
        else "Your resume covers most JD keywords well.",
        "Add a professional summary (3-4 lines) at the top of your resume",
        "Use strong action verbs: Built, Developed, Optimized, Reduced, Led",
        "Quantify achievements — e.g. 'Improved performance by 30%'",
        "Tailor your Skills section to match the JD tool requirements",
    ]

    return {
        "ats_score": ats_score,
        "match_percent": match_percent,
        "breakdown": {
            "skills_match": int(40 * match_percent / 100),
            "experience_relevance": int(30 * match_percent / 100),
            "keywords_ats": int(20 * match_percent / 100),
            "structure_format": int(10 * match_percent / 100),
        },
        "role_detected": "Not detected (AI offline)",
        "missing_keywords": missing,
        "strengths": [
            f"Resume contains {len(keyword_data.get('matched_keywords', []))} keywords matching the JD",
            "Resume submitted — keyword analysis complete",
        ],
        "feedback": feedback,
        "optimized_score": min(ats_score + 2.0, 10.0),
        "optimized_resume": None,
        "keyword_analysis": keyword_data,
        "_note": "AI model fallback used — keyword-based scoring only",
    }
