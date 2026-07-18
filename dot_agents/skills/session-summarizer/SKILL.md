---
name: session-summarizer
description: >
  Summarize an AI interaction session into a structured learning entry and append it to
  a running AI-effectiveness log (ai-learnings.md). Use when a session involved
  non-trivial prompting, skill use, agent orchestration, or problem-solving with Claude.
  Captures what worked, what failed, and why — not what was built.
---

# Summarize AI Session Skill

This skill performs **AI interaction debriefing** — reviewing how the current session
was conducted and extracting reusable learnings about working effectively with LLMs.

**Purpose**: Build a compounding personal knowledge base on AI effectiveness, separate
from domain/codebase knowledge. Output is a single dated entry appended to `ai-learnings.md`.

---

## When to Use

Trigger this skill when:
- A session involved meaningful back-and-forth before getting to a good result
- You made corrections or re-prompted more than twice
- You used a skill, tool, or prompt pattern worth remembering
- The AI surprised you — positively or negatively
- You explicitly ask: "session debrief", "summarize ai session", "ai learnings", "what did I learn about prompting"

Do NOT trigger for:
- Purely factual Q&A sessions with no interesting interaction dynamics
- Sessions you won't want to repeat or reference

---

## Workflow

### Phase 1: Interaction Archaeology

Review the full conversation and extract raw observations across these categories:

#### 1. Prompt Patterns
- What phrasings, framings, or structures produced the best outputs?
- What instructions were ignored, misunderstood, or over-interpreted?
- Were there assumption challenges that improved the result?
- Did providing examples (few-shot) noticeably change quality?

#### 2. Skill & Tool Usage
- Which skills were invoked, and did they trigger correctly?
- Were there friction points in skill activation or output format?
- Was tool chaining (e.g., search → synthesize → format) effective?
- Any skill that should be modified or created based on gaps observed?

#### 3. Decomposition & Task Structure
- How was the task broken down? Did that structure help or hurt?
- Were there moments where a large request produced scattered output, but a narrower one succeeded?
- Did context length appear to degrade output quality?

#### 4. Corrections Made
- What outputs were wrong, hallucinated, or off-target?
- What follow-up prompt fixed it — and *why* did that fix work?
- Was the error a prompt problem (ambiguity, missing context) or a model limitation?

#### 5. Meta-Observations
- What did you learn about this model's strengths or blind spots?
- Were there interaction styles that felt efficient vs. wasteful?
- Any patterns about when the model "took over" vs. stayed on task?

---

### Phase 2: Learning Extraction

For each raw observation from Phase 1, apply this filter:

**Threshold — Include only if it meets BOTH:**

1. **Reusable** — Will this change how you prompt or structure a future session?
2. **Non-obvious** — Would a first-time Claude user know this? If yes, skip it.

**Examples that PASS:**
- "Asking Claude to challenge assumptions before completing a request surfaces better constraints"
- "Prefixing the skill name in the user message improves skill trigger reliability"
- "When output drifts vague, adding 'be precisely wrong rather than vaguely right' as a constraint refocuses it"
- "Decision-council skill works best when the question is framed as a binary or ranked choice, not open-ended"

**Examples that FAIL (too obvious or too specific):**
- "Claude can write SQL" — not a learning
- "I asked it to fix a typo and it did" — not reusable
- "The output was long" — not actionable

---

### Phase 3: Write the Learning Entry

Produce a dated Markdown block structured as follows:

```markdown
---

## Session: [YYYY-MM-DD] — [2–5 word session theme]

**Context**: [1–2 sentences. What was the session about? What were you trying to accomplish?]

**Skills Used**: [List any skills invoked, or "None"]

### What Worked
- [Reusable prompt/interaction pattern] → [Why it worked / what it produced]
- ...

### What Didn't Work
- [Pattern or approach that failed] → [What went wrong / how it was fixed]
- ...

### Corrections & Why
| Wrong Output | Root Cause | Fix Applied |
|---|---|---|
| [Brief description] | [Ambiguity / missing context / model limit] | [What prompt fixed it] |

### Key Learnings
> Distilled, actionable insights. Each one should be writable on a post-it.

- **[Learning title]**: [One sentence. Specific enough to act on.]
- ...

### Skill & Tooling Notes
- [Any friction, gap, or improvement noted for existing skills]
- [Any new skill that should be built]

---
```

