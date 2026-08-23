# Skill Observation Log

Observations captured during task-oriented work. Each entry identifies a
potential skill improvement or new skill opportunity.

**Status key:** OPEN = not yet actioned | ACTIONED = skill updated/created |
DECLINED = user decided not to pursue

---

## 2026-05-16

### Observation 1: Role library too narrow — domain-specific roles emerge naturally in practice

**Status:** OPEN
**Date:** 2026-05-16
**Session context:** Analyzing 4 Decision Council outputs in PARA/3. Resources/Researches — AI memory management, memory structure comparison, post-marriage housing, and AI-assisted reading retention.
**Skill:** decision-council
**Type:** open-source
**Phase/Area:** Council Design / roles.md

**Issue:** Across 3 of 4 outputs analyzed, the agent used custom roles not present in `roles.md`. The reading comprehension decision used "Learning Scientist (Cognitive Psychologist)" and "Productivity Strategist (PKM Practitioner — BASB Lens)". The housing decision used "Perencana Keuangan", "Konsultan Properti", "Analis Risiko Karir", and "Pemerhati Dinamika Keluarga" — none of which exist in the standard library. The `council_framework.md` says "To select roles, read `resources/roles.md`" as though it is the exhaustive source, with no explicit statement that custom roles are permitted. In practice, the outputs that diverged from the library produced the most contextually grounded perspectives — especially for the housing decision, where a generic "Risk Manager" would have been far less useful than an "Analis Risiko Karir" who specifically reasoned about career relocation risk.

**Suggested improvement:** Update `council_framework.md` to explicitly state that the role library is a starting point, not an exhaustive constraint. Add: "If no library role adequately covers a key perspective on the specific decision domain, create a custom role. Name it for its domain expertise, not its archetype." Update `roles.md` to frame itself as a library of common defaults rather than a closed set.

**Principle:** A role library that implicitly discourages domain-specific roles produces generalist perspectives that miss the most high-value, decision-specific insights. The council's quality correlates with role specificity, not role conformity.

---

### Observation 2: No guidance for iterative / follow-up decisions

**Status:** OPEN
**Date:** 2026-05-16
**Session context:** Same analysis session. The second file, "Memory Structure Comparison MemPalace vs Ontology", is explicitly labeled "Iterasi 2" and scoped as a follow-up to the first memory management decision.
**Skill:** decision-council
**Type:** open-source
**Phase/Area:** Required Inputs / council_framework.md

**Issue:** The skill has no pattern for decisions that are second-pass iterations of a prior council. The memory structure comparison explicitly sets its constraint set based on the first decision's recommendation ("Tidak ada vector DB"), but the skill provides no guidance on: how to reference a prior council output as context, how to scope a follow-up question, or how to prevent the follow-up from re-litigating already-settled points. The second document handled this by restating only the constraints that changed, but this was done organically without skill guidance — a less experienced user might re-run a full unconstrained council or lose the continuity.

**Suggested improvement:** Add an "Iterative Decisions" section to `council_framework.md`. Key points to include: (1) If the user references a prior council output, read it and extract the settled recommendation as a fixed constraint before council begins. (2) Scope the new decision question around what remains open, not what was already resolved. (3) Open Section 1 with a "Context from prior decision" callout so readers have continuity. (4) The council roles can be a subset if not all perspectives are needed for the follow-up scope.

**Principle:** Complex decisions rarely resolve in a single council session. A skill that treats every council as a standalone instance loses the compounding value of decision chains, where each iteration inherits certainty from the last and focuses friction on what remains genuinely uncertain.

---

### Observation 3: Hybrid/synthesis recommendations underserved by the output template

**Status:** OPEN
**Date:** 2026-05-16
**Session context:** Same analysis session. The Memory Structure Comparison's synthesized recommendation was "Adopsi MemPalace Spatial Structure sebagai file naming convention, implementasikan retrieval via Python scripts tanpa package MemPalace" — a creative hybrid not listed as any of the original options.
**Skill:** decision-council
**Type:** open-source
**Phase/Area:** Output Structure / output_template.md — Section 4

