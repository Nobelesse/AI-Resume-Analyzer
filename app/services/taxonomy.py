"""Streaming, source-attributed ESCO and O*NET 31.0 catalog ingestion.

Import only data files obtained from the publishers. No synthetic catalog entries.
"""
from __future__ import annotations
import csv
import re
from pathlib import Path
from app.database.connection import connect


def norm(value):
    return ' '.join(str(value or '').casefold().strip().split())


def ensure_tables(db):
    db.executescript('''
    CREATE TABLE IF NOT EXISTS tax_occupations (
      id INTEGER PRIMARY KEY, source TEXT NOT NULL, source_id TEXT NOT NULL,
      name TEXT NOT NULL, normalized TEXT NOT NULL,
      UNIQUE(source, source_id));
    CREATE INDEX IF NOT EXISTS idx_tax_occ_name ON tax_occupations(normalized);
    CREATE TABLE IF NOT EXISTS tax_occupation_aliases (
      source TEXT NOT NULL, alias TEXT NOT NULL, occupation_id INTEGER NOT NULL
      REFERENCES tax_occupations(id) ON DELETE CASCADE,
      PRIMARY KEY(source, alias, occupation_id));
    CREATE INDEX IF NOT EXISTS idx_tax_occ_alias ON tax_occupation_aliases(alias);
    CREATE TABLE IF NOT EXISTS tax_skills (
      id INTEGER PRIMARY KEY, source TEXT NOT NULL, source_id TEXT NOT NULL,
      name TEXT NOT NULL, normalized TEXT NOT NULL,
      UNIQUE(source, source_id));
    CREATE INDEX IF NOT EXISTS idx_tax_skill_name ON tax_skills(normalized);
    CREATE TABLE IF NOT EXISTS tax_skill_aliases (
      source TEXT NOT NULL, alias TEXT NOT NULL, skill_id INTEGER NOT NULL
      REFERENCES tax_skills(id) ON DELETE CASCADE,
      PRIMARY KEY(source, alias, skill_id));
    CREATE INDEX IF NOT EXISTS idx_tax_skill_alias ON tax_skill_aliases(alias);
    CREATE TABLE IF NOT EXISTS tax_links (
      occupation_id INTEGER NOT NULL REFERENCES tax_occupations(id) ON DELETE CASCADE,
      skill_id INTEGER NOT NULL REFERENCES tax_skills(id) ON DELETE CASCADE,
      relation TEXT NOT NULL, PRIMARY KEY(occupation_id,skill_id,relation));
    CREATE INDEX IF NOT EXISTS idx_tax_links_occ ON tax_links(occupation_id);
    -- Career Finder retrieves linked occupations by detected skill_id.
    CREATE INDEX IF NOT EXISTS idx_tax_links_skill_occ ON tax_links(skill_id, occupation_id);
    CREATE TABLE IF NOT EXISTS tax_imports (
      source TEXT PRIMARY KEY, version TEXT NOT NULL, imported_at TEXT DEFAULT CURRENT_TIMESTAMP);
    ''')


def _csv(path):
    with Path(path).open('r', encoding='utf-8-sig', newline='') as f:
        sample=f.read(2048); f.seek(0)
        dialect=csv.excel_tab if sample.count('\t')>sample.count(',') else csv.excel
        reader=csv.DictReader(f,dialect=dialect)
        if not reader.fieldnames: raise ValueError(f'CSV has no header: {path}')
        for row in reader: yield row


def _get(row,*names):
    mapped={norm(k).replace(' ','').replace('_',''):v for k,v in row.items() if k}
    for name in names:
        value=mapped.get(norm(name).replace(' ','').replace('_',''))
        if value is not None and str(value).strip(): return str(value).strip()
    return ''


def _labels(text):
    # ESCO uses newline-separated or pipe-separated alternate labels.
    return [x.strip() for x in re.split(r'[\n|]',text or '') if 2<=len(x.strip())<=140]


