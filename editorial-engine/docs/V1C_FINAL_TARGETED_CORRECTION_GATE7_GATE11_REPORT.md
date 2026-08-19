# LUF Editorial Engine V1C. Final Targeted Correction: Gate 7 and Gate 11

**Status:** Targeted correction report. No PR created. Scoped strictly to the two locked policy
corrections in `V1C_FINAL_SCOPE_AND_DECISION_ASSESSMENT.md` (materialized, SHA-256 verified,
commit `bbe867b`).

## 1. Gate 7 (DECISION-POLICY DEFECT): corrected

`variation/comparison.py::_false_variation_verdict()`'s Local Editorial Function tier was rewritten to
match the assessment's ten-condition policy exactly. Previously it required an ADDITIONAL, independently-
agreeing construction dimension (`n_same_construction_dims >= 1`) on top of LEF corroboration -- the
assessment found this "för restriktiv": it ignored the evidentiary weight of a DIRECTLY_OBSERVABLE,
source-traced functional relation. The new tier (`gate7_local_function_strong_corroboration`) fires when:

- `lef_corroborates` -- both profiles independently found a sufficient (source-traced situation ->
  consequence) relation whose capability-change words share an internal category (unchanged mechanism from
  the prior correction, itself unmodified this turn).
- `lef_no_material_difference` -- **new**: none of `entry_mode`, `narrative_distance`, `lens`, or
  `closure_mode` confidently (bilaterally, non-default) differ. `lens` is included here specifically
  because the assessment's condition 7 names it as a difference signal to guard against, even though (per
  Correction 2's unmodified "Thesis similarity != Structural repetition" principle) it still never counts
  as MATCH evidence -- it can only veto, never corroborate.

No additional positive agreement is required beyond LEF corroboration itself -- exactly what the assessment
asked for.

## 2. Gate 7 verification

- **NC01-15 (hard precision gate): 0 false positives**, unchanged.
- **G01-20: 0 false positives**, and **G01 (FALSE_VARIATION_HIGH_RISK) is now correctly detected**
  (previously a miss).
- **SC01-50 Challenge Pack: 0 false positives**, unchanged. **SC07 is now correctly detected**
  (previously a miss). SC01-10 improved from 0/10 to 1/10; total from 34/50 to 35/50.
- Full test suite: 314/314 (all pre-existing tests, including all Human Situation Boundary regression
  tests from the prior correction, still pass).

### Disclosed residual risk (order section 4's explicit precision requirement)

