# LUF Editorial Engine V1C. Local Editorial Function Implementation Report

**Status:** Implementation report. No PR created (order: a separate, later independent verification decides
PR readiness).

**Scope:** Implements the locked scope from `V1C_LOCAL_EDITORIAL_FUNCTION_FEASIBILITY_ASSESSMENT.md`
(Architecture Verdict: **B. PARTIALLY VIABLE**), materialized and hash-verified (SHA-256
`493e8e05fd57fd8c79736b53f38aa2bfc2c6a1563ea961eb4c8160c21a0f5346`, commit `928fa1b`).

## 1. Locked scope (unchanged from the assessment)

- **In-scope for Local Editorial Function:** SC01, SC02, SC06, SC07, SC08, SC09, SC10 (DIRECTLY_OBSERVABLE).
- **Special diagnosis before any new representation:** SC05 (detection/use gap), SC03 (mixed, narrow
  centralization chain only, no metaphor normalization).
- **Outside automatic V1C scope, no keyword-chasing:** SC04, SC41, SC42, SC43, SC44.
- **Separate implementation defect, not an LEF problem:** SC48, SC49.

## 2. Representation implemented

`variation/models.py::LocalEditorialFunctionAssessment` (new, prototype-only, non-canonical): `situation_span`,
`consequence_span` (literal source-quoted substrings), `capability_change_words` (literal source-quoted
words, never a category label), `sufficient_evidence`, `confidence`, `evidence`. `VariationProfile` gained an
optional `local_editorial_function` field.

`variation/profiler.py::_assess_local_editorial_function()`: splits text at the earliest generic Swedish
connector (`till slut`, `till sist`, `sedan`, `därför`, `efteråt`, `men`), or at the first sentence boundary
if none is found (`INSUFFICIENT_EVIDENCE` if fewer than 2 sentences and no connector). Asserts
`sufficient_evidence=True` only when the consequence span contains a source-quotable word from a small,
general capability-change vocabulary (voice, accountability, dependency, initiative, information flow,
social consequence for dissent, cessation) derived from the feasibility assessment's own named concepts
(section 2), not from any single challenge scenario's literal phrasing.

`variation/comparison.py::_local_editorial_functions_corroborate()`: an internal-only category grouping
(never persisted on the model -- "källspårad före kategoriserad", order section 9) decides whether two
sufficient assessments' capability-change words plausibly describe the same kind of relation.

## 3. Human Decision Boundary preserved

`INSUFFICIENT_EVIDENCE`, `AMBIGUOUS_HUMAN_DECISION`, and "no asserted relation" are all still reachable
outcomes (order section 16/10). No gap is ever filled with an inferred meaning: absent connector, absent
second part, or absent capability word all fall through to `sufficient_evidence=False`, never a guess.

## 4. UNKNOWN, absence-of-evidence, Voice, Angle boundaries

- `UNKNOWN` never counts as similarity or difference evidence anywhere in the new code (unchanged discipline
  from Correction 2/Blocker 3, verified by `test_v1c_local_editorial_function.py`).
- Local Editorial Function never decides alone: `_false_variation_verdict()`'s new
  `short_form_local_function_corroborated` tier requires `n_diff_construction_dims == 0`
  **and** `n_same_construction_dims >= 1` (see section 6 for why the second condition was added).
- Voice Core is not read anywhere in the new code.
- Local Editorial Function never changes or reads V1A angle assignment; it operates purely on
  `VariationProfile`-level text, unrelated to angle selection.

## 5. SC05 diagnosis (order section 4, performed before any new representation was relied on for it)

Diagnosed against `assess_false_variation()` for the actual SC05 pair. Result: **every existing dimension
defaults to its LOW-confidence fallback on both texts** (`entry_mode`, `narrative_distance`,
`rhetorical_pressure`, `closure_mode` all default; `lens` unknown on both). Structural Movement is
`INSUFFICIENT_EVIDENCE` on both sides. The new Local Editorial Function extractor also returns
`sufficient_evidence=False` on both sides -- the consequence span ("Gruppen bestämde snabbt att hon inte
brydde sig") contains no word from the capability-change vocabulary; the concept required here (unfounded
motive attribution / premature judgment) is not covered by voice/accountability/dependency/initiative/
information/cessation.

