# core/analysis.py

import re
from typing import List, Dict
from collections import Counter

from core.constants import COMMON_WORDS, IMPACT_VERBS, QUANT_PATTERNS


# ---------------------------------------------------------
# KEYWORD EXTRACTION
# ---------------------------------------------------------
def extract_keywords(text: str, min_length: int = 4) -> List[str]:
    """Extract meaningful keywords from text."""
    if not text:
        return []
    words = re.findall(r'\b[a-z]+\b', text.lower())
    keywords = [w for w in words if len(w) >= min_length and w not in COMMON_WORDS]
    return list(set(keywords))


# ---------------------------------------------------------
# IMPACT VERBS & METRICS
# ---------------------------------------------------------
def count_impact_verbs(text: str) -> tuple[int, List[str]]:
    """Count impact verbs in resume."""
    text_lower = text.lower()
    found = [verb for verb in IMPACT_VERBS if verb in text_lower]
    return len(found), found


def count_quantifiable_results(text: str) -> int:
    """Count quantifiable metrics in resume."""
    count = 0
    for pattern in QUANT_PATTERNS:
        count += len(re.findall(pattern, text))
    return count


# ---------------------------------------------------------
# ATS CHECK
# ---------------------------------------------------------
def check_ats_compatibility(text: str) -> List[Dict]:
    """Check for ATS compatibility issues."""
    issues = []

    if '\t' in text:
        issues.append({
            'type': 'warning',
            'title': 'Contains Tabs',
            'description': 'Replace tabs with spaces for better ATS compatibility.'
        })

    if re.search(r'[•●○■□▪▫]', text):
        issues.append({
            'type': 'warning',
            'title': 'Special Bullet Characters',
            'description': 'Use standard bullets (-, *, or •) instead of special Unicode characters.'
        })

    text_lower = text.lower()

    if 'experience' not in text_lower and 'work history' not in text_lower:
        issues.append({
            'type': 'danger',
            'title': 'Missing Experience Section',
            'description': 'Add a clear "Experience" or "Work History" section header.'
        })

    if 'education' not in text_lower:
        issues.append({
            'type': 'info',
            'title': 'Missing Education Section',
            'description': 'Consider adding an "Education" section if applicable.'
        })

    if not re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text):
        issues.append({
            'type': 'warning',
            'title': 'No Email Found',
            'description': 'Make sure your email address is clearly visible.'
        })

    return issues


# ---------------------------------------------------------
# SECTION DETECTION
# ---------------------------------------------------------
def detect_section(line: str) -> str | None:
    """Return the section name if the line is a section header."""
    headers = {
        "skills": ["skills", "technical skills", "core competencies"],
        "experience": ["experience", "work experience", "professional experience", "work history"],
        "education": ["education"],
    }

    lower = line.strip().lower()
    for section, keywords in headers.items():
        if any(k in lower for k in keywords):
            return section
    return None


# ---------------------------------------------------------
# HIGH-LEVEL SUGGESTIONS
# ---------------------------------------------------------
def generate_suggestions(resume: str, job_desc: str, impact_count: int, quant_count: int, keyword_score: float):
    """Generate high-level improvement suggestions."""
    suggestions = []

    if impact_count < 5:
        suggestions.append({
            'type': 'warning',
            'title': 'Use More Action Verbs',
            'description': 'Start bullet points with strong action verbs to demonstrate impact.'
        })

    if quant_count < 3:
        suggestions.append({
            'type': 'danger',
            'title': 'Add Quantifiable Results',
            'description': 'Include specific metrics and numbers to demonstrate tangible impact.'
        })

    if job_desc and keyword_score < 50:
        suggestions.append({
            'type': 'danger',
            'title': 'Low Keyword Match',
            'description': 'Your resume is missing many keywords from the job description.'
        })

    if len(resume) < 500:
        suggestions.append({
            'type': 'warning',
            'title': 'Resume Seems Short',
            'description': 'Consider expanding your experience descriptions.'
        })

    resume_lower = resume.lower()
    if 'linkedin' not in resume_lower and 'github' not in resume_lower and 'http' not in resume_lower:
        suggestions.append({
            'type': 'info',
            'title': 'Add Professional Links',
            'description': 'Include your LinkedIn, GitHub, or portfolio.'
        })

    if 'skills' not in resume_lower:
        suggestions.append({
            'type': 'info',
            'title': 'Add Skills Section',
            'description': 'Include a dedicated skills section.'
        })

    return suggestions


