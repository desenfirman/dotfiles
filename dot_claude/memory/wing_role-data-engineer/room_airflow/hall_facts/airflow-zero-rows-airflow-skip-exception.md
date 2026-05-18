---
date: 2026-05-04
wing: role-data-engineer
room: airflow
hall: hall_facts
refs: []
---
KEYS: AirflowSkipException, zero-rows, empty-dataframe, df.empty, skip, PythonOperator

Rule: Every `main()` that produces a DataFrame/record list must guard zero rows with AirflowSkipException:
```python
from airflow.exceptions import AirflowSkipException

if df.empty:
    raise AirflowSkipException("No data rows — <reason>. Task marked as skipped.")
```
Never use silent `return` — task shows green (success) even though zero rows were loaded.
`AirflowSkipException` → yellow (skipped) = expected, benign absence of data.
`AirflowFailException` → red = unexpected, actionable error.
Do NOT catch AirflowSkipException inside the same function.
Apply to: every new PythonOperator pipeline loading from an external source.

retrieval_value: Code-review gate: reject main() that returns silently on empty data.
