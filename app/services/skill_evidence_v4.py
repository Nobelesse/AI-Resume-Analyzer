"""Conservative, deterministic JD/resume skill evidence helpers.

Canonicalization only combines equivalent labels. A tiny set of explicit,
reviewed task-evidence patterns is applied to the resume, never the JD.
No inferred seniority, skill proficiency, or unobserved tools.
"""
from __future__ import annotations
import re
from app.services.alias_matching import canonical_key, CANONICAL_TO_VARIANTS

# Documented word forms/phrases that express the SAME observable task.
# A pattern is enough evidence for the canonical task, not for proficiency.
TASK_EVIDENCE = {
    'data analysis': (
        r'\bdata\s+analys(?:is|t|es)\b',
        r'\banaly[sz](?:e|ed|ing)\s+(?:business\s+)?data\b',
    ),
    'data visualization': (
        r'\bdata\s+visuali[sz]ation\b',
        r'\b(?:created|developed|built)\s+(?:an?\s+)?(?:interactive\s+)?(?:power\s*bi\s+|tableau\s+)?dashboards?\b',
    ),
    'pivot tables': (
        r'\bpivot[\s-]+tables?\b',
    ),
    'kpi reporting': (
        r'\bkpi\s+(?:tracking|monitoring|reporting)\b',
        r'\b(?:monitor(?:ed|ing)?|track(?:ed|ing)?)\s+.{0,40}\bkpis?\b',
    ),
    'communicate analytical insights': (
        r'\b(?:presented|communicated|reported|explained)\s+.{0,65}\b(?:insights?|findings?|trends?|analys[ei]s|results?)\b',
    ),
    'use spreadsheets software': (
        r'\b(?:microsoft\s+excel|ms[\s-]+excel|excel|google\s+sheets|libreoffice\s+calc)\b',
    ),
}

# Explicit equivalence in text for occupation task names; do not confuse
# similar-but-different tools (Java vs JavaScript, Python vs Pandas).
EXPLICIT_TASK_REQUIREMENTS = {
    'communicate analytical insights': (r'\bcommunicat(?:e|ing|ion)\s+(?:of\s+)?analytical\s+(?:insights?|findings?)\b',),
    'use spreadsheets software': (r'\buse\s+spreadsheets?\s+software\b',),
}


def unique_skill_labels(labels):
    """Return one representative per semantic skill identity, stable order.

    Prefer a canonical label if it is present; otherwise use the shortest
    label with a deterministic alphabetical tie break.
    """
    grouped = {}
    for label in labels:
        # A publisher's generic product-family/verb label is not proof of a
        # particular transferable skill. Keep specific products such as
        # Google Analytics, Google Ads and Google Sheets.
        if str(label).strip().casefold() == 'google':
            continue
        key = canonical_key(label)
        if key and (key not in grouped or (label.casefold() == key and grouped[key].casefold() != key)
                    or (grouped[key].casefold() != key and (len(label), label.casefold()) < (len(grouped[key]), grouped[key].casefold()))):
            grouped[key] = label
    return sorted(grouped.values(), key=str.casefold)


def observable_task_evidence(resume_text, *, requested_skills=()):
    """Emit only tasks explicitly supported by the resume's own wording.

    Limit to skills actually requested in the job description. This prevents
    adding generic tasks unrelated to the JD or claiming arbitrary skills.
    """
    wanted = {canonical_key(s) for s in requested_skills}
    evidence = set()
    for skill, patterns in TASK_EVIDENCE.items():
        if canonical_key(skill) in wanted and any(re.search(p, resume_text, re.I) for p in patterns):
            evidence.add(skill)
    return evidence


def explicit_jd_tasks(jd_text):
    """Identify tightly scoped task labels explicitly written in the JD."""
    return {skill for skill, patterns in EXPLICIT_TASK_REQUIREMENTS.items()
            if any(re.search(p, jd_text, re.I) for p in patterns)}


def requirement_coverage(rows):
    """Count each assessable JD line once, excluding unverifiable claims.

    'Partial' lines get 0.5; no unverified education/experience line is
    silently marked as a match. Return None when no assessable lines exist.
    """
    assessable = [r for r in rows if r['status'] != 'unverified']
    if not assessable:
        return None
    weights = {'evidenced':1.0, 'partial':0.5, 'not-found':0.0}
    return sum(weights.get(r['status'],0.0) for r in assessable) / len(assessable)


def match_evidence_snippets(resume_text: str, skill_names, *, max_snippet=230) -> dict[str, str]:
    """Show verbatim, bounded resume excerpts for matched JD skills.

    This is *document evidence*, never verification of experience or ability.
    When the source cannot be located safely, omit the excerpt rather than
    fabricate or match an arbitrary term elsewhere in the document.
    """
    result = {}
    # Preserve lines; do not expose personal details unless that line itself
    # includes the named skill. Keep no additional state or external calls.
    lines = [x.strip() for x in str(resume_text).splitlines() if x.strip()]
    for skill in unique_skill_labels(skill_names):
        key = canonical_key(skill)
        variants = CANONICAL_TO_VARIANTS.get(key, (key,))
        patterns = [re.compile(r'(?<![\w])' + re.escape(alias).replace(r'\ ', r'\s+') + r'(?![\w])', re.I)
                    for alias in sorted(variants, key=len, reverse=True) if len(alias) >= 3]
        patterns += [re.compile(p, re.I) for p in TASK_EVIDENCE.get(key, ())]
        for line in lines:
            if any(pattern.search(line) for pattern in patterns):
                result[skill] = line[:max_snippet] + ('…' if len(line) > max_snippet else '')
                break
    return result
