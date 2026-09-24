"""
Deterministic Job Role Recommendation Engine

This module maps an extracted resume skill profile to a curated set of
common software, data, AI, and technology roles.

The engine is intentionally local and deterministic. It does not require
an external API or LLM.

The recommendation score represents application-specific skill alignment.
It is not a probability of employment and is not a hiring prediction.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Sequence, Tuple

from src.job.job_analyzer import SKILL_ALIASES
from src.nlp.skill_extractor import categorize_skills, extract_skills


# ------------------------------------------------------------------
# JOB ROLE PROFILE
# ------------------------------------------------------------------


@dataclass(frozen=True)
class JobRoleProfile:
    """
    Curated skill profile for one target job role.
    """

    name: str
    required_skills: Tuple[str, ...]
    preferred_skills: Tuple[str, ...] = ()
    description: str = ""


# ------------------------------------------------------------------
# JOB ROLE RECOMMENDATION RESULT
# ------------------------------------------------------------------


@dataclass
class JobRoleRecommendation:
    """
    Stores the recommendation result for one job role.
    """

    role: str
    alignment: str
    score: float
    matched_skills: List[str] = field(default_factory=list)
    missing_skills: List[str] = field(default_factory=list)
    preferred_matched_skills: List[str] = field(
        default_factory=list
    )
    category_coverage: Dict[str, float] = field(
        default_factory=dict
    )
    rationale: str = ""


@dataclass
class JobRoleRecommendationResult:
    """
    Stores the complete resume-to-job-role recommendation result.
    """

    success: bool
    resume_skills: List[str] = field(default_factory=list)
    recommendations: List[JobRoleRecommendation] = field(
        default_factory=list
    )
    message: str = ""


# ------------------------------------------------------------------
# JOB ROLE CATALOG
# ------------------------------------------------------------------

# These profiles are application-design profiles.
# They are not labor-market statistics or official hiring standards.

JOB_ROLE_PROFILES: Tuple[JobRoleProfile, ...] = (
    JobRoleProfile(
        name="Python Developer",
        required_skills=(
            "Python",
            "SQL",
            "Git",
            "REST API",
        ),
        preferred_skills=(
            "FastAPI",
            "Django",
            "Flask",
            "PostgreSQL",
            "Docker",
        ),
        description=(
            "Builds backend or application software using Python."
        ),
    ),
    JobRoleProfile(
        name="Data Analyst",
        required_skills=(
            "Python",
            "SQL",
            "Pandas",
            "Data Analysis",
        ),
        preferred_skills=(
            "NumPy",
            "Matplotlib",
            "Power BI",
            "Excel",
            "Tableau",
        ),
        description=(
            "Analyzes data and communicates actionable findings."
        ),
    ),
    JobRoleProfile(
        name="Machine Learning Engineer",
        required_skills=(
            "Python",
            "Machine Learning",
            "NumPy",
            "Pandas",
            "scikit-learn",
        ),
        preferred_skills=(
            "PyTorch",
            "TensorFlow",
            "Docker",
            "REST API",
            "Git",
        ),
        description=(
            "Develops and integrates machine-learning systems."
        ),
    ),
    JobRoleProfile(
        name="Data Scientist",
        required_skills=(
            "Python",
            "Machine Learning",
            "Pandas",
            "NumPy",
            "Data Science",
        ),
        preferred_skills=(
            "scikit-learn",
            "SQL",
            "Matplotlib",
            "TensorFlow",
            "PyTorch",
        ),
        description=(
            "Uses statistics, data analysis, and machine learning "
            "to solve problems."
        ),
    ),
    JobRoleProfile(
        name="AI Engineer",
        required_skills=(
            "Python",
            "Artificial Intelligence",
            "Machine Learning",
            "Git",
        ),
        preferred_skills=(
            "PyTorch",
            "TensorFlow",
            "Computer Vision",
            "NLP",
            "REST API",
        ),
        description=(
            "Builds AI-powered applications and machine-learning "
            "solutions."
        ),
    ),
    JobRoleProfile(
        name="Generative AI / LLM Engineer",
        required_skills=(
            "Python",
            "Generative AI",
            "Large Language Models",
            "NLP",
        ),
        preferred_skills=(
            "LLM",
            "RAG",
            "LangChain",
            "Hugging Face",
            "Transformers",
            "REST API",
        ),
        description=(
            "Builds applications around generative AI and "
            "language models."
        ),
    ),
    JobRoleProfile(
        name="Backend Developer",
        required_skills=(
            "Python",
            "SQL",
            "REST API",
            "Git",
        ),
        preferred_skills=(
            "FastAPI",
            "Django",
            "Flask",
            "PostgreSQL",
            "Docker",
            "Microservices",
        ),
        description=(
            "Develops server-side services, APIs, and backend systems."
        ),
    ),
    JobRoleProfile(
        name="Software Engineer",
        required_skills=(
            "Python",
            "Git",
            "Data Structures",
            "Algorithms",
            "Software Development",
        ),
        preferred_skills=(
            "SQL",
            "REST API",
            "Object-Oriented Programming",
            "Docker",
            "Unit Testing",
        ),
        description=(
            "Develops and maintains general-purpose software systems."
        ),
    ),
)


# ------------------------------------------------------------------
# INTERNAL HELPERS
# ------------------------------------------------------------------


def _canonicalize_skill(skill: str) -> str:
    """
    Return the canonical representation of a skill.
    """

    normalized = " ".join(
        skill.strip().lower().split()
    )

    if not normalized:
        return ""

    return SKILL_ALIASES.get(
        normalized,
        skill.strip(),
    )


def _normalized_skill_set(
    skills: Sequence[str] | None,
) -> Dict[str, str]:
    """
    Create a normalized skill lookup dictionary.
    """

    result: Dict[str, str] = {}

    if not skills:
        return result

    for skill in skills:
        canonical = _canonicalize_skill(skill)

        if not canonical:
            continue

        result.setdefault(
            canonical.lower(),
            canonical,
        )

    return result


def _coverage(
    resume_skills: Dict[str, str],
    target_skills: Sequence[str],
) -> Tuple[List[str], List[str]]:
    """
    Split target skills into matched and missing skills.
    """

    matched: List[str] = []
    missing: List[str] = []

    for skill in target_skills:
        canonical = _canonicalize_skill(skill)

        if not canonical:
            continue

        if canonical.lower() in resume_skills:
            matched.append(canonical)
        else:
            missing.append(canonical)

    return matched, missing


def _alignment(score: float) -> str:
    """
    Convert a numeric alignment score into a descriptive band.
    """

    if score >= 75:
        return "High"

    if score >= 50:
        return "Moderate"

    return "Developing"


def _category_coverage(
    resume_skills: Sequence[str],
    required_skills: Sequence[str],
) -> Dict[str, float]:
    """
    Calculate required-skill coverage grouped by skill category.
    """

    categories = categorize_skills(
        list(resume_skills)
    )

    resume_by_category = {
        category: {
            skill.lower()
            for skill in skills
        }
        for category, skills in categories.items()
    }

    result: Dict[str, float] = {}

    required_categories = categorize_skills(
        list(required_skills)
    )

    for category, skills in required_categories.items():
        if not skills:
            continue

        matched = sum(
            1
            for skill in skills
            if skill.lower()
            in resume_by_category.get(
                category,
                set(),
            )
        )

        result[category] = round(
            (matched / len(skills)) * 100,
            2,
        )

    return result


# ------------------------------------------------------------------
# MAIN RECOMMENDATION ENGINE
# ------------------------------------------------------------------


def recommend_job_roles(
    skills: Sequence[str] | None,
    *,
    top_n: int = 5,
) -> JobRoleRecommendationResult:
    """
    Recommend job roles from an extracted resume skill list.

    The score uses:

    - 80% required/core skill coverage
    - 20% preferred skill coverage

    This score is an application-specific skill-alignment score.
    It is not a probability of employment or a hiring prediction.

    Parameters
    ----------
    skills:
        Resume skills, preferably obtained from extract_skills()
        or parse_resume().

    top_n:
        Maximum number of recommendations to return.

    Returns
    -------
    JobRoleRecommendationResult
        Deterministic job-role recommendations.
    """

    if not skills:
        return JobRoleRecommendationResult(
            success=False,
            message="Resume skills are empty.",
        )

    if top_n <= 0:
        return JobRoleRecommendationResult(
            success=False,
            message="top_n must be greater than 0.",
        )

    resume_skills = _normalized_skill_set(skills)

    recommendations: List[
        JobRoleRecommendation
    ] = []

    for profile in JOB_ROLE_PROFILES:

        matched_required, missing_required = _coverage(
            resume_skills,
            profile.required_skills,
        )

        matched_preferred, _ = _coverage(
            resume_skills,
            profile.preferred_skills,
        )

        required_coverage = (
            len(matched_required)
            / len(profile.required_skills)
            if profile.required_skills
            else 0.0
        )

        preferred_coverage = (
            len(matched_preferred)
            / len(profile.preferred_skills)
            if profile.preferred_skills
            else 0.0
        )

        score = round(
            (
                (required_coverage * 0.80)
                + (preferred_coverage * 0.20)
            )
            * 100,
            2,
        )

        category_coverage = _category_coverage(
            list(resume_skills.values()),
            profile.required_skills,
        )

        if matched_required:
            rationale = (
                f"Matches {len(matched_required)} of "
                f"{len(profile.required_skills)} core skills"
            )

            if matched_preferred:
                rationale += (
                    f" and {len(matched_preferred)} "
                    "preferred skills."
                )
            else:
                rationale += "."

        else:
            rationale = (
                "No core skills from this role profile "
                "were detected."
            )

        recommendations.append(
            JobRoleRecommendation(
                role=profile.name,
                alignment=_alignment(score),
                score=score,
                matched_skills=matched_required,
                missing_skills=missing_required,
                preferred_matched_skills=matched_preferred,
                category_coverage=category_coverage,
                rationale=rationale,
            )
        )

    # Do not display roles with zero skill overlap.
    recommendations = [
        recommendation
        for recommendation in recommendations
        if recommendation.score > 0
    ]

    # Highest skill alignment first.
    # Ties are resolved deterministically.
    recommendations.sort(
        key=lambda item: (
            -item.score,
            -len(item.matched_skills),
            item.role.lower(),
        )
    )

    limited_recommendations = recommendations[:top_n]

    return JobRoleRecommendationResult(
        success=True,
        resume_skills=list(
            resume_skills.values()
        ),
        recommendations=limited_recommendations,
        message=(
            f"Generated {len(limited_recommendations)} "
            "job-role recommendations from the "
            "resume skill profile."
        ),
    )


# ------------------------------------------------------------------
# RESUME TEXT CONVENIENCE FUNCTION
# ------------------------------------------------------------------


def recommend_job_roles_from_resume(
    resume_text: str | None,
    *,
    top_n: int = 5,
) -> JobRoleRecommendationResult:
    """
    Extract skills from resume text and recommend job roles.
    """

    if not resume_text or not resume_text.strip():
        return JobRoleRecommendationResult(
            success=False,
            message="Resume text is empty.",
        )

    skills = extract_skills(resume_text)

    if not skills:
        return JobRoleRecommendationResult(
            success=False,
            resume_skills=[],
            message=(
                "No recognized skills were found "
                "in the resume."
            ),
        )

    return recommend_job_roles(
        skills,
        top_n=top_n,
    )