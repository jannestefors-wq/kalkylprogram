# V1C Correction Report

**Order:** "LUF Editorial Engine V1C. RIKTAD BLOCKERARKORRIGERING EFTER
FINAL AUDIT OCH STRUCTURAL EVIDENCE PACK"
**Branch:** `claude/editorial-variation-v1c` (built on `37e643a`, audited
in `9588505`)
**Scope:** two blockers only -- Structural Arc / Structural Movement, and
False Variation. No V1D, no generator, no Quality Gate, no canonical
change. `editorial-engine/docs/V1C_AUDIT_REPORT.md` is preserved
unchanged as the historical record of what the Final Audit found.

---

## 1. What was broken (recap, not re-litigated)

`docs/V1C_AUDIT_REPORT.md` (unchanged) documents the full finding.
Summary for this report's context:

- **Blocker 1 -- Structural Arc.** `_assess_structural_arc()` took only
  `entry_mode` and `closure_mode` as input, and its lookup table's key
  was `(entry.value, None)` -- the second slot was hard-coded `None`, so
  `closure_mode` never actually participated in the table lookup; its
  only effect was a single override when `closure_mode == open_question`.
  In practice `structural_arc = f(entry_mode)` almost everywhere. Two
  texts sharing the same opening and closing could get the identical arc
  label regardless of what happened between them (false positive), and
  two texts with a genuinely similar internal argument could get
  different labels purely because a single trigger word shifted the
  opening or closing classification (false negative).

- **Blocker 2 -- False Variation.** `assess_false_variation()` was
  architecturally immune to raw wording (it only ever read the six
  OBSERVED dimensions), but each of those six dimensions was itself a
  small fixed-keyword heuristic. A realistic synonym-heavy paraphrase
  that happened to replace one of those keywords (`kom` -> `anlände`,
  `konsekvensen` -> `följden`) could flip `entry_mode`/`closure_mode`'s
  individual verdicts and cause a genuinely repeated construction to
  read as `STRUCTURALLY_DISTINCT`.

## 2. Evidence Pack's role

Work's "V1C Structural Evidence & False Variation Evidence Pack" was
used as **redaktionellt underlag** (editorial evidence), never as code:
it fixed no bug directly, changed no test value by fiat, and was not
copied into `canonical_data/`. Its two directional conclusions --
(a) Structural Arc should reflect a short *sequence* of observed
movements rather than a single entry/closure-derived label, typically
3-5 movements when the material supports it; (b) False Variation must
weigh multiple corroborating signals (thesis, human situation, lens,
narrative distance, movement, closure) rather than individual keyword
triggers -- shaped the design below. Nothing from the Evidence Pack's
own conclusions was altered to fit the implementation; where the
implementation could not yet reach a described pattern with the
small-heuristic toolset available (see Known Residual Limitations,
section 6), that gap is reported here rather than hidden.

## 3. Correction: Structural Arc -> Structural Movement (primary evidence)

### 3.1 New representation (`variation/models.py`)

- `MovementStage` (str, Enum): a small, bounded vocabulary -- `claim`,
  `principle`, `concrete_situation`, `symptom_inventory`, `reframing`,
  `distinction`, `tension`, `question`, `direction`, `consequence`,
  `observation`, `unknown`. Twelve values, all explainable from a
  concrete textual signal -- not an attempt to catalogue every possible
  editorial construction (order section 7).
- `MovementStep` / `StructuralMovementAssessment`: an ordered list of
  observed stages (`steps`), plus `sufficient_evidence: bool`.
