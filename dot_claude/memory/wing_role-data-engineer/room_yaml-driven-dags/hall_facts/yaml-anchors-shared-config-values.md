---
date: 2026-04-10
wing: role-data-engineer
room: yaml-driven-dags
hall: hall_facts
refs: []
---
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
