"""Auditable offline career ranking using local skill and occupation data."""
from __future__ import annotations
import re
from app.database.connection import connect
from app.services.skills import extract_skills, seed_skills
from app.services.skill_intelligence import phrase_present
from app.services.alias_matching import catalogue_query_keys, canonical_key
from app.services.taxonomy import ensure_tables
from app.services.role_skills import ROLE_MAP
from app.services.role_profiles import core_evidence, core_skills
from app.services.career_intelligence155 import evidence_weight, occupation_focus, useful_gaps, occupation_learning_topics

DISCLAIMER = 'Evidence-based skill coverage, not a hiring probability or a verified qualification.'

# Controlled occupation domain evidence. These are ranking aids, NOT inferred
# qualifications or a substitute for the source occupation catalog.
DOMAIN_PROFILES = {
    'software': {
        'signals': ('fastapi','django','flask','rest api','sqlalchemy','postgresql','git','docker','backend','api development','software engineer','software developer','python developer','microservices','javascript','java','node.js'),
        'titles': ('software','developer','programmer','web application','web developer','application engineer','webmaster','computer programmer','computer systems analyst'),
    },
    'data': {
        'signals': ('data analyst','data analysis','power bi','tableau','pandas','data visualization','etl','data science','business intelligence','data modeling','statistics','power query','dax'),
        'titles': ('data scientist','data analyst','business intelligence','data engineer','database','statistician','operations research analyst','business analyst','market research analyst'),
    },
    'marketing': {
        'signals': ('marketing','seo','search engine optimization','content marketing','social media marketing','branding','advertising','google ads','email marketing','public relations','campaign'),
        'titles': ('marketing','advertising','promotions','public relations','search marketing','market research','communications specialist'),
    },
    'accounting': {
        'signals': ('accounting','bookkeeping','billing','accounts payable','accounts receivable','financial reporting','invoice','taxation'),
        'titles': ('accounting','bookkeeping','bookkeeper','billing','payroll','financial clerk','accounts','tax preparer'),
    },
    'customer_service': {
        'signals': ('customer service','customer support','call handling','complaint resolution','customer care','customer relations','client service'),
        'titles': ('customer service','customer support','customer representative','customer contact','receptionist','information clerk'),
    },
    'administration': {
        'signals': ('data entry','office assistant','office administration','administrative assistant','word processing','ms word','microsoft word','excel','office clerk','clerical'),
        'titles': ('office clerk','administrative assistant','administrative support','data entry','secretar','office assistant','receptionist','information clerk'),
    },
    'it_support': {
        'signals': ('computer support','technical support','it support','troubleshooting','computer hardware','help desk','ticketing systems','technical troubleshooting'),
        'titles': ('computer user support','computer network support','help desk','technical support','computer support','information technology support'),
    },
    'web_entry': {
        'signals': ('html','css','web design','web development','front end','frontend','web page'),
        'titles': ('web developer','web designer','webmaster','web and digital interface'),
    },
}


def _phrase_present(text, phrase):
    return bool(re.search(r'(?<![\w])' + re.escape(phrase) + r'(?![\w])', text))


def _domain_evidence(text, known):
    corpus = text.casefold()
    skill_text = ' '.join(known)
    strengths = {}
    for domain, profile in DOMAIN_PROFILES.items():
        signals = [term for term in profile['signals'] if _phrase_present(corpus, term) or _phrase_present(skill_text, term)]
        # Require at least two distinct signals; a single generic keyword does
        # not establish a field. Scores reflect evidence only.
        strengths[domain] = min(5, len(signals)) if len(signals) >= 2 else 0
    return strengths


def _occupation_domain(title):
    title = title.casefold()
    matches = []
    for domain, profile in DOMAIN_PROFILES.items():
        if any(term in title for term in profile['titles']):
            matches.append(domain)
    return matches