def import_esco(occupations,skills,relations,*, db_path=None, version='user-supplied-ESCO'):
    """Import official English ESCO occupations/skills/occupationSkillRelations CSV files.

    Atomic: invalid input rolls back and does not corrupt the existing catalog.
    """
    counts={'occupations':0,'skills':0,'links':0}
    with connect(db_path) as db:
        ensure_tables(db)
        for row in _csv(occupations):
            uri=_get(row,'conceptUri','uri'); name=_get(row,'preferredLabel','label')
            if not uri or not name: raise ValueError('Invalid ESCO occupation columns: conceptUri / preferredLabel required')
            db.execute('INSERT INTO tax_occupations(source,source_id,name,normalized) VALUES(?,?,?,?) ON CONFLICT(source,source_id) DO UPDATE SET name=excluded.name,normalized=excluded.normalized',('ESCO',uri,name,norm(name)))
            oid=db.execute('SELECT id FROM tax_occupations WHERE source=? AND source_id=?',('ESCO',uri)).fetchone()[0]
            for a in _labels(_get(row,'altLabels','alternativeLabels')+'\n'+_get(row,'hiddenLabels')):
                db.execute('INSERT OR IGNORE INTO tax_occupation_aliases VALUES(?,?,?)',('ESCO',norm(a),oid))
            counts['occupations']+=1
        for row in _csv(skills):
            uri=_get(row,'conceptUri','uri'); name=_get(row,'preferredLabel','label')
            if not uri or not name: raise ValueError('Invalid ESCO skill columns: conceptUri / preferredLabel required')
            db.execute('INSERT INTO tax_skills(source,source_id,name,normalized) VALUES(?,?,?,?) ON CONFLICT(source,source_id) DO UPDATE SET name=excluded.name,normalized=excluded.normalized',('ESCO',uri,name,norm(name)))
            sid=db.execute('SELECT id FROM tax_skills WHERE source=? AND source_id=?',('ESCO',uri)).fetchone()[0]
            for a in _labels(_get(row,'altLabels','alternativeLabels')+'\n'+_get(row,'hiddenLabels')):
                db.execute('INSERT OR IGNORE INTO tax_skill_aliases VALUES(?,?,?)',('ESCO',norm(a),sid))
            counts['skills']+=1
        for row in _csv(relations):
            o=_get(row,'occupationUri','occupation'); s=_get(row,'skillUri','skill')
            relation=_get(row,'relationType','type') or 'related'
            oi=db.execute('SELECT id FROM tax_occupations WHERE source=? AND source_id=?',('ESCO',o)).fetchone()
            si=db.execute('SELECT id FROM tax_skills WHERE source=? AND source_id=?',('ESCO',s)).fetchone()
            if oi and si:
                db.execute('INSERT OR IGNORE INTO tax_links VALUES(?,?,?)',(oi[0],si[0],relation[:60]))
                counts['links']+=1
        db.execute('INSERT INTO tax_imports(source,version) VALUES(?,?) ON CONFLICT(source) DO UPDATE SET version=excluded.version,imported_at=CURRENT_TIMESTAMP',('ESCO',version))
    return counts


