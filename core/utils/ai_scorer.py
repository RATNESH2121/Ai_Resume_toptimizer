"""
Advanced AI Scoring Engine — Multi-Stage Pipeline.

Stage 1: Deep structural analysis (skills taxonomy, section parsing, role detection)
Stage 2: HuggingFace LLM semantic analysis (Mistral-7B-Instruct)
Stage 3: Merge + generate precise, actionable recommendations
Stage 4: Build fully optimized resume content

This is NOT just keyword matching — it does:
- Category-by-category skills gap analysis (10 categories, 400+ skills)
- Resume section completeness check
- Experience quality analysis (quantified achievements, action verbs)
- JD requirement parsing (required vs preferred skills)
- Experience level detection
- Role-specific recommendations
- Semantic analysis via LLM for what keyword matching misses
"""

import json
import re
import os
import requests

from .resume_analyzer import (
    compute_advanced_score,
    get_flat_skills,
    extract_jd_requirements,
    parse_resume_sections,
    extract_all_skills,
    SKILLS_TAXONOMY,
)

HF_API_TOKEN = os.getenv('HF_API_TOKEN', '')

# Best HF models for structured output and reasoning
HF_MODELS = [
    "mistralai/Mistral-7B-Instruct-v0.3",
    "HuggingFaceH4/zephyr-7b-beta",
    "mistralai/Mixtral-8x7B-Instruct-v0.1",
]
HF_API_URL = "https://api-inference.huggingface.co/models/{model}"


# ═══════════════════════════════════════════════════════════════════════════════
#  MAIN ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

def analyze_resume(jd_text, resume_text):
    """
    Full multi-stage resume analysis.
    Returns comprehensive JSON with score, breakdown, recommendations, optimized resume.
    """

    # ── STAGE 1: Deep structural analysis ─────────────────────────────────── #
    local_analysis = compute_advanced_score(jd_text, resume_text)
    jd_reqs = extract_jd_requirements(jd_text)
    resume_sections = parse_resume_sections(resume_text)

    # ── STAGE 2: AI Semantic Analysis via HuggingFace ─────────────────────── #
    ai_data = None
    if HF_API_TOKEN and HF_API_TOKEN not in ('your_hf_token_here', ''):
        ai_data = _call_hf_with_retry(jd_text, resume_text, local_analysis, jd_reqs)

    # ── STAGE 3: Merge AI + local analysis ────────────────────────────────── #
    result = _merge_analysis(local_analysis, ai_data, jd_reqs, resume_sections, resume_text)

    return result


# ═══════════════════════════════════════════════════════════════════════════════
#  HUGGINGFACE API CALLS
# ═══════════════════════════════════════════════════════════════════════════════

