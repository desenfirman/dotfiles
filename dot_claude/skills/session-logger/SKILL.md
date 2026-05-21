---
name: session-logger
description: "Log agent activity at the end of a work session. Use when: exporting a session log, logging agent activity, saving what the agent did, creating a session audit trail, reviewing agent invocations, improving skill definitions. Writes a dated .log file into the relevant skill's logs/ folder with one line per agent action in the format [datetime iso] - CATEGORY: description - [optional script/file]."
argument-hint: "Optional: skill name to log into (e.g. role-data-engineer). Defaults to the primary skill used in the session."
---

# Session Logger

## Purpose
Produce a structured, human-readable audit log of everything the agent did during a session. Stored inside the relevant skill's `logs/` directory for later review and skill improvement.

## When to Use
Invoke at the **end** of a work session when the user says things like:
- "export this session into the skill's logs"
- "log agent activity"
- "save what the agent did"
- "create a session log"
- "audit trail for this session"

---

## Output Format

Each log file is named using the pattern:
```
yyyy-mm-dd_session_[session-title].log
```

Where `session-title` is a short, lowercase kebab-case slug describing the session goal (e.g. `add-5-collections-kpi-oneltl`, `create-mongo-bq-template`, `fix-forecast-dag-schedule`).

The file is placed in:
```
<skill-dir>/logs/yyyy-mm-dd_session_[session-title].log
```

Where `skill-dir` resolves in this priority order:
1. **Project-scoped**: `.agents/skills/<primary-skill>/` (if the session was project-specific)
2. **Personal-scoped**: `~/.agents/skills/<primary-skill>/` (if the skill lives only at user level)

If multiple sessions share the same title on the same day, append `_2`, `_3`, etc.

### File Structure
```
# Session Log — <primary-skill>
# Date: YYYY-MM-DD
# Workspace: <repo name>
# Tasks: <short description of session goals>
# ─────────────────────────────────────────────────────────────────────────────

<log entries>

# ─────────────────────────────────────────────────────────────────────────────
# Observations for Skill Improvement:
#
# 1. <category>: <what went wrong or was suboptimal>
#    Recommended fix: <what to add/change in SKILL.md>
# ─────────────────────────────────────────────────────────────────────────────
```

### Log Entry Format
```
YYYY-MM-DDThh:mm:ss+07:00 - CATEGORY: description - [optional: path/to/script_or_file] — est token: <N>
```

`est token` is a rough estimate of tokens consumed by that agent turn, computed as `len(all text in turn) / 4` rounded to the nearest 100. Omit if the turn involved no significant model output (e.g. pure file reads).

### Entry Categories

| Category | When to Use |
|---|---|
| `SKILL LOADED` | Agent read a SKILL.md file to guide its workflow |
| `CONTEXT READ` | Agent read a file to understand existing structure |
| `FILE CREATED` | Agent created a new file |
| `FILE MODIFIED` | Agent modified an existing file |
| `SCRIPT INVOKED` | Agent ran a terminal command or script |
| `TASK START` | A new discrete task began |
| `WORKAROUND` | An unexpected limitation forced a detour from the happy path |
| `ISSUE` | A problem was encountered (empty data, missing field, etc.) |
| `CORRECTION` | Agent had to fix/normalize output before using it |
| `VALIDATION` | Agent ran a verification step to confirm correctness |
| `SESSION COMPLETE` | Session ended successfully |

---

## Procedure

### Step 1 — Identify Primary Skill
Look at the conversation history or session summary. Find which `SKILL.md` was loaded (e.g. `role-data-engineer`, `role-analytics-engineer`). That skill's `logs/` directory receives the log.

If the user specifies a skill name as the argument, use that instead.

If no skill was loaded, log into `.agents/skills/session-logs/` at the workspace root.

### Step 2 — Determine Session Title
Derive a short kebab-case slug from the session's main goal:
- Strip filler words ("a", "the", "to", "and")
- Max 5–6 words
- Examples: `add-5-collections-kpi-oneltl`, `create-mongo-bq-template`, `fix-forecast-schedule`