def import_onet(occupations, software_skills, *, db_path=None, version='31.0'):
    """Import O*NET CSV Occupation Data and Software Skills (source IDs are SOC codes).

    Software Skills contains workplace technology examples, not all occupational skills.
    """
    counts={'occupations':0,'skills':0,'links':0}
    with connect(db_path) as db:
        ensure_tables(db)
        for row in _csv(occupations):
            code=_get(row,'O*NET-SOC Code','O*NET SOC Code'); name=_get(row,'Title')
            if not code or not name: raise ValueError('O*NET occupation CSV requires O*NET-SOC Code and Title')
            db.execute('INSERT INTO tax_occupations(source,source_id,name,normalized) VALUES(?,?,?,?) ON CONFLICT(source,source_id) DO UPDATE SET name=excluded.name,normalized=excluded.normalized',('ONET',code,name,norm(name)))
            counts['occupations']+=1
        for row in _csv(software_skills):
            code=_get(row,'O*NET-SOC Code','O*NET SOC Code'); name=_get(row,'Workplace Example')
            if not code or not name: raise ValueError('O*NET software CSV requires O*NET-SOC Code and Workplace Example')
            si='software:'+norm(name)
            db.execute('INSERT OR IGNORE INTO tax_skills(source,source_id,name,normalized) VALUES(?,?,?,?)',('ONET',si,name,norm(name)))
            oi=db.execute('SELECT id FROM tax_occupations WHERE source=? AND source_id=?',('ONET',code)).fetchone()
            sk=db.execute('SELECT id FROM tax_skills WHERE source=? AND source_id=?',('ONET',si)).fetchone()
            if oi and sk:
                db.execute('INSERT OR IGNORE INTO tax_links VALUES(?,?,?)',(oi[0],sk[0],'software-example'))
                counts['links']+=1
            counts['skills']+=1
        db.execute('INSERT INTO tax_imports(source,version) VALUES(?,?) ON CONFLICT(source) DO UPDATE SET version=excluded.version,imported_at=CURRENT_TIMESTAMP',('ONET',version))
    return counts


def counts(db_path=None):
    with connect(db_path) as db:
        ensure_tables(db)
        return {name:db.execute('SELECT COUNT(*) FROM '+table).fetchone()[0]
                for name,table in [('occupations','tax_occupations'),('skills','tax_skills'),('links','tax_links')]}


def lookup_occupation(title, *, db_path=None, limit=5):
    target=norm(title)
    if len(target)<3:return []
    with connect(db_path) as db:
        ensure_tables(db)
        rows=db.execute('''SELECT o.id,o.name,o.source,COUNT(l.skill_id) as n FROM tax_occupations o
          LEFT JOIN tax_links l ON l.occupation_id=o.id
          WHERE o.normalized=? OR o.id IN (SELECT occupation_id FROM tax_occupation_aliases WHERE alias=?)
          GROUP BY o.id ORDER BY n DESC LIMIT ?''',(target,target,limit)).fetchall()
        if not rows:
            rows=db.execute('''SELECT o.id,o.name,o.source,COUNT(l.skill_id) as n FROM tax_occupations o
              LEFT JOIN tax_links l ON l.occupation_id=o.id
              WHERE o.normalized LIKE ? GROUP BY o.id ORDER BY n DESC LIMIT ?''',('%'+target+'%',limit)).fetchall()
        return [{'id':r['id'],'name':r['name'],'source':r['source'],'links':r['n']} for r in rows]


def role_skills(title, *, db_path=None, limit=35):
    matches=lookup_occupation(title,db_path=db_path,limit=1)
    if not matches:return None
    with connect(db_path) as db:
        rows=db.execute('''SELECT s.name,l.relation FROM tax_links l JOIN tax_skills s ON s.id=l.skill_id
           WHERE l.occupation_id=? ORDER BY CASE WHEN lower(l.relation) LIKE '%essential%' THEN 0 ELSE 1 END,s.name LIMIT ?''',(matches[0]['id'],limit)).fetchall()
    return {'role':matches[0]['name'],'skills':[r['name'] for r in rows], 'source':matches[0]['source']+'-imported', 'confidence':'catalog', 'links':len(rows)}


