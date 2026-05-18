---
date: 2026-04-13
wing: role-data-engineer
room: bigquery
hall: hall_facts
refs: []
---
KEYS: columns_definition, backtick, reserved-word, BigQuery, YAML-DAG, config.yml, syntax-error

Rule: Always backtick EVERY identifier in `columns_definition` — both inside `CAST(...)` and after `AS`:
```yaml
columns_definition: >
  CAST(`date` AS DATE) AS `date`,
  CAST(`no` AS INT64) AS `no`,
  CAST(`status` AS STRING) AS `status`
```
Bare identifiers silently pass Airflow parse but fail at BQ query runtime if the name is a reserved word
(NO, IN, OUT, DAY, DATE, STATUS, TYPE, DESC, etc.).
Apply to: every `columns_definition` block in every `config.yml` (Pattern 4 YAML-driven DAGs).

retrieval_value: Code-review gate: reject any columns_definition with unquoted identifiers.
