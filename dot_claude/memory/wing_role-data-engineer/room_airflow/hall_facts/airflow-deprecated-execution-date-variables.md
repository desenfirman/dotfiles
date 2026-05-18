---
date: 2026-04-15
wing: role-data-engineer
room: airflow
hall: hall_facts
refs: []
---
KEYS: execution_date, next_execution_date, logical_date, data_interval_start, data_interval_end, Airflow, deprecated

Mapping (Airflow ≥ 2.2, removed in Airflow 3):
| Deprecated            | Replacement              | Use case                          |
|-----------------------|--------------------------|-----------------------------------|
| execution_date        | logical_date             | Scheduled date of the run         |
| next_execution_date   | data_interval_end        | End boundary of data window       |
| prev_execution_date   | data_interval_start      | Start boundary of data window     |

Rule: Never write `execution_date` or `next_execution_date` in any new DAG code (Jinja, Python, SQL).
Heuristic: "what date is this report for?" → data_interval_end; "when was this scheduled?" → logical_date.
Apply to: all new DAG authoring; code review rejects any PR containing deprecated variable names.

retrieval_value: Code-review gate: reject PRs with execution_date or next_execution_date in DAG files.