# ---------------------------------------------------------
# LINE-BY-LINE CHANGES (NOW SECTION-AWARE)
# ---------------------------------------------------------
def generate_specific_changes(resume: str, job_desc: str, missing_keywords: List[str], impact_verbs: List[str]):
    """Generate line-by-line improvement suggestions with section awareness."""
    changes = []
    lines = resume.split("\n")

    current_section = None

    # Tools to enforce in Experience
    TOOL_KEYWORDS = [
        "sql", "python", "r", "excel", "tableau", "power bi",
        "slate", "crm", "ssis", "snowflake", "looker", "bigquery"
    ]

    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue

        # Detect section headers
        section = detect_section(stripped)
        if section:
            current_section = section
            continue

        # Only analyze bullet points
        is_bullet = stripped.startswith(('-', '•', '*', '●')) or (
            stripped[0].isdigit() and '.' in stripped[:3]
        )
        if not is_bullet:
            continue

        clean_line = re.sub(r'^[\-•*●\d\.]\s*', '', stripped)
        suggestions = []

        # -----------------------------------------------------
        # SKILLS SECTION RULES
        # -----------------------------------------------------
        if current_section == "skills":
            # Skills should be comma-separated hard skills
            if " " in clean_line and "," not in clean_line:
                suggestions.append("Skills should be listed as hard skills, not full sentences")

            # Suggest missing JD hard skills
            relevant_hard_skills = [
                kw for kw in missing_keywords
                if kw.lower() in TOOL_KEYWORDS
            ]
            if relevant_hard_skills:
                suggestions.append(
                    f"Consider adding relevant tools: {', '.join(relevant_hard_skills[:5])}"
                )

        # -----------------------------------------------------
        # EXPERIENCE SECTION RULES
        # -----------------------------------------------------
        elif current_section == "experience":
            # Must start with action verb
            first_word = clean_line.split()[0].lower()
            if first_word not in impact_verbs:
                suggestions.append("Start with a strong action verb")

            # Must include a metric
            has_numbers = bool(re.search(
                r'\d+%|\d+\+|[$€£]\d+|\d+[xX]|\d+\s*(million|billion|thousand|k|m|b)',
                clean_line
            ))
            if not has_numbers:
                suggestions.append("Add a quantifiable metric to show impact")

            # Must include a tool
            if not any(t in clean_line.lower() for t in TOOL_KEYWORDS):
                suggestions.append("Mention the tool or technology used (e.g., SQL, Python, Slate CRM)")

            # Suggest missing keywords
            relevant_keywords = [
                kw for kw in missing_keywords[:10]
                if kw not in clean_line.lower()
            ]
            if relevant_keywords:
                suggestions.append(
                    f"Consider incorporating: {', '.join(relevant_keywords[:3])}"
                )

        # -----------------------------------------------------
        # OTHER SECTIONS — skip
        # -----------------------------------------------------
        else:
            continue

        if suggestions:
            changes.append({
                "line_number": i + 1,
                "original": stripped,
                "suggestions": suggestions
            })

    return changes[:15]


# ---------------------------------------------------------
# MAIN ANALYSIS
# ---------------------------------------------------------
def analyze_resume(resume: str, job_desc: str | None) -> Dict:
    """Main analysis function."""
    job_keywords = extract_keywords(job_desc) if job_desc else []
    resume_lower = resume.lower()

    found_keywords = [kw for kw in job_keywords if kw in resume_lower]
    missing_keywords = [kw for kw in job_keywords if kw not in resume_lower]

    if job_keywords:
        keyword_score = (len(found_keywords) / len(job_keywords)) * 100
        if keyword_score >= 40:
            keyword_score = min(100, keyword_score * 1.2)
    else:
        keyword_score = 75

    impact_count, impact_verbs = count_impact_verbs(resume)
    impact_score = min(100, (impact_count / 6) * 100)

    quant_count = count_quantifiable_results(resume)
    quant_score = min(100, (quant_count / 4) * 100)

    ats_issues = check_ats_compatibility(resume)
    ats_score = max(0, 100 - (len(ats_issues) * 12))

    suggestions = generate_suggestions(
        resume, job_desc, impact_count, quant_count, keyword_score
    )
    specific_changes = generate_specific_changes(
        resume, job_desc, missing_keywords, impact_verbs
    )

    overall_score = (
        keyword_score * 0.3 +
        ats_score * 0.25 +
        impact_score * 0.25 +
        quant_score * 0.2
    )

    return {
        "overall_score": round(overall_score),
        "keyword_score": round(keyword_score),
        "ats_score": round(ats_score),
        "impact_score": round(impact_score),
        "quant_score": round(quant_score),
        "found_keywords": found_keywords[:20],
        "missing_keywords": missing_keywords[:20],
        "impact_verbs": impact_verbs,
        "suggestions": suggestions,
        "ats_issues": ats_issues,
        "specific_changes": specific_changes
    }

# ---------------------------------------------------------
# LLM-LIKE OPTIMIZATION HELPERS
# ---------------------------------------------------------

WEAK_PHRASES = [
    "responsible for",
    "worked on",
    "helped with",
    "assisted with",
    "tasked with",
    "involved in",
    "participated in"
]

TOOL_KEYWORDS = [
    "sql", "python", "r", "excel", "tableau", "power bi",
    "slate", "crm", "ssis", "snowflake", "looker", "bigquery"
]


def rewrite_experience_line(line: str, missing_keywords: List[str]) -> str:
    """
    Produce an LLM-style rewrite suggestion for an experience bullet.
    Structure: Action Verb → Task → Metric → Tool
    """
    lower = line.lower()

    # 1. Pick an action verb
    verb = None
    for v in IMPACT_VERBS:
        if v in lower:
            verb = v
            break
    if not verb:
        verb = "Improved"

    # 2. Extract a tool if present
    tool = None
    for t in TOOL_KEYWORDS:
        if t in lower:
            tool = t
            break

    # 3. Suggest a missing tool if none found
    if not tool:
        for kw in missing_keywords:
            if kw.lower() in TOOL_KEYWORDS:
                tool = kw
                break

    # 4. Add a metric placeholder if none exists
    has_metric = bool(re.search(r'\d+%|\d+\+|[$€£]\d+', lower))
    metric = "" if has_metric else " (achieving a measurable improvement)"

    # 5. Build rewrite
    rewritten = f"{verb.capitalize()} {line.strip()} {metric}"
    if tool:
        rewritten += f" using {tool}"

    return rewritten.strip()
