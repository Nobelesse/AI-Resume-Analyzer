"""Reviewed job-title aliases for imported O*NET/ESCO occupation lookup.

Publisher-imported alternate labels still take precedence. Unlisted roles use
existing exact and substring lookup, never invented occupational links.
"""
from app.services.alias_matching import norm

TITLE_GROUPS = (
 ('Data Analyst', 'Data Analysts', 'Business Intelligence Analysts', 'BI Analyst', 'Data Analytics Specialist'),
 ('Software Developers', 'Software Developer', 'Software Engineer', 'SDE'),
 ('Web Developers', 'Web Developer', 'Frontend Developer', 'Front End Developer'),
 ('Software Quality Assurance Analysts and Testers', 'Software Tester', 'QA Tester', 'Software QA Engineer', 'Quality Assurance Tester'),
 ('Customer Service Representatives', 'Customer Care Executive', 'Customer Support Executive', 'Customer Care Representative', 'Call Center Agent'),
 ('Database Administrators', 'DBA', 'Database Administrator'),
 ('Information Security Analysts', 'Cybersecurity Analyst', 'Security Analyst'),
 ('Computer User Support Specialists', 'IT Help Desk Technician', 'IT Support Specialist', 'Technical Support Executive'),
 ('Bookkeeping, Accounting, and Auditing Clerks', 'Bookkeeper', 'Accounting Clerk'),
 ('Accountants and Auditors', 'Accountant', 'Audit Associate'),
 ('Graphic Designers', 'Graphic Designer'),
 ('Registered Nurses', 'Registered Nurse', 'RN'),
 ('Data Scientists', 'Data Scientist'),
 ('Human Resources Specialists', 'HR Specialist', 'Recruitment Specialist'),
 ('Financial Analysts', 'Financial Analyst'),
 ('Project Management Specialists', 'Project Manager'),
 ('Marketing Specialists', 'Digital Marketing Specialist', 'Marketing Executive'),
)

_TITLE_VARIANTS = {}
for group in TITLE_GROUPS:
    names = tuple(norm(item) for item in group)
    for variant in names:
        # Ambiguous short abbreviations should not substitute broad matching.
        _TITLE_VARIANTS[variant] = names


def occupation_title_variants(title):
    return _TITLE_VARIANTS.get(norm(title), ())