**Rules for the entry:**
- Keep **What Worked** and **What Didn't Work** to 3–5 bullets max. Force prioritization.
- **Key Learnings** must be distillable to one sentence. If you can't, the insight isn't clear yet.
- Don't document the *content* of the session (what was built). Document the *interaction mechanics*.
- Write in second person ("When you ask Claude to...") so future-you can read it prescriptively.

---

### Phase 4: Write Session File

Write the entry as a standalone Markdown file.

**File location**: `session-learning/learning_artifacts/`

**Filename format**: `YYYY-MM-DD_<slug>.md`

- `YYYY-MM-DD` — today's date
- `<slug>` — 2–4 word kebab-case summary of the session theme (e.g., `rca-postmortem-draft`, `pipeline-debug`, `prompt-refiner-usage`)

**Example filenames:**
```
session-learning/learning_artifacts/2026-05-21_rca-postmortem-draft.md
session-learning/learning_artifacts/2026-05-21_pipeline-debug.md
```

**File content**: The full dated entry from Phase 3, with no extra wrapper — the file itself is the entry.

**Do not**:
- Create an index or summary file automatically
- Append to any existing file
- Nest further subdirectories

---

## Output

The skill produces:
1. **One `.md` file** written to `session-learning/learning_artifacts/YYYY-MM-DD_<slug>_<n>.md`.
2. **A compact confirmation** displayed in chat: filename written + Key Learnings bullets only

The chat output is intentionally minimal — the file is the artifact.

---

## Example Entry

```markdown
---

## Session: 2026-05-21 — DE pipeline RCA + postmortem draft

**Context**: Investigated a GCS egress spike traced to public URL access on ML pipeline
artifacts. Drafted a postmortem in Bahasa Indonesia for stakeholder communication.

**Skills Used**: rca-analysis, message-compose

### What Worked
- Framing the problem as "what changed?" rather than "what is wrong?" helped narrow
  the RCA to GCS IAM config in one pass → Claude didn't over-expand the fishbone
- Providing the target audience (Indonesian stakeholders, non-technical) before asking
  for the draft produced tone-appropriate output immediately without revision

### What Didn't Work
- Asking for RCA and postmortem in the same prompt → output was a generic hybrid.
  Splitting into two sequential requests produced cleaner, more distinct outputs.

### Corrections & Why
| Wrong Output | Root Cause | Fix Applied |
|---|---|---|
| RCA mixed in postmortem prose | Ambiguous compound request | Split into two separate prompts |
| Formal Bahasa that felt stiff | No audience context given | Added "non-technical operations team" |

### Key Learnings
- **Compound requests degrade structure**: When two distinct documents are needed,
  always make two requests — even if they're related.
- **Audience context front-loads tone calibration**: Give audience before content,
  not after. Model uses it to set register from line one.
- **"What changed?" beats "what is wrong?" for RCA framing**: Narrows scope,
  avoids speculative fishbone branches.

### Skill & Tooling Notes
- rca-analysis skill doesn't have a bilingual output option — consider adding a
  `language` parameter to the skill header.

---
```

---

## Critical Rules

1. **Mechanics over content** — What you built is in your project notes. This log is about *how you worked with the AI*, not what it produced.
2. **Force prioritization** — If everything is a learning, nothing is. Cap at 5 bullets per section.
3. **Second person, prescriptive** — Write for future-you as the reader.
4. **One file per session, never append** — Each session gets its own file. The directory is the log.
5. **Short entries are better than complete ones** — A 3-bullet entry you'll actually read beats a 20-bullet entry you'll skip.
6. **Flag skill gaps** — If you hit friction that a better skill would fix, log it in "Skill & Tooling Notes". This is how your skills library grows from real usage.

---

## Triggering This Skill

Invoke with:
- "session debrief"
- "summarize ai session"
- "ai learnings"
- "what did I learn about prompting today"
- "update my ai log"
- "debrief this session"