def _build_deep_prompt(jd_text, resume_text, local_analysis, jd_reqs):
    """
    Build a structured, two-part prompt that gives the LLM rich context
    from our local analysis so it can do SEMANTIC analysis, not just repeat
    keyword matching.
    """
    missing_required = local_analysis.get("required_skills_missing", [])
    missing_preferred = local_analysis.get("preferred_skills_missing", [])
    section_info = local_analysis.get("section_analysis", {})
    role = local_analysis.get("role_detected", "Software Developer")
    exp_level = local_analysis.get("experience_level", "mid")
    local_score = local_analysis.get("ats_score", 5.0)

    return f"""<s>[INST] You are a senior technical recruiter and resume coach with 15+ years of experience.

## Context (from automated analysis):
- Detected Role: {role}
- Experience Level Expected: {exp_level}
- Local ATS Score: {local_score}/10
- Missing Required Skills: {', '.join(missing_required[:12]) or 'None detected'}
- Missing Preferred Skills: {', '.join(missing_preferred[:8]) or 'None detected'}
- Has Summary Section: {section_info.get('has_summary', False)}
- Has Skills Section: {section_info.get('has_skills_section', False)}
- Quantified Achievements Count: {section_info.get('quantified_achievements_count', 0)}
- Action Verbs Count: {section_info.get('action_verbs_count', 0)}

## Job Description:
{jd_text[:2000]}

## Candidate's Current Resume:
{resume_text[:2000]}

## Your Task:
Do a DEEP semantic analysis. Look beyond keywords — analyze:
1. Does experience MATCH the JD responsibilities in terms of scope and level?
2. Are missing skills critical (dealbreakers) or minor gaps?
3. Is the resume positioned correctly for this role?
4. What specific rewrites will have the biggest ATS + recruiter impact?
5. Generate an OPTIMIZED resume with fully rewritten content.

Return ONLY valid JSON (no markdown, no text before or after):

{{
  "ats_score": 6.8,
  "match_percent": 68,
  "breakdown": {{
    "skills_match": 26,
    "experience_relevance": 22,
    "keywords_ats": 13,
    "structure_format": 7
  }},
  "role_detected": "{role}",
  "experience_level": "{exp_level}",
  "critical_gaps": [
    "Missing Docker/Kubernetes — required for deployment tasks in JD",
    "No CI/CD experience mentioned — listed under required qualifications"
  ],
  "strengths": [
    "Strong Python + Django stack matching 70% of backend requirements",
    "Project experience with REST APIs aligns directly with JD responsibilities"
  ],
  "specific_feedback": [
    {{
      "section": "Skills",
      "issue": "Missing Docker, AWS, CI/CD which are required in JD",
      "fix": "Add a DevOps/Tools row: Docker, AWS EC2/S3, GitHub Actions, Linux"
    }},
    {{
      "section": "Experience",
      "issue": "Bullet points are generic — 'Worked on backend APIs'",
      "fix": "Rewrite: 'Built 12 RESTful APIs in Django processing 50K+ daily requests, reducing latency by 35%'"
    }},
    {{
      "section": "Summary",
      "issue": "No professional summary targeting this specific role",
      "fix": "Add: 'Full Stack Developer with 2+ years building Django APIs and React UIs, seeking to bring production-grade experience to [Company]'"
    }},
    {{
      "section": "Projects",
      "issue": "Projects lack technical depth and measurable outcomes",
      "fix": "Add tech stack, scale, and impact: 'E-commerce platform — React + Django + PostgreSQL, 500+ products, 99.5% uptime'"
    }}
  ],
  "ats_keywords_to_add": ["Docker", "AWS", "CI/CD", "React", "PostgreSQL"],
  "optimized_resume": {{
    "name": "Candidate Name (from resume)",
    "contact": "email | phone | LinkedIn | GitHub",
    "summary": "2-3 line summary hyper-targeted to this JD and {role} role, using JD keywords naturally",
    "skills": {{
      "languages": ["Python", "JavaScript"],
      "frameworks": ["Django", "React", "Node.js"],
      "cloud_devops": ["AWS S3/EC2", "Docker", "GitHub Actions"],
      "databases": ["PostgreSQL", "MongoDB", "Redis"],
      "tools": ["Git", "Postman", "Linux", "VS Code"]
    }},
    "experience": [
      {{
        "title": "Same title as in resume",
        "company": "Same company",
        "duration": "Duration from resume",
        "bullets": [
          "REWRITTEN: Strong action verb + what + measurable result targeting {role} JD",
          "REWRITTEN: Built X using [JD technology] that achieved Y metric",
          "REWRITTEN: Third impactful bullet with technical depth"
        ]
      }}
    ],
    "projects": [
      {{
        "name": "Project name from resume",
        "tech": "Tech stack including JD-relevant tools",
        "bullets": [
          "REWRITTEN: Clear description of what was built, tech used, and impact",
          "REWRITTEN: Scale metric or outcome (users, performance, etc)"
        ]
      }}
    ],
    "education": "Same education as in resume"
  }},
  "optimized_score": 8.6,
  "optimization_highlights": [
    "Added 5 missing keywords that were required in JD",
    "Rewrote 4 experience bullets with quantified impact",
    "Added professional summary targeting {role}",
    "Restructured skills section by category for ATS parsing"
  ]
}}

CRITICAL RULES:
- NEVER invent jobs, companies, or degrees that are not in the resume
- ONLY rephrase and rewrite existing content to be stronger
- Be extremely specific — cite actual lines from JD and resume in feedback
- specific_feedback must have at least 4-5 items covering ALL weak areas
- optimized_resume must differ meaningfully from original
[/INST]"""


