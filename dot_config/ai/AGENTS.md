# Universal Agent Instructions

## Personal memory

Before beginning a task, read `~/.config/ai/personal.md` if it exists. Treat it as private user context and apply it as background preferences. Do not modify it unless explicitly asked, and do not copy its contents into project files, commits, logs, or public output.

## Precedence

1. Explicit user request
2. Project-local instructions
3. `~/.config/ai/personal.md`
4. These universal instructions
5. Tool defaults

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

Full catalog with example invocations: see [`~/.claude/SKILLS.md`](./SKILLS.md).

Skills are discovered at runtime from `~/.agents/skills/*/SKILL.md` (personal) and `.agents/skills/*/SKILL.md` (project).

## Memory System

Agent memory tersimpan di `~/.claude/memory/` menggunakan **MemPalace Spatial Convention** — tanpa vector DB, hanya Python stdlib dan file system.

### Struktur Direktori

```
~/.claude/memory/
  identity.md              ← L0: selalu dibaca di awal setiap sesi (~80 token)
  wing_{project}/
    room_{topic}/
      hall_facts/          ← keputusan final, pilihan yang dikunci
      hall_events/         ← session logs, debugging, milestones
      hall_discoveries/    ← insight baru, breakthroughs, solusi tidak terduga
      hall_preferences/    ← habits, opini, preferensi yang terbentuk
      hall_advice/         ← rekomendasi yang diberikan ke user
```

Setiap drawer = satu file `.md` dengan frontmatter:
```markdown
---
date: YYYY-MM-DD
wing: project-name
room: topic-name
hall: hall_facts
refs: []
---
Isi memori di sini — satu fakta atau event per file.
```

### Aturan Operasional

**Awal sesi:**
1. Baca `~/.claude/memory/identity.md` — selalu.
2. Identifikasi wing yang relevan dengan task saat ini, lalu baca hall yang sesuai via path.

**Saat menyimpan memori baru:**
- Tentukan: wing (project) → room (topic) → hall (jenis memori).
- Satu drawer = satu file. Jangan campurkan fakta berbeda dalam satu file.
- Tulis `refs: [wing_x/room_y/filename.md]` jika ada relasi cross-wing (Tunnel).

**Saat retrieve:**
- Addressed recall: path langsung → `memory/wing_{x}/room_{y}/hall_{z}/`
- Keyword search: grep across wing atau seluruh memory
- Tunnel traversal: ikuti field `refs:` secara manual

### Script Retrieval

Tersedia di `~/.claude/memory/scripts/memory.py` — Python stdlib only:
- `recall(wing, room, hall=None)` → list drawer yang relevan
- `search(keyword, wing=None)` → grep-based scan
- `wake_up(wing)` → identity + top facts dari wing tertentu

@RTK.md

<!-- CODEGRAPH_START -->
## CodeGraph

In repositories indexed by CodeGraph (a `.codegraph/` directory exists at the repo root), reach for it BEFORE grep/find or reading files when you need to understand or locate code:

- **MCP tool** (when available): `codegraph_explore` answers most code questions in one call — the relevant symbols' verbatim source plus the call paths between them, including dynamic-dispatch hops grep can't follow. Name a file or symbol in the query to read its current line-numbered source. If it's listed but deferred, load it by name via tool search.
- **Shell** (always works): `codegraph explore "<symbol names or question>"` prints the same output.

If there is no `.codegraph/` directory, skip CodeGraph entirely — indexing is the user's decision.
<!-- CODEGRAPH_END -->
