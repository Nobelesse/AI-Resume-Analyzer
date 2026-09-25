"""
Deterministic Job Role Recommendation and Target Job Matching Engine
--------------------------------------------------------------------

Provides two related capabilities:

1. Recommend suitable predefined job roles from a resume skill profile.
2. Compare a resume directly against a user-provided target job
   description and identify matched and missing skills.

All processing is local and deterministic. No external API, LLM,
database, or additional dependency is required.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Sequence, Tuple

from src.job.job_analyzer import (
    SKILL_ALIASES,
    analyze_job_description,
)
from src.matching.keyword_matcher import (
    match_skills,
    normalize_term,
)
from src.nlp.skill_extractor import (
    categorize_skills,
    extract_skills,
)


# ------------------------------------------------------------------
# JOB ROLE PROFILES
# ------------------------------------------------------------------

@dataclass(frozen=True)
class JobRoleProfile:
    """Curated skill profile for a predefined technology role."""

    name: str
    required_skills: Tuple[str, ...]
    preferred_skills: Tuple[str, ...] = ()
    description: str = ""


@dataclass
class JobRoleRecommendation:
    """Recommendation result for one predefined job role."""

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
    """Complete result returned by the role recommendation engine."""

    success: bool
    resume_skills: List[str] = field(default_factory=list)
    recommendations: List[JobRoleRecommendation] = field(
        default_factory=list
    )
    message: str = ""


# ------------------------------------------------------------------
# TARGET JOB MATCHING RESULT
# ------------------------------------------------------------------

@dataclass
class TargetJobMatchResult:
    """
    Structured result for direct resume-to-target-job skill matching.

    The score represents skill coverage only. It is not a hiring
    probability, employment prediction, or validated assessment.
    """

    success: bool
    resume_skills: List[str] = field(default_factory=list)
    job_skills: List[str] = field(default_factory=list)
    matched_skills: List[str] = field(default_factory=list)
    missing_skills: List[str] = field(default_factory=list)
    extra_resume_skills: List[str] = field(
        default_factory=list
    )
    skill_match_percentage: float = 0.0
    job_keywords: List[str] = field(default_factory=list)
    experience_requirements: List[str] = field(
        default_factory=list
    )
    education_requirements: List[str] = field(
        default_factory=list
    )
    message: str = ""


# ------------------------------------------------------------------
# CURATED ROLE CATALOG
# ------------------------------------------------------------------

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
            "Develops Python-based applications, APIs, and "
            "backend services."
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
            "Analyzes structured data and communicates "
            "business or operational insights."
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
            "Builds, evaluates, and deploys machine learning "
            "models and pipelines."
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
            "Uses statistics, programming, and machine learning "
            "to extract insights from data."
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
            "Develops artificial intelligence systems and "
            "machine learning applications."
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
            "Builds applications using generative AI, "
            "large language models, and related NLP systems."
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
            "Builds server-side applications, APIs, and "
            "backend infrastructure."
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
            "Designs, implements, tests, and maintains "
            "software systems."
        ),
    ),
)


# ------------------------------------------------------------------
# SKILL NORMALIZATION
# ------------------------------------------------------------------

def _canonicalize_skill(skill: str) -> str:
    """
    Convert a skill or alias to its canonical form.

    This helper is used by the predefined role recommender.
    Direct target-job matching is delegated to keyword_matcher,
    which provides its own canonical comparison layer.
    """
    if not isinstance(skill, str):
        return ""

    normalized = " ".join(
        skill.strip().lower().split()
    )

    if not normalized:
        return ""

    if normalized in SKILL_ALIASES:
        return SKILL_ALIASES[normalized]

    return skill.strip()


def _normalized_skill_set(
    skills: Sequence[str] | None,
) -> Dict[str, str]:
    """
    Create a normalized lookup dictionary while preserving
    readable canonical skill names.
    """
    result: Dict[str, str] = {}

    if not skills:
        return result

    for skill in skills:
        canonical = _canonicalize_skill(skill)

        if not canonical:
            continue

        key = canonical.lower().strip()

        if key not in result:
            result[key] = canonical

    return result


# ------------------------------------------------------------------
# ROLE MATCHING HELPERS
# ------------------------------------------------------------------

def _coverage(
    resume_skills: Dict[str, str],
    target_skills: Sequence[str],
) -> tuple[List[str], List[str]]:
    """
    Return matched and missing skills for a predefined role.
    """
    matched: List[str] = []
    missing: List[str] = []

    for skill in target_skills:
        canonical = _canonicalize_skill(skill)

        if not canonical:
            continue

        key = canonical.lower().strip()

        if key in resume_skills:
            matched.append(resume_skills[key])
        else:
            missing.append(canonical)

    return matched, missing


def _alignment(score: float) -> str:
    """
    Convert a numeric role-alignment score to a descriptive label.
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
    Calculate required-skill coverage by skill category.
    """
    resume_categories = categorize_skills(
        list(resume_skills)
    )

    required_categories = categorize_skills(
        list(required_skills)
    )

    if not required_categories:
        return {}

    coverage: Dict[str, float] = {}

    for category, target_skills in required_categories.items():
        resume_category_skills = {
            skill.lower().strip()
            for skill in resume_categories.get(
                category,
                [],
            )
        }

        if not target_skills:
            continue

        matched_count = sum(
            1
            for skill in target_skills
            if skill.lower().strip()
            in resume_category_skills
        )

        coverage[category] = round(
            (matched_count / len(target_skills))
            * 100,
            2,
        )

    return coverage


# ------------------------------------------------------------------
# PREDEFINED ROLE RECOMMENDATION
# ------------------------------------------------------------------

def recommend_job_roles(
    skills: Sequence[str] | None,
    *,
    top_n: int = 5,
) -> JobRoleRecommendationResult:
    """
    Recommend predefined job roles from a resume skill profile.

    Scoring model
    -------------
    Required skills:
        80%

    Preferred skills:
        20%

    This is an application-specific skill-alignment score. It is not
    an employment probability or hiring prediction.
    """
    if top_n <= 0:
        return JobRoleRecommendationResult(
            success=False,
            message="top_n must be greater than 0.",
        )

    if not skills:
        return JobRoleRecommendationResult(
            success=False,
            message="Resume skills are empty.",
        )

    resume_skill_lookup = _normalized_skill_set(
        skills
    )

    if not resume_skill_lookup:
        return JobRoleRecommendationResult(
            success=False,
            message="No usable resume skills were provided.",
        )

    recommendations: List[
        JobRoleRecommendation
    ] = []

    for profile in JOB_ROLE_PROFILES:
        matched_required, missing_required = _coverage(
            resume_skill_lookup,
            profile.required_skills,
        )

        matched_preferred, _ = _coverage(
            resume_skill_lookup,
            profile.preferred_skills,
        )

        required_count = len(
            profile.required_skills
        )

        preferred_count = len(
            profile.preferred_skills
        )

        required_score = (
            (
                len(matched_required)
                / required_count
            )
            * 100
            if required_count
            else 0.0
        )

        preferred_score = (
            (
                len(matched_preferred)
                / preferred_count
            )
            * 100
            if preferred_count
            else 0.0
        )

        score = round(
            (
                required_score * 0.80
            )
            + (
                preferred_score * 0.20
            ),
            2,
        )

        if score <= 0:
            continue

        alignment = _alignment(score)

        category_coverage = _category_coverage(
            list(resume_skill_lookup.values()),
            profile.required_skills,
        )

        if missing_required:
            rationale = (
                f"{len(matched_required)} of "
                f"{required_count} required skills "
                f"were detected. "
                f"{len(missing_required)} required "
                f"skill"
                f"{'s' if len(missing_required) != 1 else ''} "
                f"still need attention."
            )
        else:
            rationale = (
                "All required skills for this predefined "
                "role were detected in the resume."
            )

        recommendations.append(
            JobRoleRecommendation(
                role=profile.name,
                alignment=alignment,
                score=score,
                matched_skills=matched_required,
                missing_skills=missing_required,
                preferred_matched_skills=matched_preferred,
                category_coverage=category_coverage,
                rationale=rationale,
            )
        )

    recommendations.sort(
        key=lambda item: (
            -item.score,
            -len(item.matched_skills),
            item.role.lower(),
        )
    )

    recommendations = recommendations[:top_n]

    return JobRoleRecommendationResult(
        success=True,
        resume_skills=list(
            resume_skill_lookup.values()
        ),
        recommendations=recommendations,
        message=(
            f"Identified {len(recommendations)} "
            f"suitable role"
            f"{'s' if len(recommendations) != 1 else ''} "
            "from the detected resume skills."
        ),
    )


def recommend_job_roles_from_resume(
    resume_text: str | None,
    *,
    top_n: int = 5,
) -> JobRoleRecommendationResult:
    """
    Extract skills from resume text and recommend predefined roles.
    """
    if not isinstance(resume_text, str):
        return JobRoleRecommendationResult(
            success=False,
            message="Resume text is empty.",
        )

    if not resume_text.strip():
        return JobRoleRecommendationResult(
            success=False,
            message="Resume text is empty.",
        )

    resume_skills = extract_skills(
        resume_text
    )

    if not resume_skills:
        return JobRoleRecommendationResult(
            success=False,
            message=(
                "No recognized skills were found "
                "in the resume."
            ),
        )

    return recommend_job_roles(
        resume_skills,
        top_n=top_n,
    )


# ------------------------------------------------------------------
# TARGET JOB MATCHING
# ------------------------------------------------------------------

def _restore_canonical_match_names(
    matched_items: Sequence[str],
    canonical_items: Sequence[str],
) -> List[str]:
    """
    Restore canonical display names after keyword matching.

    keyword_matcher intentionally normalizes display strings for
    generic matching. The target-job UI, however, should display
    the canonical names produced by the project's skill analyzer.

    Example:
        "Nlp"       -> "NLP"
        "Rest Api"  -> "REST API"
        "Postgresql"-> "PostgreSQL"
    """
    matched_normalized = {
        normalize_term(item)
        for item in matched_items
    }

    result: List[str] = []
    seen = set()

    for item in canonical_items:
        normalized = normalize_term(item)

        if (
            normalized in matched_normalized
            and normalized not in seen
        ):
            result.append(item)
            seen.add(normalized)

    return result


def _restore_canonical_missing_names(
    missing_items: Sequence[str],
    canonical_items: Sequence[str],
) -> List[str]:
    """
    Restore canonical names for missing target-job skills.
    """
    missing_normalized = {
        normalize_term(item)
        for item in missing_items
    }

    result: List[str] = []
    seen = set()

    for item in canonical_items:
        normalized = normalize_term(item)

        if (
            normalized in missing_normalized
            and normalized not in seen
        ):
            result.append(item)
            seen.add(normalized)

    return result


def _restore_canonical_extra_resume_names(
    extra_items: Sequence[str],
    resume_skills: Sequence[str],
) -> List[str]:
    """
    Restore canonical names for resume-only skills.
    """
    extra_normalized = {
        normalize_term(item)
        for item in extra_items
    }

    result: List[str] = []
    seen = set()

    for item in resume_skills:
        normalized = normalize_term(item)

        if (
            normalized in extra_normalized
            and normalized not in seen
        ):
            result.append(item)
            seen.add(normalized)

    return result


def match_resume_to_target_job(
    resume_text: str | None,
    job_description: str | None,
) -> TargetJobMatchResult:
    """
    Compare a resume directly against a target job description.

    The job description is analyzed with the existing job analyzer.
    Resume skills are extracted with the existing resume skill
    extractor. Skill comparison is delegated to the existing
    keyword matching engine so alias normalization remains
    consistent with the project's matching tests.

    The returned percentage represents the percentage of detected
    target-job skills also detected in the resume.
    """
    if not isinstance(resume_text, str):
        return TargetJobMatchResult(
            success=False,
            message="Resume text is empty.",
        )

    if not resume_text.strip():
        return TargetJobMatchResult(
            success=False,
            message="Resume text is empty.",
        )

    if not isinstance(job_description, str):
        return TargetJobMatchResult(
            success=False,
            message="Target job description is empty.",
        )

    if not job_description.strip():
        return TargetJobMatchResult(
            success=False,
            message="Target job description is empty.",
        )

    resume_skills = extract_skills(
        resume_text
    )

    if not resume_skills:
        return TargetJobMatchResult(
            success=False,
            message=(
                "No recognized skills were found "
                "in the resume."
            ),
        )

    job_analysis = analyze_job_description(
        job_description
    )

    if not job_analysis.success:
        return TargetJobMatchResult(
            success=False,
            resume_skills=resume_skills,
            message=(
                job_analysis.message
                or "Target job analysis failed."
            ),
        )

    job_skills = job_analysis.skills

    if not job_skills:
        return TargetJobMatchResult(
            success=False,
            resume_skills=resume_skills,
            job_keywords=job_analysis.keywords,
            experience_requirements=(
                job_analysis.experience_requirements
            ),
            education_requirements=(
                job_analysis.education_requirements
            ),
            message=(
                "No recognized skills were found "
                "in the target job description."
            ),
        )

    # --------------------------------------------------------------
    # Existing matching engine performs the actual comparison.
    # --------------------------------------------------------------

    skill_match = match_skills(
        resume_skills=resume_skills,
        job_skills=job_skills,
    )

    # --------------------------------------------------------------
    # Restore canonical names for UI/test output.
    # --------------------------------------------------------------

    matched_skills = (
        _restore_canonical_match_names(
            skill_match.matched_items,
            job_skills,
        )
    )

    missing_skills = (
        _restore_canonical_missing_names(
            skill_match.missing_items,
            job_skills,
        )
    )

    extra_resume_skills = (
        _restore_canonical_extra_resume_names(
            skill_match.extra_items,
            resume_skills,
        )
    )

    return TargetJobMatchResult(
        success=True,
        resume_skills=resume_skills,
        job_skills=job_skills,
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        extra_resume_skills=extra_resume_skills,
        skill_match_percentage=(
            skill_match.match_percentage
        ),
        job_keywords=job_analysis.keywords,
        experience_requirements=(
            job_analysis.experience_requirements
        ),
        education_requirements=(
            job_analysis.education_requirements
        ),
        message=(
            "Resume-to-target-job skill matching "
            "completed successfully."
        ),
    )