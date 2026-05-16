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
| `decision-council` | Stress-test an important decision by running a structured council of expert perspectives |
| `one-skill-to-rule-them-all` | Monitor task execution for skill improvement opportunities; invoke at the start of every task-oriented session |
| `role-data-engineer` | Data Engineer role — build and maintain ETL/ELT pipelines, Airflow DAGs, BigQuery optimization |

Skills are discovered at runtime from `~/.claude/skills/*/SKILL.md`.

## Task Observer — Skill Improvement

At the start of any task-oriented session — any interaction where you will
use tools and produce deliverables — invoke the task-observer skill before
beginning work. This ensures skill improvement opportunities are captured
throughout the session.

When loading any skill, check the observation log for OPEN observations
tagged to that skill. Apply their insights to the current work, even if
the skill file hasn't been updated yet.

**Workspace folder** (for task-observer paths): `~/.local/share/chezmoi`

- Observation log: `~/.local/share/chezmoi/skill-observations/log.md`
- Cross-cutting principles: `~/.local/share/chezmoi/skill-observations/cross-cutting-principles.md`
- Skill updates staging: `~/.local/share/chezmoi/skill-updates/`
