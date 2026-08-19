# V1C Variation Profile

`variation/profiler.py` builds a `VariationProfile` from raw text using
small, transparent, deterministic rules -- no embeddings, no external NLP
library, no LLM call required for the test suite (order section 31).

## The six OBSERVED dimensions

| Dimension | Example values (from Work's Variation Foundation) | Signal used |
|---|---|---|
| `entry_mode` | situation, claim, question, process, consequence | First ~4 sentences: `?` -> question; number+concrete-event word -> situation; 2+ imperative verbs -> process; starts with "resultatet"/"konsekvensen" -> consequence; else claim (low confidence) |
| `lens` | responsibility, power, relation, system, consequence, individual_experience | First occurring keyword from a small fixed list (ansvar, makt, konsekvens, relation/tillit, verksamheten/organisationen, "jag ") |
| `narrative_distance` | close_human, direct_address, observer, system_level | 2nd-person words -> direct_address; named role words -> close_human; system words -> system_level; else observer (low confidence) |
| `structural_arc` | scene_to_insight, claim_to_evidence, framework_to_direction, escalation_to_consequence, dilemma_to_open_end | **[V1C Correction]** A SECONDARY summary label, derived from the observed `structural_movement` sequence's first and last known step (never the primary source of structural truth -- see below) |
| `rhetorical_pressure` | contrast, question, consequence, imperative, quiet_observation | `?` -> question; "men" -> contrast; "konsekvens" -> consequence; 2+ imperative verbs -> imperative; else quiet_observation |
| `closure_mode` | action, consequence, open_question, still_statement, unresolved_tension | Last ~2 sentences: `?` -> open_question; imperative verb -> action; "konsekvens" -> consequence; short "Men..." fragment -> unresolved_tension; else still_statement |

Every dimension can legitimately be `unknown` -- there is no fallback
that forces a text into the nearest category when no real signal exists
(order section 12).

## `structural_movement` -- the PRIMARY structural evidence (V1C Correction)

The Final Audit found that `structural_arc` (derived purely from
`entry_mode` + `closure_mode`, in practice mostly `entry_mode` alone --
`closure_mode` only ever mattered via a single open-question override)
produced both false positives (genuinely different texts sharing the
same label) and false negatives (genuinely similar texts landing on
different labels because a trigger word shifted). `structural_movement`
replaces it as the primary signal: the WHOLE text is segmented into up
to 5 contiguous groups of sentences (not just the first-4/last-2-sentence
windows `entry_mode`/`closure_mode` use), and each segment is classified
into one of a small, bounded `MovementStage` vocabulary (claim,
principle, concrete_situation, symptom_inventory, reframing, distinction,
tension, question, direction, consequence, observation, unknown) using
the same explainable keyword-signal discipline as every other dimension.
Consecutive segments with the same stage are collapsed. A text needs at
least 3 sentences to produce a movement sequence at all (order section
10: FULL text-completeness does not imply sufficient structural
evidence) -- shorter texts get `sufficient_evidence=False` and an
`unknown` `structural_arc`.

Two movement sequences are compared with a longest-common-subsequence
match (order-preserving, insertion/deletion-tolerant, still a plain
exact count, not a fabricated similarity score) -- see
`docs/V1C_STRUCTURAL_COMPARISON.md`. `structural_arc`'s value is derived
from the observed sequence's first and last known step, so a claim like
"claim_to_evidence" is now explainable by pointing at the movements that
produced it, never the reverse.

## Confidence and evidence

Every `DimensionAssessment` carries:
- `value` -- the enum value, or `"unknown"`.
- `confidence` -- `engine.models.ConfidenceLevel` (LOW/MEDIUM/HIGH),
  reused, not duplicated. Signals from an explicit strong marker (a `?`,
  a 2nd-person pronoun) are HIGH; derived/default values are LOW.
- `evidence` -- a human-readable sentence naming exactly which words or
  structural pattern produced the value. No black box (order section 14).
- `evidence_status` -- copied from the fixed `DIMENSION_EVIDENCE_STATUS`
  table, never set per-analysis.

## disclosure_pace and emotional_temperature

Implemented, but deliberately weaker (order section 28): `confidence` is
structurally always `LOW`, and they play no role anywhere in
`variation/comparison.py` or `variation/options.py` -- see
`docs/V1C_VARIATION_BOUNDARY.md`.

## Sanity-checked against real material

Run against all 12 real full-text Editorial Memory records, the profiler
produces meaningfully different profiles -- e.g. `content-work-006`
("Observation fore tolkning... Tre personer kom sent till motet...")
profiles as `situation` / `close_human` / `scene_to_insight`, while
`content-work-007` ("Sa flyttar vi verksamheten. Se. Forsta. Prioritera...")
profiles as `process` / `system_level` / `framework_to_direction`. Not
identical, not random -- explainable per field.
