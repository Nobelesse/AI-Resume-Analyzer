"""
Resume Parser
-------------

Provides deterministic parsing of structured information from resume
text.

This module builds on the existing text-processing and skill-extraction
modules. It does not require an external API, LLM, or additional
dependency.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from src.nlp.skill_extractor import (
    analyze_resume_skills,
)
from src.nlp.text_processor import (
    clean_resume_text,
    count_characters,
    count_lines,
    count_words,
)


# ------------------------------------------------------------------
# SECTION ALIASES
# ------------------------------------------------------------------

SECTION_ALIASES: Dict[str, tuple[str, ...]] = {
    "summary": (
        "summary",
        "professional summary",
        "profile",
        "professional profile",
        "objective",
        "career objective",
        "about me",
    ),
    "skills": (
        "skills",
        "technical skills",
        "technical skill",
        "core skills",
        "key skills",
        "skills & technologies",
        "skills and technologies",
        "technologies",
    ),
    "experience": (
        "experience",
        "work experience",
        "professional experience",
        "employment",
        "employment history",
        "work history",
        "career history",
    ),
    "education": (
        "education",
        "educational qualification",
        "educational qualifications",
        "academic qualification",
        "academic qualifications",
        "academic background",
    ),
    "projects": (
        "projects",
        "academic projects",
        "personal projects",
        "key projects",
        "project experience",
    ),
    "certifications": (
        "certifications",
        "certificates",
        "professional certifications",
        "licenses & certifications",
        "licenses and certifications",
    ),
    "achievements": (
        "achievements",
        "accomplishments",
        "awards",
        "honors",
    ),
    "languages": (
        "languages",
        "language",
        "spoken languages",
    ),
    "interests": (
        "interests",
        "hobbies",
        "hobbies & interests",
        "hobbies and interests",
    ),
}


# ------------------------------------------------------------------
# RESULT DATA CLASSES
# ------------------------------------------------------------------

@dataclass
class ResumeContactInfo:
    """Stores contact information identified in a resume."""

    name: str = ""
    email: str = ""
    phone: str = ""
    linkedin: str = ""
    github: str = ""


@dataclass
class ResumeSection:
    """Stores a detected resume section."""

    name: str
    content: str


@dataclass
class ResumeEducation:
    """Stores one education entry."""

    degree: str = ""
    institution: str = ""
    year: str = ""
    details: str = ""


@dataclass
class ResumeExperience:
    """Stores one work-experience entry."""

    job_title: str = ""
    company: str = ""
    duration: str = ""
    details: str = ""


@dataclass
class ResumeProject:
    """Stores one project entry."""

    name: str = ""
    duration: str = ""
    details: str = ""


@dataclass
class ResumeCertification:
    """Stores one certification entry."""

    name: str = ""
    issuer: str = ""
    year: str = ""


@dataclass
class ResumeStatistics:
    """Stores basic resume text statistics."""

    word_count: int = 0
    line_count: int = 0
    character_count: int = 0
    section_count: int = 0
    skill_count: int = 0


@dataclass
class ResumeParseResult:
    """
    Stores the complete structured result of resume parsing.
    """

    success: bool
    original_text: str = ""
    cleaned_text: str = ""
    contact: ResumeContactInfo = field(
        default_factory=ResumeContactInfo
    )
    summary: str = ""
    skills: List[str] = field(default_factory=list)
    skill_categories: Dict[str, List[str]] = field(
        default_factory=dict
    )
    education: List[ResumeEducation] = field(
        default_factory=list
    )
    experience: List[ResumeExperience] = field(
        default_factory=list
    )
    projects: List[ResumeProject] = field(
        default_factory=list
    )
    certifications: List[ResumeCertification] = field(
        default_factory=list
    )
    sections: Dict[str, str] = field(
        default_factory=dict
    )
    statistics: ResumeStatistics = field(
        default_factory=ResumeStatistics
    )
    message: str = ""


# ------------------------------------------------------------------
# NORMALIZATION HELPERS
# ------------------------------------------------------------------

def _normalize_heading(text: str) -> str:
    """
    Normalize a possible section heading for comparison.
    """

    if not isinstance(text, str):
        return ""

    normalized = text.strip().lower()

    normalized = re.sub(
        r"^[\s\-•*▪◦⁃]+",
        "",
        normalized,
    )

    normalized = re.sub(
        r"[\s:|]+$",
        "",
        normalized,
    )

    normalized = re.sub(
        r"\s+",
        " ",
        normalized,
    )

    return normalized.strip()


def _canonical_section_name(
    heading: str,
) -> Optional[str]:
    """
    Convert a section heading into its canonical section name.
    """

    normalized = _normalize_heading(heading)

    if not normalized:
        return None

    for canonical_name, aliases in SECTION_ALIASES.items():
        for alias in aliases:
            if normalized == alias.lower():
                return canonical_name

    return None


def _clean_lines(text: str) -> List[str]:
    """
    Return cleaned non-empty resume lines.
    """

    if not text:
        return []

    return [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]


def _unique_preserving_order(
    items: List[str],
) -> List[str]:
    """
    Remove duplicate strings while preserving order.
    """

    result: List[str] = []
    seen = set()

    for item in items:
        normalized = item.strip().lower()

        if not normalized or normalized in seen:
            continue

        seen.add(normalized)
        result.append(item.strip())

    return result


# ------------------------------------------------------------------
# CONTACT INFORMATION
# ------------------------------------------------------------------

def _extract_email(text: str) -> str:
    """
    Extract the first email address.
    """

    match = re.search(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
        text,
        flags=re.IGNORECASE,
    )

    return match.group(0) if match else ""


def _extract_phone(text: str) -> str:
    """
    Extract the first plausible phone number.
    """

    phone_patterns = (
        r"(?<!\d)(?:\+\d{1,3}[\s.-]?)?"
        r"(?:\(?\d{2,4}\)?[\s.-]?)?"
        r"\d{3,4}[\s.-]?\d{3,4}(?!\d)",
        r"(?<!\d)\d{10}(?!\d)",
    )

    for pattern in phone_patterns:
        match = re.search(
            pattern,
            text,
        )

        if not match:
            continue

        value = match.group(0).strip()

        digits = re.sub(
            r"\D",
            "",
            value,
        )

        if 10 <= len(digits) <= 15:
            return value

    return ""


def _extract_url(
    text: str,
    service: str,
) -> str:
    """
    Extract a LinkedIn or GitHub URL.
    """

    pattern = (
        rf"(?:https?://)?(?:www\.)?"
        rf"{service}\.com/[A-Za-z0-9._~:/?#\[\]@!$&'()*+,;=%-]+"
    )

    match = re.search(
        pattern,
        text,
        flags=re.IGNORECASE,
    )

    if not match:
        return ""

    return match.group(0).rstrip(
        ".,;:)"
    )


def _looks_like_name(line: str) -> bool:
    """
    Determine whether a line is likely to contain a person's name.
    """

    if not line:
        return False

    if len(line) > 80:
        return False

    if any(char.isdigit() for char in line):
        return False

    if "@" in line:
        return False

    if re.search(
        r"https?://|www\.",
        line,
        flags=re.IGNORECASE,
    ):
        return False

    if re.search(
        r"\b("
        r"resume|curriculum vitae|cv|summary|"
        r"skills|education|experience|projects|"
        r"certifications|developer|engineer|"
        r"student|objective"
        r")\b",
        line,
        flags=re.IGNORECASE,
    ):
        return False

    words = line.split()

    if not 2 <= len(words) <= 5:
        return False

    return all(
        re.match(
            r"^[A-Za-z][A-Za-z.'-]*$",
            word,
        )
        for word in words
    )


def extract_contact_information(
    text: str,
) -> ResumeContactInfo:
    """
    Extract basic contact information from resume text.
    """

    if not text:
        return ResumeContactInfo()

    lines = _clean_lines(text)

    name = ""

    for line in lines[:10]:
        if _looks_like_name(line):
            name = line
            break

    return ResumeContactInfo(
        name=name,
        email=_extract_email(text),
        phone=_extract_phone(text),
        linkedin=_extract_url(text, "linkedin"),
        github=_extract_url(text, "github"),
    )


# ------------------------------------------------------------------
# SECTION EXTRACTION
# ------------------------------------------------------------------

def extract_resume_sections(
    text: str,
) -> Dict[str, str]:
    """
    Detect and extract recognized resume sections.
    """

    if not text:
        return {}

    lines = _clean_lines(text)

    sections: Dict[str, List[str]] = {}
    current_section: Optional[str] = None

    for line in lines:
        section_name = _canonical_section_name(line)

        if section_name:
            current_section = section_name

            if current_section not in sections:
                sections[current_section] = []

            continue

        if current_section is not None:
            sections[current_section].append(line)

    return {
        section_name: "\n".join(content).strip()
        for section_name, content in sections.items()
        if "\n".join(content).strip()
    }


# ------------------------------------------------------------------
# SUMMARY EXTRACTION
# ------------------------------------------------------------------

def _extract_summary(
    sections: Dict[str, str],
) -> str:
    """
    Extract the professional summary from detected sections.
    """

    summary = sections.get("summary", "")

    if not summary:
        return ""

    return summary.strip()


# ------------------------------------------------------------------
# EDUCATION EXTRACTION
# ------------------------------------------------------------------

EDUCATION_TERMS = (
    "bachelor",
    "master",
    "b.tech",
    "btech",
    "m.tech",
    "mtech",
    "b.e",
    "be",
    "m.e",
    "me",
    "bca",
    "mca",
    "b.sc",
    "bsc",
    "m.sc",
    "msc",
    "mba",
    "phd",
    "diploma",
    "degree",
)


def _is_education_line(line: str) -> bool:
    """
    Determine whether a line appears to describe an education entry.
    """

    lowered = line.lower()

    return any(
        term in lowered
        for term in EDUCATION_TERMS
    )


def _extract_year_range(text: str) -> str:
    """
    Extract a year or year range from text.
    """

    match = re.search(
        r"\b(?:19|20)\d{2}"
        r"(?:\s*[-–—]\s*(?:19|20)\d{2}"
        r"|\s*[-–—]\s*(?:Present|Current))?\b",
        text,
        flags=re.IGNORECASE,
    )

    return match.group(0) if match else ""


def _remove_year_range(text: str) -> str:
    """
    Remove a year or year range from text.
    """

    return re.sub(
        r"\b(?:19|20)\d{2}"
        r"(?:\s*[-–—]\s*(?:19|20)\d{2}"
        r"|\s*[-–—]\s*(?:Present|Current))?\b",
        "",
        text,
        flags=re.IGNORECASE,
    )


def extract_education(
    section_text: str,
) -> List[ResumeEducation]:
    """
    Extract education entries using line-based heuristics.

    Supports both:

        MCA - Oriental University - 2025-2027

    and multi-line formats where degree, institution, and year are
    placed on separate lines.
    """

    if not section_text:
        return []

    lines = _clean_lines(section_text)
    entries: List[ResumeEducation] = []

    for index, line in enumerate(lines):
        if not _is_education_line(line):
            continue

        year = _extract_year_range(line)

        cleaned_line = _remove_year_range(line).strip(
            " ,|-–—"
        )

        parts = [
            part.strip()
            for part in re.split(
                r"\s+-\s+|\s+–\s+|\s+—\s+|\s+\|\s+",
                cleaned_line,
            )
            if part.strip()
        ]

        degree = parts[0] if parts else cleaned_line
        institution = ""

        if len(parts) >= 2:
            institution = parts[1]

        if not year:
            for look_ahead in range(
                index + 1,
                min(index + 3, len(lines)),
            ):
                candidate_year = _extract_year_range(
                    lines[look_ahead]
                )

                if candidate_year:
                    year = candidate_year
                    break

        if not institution and index + 1 < len(lines):
            next_line = lines[index + 1]

            if (
                not _is_education_line(next_line)
                and not _extract_year_range(next_line)
            ):
                institution = next_line

        details = ""

        if index + 2 < len(lines):
            candidate = lines[index + 2]

            if (
                not _is_education_line(candidate)
                and not _extract_year_range(candidate)
            ):
                details = candidate

        entries.append(
            ResumeEducation(
                degree=degree,
                institution=institution,
                year=year,
                details=details,
            )
        )

    return entries


# ------------------------------------------------------------------
# EXPERIENCE EXTRACTION
# ------------------------------------------------------------------

EXPERIENCE_ROLE_TERMS = (
    "developer",
    "engineer",
    "analyst",
    "intern",
    "manager",
    "designer",
    "consultant",
    "administrator",
    "specialist",
    "executive",
    "lead",
    "architect",
    "scientist",
    "trainee",
    "associate",
)


def _looks_like_experience_role(line: str) -> bool:
    """
    Determine whether a line likely represents a job title.
    """

    lowered = line.lower()

    return any(
        re.search(
            rf"\b{re.escape(term)}\b",
            lowered,
        )
        for term in EXPERIENCE_ROLE_TERMS
    )


def _find_duration_in_lines(
    lines: List[str],
    start_index: int,
    end_index: int,
) -> tuple[str, Optional[int]]:
    """
    Find a duration within a bounded line range.

    Returns
    -------
    tuple[str, Optional[int]]
        Duration text and the line index containing it.
    """

    month_pattern = (
        r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
        r"(?:uary|ruary|ch|il|e|y|tober|ember)?"
    )

    month_range_pattern = re.compile(
        rf"\b{month_pattern}\s+\d{{4}}"
        rf"\s*[-–—]\s*"
        rf"(?:Present|Current|{month_pattern}\s+\d{{4}})\b",
        flags=re.IGNORECASE,
    )

    for index in range(
        start_index,
        min(end_index, len(lines)),
    ):
        line = lines[index]

        year_range = _extract_year_range(line)

        if year_range:
            return year_range, index

        month_range = month_range_pattern.search(
            line
        )

        if month_range:
            return month_range.group(0), index

    return "", None


def extract_experience(
    section_text: str,
) -> List[ResumeExperience]:
    """
    Extract work-experience entries using conservative heuristics.

    The parser identifies job-title lines first, then searches the
    corresponding block for company, duration, and description lines.
    """

    if not section_text:
        return []

    lines = _clean_lines(section_text)

    role_indices = [
        index
        for index, line in enumerate(lines)
        if _looks_like_experience_role(line)
    ]

    entries: List[ResumeExperience] = []

    for role_position, role_index in enumerate(
        role_indices
    ):
        next_role_index = (
            role_indices[role_position + 1]
            if role_position + 1 < len(role_indices)
            else len(lines)
        )

        job_title = lines[role_index]
        company = ""

        company_index: Optional[int] = None

        if role_index + 1 < next_role_index:
            candidate = lines[role_index + 1]

            if (
                not _extract_year_range(candidate)
                and not _looks_like_experience_role(candidate)
            ):
                company = candidate
                company_index = role_index + 1

        search_start = (
            company_index + 1
            if company_index is not None
            else role_index + 1
        )

        duration, duration_index = _find_duration_in_lines(
            lines,
            search_start,
            next_role_index,
        )

        details_start = (
            duration_index + 1
            if duration_index is not None
            else search_start
        )

        details_lines: List[str] = []

        for detail_index in range(
            details_start,
            next_role_index,
        ):
            detail_line = lines[detail_index]

            if _extract_year_range(detail_line):
                continue

            if detail_line == company:
                continue

            details_lines.append(detail_line)

            if len(details_lines) >= 8:
                break

        entries.append(
            ResumeExperience(
                job_title=job_title,
                company=company,
                duration=duration,
                details="\n".join(details_lines),
            )
        )

    return entries


# ------------------------------------------------------------------
# PROJECT EXTRACTION
# ------------------------------------------------------------------

PROJECT_DESCRIPTION_STARTERS = (
    "developed ",
    "built ",
    "created ",
    "implemented ",
    "designed ",
    "using ",
    "used ",
    "developing ",
    "built using ",
    "created using ",
    "analyzed ",
    "analysis ",
    "application ",
    "resume analysis ",
    "this project ",
    "the project ",
)


def _looks_like_project_heading(
    line: str,
) -> bool:
    """
    Determine whether a line looks like a project heading.

    A project heading is normally short, does not end in sentence
    punctuation, and does not read like a descriptive sentence.
    """

    if not line:
        return False

    if _extract_year_range(line):
        return False

    if len(line) > 100:
        return False

    stripped = line.strip()
    lowered = stripped.lower()

    if stripped.endswith(
        (".", "!", "?", ";")
    ):
        return False

    if lowered.startswith(
        PROJECT_DESCRIPTION_STARTERS
    ):
        return False

    if len(stripped.split()) > 10:
        return False

    return True


def extract_projects(
    section_text: str,
) -> List[ResumeProject]:
    """
    Extract project entries from the projects section.

    Short standalone lines are treated as project names.
    Descriptive sentences are attached to the current project.
    """

    if not section_text:
        return []

    lines = _clean_lines(section_text)

    if not lines:
        return []

    projects: List[ResumeProject] = []
    current_project: Optional[ResumeProject] = None

    for line in lines:
        if _looks_like_project_heading(line):
            if current_project is not None:
                projects.append(current_project)

            current_project = ResumeProject(
                name=line,
                duration=_extract_year_range(line),
                details="",
            )
            continue

        if current_project is None:
            current_project = ResumeProject(
                name="Project",
                details=line,
            )
        else:
            if current_project.details:
                current_project.details += "\n"

            current_project.details += line

    if current_project is not None:
        projects.append(current_project)

    return projects


# ------------------------------------------------------------------
# CERTIFICATION EXTRACTION
# ------------------------------------------------------------------

def extract_certifications(
    section_text: str,
) -> List[ResumeCertification]:
    """
    Extract certification entries from the certifications section.
    """

    if not section_text:
        return []

    lines = _clean_lines(section_text)
    certifications: List[ResumeCertification] = []

    for line in lines:
        year = _extract_year_range(line)

        cleaned_line = _remove_year_range(line).strip(
            " ,|-–—"
        )

        issuer = ""

        separator_match = re.search(
            r"\s(?:-|–|—|\|)\s",
            cleaned_line,
        )

        name = cleaned_line

        if separator_match:
            position = separator_match.start()

            name = cleaned_line[:position].strip()
            issuer = cleaned_line[
                separator_match.end():
            ].strip()

        certifications.append(
            ResumeCertification(
                name=name,
                issuer=issuer,
                year=year,
            )
        )

    return certifications


# ------------------------------------------------------------------
# RESUME PARSER
# ------------------------------------------------------------------

def parse_resume(
    text: str | None,
) -> ResumeParseResult:
    """
    Parse a resume into a structured representation.

    Parameters
    ----------
    text:
        Raw resume text.

    Returns
    -------
    ResumeParseResult
        Structured resume information.
    """

    if not isinstance(text, str) or not text.strip():
        return ResumeParseResult(
            success=False,
            message="Resume text is empty.",
        )

    cleaned_text = clean_resume_text(text)

    if not cleaned_text:
        return ResumeParseResult(
            success=False,
            original_text=text,
            message="Resume text does not contain usable content.",
        )

    sections = extract_resume_sections(
        cleaned_text
    )

    skill_result = analyze_resume_skills(
        cleaned_text
    )

    contact = extract_contact_information(
        cleaned_text
    )

    summary = _extract_summary(sections)

    education = extract_education(
        sections.get("education", "")
    )

    experience = extract_experience(
        sections.get("experience", "")
    )

    projects = extract_projects(
        sections.get("projects", "")
    )

    certifications = extract_certifications(
        sections.get("certifications", "")
    )

    statistics = ResumeStatistics(
        word_count=count_words(cleaned_text),
        line_count=count_lines(cleaned_text),
        character_count=count_characters(cleaned_text),
        section_count=len(sections),
        skill_count=skill_result.skill_count,
    )

    return ResumeParseResult(
        success=True,
        original_text=text,
        cleaned_text=cleaned_text,
        contact=contact,
        summary=summary,
        skills=skill_result.skills,
        skill_categories=skill_result.categories,
        education=education,
        experience=experience,
        projects=projects,
        certifications=certifications,
        sections=sections,
        statistics=statistics,
        message="Resume parsed successfully.",
    )