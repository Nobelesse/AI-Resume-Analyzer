"""Safe, local-only official ESCO + O*NET supplemental importer."""
from __future__ import annotations
import argparse
import csv
import json
import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from app.config import DATABASE_PATH
from app.services.taxonomy import import_esco,import_onet_supplements,counts

REQUIRED = {
 'skills_en.csv': {'conceptUri','preferredLabel','altLabels'},
 'occupations_en.csv': {'conceptUri','preferredLabel'},
 'occupationSkillRelations_en.csv': {'occupationUri','skillUri','relationType'},
 'software_skills.csv': {'O*NET-SOC Code','Workplace Example'},
 'essential_skills.csv': {'O*NET-SOC Code','Element ID','Element Name'},
}

def csv_file(folder,filename):
    matches=list(Path(folder).rglob(filename))
    if len(matches)!=1: raise FileNotFoundError(f'Expected exactly one {filename} under {folder}; found {len(matches)}')
    path=matches[0]
    with path.open(encoding='utf-8-sig',newline='') as file:
        header=next(csv.reader(file))
    absent=REQUIRED[filename]-set(header)
    if absent:raise ValueError(f'{filename}: missing columns {sorted(absent)}')
    return path

def backup_database(db):
    if not db.exists():raise FileNotFoundError(f'Existing database not found: {db}; initialize app and import O*NET first')
    destination=db.with_name(db.stem+'-before-1599-'+datetime.now().strftime('%Y%m%d-%H%M%S-%f')+'.sqlite3')
    with sqlite3.connect(f'file:{db}?mode=ro',uri=True) as source, sqlite3.connect(destination) as target:
        source.backup(target)
    return destination

def main(argv=None):
    parser=argparse.ArgumentParser(description='Import verified local ESCO/O*NET CSVs (never downloads or sends resumes)')
    parser.add_argument('--esco-dir',type=Path,default=ROOT/'datasets'/'ESCO')
    parser.add_argument('--onet-dir',type=Path,default=ROOT/'datasets'/'ONET')
    parser.add_argument('--db',type=Path,default=DATABASE_PATH)
    parser.add_argument('--apply',action='store_true',help='Back up database and import; default is validation only')
    args=parser.parse_args(argv)
    esco=[csv_file(args.esco_dir,f) for f in ('occupations_en.csv','skills_en.csv','occupationSkillRelations_en.csv')]
    onet=[csv_file(args.onet_dir,f) for f in ('software_skills.csv','essential_skills.csv')]
    print('Validated official CSV layouts:')
    for path in esco+onet:print(' ',path.name, f'({path.stat().st_size:,} bytes)')
    if not args.apply:
        print('DRY RUN — nothing written. Add --apply to back up and import into',args.db)
        return 0
    backup=backup_database(args.db)
    print('SQLite backup:',backup)
    print('ESCO:',json.dumps(import_esco(*esco,db_path=args.db,version='ESCO English user downloaded')))
    print('O*NET supplements:',json.dumps(import_onet_supplements(*onet,db_path=args.db,version='O*NET user downloaded')))
    print('Final counts:',json.dumps(counts(args.db)))
    print('Complete. Keep the backup until you verify your application.')
    return 0

if __name__=='__main__':raise SystemExit(main())
