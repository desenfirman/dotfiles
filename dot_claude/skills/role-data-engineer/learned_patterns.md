# Learned Patterns — LNK Data Engineer

> **Purpose:** Codified lessons from real incidents and pipeline work on the LNK Data Platform.  
> **Audience:** Data Engineers, Tech Lead  
> **Owner:** `@mis.stf08`  
> **Last updated:** 2026-05-12  

---

## Pattern Index

| # | Pattern | Domain | Source |
|---|---------|--------|--------|
| 1 | [Parquet DATE columns → BigQuery external table type mismatch](#1-parquet-date-columns--bigquery-external-table-type-mismatch) | BigQuery / GCS / Parquet | Incident 2026-04-09 |
| 2 | [YAML anchors for shared config values in config.yml DAGs](#2-yaml-anchors-for-shared-config-values-in-configyml-dags) | YAML-driven DAGs | Standard 2026-04-10 |
| 3 | [Always wrap column names in backticks inside `columns_definition`](#3-always-wrap-column-names-in-backticks-inside-columns_definition) | BigQuery / config.yml DAGs | Incident 2026-04-13 |
| 4 | [Use `logical_date` / `data_interval_start` / `data_interval_end` instead of `execution_date` / `next_execution_date`](#4-use-logical_date--data_interval_start--data_interval_end-instead-of-execution_date--next_execution_date) | Airflow DAGs | Standard 2026-04-15 |
| 5 | [Raise `AirflowSkipException` when a pipeline produces zero rows](#5-raise-airflowskipexception-when-a-pipeline-produces-zero-rows) | Airflow DAGs | Standard 2026-05-04 |
| 6 | [Standard metadata columns: `id` and `load_timestamp` on every target table](#6-standard-metadata-columns-id-and-load_timestamp-on-every-target-table) | BigQuery / Pipeline Standards | Standard 2026-05-04 |
| 7 | [Excel Online via Graph API — prefer binary download + pd.read_excel over usedRange JSON](#7-excel-online-via-graph-api--prefer-binary-download--pdread_excel-over-usedrange-json) | Excel Online / Microsoft Graph API | Standard 2026-05-12 |

---

## 1. Parquet DATE columns → BigQuery external table type mismatch

### Context

When using `PostgresToGCSOperator` (or any pyarrow-based Parquet writer) to export Postgres `DATE` columns, then loading into BigQuery via an external table, type mismatches cause `Invalid cast` errors at query time.

### Root Cause

| Parquet state | BQ external table type | Why |
|---|---|---|
| Column has real `DATE` values | `DATE` | pyarrow writes `date32` logical type; BQ promotes to `DATE` |
| Column is **all-NULL** | `INT64` | pyarrow has no values to infer a type → writes Parquet `null` logical type → BQ defaults to `INT64` |

When BQ reads the column as `INT64` and the generated SQL expression is `CAST(\`col\` AS DATE)`, the query fails:
```
BadRequest: 400 … Query error: Invalid cast from INT64 to DATE
```

### Failed Approaches

| Approach | Why it fails |
|---|---|
| `::TEXT` cast at Postgres export (GCS level) | When all values are NULL, pyarrow still writes `null` Parquet type regardless of upstream SQL cast. BQ still reads INT64. |
| `DATE_FROM_UNIX_DATE(SAFE_CAST(\`col\` AS INT64))` at BQ load | Treats real DATE values as Unix epoch integers — corrupts actual dates when the column has real data. |

### Correct Fix

**Apply a double-cast through STRING at the BigQuery load step (`columns_formatted_to_bq`):**

```python
# In the column builder for `columns_formatted_to_bq`:
f'SAFE_CAST(SAFE_CAST(`{col}` AS STRING) AS DATE) AS `{col}`'
```

**Why this works:**

| Scenario | BQ column type | Cast path | Result |
|---|---|---|---|
| Column has real `DATE` values | `DATE` | `DATE → '2024-01-01' → DATE` | ✓ Correct date |
| Column is all-NULL | `INT64` | `NULL → NULL → NULL` | ✓ NULL, no error |

- `SAFE_CAST(anything AS STRING)` never throws — it converts or returns NULL.
- `SAFE_CAST(STRING AS DATE)` succeeds only for `'YYYY-MM-DD'` format strings; NULL passes through.
- This is **polymorphic**: it handles both type states without knowing which one will occur at runtime.

### Implementation Reference

File: `dags/lnk/domain/supply_chain/logistics_outbound_sap/task_group.py`

```python
columns_formatted_to_bq = ', '.join(
    [
        f'{tup[3]} AS `{tup[0]}`' if len(tup) > 3                                           # custom expression override
        else f'SAFE_CAST(SAFE_CAST(`{tup[0]}` AS STRING) AS DATE) AS `{tup[0]}`' if tup[1] == 'DATE'  # DATE columns
        else f'CAST(`{tup[0]}` AS {tup[1]}) AS `{tup[0]}`'                                  # all other types
        for tup in config['pg_columns_to_load_in_bq']
    ]
)
```

Column specs in `specs.py` use tuples `(column_name, bq_type, mode[, custom_expr])`:
```python
('loading_date', 'DATE', 'NULLABLE'),          # → SAFE_CAST(SAFE_CAST(...) AS STRING) AS DATE)
('goods_issue_time', 'TIMESTAMP', 'NULLABLE',  # → custom expression (len > 3)
 "TIMESTAMP(DATETIME(DATE '1900-01-01', `goods_issue_time`))"),
```

### Rule of Thumb

> **Never use `CAST(\`col\` AS DATE)` directly on a BigQuery external Parquet table column.**  
> Always use `SAFE_CAST(SAFE_CAST(\`col\` AS STRING) AS DATE)` to guard against the all-NULL `INT64` edge case.

### When to Apply

- Any pipeline using `PostgresToGCSOperator` → Parquet → BigQuery external table → INSERT/MERGE.
- Any pipeline using `pandas.to_parquet` / pyarrow with `DATE`-typed source columns.
- Columns that are **nullable** and may be entirely NULL in a given time partition/batch.

### Related Incident

`docs/incidents/2026-04-09_supply_chain__logistics_outbound_sap_pipeline__every_5min_bq_invalid_date_cast/`
- [POSTMORTEM.md](../../docs/incidents/2026-04-09_supply_chain__logistics_outbound_sap_pipeline__every_5min_bq_invalid_date_cast/POSTMORTEM.md)
- [RCA.md](../../docs/incidents/2026-04-09_supply_chain__logistics_outbound_sap_pipeline__every_5min_bq_invalid_date_cast/RCA.md)

---

## 2. YAML anchors for shared config values in config.yml DAGs

### Context

YAML-driven DAGs (Pattern 4) define a `base_config` block at the top of `config.yml` that holds shared values like `gcp_project_id`, `gcp_dataset_id`, and connection IDs. Without anchors, these values are duplicated in every `load-to-gbq-config.params` block across every task, making updates error-prone.

### Problem

Hardcoding `project_id` and `dataset_id` inside each task block:

```yaml
load-to-gbq-config:
  sql: load_data_from_gcs_to_gbq.sql
  params:
    project_id: lnk-dw          # ← duplicated N times
    dataset_id: ios_database    # ← duplicated N times
    table_id: my_table
```

- Any dataset/project change requires editing every task individually.
- Risk of partial updates leaving inconsistent dataset targets across tasks in the same DAG.

### Correct Pattern

Declare YAML anchors in `base_config` and reference them via aliases (`*`) in every task:

```yaml
base_config:
  gcp_project_id:  &gcp_project_id   lnk-dw
  gcp_dataset_id:  &gcp_dataset_id   ios_database
  location:        asia-southeast2
  sql_conn_id:     &ios_conn_id      prod__postgres__ios_db__rw
  gcp_conn_id:     &gcp_conn_id      prod__gcp__lnk_dw__rw

# In each task:
load-to-gbq-config:
  sql: load_data_from_gcs_to_gbq.sql
  params:
    project_id: *gcp_project_id    # ← alias, resolved from base_config
    dataset_id: *gcp_dataset_id    # ← alias, resolved from base_config
    table_id: my_table
```

### Rules

1. **All** `project_id` and `dataset_id` values inside `load-to-gbq-config.params` **must** use `*gcp_project_id` and `*gcp_dataset_id` aliases — never hardcoded strings.
2. SQL query anchors (e.g. `&my_table_sql`) follow the same convention: define once in `_sql_anchors`, reference with `*my_table_sql` in the task.
3. Connection IDs (`source_connection_id`, `dest_connection_id`) in task groups should also reference `*ios_conn_id` / `*gcp_conn_id` anchors where supported by the parser.
4. `base_config` is the **single source of truth** for all shared scalar values in the file.

### Anchor Naming Convention

| Anchor | Value type |
|---|---|
| `&gcp_project_id` | GCP project ID string |
| `&gcp_dataset_id` | BigQuery dataset ID string |
| `&gcp_conn_id` | GCP Airflow connection ID |
| `&ios_conn_id` | IOS/source Postgres connection ID |
| `&<table_name>_sql` | SQL query string for a specific table |

### Implementation Reference

Files: `dags/lnk/domain/supply_chain/logistics_*/config.yml`

### Rule of Thumb

> **Any value that appears more than once in a `config.yml` must be defined as a YAML anchor.**  
> Never hardcode `project_id` or `dataset_id` in individual task blocks when `base_config` already defines them.

### When to Apply

- Every new or updated `config.yml` for YAML-driven DAGs (Pattern 4).
- Code review: reject PRs that have literal `project_id: lnk-dw` or `dataset_id: <name>` inside task `params` blocks when `base_config` anchors exist.

---

*Add new patterns below this line following the same structure.*

---

## 7. Excel Online via Graph API — usedRange JSON used instead of binary download

**Date:** 2026-05-12  
**Pipeline:** `trade_marketing__kpi__monthly`  
**File:** `dags/lnk/domain/trade_marketing/kpi/main.py`

Initial implementation called the `usedRange` JSON endpoint and manually extracted `rows[0]` as headers, then constructed the DataFrame with `dict(zip(...))`. The prompt specified that endpoint explicitly so it was followed, but `MicrosoftGraphAPI._perform_request()` + `/content` + `pd.read_excel(..., header=0)` would have been simpler and removed all manual header handling.

Corrected in the same session by replacing `_fetch_sheet_data()` with `_fetch_sheet_df()`.

**Standard:** see `standards.md` → *Excel Online / Graph API ingestion*

---

## 4. Use `logical_date` / `data_interval_start` / `data_interval_end` instead of `execution_date` / `next_execution_date`

### Context

Airflow 2.2 deprecated `execution_date` and `next_execution_date` in favour of clearer, semantically correct variables. Using the old names in new code causes `RemovedInAirflow3Warning` deprecation warnings and will break in Airflow 3.x.

### Mapping

| Deprecated (Airflow ≤ 2.1) | Replacement (Airflow ≥ 2.2) | Notes |
|---|---|---|
| `execution_date` | `logical_date` | The logical schedule date of the DAG run. In Jinja: `{{ logical_date }}` |
| `next_execution_date` | `data_interval_end` | The end boundary of the data interval. In Jinja: `{{ data_interval_end }}` |
| `prev_execution_date` | `data_interval_start` | The start boundary of the data interval. In Jinja: `{{ data_interval_start }}` |
| `context['execution_date']` (Python) | `context['logical_date']` | Inside `python_callable(**context)` |
| `context['next_execution_date']` (Python) | `context['data_interval_end']` | Inside `python_callable(**context)` |

### Correct Usage — Jinja Templates

```python
# ✅ Correct
subject="Report {{ data_interval_end.in_timezone('Asia/Jakarta').strftime('%d %B %Y') }}"

local_path=(
    "/tmp/report-"
    "{{ data_interval_end.in_timezone('Asia/Jakarta').strftime('%Y%m%d') }}.xlsx"
)

# ❌ Deprecated
subject="Report {{ next_execution_date.in_timezone('Asia/Jakarta').strftime('%d %B %Y') }}"
```

### Correct Usage — Python Callables

```python
def run_task(**context):
    # ✅ Correct
    logical_date       = context['logical_date']          # pendulum.DateTime
    data_interval_start = context['data_interval_start']  # pendulum.DateTime
    data_interval_end   = context['data_interval_end']    # pendulum.DateTime

    run_date = data_interval_end.in_timezone('Asia/Jakarta').strftime('%Y-%m-%d')

    # ❌ Deprecated
    # execution_date = context['execution_date']
    # next_execution_date = context['next_execution_date']
```

### Airflow Metadata DB

The `dag_run` table uses `logical_date` as the canonical column name (Airflow 2.2+). Use it in diagnostic SQL:

```sql
SELECT
    dag_id,
    logical_date AS last_run,
    NOW() - logical_date AS time_since_last_run
FROM dag_run
WHERE state = 'success'
ORDER BY logical_date DESC;
```

### Rules

1. **Never** use `execution_date` or `next_execution_date` in new DAG code (Jinja, Python, SQL).
2. Use `logical_date` when you need the schedule timestamp of the run.
3. Use `data_interval_start` / `data_interval_end` when you need the data window boundaries — prefer these for date-parameterised queries.
4. When backfilling or running catchup DAGs, `data_interval_start`/`end` correctly represent the data window; `logical_date` is the schedule date.
5. Update existing DAGs and scripts that reference deprecated variables whenever touching those files.

### Rule of Thumb

> **Use `data_interval_end` for "what date is this report for?" and `logical_date` for "when was this run scheduled?".**  
> Never write `execution_date` or `next_execution_date` — they are deprecated and will be removed in Airflow 3.

### When to Apply

- All new DAG authoring (Jinja templates, Python callables, SQL parameters).
- Code review: reject PRs containing `execution_date` or `next_execution_date` in DAG files.
- When migrating legacy DAGs.
- Diagnostic queries against the Airflow metadata DB.

---

## 3. Always wrap column names in backticks inside `columns_definition`

### Context

YAML-driven DAGs (Pattern 4) use a `columns_definition` block inside `load-to-gbq-config.params` to define the BigQuery `SELECT` projection used in the load SQL template (e.g. `full_refresh_from_external_gcs.sql`). Column names and aliases are written as plain identifiers — without backticks — which causes failures when any column name collides with a BigQuery reserved word.

### Root Cause

BigQuery reserves many common English words as SQL keywords: `NO`, `IN`, `OUT`, `DAY`, `DATE`, `STATUS`, `TYPE`, `DESC`, etc. When any column or alias in a `CAST(col AS TYPE) AS alias` expression matches a reserved word and is not quoted, BigQuery raises a syntax error at query execution time:

```
Syntax error: Expected end of input but got keyword NO at [1:63]
```

This error is silent at DAG-parse time (Airflow only validates YAML/Python, not SQL semantics), so it only surfaces when the DAG actually runs.

### Failed Approach

Only quoting known reserved words (e.g. adding backticks to `no`, `in`, `out` while leaving others unquoted):

```yaml
columns_definition: >
  CAST(date AS DATE) AS date,
  CAST(`no` AS INT64) AS `no`,   # ← backtick added after error
  CAST(status AS STRING) AS status
```

- Brittle: requires knowing every reserved word in advance.
- Error-prone: any new column added later may silently be a reserved word.
- Inconsistent: mixed style within the same block.

### Correct Pattern

**Always wrap every column name and alias in backticks**, without exception:

```yaml
columns_definition: >
  CAST(`date` AS DATE) AS `date`,
  CAST(`no` AS INT64) AS `no`,
  CAST(`status` AS STRING) AS `status`,
  CAST(`accuracy_of_information_from_driver_or_transporter` AS STRING) AS `accuracy_of_information_from_driver_or_transporter`
```

### Rules

1. **Every** identifier in `columns_definition` — both inside `CAST(...)` and after `AS` — **must be backtick-quoted**, regardless of whether it is a known reserved word.
2. Apply this uniformly to all `columns_definition` blocks in every `config.yml` file.
3. This rule applies equally to the `load_data_from_gcs_to_gbq.sql` and `full_refresh_from_external_gcs.sql` load strategies.
4. Code review: reject any `columns_definition` block containing unquoted identifiers.

### Known BigQuery Reserved Words That Appear in IOS Tables

| Column | Table |
|---|---|
| `no` | `t_rmpm`, `t_pra_loading` |
| `in` | `t_do` |
| `out` | `t_do` |
| `desc` | `t_do` |
| `date` | multiple |
| `status` | multiple |
| `type` | multiple |

### Implementation Reference

Files: `dags/lnk/domain/supply_chain/logistics_*/config.yml`

### Rule of Thumb

> **Always backtick every column name and alias in `columns_definition` — never write bare identifiers.**  
> Backtick-quoting is idempotent and harmless for non-reserved names; omitting it for reserved words causes runtime SQL errors that only surface when the DAG executes.

### When to Apply

- Every `columns_definition` block in any new or updated `config.yml` for YAML-driven DAGs.
- When converting `load_data_from_gcs_to_gbq.sql` → `full_refresh_from_external_gcs.sql` (both use the same `columns_definition` parameter).
- Code review: reject PRs with unquoted identifiers in `columns_definition`.

---

## 5. Raise `AirflowSkipException` when a pipeline produces zero rows

### Context

Pipelines that read from external sources (Excel Online, APIs, databases) may legitimately produce zero rows — e.g. no period columns detected, source file is empty, or all rows filtered out. Silently returning `None` from a task makes the task appear **successful** in Airflow, hiding the fact that no data was processed.

### Problem

Using `return` or `logger.warning()` and exiting early:

```python
if df.empty:
    logger.warning("No records to load.")
    return  # ← task shows green in Airflow UI — misleading
```

- The task shows ✅ success even though zero rows were loaded.
- Downstream consumers or on-call engineers have no signal that data is missing.
- Incidents can go undetected until someone notices stale data.

### Correct Pattern

Raise `AirflowSkipException` so the task turns **yellow (skipped)** in the Airflow UI:

```python
from airflow.exceptions import AirflowSkipException

if df.empty:
    raise AirflowSkipException(
        "No data rows produced — source may be empty or no valid columns detected. "
        "Task marked as skipped."
    )
```

### Why `AirflowSkipException` and not `AirflowFailException`?

| Signal | Semantics | Use when |
|---|---|---|
| `AirflowSkipException` | Expected, benign absence of data | Source legitimately has no data to process |
| `AirflowFailException` | Unexpected, actionable error | Pipeline broke — requires investigation |
| Silent `return` | **Never** | Never use for zero-row guard |

Zero rows from an Excel file or API is often **expected** (e.g. off-schedule run, empty staging folder). Skipping is the correct signal: it alerts without paging, and downstream sensors can handle it gracefully.

### Rules

1. **Every `main()` function** that produces a DataFrame or record list **must** guard against zero rows with `AirflowSkipException`.
2. The exception message must describe **why** data is empty (e.g. "no period columns detected", "API returned 0 records").
3. Do **not** catch `AirflowSkipException` inside the same function — let Airflow handle it.
4. Intermediate helpers may return an empty structure; only the top-level `main()` raises.

### Implementation Reference

File: `dags/lnk/domain/finance/cashflow_projection/main.py`

```python
from airflow.exceptions import AirflowSkipException

def main(**kwargs) -> None:
    ...
    df = _parse_excel(excel_bytes)

    if df.empty:
        raise AirflowSkipException(
            "No period columns or data rows were found in the sheet. "
            "Task marked as skipped."
        )
    ...
```

### When to Apply

- Every new PythonOperator-based pipeline that loads data from an external source.
- Any existing pipeline that currently uses `return` as a zero-row guard.
- Code review: reject PRs where `main()` returns silently on empty data.

---

## 6. Standard metadata columns: `id` and `load_timestamp` on every target table

### Context

Every BigQuery target table written by a pipeline must carry two standard metadata columns — a deterministic surrogate key (`id`) and an audit timestamp (`load_timestamp`). These are computed **server-side by BigQuery** during the MERGE so that:
- Python code stays free of hashing logic.
- `id` is always consistent regardless of language or framework.
- `load_timestamp` reflects the actual BigQuery write time, not the Airflow task start time.

### Rules

1. **`id`** — `STRING NOT NULL`. Computed as `TO_HEX(MD5(CONCAT(key_col_1, key_col_2, ...)))` using the same columns that form the MERGE `ON` clause (the natural key of the record).
2. **`load_timestamp`** — `TIMESTAMP NOT NULL`. Set to `CURRENT_TIMESTAMP()` on every INSERT and every UPDATE.
3. Both columns are **not** present in the staging table — they are derived inside the MERGE `USING` subquery or the `WHEN` clauses.
4. `id` is **never updated** on a MATCHED row (it is derived from the natural key which cannot change).
5. Always declare both columns in `CREATE TABLE IF NOT EXISTS` DDL.

### Correct Pattern

```python
merge_sql = f"""
    MERGE {tgt_full} AS T
    USING (
        SELECT
            TO_HEX(MD5(CONCAT(col_a, col_b))) AS id,
            col_a,
            col_b,
            value
        FROM {stg_full}
    ) AS S
    ON  T.col_a = S.col_a
    AND T.col_b = S.col_b
    WHEN MATCHED THEN
        UPDATE SET
            T.`value`          = S.`value`,
            T.`load_timestamp` = CURRENT_TIMESTAMP()
    WHEN NOT MATCHED BY TARGET THEN
        INSERT (`id`, `col_a`, `col_b`, `value`, `load_timestamp`)
        VALUES (S.`id`, S.`col_a`, S.`col_b`, S.`value`, CURRENT_TIMESTAMP())
"""
```

DDL to match:

```sql
CREATE TABLE IF NOT EXISTS `project.dataset.table` (
    `id`             STRING    NOT NULL,
    `col_a`          STRING    NOT NULL,
    `col_b`          STRING    NOT NULL,
    `value`          FLOAT64,
    `load_timestamp` TIMESTAMP NOT NULL
)
```

### Implementation Reference

File: `dags/lnk/domain/finance/cashflow_projection/main.py`

```python
# MERGE computes id = TO_HEX(MD5(CONCAT(metric, period)))
# load_timestamp = CURRENT_TIMESTAMP() on both INSERT and UPDATE
```

### When to Apply

- Every new PythonOperator pipeline that writes to a BigQuery target table.
- Brownfield pipelines being refactored — add both columns in a schema migration.
- Code review: reject PRs that create target tables without `id` and `load_timestamp`.
