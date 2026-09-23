"""
Resume Text Processor
---------------------

Provides deterministic text-cleaning and text-processing utilities for
resume analysis.

This module is intentionally independent from Streamlit and external
APIs so it can be reused by the resume parser, skill extractor,
tests, and future application components.
"""

from __future__ import annotations

import re
import unicodedata
from typing import List


# ------------------------------------------------------------------
# UNICODE NORMALIZATION
# ------------------------------------------------------------------

UNICODE_REPLACEMENTS = {
    "\u2018": "'",
    "\u2019": "'",
    "\u201c": '"',
    "\u201d": '"',
    "\u2013": "-",
    "\u2014": "-",
    "\u2212": "-",
    "\u2022": "-",
    "\u25cf": "-",
    "\u25aa": "-",
    "\u25e6": "-",
    "\u2043": "-",
    "\u00a0": " ",

    # Common UTF-8 mojibake sequences that may appear when PDF text
    # has been decoded incorrectly before reaching the parser.
    "â€¢": "-",
    "â—": "-",
    "â–ª": "-",
    "â—¦": "-",
    "â€£": "-",
    "âƒ": "-",
    "â€“": "-",
    "â€”": "-",
    "âˆ’": "-",
    "Â·": "-",
    "Â ": " ",
}


# ------------------------------------------------------------------
# PDF PAGE MARKERS
# ------------------------------------------------------------------

PAGE_MARKER_PATTERN = re.compile(
    r"^\s*---\s*Page\s+\d+\s*---\s*$",
    flags=re.IGNORECASE,
)


# ------------------------------------------------------------------
# BULLET PATTERNS
# ------------------------------------------------------------------

BULLET_PATTERN = re.compile(
    r"^\s*(?:[-*•●▪◦⁃]|\u00e2\u20ac\u00a2|\u00e2\u2014|\u00e2\u2013\u00aa|\u00e2\u2014\u00a6|\u00e2\u20ac\u00a3|\u00e2\u0192)\s+"
)


# ------------------------------------------------------------------
# BASIC TEXT NORMALIZATION
# ------------------------------------------------------------------

def normalize_unicode(text: str | None) -> str:
    """
    Normalize Unicode characters while preserving useful text.

    Parameters
    ----------
    text:
        Raw text.

    Returns
    -------
    str
        Unicode-normalized text.
    """

    if not isinstance(text, str) or not text:
        return ""

    normalized = unicodedata.normalize(
        "NFKC",
        text,
    )

    for source, replacement in UNICODE_REPLACEMENTS.items():
        normalized = normalized.replace(
            source,
            replacement,
        )

    return normalized


def normalize_newlines(text: str | None) -> str:
    """
    Normalize Windows, old-Mac, and mixed newline formats.
    """

    if not isinstance(text, str) or not text:
        return ""

    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    return text


def normalize_whitespace(text: str | None) -> str:
    """
    Normalize spaces and tabs without removing line structure.
    """

    if not isinstance(text, str) or not text:
        return ""

    text = re.sub(
        r"[ \t]+",
        " ",
        text,
    )

    text = re.sub(
        r" *\n *",
        "\n",
        text,
    )

    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text,
    )

    return text.strip()


# ------------------------------------------------------------------
# BULLET NORMALIZATION
# ------------------------------------------------------------------

def normalize_bullets(text: str | None) -> str:
    """
    Normalize common bullet characters to a standard dash.

    Both normal Unicode bullets and common UTF-8 mojibake
    representations are supported.

    Only bullets at the beginning of a line are modified so that
    technical content containing punctuation is preserved.
    """

    if not isinstance(text, str) or not text:
        return ""

    normalized_lines: List[str] = []

    bullet_pattern = re.compile(
        r"^\s*(?:"
        r"[-*•●▪◦⁃]"
        r"|â€¢"
        r"|â—"
        r"|â–ª"
        r"|â—¦"
        r"|â€£"
        r"|âƒ"
        r")\s+"
    )

    for line in text.splitlines():
        normalized_line = bullet_pattern.sub(
            "- ",
            line,
        )

        normalized_lines.append(
            normalized_line
        )

    return "\n".join(normalized_lines)


# ------------------------------------------------------------------
# PAGE MARKER REMOVAL
# ------------------------------------------------------------------

