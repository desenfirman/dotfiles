---
name: course-material-generator
description: >
  Use this skill whenever the user wants to generate course material content from a structured outline.
  Triggers when the user provides a course syllabus or outline containing [course material: ...] placeholder tags,
  or when the user says things like "generate my course content", "fill in this course outline", "write course material",
  or "expand this syllabus". Also trigger if the user pastes a block of text that contains section headings and
  [course material] placeholders. Also trigger when the user adds a NEW section heading + placeholder in a
  follow-up message mid-conversation — this is incremental input mode and should be handled seamlessly.
  The skill processes each section one at a time, replacing each placeholder with contextually appropriate
  written content informed by the full course context established earlier in the conversation.
---
 
# Course Material Generator
 
This skill generates written course content from a structured outline. The user provides:
1. **A course context block** — a plain-text description of the course (title, audience, goals, tone, scope)
2. **An outline** — section headings with `[course material: <length hint>]` placeholders, either **all at once** or **incrementally** across multiple messages
Claude processes the outline **section by section**, replacing each placeholder with real content before moving to the next.
 
---
 
## Two Input Modes
 
### Mode A — Full outline upfront
User pastes the course context + all sections in one message. Claude parses everything, announces the section count, then generates one section at a time with approval checkpoints.
 
### Mode B — Incremental input
User sets the course context first, then feeds sections one by one across separate messages. Claude recognizes each new `[course material: ...]` block as the next section to generate and processes it immediately.
 
Claude should **auto-detect** which mode is being used:
- If the first message contains 2+ `[course material]` placeholders → **Mode A**
- If the user sends context first, then a single section in a follow-up → **Mode B**
- If unclear, default to **Mode B** and generate whatever section just arrived
---
 
## Workflow
 
### Step 1 — Extract the Course Context
 
At the top of the user's message (or in a prior message), look for a block describing the course. This may be labeled as:
- `[course context: ...]`
- `Course Overview:`, `Syllabus:`, `About this course:`
- Or simply a paragraph before the outline begins
Extract and hold onto:
- **Course title**
- **Target audience** (who is this for?)
- **Learning goals** (what will learners be able to do?)
- **Tone/style** (formal, conversational, practical, academic?)
- **Domain/field** (data engineering, leadership, design, etc.)
If no context block is found, ask the user to provide one before proceeding. A good context block is 100–400 words.
 
**In incremental mode (Mode B):** The context is set once at the start of the conversation. In every subsequent message, Claude reuses it automatically — never ask for the context again unless the user explicitly says they want to change it.
 
---
 
### Step 2 — Parse the Input
 
#### Mode A (full outline)
Scan the full outline for all `[course material: ...]` placeholders. Each placeholder belongs to the **nearest preceding section heading**.
 
Build a mental list:
```
Section 1: Introduction          → [course material: less than 1000 char]
Section 2: Core Concepts         → [course material: less than 500 char]
...
```
 
Count them. Tell the user: *"I found N sections to fill. I'll generate them one at a time — starting with Section 1."*
 
#### Mode B (incremental)
Each follow-up message contains one section heading + one placeholder. Treat it as the next section in sequence. Claude maintains a running count of sections generated so far in the conversation (Section 1, Section 2, etc.) and continues the sequence naturally.
 
When a new section arrives in Mode B, Claude acknowledges it briefly:
> *"Got it — here's Section [N]:"*
 
No need to re-announce the course context or recap previous sections.
 
---
 
### Step 3 — Generate Section by Section
 
For **each section**, in order:
 
1. **Output the section heading** as-is
2. **Generate the content** — replace the placeholder with written prose
3. **Pause** and ask:
   > "Here's Section [X]. Does this look good, or would you like me to adjust anything before I continue?"
In **Mode B**, the pause is implicit — the user controls pacing by sending the next section when ready. Claude should not prompt "send me the next section"; just wait.
 
#### Content Generation Rules
 