def detect_catalog_skills(text, *,db_path=None, max_chars=30000):
    """Chunked phrase search. Doesn't mistake an unobserved skill for absent proficiency."""
    if not text:return []
    content=str(text)[:max_chars].casefold()
    with connect(db_path) as db:
        rows=db.execute('SELECT normalized as term,name,id FROM tax_skills').fetchall()
        aliases=db.execute('''SELECT a.alias as term,s.name,s.id FROM tax_skill_aliases a
                             JOIN tax_skills s ON s.id=a.skill_id''').fetchall()
    detected={}
    for row in list(rows)+list(aliases):
        term=row['term']
        if len(term)<3 or len(term)>100:continue
        if re.search(r'(?<!\w)'+re.escape(term)+r'(?!\w)',content): detected[row['id']]=row['name']
    return sorted(detected.values(),key=str.casefold)


# O*NET supplemental files are official publisher data, not generated skills.
def import_onet_expanded(folder, *, db_path=None, version='O*NET 31.0'):
    """Merge job titles, knowledge and essential skills into existing O*NET catalog.

    Run import_onet first. Accepts filename/header variants across O*NET releases.
    Unknown occupation codes/element IDs are skipped instead of inventing entries.
    """
    directory=Path(folder)
    paths={f.stem.casefold():f for f in directory.glob('*.csv')}
    if 'occupation_data' not in paths:
        raise FileNotFoundError(f'Missing occupation_data.csv in {directory}')
    summary={'occupations':0,'title_aliases':0,'skills':0,'links':0,'skipped':0,'files':[]}
    # Build reference lookup from the publisher's own descriptions.
    definitions={}
    ref=paths.get('content_model_reference')
    if ref:
        for r in _csv(ref):
            key=_get(r,'Element ID','ElementID')
            label=_get(r,'Element Name','ElementName','Name')
            if key and label: definitions[key]=label
    with connect(db_path) as db:
        ensure_tables(db)
        # Import occupation catalogue in case Version 1.4 software import was skipped.
        for r in _csv(paths['occupation_data']):
            code=_get(r,'O*NET-SOC Code'); title=_get(r,'Title')
            if not code or not title: raise ValueError('Invalid O*NET occupation_data.csv')
            db.execute('INSERT INTO tax_occupations(source,source_id,name,normalized) VALUES(?,?,?,?) ON CONFLICT(source,source_id) DO UPDATE SET name=excluded.name,normalized=excluded.normalized',('ONET',code,title,norm(title)))
            summary['occupations']+=1
        summary['files'].append('occupation_data.csv')
        aliases=paths.get('job_titles') or paths.get('alternate_titles') or paths.get('sample_of_reported_titles')
        if aliases:
            for r in _csv(aliases):
                code=_get(r,'O*NET-SOC Code'); title=_get(r,'Title','Job Title','Alternate Title','Reported Job Title')
                oid=db.execute('SELECT id FROM tax_occupations WHERE source=? AND source_id=?',('ONET',code)).fetchone()
                if oid and title and len(title)<=140:
                    db.execute('INSERT OR IGNORE INTO tax_occupation_aliases(source,alias,occupation_id) VALUES(?,?,?)',('ONET',norm(title),oid[0]))
                    summary['title_aliases']+=1
            summary['files'].append(aliases.name)
        for key,relation in [('essential_skills','essential-skill'),('knowledge','knowledge')]:
            file=paths.get(key)
            if not file:continue
            for r in _csv(file):
                code=_get(r,'O*NET-SOC Code')
                element=_get(r,'Element ID')
                label=_get(r,'Element Name','Skill','Skill Name','Knowledge') or definitions.get(element,'')
                if not label or not code or not element:
                    summary['skipped']+=1;continue
                occ=db.execute('SELECT id FROM tax_occupations WHERE source=? AND source_id=?',('ONET',code)).fetchone()
                if not occ:
                    summary['skipped']+=1;continue
                sid='onet-element:'+element
                db.execute('INSERT INTO tax_skills(source,source_id,name,normalized) VALUES(?,?,?,?) ON CONFLICT(source,source_id) DO UPDATE SET name=excluded.name,normalized=excluded.normalized',('ONET',sid,label,norm(label)))
                skill=db.execute('SELECT id FROM tax_skills WHERE source=? AND source_id=?',('ONET',sid)).fetchone()
                db.execute('INSERT OR IGNORE INTO tax_links(occupation_id,skill_id,relation) VALUES(?,?,?)',(occ[0],skill[0],relation))
                summary['skills']+=1;summary['links']+=1
            summary['files'].append(file.name)
        db.execute('INSERT INTO tax_imports(source,version) VALUES(?,?) ON CONFLICT(source) DO UPDATE SET version=excluded.version,imported_at=CURRENT_TIMESTAMP',('ONET',version))
    return summary


