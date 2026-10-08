"""Interactive one-time admin bootstrap; no passwords in arguments or source files."""
import getpass
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))
from app.database.connection import initialize_database
from app.auth.service import create_initial_admin

def main():
    initialize_database()
    print("AI Resume Analyzer — first administrator setup")
    print("This command works only if no administrator currently exists.")
    email=input("Admin email: ").strip()
    name=input("Admin display name: ").strip()
    password=getpass.getpass("Admin password (12+ characters): ")
    confirmation=getpass.getpass("Repeat password: ")
    if password!=confirmation:
        print("Passwords do not match.")
        return 1
    try:
        create_initial_admin(email,name,password)
    except ValueError as exc:
        print(f"Setup refused: {exc}")
        return 1
    print("Administrator created. Use the Admin Login page.")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
