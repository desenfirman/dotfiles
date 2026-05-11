# Claude Global Memory

## Global Context

This file is loaded automatically by Claude Code and compatible agents at the start of every session.
It establishes shared context, working preferences, and pointers to available skills.

- Primary domain: data engineering, analytics engineering, and platform/DevOps provisioning.
- Data stack: BigQuery (warehouse), dbt (transformations), Cloud Composer / Airflow (orchestration), GCS (storage).
- Infrastructure: GCP-first, containers via Docker/Docker Compose, provisioning via chezmoi dotfiles.
- Version control: Git with GitHub; follow conventional commits where applicable.

## Working Style

- **Language preference**: Python first; shell (bash/fish) for environment glue scripts.
- **SQL dialect**: BigQuery Standard SQL; prefer CTEs over nested subqueries.
- **dbt patterns**: use ref() and source() macros, keep models in staging/intermediate/mart layers.
- **Brevity**: be concise and direct — skip boilerplate explanations unless asked.
- **Code over prose**: prefer working code snippets over abstract descriptions.
- **Idempotency**: all provisioning and migration scripts must be safe to re-run.
- **Security**: never hardcode credentials; use environment variables or secret managers.

## Active Skills

The following skills are registered under `skills/` and are available to assist in sessions:

| Skill | Description |
|-------|-------------|
| `rca-analysis` | Structured root cause analysis for production incidents and data quality issues |
| `prompt-refiner` | Iteratively refine and improve prompts for AI agents and LLM pipelines |
| `course-material-generator` | Generate structured course outlines, exercises, and learning materials |

Skills are discovered at runtime from `~/.claude/skills/*/SKILL.md`.