- `VariationProfile.structural_movement: StructuralMovementAssessment`
  -- a new field, alongside (not replacing) the existing `structural_arc`
  field, so V1C's existing internal contract (six OBSERVED dimensions,
  `observed_values()`) is unchanged (order section 8's "om befintlig
  structural_arc behöver finnas kvar... får den finnas kvar").
- `DIMENSION_EVIDENCE_STATUS["structural_movement"] = OBSERVED`.
  `OBSERVED_DIMENSIONS` itself is **unchanged** (still the original six)
  -- `structural_movement` is the evidence `structural_arc`'s slot in
  that six-dimension contract is now grounded in, not a seventh
  independent slot (see 3.3).

### 3.2 Observation (`variation/profiler.py`)

`_assess_structural_movement(text)`:

1. Requires >= 3 sentences (order section 10: "en tvåmeningsartefakt kan
   vara komplett som text men ändå för kort för trovärdig structural
   inference"). Below that, `sufficient_evidence=False`, `steps=[]`.
2. Splits the sentences into up to 5 contiguous, roughly equal segments
   (`_segment_sentences()`) -- e.g. 4 sentences -> 4 one-sentence
   segments; 12 sentences -> 5 groups of ~2-3. This guarantees at least
   one segment strictly between the first and last for any text with
   >= 3 sentences (order section 9: "systemet måste försöka observera
   vad texten gör mellan dessa").
3. Classifies each segment independently (`_classify_movement_segment()`)
   using the same small-keyword-signal style as `entry_mode`/
   `closure_mode`/`rhetorical_pressure` already use, but applied to
   EVERY segment, not just the first/last window.
4. Collapses consecutive identical stages (order section 7: no padding
   for its own sake) -- typically leaves 2-4 distinct steps on real
   material of moderate length.

`structural_arc` is then derived FROM the movement sequence
(`_assess_structural_arc(movement)`), not the reverse: it takes the
first and last known step, applies a small first-step -> arc mapping
(reusing the same five legacy labels), with a closing-question override
-- and its `evidence` string names the movement sequence that produced
it, so the secondary label is always traceable to the primary evidence
(order section 8: "en derived label måste kunna förklaras genom de
movements som gav upphov till den").

### 3.3 Comparison (`variation/comparison.py`)

`compare_structural_movements(a, b)` -- the actual fix:

- Compares the two OBSERVED stage sequences with a **longest common
  subsequence** (order-preserving, insertion/deletion-tolerant -- a hook
  inserted at the front, or one extra middle step, does not throw off an
  otherwise-matching sequence). Still a plain, exact, explainable count
  (order section 12: "Ingen falsk exakt similarity score"), not an
  edit-distance library or embedding.
- Categories: `STRONGLY_SIMILAR` (matched/compared ratio >= 0.75),
  `PARTIALLY_SIMILAR` (>= 0.34), `STRUCTURALLY_DISTINCT` (below),
  `INSUFFICIENT_EVIDENCE` (either sequence too short, or compared length
  < 2 -- a single shared, often-generic step is too little evidence for
  a firm claim).
- `compare_variation_profiles()` now derives the **structural_arc
  dimension slot's** same/different verdict from this movement
  comparison (`STRONGLY_SIMILAR` -> same, else -> different) instead of
  naive label equality. The other five OBSERVED dimensions
  (`entry_mode`, `lens`, `narrative_distance`, `rhetorical_pressure`,
  `closure_mode`) are unchanged -- order sections 13-14 explicitly keep
  them as independent, still-keyword-based signals; only what feeds the
  "structural_arc" slot changed.
- `category_for_value_dicts()` gained an optional
  `structural_arc_same_override` parameter so `variation/options.py`'s
  hypothetical (not-yet-built) value dicts can also route through
  movement-based structural comparison, not just real `VariationProfile`
  pairs.

### 3.4 Options (`variation/options.py`)

`_SWAP_PRIORITY` swaps `"structural_arc"` for `"structural_movement"` as
the "biggest shape" candidate dimension -- exactly the order's own
illustrative example ("byt rörelsen från claim -> inventory -> reframing
till scene -> distinction -> unresolved consequence"). A small, fixed,
deterministic list of six prototype movement sequences
(`_PROTOTYPE_MOVEMENT_SEQUENCES`) provides the alternative -- the same
"no hidden preference logic" discipline `_next_value()` already used for
the other five dimensions. `structural_arc` is no longer directly
swappable (it is derived, not an independent variable); when a
different dimension is swapped, `stable_dimensions` now also reports the
unchanged movement sequence explicitly (order section 22's "Behåll...
men byt rörelsen" framing, inverted).

## 4. Correction: False Variation weighs corroborating evidence

`variation/comparison.py::_corroborated_false_variation_verdict()`:

```
if flat_six_dimension_category == TOO_SIMILAR:
    False Variation = True   # already confidently similar
elif flat_category == INSUFFICIENT_EVIDENCE or movement == INSUFFICIENT_EVIDENCE:
    False Variation = False  # refuse to guess on thin evidence
elif movement == STRONGLY_SIMILAR and (lens_same or narrative_distance_same):
    False Variation = True   # corroborated: construction persists despite keyword drift
else:
    False Variation = False
```

This directly implements order section 15's "väga samman relevant
evidens... keywords får inte ensamma bära beslutet": a synonym-heavy
rewrite that breaks `entry_mode`'s or `closure_mode`'s individual
keyword trigger no longer automatically escapes False Variation, as
long as the movement sequence and at least one interpretive-frame signal
(lens or narrative distance) still corroborate that the same
construction persists. Used identically by `assess_false_variation()`
(profile-to-profile) and `options.py::assess_false_variation_from_values()`
(hypothetical option dicts), so an option's risk assessment against
memory (order section 23) benefits from the same corroboration logic
even when the swapped dimension is something other than movement.

## 5. Blocker verification (adversarial, run against real code)

Both blockers were re-tested against the **exact adversarial pairs the
Final Audit used to establish them** (not new, cherry-picked material),
plus a formal pytest suite (`tests/test_v1c_correction.py`, 21 tests):

- `test_structural_arc_blocker_same_entry_and_closure_different_movement_now_distinguished`
  -- reproduces the audit's "generic research vs. specific betrayal
  anecdote" pair (identical `entry_mode=claim`, `closure_mode=action`).
  Before: `TOO_SIMILAR`, same label. After: `PARTIALLY_DISTINCT`,
  `same_count=4/6`, movement sequences differ
  (`['observation','symptom_inventory','observation']` vs.
  `['observation','concrete_situation','observation']`).
- `test_false_variation_blocker_synonym_rewrite_not_automatically_excused`
  -- reproduces the audit's Scenario A synonym rewrite. Before:
  `STRUCTURALLY_DISTINCT`, `is_false_variation=False` (the exact false
  negative the audit reported). After: `is_false_variation=True`, with a
  rationale citing the `STRONGLY_SIMILAR` movement comparison and the
  matching `narrative_distance`.
- D1/D2/D3 (`test_d1_*`, `test_d2_*`, `test_d3_*`): three fresh
  adversarial fixtures modeled on the Evidence Pack's own W06/W11/W03-style
  descriptions (heavy lexical replacement with preserved thesis/
  situation/lens/movement/closure; new claim with preserved
  thesis -> delimitation -> actions -> consequence movement; new hook
  with preserved symptom-inventory -> reframing movement). All three are
  adversarial fixtures only -- none were added to `canonical_data/` or
  Editorial Memory (order section 16).
- Evidence Matrix principles A-E (`test_evidence_matrix_*`): same entry,
  different movement (A); high lexical/conceptual overlap, different
  movement (B); different entry, related movement (C); same rhetorical
  device (a three-part "tretal"), different function, not structural
  identity (D); a too-short FULL text yields `INSUFFICIENT_EVIDENCE` (E).
- Ten further new adversarial scenarios (`test_new_01` through
  `test_new_10`) covering the order's own list: same entry/different
  movement, same closure/different movement, different entry/related
  movement, synonym rewrite, high lexical overlap/different construction,
  low lexical overlap/same construction, same-thesis-new-situation
  (legitimate variation), different-thesis-similar-movement (flaggable),
  a very short FULL text, and same Voice Core traits with genuinely
  different expression.

None of these hardcode a record ID or a specific text to a desired
answer -- every scenario constructs fresh text and runs it through the
unmodified, real `build_variation_profile()` / `compare_variation_profiles()`
/ `assess_false_variation()` / `generate_controlled_variation_options()`
functions.

## 6. Known residual limitations (reported honestly, not corrected further)

This correction is targeted, not exhaustive. Two residual, bounded
limitations remain, consistent with V1C's prototype status:

1. **Movement classification is still keyword-based**, using a modestly
   broader vocabulary than the old entry/closure heuristics (a handful
   of new trigger phrases for reframing/distinction/principle/inventory,
   plus an expanded number-word list for `_QUANTITY_WORDS` and a
   broadened concrete-event-verb check). A sufficiently unusual
   paraphrase that avoids ALL of a segment's trigger words can still
   under-classify to the generic `observation` fallback, collapsing
   distinguishable content into one step. This is the same class of
   limitation the original audit found in `entry_mode`/`closure_mode`,
   now spread across more (but still finite) keyword lists rather than
   eliminated -- a genuine NLP model would remove it, which order
   section 39 forbids for this prototype.
2. **Movement-corroborated False Variation requires `STRONGLY_SIMILAR`
   movement specifically** (not `PARTIALLY_SIMILAR`) plus one matching
   interpretive-frame signal. A pair whose movement sequence is only
   partially preserved after heavy paraphrase (e.g. 2 of 4 steps) will
   not be corroborated into False Variation even if a human editor would
   recognize the same construction. This is a deliberately conservative
   threshold to avoid re-introducing false positives; it means some real
   repetition can still be missed, in the safer direction (under- rather
   than over-flagging).

Both are disclosed here rather than hidden, per the order's own standard
("ingen falsk trygghet").

## 7. Verification summary

| Check | Result |
|---|---|
| Canonical (`schema/`, `canonical_data/`, `fixtures/`) | Unchanged vs. `origin/main` |
| `engine/` (V1A), `memory/` (V1B) | Unchanged |
| Files touched | `variation/{models,profiler,comparison,options,pipeline}.py`, `tests/test_v1c_{comparison,paths}.py` (2 pre-existing assertions updated to a more honest count -- see inline comments), new `tests/test_v1c_correction.py`, three `docs/V1C_*.md` updated to describe the new mechanism, this file |
| `docs/V1C_AUDIT_REPORT.md` | Byte-unchanged |
| Canonical tests | 76/76 |
| V1A tests | 51/51 |
| V1B tests | 47/47 |
| Pre-existing V1C tests | 39/39 |
| New correction tests | 21/21 |
| **Full suite** | **234/234** |
| JSON Schema | Regenerated, byte-identical, reproducible |
| Forbidden functionality scan (generator, Quality Gate, RAG/embeddings, UI/API, LinkedIn/CTA/publish) | None found |
| Voice / Reader Feedback / Angle boundaries | Still zero references in `variation/` |
| Sustained Narrative Form | Still not implemented |
| Golden Path hardcoding | None found |
| Options remain direction-plans (no proposed value >= 60 chars, no prose) | Confirmed |
| Diff scope | Entirely under `editorial-engine/`, entirely under `variation/` + `tests/` + `docs/` |
