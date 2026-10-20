# Career Finder database performance optimization (v1.5.9.9.9.9)

## Observed issue
The `rank_careers` skill-to-occupation lookup joins `tax_links` on `skill_id`, but the previous schema indexed only `occupation_id`. On a large local O*NET + ESCO database the missing reverse-lookup index can add significant query work.

## Change
Create `idx_tax_links_skill_occ` on `tax_links(skill_id, occupation_id)` in `ensure_tables()`. Applied to both new and existing catalogs on their next initialization. No dataset reimport or changes to ranking/evidence logic.

## Test
`tests/test_career_query_index1599999.py` verifies index existence and SQLite's query plan. Run all regression tests and final audit.

## Remaining considerations
Elapsed time will vary with SSD/HDD, resume size, existing schema and operating system. Further optimization needs before/after profiling against the user's actual large database, which is not included in the release.
