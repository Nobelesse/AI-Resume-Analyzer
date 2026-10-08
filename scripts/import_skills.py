"""Offline trusted CSV skill import; usage: python scripts/import_skills.py path/to/skills.csv"""
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from app.database.connection import initialize_database
from app.services.skills import import_skills_csv,skill_count
if __name__=='__main__':
    if len(sys.argv)!=2:raise SystemExit('Usage: python scripts/import_skills.py path/to/skills.csv')
    initialize_database()
    imported=import_skills_csv(sys.argv[1],source='reviewed-csv')
    print(f'Processed {imported} entries; catalog now has {skill_count()} unique skills')
