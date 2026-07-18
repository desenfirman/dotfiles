---
wing: role-data-engineer
updated: 2026-05-12
---

<!-- AGENT RECALL  : grep_search "KEYS:" + domain terms → read the enclosing drawer block (next ~20 lines). -->
<!-- AGENT WRITE   : append drawer to the matching room section; mark superseded drawers `valid: false`. -->
<!-- COMPACTION    : if total file > 150 lines, consolidate valid:false drawers into a single anti-patterns room. -->

---

## room: bigquery

### drawer: parquet-date-null-type-mismatch
valid: true | scope: repo | timestamp: 2026-04-09
KEYS: parquet, DATE, NULL, INT64, BigQuery, external-table, SAFE_CAST, pyarrow, PostgresToGCSOperator

Rule: Never `CAST(col AS DATE)` on a BQ external Parquet column. Use the double-cast:
```python
SAFE_CAST(SAFE_CAST(`col` AS STRING) AS DATE) AS `col`
```
Handles both real DATE values and all-NULL columns (stored as INT64 in Parquet) without error.
Apply to: any `PostgresToGCSOperator` → Parquet → BQ external table pipeline with DATE-typed columns.
ref: docs/incidents/2026-04-09_supply_chain__logistics_outbound_sap_pipeline__every_5min_bq_invalid_date_cast/

retrieval_value: Any BQ external table load from Parquet with nullable DATE columns must use this cast.

---

### drawer: bq-columns-definition-backtick-all-identifiers
valid: true | scope: repo | timestamp: 2026-04-13
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

---

### drawer: bq-merge-metadata-columns
valid: true | scope: repo | timestamp: 2026-05-04
KEYS: MERGE, id, load_timestamp, MD5, surrogate-key, BigQuery, metadata-columns, TO_HEX

Rule: Every BQ target table must have `id STRING NOT NULL` and `load_timestamp TIMESTAMP NOT NULL`.
- `id` = `TO_HEX(MD5(CONCAT(natural_key_col1, natural_key_col2, ...)))` — computed in MERGE USING subquery.
- `load_timestamp` = `CURRENT_TIMESTAMP()` on both INSERT and UPDATE WHEN clauses.
- Neither column exists in staging; both are derived server-side in BigQuery.
- `id` is NEVER updated on MATCHED rows (derived from immutable natural key).
Apply to: every new pipeline writing to a BQ target table; brownfield refactors add via schema migration.

retrieval_value: Code-review gate: reject target table DDL without id and load_timestamp.

---

## room: airflow

### drawer: airflow-deprecated-execution-date-variables
valid: true | scope: repo | timestamp: 2026-04-15
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

---

### drawer: airflow-zero-rows-airflow-skip-exception
valid: true | scope: repo | timestamp: 2026-05-04
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

---

## room: yaml-driven-dags

### drawer: yaml-anchors-shared-config-values
valid: true | scope: repo | timestamp: 2026-04-10
KEYS: YAML, anchor, alias, base_config, gcp_project_id, gcp_dataset_id, config.yml, Pattern-4

Rule: Any value appearing more than once in `config.yml` MUST be a YAML anchor in `base_config`.
```yaml
base_config:
  gcp_project_id: &gcp_project_id  lnk-dw
  gcp_dataset_id: &gcp_dataset_id  ios_database
  gcp_conn_id:    &gcp_conn_id     prod__gcp__lnk_dw__rw

# In each task:
load-to-gbq-config:
  params:
    project_id: *gcp_project_id    # ← alias, never hardcoded
    dataset_id: *gcp_dataset_id
```
SQL query anchors: define in `_sql_anchors`, reference with `*anchor_name` in tasks.
Apply to: every new or updated `config.yml`; code review rejects literal project_id/dataset_id in task params.

retrieval_value: Code-review gate: reject config.yml with hardcoded project_id or dataset_id in task params.

---
