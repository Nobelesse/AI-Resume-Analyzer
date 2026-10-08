"""Interpretable ATS-readiness heuristics; never imply vendor ATS certification."""
import re
from app.services.skills import extract_skills
SECTIONS={'summary':r'(?im)^\s*(?:professional\s+)?(?:summary|profile|objective)\s*:?[ \t]*$', 'skills':r'(?im)^\s*(?:technical\s+|core\s+)?skills(?:\s+and\s+technologies)?\s*:?[ \t]*$', 'experience':r'(?im)^\s*(?:work\s+|professional\s+)?(?:experience|employment|internships?)\s*:?[ \t]*$', 'education':r'(?im)^\s*(?:education|academic\s+background|qualifications)\s*:?[ \t]*$', 'projects':r'(?im)^\s*(?:projects|personal\s+projects|academic\s+projects)\s*:?[ \t]*$'}
def analyze_text(text,*,db_path=None):
    if not text or not text.strip():raise ValueError('No extracted resume text available')
    skills=extract_skills(text,db_path=db_path)
    sections={label:bool(re.search(pattern,text)) for label,pattern in SECTIONS.items()}
    words=re.findall(r'\b[\w+#.-]+\b',text)
    email=bool(re.search(r'(?i)\b[\w.+-]+@[\w.-]+\.[a-z]{2,}\b',text))
    phone=bool(re.search(r'(?<!\d)(?:\+?\d[\s().-]?){10,14}(?!\d)',text))
    has_bullets=bool(re.search(r'(?m)^\s*(?:[-*•]|\d+[.)])\s+',text))
    has_metrics=bool(re.search(r'\b\d+(?:\.\d+)?\s*(?:%|percent|users|clients|projects|hours|days|revenue|requests)\b',text,re.I))
    # weighted heuristic components (sum = 100)
    components={'Resume sections':sum(sections.values())*7, 'Contact details':int(email)*10+int(phone)*5,'Skill evidence':min(len(skills),10)*2,'Substance':15 if len(words)>=250 else 8 if len(words)>=100 else 0,'Bullet formatting':10 if has_bullets else 0,'Quantified impact':5 if has_metrics else 0}
    score=min(100,sum(components.values()))
    advice=[]
    for name,exists in sections.items():
        if not exists:advice.append(f'Add a clearly labeled {name.title()} section if relevant.')
    if not email:advice.append('Include a professional contact email.')
    if not phone:advice.append('Consider including a contact phone number.')
    if len(words)<100:advice.append('Provide more specific evidence of projects, education, and experience.')
    if not has_bullets:advice.append('Use readable bullet points for achievements and responsibilities.')
    if not has_metrics:advice.append('Where truthful, quantify measurable outcomes with numbers.')
    if not skills:advice.append('Use unambiguous names for relevant demonstrated skills.')
    return {'score':score,'sections':sections,'skills':skills,'components':components,'recommendations':advice,'word_count':len(words),'disclaimer':'Estimated ATS-readiness heuristic; not a prediction of hiring or any vendor ATS score.'}
