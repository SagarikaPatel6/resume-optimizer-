# core/analysis.py

import re
from typing import List, Dict
from collections import Counter

from core.constants import COMMON_WORDS, IMPACT_VERBS, QUANT_PATTERNS


def extract_keywords(text: str, min_length: int = 4) -> List[str]:
    """Extract meaningful keywords from text."""
    words = re.findall(r'\b[a-z]+\b', text.lower())
    keywords = [w for w in words if len(w) >= min_length and w not in COMMON_WORDS]
    return list(set(keywords))


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


def generate_specific_changes(resume: str, job_desc: str, missing_keywords: List[str], impact_verbs: List[str]):
    """Generate line-by-line improvement suggestions."""
    changes = []
    lines = resume.split('\n')

    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue

        is_bullet = stripped.startswith(('-', '•', '*', '●')) or (stripped[0].isdigit() and '.' in stripped[:3])
        if not is_bullet:
            continue

        clean_line = re.sub(r'^[\-•*●\d\.]\s*', '', stripped)
        has_impact = any(v in clean_line.lower() for v in impact_verbs)
        has_numbers = bool(re.search(r'\d+%|\d+\+|[$€£]\d+|\d+[xX]|\d+\s*(million|billion|thousand|k|m|b)', clean_line))

        suggestions = []

        if not has_impact and len(clean_line) > 10:
            suggestions.append("Start with an action verb")

        if not has_numbers and len(clean_line) > 10:
            suggestions.append("Add quantifiable metrics")

        relevant_keywords = [kw for kw in missing_keywords[:10] if kw not in clean_line.lower()]
        if relevant_keywords and suggestions:
            suggestions.append(f"Consider adding: {', '.join(relevant_keywords[:3])}")

        if suggestions:
            changes.append({
                'line_number': i + 1,
                'original': stripped,
                'suggestions': suggestions
            })

    return changes[:15]

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

    suggestions = generate_suggestions(resume, job_desc, impact_count, quant_count, keyword_score)
    specific_changes = generate_specific_changes(resume, job_desc, missing_keywords, impact_verbs)

    overall_score = (
        keyword_score * 0.3 +
        ats_score * 0.25 +
        impact_score * 0.25 +
        quant_score * 0.2
    )

    return {
        'overall_score': round(overall_score),
        'keyword_score': round(keyword_score),
        'ats_score': round(ats_score),
        'impact_score': round(impact_score),
        'quant_score': round(quant_score),
        'found_keywords': found_keywords[:20],
        'missing_keywords': missing_keywords[:20],
        'impact_verbs': impact_verbs,
        'suggestions': suggestions,
        'ats_issues': ats_issues,
        'specific_changes': specific_changes
    }
