# Project-wide skill extraction fast path — 1.5.9.9.10

Both curated and imported O*NET/ESCO skill matchers now first reject candidate phrases absent from the casefolded resume text using a substring check. Only candidate phrases that are present are then checked using the existing boundary-safe regular expression. This preserves the existing matching logic, scores, data and permissions while avoiding thousands of unnecessary regular-expression compilations and searches across ATS, Job Match and Career Finder.

The existing Career Finder tax_links(skill_id, occupation_id) index from v1.5.9.9.9.9 is retained. This update does not remove Ollama inference latency or promise a fixed full-page response time. Never include local SQLite DB or uploads in a release.