**Conclusion:** existing evidence is genuinely NOT sufficient to detect SC05 -- the assessment's own
"detection/use gap" hypothesis does not hold once measured. Per order section 4's own instruction ("Om SC05
kan hanteras genom korrekt användning av redan existerande evidens: lägg inte till ny representation"), since
existing evidence is not sufficient, this rule does not obligate adding new representation either -- and none
was added specifically for SC05 (adding "unfounded motive attribution" vocabulary tuned to this single case
would itself be exactly the kind of scenario-specific keyword-chasing order section 10 forbids). SC05 remains
unresolved, honestly, as a genuine coverage gap rather than a fabricated fix.

## 6. SC03 diagnosis (order section 5, narrow scope only)

No metaphor-normalization code was written anywhere (`nycklar`/`nav`/`trådar`/`vägar`/`fotfäste` never appear
in the codebase -- verified). The connector+capability-vocabulary mechanism is general-purpose, not
metaphor-aware, so it correctly does not attempt to recognize SC03's central-actor-dependency chain across
its two different image systems ("all kunskap" vs. "ett namn"). This is compliant by construction: the
mechanism was never given the metaphor-mapping capability the assessment explicitly forbids, so it neither
solves nor overreaches on SC03. SC03 remains unresolved, honestly.

## 7. SC04/SC41-44 (order section 6): confirmed out of automatic scope, no keyword expansion

