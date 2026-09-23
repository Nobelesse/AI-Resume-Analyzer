"""
Tests for the Resume NLP text processor and skill extractor.
"""

from src.nlp.skill_extractor import (
    analyze_resume_skills,
    categorize_skills,
    extract_skills,
)
from src.nlp.text_processor import (
    clean_resume_text,
    count_characters,
    count_lines,
    count_words,
    extract_lines,
    extract_paragraphs,
    extract_words,
    normalize_bullets,
    normalize_newlines,
    normalize_unicode,
    normalize_whitespace,
    remove_page_markers,
)


# ------------------------------------------------------------------
# TEXT PROCESSOR TESTS
# ------------------------------------------------------------------

def test_normalize_unicode():
    text = "Python \u2013 Machine Learning \u201cProject\u201d"

    result = normalize_unicode(text)

    assert result == 'Python - Machine Learning "Project"'


def test_normalize_newlines():
    text = "Line 1\r\nLine 2\rLine 3"

    result = normalize_newlines(text)

    assert result == "Line 1\nLine 2\nLine 3"


def test_normalize_whitespace():
    text = "Python    Developer\t\tMachine Learning\n\n\nExperience"

    result = normalize_whitespace(text)

    assert result == (
        "Python Developer Machine Learning\n\nExperience"
    )


def test_normalize_bullets():
    text = (
        "• Python development\n"
        "● Machine learning\n"
        "* Data analysis"
    )

    result = normalize_bullets(text)

    assert result == (
        "- Python development\n"
        "- Machine learning\n"
        "- Data analysis"
    )


def test_remove_page_markers():
    text = (
        "--- Page 1 ---\n"
        "Aditya Singh Rajput\n"
        "--- Page 2 ---\n"
        "Python Developer"
    )

    result = remove_page_markers(text)

    assert result == (
        "Aditya Singh Rajput\n"
        "Python Developer"
    )


def test_clean_resume_text():
    text = (
        "  Aditya Singh Rajput  \r\n"
        "\r\n"
        "• Python Developer\n"
        "--- Page 1 ---\n"
        "Python    Machine Learning"
    )

    result = clean_resume_text(text)

    assert result == (
        "Aditya Singh Rajput\n\n"
        "- Python Developer\n"
        "Python Machine Learning"
    )


def test_clean_resume_text_empty():
    assert clean_resume_text("") == ""
    assert clean_resume_text("   ") == ""
    assert clean_resume_text(None) == ""


def test_extract_lines():
    text = (
        "Aditya Singh Rajput\n"
        "\n"
        "Python Developer\n"
        "\n"
        "Machine Learning"
    )

    result = extract_lines(text)

    assert result == [
        "Aditya Singh Rajput",
        "Python Developer",
        "Machine Learning",
    ]


def test_extract_lines_keeps_empty_lines_when_requested():
    text = (
        "Name\n"
        "\n"
        "Python Developer"
    )

    result = extract_lines(
        text,
        remove_empty=False,
    )

    assert result == [
        "Name",
        "",
        "Python Developer",
    ]


def test_extract_paragraphs():
    text = (
        "Aditya Singh Rajput\n"
        "Python Developer\n"
        "\n"
        "Machine Learning specialist\n"
        "with Python experience."
    )

    result = extract_paragraphs(text)

    assert result == [
        "Aditya Singh Rajput Python Developer",
        "Machine Learning specialist with Python experience.",
    ]


def test_extract_words_preserves_technical_terms():
    text = (
        "Python C++ C# Node.js scikit-learn "
        "Machine Learning"
    )

    result = extract_words(text)

    assert "Python" in result
    assert "C++" in result
    assert "C#" in result
    assert "Node.js" in result
    assert "scikit-learn" in result


def test_extract_words_empty():
    assert extract_words("") == []
    assert extract_words(None) == []


def test_count_words():
    text = "Python Developer Machine Learning"

    assert count_words(text) == 4


def test_count_lines():
    text = (
        "Python Developer\n"
        "\n"
        "Machine Learning\n"
        "Data Analysis"
    )

    assert count_lines(text) == 3


def test_count_characters():
    text = "  Python   Developer  "

    assert count_characters(text) == len(
        "Python Developer"
    )


# ------------------------------------------------------------------
# SKILL EXTRACTION TESTS
# ------------------------------------------------------------------

def test_extract_skills_basic():
    text = (
        "Python developer with experience in "
        "Machine Learning, SQL, Git, and Docker."
    )

    result = extract_skills(text)

    assert "Python" in result
    assert "Machine Learning" in result
    assert "SQL" in result
    assert "Git" in result
    assert "Docker" in result


def test_extract_skills_aliases():
    text = (
        "Experienced in ML, AI, NLP, PostgreSQL, "
        "REST APIs, and scikit learn."
    )

    result = extract_skills(text)

    assert "Machine Learning" in result
    assert "Artificial Intelligence" in result
    assert "NLP" in result
    assert "PostgreSQL" in result
    assert "REST API" in result
    assert "scikit-learn" in result


def test_extract_skills_technical_terms():
    text = (
        "Developed applications using C++, C#, "
        "Node.js, JavaScript, and React."
    )

    result = extract_skills(text)

    assert "C++" in result
    assert "C#" in result
    assert "Node.js" in result
    assert "JavaScript" in result
    assert "React" in result


def test_extract_skills_avoids_partial_matches():
    text = (
        "This candidate knows JavaScript and "
        "JavaScript frameworks."
    )

    result = extract_skills(text)

    assert "JavaScript" in result
    assert "Java" not in result


def test_extract_skills_deduplicates_aliases():
    text = (
        "Machine Learning and ML experience. "
        "Artificial Intelligence and AI projects."
    )

    result = extract_skills(text)

    assert result.count("Machine Learning") == 1
    assert result.count("Artificial Intelligence") == 1


def test_extract_skills_empty():
    assert extract_skills("") == []
    assert extract_skills(None) == []


def test_categorize_skills():
    skills = [
        "Python",
        "Java",
        "PostgreSQL",
        "Machine Learning",
        "Docker",
        "Git",
        "REST API",
    ]

    result = categorize_skills(skills)

    assert result["programming_languages"] == [
        "Python",
        "Java",
    ]

    assert result["databases"] == [
        "PostgreSQL",
    ]

    assert result["data_ai_ml"] == [
        "Machine Learning",
    ]

    assert result["cloud_devops"] == [
        "Docker",
        "Git",
    ]

    assert result["software_engineering"] == [
        "REST API",
    ]


def test_categorize_skills_empty():
    assert categorize_skills([]) == {}
    assert categorize_skills(None) == {}


def test_analyze_resume_skills():
    text = (
        "Python developer with Machine Learning experience.\n"
        "Built APIs using FastAPI and worked with PostgreSQL.\n"
        "Used Docker and Git for deployment."
    )

    result = analyze_resume_skills(text)

    assert result.success is True
    assert result.skill_count >= 6
    assert "Python" in result.skills
    assert "Machine Learning" in result.skills
    assert "FastAPI" in result.skills
    assert "PostgreSQL" in result.skills
    assert "Docker" in result.skills
    assert "Git" in result.skills
    assert "programming_languages" in result.categories
    assert "databases" in result.categories
    assert "data_ai_ml" in result.categories
    assert "cloud_devops" in result.categories


def test_analyze_resume_skills_empty():
    result = analyze_resume_skills("")

    assert result.success is False
    assert result.skills == []
    assert result.categories == {}
    assert result.skill_count == 0
    assert result.message == "Resume text is empty."