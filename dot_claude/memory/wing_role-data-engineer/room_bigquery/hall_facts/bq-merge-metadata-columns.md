---
date: 2026-05-04
wing: role-data-engineer
room: bigquery
hall: hall_facts
refs: []
---
KEYS: MERGE, id, load_timestamp, MD5, surrogate-key, BigQuery, metadata-columns, TO_HEX

Rule: Every BQ target table must have `id STRING NOT NULL` and `load_timestamp TIMESTAMP NOT NULL`.
- `id` = `TO_HEX(MD5(CONCAT(natural_key_col1, natural_key_col2, ...)))` — computed in MERGE USING subquery.
- `load_timestamp` = `CURRENT_TIMESTAMP()` on both INSERT and UPDATE WHEN clauses.
- Neither column exists in staging; both are derived server-side in BigQuery.
- `id` is NEVER updated on MATCHED rows (derived from immutable natural key).
Apply to: every new pipeline writing to a BQ target table; brownfield refactors add via schema migration.

retrieval_value: Code-review gate: reject target table DDL without id and load_timestamp.