def _call_hf_api(prompt, model):
    """Call HuggingFace Inference API."""
    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 2500,
            "temperature": 0.15,
            "top_p": 0.9,
            "return_full_text": False,
            "do_sample": True,
        },
    }
    url = HF_API_URL.format(model=model)
    resp = requests.post(url, headers=headers, json=payload, timeout=120)
    resp.raise_for_status()
    data = resp.json()

    if isinstance(data, list) and data:
        return data[0].get("generated_text", "")
    if isinstance(data, dict):
        return data.get("generated_text", "")
    return ""


def _extract_json_from_text(raw_text):
    """Robust JSON extraction — multiple strategies."""
    if not raw_text:
        return None

    # Strategy 1: Find first { to last }
    start = raw_text.find('{')
    end = raw_text.rfind('}')
    if start != -1 and end > start:
        candidate = raw_text[start:end+1]
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass

    # Strategy 2: Strip markdown and try again
    cleaned = re.sub(r'```(?:json)?\s*', '', raw_text).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # Strategy 3: Try to fix common issues (trailing commas, etc.)
    try:
        fixed = re.sub(r',\s*}', '}', cleaned)
        fixed = re.sub(r',\s*]', ']', fixed)
        start = fixed.find('{')
        end = fixed.rfind('}')
        if start != -1 and end > start:
            return json.loads(fixed[start:end+1])
    except Exception:
        pass

    return None


def _call_hf_with_retry(jd_text, resume_text, local_analysis, jd_reqs):
    """Try all HF models until one returns valid JSON."""
    prompt = _build_deep_prompt(jd_text, resume_text, local_analysis, jd_reqs)

    for model in HF_MODELS:
        try:
            print(f"[ai_scorer] Trying model: {model}")
            raw_text = _call_hf_api(prompt, model)
            if not raw_text:
                print(f"[ai_scorer] {model}: empty response")
                continue

            data = _extract_json_from_text(raw_text)
            if data and isinstance(data, dict):
                print(f"[ai_scorer] ✅ Success with {model}")
                return data
            else:
                print(f"[ai_scorer] {model}: could not parse JSON from response")

        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if e.response else 0
            if status == 503:
                print(f"[ai_scorer] {model}: loading (503), trying next...")
            elif status == 429:
                print(f"[ai_scorer] {model}: rate limited, trying next...")
            else:
                print(f"[ai_scorer] {model}: HTTP {status}: {str(e)}")
            continue
        except requests.exceptions.Timeout:
            print(f"[ai_scorer] {model}: timeout, trying next...")
            continue
        except Exception as e:
            print(f"[ai_scorer] {model}: error: {str(e)}")
            continue

    print("[ai_scorer] All HF models failed — using local analysis only")
    return None


# ═══════════════════════════════════════════════════════════════════════════════
#  MERGE ANALYSIS — Combine local deep analysis + AI data
# ═══════════════════════════════════════════════════════════════════════════════

