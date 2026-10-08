"""Offline occupational skill suggestions, distinct from employer requirements.

This is a curated starter role library; optional local Ollama improves unusual titles.
"""
import json
import re
import urllib.error
import urllib.request

ROLE_MAP = {
 'software engineer': ('Python','Java','Git','SQL','Problem Solving','REST API','Testing','Docker','Communication'),
 'python developer': ('Python','Git','SQL','Django','Flask','FastAPI','REST API','Testing','Docker'),
 'backend developer': ('Python','Java','SQL','REST API','Git','Docker','PostgreSQL','Authentication','Microservices'),
 'frontend developer': ('HTML','CSS','JavaScript','TypeScript','React','Responsive Design','Git','Accessibility'),
 'full stack developer': ('HTML','CSS','JavaScript','React','Node.js','SQL','Git','REST API','Docker'),
 'web developer': ('HTML','CSS','JavaScript','Git','React','REST API','Responsive Design'),
 'mobile app developer': ('Kotlin','Swift','Dart','Flutter','Git','REST API','UI Design'),
 'android developer': ('Kotlin','Java','Git','REST API','SQLite','UI Design'),
 'ios developer': ('Swift','Git','REST API','UI Design'),
 'data analyst': ('SQL','Microsoft Excel','Python','Power BI','Tableau','Data Analysis','Statistics','Data Visualization','Communication'),
 'business analyst': ('Business Analysis','SQL','Microsoft Excel','Stakeholder Management','Documentation','Power BI','Requirements Gathering'),
 'data scientist': ('Python','SQL','Statistics','Machine Learning','Pandas','Scikit-learn','Data Visualization','Model Evaluation'),
 'machine learning engineer': ('Python','Machine Learning','PyTorch','TensorFlow','Scikit-learn','MLOps','Docker','Model Evaluation'),
 'ai engineer': ('Python','Machine Learning','Deep Learning','PyTorch','LLMs','RAG','Prompt Engineering','Vector Databases'),
 'data engineer': ('Python','SQL','ETL','Apache Spark','Data Warehousing','Apache Airflow','Cloud Computing'),
 'database administrator': ('SQL','PostgreSQL','MySQL','Database Administration','Backup and Recovery','Database Performance'),
 'devops engineer': ('Linux','Docker','Kubernetes','Git','CI/CD','Terraform','Jenkins','AWS','Monitoring'),
 'cloud engineer': ('AWS','Microsoft Azure','Google Cloud Platform','Linux','Docker','Terraform','Networking'),
 'site reliability engineer': ('Linux','Kubernetes','Docker','Prometheus','Grafana','Python','CI/CD','Incident Response'),
 'cybersecurity analyst': ('Cybersecurity','Network Security','SIEM','Incident Response','Risk Assessment','Vulnerability Assessment','Splunk'),
 'security engineer': ('Cybersecurity','Network Security','Penetration Testing','Threat Modeling','OWASP Top 10','Encryption'),
 'penetration tester': ('Penetration Testing','Burp Suite','Wireshark','Vulnerability Assessment','Network Security','Python'),
 'network engineer': ('Network Security','Networking','Linux','Cisco','Routing','Switching','Troubleshooting'),
 'qa engineer': ('Quality Assurance','Testing','Test Automation','Python','Selenium','Git','Bug Tracking'),
 'software tester': ('Testing','Quality Assurance','Test Cases','Bug Tracking','Selenium','Automation Testing'),
 'ui ux designer': ('Figma','UI Design','UX Design','Wireframing','Prototyping','User Research','Accessibility'),
 'graphic designer': ('Graphic Design','Adobe Photoshop','Adobe Illustrator','Canva','Branding','Typography'),
 'product manager': ('Product Management','Market Research','Stakeholder Management','Agile','Scrum','Roadmapping','Communication'),
 'project manager': ('Project Management','Budgeting','Leadership','Risk Management','Stakeholder Management','Agile','Jira'),
 'digital marketer': ('Digital Marketing','Search Engine Optimization','Google Analytics','Google Ads','Content Marketing','Social Media Marketing'),
 'seo specialist': ('Search Engine Optimization','Google Analytics','Content Marketing','Keyword Research','Search Engine Marketing'),
 'content writer': ('Copywriting','Content Marketing','Research Methods','Search Engine Optimization','Communication','Editing'),
 'social media manager': ('Social Media Marketing','Content Marketing','Branding','Marketing Analytics','Communication'),
 'sales executive': ('CRM','Salesforce','Negotiation','Communication','Customer Service','Sales Strategy'),
 'customer support representative': ('Customer Service','Customer Support','Communication','Problem Solving','CRM','Conflict Resolution'),
 'hr manager': ('Human Resources','Recruitment','Performance Management','Employee Relations','Leadership','Labor Law'),
 'recruiter': ('Recruitment','Talent Acquisition','Interviewing','Communication','ATS','Candidate Sourcing'),
 'accountant': ('Accounting','Bookkeeping','Financial Reporting','Taxation','Microsoft Excel','Auditing','Budgeting'),
 'financial analyst': ('Financial Analysis','Financial Modeling','Microsoft Excel','Budgeting','Forecasting','Financial Reporting'),
 'investment analyst': ('Investment Analysis','Financial Modeling','Financial Analysis','Risk Management','Market Research'),
 'operations manager': ('Operations Management','Supply Chain Management','Inventory Management','Leadership','Budgeting','Quality Control'),
 'supply chain analyst': ('Supply Chain Management','Microsoft Excel','SQL','Inventory Management','Data Analysis','Forecasting'),
 'logistics coordinator': ('Logistics','Inventory Management','Supply Chain Management','Communication','Operations Management'),
 'mechanical engineer': ('Mechanical Engineering','SolidWorks','AutoCAD','CAD','Finite Element Analysis','Quality Control'),
 'civil engineer': ('Civil Engineering','AutoCAD','Project Management','Structural Analysis','Surveying','CAD'),
 'electrical engineer': ('Electrical Engineering','Electronics','MATLAB','AutoCAD','PLC','Circuit Design'),
 'electronics engineer': ('Electronics','Embedded Systems','PCB Design','Arduino','MATLAB','Circuit Design'),
 'robotics engineer': ('Robotics','Python','ROS','Embedded Systems','C++','Computer Vision'),
 'teacher': ('Teaching','Curriculum Development','Instructional Design','Classroom Management','Communication'),
 'professor': ('Teaching','Research Methods','Curriculum Development','Academic Writing','Mentoring'),
 'nurse': ('Nursing','Patient Care','Electronic Health Records','Clinical Documentation','Communication'),
 'medical coder': ('Medical Coding','Electronic Health Records','Clinical Documentation','Healthcare Analytics'),
 'pharmacist': ('Pharmacology','Patient Care','Medication Safety','Inventory Management','Communication'),
 'doctor': ('Patient Care','Clinical Research','Medical Imaging','Electronic Health Records','Communication'),
 'research scientist': ('Research Methods','Statistics','Data Analysis','Scientific Writing','Experiment Design'),
 'lawyer': ('Legal Research','Contract Drafting','Negotiation','Communication','Legal Writing'),
 'architect': ('AutoCAD','CAD','3D Modeling','Building Information Modeling','Project Management'),
 'video editor': ('Video Editing','Adobe Premiere Pro','Adobe After Effects','Motion Graphics','Storytelling'),
 'photographer': ('Photography','Adobe Photoshop','Lighting','Photo Editing','Creative Direction'),
 'chef': ('Food Safety','Menu Planning','Inventory Management','Culinary Arts','Teamwork'),
 'hotel manager': ('Hospitality Management','Customer Service','Operations Management','Budgeting','Leadership'),
 'receptionist': ('Customer Service','Communication','Scheduling','Microsoft Excel','Organization'),
 'administrative assistant': ('Scheduling','Microsoft Excel','Communication','Documentation','Time Management'),
 'electrician': ('Electrical Wiring','Electrical Safety','Circuit Testing','Troubleshooting','Electrical Engineering'),
 'plumber': ('Plumbing','Pipe Fitting','Blueprint Reading','Troubleshooting','Safety Compliance'),
 'automotive technician': ('Vehicle Diagnostics','Mechanical Engineering','Troubleshooting','Preventive Maintenance'),
 'agricultural engineer': ('Agriculture','Irrigation','GIS','Precision Agriculture','Soil Science','Data Analysis'),
}

