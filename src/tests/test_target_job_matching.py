from src.recommendations.skill_recommender import (
    TargetJobMatchResult,
    match_resume_to_target_job,
)


def test_target_job_match_identifies_matched_and_missing_skills():
    resume_text = """
    Python developer with experience in Python, SQL,
    Pandas, Git, and REST API development.
    """

    job_description = """
    We are looking for a Python developer with Python,
    SQL, Pandas, Docker, and REST API experience.
    """

    result = match_resume_to_target_job(
        resume_text,
        job_description,
    )

    assert result.success is True

    assert "Python" in result.resume_skills
    assert "SQL" in result.resume_skills

    assert "Docker" in result.job_skills

    assert "Python" in result.matched_skills
    assert "SQL" in result.matched_skills
    assert "Pandas" in result.matched_skills
    assert "REST API" in result.matched_skills

    assert "Docker" in result.missing_skills

    assert result.skill_match_percentage > 0
    assert result.skill_match_percentage < 100


def test_target_job_match_supports_skill_aliases():
    resume_text = """
    Python developer with machine learning,
    natural language processing, and PostgreSQL experience.
    """

    job_description = """
    Required skills:
    Python, ML, NLP, Postgres
    """

    result = match_resume_to_target_job(
        resume_text,
        job_description,
    )

    assert result.success is True

    assert "Machine Learning" in result.matched_skills
    assert "NLP" in result.matched_skills
    assert "PostgreSQL" in result.matched_skills

    assert result.missing_skills == []


def test_target_job_match_identifies_extra_resume_skills():
    resume_text = """
    Python, Java, SQL, Docker, and Git.
    """

    job_description = """
    Required skills:
    Python, SQL, Git
    """

    result = match_resume_to_target_job(
        resume_text,
        job_description,
    )

    assert result.success is True

    assert "Python" in result.matched_skills
    assert "SQL" in result.matched_skills
    assert "Git" in result.matched_skills

    assert "Java" in result.extra_resume_skills
    assert "Docker" in result.extra_resume_skills


def test_target_job_match_empty_job_description():
    resume_text = """
    Python, SQL, and Git developer.
    """

    result = match_resume_to_target_job(
        resume_text,
        "",
    )

    assert result.success is False
    assert result.skill_match_percentage == 0.0


def test_target_job_match_empty_resume():
    job_description = """
    Required skills:
    Python, SQL, and Git.
    """

    result = match_resume_to_target_job(
        "",
        job_description,
    )

    assert result.success is False
    assert result.resume_skills == []


def test_target_job_match_requires_recognized_job_skills():
    resume_text = """
    Python developer with SQL and Git experience.
    """

    job_description = """
    We are looking for someone with excellent
    creativity and enthusiasm.
    """

    result = match_resume_to_target_job(
        resume_text,
        job_description,
    )

    assert result.success is False
    assert result.job_skills == []