def _merge_analysis(local_analysis, ai_data, jd_reqs, resume_sections, resume_text):
    """
    Merge local deep analysis with AI output.
    Local analysis is always authoritative for scores.
    AI provides semantic feedback and optimized resume content.
    """
    role = local_analysis.get("role_detected", "Software Developer")
    exp_level = local_analysis.get("experience_level", "mid")
    section_info = local_analysis.get("section_analysis", {})

    if ai_data:
        # Trust local structural score more than AI score for accuracy
        local_score = local_analysis["ats_score"]
        ai_score = float(ai_data.get("ats_score", local_score))
        # Blend: 60% local (accurate) + 40% AI (semantic)
        final_score = round(local_score * 0.6 + ai_score * 0.4, 1)

        # Use AI breakdown if available, but cap with local breakdown
        local_bd = local_analysis["breakdown"]
        ai_bd = ai_data.get("breakdown", {})
        breakdown = {
            "skills_match": max(local_bd["skills_match"], ai_bd.get("skills_match", 0)),
            "experience_relevance": max(local_bd["experience_relevance"], ai_bd.get("experience_relevance", 0)),
            "keywords_ats": max(local_bd["keywords_ats"], ai_bd.get("keywords_ats", 0)),
            "structure_format": max(local_bd["structure_format"], ai_bd.get("structure_format", 0)),
        }
        # Clamp to max
        breakdown["skills_match"] = min(breakdown["skills_match"], 40)
        breakdown["experience_relevance"] = min(breakdown["experience_relevance"], 30)
        breakdown["keywords_ats"] = min(breakdown["keywords_ats"], 20)
        breakdown["structure_format"] = min(breakdown["structure_format"], 10)

        match_percent = ai_data.get("match_percent", local_analysis["match_percent"])

        # Get feedback — prefer AI's specific_feedback (richer)
        specific_feedback_raw = ai_data.get("specific_feedback", [])
        specific_feedback = []
        for item in specific_feedback_raw:
            if isinstance(item, dict):
                section = item.get("section", "")
                issue = item.get("issue", "")
                fix = item.get("fix", "")
                if issue and fix:
                    specific_feedback.append(f"[{section}] {issue} → {fix}")
            elif isinstance(item, str):
                specific_feedback.append(item)

        # Merge missing keywords: local (accurate) + AI's ats_keywords_to_add
        missing_required = local_analysis.get("required_skills_missing", [])
        ai_keywords_to_add = ai_data.get("ats_keywords_to_add", [])
        missing_keywords = _dedupe_merge(missing_required, ai_keywords_to_add, limit=15)

        strengths = ai_data.get("strengths", []) or _generate_strengths_fallback(local_analysis)
        critical_gaps = ai_data.get("critical_gaps", [])
        optimized_resume = ai_data.get("optimized_resume")
        opt_score = float(ai_data.get("optimized_score", min(final_score + 2.0, 10.0)))
        optimization_highlights = ai_data.get("optimization_highlights", [])

    else:
        # No AI — use local analysis to generate structured feedback
        final_score = local_analysis["ats_score"]
        breakdown = local_analysis["breakdown"]
        match_percent = local_analysis["match_percent"]
        specific_feedback = _generate_specific_feedback(local_analysis, resume_sections)
        missing_keywords = local_analysis.get("required_skills_missing", [])[:15]
        strengths = _generate_strengths_fallback(local_analysis)
        critical_gaps = _generate_critical_gaps(local_analysis)
        optimized_resume = _generate_fallback_resume_data(resume_sections, resume_text)
        opt_score = min(final_score + 2.0, 10.0)
        optimization_highlights = []

    return {
        "ats_score": final_score,
        "match_percent": match_percent,
        "breakdown": breakdown,
        "role_detected": role,
        "experience_level": exp_level,
        "missing_keywords": missing_keywords,
        "preferred_skills_missing": local_analysis.get("preferred_skills_missing", [])[:8],
        "missing_by_category": local_analysis.get("missing_by_category", {}),
        "resume_skills_found": local_analysis.get("resume_skills_found", []),
        "section_analysis": section_info,
        "resume_sections_parsed": local_analysis.get("resume_sections", []),
        "strengths": strengths,
        "critical_gaps": critical_gaps,
        "feedback": specific_feedback,
        "optimized_resume": optimized_resume,
        "optimized_score": round(opt_score, 1),
        "optimization_highlights": optimization_highlights,
        "keyword_analysis": {
            "match_percent": match_percent,
            "matched_keywords": local_analysis.get("required_skills_matched", []),
            "missing_keywords": missing_keywords,
        },
        "ai_powered": ai_data is not None,
        "status": "success",
    }