def remove_page_markers(text: str | None) -> str:
    """
    Remove page markers inserted by the PDF extraction layer.

    Examples
    --------
    ``--- Page 1 ---``
    ``--- Page 2 ---``
    """

    if not isinstance(text, str) or not text:
        return ""

    lines = []

    for line in text.splitlines():
        if PAGE_MARKER_PATTERN.match(line):
            continue

        lines.append(line)

    return "\n".join(lines)


# ------------------------------------------------------------------
# COMPLETE CLEANING
# ------------------------------------------------------------------

def clean_resume_text(text: str | None) -> str:
    """
    Perform the standard resume text-cleaning pipeline.

    The cleaning process:

    1. Handles invalid/empty input.
    2. Normalizes Unicode characters.
    3. Normalizes newline formats.
    4. Removes PDF page markers.
    5. Normalizes bullet characters.
    6. Normalizes spaces and blank lines.
    7. Preserves useful technical punctuation.

    Parameters
    ----------
    text:
        Raw resume text.

    Returns
    -------
    str
        Cleaned resume text.
    """

    if not isinstance(text, str) or not text.strip():
        return ""

    cleaned = normalize_unicode(text)
    cleaned = normalize_newlines(cleaned)
    cleaned = remove_page_markers(cleaned)
    cleaned = normalize_bullets(cleaned)
    cleaned = normalize_whitespace(cleaned)

    return cleaned


# ------------------------------------------------------------------
# LINE PROCESSING
# ------------------------------------------------------------------

def extract_lines(
    text: str | None,
    remove_empty: bool = True,
) -> List[str]:
    """
    Extract normalized lines from resume text.

    Parameters
    ----------
    text:
        Resume text.
    remove_empty:
        Whether empty lines should be removed.

    Returns
    -------
    list[str]
        Ordered resume lines.
    """

    cleaned = clean_resume_text(text)

    if not cleaned:
        return []

    lines = [
        line.strip()
        for line in cleaned.splitlines()
    ]

    if remove_empty:
        lines = [
            line
            for line in lines
            if line
        ]

    return lines


# ------------------------------------------------------------------
# PARAGRAPH PROCESSING
# ------------------------------------------------------------------

def extract_paragraphs(
    text: str | None,
) -> List[str]:
    """
    Extract paragraphs separated by blank lines.

    Returns
    -------
    list[str]
        Ordered non-empty paragraphs.
    """

    cleaned = clean_resume_text(text)

    if not cleaned:
        return []

    paragraphs = re.split(
        r"\n\s*\n",
        cleaned,
    )

    return [
        re.sub(
            r"\s+",
            " ",
            paragraph,
        ).strip()
        for paragraph in paragraphs
        if paragraph.strip()
    ]


# ------------------------------------------------------------------
# WORD EXTRACTION
# ------------------------------------------------------------------

def extract_words(
    text: str | None,
) -> List[str]:
    """
    Extract basic word/token candidates from resume text.

    Common technical terms such as ``C++``, ``C#``, ``Node.js``,
    ``scikit-learn``, and version-like terms are preserved where
    possible.
    """

    cleaned = clean_resume_text(text)

    if not cleaned:
        return []

    # The pattern supports common technical terms:
    #
    # C++          -> C++
    # C#           -> C#
    # Node.js      -> Node.js
    # scikit-learn -> scikit-learn
    # Python       -> Python
    # version2     -> version2
    #
    # A token begins with an alphanumeric character and may contain
    # technical punctuation such as +, #, ., or -.
    return re.findall(
        r"[A-Za-z0-9]+(?:[+#.-][A-Za-z0-9+#.-]*)*",
        cleaned,
    )


# ------------------------------------------------------------------
# TEXT STATISTICS
# ------------------------------------------------------------------

def count_words(text: str | None) -> int:
    """
    Return the number of basic word/token candidates.
    """

    return len(
        extract_words(text)
    )


def count_lines(text: str | None) -> int:
    """
    Return the number of non-empty normalized lines.
    """

    return len(
        extract_lines(text)
    )


def count_characters(text: str | None) -> int:
    """
    Return the number of characters in cleaned resume text.
    """

    return len(
        clean_resume_text(text)
    )