# Normalize simple natural-language variants, without claiming coverage for all occupations.
ALIASED_ROLES = {
 'sde':'software engineer','software developer':'software engineer','programmer':'software engineer',
 'python engineer':'python developer','back end developer':'backend developer','front end developer':'frontend developer',
 'fullstack developer':'full stack developer','ml engineer':'machine learning engineer',
 'artificial intelligence engineer':'ai engineer','business intelligence analyst':'data analyst',
 'bi analyst':'data analyst','data analytics specialist':'data analyst',
 'security analyst':'cybersecurity analyst','ethical hacker':'penetration tester',
 'human resources manager':'hr manager','human resources executive':'hr manager',
 'talent acquisition specialist':'recruiter','marketing executive':'digital marketer',
 'ux designer':'ui ux designer','ui designer':'ui ux designer','accounting specialist':'accountant',
 'registered nurse':'nurse','physician':'doctor','software quality assurance engineer':'qa engineer',
}


def normalize_title(title: str) -> str:
    value = re.sub(r'[^\w\s+#]', ' ', title.casefold())
    value = re.sub(r'\b(senior|junior|entry level|intern|lead|principal|associate|remote|fresher|staff)\b', ' ', value)
    return ' '.join(value.split())


def suggest_for_title(title: str) -> dict:
    normalized = normalize_title(title)
    normalized = ALIASED_ROLES.get(normalized, normalized)
    if normalized in ROLE_MAP:
        return {'skills': list(ROLE_MAP[normalized]), 'role': normalized, 'source': 'curated-role-library', 'confidence': 'high'}
    candidates = [(len(key.split()), len(key), key) for key in ROLE_MAP if re.search(r'(?<!\w)'+re.escape(key)+r'(?!\w)', normalized)]
    if candidates:
        key = max(candidates)[2]
        return {'skills': list(ROLE_MAP[key]), 'role': key, 'source': 'curated-role-library', 'confidence': 'medium'}
    return {'skills': [], 'role': normalized, 'source': 'unknown-role', 'confidence': 'none'}