def _ranking_score(title, skills, matched, strengths):
    """Rank using occupation evidence first; career family only breaks close ties.

    Scores are heuristic ordering aids, not calibrated suitability probabilities.
    Distinct matched requirements/coverage and role-specific evidence produce
    distinct scores when the data supports distinguishing two occupations.
    """
    domains = _occupation_domain(title)
    total = max(len(skills), 1)
    matched_count = len(matched)
    coverage = (matched_count / total) * min(1.0, matched_count / 3.0)
    breadth = min(matched_count / 8, 1.0)
    # Distinct title-specific overlap matters even for large O*NET skill sets.
    rarity_adjusted = sum(evidence_weight(skill) / (1.0 + 0.025 * len(skill)) for skill in matched) / 8
    rarity_adjusted = min(1.0, rarity_adjusted)
    aligned = max((strengths.get(d, 0) for d in domains), default=0)
    strongest = max(strengths.values(), default=0)
    alignment = 'aligned' if aligned >= 2 else ('unconfirmed' if strongest >= 2 else 'undetermined')
    # The alignment bonus is bounded; it cannot dominate occupation evidence.
    domain_component = 0.12 * (aligned / 5) if aligned >= 2 else 0
    misalignment_multiplier = 0.75 if strongest >= 2 and not aligned else 1.0
    score_parts = {
        'catalog_coverage': round(100 * 0.48 * coverage, 2),
        'matched_skill_breadth': round(100 * 0.30 * breadth, 2),
        'specific_skill_evidence': round(100 * 0.10 * rarity_adjusted, 2),
        'domain_alignment': round(100 * domain_component, 2),
    }
    raw = 100 * (0.48 * coverage + 0.30 * breadth + 0.10 * rarity_adjusted + domain_component)
    return round(min(100, raw * misalignment_multiplier), 1), domains, alignment, score_parts


# Only aliases that describe the SAME O*NET-level role belong here.
# Related specialties (medical receptionist, executive assistant, web designer,
# webmaster, data analyst/BI analyst) intentionally remain distinct.
_EQUIVALENT_OCCUPATION_TITLES = {
    'receptionist': 'receptionists and information clerk',
    'receptionists': 'receptionists and information clerk',
    'receptionist and information clerk': 'receptionists and information clerk',
    'general office clerk': 'office clerks general',
    'general office clerks': 'office clerks general',
    'office clerk general': 'office clerks general',
    'office clerks general': 'office clerks general',
}

_TITLE_ACRONYMS = frozenset({'it', 'qa', 'ui', 'ux', 'hr', 'seo', 'sql', 'api', 'crm', 'erp', 'gis'})


def _professional_occupation_title(title):
    """Repair fully lowercase imported titles; preserve official title casing.

    Never invent or rewrite the catalog occupation's identity, evidence, or
    score. This function changes only the name presented to the user.
    """
    title = str(title).strip()
    if not title or title != title.lower():
        return title
    return re.sub(r"[A-Za-z]+(?:'[A-Za-z]+)?", lambda match: (
        match.group().upper() if match.group().casefold() in _TITLE_ACRONYMS
        else match.group()[0].upper() + match.group()[1:]
    ), title)


def _occupation_identity(title):
    """Conservative role identity for deduplicating equivalent occupation names.

    Publisher IDs remain distinct in the catalog; this collapses only identical
    title forms and a small, reviewed set of equivalent labels in the results.
    Broad occupation-title synonym tables MUST NOT be used as identities.
    """
    normalized = re.sub(r'[^\w\s]+', ' ', str(title).casefold())
    words = normalized.split()
    if not words:
        return ''
    # Normalize only final-word singular/plural (do not stem the whole title).
    if words[-1].endswith('ies') and len(words[-1]) > 5:
        words[-1] = words[-1][:-3] + 'y'
    elif words[-1].endswith('s') and not words[-1].endswith(('ss', 'us')) and len(words[-1]) > 4:
        words[-1] = words[-1][:-1]
    key = ' '.join(words)
    return _EQUIVALENT_OCCUPATION_TITLES.get(key, key)


def _deduplicate_career_candidates(candidates):
    """Pick one real catalog candidate per conservative identity.

    Keep the original candidate's score, skill list, evidence, and source;
    never combine claims from two occupation records. Prefer professionally
    formatted publisher titles for near-equal scores.
    """
    grouped = {}
    for candidate in candidates:
        score, matched_count, name, job = candidate
        identity = _occupation_identity(job['title'])
        old = grouped.get(identity)
        if old is None:
            grouped[identity] = candidate
            continue
        old_score, old_count, _, old_job = old
        close = abs(score - old_score) <= 2
        old_presentation = old_job['title'] != old_job['title'].lower()
        presentation = job['title'] != job['title'].lower()
        if ((close and presentation and not old_presentation)
                or (not close and (score, matched_count) > (old_score, old_count))
                or (close and presentation == old_presentation
                    and (score, matched_count) > (old_score, old_count))):
            grouped[identity] = candidate
    return list(grouped.values())


def _skill_keys(text, db_path=None):
    seed_skills(db_path)
    return {s.casefold() for s in extract_skills(text, db_path=db_path)}


