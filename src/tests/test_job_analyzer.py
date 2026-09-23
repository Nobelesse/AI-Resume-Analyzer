"""
Tests for the Job Description Analyzer.
"""

from src.job.job_analyzer import (
    analyze_job_description,
    clean_job_description,
    extract_education_requirements,
    extract_experience_requirements,
    extract_keywords,
    extract_sections,
    extract_skills,
)


SAMPLE_JOB_DESCRIPTION = """
Software Engineer

About the Role

We are looking for a Python developer to build scalable software
applications and data-driven solutions.

Requirements

- Bachelor's degree in Computer Science or Information Technology.
- 2+ years of experience in Python and SQL.
- Experience with REST APIs and Git.
- Strong knowledge of Machine Learning and Data Analysis.
- Experience with Pandas and NumPy.

Responsibilities

- Develop Python applications.
- Work with PostgreSQL databases.
- Collaborate with the engineering team.
- Participate in Agile development.

Preferred Skills

- Docker
- AWS
- TensorFlow
"""


def test_clean_job_description():
    text = "Python   Developer\r\n\r\n\r\nSQL\tDeveloper"

    cleaned = clean_job_description(text)

    assert cleaned == "Python Developer\n\nSQL Developer"


def test_extract_sections():
    sections = extract_sections(SAMPLE_JOB_DESCRIPTION)

    assert "requirements" in sections
    assert "responsibilities" in sections
    assert "preferred" in sections

    assert "Python" in sections["requirements"]
    assert "Docker" in sections["preferred"]


def test_extract_skills():
    skills = extract_skills(SAMPLE_JOB_DESCRIPTION)

    assert "Python" in skills
    assert "SQL" in skills
    assert "REST API" in skills
    assert "Git" in skills
    assert "Machine Learning" in skills
    assert "Pandas" in skills
    assert "NumPy" in skills
    assert "PostgreSQL" in skills
    assert "Docker" in skills
    assert "AWS" in skills
    assert "TensorFlow" in skills


def test_extract_experience_requirements():
    requirements = extract_experience_requirements(
        SAMPLE_JOB_DESCRIPTION
    )

    assert any(
        "2+ years" in requirement.lower()
        for requirement in requirements
    )


def test_extract_education_requirements():
    requirements = extract_education_requirements(
        SAMPLE_JOB_DESCRIPTION
    )

    assert any(
        "bachelor" in requirement.lower()
        for requirement in requirements
    )


def test_extract_keywords():
    skills = extract_skills(SAMPLE_JOB_DESCRIPTION)

    keywords = extract_keywords(
        SAMPLE_JOB_DESCRIPTION,
        skills=skills,
    )

    assert "Python" in keywords
    assert "SQL" in keywords


def test_analyze_job_description():
    result = analyze_job_description(
        SAMPLE_JOB_DESCRIPTION
    )

    assert result.success is True
    assert result.original_text == SAMPLE_JOB_DESCRIPTION
    assert result.cleaned_text

    assert result.skills
    assert result.keywords
    assert result.experience_requirements
    assert result.education_requirements
    assert result.sections

    assert "Python" in result.skills
    assert "SQL" in result.skills


def test_empty_job_description():
    result = analyze_job_description("")

    assert result.success is False
    assert result.cleaned_text == ""
    assert result.skills == []
    assert result.keywords == []
    assert result.experience_requirements == []
    assert result.education_requirements == []
    assert "empty" in result.message.lower()