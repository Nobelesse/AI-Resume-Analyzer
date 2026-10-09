# Phase 6.2 — Customer Care Executive and local Ollama

The offline role library now supports **Customer Care Executive**, **Customer Service Executive**, customer support and call-centre variants. This is a starter catalog and cannot know every occupation.

## Install Ollama on Windows

1. Download the official Windows installer: https://ollama.com/download/windows
2. Restart VS Code / PowerShell so the `ollama` command is found.
3. Run `ollama --version`, then `ollama pull llama3.2`.
4. Run `ollama list` to verify the model is installed.
5. Ollama usually runs its local service automatically. If not, run `ollama serve` in a separate PowerShell terminal.
6. Test it using `ollama run llama3.2 "List useful skills for a customer care executive"`.
7. In Streamlit, sign in as a user, select a resume, open Job Match Studio, type a job title, tick **Use local Ollama AI**, keep model `llama3.2`, and click **Compare and save**.

Ollama uses the local HTTP API at http://127.0.0.1:11434/api/generate. Only localhost is allowed in the app; resume text is not sent to Ollama by the job-title suggestion helper, only the job title. Avoid sensitive titles.

## Notes

The app does not require the Python `ollama` library: it uses Python's built-in `urllib.request`. When the model is not installed or the server is stopped, the app reports an error. A local model may be incorrect or invent skills: all role-inferred skills are marked as unverified suggestions. Ollama inference may take longer than the current 12-second request timeout on slow computers.

The editable files for this patch are: `app/services/role_skills.py`, `app/services/skills.py`, `app/database/job_matches.py`, `app/pages/job_pages.py`, `app/config.py`, `tests/test_phase6_customer_care.py`, and this documentation.
