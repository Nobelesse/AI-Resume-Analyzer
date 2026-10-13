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
