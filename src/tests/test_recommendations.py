"""
Tests for the deterministic resume-to-job-role recommendation engine.
"""

from src.recommendations.skill_recommender import (
    JOB_ROLE_PROFILES,
    recommend_job_roles,
    recommend_job_roles_from_resume,
)


def test_job_role_catalog_is_available():
    assert JOB_ROLE_PROFILES

    assert any(
        profile.name == "Python Developer"
        for profile in JOB_ROLE_PROFILES
    )


def test_recommend_job_roles_matches_python_profile():
    result = recommend_job_roles(
        [
            "Python",
            "SQL",
            "Git",
            "REST API",
            "FastAPI",
            "PostgreSQL",
            "Docker",
        ],
        top_n=5,
    )

    assert result.success is True
    assert result.resume_skills
    assert result.recommendations

    python_role = next(
        item
        for item in result.recommendations
        if item.role == "Python Developer"
    )

    assert python_role.score > 0

    assert python_role.alignment in {
        "High",
        "Moderate",
        "Developing",
    }

    assert "Python" in python_role.matched_skills
    assert "SQL" in python_role.matched_skills
    assert "Git" in python_role.matched_skills
    assert "REST API" in python_role.matched_skills

    assert (
        "FastAPI"
        in python_role.preferred_matched_skills
    )

    assert python_role.missing_skills == []


def test_recommend_job_roles_identifies_missing_core_skills():
    result = recommend_job_roles(
        [
            "Python",
            "Pandas",
            "NumPy",
        ],
        top_n=5,
    )

    assert result.success is True

    ml_role = next(
        item
        for item in result.recommendations
        if item.role == "Machine Learning Engineer"
    )

    assert "Python" in ml_role.matched_skills
    assert "Pandas" in ml_role.matched_skills
    assert "NumPy" in ml_role.matched_skills

    assert (
        "Machine Learning"
        in ml_role.missing_skills
    )

    assert (
        "scikit-learn"
        in ml_role.missing_skills
    )


def test_recommend_job_roles_supports_skill_aliases():
    result = recommend_job_roles(
        [
            "Python",
            "ML",
            "Postgres",
            "REST APIs",
            "Git",
        ],
        top_n=5,
    )

    assert result.success is True

    python_role = next(
        item
        for item in result.recommendations
        if item.role == "Python Developer"
    )

    assert "REST API" in python_role.matched_skills

    assert (
        "PostgreSQL"
        in python_role.preferred_matched_skills
    )

    ml_role = next(
        item
        for item in result.recommendations
        if item.role == "Machine Learning Engineer"
    )

    assert (
        "Machine Learning"
        in ml_role.matched_skills
    )


def test_recommend_job_roles_from_resume_extracts_skills():
    resume_text = """
    Python developer with Machine Learning experience.
    Built APIs using FastAPI and worked with PostgreSQL.
    Used Docker and Git for deployment.
    """

    result = recommend_job_roles_from_resume(
        resume_text,
        top_n=3,
    )

    assert result.success is True

    assert "Python" in result.resume_skills
    assert "Machine Learning" in result.resume_skills
    assert "FastAPI" in result.resume_skills
    assert "PostgreSQL" in result.resume_skills
    assert "Docker" in result.resume_skills
    assert "Git" in result.resume_skills

    assert len(result.recommendations) <= 3


def test_recommend_job_roles_respects_top_n():
    result = recommend_job_roles(
        [
            "Python",
            "SQL",
            "Git",
        ],
        top_n=2,
    )

    assert result.success is True
    assert len(result.recommendations) <= 2


def test_recommend_job_roles_empty_input():
    result = recommend_job_roles([])

    assert result.success is False
    assert result.resume_skills == []
    assert result.recommendations == []
    assert (
        result.message
        == "Resume skills are empty."
    )


def test_recommend_job_roles_invalid_top_n():
    result = recommend_job_roles(
        ["Python"],
        top_n=0,
    )

    assert result.success is False
    assert (
        result.message
        == "top_n must be greater than 0."
    )


def test_recommend_job_roles_from_empty_resume():
    result = recommend_job_roles_from_resume("")

    assert result.success is False
    assert result.resume_skills == []
    assert result.recommendations == []

    assert (
        result.message
        == "Resume text is empty."
    )


def test_recommend_job_roles_from_resume_without_recognized_skills():
    result = recommend_job_roles_from_resume(
        "Experienced professional seeking a new opportunity."
    )

    assert result.success is False
    assert result.resume_skills == []
    assert result.recommendations == []

    assert (
        result.message
        == "No recognized skills were found "
        "in the resume."
    )