# Generate catalog lookup variants from the same reviewed alias library as
# Job Matching; no separate, divergent shortlist of eight synonyms.
def _onet_query_keys(text, extracted):
    # Preserve direct mentions of reviewed brand shorthands even when a caller
    # passes a partial extracted set (legacy integration contract).
    observed = set(extracted)
    for short, official in (('ms word', 'microsoft word'),
                            ('ms excel', 'microsoft excel'),
                            ('powerbi', 'power bi'), ('power bi', 'power bi'),
                            ('postgres', 'postgresql'), ('html', 'html'),
                            ('css', 'css')):
        if phrase_present(text, short):
            observed.add(official)
    return catalogue_query_keys(observed)


def rank_careers(resume_text: str, *, db_path=None, limit=8):
    """Rank catalog roles with explicit matches, conservative coverage, and evidence.

    We never infer education/licensing or predict hiring probability. The database
    query fetches only occupations linked to detected skills rather than loading
    every relation into application memory.
    """
    if not resume_text or not resume_text.strip():
        raise ValueError('Resume has no extractable text')
    known = _skill_keys(resume_text, db_path)
    strengths = _domain_evidence(resume_text, known)
    bounded_limit = max(1, min(20, int(limit)))
    candidates = []
    query_keys = _onet_query_keys(resume_text, known)
    diagnostics = {'extracted_skills': len(known), 'onet_query_terms': len(query_keys),
                   'catalog_skill_matches': 0, 'occupations_retrieved': 0,
                   'occupations_after_filter': 0, 'fallback_reason': ''}
    if query_keys:
        with connect(db_path) as db:
            ensure_tables(db)
            # Query in batches to respect SQLite bind-parameter limits.
            found = {}
            keys = sorted(query_keys)
            matched_skill_ids = set()
            for pos in range(0, len(keys), 400):
                batch = keys[pos:pos+400]
                marks = ','.join('?' for _ in batch)
                # Publisher names and publisher-provided alternate labels both
                # resolve to one catalog skill ID. A returned occupation counts
                # each linked skill only once, even if multiple aliases match.
                base = f"""SELECT o.id, o.name, o.source,
                    s.name AS skill, s.id AS skill_id
                    FROM tax_skills s
                    JOIN tax_links l ON l.skill_id = s.id
                    JOIN tax_occupations o ON o.id = l.occupation_id
                    WHERE {{condition}}"""
                for condition, values in (
                    (f's.normalized IN ({marks})', batch),
                    (f's.id IN (SELECT skill_id FROM tax_skill_aliases WHERE alias IN ({marks}))', batch),
                ):
                    rows = db.execute(base.format(condition=condition), values).fetchall()
                    for row in rows:
                        record = found.setdefault(row['id'], {
                            'title': row['name'], 'source': row['source'],
                            'matched': set(), 'matched_ids': set()})
                        record['matched'].add(row['skill'])
                        record['matched_ids'].add(row['skill_id'])
                        matched_skill_ids.add(row['skill_id'])
            diagnostics['catalog_skill_matches'] = len(matched_skill_ids)
            diagnostics['occupations_retrieved'] = len(found)
            if found:
                ids = list(found)
                for pos in range(0, len(ids), 400):
                    batch = ids[pos:pos+400]
                    marks = ','.join('?' for _ in batch)
                    rows = db.execute(f"""SELECT l.occupation_id, s.name
                        FROM tax_links l JOIN tax_skills s ON s.id=l.skill_id
                        WHERE l.occupation_id IN ({marks})""", batch).fetchall()
                    for row in rows:
                        found[row['occupation_id']].setdefault('skills', set()).add(row['name'])
            for group in found.values():
                skills = group.get('skills', set())
                matched = sorted(group['matched'], key=str.casefold)
                missing = sorted(skills - group['matched'], key=str.casefold)
                total = len(skills)
                if total == 0:
                    continue
                coverage = len(matched)/total
                # Avoid a one-of-one role outranking a role supported by many
                # distinct resume skills. Still show observed coverage separately.
                breadth = min(len(matched)/5, 1.0)
                score, domains, alignment, breakdown = _ranking_score(group['title'], skills, matched, strengths)
                # The same reviewed core profile used by title-only Job Studio
                # supplies a small *evidence-backed* tie-breaker here. Do not
                # award points for a role title alone or for generic keywords.
                core_matched, core_missing = core_evidence(group['title'], known)
                core_total = len(core_matched) + len(core_missing)
                # Use the same reviewed *core evidence* as title-only Job Studio
                # without presenting the resulting career rank as a hiring score.
                # This also avoids generic, long imported software lists diluting
                # essential role coverage. Unrecognized jobs use catalog ranking.
                if core_total:
                    core_pct = 100 * len(core_matched) / core_total
                    score = round(0.55 * score + 0.45 * core_pct, 1)
                    breakdown['reviewed_role_core_evidence'] = round(0.45 * core_pct, 2)
                    breakdown['reviewed_role_core_coverage'] = round(core_pct)
                else:
                    breakdown['reviewed_role_core_evidence'] = 0.0
                # A weak, stated-role context tie-breaker; never a qualification.
                focus = occupation_focus(group['title'], resume_text)
                score = round(min(100, score + 2.0 * focus), 1)
                breakdown['resume_role_context'] = round(2.0 * focus, 2)
                # A few generic catalog overlaps must never be converted into
                # unrelated career advice. Strong domain evidence or multiple
                # concrete occupation matches are necessary before display.
                concrete = [term for term in matched if evidence_weight(term) >= 0.9]
                has_domain = alignment == 'aligned'
                if (not has_domain and (len(concrete) < 2 or score < 20)) or score < 12:
                    continue
                candidates.append((score, len(matched), group['title'].casefold(), {
                    'title': group['title'],
                    'reason': f"Matched {len(matched)} of {total} catalogued skills from {group['source']}. No eligibility decision was made.",
                    'skills_detected': matched, 'high_signal_skills': [s for s in matched if evidence_weight(s) >= 0.9],
                    'skills_not_detected': occupation_learning_topics(group['title'], skills, matched, resume_text),
                    'skills_coverage': round(100*coverage),
                    'match_strength': score, 'score_breakdown': breakdown,
                    'domain_alignment': alignment, 'occupation_domains': domains,
                    'matched_skill_count': len(matched),
                    'catalog_skill_count': total,
                    'core_skills_matched': core_matched,
                    'core_skills_not_detected': core_missing,
                    'core_skill_coverage': round(100 * len(core_matched) / core_total) if core_total else None,
                    'learning_topic_basis': 'Optional topics are selected from occupation-catalog skills and curated field priorities; not verified requirements.',
                    'eligibility': 'Education, experience and licensing not assessed.',
                    'evidence_source': group['source'],
                }))
    diagnostics['occupations_after_filter'] = len(candidates)
    candidates = _deduplicate_career_candidates(candidates)
    diagnostics['unique_occupations'] = len(candidates)
    candidates.sort(key=lambda item: (-item[0], -item[1], item[2]))
    source = 'ONET/ESCO-imported-catalog' if candidates else 'curated-offline-catalog'
    if not candidates:
        diagnostics['fallback_reason'] = (
            'No resume skills were identified' if not known else
            'No extracted skills or verified aliases matched O*NET' if not diagnostics['occupations_retrieved'] else
            'O*NET occupations were retrieved but none passed the minimum evidence checks'
        )
        for title, skills in ROLE_MAP.items():
            matched = [skill for skill in skills if canonical_key(skill) in {canonical_key(k) for k in known}]
            if len(matched) >= 2:
                coverage = len(matched)/len(skills)
                score, domains, alignment, breakdown = _ranking_score(title, skills, matched, strengths)
                candidates.append((score,len(matched),title.casefold(),{
                    'title':title.title(), 'reason':'Matched explicitly detected resume skills from the curated role library.',
                    'skills_detected':matched, 'skills_not_detected':[s for s in skills if s not in matched],
                    'skills_coverage':round(100*coverage), 'match_strength':score, 'score_breakdown':breakdown,
                    'matched_skill_count':len(matched), 'catalog_skill_count':len(skills),
                    'domain_alignment':alignment, 'occupation_domains':domains,
                    'eligibility':'Education, experience and licensing not assessed.',
                    'evidence_source':'curated-role-library'}))
        candidates = _deduplicate_career_candidates(candidates)
        diagnostics['unique_occupations'] = len(candidates)
        candidates.sort(key=lambda item:(-item[0],-item[1],item[2]))
    return {'jobs':[{**item[3], 'title': _professional_occupation_title(item[3]['title'])} for item in candidates[:bounded_limit]],
            'resume_skills': sorted(known), 'source':source, 'diagnostics': diagnostics,
            'warning':'' if candidates else 'Insufficient occupation-specific evidence for reliable career recommendations. Add relevant skills, projects, or experience; no unrelated careers will be suggested.',
            'methodology':'Low-evidence and unrelated occupations are filtered. Base ranking combines occupation catalog coverage (48%), matched skill breadth (30%), specificity-weighted evidence (10%) and career-family alignment (up to 12 points). Recognized roles then blend 55% of that base ranking with 45% reviewed core skill coverage; unknown roles retain catalog scoring. A bounded 2-point stated-role tie-break is applied. Learning topics use field-specific priorities when listed in the occupation catalog; absence from a resume does not prove missing proficiency. No education or seniority inference. Heuristic ranking, not a hiring probability.',
            'disclaimer':DISCLAIMER}
