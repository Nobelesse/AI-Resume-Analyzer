"""Versioned curated seed taxonomy; unlimited indexed SQLite imports supported."""
import csv
import re
from pathlib import Path
from app.database.connection import connect

SEED = {
'Programming': 'Python, Java, JavaScript, TypeScript, C, C++, C#, Go, Rust, Kotlin, Swift, PHP, Ruby, R, MATLAB, Scala, Dart, Bash, PowerShell, SQL, HTML, CSS, Solidity, Perl, Lua, Haskell, Julia, Objective-C, Visual Basic, Assembly, VBA',
'Backend & APIs': 'Django, Flask, FastAPI, Spring Boot, ASP.NET Core, Express.js, NestJS, Node.js, REST API, GraphQL, gRPC, Microservices, WebSockets, Authentication, Authorization, OAuth 2.0, JWT, Redis, Celery, RabbitMQ, Apache Kafka, Nginx, Apache HTTP Server, Gunicorn, Uvicorn, OpenAPI, Swagger, Postman',
'Frontend & UI': 'React, Angular, Vue.js, Next.js, Nuxt, Svelte, Tailwind CSS, Bootstrap, jQuery, Redux, Zustand, Streamlit, Gradio, Figma, UI Design, UX Design, Responsive Design, Accessibility, Web Components, Vite, Webpack, Three.js, D3.js',
'Data & AI': 'Machine Learning, Deep Learning, Artificial Intelligence, Natural Language Processing, Computer Vision, Data Analysis, Data Science, Data Engineering, Data Visualization, Statistics, Probability, Linear Algebra, Scikit-learn, TensorFlow, PyTorch, Keras, Pandas, NumPy, Matplotlib, Seaborn, Plotly, OpenCV, XGBoost, LightGBM, CatBoost, Hugging Face, Transformers, spaCy, NLTK, LangChain, RAG, Vector Databases, Prompt Engineering, Feature Engineering, Model Evaluation, MLOps, LLMs, Generative AI, Reinforcement Learning, Time Series Forecasting, A/B Testing',
'Databases & Analytics': 'SQLite, PostgreSQL, MySQL, MariaDB, Microsoft SQL Server, Oracle Database, MongoDB, DynamoDB, Firebase, Firestore, Elasticsearch, Neo4j, Cassandra, ClickHouse, Snowflake, BigQuery, Redshift, DuckDB, Databricks, Apache Spark, Apache Airflow, dbt, ETL, ELT, Power BI, Tableau, Microsoft Excel, Google Sheets, DAX, Power Query, Looker, Qlik Sense, Data Modeling, Data Warehousing, SQLAlchemy',
'Cloud & DevOps': 'AWS, Microsoft Azure, Google Cloud Platform, Docker, Kubernetes, Terraform, Ansible, Jenkins, GitHub Actions, GitLab CI, CI/CD, Linux, Ubuntu, Debian, Windows Server, Bash Scripting, Git, GitHub, GitLab, Bitbucket, Helm, Prometheus, Grafana, OpenTelemetry, Cloud Run, Cloud Functions, AWS Lambda, Amazon EC2, Amazon S3, Azure Functions, Infrastructure as Code, DevSecOps, Site Reliability Engineering',
'Security': 'Cybersecurity, Network Security, Information Security, Penetration Testing, Threat Modeling, Vulnerability Assessment, SIEM, Splunk, Wireshark, Burp Suite, OWASP Top 10, Secure Coding, Encryption, Incident Response, Identity and Access Management, Zero Trust, SOC, Digital Forensics, Malware Analysis, Risk Assessment, GDPR, ISO 27001, NIST',
'Business & Finance': 'Business Analysis, Financial Analysis, Financial Modeling, Accounting, Bookkeeping, Budgeting, Forecasting, Financial Reporting, Taxation, Auditing, Risk Management, Investment Analysis, Market Research, CRM, Salesforce, SAP, ERP, Customer Service, Supply Chain Management, Inventory Management, Operations Management, Business Intelligence, Project Management, Agile, Scrum, Kanban, Jira, Confluence, Product Management, Strategic Planning',
'Creative & Marketing': 'Digital Marketing, Search Engine Optimization, Search Engine Marketing, Content Marketing, Social Media Marketing, Email Marketing, Copywriting, Branding, Graphic Design, Adobe Photoshop, Adobe Illustrator, Adobe Premiere Pro, Adobe After Effects, Canva, Video Editing, Photography, Motion Graphics, Google Analytics, Google Ads, Marketing Analytics, Public Relations',
'Engineering & Science': 'AutoCAD, SolidWorks, CATIA, Fusion 360, Mechanical Engineering, Civil Engineering, Electrical Engineering, Electronics, Embedded Systems, Arduino, Raspberry Pi, Robotics, Internet of Things, PCB Design, CAD, CAM, Finite Element Analysis, Quality Assurance, Quality Control, Lean Manufacturing, Six Sigma, PLC, SCADA, MATLAB Simulink, Geographic Information Systems, ArcGIS, QGIS',
'Healthcare & Education': 'Clinical Research, Patient Care, Medical Coding, Electronic Health Records, Healthcare Analytics, Nursing, Medical Imaging, Laboratory Testing, Pharmacovigilance, Clinical Data Management, Teaching, Instructional Design, Curriculum Development, Educational Technology, Learning Management Systems, Research Methods',
'Professional': 'Active Listening, Complaint Resolution, Call Handling, Email Support, Data Entry, Empathy, Ticketing Systems, Technical Support, Customer Success, Account Management, Customer Retention, Communication, Teamwork, Leadership, Problem Solving, Critical Thinking, Time Management, Adaptability, Collaboration, Presentation Skills, Negotiation, Conflict Resolution, Decision Making, Stakeholder Management, Attention to Detail, Customer Support, Documentation, Mentoring, Analytical Thinking, Creativity, Public Speaking, Organization, Emotional Intelligence'
}
ALIASES = {'js':'JavaScript','ts':'TypeScript','py':'Python','postgres':'PostgreSQL','sklearn':'Scikit-learn','ml':'Machine Learning','nlp':'Natural Language Processing','cv':'Computer Vision','ai':'Artificial Intelligence','genai':'Generative AI','gcp':'Google Cloud Platform','k8s':'Kubernetes','powerbi':'Power BI','ms excel':'Microsoft Excel','excel':'Microsoft Excel','node':'Node.js','reactjs':'React','vue':'Vue.js','golang':'Go','ci cd':'CI/CD','restful api':'REST API','llm':'LLMs','llms':'LLMs','tf':'TensorFlow','pytorch':'PyTorch','github actions':'GitHub Actions'}

