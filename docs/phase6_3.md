# Phase 6.3: Universal Job Intelligence and Career Finder

## Setup
Install Ollama for Windows and confirm `ollama list` includes `llama3.2:3b` and `llama3.2:1b`. Run `ollama serve` only if the Ollama service is not already active. Check `http://127.0.0.1:11434/api/tags`. Then install `requirements-dev.txt` and run `python -m streamlit run app/main.py`.

## Behavior
Job Match Studio automatically calls a local-only Ollama model, falls back to 1B if 3B fails, and finally falls back to the offline role library. Career Finder uses the selected resume; on model failure it ranks offline role profiles. An unfamiliar title can produce a useful AI profile but the app never represents model suggestions as verified employer qualifications.

## Performance
Default total timeout is up to 180 seconds per model, configurable with `ARA_OLLAMA_TIMEOUT` (10–300). One request at a time in the UI. Close memory-heavy applications on 8GB machines. Initial response may be slow.

## Safety
No remote AI service or external employer data is used. Do not assume a licensed profession is accessible based on skill similarity alone. Career recommendations are not hiring or eligibility decisions.
