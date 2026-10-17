"""Evidence-preserving, offline resume profile for student-facing career explanations.

This is an explanation layer, not proof of proficiency or occupational eligibility.
Do not infer skills from hobbies, family details, address or the user's aspirations.
"""
from __future__ import annotations
import re

# Safe, explicit aliases only. Skills are supported by literal mentions.
SKILL_ALIASES = (
    ("HTML", (r"\bhtml\b", r"\bhypertext markup language\b"), "technical"),
    ("CSS", (r"\bcss\b", r"\bcascading style sheets\b"), "technical"),
    ("Microsoft Word", (r"\bms\s+word\b", r"\bmicrosoft\s+word\b"), "office"),
    ("Microsoft Excel", (r"\b(?:ms|microsoft)\s+excel\b", r"\bexcel\b"), "office"),
    ("Basic computer knowledge", (r"\bbasic\s+computer\s+knowledge\b", r"\bcomputer\s+literacy\b"), "technical"),
    ("Accounting", (r"\baccounting\b",), "business"),
    ("Bookkeeping", (r"\bbookkeeping\b",), "business"),
    ("Communication", (r"\b(?:good|strong|effective)\s+communication\b", r"\bcommunication\s+skills\b"), "transferable"),
    ("Customer service", (r"\bcustomer\s+service\b",), "interest"),
    ("Python", (r"\bpython\b",), "technical"),
    ("FastAPI", (r"\bfastapi\b",), "technical"),
    ("SQL", (r"\bsql\b",), "technical"),
    ("PostgreSQL", (r"\bpostgresql\b",), "technical"),
    ("Power BI", (r"\bpower\s*bi\b",), "technical"),
    ("Tableau", (r"\btableau\b",), "technical"),
    ("Pandas", (r"\bpandas\b",), "technical"),
    ("SEO", (r"\bseo\b", r"\bsearch engine optimiz(?:ation|ing)\b"), "technical"),
    ("Google Analytics", (r"\bgoogle analytics\b",), "technical"),
    ("Google Ads", (r"\bgoogle ads\b",), "technical"),
)

# Occupation families are explanatory; these terms do not create or alter rankings.
FAMILIES = {
    "web": ("web developer", "web and digital", "web designer", "interface designer", "webmaster"),
    "it": ("computer user support", "computer network support", "technical support", "help desk", "it support"),
    "office": ("administrative", "secretar", "office clerk", "receptionist", "data entry", "information clerk"),
    "accounts": ("account", "bookkeep", "billing", "payroll"),
    "customer": ("customer service", "customer support", "customer representative"),
    "software": ("software developer", "computer programmer", "application developer"),
    "data": ("data scientist", "data analyst", "business intelligence", "statistician"),
    "marketing": ("marketing", "advertising", "public relations", "search marketing"),
}
RELEVANCE = {
    "web": ("HTML", "CSS", "Python", "FastAPI"),
    "it": ("Basic computer knowledge", "Microsoft Word", "Microsoft Excel", "HTML", "CSS"),
    "office": ("Microsoft Word", "Microsoft Excel", "Basic computer knowledge", "Communication", "Bookkeeping"),
    "accounts": ("Accounting", "Bookkeeping", "Microsoft Excel", "Microsoft Word"),
    "customer": ("Communication", "Microsoft Word", "Microsoft Excel", "Basic computer knowledge"),
    "software": ("Python", "FastAPI", "SQL", "PostgreSQL", "HTML", "CSS"),
    "data": ("SQL", "Microsoft Excel", "Power BI", "Tableau", "Pandas", "Python"),
    "marketing": ("SEO", "Google Analytics", "Google Ads", "Communication", "Microsoft Excel"),
}

def _section(text, name, stops):
    found = re.search(r"(?im)^\s*" + name + r"\s*:?\s*$", text)
    if not found:
        return ""
    remaining = text[found.end():]
    stop = re.search(r"(?im)^\s*(?:" + "|".join(stops) + r")\s*:?\s*$", remaining)
    return remaining[:stop.start()] if stop else remaining


def extract_resume_evidence(text: str) -> dict:
    """Conservative explicit claims; interests are NOT skills or employment history."""
    text = text or ""
    skills_section = _section(text, r"skills(?:\s+and\s+abilities)?", (
        "education", "work experience", "experience", "projects", "hobbies.*", "personal details", "certifications"))
    # When resume has a skills section, avoid matching unrelated text in hobbies/address.
    skills_corpus = skills_section or text
    objective = _section(text, r"(?:career )?objective|summary|profile", (
        "skills", "education", "work experience", "experience", "projects", "personal details"))
    extracted = []
    interests = []
    basic = []
    categories = {}
    for label, patterns, kind in SKILL_ALIASES:
        mentioned_as_skill = any(re.search(p, skills_corpus, re.I) for p in patterns)
        mentioned_in_objective = any(re.search(p, objective, re.I) for p in patterns)
        if kind == 'interest':
            if mentioned_as_skill and not mentioned_in_objective:
                extracted.append(label)
                categories[label] = 'transferable'
            elif mentioned_in_objective:
                interests.append(label)
            continue
        if mentioned_as_skill:
            extracted.append(label)
            categories[label] = kind
            if re.search(r"(?i)\bbasic\s+(?:ms\s+)?" + (r"excel" if label == "Microsoft Excel" else r"accounting|bookkeeping" if label in ("Accounting", "Bookkeeping") else re.escape(label)), skills_corpus):
                basic.append(label)
    education = []
    if re.search(r"\bBCA\b", text, re.I): education.append('BCA')
    if re.search(r"\bMCA\b", text, re.I):
        ongoing = bool(re.search(r"(?i)(?:MCA\s+(?:running|pursuing|ongoing)|(?:pursuing|ongoing)\s+MCA)", text))
        education.append('MCA (ongoing)' if ongoing else 'MCA (completion not verified)')
    fresher = bool(re.search(r"\bfresher\b", text, re.I))
    return {'skills': extracted, 'skill_categories': categories, 'basic_skills': basic,
            'career_interests': interests, 'education': education,
            'experience_level': 'Fresher (stated)' if fresher else 'Not verified'}


def career_evidence(title: str, profile: dict) -> dict:
    """Only show evidence relevant to the displayed occupation, not the full resume."""
    normalized = title.casefold()
    families = [family for family, words in FAMILIES.items() if any(word in normalized for word in words)]
    allowed = {s for family in families for s in RELEVANCE[family]}
    relevant = [s for s in profile['skills'] if s in allowed]
    interests = [s for s in profile['career_interests'] if
                 (s == 'Customer service' and any(f in families for f in ('customer', 'office', 'it')))]
    return {'relevant_skills': relevant, 'career_interests': interests,
            'education': list(profile['education']), 'experience_level': profile['experience_level'],
            'basic_skills': [s for s in relevant if s in profile['basic_skills']]}