def suggest_with_ollama(title: str, *, model: str = 'llama3.2', endpoint: str = 'http://127.0.0.1:11434', timeout: float = 12) -> dict:
    """Optional local language-model suggestions. Never silently call a cloud service."""
    if not re.fullmatch(r'[a-zA-Z0-9_.:\-]+', model):
        raise ValueError('Invalid local model name')
    if endpoint.rstrip('/') not in ('http://127.0.0.1:11434','http://localhost:11434'):
        raise ValueError('Only local Ollama endpoints are allowed')
    prompt = ("Suggest 6-15 typical skills for the occupation below. Never assert they are employer-stated requirements. "
              "Return a JSON object with only a skills array of strings. Job title: " + json.dumps(title[:150]))
    body = json.dumps({'model':model, 'prompt':prompt, 'stream':False,'format':'json'}).encode()
    req = urllib.request.Request(endpoint.rstrip('/') + '/api/generate', body, {'Content-Type':'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            response_body = response.read(35000)
        parsed = json.loads(json.loads(response_body).get('response','{}'))
        skills = parsed.get('skills', [])
        if not isinstance(skills,list): raise ValueError('Local model gave an invalid response')
        cleaned = list(dict.fromkeys(' '.join(s.split())[:100] for s in skills if isinstance(s,str) and 2<=len(s.strip())<=100))[:20]
        return {'skills':cleaned,'role':title,'source':'local-ollama-suggestions','confidence':'unverified'}
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        raise ValueError('Local Ollama is unavailable or returned invalid skill suggestions: '+str(exc)) from exc
