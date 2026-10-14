# Version 1.5.6 — Occupation-Aware Learning Topics

This university-project release works offline, without API fees. Candidate career scores remain heuristic and unchanged from v1.5.5. This release improves *optional learning topics* only.

- Sort suggestions by a small, documented field-specific priority list instead of by name length or alphabetical order.
- Only suggest topics already listed for the occupation in the imported catalog; never invent occupational requirements.
- Handle selected aliases such as Microsoft Power BI / Power BI.
- Stop presenting arbitrary unrelated technologies as priorities for software, data, and marketing careers.
- Distinguish a skill not mentioned on a resume from a verified skill deficit.

**Limitations:** This is not a validated essential/preferred requirements model. O*NET skill importance scores and Job Zones have not yet been incorporated. The local database and uploads are not bundled into the release.
