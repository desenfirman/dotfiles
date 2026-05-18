# Skills Catalog

All registered skills available across sessions. Updated: 2026-05-18.

---

## Personal Skills
> Location: `~/.agents/skills/`
> Scope: cross-project, always available

### `session-logger`
Export a structured activity log at the end of a work session. Writes into the primary skill's `logs/` folder using the naming convention `yyyy-mm-dd_session_[session-title].log`. Includes an "Observations for Skill Improvement" section for SKILL.md review.

**Example invocations:**
- "export this session into the skill's logs"
- "log agent activity for this session"
- "save what the agent did today"
- "create an audit trail for this session — primary skill was `role-data-engineer`"

---

### `rca-analysis`
Structured root cause analysis using **5 Whys** and **Fishbone diagram**. Use for any production incident, data quality issue, or unexpected regression.

**Example invocations:**
- "run an RCA on why the forecast DAG keeps failing"
- "help me figure out why the BigQuery table is missing rows"
- "do a post-mortem on yesterday's data incident"
- "investigate this problem: [describe issue]"

---

### `prompt-refiner`
Transforms raw or noisy user requests into concise, token-efficient, high-performance prompts for GPT, Claude, or Gemini.

**Example invocations:**
- "make this prompt better: [paste prompt]"
- "write me a good system prompt for a data engineer agent"
- "turn this into a clean master prompt"
- "this prompt isn't working — refine it for Claude"

---

### `decision-council`
Stress-tests an important decision by assembling a council of expert perspectives, surfacing tensions, and producing a synthesized recommendation with next steps.

**Example invocations:**
- "run a decision council on whether to use Kafka or Pub/Sub"
- "stress-test this architecture decision: [describe decision]"
- "I need to choose between dbt Cloud and self-hosted dbt Core — run a council"
- "help me evaluate this trade-off from multiple expert views"

---

### `course-material-generator`
Generates structured course content from a syllabus or outline containing `[course material: ...]` placeholder tags. Processes each section sequentially and replaces placeholders with contextually appropriate written content.

**Example invocations:**
- "generate my course content" + paste outline with placeholders
- "fill in this course outline: [paste sections]"
- "write course material for this syllabus"
- Add a new section heading + placeholder in a follow-up to trigger incremental mode

---

### `one-skill-to-rule-them-all` *(task-observer)*
Monitors ongoing task execution for skill improvement opportunities. Captures patterns, user corrections, and workflow insights worth preserving as reusable skills. Best activated at the start of any multi-step agentic session.

**Example invocations:**
- "activate one skill to rule them all"
- "watch this session for skill opportunities"
- "observe what we're doing and surface reusable patterns"

---

## Project Skills — LNK Airflow Orchestrator
> Location: `lnk-data-platform-orchestrator-airflow/.agents/skills/`
> Scope: project-specific, data platform team roles

### `role-data-engineer`
Build and maintain ETL/ELT pipelines. Author Airflow DAGs, ingest data from APIs/MongoDB/SAP, optimize BigQuery queries, debug failing pipelines.

**Example invocations:**
- "act as the data engineer — create a new DAG for [domain/function]"
- "add a new MongoDB collection to this pipeline config"
- "help me build an incremental ingestion DAG for [source]"
- "debug why this pipeline is failing"

---

### `role-analytics-engineer`
Own the dbt transformation layer. Build and test dbt models, design star schema / SCD, write dbt tests, optimize BigQuery costs.

**Example invocations:**
- "act as the analytics engineer — create a staging model for [source]"
- "write a dbt test for this column"
- "design a star schema for the sales domain"
- "my dbt model is returning duplicates — help me fix it"

---

### `role-data-ops-reliability`
Incident management, on-call support, runbooks, SLA/SLO enforcement, post-mortems. Use for debugging active failures.

**Example invocations:**
- "act as data ops — the [dag_id] DAG is failing in production"
- "write a runbook for this pipeline"
- "create a post-mortem for yesterday's data incident"
- "what's the SLA impact if this pipeline stays down?"

---

### `role-data-platform-infra-engineer`
Manage Airflow infrastructure, Docker, Kubernetes, CI/CD, Airflow connections, and security configuration.

**Example invocations:**
- "act as the infra engineer — debug this Docker build error"
- "add a new Airflow connection for [service]"
- "review this Kubernetes deployment manifest"
- "how do I safely rotate a connection credential in Airflow?"

---

### `role-data-quality-governance`
Enforce data quality standards, manage Airflow Asset lineage, data catalog, and PII compliance.

**Example invocations:**
- "act as data governance — add lineage assets to this DAG"
- "define data quality checks for the [table] table"
- "does this pipeline handle PII correctly?"
- "create an Asset definition for this MongoDB collection"

---

### `role-solution-architect`
System design, technology evaluation, architectural decision records (ADRs), standards enforcement, design reviews.

**Example invocations:**
- "act as solution architect — evaluate Kafka vs Pub/Sub for our streaming layer"
- "write an ADR for using YAML-driven DAG pattern"
- "review this system design: [describe design]"
- "what's the right pattern for real-time vs batch ingestion here?"

---

### `role-tech-lead`
PR code reviews, mentorship, shared library ownership, onboarding, tech debt management, team conventions.

**Example invocations:**
- "act as tech lead — review this DAG implementation"
- "is this code consistent with our team conventions?"
- "write a contribution guide for new team members"
- "identify tech debt in this shared library"

---

### `role-project-manager`
Request triage, backlog prioritization, sprint planning, stakeholder communication, delivery metrics.

**Example invocations:**
- "act as project manager — triage this list of incoming requests"
- "help me prioritize these three pipeline requests"
- "draft a status update for stakeholders on [project]"
- "break down this epic into sprint-sized tasks"

---

### `role-platform-devops-engineer`
Capacity planning, cost tracking, infrastructure scaling, CI/CD pipelines, monitoring, Airflow upgrades.

**Example invocations:**
- "act as platform DevOps — the Airflow workers are OOMing"
- "how do I scale the on-premise worker pool?"
- "review our CI/CD pipeline for DAG deployment"
- "estimate the cost impact of adding 5 new daily DAGs"

---

### `role-wit-creator`
Create structured Work Instructions (WIT / SOP) for data engineering processes, focused on precision, traceability, and audit readiness.

**Example invocations:**
- "act as WIT creator — write a work instruction for adding a new MongoDB source"
- "create an SOP for the schema discovery workflow"
- "document this data ingestion process as a WIT"
- "turn this runbook into a formal work instruction"
