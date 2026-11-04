"""Small, auditable title-only core skill profiles shared across the two tools.

These are typical role competencies, *not* employer job requirements.
An occupation's imported catalog remains available, but a large alphabetical
software/knowledge list must not dilute explicit core skill evidence.
"""
from __future__ import annotations
import re
from app.services.alias_matching import canonical_key
from app.services.role_skills import ROLE_MAP, ALIASED_ROLES, normalize_title

# Exact official titles/recognised forms, not keyword fuzzy matching.
OFFICIAL_TITLE_TO_ROLE = {
    'web developers': 'web developer',
    'web and digital interface designers': 'frontend developer',
    'customer service representatives': 'customer care executive',
    'bookkeeping accounting and auditing clerks': 'accountant',
    'bookkeeping accounting and auditing clerk': 'accountant',
    'accountants and auditors': 'accountant',
    'software developers': 'software engineer',
    'software quality assurance analysts and testers': 'software tester',
    'computer user support specialists': 'technical support executive',
    'data scientists': 'data scientist',
    'database administrators': 'database administrator',
    'financial analysts': 'financial analyst',
    'market research analysts and marketing specialists': 'digital marketer',
    'marketing coordinators': 'marketing coordinator',
    'receptionists and information clerks': 'receptionist',
    'office clerks general': 'administrative assistant',
}


def core_role(title: str) -> str | None:
    normalized = normalize_title(title)
    key = re.sub(r'[^a-z0-9]+', ' ', normalized).strip()
    mapped = OFFICIAL_TITLE_TO_ROLE.get(key)
    if mapped:
        return mapped
    normalized = ALIASED_ROLES.get(normalized, normalized)
    if normalized in ROLE_MAP:
        return normalized
    # Safe singular/plural handling for canonical role names only.
    if normalized.endswith('s') and normalized[:-1] in ROLE_MAP:
        return normalized[:-1]
    return None


def core_skills(title: str) -> tuple[str, ...]:
    role = core_role(title)
    return ROLE_MAP.get(role, ()) if role else ()


def core_evidence(title: str, detected: set[str] | list[str]):
    skills = core_skills(title)
    known = {canonical_key(item) for item in detected}
    matched = [item for item in skills if canonical_key(item) in known]
    missing = [item for item in skills if canonical_key(item) not in known]
    return matched, missing
