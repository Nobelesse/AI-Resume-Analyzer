"""Reviewed, offline-safe equivalent names for matching *observed* skills.

Not an exhaustive dictionary or evidence of proficiency. A match requires a
skill actually extracted from the document; unrelated technologies are never
merged. The same normalization is used by the two recommendation services.
"""
import re

# Each group contains interchangeable names for the same technology/skill.
# Do not add related-but-distinct skills (e.g. Python vs Pandas, Excel vs Sheets).
EQUIVALENT_NAMES = (
    ('Microsoft Excel', 'Excel', 'MS Excel', 'MS-Excel', 'Microsoft Office Excel', 'Excel spreadsheet software'),
    ('Microsoft Word', 'Word', 'MS Word', 'MS-Word', 'Microsoft Office Word'),
    ('Microsoft PowerPoint', 'PowerPoint', 'MS PowerPoint', 'MS PPT', 'Microsoft Office PowerPoint'),
    ('Microsoft Outlook', 'MS Outlook', 'Outlook email'),
    ('Microsoft Access', 'MS Access', 'Access database'),
    ('Power BI', 'Microsoft Power BI', 'PowerBI', 'Power-BI', 'Power BI Desktop'),
    ('PostgreSQL', 'Postgres', 'Postgres SQL', 'PostgreSQL database'),
    ('Microsoft SQL Server', 'MS SQL Server', 'SQL Server', 'MSSQL'),
    ('MySQL', 'My SQL', 'MySQL database'),
    ('MongoDB', 'Mongo DB', 'MongoDB database'),
    ('JavaScript', 'JS', 'JavaScript language'),
    ('TypeScript', 'TS', 'TypeScript language'),
    ('React', 'ReactJS', 'React.js', 'React JS'),
    ('Vue.js', 'VueJS', 'Vue JS', 'Vue'),
    ('Node.js', 'NodeJS', 'Node JS'),
    ('Express.js', 'ExpressJS', 'Express JS'),
    ('Next.js', 'NextJS', 'Next JS'),
    ('HTML', 'Hypertext Markup Language', 'Hypertext markup language HTML', 'HTML5'),
    ('CSS', 'Cascading Style Sheets', 'Cascading style sheets CSS', 'CSS3'),
    ('Python', 'Python3', 'Python 3', 'Python (computer programming)'),
    ('Go', 'Golang', 'Go language'),
    ('Scikit-learn', 'sklearn', 'scikit learn'),
    ('PyTorch', 'Torch', 'Py Torch'),
    ('TensorFlow', 'Tensor Flow'),
    ('NumPy', 'numpy library'),
    ('Pandas', 'pandas library', 'python pandas'),
    ('Kubernetes', 'K8s'),
    ('Google Cloud Platform', 'GCP', 'Google Cloud'),
    ('Amazon Web Services', 'AWS'),
    ('Natural Language Processing', 'NLP'),
    ('Machine Learning', 'ML'),
    ('Generative AI', 'Gen AI', 'GenAI'),
    ('Large Language Models', 'LLM', 'LLMs', 'large language model'),
    ('Retrieval Augmented Generation', 'RAG', 'Retrieval-Augmented Generation'),
    ('Extract Transform Load', 'ETL', 'ETL pipelines'),
    ('Continuous Integration and Continuous Delivery', 'CI/CD', 'CI CD', 'CICD'),
    ('REST API', 'RESTful API', 'RESTful APIs', 'REST API development'),
    ('GitHub Actions', 'GitHub Action'),
    ('Search Engine Optimization', 'SEO'),
    ('Google Analytics', 'Google Analytics 4', 'GA4'),
    ('TallyPrime', 'Tally Prime'),
    ('QuickBooks', 'Quick Books'),
    ('Power Query', 'Power Query Editor'),
    ('Pivot Tables', 'Pivot Table'),
    ('Data Cleaning', 'Data Cleansing'),
    ('Data Analysis', 'Data Analyses'),
    ('Data Visualization', 'Data Visualisation'),
    ('Pivot Tables', 'Pivot Table', 'Pivot-table', 'Pivot-tables'),
    ('KPI Reporting', 'KPI Monitoring', 'KPI Tracking'),
    ('Exploratory Data Analysis', 'EDA'),
    ('A/B Testing', 'AB Testing', 'A B Testing'),
    ('Unit Testing', 'Unit Tests'),
    ('Quality Assurance', 'QA', 'Software Quality Assurance'),
    ('User Experience Design', 'UX Design'),
    ('User Interface Design', 'UI Design'),
    ('Customer Service', 'Customer Care'),
    ('Customer Relationship Management', 'CRM'),
    ('Object-Oriented Programming', 'OOP'),
    ('Version Control', 'Source Control'),
    ('Postman', 'Postman API Client'),
    ('Jupyter Notebook', 'Jupyter Notebooks'),
    ('Apache Spark', 'Spark framework'),
    ('Looker Studio', 'Google Looker Studio', 'Google Data Studio'),
    ('VS Code', 'Visual Studio Code', 'VScode'),
    ('Docker', 'Docker Engine'),
    ('Git', 'Git version control'),
    ('Selenium', 'Selenium WebDriver'),
    ('Playwright', 'Microsoft Playwright'),
    ('Django', 'Django framework'),
    ('FastAPI', 'Fast API'),
    ('Flask', 'Flask framework'),
    ('SQLite', 'SQLite3', 'SQLite database'),
    ('Tableau', 'Tableau Desktop'),
)


def norm(value):
    value = str(value or '').casefold().strip()
    # Normalize punctuation *only* where spelling variants require it; avoid
    # collapsing C, C++, C# or Java and JavaScript into one representation.
    value = re.sub(r'\s+', ' ', value)
    return value


KEY_TO_CANONICAL = {}
CANONICAL_TO_VARIANTS = {}
for group in EQUIVALENT_NAMES:
    key = norm(group[0])
    variants = frozenset(norm(label) for label in group)
    CANONICAL_TO_VARIANTS[key] = variants
    for alias in variants:
        if alias in KEY_TO_CANONICAL and KEY_TO_CANONICAL[alias] != key:
            raise ValueError('Conflicting reviewed alias: ' + alias)
        KEY_TO_CANONICAL[alias] = key


def canonical_key(label):
    """Compare alternate *labels* of one skill, never related technologies."""
    key = norm(label)
    return KEY_TO_CANONICAL.get(key, key)


def equivalent(a, b):
    return canonical_key(a) == canonical_key(b)


def catalogue_query_keys(extracted):
    """Look up all reviewed names for only the skills observed in a resume."""
    names = {norm(name) for name in extracted if norm(name)}
    keys = set(names)
    for name in names:
        key = canonical_key(name)
        keys.add(key)
        keys.update(CANONICAL_TO_VARIANTS.get(key, ()))
    return keys


def matched_labels(required, candidate):
    """Return requirement labels with explicit equivalent resume evidence."""
    observed = {canonical_key(name) for name in candidate}
    return sorted((name for name in required if canonical_key(name) in observed), key=str.casefold)


def absent_labels(required, candidate):
    observed = {canonical_key(name) for name in candidate}
    return sorted((name for name in required if canonical_key(name) not in observed), key=str.casefold)
