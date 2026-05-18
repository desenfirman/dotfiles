---
date: 2026-05-16
wing: role-data-engineer
room: bigquery
hall: hall_facts
refs: []
---
KEYS: parquet, gcs, bigquery, load, date, null, type mismatch, GcsToBigQueryOperator, schema, INT96

When loading Parquet files from GCS to BigQuery using `GCSToBigQueryOperator`, DATE columns
that contain null values may be inferred as INT64 (epoch days) instead of DATE by BigQuery's
schema auto-detection. This causes a type mismatch error at load time:
`Error while reading data, error message: Parquet column 'col_name' has type INT64 ...`

**Fix:** The fix happens at the **load process** — when BigQuery reads a DATE column that was
inferred as INT64, apply a double-cast during load using a `schema_update_options` or, more
reliably, in a post-load transformation step. When loading or selecting a DATE-typed column
that may have been stored as a numeric type in Parquet, cast it explicitly:

```sql
CAST(CAST(col AS STRING) AS DATE) AS col
```

This forces BigQuery to re-interpret the raw numeric/string value as a proper DATE, avoiding
the INT64 → DATE type mismatch error.

Additionally, always provide an explicit `schema_fields` or `schema_object` in
`GCSToBigQueryOperator` to prevent schema auto-detection issues:

```python
GCSToBigQueryOperator(
    task_id="load_to_bq",
    bucket="{{ var.value.gcs_bucket }}",
    source_objects=["path/to/file.parquet"],
    destination_project_dataset_table="project.dataset.table",
    source_format="PARQUET",
    schema_object="schemas/my_table_schema.json",  # ← mandatory, no autodetect
    write_disposition="WRITE_TRUNCATE",
    autodetect=False,  # ← must be False
)
```

retrieval_value: Apply this whenever generating a DAG that loads Parquet from GCS to BigQuery,
or when writing SELECT queries over a table loaded from Parquet with nullable DATE columns.
