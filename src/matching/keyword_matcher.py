"""
Keyword Matching Engine
-----------------------

Provides deterministic keyword and skill matching between a resume
and a job description.

This module is intentionally independent from Streamlit so it can be
used by the application, tests, or future APIs.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable, List, Sequence


@dataclass
class KeywordMatchResult:
    """Structured result returned by the keyword matching engine."""

    matched_items: List[str]
    missing_items: List[str]
    extra_items: List[str]
    match_percentage: float
    total_required: int
    total_matched: int

    @property
    def success(self) -> bool:
        """Return True when the matching operation completed normally."""
        return True


# Canonical aliases used to make equivalent terms comparable.
TERM_ALIASES = {
    "rest apis": "REST API",
    "rest api": "REST API",
    "restful api": "REST API",
    "restful apis": "REST API",
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "scikit learn": "scikit-learn",
    "scikit-learn": "scikit-learn",
    "sklearn": "scikit-learn",
    "machine learning": "Machine Learning",
    "ml": "Machine Learning",
    "artificial intelligence": "Artificial Intelligence",
    "ai": "Artificial Intelligence",
    "natural language processing": "NLP",
    "nlp": "NLP",
    "large language model": "LLM",
    "large language models": "LLM",
    "llm": "LLM",
    "object oriented programming": "OOP",
    "object-oriented programming": "OOP",
    "oop": "OOP",
}


# Display names for common technical terms.
DISPLAY_NAMES = {
    "python": "Python",
    "sql": "SQL",
    "java": "Java",
    "javascript": "JavaScript",
    "typescript": "TypeScript",
    "c": "C",
    "c++": "C++",
    "c#": "C#",
    "html": "HTML",
    "css": "CSS",
    "aws": "AWS",
    "azure": "Azure",
    "gcp": "GCP",
    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "git": "Git",
    "github": "GitHub",
    "linux": "Linux",
    "pandas": "Pandas",
    "numpy": "NumPy",
    "scipy": "SciPy",
    "tensorflow": "TensorFlow",
    "pytorch": "PyTorch",
    "matplotlib": "Matplotlib",
    "plotly": "Plotly",
    "streamlit": "Streamlit",
    "flask": "Flask",
    "django": "Django",
    "fastapi": "FastAPI",
    "mongodb": "MongoDB",
    "mysql": "MySQL",
    "postgresql": "PostgreSQL",
    "redis": "Redis",
    "spark": "Spark",
    "hadoop": "Hadoop",
}


def normalize_term(term: str) -> str:
    """
    Normalize a single term for comparison.

    Parameters
    ----------
    term:
        Raw skill or keyword.

    Returns
    -------
    str
        Canonicalized comparison term.
    """
    if not isinstance(term, str):
        return ""

    normalized = term.strip().lower()
    normalized = re.sub(r"\s+", " ", normalized)

    if not normalized:
        return ""

    return TERM_ALIASES.get(normalized, normalized)


def _display_term(term: str) -> str:
    """
    Convert a normalized term into a readable display form.
    """
    normalized = normalize_term(term)

    if not normalized:
        return ""

    # Canonical aliases already have the desired display form.
    for alias, canonical in TERM_ALIASES.items():
        if normalized == canonical.lower():
            return canonical

    # Common technical terms use established capitalization.
    if normalized in DISPLAY_NAMES:
        return DISPLAY_NAMES[normalized]

    # Fallback for unknown terms.
    return normalized.title()


def normalize_terms(terms: Iterable[str] | None) -> List[str]:
    """
    Normalize, canonicalize, and deduplicate a collection of terms.

    Order is preserved according to the first occurrence.
    """
    if terms is None:
        return []

    normalized_terms: List[str] = []
    seen = set()

    for term in terms:
        normalized = normalize_term(term)

        if not normalized or normalized in seen:
            continue

        seen.add(normalized)
        normalized_terms.append(normalized)

    return normalized_terms


def match_keywords(
    resume_keywords: Sequence[str] | None,
    job_keywords: Sequence[str] | None,
) -> KeywordMatchResult:
    """
    Compare resume keywords against required job keywords.

    Parameters
    ----------
    resume_keywords:
        Keywords/skills identified in the resume.

    job_keywords:
        Keywords/skills identified from the job description.

    Returns
    -------
    KeywordMatchResult
        Structured matching information.
    """
    resume_terms = normalize_terms(resume_keywords)
    job_terms = normalize_terms(job_keywords)

    resume_set = set(resume_terms)

    matched_normalized = [
        term for term in job_terms
        if term in resume_set
    ]

    missing_normalized = [
        term for term in job_terms
        if term not in resume_set
    ]

    job_set = set(job_terms)

    extra_normalized = [
        term for term in resume_terms
        if term not in job_set
    ]

    matched_items = [
        _display_term(term)
        for term in matched_normalized
    ]

    missing_items = [
        _display_term(term)
        for term in missing_normalized
    ]

    extra_items = [
        _display_term(term)
        for term in extra_normalized
    ]

    total_required = len(job_terms)
    total_matched = len(matched_normalized)

    if total_required == 0:
        match_percentage = 0.0
    else:
        match_percentage = round(
            (total_matched / total_required) * 100,
            2,
        )

    return KeywordMatchResult(
        matched_items=matched_items,
        missing_items=missing_items,
        extra_items=extra_items,
        match_percentage=match_percentage,
        total_required=total_required,
        total_matched=total_matched,
    )


def match_skills(
    resume_skills: Sequence[str] | None,
    job_skills: Sequence[str] | None,
) -> KeywordMatchResult:
    """
    Compare resume skills against job-required skills.

    This is a semantic alias for ``match_keywords`` and keeps the
    matching API readable when working specifically with skills.
    """
    return match_keywords(
        resume_keywords=resume_skills,
        job_keywords=job_skills,
    )