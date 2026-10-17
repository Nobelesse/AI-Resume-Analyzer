# Version 1.5.8 — Advanced ATS Intelligence

## Delivered
- Separate resume readiness (existing interpretable quality heuristic) and job-specific compatibility (new deterministic requirements analysis).
- Required and preferred requirement-line detection with manual-review status for degrees, years of experience and certifications.
- No job compatibility number when the job description has no recognized evaluable skills.
- Explicit, conservative claims: missing resume evidence is not missing real-world competence; no employer ATS simulation.
- New user page replaces the existing ATS Analysis navigation entry and retains saved-analysis functionality in code and Analysis History.
- Existing Dark Abyss UI, offline operation, authentication and database preserved.

## Limitations
The readiness metric is still the existing heuristic and has not been benchmark-calibrated. Job compatibility is a simplified ratio of recognizable requirement lines, not a hiring probability. Formatting checks cannot inspect PDF spatial structure from extracted text alone. Do not present this software as a certified ATS system.