- Write in **flowing prose**, not bullet points, unless the section is explicitly instructional (e.g., "Step-by-step guide to...")
- Maintain **consistency** with the course context throughout — same audience, tone, vocabulary level
- Honor the **character hint** in the tag as a soft guideline:
  - `less than 500 char` → keep it tight, 2–4 sentences
  - `less than 1000 char` → a solid paragraph, ~100–150 words
  - `less than 2000 char` → 2–3 paragraphs, more depth
  - No hint → use judgment based on section importance
- **Do not exceed** the hint by more than ~30% unless the user explicitly asks for more
- Each section should feel like it **belongs** to the same course — reference earlier concepts where natural
- Avoid generic AI filler phrases like "In this section, we will explore..." — get straight to substance
---
 
### Step 4 — Completion
 
#### Mode A
After the final section is approved, output a clean summary:
 
```
✅ All [N] sections generated.
 
Would you like me to:
1. Compile the full document in one clean block?
2. Adjust any sections?
3. Export to a file?
```
 
#### Mode B
Claude does not know when the user is "done" — the user decides. After generating any section, Claude can optionally note:
> *"Ready for the next section whenever you are."*
 
If the user says "that's all" or "compile everything", Claude assembles all sections generated in the conversation into one clean document block.
 
---
 
## Internal Prompt Template
 
When generating content for a section, use this internal reasoning structure (do not show it to the user):
 
```
COURSE CONTEXT:
[Insert extracted course context here]
 
SECTION: [Section heading]
HINT: [Character limit from tag]
PRECEDING SECTIONS GENERATED: [list titles only, for continuity]
 
TASK: Write course material for this section. It should:
- Match the tone and audience from the course context
- Be approximately [hint] in length (soft guideline, ±30%)
- Flow naturally from the preceding sections
- Be written in prose unless instructional content demands otherwise
- Avoid generic filler; be specific and substantive
```
 
---
 
## Example
 
**User input:**
 
```
Course Context:
Title: Decision-Making with AI for Data Professionals
Audience: Mid-level data engineers and analysts
Goal: Help practitioners use AI tools to make better, faster decisions at work
Tone: Practical, conversational, slightly opinionated
 
Section 1: Introduction
[course material: less than 1000 char]
 
Section 2: Why AI Changes the Decision-Making Game
[course material: less than 1000 char]
```
 
**Claude's response for Section 1:**
 
> **Section 1: Introduction**
>
> Data professionals have always been in the business of turning information into decisions — but the tools available to support that work have changed dramatically. AI assistants can now draft analyses, surface patterns, flag anomalies, and generate recommendations at a speed no human analyst could match alone. The question is no longer whether AI belongs in your workflow; it's whether you're using it deliberately enough to trust the output.
>
> This course is built for practitioners who already understand data — engineers who write pipelines, analysts who build dashboards — and want a structured way to think about where AI fits into their decision-making process. We'll cover the foundations, the failure modes, and the practical habits that separate good AI-assisted decisions from fast but flawed ones.
>
> ---
> Here's Section 1. Does this look good, or would you like any adjustments before I move to Section 2?
 
---
 
## Edge Cases
 
| Situation | How to Handle |
|---|---|
| No course context provided | Ask for it before generating anything |
| Placeholder with no length hint | Use ~800 characters as default |
| User says "just do all of them" | Generate all sections but still pause between each for a quick "✓ or adjust?" |
| Section heading is vague (e.g., "Part 3") | Infer intent from course context and surrounding sections |
| User edits a section mid-flow | Incorporate the change into your context before continuing |
| User sends context only (no placeholder yet) | Acknowledge the context is set, tell them to send sections when ready |
| User switches from Mode B to full outline mid-conversation | Detect the multiple placeholders and shift to Mode A from that point |
| User asks "compile everything" in Mode B | Gather all sections generated in the conversation and output as one clean block |
| User sends a new section without a heading | Use the placeholder hint and surrounding context to infer a logical heading |
| User wants to redo a previous section | Regenerate it, then confirm before resuming the sequence |
 