def catalog_details(*, db_path=None):
    with connect(db_path) as db:
        ensure_tables(db)
        sources=db.execute("SELECT source, COUNT(*) AS occupations FROM tax_occupations GROUP BY source ORDER BY source").fetchall()
        skills=db.execute("SELECT source, COUNT(*) AS skills FROM tax_skills GROUP BY source ORDER BY source").fetchall()
        relations=db.execute("SELECT o.source, l.relation, COUNT(*) AS count FROM tax_links l JOIN tax_occupations o ON o.id=l.occupation_id GROUP BY o.source,l.relation ORDER BY o.source,l.relation").fetchall()
        aliases=db.execute('SELECT source, COUNT(*) AS count FROM tax_occupation_aliases GROUP BY source ORDER BY source').fetchall()
        imports=db.execute('SELECT source,version,imported_at FROM tax_imports ORDER BY source').fetchall()
        return dict(counts=counts(db_path),sources=[dict(r) for r in sources],skills=[dict(r) for r in skills],relations=[dict(r) for r in relations],aliases=[dict(r) for r in aliases],imports=[dict(r) for r in imports])


def import_onet_supplements(software_csv, essential_csv, *, db_path=None, version='O*NET supplemental CSV'):
    """Attach official O*NET examples/skills to already imported SOC occupations, repeatably."""
    result={'software_rows':0,'essential_rows':0,'linked':0,'unknown_occupation':0,'skipped':0}
    with connect(db_path) as db:
        ensure_tables(db)
        if not db.execute("SELECT COUNT(*) FROM tax_occupations WHERE source='ONET'").fetchone()[0]:
            raise ValueError('Import O*NET occupations before supplements')
        for filepath,kind,relation in [(software_csv,'software','software-example'),(essential_csv,'essential','essential-skill')]:
            for row in _csv(filepath):
                code=_get(row,'O*NET-SOC Code'); element=_get(row,'Element ID')
                label=_get(row,'Workplace Example') if kind=='software' else _get(row,'Element Name')
                skill_key=('software:'+norm(label)) if kind=='software' else ('onet-element:'+element)
                if not code or not label or not skill_key or (kind=='essential' and not element):
                    result['skipped']+=1;continue
                occ=db.execute("SELECT id FROM tax_occupations WHERE source='ONET' AND source_id=?",(code,)).fetchone()
                if not occ:
                    result['unknown_occupation']+=1;continue
                db.execute("INSERT INTO tax_skills(source,source_id,name,normalized) VALUES('ONET',?,?,?) ON CONFLICT(source,source_id) DO UPDATE SET name=excluded.name,normalized=excluded.normalized",(skill_key,label,norm(label)))
                skill=db.execute("SELECT id FROM tax_skills WHERE source='ONET' AND source_id=?",(skill_key,)).fetchone()[0]
                cur=db.execute('INSERT OR IGNORE INTO tax_links(occupation_id,skill_id,relation) VALUES(?,?,?)',(occ[0],skill,relation))
                result['linked']+=int(cur.rowcount>0)
                result[kind+'_rows']+=1
        db.execute("INSERT INTO tax_imports(source,version) VALUES('ONET-SUPPLEMENTS',?) ON CONFLICT(source) DO UPDATE SET version=excluded.version,imported_at=CURRENT_TIMESTAMP",(version,))
    return result