**Issue:** Section 4 of the output template says "Recommended path: [the winning option]" — language that implies selecting from the options originally listed. In the memory structure comparison, the most valuable recommendation was a synthesis that transcended the two options: adopt MemPalace's spatial taxonomy (Hall structure) as a naming convention within an Ontology-style JSONL storage. This emerged from the Operator perspective's "Hybrid" suggestion and was elevated to the final recommendation. The template framing pushed the agent toward "pick one" but the output correctly broke out of it anyway. A less confident agent execution might have artificially selected an option to comply with the template.

**Suggested improvement:** Update Section 4 of `output_template.md` to explicitly acknowledge hybrid recommendations: change "Recommended path: [the winning option]" to "Recommended path: [the winning option, or a hybrid/synthesis if the council revealed a combination superior to any single option]". Add a brief note: "The best recommendation sometimes synthesizes elements across options rather than selecting one. This is a valid and often superior outcome."

**Principle:** A template that frames the output as "choose from the listed options" suppresses the most creative and often most correct class of recommendation — the synthesis that emerges from the tension between options. Explicit authorization in the template produces better outputs than leaving it to agent judgment under template pressure.

---

### Observation 4: 6-section template too strict for comparison-heavy decisions

**Status:** OPEN
**Date:** 2026-05-16
**Session context:** Same analysis session. The AI Memory Management decision appended a "Section 7: Tool Comparison Matrix" — a structured table comparing 3 tools across 10+ criteria — beyond the 6-section template.
**Skill:** decision-council
**Type:** open-source
**Phase/Area:** Output Structure / output_template.md

**Issue:** The `output_template.md` says "Use this structure exactly. Do not skip sections." The AI memory management output added a Section 7 Tool Comparison Matrix anyway. The matrix (comparing MemPalace, Mem0, and ClawhHub Ontology across token efficiency, installation requirements, offline capability, licensing, etc.) was arguably the clearest single artifact in the entire document — it let the reader scan across all criteria at once rather than extracting them from narrative prose. The strict "exactly" instruction creates tension: agents either deviate silently (as happened here) or comply and produce an output that's less useful for quantitative multi-option decisions. Neither outcome is ideal.

**Suggested improvement:** Add an explicitly authorized optional section to the template: "### 7. Comparison Matrix (optional) — Use when evaluating 3 or more options with quantitative or categorical attributes that benefit from side-by-side comparison. If used, list all options as columns and evaluation criteria as rows." Keep the core 6 sections required and this one optional with a clear trigger condition.

**Principle:** Template rigidity that prohibits naturally emerging structural improvements creates silent non-compliance. A template that explicitly authorizes the most common valid extensions produces consistently better outputs than one that forces agents to either deviate or suppress useful structure.

---

### Observation 5: "When to use" scope implicitly excludes personal/life decisions

**Status:** OPEN
**Date:** 2026-05-16
**Session context:** Same analysis session. The housing decision ("Keputusan Tempat Tinggal Pasca Nikah") is a personal life decision — post-marriage housing, mortgage vs. land purchase, financial tradeoffs — not a business decision.
**Skill:** decision-council
**Type:** open-source
**Phase/Area:** SKILL.md — When to use

**Issue:** The skill's "When to use" section lists: "strategic, financial, operational, reputational, or people-related consequences." This language reads as business/professional framing. The housing decision is a personal financial and relational decision. It produced one of the highest-quality council outputs in the set — especially the Analyst Risiko Karir perspective, which surfaced the double-cost scenario (mortgage + Jakarta rental) that a generalist financial analysis would likely have missed. Nothing in the skill prohibits personal decisions, but the framing doesn't invite them either. A user reading the skill description might not think to invoke it for a life decision.

**Suggested improvement:** Add "personal or life decisions with significant long-term consequences (financial, relational, geographic, career)" to the "When to use" examples. Optionally add a brief note: "The council format is domain-agnostic — it works for business, technical, and personal decisions equally. The key criterion is consequence, not context."

**Principle:** The decision council's value — structured multi-perspective friction before commitment — applies equally to personal and professional decisions. A "When to use" framing that implies business context undersells the skill's applicability and leaves high-value use cases uncaptured.
