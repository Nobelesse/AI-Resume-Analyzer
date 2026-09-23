"""
Resume Match Score Calculator
-----------------------------

Combines individual resume/job matching components into one structured
match score.

The default scoring model is:

- Skills:              40%
- Experience:          25%
- Education:           10%
- Projects:            10%
- Semantic similarity: 15%

These weights are configurable and represent application-design
choices. They are not a validated hiring or employment assessment
methodology.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Sequence

from src.matching.keyword_matcher import match_keywords
from src.matching.semantic_matcher import (
    SemanticMatchResult,
    compare_texts,
)


# ------------------------------------------------------------------
# DEFAULT WEIGHTS
# ------------------------------------------------------------------

SKILLS_WEIGHT = 0.40
EXPERIENCE_WEIGHT = 0.25
EDUCATION_WEIGHT = 0.10
PROJECTS_WEIGHT = 0.10
SEMANTIC_WEIGHT = 0.15

TOTAL_WEIGHT = (
    SKILLS_WEIGHT
    + EXPERIENCE_WEIGHT
    + EDUCATION_WEIGHT
    + PROJECTS_WEIGHT
    + SEMANTIC_WEIGHT
)


# ------------------------------------------------------------------
# RESULT DATA CLASS
# ------------------------------------------------------------------

@dataclass
class MatchScoreResult:
    """Complete result returned by the score calculator."""

    final_score: float

    skills_score: float
    experience_score: float
    education_score: float
    projects_score: float
    semantic_score: float

    skills_weighted_score: float
    experience_weighted_score: float
    education_weighted_score: float
    projects_weighted_score: float
    semantic_weighted_score: float

    semantic_result: SemanticMatchResult

    success: bool
    message: str = ""


# ------------------------------------------------------------------
# VALUE NORMALIZATION
# ------------------------------------------------------------------

def _clamp_percentage(value: float) -> float:
    """
    Clamp a score to the valid percentage range of 0 to 100.
    """
    try:
        numeric_value = float(value)
    except (TypeError, ValueError):
        return 0.0

    return round(
        max(0.0, min(100.0, numeric_value)),
        2,
    )


def _normalize_text(value: str | None) -> str:
    """
    Normalize text for case-insensitive comparison.
    """
    if not isinstance(value, str):
        return ""

    return " ".join(value.lower().split())


# ------------------------------------------------------------------
# EXPERIENCE SCORING
# ------------------------------------------------------------------

def extract_year_requirement(
    requirements: Sequence[str] | None,
) -> float:
    """
    Extract the highest explicit years-of-experience requirement.

    Examples
    --------
    "2 years of experience" -> 2.0
    "3+ years experience"   -> 3.0
    "At least 5 years"      -> 5.0
    """
    if not requirements:
        return 0.0

    highest_requirement = 0.0

    for requirement in requirements:
        if not isinstance(requirement, str):
            continue

        matches = re.findall(
            r"(?<!\d)(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)",
            requirement.lower(),
        )

        for match in matches:
            try:
                years = float(match)
            except ValueError:
                continue

            highest_requirement = max(
                highest_requirement,
                years,
            )

    return highest_requirement


def calculate_experience_score(
    resume_years: float | int | None,
    job_requirements: Sequence[str] | None,
) -> float:
    """
    Calculate the experience score as a percentage.

    Rules
    -----
    - No explicit job experience requirement -> 100%.
    - No resume experience -> 0% when a requirement exists.
    - Meeting the requirement -> 100%.
    - Partial experience -> proportional score.
    - Experience above the requirement is capped at 100%.
    """
    required_years = extract_year_requirement(
        job_requirements
    )

    if required_years <= 0:
        return 100.0

    try:
        candidate_years = max(
            0.0,
            float(resume_years or 0),
        )
    except (TypeError, ValueError):
        candidate_years = 0.0

    score = (
        candidate_years / required_years
    ) * 100.0

    return _clamp_percentage(score)


# ------------------------------------------------------------------
# EDUCATION SCORING
# ------------------------------------------------------------------

def calculate_education_score(
    resume_education: Sequence[str] | None,
    job_education: Sequence[str] | None,
) -> float:
    """
    Calculate education similarity using keyword overlap.

    If no education requirement is specified, the component receives
    100% because there is no explicit education requirement to miss.
    """
    job_items = [
        item
        for item in (job_education or [])
        if isinstance(item, str) and item.strip()
    ]

    resume_items = [
        item
        for item in (resume_education or [])
        if isinstance(item, str) and item.strip()
    ]

    if not job_items:
        return 100.0

    if not resume_items:
        return 0.0

    resume_text = _normalize_text(
        " ".join(resume_items)
    )

    matched = 0

    for requirement in job_items:
        requirement_text = _normalize_text(requirement)

        if not requirement_text:
            continue

        # Direct phrase match first.
        if requirement_text in resume_text:
            matched += 1
            continue

        # Otherwise compare meaningful words.
        requirement_words = {
            word
            for word in re.findall(
                r"\b[a-z0-9]+\b",
                requirement_text,
            )
            if len(word) >= 3
        }

        if not requirement_words:
            continue

        matched_words = {
            word
            for word in requirement_words
            if word in resume_text
        }

        if matched_words:
            matched += 1

    score = (
        matched / len(job_items)
    ) * 100.0

    return _clamp_percentage(score)


# ------------------------------------------------------------------
# PROJECT SCORING
# ------------------------------------------------------------------

def calculate_project_score(
    resume_project_text: str | None,
    job_keywords: Sequence[str] | None,
) -> float:
    """
    Calculate project relevance using keyword overlap.

    The score represents how many of the job's important keywords are
    represented in the candidate's project text.

    If no job keywords are supplied, the component receives 100%.
    """
    keywords = [
        keyword
        for keyword in (job_keywords or [])
        if isinstance(keyword, str) and keyword.strip()
    ]

    project_text = _normalize_text(
        resume_project_text
    )

    if not keywords:
        return 100.0

    if not project_text:
        return 0.0

    matched = 0

    for keyword in keywords:
        normalized_keyword = _normalize_text(keyword)

        if not normalized_keyword:
            continue

        if normalized_keyword in project_text:
            matched += 1

    score = (
        matched / len(keywords)
    ) * 100.0

    return _clamp_percentage(score)


# ------------------------------------------------------------------
# SKILL SCORING
# ------------------------------------------------------------------

def calculate_skill_score(
    resume_skills: Sequence[str] | None,
    job_skills: Sequence[str] | None,
) -> float:
    """
    Calculate the skill score using the keyword matching engine.
    """
    result = match_keywords(
        resume_keywords=resume_skills,
        job_keywords=job_skills,
    )

    return _clamp_percentage(
        result.match_percentage
    )


# ------------------------------------------------------------------
# SEMANTIC SCORING
# ------------------------------------------------------------------

def calculate_semantic_score(
    resume_text: str | None,
    job_description: str | None,
) -> tuple[float, SemanticMatchResult]:
    """
    Calculate the semantic similarity score.

    Returns
    -------
    tuple
        Percentage score and detailed semantic result.
    """
    result = compare_texts(
        resume_text=resume_text,
        job_description=job_description,
    )

    return (
        _clamp_percentage(
            result.similarity_percentage
        ),
        result,
    )


# ------------------------------------------------------------------
# FINAL SCORE
# ------------------------------------------------------------------

def calculate_match_score(
    resume_skills: Sequence[str] | None,
    job_skills: Sequence[str] | None,
    resume_years: float | int | None,
    job_experience_requirements: Sequence[str] | None,
    resume_education: Sequence[str] | None,
    job_education_requirements: Sequence[str] | None,
    resume_project_text: str | None,
    job_keywords: Sequence[str] | None,
    resume_text: str | None,
    job_description: str | None,
) -> MatchScoreResult:
    """
    Calculate the complete resume-to-job match score.

    Parameters
    ----------
    resume_skills:
        Skills detected in the candidate's resume.

    job_skills:
        Skills detected in the job description.

    resume_years:
        Candidate's total relevant experience in years.

    job_experience_requirements:
        Experience requirements detected from the job description.

    resume_education:
        Education information from the candidate's resume.

    job_education_requirements:
        Education requirements detected from the job description.

    resume_project_text:
        Combined project-related text from the resume.

    job_keywords:
        Important keywords extracted from the job description.

    resume_text:
        Complete cleaned resume text.

    job_description:
        Complete cleaned job description.

    Returns
    -------
    MatchScoreResult
        Complete weighted match result.
    """

    if not isinstance(resume_text, str):
        resume_text = ""

    if not isinstance(job_description, str):
        job_description = ""

    skills_score = calculate_skill_score(
        resume_skills=resume_skills,
        job_skills=job_skills,
    )

    experience_score = calculate_experience_score(
        resume_years=resume_years,
        job_requirements=job_experience_requirements,
    )

    education_score = calculate_education_score(
        resume_education=resume_education,
        job_education=job_education_requirements,
    )

    projects_score = calculate_project_score(
        resume_project_text=resume_project_text,
        job_keywords=job_keywords,
    )

    semantic_score, semantic_result = (
        calculate_semantic_score(
            resume_text=resume_text,
            job_description=job_description,
        )
    )

    skills_weighted_score = (
        skills_score * SKILLS_WEIGHT
    )

    experience_weighted_score = (
        experience_score * EXPERIENCE_WEIGHT
    )

    education_weighted_score = (
        education_score * EDUCATION_WEIGHT
    )

    projects_weighted_score = (
        projects_score * PROJECTS_WEIGHT
    )

    semantic_weighted_score = (
        semantic_score * SEMANTIC_WEIGHT
    )

    final_score = (
        skills_weighted_score
        + experience_weighted_score
        + education_weighted_score
        + projects_weighted_score
        + semantic_weighted_score
    )

    final_score = _clamp_percentage(
        final_score
    )

    success = (
        semantic_result.success
        and math.isclose(
            TOTAL_WEIGHT,
            1.0,
            rel_tol=1e-9,
            abs_tol=1e-9,
        )
    )

    if success:
        message = (
            "Resume-to-job match score calculated "
            "successfully."
        )
    else:
        message = (
            "Match score was calculated, but semantic "
            "matching was not completed successfully."
        )

    return MatchScoreResult(
        final_score=final_score,
        skills_score=skills_score,
        experience_score=experience_score,
        education_score=education_score,
        projects_score=projects_score,
        semantic_score=semantic_score,
        skills_weighted_score=round(
            skills_weighted_score,
            2,
        ),
        experience_weighted_score=round(
            experience_weighted_score,
            2,
        ),
        education_weighted_score=round(
            education_weighted_score,
            2,
        ),
        projects_weighted_score=round(
            projects_weighted_score,
            2,
        ),
        semantic_weighted_score=round(
            semantic_weighted_score,
            2,
        ),
        semantic_result=semantic_result,
        success=success,
        message=message,
    )