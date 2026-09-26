from __future__ import annotations

from src.matching.match_pipeline import (
    _parse_duration_years,
    estimate_resume_experience_years,
    analyze_resume_against_job,
)
from src.matching.semantic_matcher import SemanticMatchResult
from src.nlp.resume_parser import ResumeExperience


def test_parse_duration_years_explicit_duration() -> None:
    assert _parse_duration_years("2 years") == 2.0
    assert _parse_duration_years("3+ years") == 3.0


def test_parse_duration_years_year_range() -> None:
    assert _parse_duration_years("2022 - 2024") == 2.0


def test_parse_duration_years_month_range() -> None:
    assert _parse_duration_years(
        "Jan 2023 - Jan 2024"
    ) == 1.0


def test_estimate_resume_experience_years() -> None:
    experience = [
        ResumeExperience(
            job_title="Python Developer",
            company="ABC",
            duration="2022 - 2024",
        ),
        ResumeExperience(
            job_title="Intern",
            company="XYZ",
            duration="6 months",
        ),
    ]

    assert estimate_resume_experience_years(
        experience
    ) == 2.0


def test_estimate_resume_experience_without_duration() -> None:
    experience = [
        ResumeExperience(
            job_title="Python Developer",
            company="ABC",
            duration="",
            details="Worked for 2 years on Python applications.",
        ),
    ]

    assert estimate_resume_experience_years(
        experience
    ) == 2.0


def test_full_pipeline(
    monkeypatch,
) -> None:
    fake_semantic_result = SemanticMatchResult(
        similarity_score=0.80,
        similarity_percentage=80.0,
        model_name="test-model",
        success=True,
        message="Test semantic comparison completed.",
    )

    monkeypatch.setattr(
        "src.matching.score_calculator.compare_texts",
        lambda **kwargs: fake_semantic_result,
    )

    resume_text = """
    John Doe

    Skills
    Python
    SQL
    Git

    Experience
    Software Engineer
    ABC Technologies
    2022 - 2024
    Developed Python applications and REST APIs.

    Education
    B.Tech - ABC University - 2018 - 2022

    Projects
    Resume Analyzer
    Built using Python and SQL.
    """

    job_description = """
    We are looking for a Python Developer.

    Requirements:
    Python
    SQL
    Git
    REST API

    2 years of experience.

    Bachelor's degree in computer science or related field.
    """

    result = analyze_resume_against_job(
        resume_text=resume_text,
        job_description=job_description,
    )

    assert result.resume_parse.success is True
    assert result.job_analysis.success is True
    assert result.match_score is not None

    assert result.match_score.skills_score >= 0.0
    assert result.match_score.experience_score >= 0.0
    assert result.match_score.education_score >= 0.0
    assert result.match_score.projects_score >= 0.0
    assert result.match_score.semantic_score == 80.0

    assert 0.0 <= result.match_score.final_score <= 100.0