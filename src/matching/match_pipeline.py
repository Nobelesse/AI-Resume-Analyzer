"""
Resume-to-Job Match Pipeline
----------------------------

Connects the resume parser, job-description analyzer, and match-score
calculator into one deterministic application-level pipeline.

This module does not perform hiring decisions. It only calculates a
technical resume-to-job matching score from the application's defined
components and weights.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from typing import List, Optional, Sequence

from src.job.job_analyzer import (
    JobDescriptionAnalysis,
    analyze_job_description,
)
from src.matching.score_calculator import (
    MatchScoreResult,
    calculate_match_score,
)
from src.nlp.resume_parser import (
    ResumeEducation,
    ResumeExperience,
    ResumeParseResult,
    ResumeProject,
    parse_resume,
)


# ------------------------------------------------------------------
# RESULT DATA CLASS
# ------------------------------------------------------------------

@dataclass
class ResumeJobMatchResult:
    """Complete result returned by the resume-to-job pipeline."""

    success: bool

    resume_parse: ResumeParseResult
    job_analysis: JobDescriptionAnalysis
    match_score: Optional[MatchScoreResult] = None

    resume_experience_years: float = 0.0

    message: str = ""


# ------------------------------------------------------------------
# TEXT HELPERS
# ------------------------------------------------------------------

def _normalize_text(value: str | None) -> str:
    """Normalize whitespace for safe text comparison."""
    if not isinstance(value, str):
        return ""

    return " ".join(value.split())


# ------------------------------------------------------------------
# EXPERIENCE PARSING
# ------------------------------------------------------------------

_MONTHS = {
    "jan": 1,
    "january": 1,
    "feb": 2,
    "february": 2,
    "mar": 3,
    "march": 3,
    "apr": 4,
    "april": 4,
    "may": 5,
    "jun": 6,
    "june": 6,
    "jul": 7,
    "july": 7,
    "aug": 8,
    "august": 8,
    "sep": 9,
    "sept": 9,
    "september": 9,
    "oct": 10,
    "october": 10,
    "nov": 11,
    "november": 11,
    "dec": 12,
    "december": 12,
}


def _parse_month(value: str) -> Optional[int]:
    """Convert a month name or abbreviation to its numeric value."""
    return _MONTHS.get(
        value.strip().lower()
    )


def _parse_date_point(
    month: str,
    year: str,
) -> Optional[tuple[int, int]]:
    """Parse a month/year pair."""
    try:
        parsed_year = int(year)
    except (TypeError, ValueError):
        return None

    parsed_month = _parse_month(month)

    if parsed_month is None:
        return None

    return parsed_year, parsed_month


def _parse_duration_years(
    duration: str | None,
) -> float:
    """
    Convert a resume experience duration into years.

    Supported examples:
        2 years
        3+ years
        2023 - 2025
        Jan 2023 - Dec 2024
        Jan 2023 - Present
    """
    text = _normalize_text(duration)

    if not text:
        return 0.0

    # --------------------------------------------------------------
    # Explicit duration such as "2 years".
    # --------------------------------------------------------------

    explicit_match = re.search(
        r"(?<!\d)(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)\b",
        text,
        flags=re.IGNORECASE,
    )

    if explicit_match:
        try:
            return max(
                0.0,
                float(explicit_match.group(1)),
            )
        except ValueError:
            return 0.0

    # --------------------------------------------------------------
    # Month/year duration.
    #
    # Capture groups:
    #   1 = start month
    #   2 = start year
    #   3 = complete end value
    #   4 = end month
    #   5 = end year
    #
    # All groups inside month_pattern are non-capturing.
    # --------------------------------------------------------------

    month_pattern = (
        r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|"
        r"May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|"
        r"Sep(?:t(?:ember)?)?|Oct(?:ober)?|"
        r"Nov(?:ember)?|Dec(?:ember)?)"
    )

    month_range = re.search(
        rf"\b({month_pattern})\s+(\d{{4}})"
        rf"\s*[-–—]\s*"
        rf"(Present|Current|({month_pattern})\s+(\d{{4}}))\b",
        text,
        flags=re.IGNORECASE,
    )

    if month_range:
        start_month_name = month_range.group(1)
        start_year_text = month_range.group(2)
        end_value = month_range.group(3).strip()

        try:
            start_year = int(
                start_year_text
            )
        except ValueError:
            return 0.0

        start_month = _parse_month(
            start_month_name
        )

        if start_month is None:
            return 0.0

        if end_value.lower() in {
            "present",
            "current",
        }:
            current = date.today()

            end_year = current.year
            end_month = current.month

        else:
            end_month_name = month_range.group(4)
            end_year_text = month_range.group(5)

            end_month = _parse_month(
                end_month_name
            )

            try:
                end_year = int(
                    end_year_text
                )
            except (TypeError, ValueError):
                return 0.0

            if end_month is None:
                return 0.0

        total_months = (
            (end_year - start_year) * 12
            + (end_month - start_month)
        )

        if total_months < 0:
            return 0.0

        return round(
            total_months / 12.0,
            2,
        )

    # --------------------------------------------------------------
    # Year/year duration.
    # --------------------------------------------------------------

    year_range = re.search(
        r"\b((?:19|20)\d{2})\s*[-–—]\s*"
        r"(Present|Current|((?:19|20)\d{2}))\b",
        text,
        flags=re.IGNORECASE,
    )

    if year_range:
        start_year = int(
            year_range.group(1)
        )

        end_value = year_range.group(2)

        if end_value.lower() in {
            "present",
            "current",
        }:
            end_year = date.today().year

        else:
            end_year = int(
                year_range.group(3)
            )

        if end_year < start_year:
            return 0.0

        return float(
            end_year - start_year
        )

    return 0.0


def estimate_resume_experience_years(
    experience: Sequence[ResumeExperience] | None,
) -> float:
    """
    Estimate total resume experience in years from parsed experience
    entries.

    The estimate is based only on durations detected in the resume.
    Entries without recognizable durations contribute zero.
    """
    if not experience:
        return 0.0

    total_years = 0.0

    for entry in experience:
        if not isinstance(
            entry,
            ResumeExperience,
        ):
            continue

        duration_years = _parse_duration_years(
            entry.duration
        )

        if duration_years <= 0.0:
            duration_years = _parse_duration_years(
                entry.details
            )

        total_years += duration_years

    return round(
        max(0.0, total_years),
        2,
    )


# ------------------------------------------------------------------
# RESUME COMPONENT BUILDERS
# ------------------------------------------------------------------

def _build_resume_education_items(
    education: Sequence[ResumeEducation] | None,
) -> List[str]:
    """
    Convert structured education entries into strings accepted by the
    scoring engine.
    """
    if not education:
        return []

    items: List[str] = []

    for entry in education:
        if not isinstance(
            entry,
            ResumeEducation,
        ):
            continue

        parts = [
            entry.degree,
            entry.institution,
            entry.year,
            entry.details,
        ]

        value = _normalize_text(
            " ".join(
                part
                for part in parts
                if isinstance(part, str)
                and part.strip()
            )
        )

        if value:
            items.append(value)

    return items


def _build_resume_project_text(
    projects: Sequence[ResumeProject] | None,
) -> str:
    """
    Combine structured project entries into project-related text.
    """
    if not projects:
        return ""

    parts: List[str] = []

    for project in projects:
        if not isinstance(
            project,
            ResumeProject,
        ):
            continue

        project_parts = [
            project.name,
            project.duration,
            project.details,
        ]

        value = _normalize_text(
            " ".join(
                part
                for part in project_parts
                if isinstance(part, str)
                and part.strip()
            )
        )

        if value:
            parts.append(value)

    return "\n".join(parts)


# ------------------------------------------------------------------
# MAIN PIPELINE
# ------------------------------------------------------------------

def analyze_resume_against_job(
    resume_text: str | None,
    job_description: str | None,
) -> ResumeJobMatchResult:
    """
    Run the complete resume-to-job matching pipeline.

    Steps:
        1. Parse the resume.
        2. Analyze the job description.
        3. Convert parsed resume information into scoring inputs.
        4. Calculate the weighted match score.
        5. Return all intermediate and final results together.
    """
    resume_parse = parse_resume(
        resume_text
    )

    if not resume_parse.success:
        return ResumeJobMatchResult(
            success=False,
            resume_parse=resume_parse,
            job_analysis=JobDescriptionAnalysis(
                success=False,
                original_text="",
                cleaned_text="",
                message="Job analysis was not started.",
            ),
            message=resume_parse.message,
        )

    job_analysis = analyze_job_description(
        job_description
    )

    if not job_analysis.success:
        return ResumeJobMatchResult(
            success=False,
            resume_parse=resume_parse,
            job_analysis=job_analysis,
            message=job_analysis.message,
        )

    resume_years = estimate_resume_experience_years(
        resume_parse.experience
    )

    resume_education = (
        _build_resume_education_items(
            resume_parse.education
        )
    )

    resume_project_text = (
        _build_resume_project_text(
            resume_parse.projects
        )
    )

    match_score = calculate_match_score(
        resume_skills=resume_parse.skills,
        job_skills=job_analysis.skills,
        resume_years=resume_years,
        job_experience_requirements=(
            job_analysis.experience_requirements
        ),
        resume_education=resume_education,
        job_education_requirements=(
            job_analysis.education_requirements
        ),
        resume_project_text=resume_project_text,
        job_keywords=job_analysis.keywords,
        resume_text=resume_parse.cleaned_text,
        job_description=job_analysis.cleaned_text,
    )

    return ResumeJobMatchResult(
        success=match_score.success,
        resume_parse=resume_parse,
        job_analysis=job_analysis,
        match_score=match_score,
        resume_experience_years=resume_years,
        message=match_score.message,
    )