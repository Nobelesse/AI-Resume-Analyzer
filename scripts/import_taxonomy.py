"""Import externally downloaded official taxonomies; no user uploads or secrets involved."""
import argparse,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app.database.connection import initialize_database
from app.services.taxonomy import import_esco,import_onet,import_onet_expanded,counts

def main():
    parser=argparse.ArgumentParser(description='Import official source-attributed occupation and skill CSVs into local SQLite')
    parser.add_argument('--esco',nargs=3,metavar=('OCCUPATIONS','SKILLS','RELATIONS'))
    parser.add_argument('--onet',nargs=2,metavar=('OCCUPATIONS','SOFTWARE_SKILLS'))
    parser.add_argument('--onet-expanded',type=Path,metavar='CSV_DIRECTORY',help='Import supplemental O*NET titles, knowledge and essential skills')
    parser.add_argument('--db',type=Path,default=None)
    parser.add_argument('--version',default='source CSV')
    args=parser.parse_args()
    if not args.esco and not args.onet and not args.onet_expanded:parser.error('Specify --esco or --onet')
    initialize_database(args.db)
    if args.esco:print('ESCO imported:',import_esco(*args.esco,db_path=args.db,version=args.version))
    if args.onet:print('O*NET imported:',import_onet(*args.onet,db_path=args.db,version=args.version))
    if args.onet_expanded:print('O*NET expanded:',import_onet_expanded(args.onet_expanded,db_path=args.db,version=args.version))
    print('Actual catalog counts:',counts(args.db))
if __name__=='__main__':main()
