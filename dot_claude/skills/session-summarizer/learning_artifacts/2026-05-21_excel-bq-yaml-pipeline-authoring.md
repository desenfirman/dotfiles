---

## Session: 2026-05-21 — Excel Online YAML pipeline authoring

**Context**: Created a YAML-driven Airflow pipeline (Excel Online → BigQuery) for finance
cashflow projection. Session involved multiple refinement rounds: DAG rename, SQL template
switch, data type correction, and dbt model prompt advice.

**Skills Used**: role-data-engineer, session-logger, session-summarizer

### What Worked
- Providing `approach: like #file:masterdata` gave the agent a precise structural anchor —
  the first YAML config draft matched the target pattern with minimal scaffolding noise
- Screenshot attachments (Excel row layout + OneDrive folder) gave the agent enough context
  to infer `skiprows`, `usecols`, and column names without asking clarifying questions
- Atomic follow-up requests ("change name into X", "use numeric please") produced clean,
  surgical edits with no drift — short requests beat compound ones for config surgery
- Prefixing `target: #file:cashflow_projection dir manual_data` eliminated ambiguity about
  file placement; the agent created the subdirectory without being told it didn't exist

### What Didn't Work
- First config used `load_data_from_gcs_to_gbq.sql` instead of
  `full_refresh_from_external_gcs_excel_online.sql` → required a correction turn. The agent
  copied from a reference example that happened to use the wrong template for an Excel
  Online source without catching the mismatch proactively
- Financial columns defaulted to `FLOAT64` instead of `NUMERIC` — the agent didn't infer
  precision requirements from domain context ("cashflow projection = monetary data")

### Corrections & Why
| Wrong Output | Root Cause | Fix Applied |
|---|---|---|
| `load_data_from_gcs_to_gbq.sql` used for Excel Online | Agent pattern-matched from reference config that used wrong template; no enforced rule | User: "it should use full_refresh_from_external_gcs_excel_online.sql" |
| `FLOAT64` for financial columns | Agent defaulted to float without inferring domain precision needs | User: "use numeric please" |
| `*default_project_id2` broken anchor | User introduced during manual edit between turns | Fixed as part of the SQL template correction turn |
| `load_timestamp` + `__scheduled_at__` in `columns_definition` | Agent didn't read target SQL template to know which columns it auto-injects | Removed after reading template — these 8 columns are auto-injected |

### Key Learnings
- **Read the SQL template before writing `columns_definition`**: `full_refresh_from_external_gcs_excel_online.sql` auto-injects 8 columns — including `load_timestamp` and `__airflow_scheduled_at__`. Writing them into `columns_definition` causes duplicate column errors at runtime.
- **Excel Online → BQ always uses `full_refresh_from_external_gcs_excel_online.sql`**: State this explicitly upfront or the agent pattern-matches from whatever reference example it finds first.
- **`approach: like #file:X` is the fastest structural anchor**: One file reference eliminates the need to describe schema, nesting, and anchor conventions — the agent reverse-engineers the pattern from the example.
- **Financial domain = NUMERIC, not FLOAT64**: State the type preference upfront for any monetary pipeline, or add one word ("numeric") to the initial request to save a correction turn.

### Skill & Tooling Notes
- `role-data-engineer` SKILL.md is missing a mandatory SQL template rule for Excel Online
  sources — this caused one avoidable correction turn; add: "Excel Online kind MUST use
  `full_refresh_from_external_gcs_excel_online.sql`"
- The skill should include a "financial data type defaults" note: monetary columns → NUMERIC,
  counts/IDs → INT64, ratios → FLOAT64
- Session logger was invoked twice (main log + addendum `_2`) because the critical
  observation surfaced after the main log was written — consider a "late observation"
  workflow in session-logger SKILL.md to avoid `_2` files for addenda

---
