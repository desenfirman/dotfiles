---
wing: <skill-slug>
updated: YYYY-MM-DD
---

<!-- AGENT RECALL  : grep_search "KEYS:" + domain terms → read the enclosing drawer block (next ~20 lines). -->
<!-- AGENT WRITE   : append drawer to the matching room section; mark superseded drawers `valid: false`. -->
<!-- COMPACTION    : if total file > 150 lines, consolidate valid:false drawers into a single anti-patterns room. -->

---

## room: <topic-slug>

### drawer: <kebab-slug>
valid: true | scope: user|session|repo | timestamp: YYYY-MM-DD
KEYS: kw1, kw2, kw3, kw4, kw5

<verbatim rule or pattern — max 100 words, preserve exact names/values, include minimal code if essential>

retrieval_value: <one sentence: why this drawer matters in a future session>

---

## room: anti-patterns

<!-- Consolidate superseded drawers here during compaction. Keep for at least 30 days before deletion. -->

### drawer: <failed-approach-slug>
valid: false | scope: repo | timestamp: YYYY-MM-DD
KEYS: kw1, kw2, kw3

<what was tried and why it fails — preserve exact error messages if known>

superseded_by: <drawer-slug of the correct pattern>

---
