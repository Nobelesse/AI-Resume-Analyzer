"""
Job Description Analyzer
------------------------

Provides rule-based analysis of job descriptions for the ResumeAI
matching pipeline.

The analyzer extracts:
- cleaned job description text
- common technical and professional skills
- important keywords
- experience requirements
- education requirements
- detected job-description sections

This module is intentionally local and deterministic. It does not
require an external API or LLM.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Tuple


# ------------------------------------------------------------------
# COMMON SKILLS
# ------------------------------------------------------------------

COMMON_SKILLS: Tuple[str, ...] = (
    # Programming languages
    "Python",
    "Java",
    "C",
    "C++",
    "C#",
    "JavaScript",
    "TypeScript",
    "Go",
    "Rust",
    "PHP",
    "Ruby",
    "Kotlin",
    "Swift",

    # Web technologies
    "HTML",
    "CSS",
    "React",
    "Angular",
    "Vue",
    "Node.js",
    "Express.js",
    "Django",
    "Flask",
    "FastAPI",

    # Databases
    "SQL",
    "MySQL",
    "PostgreSQL",
    "MongoDB",
    "Oracle",
    "SQLite",
    "Redis",

    # Data / AI / ML
    "Machine Learning",
    "Deep Learning",
    "Artificial Intelligence",
    "Natural Language Processing",
    "NLP",
    "Computer Vision",
    "Data Science",
    "Data Analysis",
    "Data Analytics",
    "Generative AI",
    "Large Language Models",
    "LLM",
    "RAG",
    "LangChain",
    "TensorFlow",
    "PyTorch",
    "Keras",
    "scikit-learn",
    "Pandas",
    "NumPy",
    "Matplotlib",
    "Seaborn",
    "Hugging Face",
    "Transformers",

    # Cloud / DevOps
    "AWS",
    "Azure",
    "Google Cloud",
    "GCP",
    "Docker",
    "Kubernetes",
    "Jenkins",
    "Git",
    "GitHub",
    "GitLab",
    "CI/CD",

    # Development / engineering
    "REST API",
    "REST APIs",
    "API",
    "Microservices",
    "Object-Oriented Programming",
    "OOP",
    "Data Structures",
    "Algorithms",
    "System Design",
    "Software Development",
    "Agile",
    "Scrum",

    # Testing
    "Unit Testing",
    "PyTest",
    "pytest",
    "Selenium",

    # Cybersecurity
    "Cyber Security",
    "Cybersecurity",
    "Network Security",
    "Cryptography",

    # Other professional skills
    "Problem Solving",
    "Communication",
    "Leadership",
    "Teamwork",
    "Time Management",
)


# ------------------------------------------------------------------
# SKILL ALIASES
# ------------------------------------------------------------------

# Different ways the same skill may appear in a job description.
# The returned value is the canonical skill name.
SKILL_ALIASES: Dict[str, str] = {
    "rest api": "REST API",
    "rest apis": "REST API",
    "restful api": "REST API",
    "restful apis": "REST API",

    "machine learning": "Machine Learning",
    "ml": "Machine Learning",

    "artificial intelligence": "Artificial Intelligence",
    "ai": "Artificial Intelligence",

    "natural language processing": "Natural Language Processing",
    "nlp": "NLP",

    "data analysis": "Data Analysis",
    "data analytics": "Data Analytics",

    "large language model": "Large Language Models",
    "large language models": "Large Language Models",
    "llm": "LLM",
    "llms": "LLM",

    "object oriented programming": "Object-Oriented Programming",
    "object-oriented programming": "Object-Oriented Programming",
    "oop": "OOP",

    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",

    "scikit learn": "scikit-learn",
    "scikit-learn": "scikit-learn",

    "pytorch": "PyTorch",
    "tensorflow": "TensorFlow",

    "github": "GitHub",
    "gitlab": "GitLab",

    "ci/cd": "CI/CD",
}


# ------------------------------------------------------------------
# SECTION HEADINGS
# ------------------------------------------------------------------

SECTION_ALIASES: Dict[str, Tuple[str, ...]] = {
    "summary": (
        "summary",
        "about the role",
        "about the position",
        "overview",
        "job overview",
    ),
    "responsibilities": (
        "responsibilities",
        "key responsibilities",
        "roles and responsibilities",
        "what you will do",
        "what you'll do",
        "duties",
        "job duties",
    ),
    "requirements": (
        "requirements",
        "job requirements",
        "qualifications",
        "required qualifications",
        "basic qualifications",
        "must have",
        "what we are looking for",
        "what we're looking for",
    ),
    "skills": (
        "skills",
        "technical skills",
        "required skills",
        "technical requirements",
    ),
    "education": (
        "education",
        "educational qualifications",
        "academic qualifications",
        "education requirements",
    ),
    "experience": (
        "experience",
        "work experience",
        "professional experience",
        "experience requirements",
    ),
    "preferred": (
        "preferred qualifications",
        "preferred requirements",
        "preferred skills",
        "nice to have",
        "good to have",
    ),
}


# ------------------------------------------------------------------
# RESULT DATA CLASS
# ------------------------------------------------------------------

@dataclass
class JobDescriptionAnalysis:
    """
    Stores the structured result of job-description analysis.
    """

    success: bool
    original_text: str
    cleaned_text: str
    skills: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    experience_requirements: List[str] = field(default_factory=list)
    education_requirements: List[str] = field(default_factory=list)
    sections: Dict[str, str] = field(default_factory=dict)
    message: str = ""


# ------------------------------------------------------------------
# TEXT CLEANING
# ------------------------------------------------------------------

def clean_job_description(text: str) -> str:
    """
    Normalize job-description text while preserving useful structure.

    Parameters
    ----------
    text:
        Raw job-description text.

    Returns
    -------
    str
        Cleaned job-description text.
    """

    if not text:
        return ""

    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Normalize tabs and repeated spaces.
    text = re.sub(r"[ \t]+", " ", text)

    # Remove spaces around line breaks.
    text = re.sub(r" *\n *", "\n", text)

    # Reduce excessive blank lines.
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


# ------------------------------------------------------------------
# SECTION DETECTION
# ------------------------------------------------------------------

def _normalize_heading(text: str) -> str:
    """
    Normalize a potential section heading for comparison.
    """

    text = text.lower().strip()
    text = re.sub(r"[:\-–—]+$", "", text)
    text = re.sub(r"\s+", " ", text)

    return text


def _get_section_name(heading: str) -> str | None:
    """
    Map a heading to a canonical section name.
    """

    normalized_heading = _normalize_heading(heading)

    for section_name, aliases in SECTION_ALIASES.items():
        if normalized_heading in aliases:
            return section_name

    return None


def extract_sections(text: str) -> Dict[str, str]:
    """
    Detect common job-description sections.

    A section begins when a recognized heading is encountered and
    continues until another recognized heading is found.

    Parameters
    ----------
    text:
        Cleaned or raw job-description text.

    Returns
    -------
    dict
        Mapping of section name to section content.
    """

    if not text:
        return {}

    lines = text.splitlines()

    sections: Dict[str, List[str]] = {}
    current_section: str | None = None

    for line in lines:
        stripped_line = line.strip()

        if not stripped_line:
            if current_section is not None:
                sections.setdefault(current_section, []).append("")
            continue

        section_name = _get_section_name(stripped_line)

        if section_name is not None:
            current_section = section_name
            sections.setdefault(current_section, [])
            continue

        if current_section is not None:
            sections.setdefault(current_section, []).append(stripped_line)

    return {
        section_name: "\n".join(content).strip()
        for section_name, content in sections.items()
        if "\n".join(content).strip()
    }


# ------------------------------------------------------------------
# SKILL EXTRACTION
# ------------------------------------------------------------------

def _contains_skill(text: str, skill: str) -> bool:
    """
    Check whether a skill appears as a meaningful term in text.
    """

    escaped_skill = re.escape(skill)

    pattern = rf"(?<!\w){escaped_skill}(?!\w)"

    return re.search(
        pattern,
        text,
        flags=re.IGNORECASE,
    ) is not None


def extract_skills(text: str) -> List[str]:
    """
    Extract recognized technical and professional skills.

    Parameters
    ----------
    text:
        Job-description text.

    Returns
    -------
    list[str]
        Unique recognized skills in their canonical form.
    """

    if not text:
        return []

    found_skills: List[str] = []

    # Check aliases first so plural/alternate forms are converted
    # to their canonical representation.
    for alias, canonical_skill in SKILL_ALIASES.items():

        if _contains_skill(text, alias):

            if not any(
                existing.lower() == canonical_skill.lower()
                for existing in found_skills
            ):
                found_skills.append(canonical_skill)

    # Check the main skill dictionary.
    for skill in COMMON_SKILLS:

        if _contains_skill(text, skill):

            canonical_skill = skill

            # Convert REST APIs to the canonical REST API name.
            if canonical_skill.lower() == "rest apis":
                canonical_skill = "REST API"

            if not any(
                existing.lower() == canonical_skill.lower()
                for existing in found_skills
            ):
                found_skills.append(canonical_skill)

    return found_skills


# ------------------------------------------------------------------
# KEYWORD EXTRACTION
# ------------------------------------------------------------------

STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "in",
    "into",
    "is",
    "it",
    "of",
    "on",
    "or",
    "our",
    "the",
    "their",
    "this",
    "to",
    "we",
    "with",
    "you",
    "your",
}


def extract_keywords(
    text: str,
    skills: List[str] | None = None,
) -> List[str]:
    """
    Extract important keyword candidates from a job description.

    Skills are included first, followed by meaningful repeated words.

    Parameters
    ----------
    text:
        Job-description text.
    skills:
        Previously extracted skills.

    Returns
    -------
    list[str]
        Ordered unique keywords.
    """

    if not text:
        return []

    if skills is None:
        skills = extract_skills(text)

    keywords: List[str] = []

    # Skills are high-value keywords.
    for skill in skills:
        if skill not in keywords:
            keywords.append(skill)

    normalized = text.lower()

    words = re.findall(
        r"\b[a-zA-Z][a-zA-Z0-9+#.-]{2,}\b",
        normalized,
    )

    frequencies: Dict[str, int] = {}

    for word in words:

        cleaned_word = word.strip(".-")

        if not cleaned_word:
            continue

        if cleaned_word in STOPWORDS:
            continue

        if len(cleaned_word) < 3:
            continue

        frequencies[cleaned_word] = (
            frequencies.get(cleaned_word, 0) + 1
        )

    repeated_words = sorted(
        (
            (word, count)
            for word, count in frequencies.items()
            if count >= 2
        ),
        key=lambda item: (-item[1], item[0]),
    )

    existing_lower = {
        keyword.lower()
        for keyword in keywords
    }

    for word, _count in repeated_words:

        if word.lower() not in existing_lower:
            keywords.append(word)
            existing_lower.add(word.lower())

    return keywords


# ------------------------------------------------------------------
# EXPERIENCE EXTRACTION
# ------------------------------------------------------------------

EXPERIENCE_PATTERNS: Tuple[str, ...] = (
    r"\b\d+\+?\s*(?:years?|yrs?)\s+of\s+experience\b",
    r"\b\d+\+?\s*(?:years?|yrs?)\s+experience\b",
    r"\bminimum\s+of\s+\d+\+?\s*(?:years?|yrs?)\b",
    r"\bat\s+least\s+\d+\+?\s*(?:years?|yrs?)\b",
    r"\b\d+\+?\s*(?:years?|yrs?)\s+in\b[^.\n;]*",
    r"\bexperience\s+with\b[^.\n;]*",
    r"\bexperience\s+in\b[^.\n;]*",
)


def extract_experience_requirements(text: str) -> List[str]:
    """
    Extract experience-related requirements.
    """

    if not text:
        return []

    requirements: List[str] = []

    for pattern in EXPERIENCE_PATTERNS:

        matches = re.findall(
            pattern,
            text,
            flags=re.IGNORECASE,
        )

        for match in matches:

            requirement = re.sub(
                r"\s+",
                " ",
                match,
            ).strip(" .,:;-")

            if requirement and requirement.lower() not in {
                item.lower()
                for item in requirements
            }:
                requirements.append(requirement)

    return requirements


# ------------------------------------------------------------------
# EDUCATION EXTRACTION
# ------------------------------------------------------------------

EDUCATION_TERMS: Tuple[str, ...] = (
    "bachelor",
    "bachelors",
    "bachelor's",
    "master",
    "masters",
    "master's",
    "b.tech",
    "b.e.",
    "bca",
    "mca",
    "m.tech",
    "m.e.",
    "mba",
    "phd",
    "ph.d",
    "doctorate",
    "degree",
    "diploma",
    "computer science",
    "information technology",
    "software engineering",
    "engineering",
)


def extract_education_requirements(text: str) -> List[str]:
    """
    Extract education-related requirement phrases.
    """

    if not text:
        return []

    requirements: List[str] = []

    lines = text.splitlines()

    for line in lines:

        line_clean = line.strip()

        if not line_clean:
            continue

        line_lower = line_clean.lower()

        if any(
            term in line_lower
            for term in EDUCATION_TERMS
        ):

            cleaned_line = re.sub(
                r"^[•*\-–—\s]+",
                "",
                line_clean,
            )

            if cleaned_line.lower() not in {
                item.lower()
                for item in requirements
            }:
                requirements.append(cleaned_line)

    return requirements


# ------------------------------------------------------------------
# MAIN ANALYZER
# ------------------------------------------------------------------

def analyze_job_description(
    text: str,
) -> JobDescriptionAnalysis:
    """
    Analyze a complete job description.

    Parameters
    ----------
    text:
        Raw job-description text.

    Returns
    -------
    JobDescriptionAnalysis
        Structured analysis result.
    """

    if not text or not text.strip():
        return JobDescriptionAnalysis(
            success=False,
            original_text=text or "",
            cleaned_text="",
            message="Job description is empty.",
        )

    cleaned_text = clean_job_description(text)

    if not cleaned_text:
        return JobDescriptionAnalysis(
            success=False,
            original_text=text,
            cleaned_text="",
            message="Job description does not contain usable text.",
        )

    sections = extract_sections(cleaned_text)

    skills = extract_skills(cleaned_text)

    keywords = extract_keywords(
        cleaned_text,
        skills=skills,
    )

    experience_requirements = (
        extract_experience_requirements(cleaned_text)
    )

    education_requirements = (
        extract_education_requirements(cleaned_text)
    )

    return JobDescriptionAnalysis(
        success=True,
        original_text=text,
        cleaned_text=cleaned_text,
        skills=skills,
        keywords=keywords,
        experience_requirements=experience_requirements,
        education_requirements=education_requirements,
        sections=sections,
        message=(
            "Job description analyzed successfully. "
            f"Detected {len(skills)} skills, "
            f"{len(keywords)} keywords, "
            f"{len(experience_requirements)} "
            "experience requirements, "
            f"and {len(education_requirements)} "
            "education requirements."
        ),
    )