### Step 3 — Reconstruct the Timeline
Scan the conversation summary and terminal history for:
- Files read (context gathering)
- Skills loaded
- Files created or modified
- Terminal commands / scripts invoked
- Errors, workarounds, and corrections applied
- Validation steps run

Use timestamps from terminal output where available. Approximate other timestamps by interpolating between known anchors (session start, session end).

For each entry, estimate tokens consumed by that agent turn: count all characters (prompt + response + tool outputs) and divide by 4, rounded to the nearest 100. Append as `— est token: <N>` at the end of the line.

### Step 4 — Identify Observations
After building the timeline, review for recurring friction patterns:
- Did the agent need a workaround for something the skill should have warned about?
- Did the agent have to normalize/correct output from a referenced script?
- Was there a decision point the skill left ambiguous?
- Did the agent scaffold missing data (e.g. empty collection) with no guidance?

Each observation becomes a numbered comment block at the bottom of the log file.

### Step 5 — Write the Log File
Create the file at `<skill-dir>/logs/yyyy-mm-dd_session_[session-title].log`.

Ensure the `logs/` subdirectory exists (create it if not).

### Step 6 — Confirm to User
Report:
- File path created
- Number of log entries written
- Number of skill improvement observations captured
- Suggest which section of `SKILL.md` each observation should improve

---

## Example Session Log

```
# Session Log — role-data-engineer
# Date: 2026-05-18
# Workspace: lnk-data-platform-orchestrator-airflow
# Tasks: Add 5 new MongoDB collections to kpi_oneltl pipeline
# ─────────────────────────────────────────────────────────────────────────────

2026-05-18T10:01:12+07:00 - SKILL LOADED: role-data-engineer SKILL.md read to guide DAG authoring workflow — est token: 800
2026-05-18T10:02:00+07:00 - CONTEXT READ: dags/lnk/domain/people/kpi_oneltl/config.yml — est token: 1200
2026-05-18T10:12:00+07:00 - WORKAROUND: fish shell does not support `VAR=val cmd` inline env var syntax. Used `set -x VAR val` instead - scripts/mongodb_source_definition_generator.py — est token: 600
2026-05-18T10:16:00+07:00 - SCRIPT INVOKED: scripts/mongodb_source_definition_generator.py --conn-id prod__mongo__one_employee__rw --collection t_kpi_strategic_map_corporate_detail — est token: 1800
2026-05-18T10:22:00+07:00 - ISSUE: t_kpi_ham_detail returned 0 documents — collection empty in current environment — est token: 400
2026-05-18T10:23:00+07:00 - WORKAROUND: Scaffolded t_kpi_ham_detail schema manually, mirroring t_kpi_vam_detail structure — est token: 900
2026-05-18T10:30:00+07:00 - CORRECTION: Generator outputs *gcp_project_id but config uses *default_project_id — renamed all aliases — est token: 500
2026-05-18T10:35:00+07:00 - FILE MODIFIED: dags/lnk/domain/people/kpi_oneltl/config.yml — 5 collections added to &default_dag_config — est token: 2400
2026-05-18T10:47:21+07:00 - VALIDATION: python -c "import yaml; parse config.yml; print task IDs" — est token: 700
2026-05-18T10:47:21+07:00 - SESSION COMPLETE

# ─────────────────────────────────────────────────────────────────────────────
# Observations for Skill Improvement:
#
# 1. WORKAROUND: Fish shell env var syntax not documented in skill.
#    Recommended fix: Add "Shell Environment Setup" section to SKILL.md
#    with fish-compatible syntax for pre-exporting connection strings.
#
# 2. CORRECTION: mongodb_source_definition_generator.py outputs wrong
#    anchor names and backtick-wrapped unique_identifier every run.
#    Recommended fix: Add a "Generator Output Normalization" step to the
#    schema discovery section of SKILL.md.
# ─────────────────────────────────────────────────────────────────────────────
```

---

## Notes
- Timestamps use `Asia/Jakarta` timezone (`+07:00`). Adjust for your local timezone if needed.
- Log files are append-only artifacts — never edit a previously written log.
- The `logs/` folder inside each skill directory is the canonical location.