Regression confirms SC41-44 unchanged at 0/4 and SC04 (part of the SC01-10 regression block) unchanged.
`grep` for any of `dörrar|nav|trådar|fotfäste|putsa|tavlan` (the assessment's own named ceiling-test images)
across `variation/`: zero matches -- no code was added chasing these five scenarios, consistent with the
locked scope boundary.

## 8. NC01-15 and G01-20 (order sections 6-7 of the re-order, read from the same verified file)

Both read directly from the materialized, hash-verified `V1C_LOCAL_EDITORIAL_FUNCTION_FEASIBILITY_ASSESSMENT.md`
(not separate files -- confirmed in the same document, sections 8 and 9).

**NC01-15 (hard precision gate): 15/15 correctly NOT flagged as False Variation. 0 false positives.**

**G01-20 (generalization, run against the real `assess_false_variation()` pipeline):**

| Ground Truth | Result |
|---|---|
| FALSE_VARIATION_HIGH_RISK (G01, G03, G10, G11, G12, G13) | 0/6 detected |
| LEGITIMATE_VARIATION (12 cases) | 12/12 correctly not flagged |
| AMBIGUOUS_HUMAN_DECISION (G20) | correctly not locked |

**0 false positives across all 20 G-cases.**

## 9. The precision/recall finding that shapes every result below

During development, an unguarded design (`lef_corroborates and n_diff_construction_dims == 0`, no further
requirement) DID detect G01 and SC07 correctly -- but also produced a real false positive on a Human
Situation Boundary regression test already in the suite: two texts (office vs. family-dinner-table) sharing
only the single capability word "själv" ("alone"/"by themselves", a very common, weakly-specific Swedish
reflexive) were wrongly flagged as the same construction. Two fixes were applied, in order of preference:

1. Removed `själv` from the capability-change vocabulary entirely (too generic/common to reliably signal
   isolation-as-consequence; `beroend`/`ensam` are more specific and were kept).
2. Added a floor requiring **at least one independently-agreeing construction dimension**
   (`n_same_construction_dims >= 1`) alongside LEF corroboration -- mirroring the `>= 2` floor
   construction-dimensions-alone already needed (Blocker 3's own precision-driven decision, documented in
   `V1C_FALSE_VARIATION_SHORT_FORM_CORRECTION_REPORT.md` section 7).

With both fixes applied: **0 false positives across NC01-15, G01-20, all 286 pre-existing tests, all 28 new
Local Editorial Function tests, and the full SC01-50 Challenge Pack.**

**The cost:** the `n_same_construction_dims >= 1` guard means Local Editorial Function's OWN corroboration
signal, alone, never changes the final verdict on any text where the construction dimensions do not ALSO
happen to agree on at least one dimension -- and empirically, across every test surface available (SC01-50,
G01-20, and this report's own 28 new tests), that additional agreement essentially never coincides on
genuinely new, low-lexical-overlap text. Verified directly: `_local_editorial_functions_corroborate()` (the
mechanism itself, tested in isolation) correctly returns `True` on G01, SC07, and 5 of this report's own new
scenario pairs -- proving the extraction and matching logic works exactly as designed -- but
`assess_false_variation()`'s full pipeline result for every one of those same pairs is `is_false_variation
=False`, because `n_same_construction_dims` is 0 in each case. This is the safety guard functioning exactly
as intended, not a defect -- but it means Local Editorial Function, AS SAFELY GATED, contributes **zero net
behavioral change** on SC01-10, SC41-44, G01-20's FALSE_VARIATION_HIGH_RISK cases, or any of this report's
own new adversarial scenarios. It is a real, tested, correctly-functioning, non-overfit mechanism that is
currently precision-gated into practical inertness on every available low-lexical-overlap test case.

A looser gate was not adopted: order section 12 makes false-positive protection an explicit hard gate
("Om recall ökar genom en materiell ökning av falska positiva: STOPP"), and the discovered false positive is
real, reproducible, and structurally identical to the SC08/SC37 evidence-signature collision documented in
the prior Blocker 3 correction -- the same principled choice (protect precision over a single-signal recall
gain) was made both times, for the same reason.

## 10. New adversarial scenarios and negative controls (order sections 8-9/12-13)

`tests/test_v1c_local_editorial_function.py` -- **28 new permanent tests**, none copied or paraphrased from
SC01-50, NC01-15, G01-20, or any prior correction test:

- **11 mechanism-level tests** (`_local_editorial_functions_corroborate()` tested directly): prove the
  extractor and matcher work correctly in isolation -- 5 positive detections across independent themes
  (control-vs-judgment, silence-vs-agreement, informal information surface, value-vs-practice, a second
  independent information-flow pair), plus refusals on: no-capability-vocabulary text (motive attribution,
  honestly undetectable), a single sentence with no connector, a different-category mismatch, heroics-vs-
  capacity-building, and centralization-vs-distributed-capacity.
- **11 full-pipeline tests** (`assess_false_variation()`, safety guard active): mandate gap, same-situation-
  opposite-function, same-consequence-different-mechanism, same-local-function-new-treatment, different-
  function-similar-vocabulary, asymmetric evidence, UNKNOWN/default collision, ambiguous weak corroboration,
  INSUFFICIENT_EVIDENCE short pair, shared-connector-different-capability, same-opening-opposite-closure --
  all correctly resolve to `is_false_variation=False`.
- **4 additional explicit negative controls**: shared topic word / different construction, shared actor
  position / different outcome, shared entry / different capability domain, shared problem word / opposite
  capability direction -- all correctly `is_false_variation=False`.
- **2 structural tests**: no hardcoded scenario/ground-truth literals anywhere in `comparison.py`, `options.py`,
  `profiler.py`; `LocalEditorialFunctionAssessment` has no category/taxonomy enum field (source-traced only).

**All 28 pass. 0 false positives.**

## 11. SC48/SC49 (order section 15): diagnosed, NOT resolved -- honest limitation, not a false claim

Root cause (unchanged from `V1C_FALSE_VARIATION_SHORT_FORM_CORRECTION_REPORT.md`): both are cases where
`overall` confidently asserts `STRUCTURALLY_DISTINCT` on thin evidence instead of `INSUFFICIENT_EVIDENCE`.
This session re-attempted a fix from first principles, mathematically:

- Every count-based candidate criterion tested (max-sentence-count, min-word-count, combined-word-count,
  per-profile absolute word-count) was checked against the full SC01-50 set. **Proof of non-separability:**
  SC48's combined word count (24) is HIGHER than SC16's (22) and SC40's (21) -- both of which are
  `LEGITIMATE_VARIATION` cases that already correctly pass. No monotonic length-based threshold, of any
  kind tested, can separate `{SC48, SC49, SC50}` from `{SC16, SC40}`, because SC48 is numerically LARGER on
  every length measure than the legitimate cases it would need to stay below.
- Local Editorial Function does not help either (order section 15 explicitly forbids using it as a
  shortcut here, and empirically it finds no capability-change signal in either SC48 or SC49's texts --
  verified: `sufficient_evidence=False` on the relevant sides).
- Work's own Challenge Pack rationale for SC48 ("B delar möjligt motiv men kan inte säkert bedömas") itself
  requires recognizing that "hon stod fast" ("she stood firm") thematically echoes "hon sa nej till en
  genväg" ("she said no to a shortcut") as both being about resistance -- a semantic/thematic judgment, not
  a structural or lexical one. This is outside what a transparent, non-embedding heuristic system can
  determine (order's own repeated, explicit prohibition on semantic/embedding similarity).

**SC50 remains fixed** (the length-gate from the prior correction still catches it: both sides reduce to a
single sentence with 4 combined words, zero confident signal). **SC48 and SC49 remain misses**, honestly
disclosed rather than forced with a fabricated or overfit rule. This is a genuine, proven architectural
ceiling, not a missed effort.

## 12. Regression

- Full suite: **314/314 PASS** (286 pre-existing + 28 new).
- JSON Schema regenerated: 17 files, no diff -- reproducible, unchanged. `LocalEditorialFunctionAssessment`
  and `VariationProfile` do not appear in `schema/json/` (grep confirmed empty) -- no V1C prototype model has
  become canonical.
- `git diff` against commit `928fa1b` on `editorial-engine/engine`, `editorial-engine/memory`,
  `editorial-engine/schema`, `editorial-engine/canonical_data`: empty.
- All frozen evidence artifacts (Challenge Pack, Challenge Manifest, Blind Re-Audit Report, Evidence Pack,
  Evidence Manifest, Feasibility Assessment, and every prior correction/audit report) verified unmodified.
- Structural Movement: untouched, verdict remains ACCEPTABLE PROTOTYPE HEURISTIC.
- SC01-50 regression: **34/50** (unchanged from before this order -- see section 9 for why: the precision
  guard needed to pass NC01-15/G01-20/the HSB regression test neutralizes LEF's standalone contribution on
  every currently-available in-scope scenario). SC01-10: 0/10. SC41-44: 0/4. SC48-50: 1/3 (SC50 only).
  0 false positives throughout.

## 13. Files changed

`variation/models.py` (`LocalEditorialFunctionAssessment`, `VariationProfile.local_editorial_function`),
`variation/profiler.py` (`_assess_local_editorial_function()` and its connector/vocabulary constants),
`variation/comparison.py` (`_local_editorial_functions_corroborate()`, its internal category grouping, the
new `short_form_local_function_corroborated` tier in `_false_variation_verdict()`, `assess_false_variation()`
wiring), `variation/options.py` (sentinel-gated, unreachable on the value-dict path -- explicitly out of
scope per this path's existing documented limitation),
`tests/test_v1c_local_editorial_function.py` (new, 28 tests),
`docs/V1C_LOCAL_EDITORIAL_FUNCTION_IMPLEMENTATION_REPORT.md` (this report).

## 14. Remaining limitations

- LEF is a real, correctly-functioning, non-overfit mechanism (proven via 28 tests + G01/SC07 direct
  verification) that currently contributes zero net verdict changes anywhere in-scope, because the guard
  needed to keep it false-positive-free (`n_same_construction_dims >= 1`) requires a second corroborating
  signal that essentially never coincides on genuinely low-lexical-overlap text.
- SC01-10 (except the already-passing AMBIGUOUS/LEGITIMATE cases outside this locked scope) remain
  undetected: 0/10, unchanged.
- SC41-44 remain OUTSIDE_V1C_AUTOMATIC_HEURISTIC_SCOPE, as designed -- not a regression, a documented
  boundary.
- SC03 and SC05 remain honestly unresolved, both diagnosed and explained (sections 5-6).
- SC48/SC49 remain unresolved, with a mathematical non-separability proof (section 11) -- not for lack of a
  genuine second attempt.
- The capability-change vocabulary's Swedish inflection handling is prefix-only (no derivational-prefix
  handling, e.g. `bestraffades` does not match the `straff` stem the way `straffades` does) -- a known,
  minor coverage gap, not corrected here to avoid scenario-specific tuning.