Four of this session's own adversarial tests (not part of NC01-15, G01-20, or SC01-50 -- Work's own
verified batteries, all clean) now correctly fire under the loosened policy where they previously did not:
same-consequence-words/different-situation, same-local-function/genuinely-new-treatment,
different-situation/similar-vocabulary, and an ambiguous-motive case. Each was re-examined and found to be
exactly the kind of residual risk `V1C_FINAL_SCOPE_AND_DECISION_ASSESSMENT.md` section 4 itself predicts and
accepts ("Risk med en källspårad, explicit och osäkerhetsbevarande avgränsning: MEDEL, fortfarande inte
låg" -- medium, not zero). They are pinned as permanent, clearly-labeled regression tests documenting this
accepted risk (`test_v1c_local_editorial_function.py`, `*_is_disclosed_residual_risk` tests) rather than
silently patched away or hidden. No further rule-trimming was attempted to chase them, per order section 5's
explicit "Ingen vidare regeltrimning."

The ambiguous-motive case is flagged as the strongest argument for a future, separate
`AMBIGUOUS_HUMAN_DECISION` outcome distinct from a confident lock -- noted, not built here (order's explicit
"Ingen ytterligare funktionell expansion").

## 3. Gate 11 (IMPLEMENTATION DEFECT): attempted, NOT resolved -- STOPP condition met

The assessment explicitly rejects the prior report's non-separability claim and proposes a specific
alternative principle (section 6): a pair is `INSUFFICIENT_EVIDENCE` when at least one text lacks a
"belagd jämförbar relation" (a confirmed comparable relation), while a genuine `LEGITIMATE_VARIATION` case
shows a "belagd materiell skillnad" (a confirmed material difference) somewhere. This was implemented
literally and tested, not assumed:

```
profile_has_any_evidence(p) = any confident construction-dimension signal
                               OR structural_movement.sufficient_evidence
                               OR local_editorial_function.sufficient_evidence
any_confident_diff(a, b)    = any of entry_mode/narrative_distance/lens/closure_mode
                               confidently (bilaterally, non-default) differs
```

Computed directly against the real profiles (not estimated) for every relevant SC01-50 pair:

| SC | Ground Truth | A has evidence | B has evidence | Confident diff exists |
|---|---|---|---|---|
| SC48 | INSUFFICIENT_EVIDENCE | True | **False** | False |
| SC49 | INSUFFICIENT_EVIDENCE | False | False | False |
| SC50 | INSUFFICIENT_EVIDENCE | False | False | False |
| SC40 | LEGITIMATE_VARIATION | **False** | **True** | False |
| SC16 | LEGITIMATE_VARIATION | False | False | False |
| SC32-35, SC14-15 | LEGITIMATE_VARIATION | False | False | False |

**SC48 and SC40 have the IDENTICAL evidence-presence shape** (exactly one side carries any confidently-
detected signal, the other carries none, no confident difference anywhere) **and opposite required
outcomes.** SC49/50 and SC16/32-35/14-15 have the identical symmetric-zero-evidence shape with the same
opposite-outcome problem. This is the assessment's own proposed principle, operationalized exactly as
written, tested against real data -- and it does not separate the two classes.

This is the third independent confirmation of the same underlying fact, using three genuinely different
methodologies across two correction rounds:

1. Sentence-count-based gating (prior correction): SC48's combined word count (24) exceeds SC16's (22) and
   SC40's (21) -- non-separable by any length measure.
2. Word-count-based gating (prior correction, narrower): still collides on SC49 vs. SC16/40 at the `<= 6`
   boundary.
3. Evidence-presence-based gating (this correction, the assessment's own proposed principle): collides
   identically on SC48 vs. SC40 and SC49/50 vs. SC16/32-35/14-15.

No further variant of "does either/both side(s) lack X" was invented to chase this pattern -- doing so
without a principled basis would be exactly the "specialfallsoptimering" both the assessment (section 9)
and this order (section 3) forbid, and order section 5 provides an explicit, applicable off-ramp for exactly
this outcome: **"Om ... resultatet kräver semantisk förståelse: STOPP."**

What distinguishes SC48 ("Hon stod fast. Det räckte.") from SC40's short side, or SC49 from SC16/32-35, is
not structurally, lexically, or evidentially observable with the current OBSERVED-dimension set
(`entry_mode`, `narrative_distance`, `rhetorical_pressure`, `closure_mode`, `lens`, `structural_movement`,
`local_editorial_function`). It requires recognizing that "Hon stod fast" thematically echoes "sa nej till
en genväg" as both being about resistance (the assessment's own SC48 rationale explicitly makes this
semantic connection: "B delar möjligt motiv") -- a judgment about meaning, not structure. **No code change
was made for Gate 11.** SC48 and SC49 remain at their pre-correction state (`LEGITIMATE_VARIATION` via the
unchanged default fall-through), honestly disclosed as unresolved rather than forced.

## 4. Hard scope boundaries verified

- Structural Movement: `git diff` against its functions is empty -- untouched.
- No keyword taxonomy, synonym table, or metaphor lexicon added (`grep` for `nycklar|nav|trådar|fotfäste`
  across `variation/`: zero matches, unchanged from the prior report).
- No embeddings, RAG, or LLM semantic classifier anywhere in the diff.
- SC41-44 not attempted; regression confirms unchanged at 0/4.
- Challenge Pack, Challenge Manifest, Ground Truth, Evidence Pack, Feasibility Assessment, Final Scope and
  Decision Assessment: all verified byte-unchanged (`git diff` empty against commit `bbe867b`).
- Canonical Foundation, V1A, V1B, `schema/`: `git diff` empty.

## 5. Regression

- Full suite: **314/314 PASS** (no new tests added this correction; 4 existing tests' expected outcomes
  updated and relabeled to reflect the intentionally-broadened, disclosed-risk Gate 7 policy).
- JSON Schema regenerated: 17 files, no diff.
- SC01-50: **35/50** (up from 34/50). SC01-10: 1/10 (SC07). SC41-44: 0/4 (unchanged). SC48-50: 1/3 (SC50
  only, unchanged). **0 false positives.**
- Voice Boundary, Angle Boundary, Reader Feedback Boundary, Memory Boundary, Human Authority: all PASS,
  unaffected (no new callers of any Voice/Angle/Reader-Feedback/Memory model anywhere in the diff).

## 6. Files changed

`variation/comparison.py` (Gate 7 tier rewrite, new `lef_no_material_difference` computation and parameter),
`variation/options.py` (sentinel parameter update, value-dict path unaffected as before),
`tests/test_v1c_local_editorial_function.py` (4 tests relabeled/updated to disclosed-residual-risk,
consistent with actual verified policy behavior), this report.

## 7. Verdict

**Gate 7: corrected, verified, materially improves detection (G01, SC07) with zero new false positives
across every officially verified battery (NC01-15, G01-20, SC01-50).**

**Gate 11: attempted with the assessment's own proposed principle, rigorously proven non-separable a third
time. Requires semantic understanding beyond transparent V1C scope. Order section 5's explicit STOPP
condition is met.**

Per the order's own rule that both corrections must succeed for a "REDO" verdict, and per order section 5's
explicit instruction that a result requiring semantic understanding triggers STOPP: **overall result is
STOPP**, notwithstanding Gate 7's genuine, verified success.
