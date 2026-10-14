"""Conservative occupation evidence selectors. No fabricated qualifications or API calls."""
import re

# Broad catalog entries should never be sold as required skills or strong evidence.
GENERIC = frozenset({'science','biology','active listening','active learning','critical thinking',
 'administration and management','administrative','computers and electronics',
 'customer and personal service','building and construction','writing','google',
 'communication','communications and media','design'})
# High specificity technical signals. These are not an exhaustive list: novel concrete
# technologies still get a nonzero weight, unlike generic transferable labels.
TECH_MARKERS = ('python','fastapi','django','flask','sql','postgres','redis','docker','git',
 'linux','api','java','javascript','node','react','azure','aws','power bi','tableau',
 'pandas','numpy','excel','etl','analytics','visualization','google ads','seo',
 'search engine','email marketing','campaign','social media','instagram','canva',
 'marketing','statistics','testing','scripting','database','cloud','kubernetes')


def evidence_weight(skill):
    term = skill.casefold().strip()
    if term in GENERIC or len(term) < 3:
        return 0.1
    if any(marker in term for marker in TECH_MARKERS):
        return 1.0
    return 0.55


def occupation_focus(title, resume_text):
    """Weak title-level intent tie breaker, NOT evidence of a qualification."""
    text = resume_text.casefold()
    title = title.casefold()
    categories = (
        (('backend developer','backend engineer','back-end developer'), ('software developer','software engineer','application developer','computer programmer')),
        (('data analyst','business intelligence analyst','bi analyst'), ('business intelligence','data analyst','data scientists','operations research')),
        (('marketing coordinator','digital marketing','marketing specialist'), ('marketing specialist','market research analyst','search marketing','public relations specialist')),
    )
    for tokens, occupations in categories:
        if any(re.search(r'(?<!\w)' + re.escape(t) + r'(?!\w)', text) for t in tokens):
            return 1.0 if any(o in title for o in occupations) else 0.0
    return 0.0


def useful_gaps(skills, matched, limit=8):
    """Potential learning topics, not verified requirements or proof of deficiency."""
    found = {s.casefold() for s in matched}
    candidates = [s for s in skills if s.casefold() not in found and evidence_weight(s) >= 0.9]
    return sorted(candidates, key=lambda s: (len(s) > 44, len(s), s.casefold()))[:limit]


# Practical learning priorities, not employment requirements. Exact terms must
# occur in the imported occupation list; no missing competency is invented.
CAREER_LEARNING_PRIORITIES = {
    'software': ('rest api','api development','fastapi','django','flask','python',
       'postgresql','sql','sqlalchemy','redis','docker','git','github','linux',
       'unit testing','testing','security','aws','node.js','javascript','react',
       'mysql','kubernetes','ci/cd','microservices'),
    'data': ('sql','microsoft excel','power bi','microsoft power bi','tableau',
       'pandas','numpy','python','statistics','data visualization','data analysis',
       'etl','power query','dax','data modeling','data warehousing','bigquery',
       'business intelligence','r','matplotlib','apache spark'),
    'marketing': ('search engine optimization','seo','google analytics','google ads',
       'digital marketing','social media marketing','email marketing',
       'content marketing','copywriting','market research','campaign',
       'canva','advertising','brand management','adobe photoshop',
       'marketing automation','social media sites','public relations'),
}

# Normalize known synonyms only for comparative evidence. A skill not explicitly
# supported by the resume must never be asserted as possessed.
SKILL_EQUIVALENTS = {
    'powerbi':'power bi', 'microsoft power bi':'power bi',
    'ms excel':'microsoft excel', 'excel':'microsoft excel',
    'postgres':'postgresql', 'postgresql database':'postgresql',
    'google analytics 4':'google analytics', 'ga4':'google analytics',
    'restful api':'rest api', 'restful apis':'rest api',
    'search engine optimization':'seo',
}


def canonical_skill(skill):
    term = ' '.join(skill.casefold().strip().split())
    return SKILL_EQUIVALENTS.get(term, term)


def occupation_learning_topics(title, skills, matched, resume_text='', limit=6):
    """Catalog-grounded learning ideas ranked for the *occupation*, not alphabetically.

    Fallback for unfamiliar occupations is intentionally small and explicitly
    provisional. Never represent absence on a resume as proof of a skill gap.
    """
    from app.services.hybrid_intelligence import _occupation_domain, _domain_evidence
    domains = _occupation_domain(title)
    strengths = _domain_evidence(resume_text, set()) if resume_text else {}
    # Occupational title takes precedence over candidate background.
    domain = next((d for d in ('marketing','software','data') if d in domains), None)
    if domain is None:
        domain = max(strengths, key=strengths.get) if strengths and max(strengths.values()) >= 2 else None
    priorities = CAREER_LEARNING_PRIORITIES.get(domain, ())
    known = {canonical_skill(x) for x in matched}
    # Resume text can reveal a canonical alias even when O*NET uses another label;
    # using boundary-aware patterns avoids substring false positives.
    import re
    lower_text = resume_text.casefold()
    for alias, canonical in SKILL_EQUIVALENTS.items():
        if re.search(r'(?<!\w)' + re.escape(alias) + r'(?!\w)', lower_text):
            known.add(canonical)
    indexed = {}
    for skill in skills:
        indexed.setdefault(canonical_skill(skill), []).append(skill)
    ordered = []
    for priority in priorities:
        key = canonical_skill(priority)
        if key not in known and key in indexed:
            choice = sorted(indexed[key],key=lambda x:(len(x),x.casefold()))[0]
            if choice not in ordered:ordered.append(choice)
        if len(ordered)>=limit:break
    # An unrecognized domain should not be filled with arbitrary unrelated tech.
    return ordered
