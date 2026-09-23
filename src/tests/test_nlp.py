"""
Tests for the Resume NLP text processor.
"""

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