# ═══════════════════════════════════════════════════════════════════════════════
#  FALLBACK FEEDBACK GENERATORS — Rich, specific feedback without AI
# ═══════════════════════════════════════════════════════════════════════════════

def _generate_fallback_resume_data(resume_sections, resume_text):
    """Generate a structured resume dict from parsed sections for PDF generation when AI fails."""
    lines = [L.strip() for L in resume_text.split('\n') if L.strip()]
    name = lines[0] if lines else "Candidate"
    
    email_match = re.search(r'[\w\.-]+@[\w\.-]+', resume_text)
    email = email_match.group(0) if email_match else ""
    
    phone_match = re.search(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', resume_text)
    phone = phone_match.group(0) if phone_match else ""
    
    contact = " | ".join(filter(None, [email, phone]))
    
    def _text_to_list(text):
        if not text: return []
        return [line.strip() for line in text.split('\n') if len(line.strip()) > 5]

    return {
        "name": name,
        "contact": contact,
        "summary": resume_sections.get("summary", ""),
        "skills": resume_sections.get("skills", ""),
        "experience": _text_to_list(resume_sections.get("experience", "")),
        "projects": _text_to_list(resume_sections.get("projects", "")),
        "education": resume_sections.get("education", "")
    }


def _generate_specific_feedback(local_analysis, resume_sections):
    """Generate highly specific feedback from structural analysis."""
    feedback = []
    section_info = local_analysis.get("section_analysis", {})
    missing_required = local_analysis.get("required_skills_missing", [])
    missing_by_cat = local_analysis.get("missing_by_category", {})
    breakdown = local_analysis.get("breakdown", {})
    quant_count = section_info.get("quantified_achievements_count", 0)
    action_count = section_info.get("action_verbs_count", 0)
    role = local_analysis.get("role_detected", "this role")

    # 1. Skills gap feedback (most important)
    if missing_required:
        top_missing = missing_required[:6]
        feedback.append(
            f"[Skills] Add these {len(missing_required)} required skills from JD: "
            f"**{', '.join(top_missing)}**"
            + (f" (+{len(missing_required)-6} more)" if len(missing_required) > 6 else "")
        )

    # 2. Category-specific gaps
    for cat, missing in list(missing_by_cat.items())[:3]:
        cat_label = {
            "devops_cloud": "DevOps/Cloud", "ai_ml": "AI/ML", "backend": "Backend",
            "frontend": "Frontend", "databases": "Databases", "tools_practices": "Tools"
        }.get(cat, cat.title())
        feedback.append(
            f"[{cat_label}] Missing: **{', '.join(missing[:4])}** — "
            f"add these to your Skills section to pass ATS filters for {role}"
        )

    # 3. No summary
    if not section_info.get("has_summary"):
        feedback.append(
            f"[Summary] Missing professional summary — add 3-4 lines at the top:\n"
            f"  Example: 'Results-driven {role} with X years building Y for Z. "
            f"Skilled in [top JD skills]. Looking to bring [key strength] to [target impact].'"
        )

    # 4. Low quantification
    if quant_count < 3:
        feedback.append(
            f"[Experience] Only {quant_count} quantified achievements found — "
            f"ATS and recruiters love numbers. Convert generic bullets:\n"
            f"  ❌ 'Worked on REST APIs'\n"
            f"  ✅ 'Built 8 REST APIs in Django serving 10K+ daily requests, reducing latency by 30%'"
        )
    elif quant_count < 6:
        feedback.append(
            f"[Experience] {quant_count} quantified achievements found — good start! "
            f"Aim for 6+ — add metrics like response time, users served, uptime%, lines of code, team size"
        )

    # 5. Low action verbs
    if action_count < 5:
        feedback.append(
            "[Experience] Weak action verbs detected. Start every bullet with a strong verb:\n"
            "  Use: Built, Developed, Architected, Optimized, Reduced, Deployed, Automated, Led"
        )

    # 6. No projects section
    if not section_info.get("has_projects"):
        feedback.append(
            "[Projects] No projects section found — "
            "for tech roles this is critical! Add 2-3 projects with: name, tech stack, what you built, and impact"
        )

    # 7. Skills score low
    if breakdown.get("skills_match", 0) < 20:
        feedback.append(
            f"[Skills] Skills match is only {breakdown.get('skills_match', 0)}/40 — "
            f"this is your biggest weakness. Completely rewrite your Skills section to mirror JD language"
        )

    # 8. Experience section score low
    if breakdown.get("experience_relevance", 0) < 15:
        feedback.append(
            f"[Experience] Experience relevance is {breakdown.get('experience_relevance', 0)}/30 — "
            f"rewrite bullet points to explicitly reference JD responsibilities. "
            f"Use the same verbs and context as the JD"
        )

    # Ensure at least 4 feedback items
    if len(feedback) < 4:
        feedback.append(
            "[General] Consider adding a certifications section if you have relevant course certificates "
            "(AWS, Google Cloud, Coursera, etc.) — heavily weighted in ATS scoring"
        )

    return feedback[:8]  # Max 8 specific items


def _generate_strengths_fallback(local_analysis):
    """Generate strength statements from local analysis."""
    strengths = []
    matched = local_analysis.get("required_skills_matched", [])
    section_info = local_analysis.get("section_analysis", {})
    score = local_analysis.get("ats_score", 0)
    cat_scores = local_analysis.get("category_scores", {})

    if matched:
        strengths.append(
            f"{len(matched)} required JD skills found in resume: {', '.join(matched[:5])}"
        )
    if section_info.get("quantified_achievements_count", 0) >= 3:
        strengths.append(f"{section_info['quantified_achievements_count']} quantified achievements — strong signal for recruiters")
    if section_info.get("action_verbs_count", 0) >= 5:
        strengths.append("Good use of action verbs in experience bullets")
    if section_info.get("has_projects"):
        strengths.append("Projects section present — critical for most tech roles")
    if section_info.get("has_education"):
        strengths.append("Education section present")
    for cat, score in cat_scores.items():
        if score >= 0.7:
            strengths.append(f"Strong {cat.replace('_', ' ').title()} skills — high category coverage")

    return strengths[:5] or ["Resume submitted — full analysis complete"]


def _generate_critical_gaps(local_analysis):
    """Generate critical gap statements."""
    gaps = []
    missing = local_analysis.get("required_skills_missing", [])
    section_info = local_analysis.get("section_analysis", {})

    if missing:
        gaps.append(f"Critical: {len(missing)} required skills from JD not found: {', '.join(missing[:5])}")
    if not section_info.get("has_summary"):
        gaps.append("Missing professional summary — first thing ATS and recruiters check")
    if section_info.get("quantified_achievements_count", 0) == 0:
        gaps.append("No quantified achievements — generic bullets don't pass ATS ranking")
    if not section_info.get("has_skills_section"):
        gaps.append("No dedicated Skills section — critical for ATS keyword extraction")

    return gaps[:4]


def _dedupe_merge(list1, list2, limit=15):
    """Merge two lists, deduplicate, preserve order."""
    seen = set()
    result = []
    for item in (list1 + list2):
        key = item.lower().strip()
        if key not in seen and item:
            seen.add(key)
            result.append(item)
    return result[:limit]
