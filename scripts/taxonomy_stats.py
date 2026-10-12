"""Print real imported occupation/skill/link counts without changing records."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app.database.connection import initialize_database
from app.services.taxonomy import counts,catalog_details
from app.services.skills import skill_count

if __name__ == '__main__':
    initialize_database()
    print('Curated vocabulary:',skill_count())
    print('Official imported catalog:',counts())

    print('Details:',catalog_details())