def normalize(value):
    return ' '.join(value.casefold().strip().split())

def seed_skills(db_path=None):
    with connect(db_path) as db:
        for category, skill_string in SEED.items():
            for skill in (v.strip() for v in skill_string.split(',')):
                db.execute('INSERT OR IGNORE INTO skills (name,normalized,category,source) VALUES (?,?,?,?)',(skill,normalize(skill),category,'curated-seed-v1'))
        for alias,name in ALIASES.items():
            row=db.execute('SELECT id FROM skills WHERE normalized=?',(normalize(name),)).fetchone()
            if row:db.execute('INSERT OR IGNORE INTO skill_aliases(alias,skill_id) VALUES(?,?)',(normalize(alias),row['id']))

def import_skills_csv(filename, *, db_path=None, source='external'):
    """Import a reviewed CSV with columns name,category,aliases (aliases separated by |).
    Only import trusted catalogs; this is a local admin/maintainer operation.
    """
    count=0
    with Path(filename).open(encoding='utf-8-sig',newline='') as f:
        reader=csv.DictReader(f)
        if not {'name','category'}.issubset(reader.fieldnames or []):raise ValueError('CSV requires name and category columns')
        with connect(db_path) as db:
            for item in reader:
                name=' '.join((item.get('name') or '').split())[:120]
                category=' '.join((item.get('category') or 'Other').split())[:100]
                if len(name)<2 or not category:continue
                db.execute('INSERT OR IGNORE INTO skills(name,normalized,category,source) VALUES(?,?,?,?)',(name,normalize(name),category,source))
                row=db.execute('SELECT id FROM skills WHERE normalized=?',(normalize(name),)).fetchone()
                if row:
                    for alias in (item.get('aliases') or '').split('|'):
                        alias=normalize(alias)[:120]
                        if len(alias)>1:db.execute('INSERT OR IGNORE INTO skill_aliases(alias,skill_id) VALUES(?,?)',(alias,row['id']))
                    count+=1
    return count

def skill_count(db_path=None):
    with connect(db_path) as db:return db.execute('SELECT COUNT(*) FROM skills').fetchone()[0]

def extract_skills(text, *, db_path=None):
    """Boundary-respecting phrase matches; returns a list of named skills. No inferred proficiency."""
    if not text or not text.strip():return []
    content=text.casefold()
    with connect(db_path) as db:
        entries=db.execute('SELECT id,name,normalized FROM skills').fetchall()
        aliases=db.execute('SELECT alias,skill_id FROM skill_aliases').fetchall()
    by_id={e['id']:e['name'] for e in entries}
    candidates=[(e['normalized'],e['id']) for e in entries]+[(a['alias'],a['skill_id']) for a in aliases]
    found=set()
    for term,identifier in candidates:
        if len(term)<2:continue
        pattern=r'(?<![\w])'+re.escape(term)+r'(?![\w])'
        if re.search(pattern,content):found.add(by_id[identifier])
    return sorted(found,key=str.casefold)
