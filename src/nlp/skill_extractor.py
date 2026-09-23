"""
Resume Skill Extractor
----------------------

Provides deterministic skill extraction from resume text.

The extractor reuses the skill vocabulary and aliases defined by the
job-description analyzer so that resume and job-description skills
remain compatible with the matching engine.

This module is intentionally local and deterministic. It does not
require an external API, LLM, or additional dependency.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from src.job.job_analyzer import (
    COMMON_SKILLS,
    SKILL_ALIASES,
)
from src.nlp.text_processor import clean_resume_text


# ------------------------------------------------------------------
# SKILL CATEGORIES
# ------------------------------------------------------------------

SKILL_CATEGORIES: Dict[str, Tuple[str, ...]] = {
    "programming_languages": (
        "Python",
        "Java",
        "C",
        "C++",
        "C#",
        "JavaScript",
        "TypeScript",
        "Go",
        "Rust",
        "PHP",
        "Ruby",
        "Kotlin",
        "Swift",
    ),
    "web_technologies": (
        "HTML",
        "CSS",
        "React",
        "Angular",
        "Vue",
        "Node.js",
        "Express.js",
        "Django",
        "Flask",
        "FastAPI",
    ),
    "databases": (
        "SQL",
        "MySQL",
        "PostgreSQL",
        "MongoDB",
        "Oracle",
        "SQLite",
        "Redis",
    ),
    "data_ai_ml": (
        "Machine Learning",
        "Deep Learning",
        "Artificial Intelligence",
        "Natural Language Processing",
        "NLP",
        "Computer Vision",
        "Data Science",
        "Data Analysis",
        "Data Analytics",
        "Generative AI",
        "Large Language Models",
        "LLM",
        "RAG",
        "LangChain",
        "TensorFlow",
        "PyTorch",
        "Keras",
        "scikit-learn",
        "Pandas",
        "NumPy",
        "Matplotlib",
        "Seaborn",
        "Hugging Face",
        "Transformers",
    ),
    "cloud_devops": (
        "AWS",
        "Azure",
        "Google Cloud",
        "GCP",
        "Docker",
        "Kubernetes",
        "Jenkins",
        "Git",
        "GitHub",
        "GitLab",
        "CI/CD",
    ),
    "software_engineering": (
        "REST API",
        "API",
        "Microservices",
        "Object-Oriented Programming",
        "OOP",
        "Data Structures",
        "Algorithms",
        "System Design",
        "Software Development",
        "Agile",
        "Scrum",
    ),
    "testing": (
        "Unit Testing",
        "PyTest",
        "pytest",
        "Selenium",
    ),
    "cybersecurity": (
        "Cyber Security",
        "Cybersecurity",
        "Network Security",
        "Cryptography",
    ),
    "professional": (
        "Problem Solving",
        "Communication",
        "Leadership",
        "Teamwork",
        "Time Management",
    ),
}


# ------------------------------------------------------------------
# RESULT DATA CLASS
# ------------------------------------------------------------------

@dataclass
class ResumeSkillExtraction:
    """
    Stores the structured result of resume skill extraction.
    """

    success: bool
    skills: List[str] = field(default_factory=list)
    categories: Dict[str, List[str]] = field(
        default_factory=dict
    )
    skill_count: int = 0
    message: str = ""


# ------------------------------------------------------------------
# NORMALIZATION HELPERS
# ------------------------------------------------------------------

def _normalize_skill_name(skill: str) -> str:
    """
    Normalize a skill name for comparison.

    Parameters
    ----------
    skill:
        Raw skill name.

    Returns
    -------
    str
        Lowercase normalized skill name.
    """

    if not isinstance(skill, str):
        return ""

    normalized = skill.strip().lower()
    normalized = re.sub(
        r"\s+",
        " ",
        normalized,
    )

    return normalized


def _canonicalize_skill(skill: str) -> str:
    """
    Convert an extracted skill or alias to its canonical name.
    """

    normalized = _normalize_skill_name(skill)

    if not normalized:
        return ""

    # Direct alias lookup.
    if normalized in SKILL_ALIASES:
        return SKILL_ALIASES[normalized]

    # Match against the standard vocabulary.
    for common_skill in COMMON_SKILLS:
        if _normalize_skill_name(common_skill) == normalized:
            return common_skill

    return skill.strip()


def _contains_skill(text: str, skill: str) -> bool:
    """
    Check whether a skill occurs as a meaningful term.

    Boundary handling prevents false positives such as:
        Java    matching "JavaScript"
        C       matching arbitrary words beginning with C

    Technical punctuation such as +, #, ., and / is preserved.
    """

    if not text or not skill:
        return False

    escaped_skill = re.escape(skill)

    pattern = rf"(?<![A-Za-z0-9]){escaped_skill}(?![A-Za-z0-9])"

    return re.search(
        pattern,
        text,
        flags=re.IGNORECASE,
    ) is not None


# ------------------------------------------------------------------
# SKILL EXTRACTION
# ------------------------------------------------------------------

def extract_skills(
    text: str | None,
) -> List[str]:
    """
    Extract recognized skills from resume text.

    Parameters
    ----------
    text:
        Raw or cleaned resume text.

    Returns
    -------
    list[str]
        Unique skills in canonical form.
    """

    if not text or not isinstance(text, str):
        return []

    cleaned_text = clean_resume_text(text)

    if not cleaned_text:
        return []

    found_skills: List[str] = []
    seen = set()

    # Check aliases first so alternate forms are converted into
    # canonical skill names.
    for alias, canonical_skill in SKILL_ALIASES.items():

        if not _contains_skill(
            cleaned_text,
            alias,
        ):
            continue

        normalized_canonical = _normalize_skill_name(
            canonical_skill
        )

        if normalized_canonical in seen:
            continue

        found_skills.append(canonical_skill)
        seen.add(normalized_canonical)

    # Check the complete common-skill vocabulary.
    for skill in COMMON_SKILLS:

        if not _contains_skill(
            cleaned_text,
            skill,
        ):
            continue

        canonical_skill = _canonicalize_skill(skill)
        normalized_canonical = _normalize_skill_name(
            canonical_skill
        )

        if normalized_canonical in seen:
            continue

        found_skills.append(canonical_skill)
        seen.add(normalized_canonical)

    return found_skills


# ------------------------------------------------------------------
# SKILL CATEGORIZATION
# ------------------------------------------------------------------

def categorize_skills(
    skills: List[str] | None,
) -> Dict[str, List[str]]:
    """
    Organize extracted skills into predefined categories.

    Parameters
    ----------
    skills:
        List of canonical or recognized skills.

    Returns
    -------
    dict[str, list[str]]
        Category-to-skills mapping.
    """

    if not skills:
        return {}

    normalized_input = {
        _normalize_skill_name(skill): skill
        for skill in skills
        if isinstance(skill, str) and skill.strip()
    }

    categories: Dict[str, List[str]] = {}

    for category_name, category_skills in SKILL_CATEGORIES.items():

        matched: List[str] = []

        for category_skill in category_skills:

            normalized_category_skill = _normalize_skill_name(
                _canonicalize_skill(category_skill)
            )

            if normalized_category_skill not in normalized_input:
                continue

            actual_skill = normalized_input[
                normalized_category_skill
            ]

            if actual_skill not in matched:
                matched.append(actual_skill)

        if matched:
            categories[category_name] = matched

    return categories


# ------------------------------------------------------------------
# MAIN EXTRACTION
# ------------------------------------------------------------------

def analyze_resume_skills(
    text: str | None,
) -> ResumeSkillExtraction:
    """
    Extract and categorize skills from resume text.

    Parameters
    ----------
    text:
        Raw or cleaned resume text.

    Returns
    -------
    ResumeSkillExtraction
        Structured skill extraction result.
    """

    if not isinstance(text, str) or not text.strip():
        return ResumeSkillExtraction(
            success=False,
            message="Resume text is empty.",
        )

    cleaned_text = clean_resume_text(text)

    if not cleaned_text:
        return ResumeSkillExtraction(
            success=False,
            message="Resume text does not contain usable content.",
        )

    skills = extract_skills(cleaned_text)
    categories = categorize_skills(skills)

    return ResumeSkillExtraction(
        success=True,
        skills=skills,
        categories=categories,
        skill_count=len(skills),
        message=(
            "Resume skills extracted successfully. "
            f"Detected {len(skills)} skill"
            f"{'s' if len(skills) != 1 else ''}."
        ),
    )