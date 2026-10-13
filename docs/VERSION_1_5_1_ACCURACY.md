# Version 1.5.1: Offline matching accuracy and transparency

Career Finder now uses a selective SQLite indexed join for detected skills instead of loading the full catalog into Python. Its score explicitly combines 60% observed occupation skill coverage with 40% breadth of supporting skills (capped at five), reducing one-skill occupation dominance. Rankings remain heuristics, not probabilities or eligibility determinations.

Job Studio now exposes the scoring methodology and whether the scoring basis is a pasted employer description or suggested occupation skills. ATS readiness remains a separate heuristic in `app/services/ats.py`. No paid AI API is required; Gemini remains opt-in.

This release adds controlled fixtures testing role ranking, non-inference of missing skills, and required-skill evidence. No claim of externally benchmarked predictive accuracy is made.

## Windows upgrade

Extract the release ZIP to a new folder. Back up your existing project. Copy updated source over the existing project excluding `.git`, `.venv`, `.env`, `data/`, `*.db`, `*.sqlite*`, and uploaded resumes. Run `.\.venv\Scripts\python.exe -m pytest -q` and `.\.venv\Scripts\python.exe -m streamlit run app/main.py`.
