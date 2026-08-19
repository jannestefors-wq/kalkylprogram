# LUF Editorial Engine V1C. False Variation Blind Independent Re-Audit Report

**Status:** Audit report. Read-only findings against frozen Work Challenge Pack + Manifest, run against
implementation commit `203405b` (V1C False Variation Blocker 2 Correction) with zero code changes after
materialization.

**Scope:** False Variation mechanism only, as challenged by `V1C_FALSE_VARIATION_REAUDIT_CHALLENGE_PACK.md`
(SC01-SC50). Structural Movement, Canonical Foundation, V1A, and V1B are verified unchanged, not re-derived.

## 1. Materialization gate

| Artifact | Expected SHA-256 | Computed SHA-256 | Match |
|---|---|---|---|
| `V1C_FALSE_VARIATION_REAUDIT_CHALLENGE_PACK.md` | `8c1dace9e8e8723a774c880fd50797154651fb5e8370083e1927360ebcbc9f7b` | `8c1dace9e8e8723a774c880fd50797154651fb5e8370083e1927360ebcbc9f7b` | YES |
| `V1C_FALSE_VARIATION_REAUDIT_CHALLENGE_MANIFEST.md` | `51805ac64de188ca973238a1b209f92cde6e5ff2a367272b5ca98a7b669c3d45` | `51805ac64de188ca973238a1b209f92cde6e5ff2a367272b5ca98a7b669c3d45` | YES |

Both files materialized via byte-exact `cp` from the uploaded Work exports (not retyped). `diff` against the
source uploads is empty for both. Materialization committed separately (`57c7558`) before any audit logic ran.

## 2. Checkpoint

- Branch: `claude/editorial-variation-v1c`
- HEAD at audit start: `203405b3d12ddaa1e6ed25ab828be37664fcddee` ("V1C False Variation Blocker 2 Correction: D1-D3 now 3/3")
- Worktree clean, branch in sync with `origin/claude/editorial-variation-v1c`
- No PR existed before this audit
- Baseline suite: **249/249 PASS**

## 3. Frozen semantic mapping (registered before executing any scenario)

The implementation's actual output is `assess_false_variation(a, b).is_false_variation: bool` plus
`compare_variation_profiles(a, b).overall: VariationDistanceCategory` (four values). It has no native
"ambiguous" output. The following mapping to Work's four Ground Truth classes was fixed **before** SC01 was
run and was not altered afterward:

```
map_output(is_false_variation, overall):
  is_false_variation == True                                  -> FALSE_VARIATION_HIGH_RISK
  is_false_variation == False AND overall == INSUFFICIENT_EVIDENCE -> INSUFFICIENT_EVIDENCE
  is_false_variation == False AND overall != INSUFFICIENT_EVIDENCE -> LEGITIMATE_VARIATION
```

Scoring:
- GT `FALSE_VARIATION_HIGH_RISK`: PASS iff system class matches. Else FAIL (false negative).
- GT `LEGITIMATE_VARIATION`: PASS iff system class matches. `FALSE_VARIATION_HIGH_RISK` -> FAIL (false positive). `INSUFFICIENT_EVIDENCE` -> FAIL (under-confident miss).
- GT `INSUFFICIENT_EVIDENCE`: PASS iff system class matches. `FALSE_VARIATION_HIGH_RISK` -> FAIL (dangerous overclaim). `LEGITIMATE_VARIATION` -> FAIL (miss, non-dangerous).
- GT `AMBIGUOUS_HUMAN_DECISION` (facit key: "evidens åt båda håll. Systemet bör flagga, inte låsa beslutet."):
  PASS iff system class != `FALSE_VARIATION_HIGH_RISK` (i.e. the system did not lock a False Variation
  verdict — either `LEGITIMATE_VARIATION` or `INSUFFICIENT_EVIDENCE` leaves the human free to decide, which
  is what the facit key itself defines as correct). FAIL only if the system locks `FALSE_VARIATION_HIGH_RISK`.

The system's structural inability to emit a genuine third/fourth-value "ambiguous" or "flagged" state is
itself reported as a finding (section 7), not concealed by this mapping.

## 4. SC01-SC50 results (all 50 executed, zero code changes after SC01)

| ID | Difficulty | Ground Truth | System Class | Verdict | overall | movement | same_count |
|---|---|---|---|---|---|---|---|
| SC01 | ADVERSARIAL | FALSE_VARIATION_HIGH_RISK | LEGITIMATE_VARIATION | FAIL | STRUCTURALLY_DISTINCT | INSUFFICIENT_EVIDENCE (0) | 0/6 |
| SC02 | ADVERSARIAL | FALSE_VARIATION_HIGH_RISK | LEGITIMATE_VARIATION | FAIL | STRUCTURALLY_DISTINCT | INSUFFICIENT_EVIDENCE (0) | 0/6 |
| SC03 | ADVERSARIAL | FALSE_VARIATION_HIGH_RISK | LEGITIMATE_VARIATION | FAIL | STRUCTURALLY_DISTINCT | INSUFFICIENT_EVIDENCE (0) | 0/6 |
| SC04 | ADVERSARIAL | FALSE_VARIATION_HIGH_RISK | LEGITIMATE_VARIATION | FAIL | STRUCTURALLY_DISTINCT | INSUFFICIENT_EVIDENCE (0) | 0/6 |
| SC05 | ADVERSARIAL | FALSE_VARIATION_HIGH_RISK | LEGITIMATE_VARIATION | FAIL | STRUCTURALLY_DISTINCT | INSUFFICIENT_EVIDENCE (0) | 0/6 |
| SC06 | ADVERSARIAL | FALSE_VARIATION_HIGH_RISK | LEGITIMATE_VARIATION | FAIL | STRUCTURALLY_DISTINCT | INSUFFICIENT_EVIDENCE (0) | 0/6 |
| SC07 | ADVERSARIAL | FALSE_VARIATION_HIGH_RISK | LEGITIMATE_VARIATION | FAIL | STRUCTURALLY_DISTINCT | INSUFFICIENT_EVIDENCE (0) | 0/6 |
| SC08 | ADVERSARIAL | FALSE_VARIATION_HIGH_RISK | LEGITIMATE_VARIATION | FAIL | STRUCTURALLY_DISTINCT | INSUFFICIENT_EVIDENCE (0) | 1/6 |
| SC09 | ADVERSARIAL | FALSE_VARIATION_HIGH_RISK | LEGITIMATE_VARIATION | FAIL | STRUCTURALLY_DISTINCT | INSUFFICIENT_EVIDENCE (0) | 0/6 |
| SC10 | ADVERSARIAL | FALSE_VARIATION_HIGH_RISK | LEGITIMATE_VARIATION | FAIL | STRUCTURALLY_DISTINCT | INSUFFICIENT_EVIDENCE (0) | 0/6 |
| SC11 | ADVERSARIAL | LEGITIMATE_VARIATION | LEGITIMATE_VARIATION | PASS | STRUCTURALLY_DISTINCT | INSUFFICIENT_EVIDENCE (0) | 0/6 |
| SC12 | ADVERSARIAL | LEGITIMATE_VARIATION | LEGITIMATE_VARIATION | PASS | STRUCTURALLY_DISTINCT | INSUFFICIENT_EVIDENCE (0) | 0/6 |
| SC13 | ADVERSARIAL | LEGITIMATE_VARIATION | LEGITIMATE_VARIATION | PASS | STRUCTURALLY_DISTINCT | INSUFFICIENT_EVIDENCE (0) | 1/6 |
| SC14 | ADVERSARIAL | LEGITIMATE_VARIATION | LEGITIMATE_VARIATION | PASS | STRUCTURALLY_DISTINCT | INSUFFICIENT_EVIDENCE (0) | 0/6 |
| SC15 | ADVERSARIAL | LEGITIMATE_VARIATION | LEGITIMATE_VARIATION | PASS | STRUCTURALLY_DISTINCT | INSUFFICIENT_EVIDENCE (0) | 0/6 |
| SC16 | ADVERSARIAL | LEGITIMATE_VARIATION | LEGITIMATE_VARIATION | PASS | STRUCTURALLY_DISTINCT | INSUFFICIENT_EVIDENCE (0) | 0/6 |
| SC17 | ADVERSARIAL | LEGITIMATE_VARIATION | LEGITIMATE_VARIATION | PASS | STRUCTURALLY_DISTINCT | INSUFFICIENT_EVIDENCE (0) | 0/6 |
| SC18 | ADVERSARIAL | LEGITIMATE_VARIATION | LEGITIMATE_VARIATION | PASS | STRUCTURALLY_DISTINCT | INSUFFICIENT_EVIDENCE (0) | 0/6 |
| SC19 | INTERMEDIATE | LEGITIMATE_VARIATION | LEGITIMATE_VARIATION | PASS | STRUCTURALLY_DISTINCT | INSUFFICIENT_EVIDENCE (0) | 1/6 |
| SC20 | ADVERSARIAL | LEGITIMATE_VARIATION | LEGITIMATE_VARIATION | PASS | STRUCTURALLY_DISTINCT | INSUFFICIENT_EVIDENCE (0) | 0/6 |
| SC21 | ADVERSARIAL | AMBIGUOUS_HUMAN_DECISION | LEGITIMATE_VARIATION | PASS | STRUCTURALLY_DISTINCT | INSUFFICIENT_EVIDENCE (0) | 0/6 |
| SC22 | ADVERSARIAL | LEGITIMATE_VARIATION | LEGITIMATE_VARIATION | PASS | STRUCTURALLY_DISTINCT | INSUFFICIENT_EVIDENCE (0) | 0/6 |
| SC23 | ADVERSARIAL | LEGITIMATE_VARIATION | LEGITIMATE_VARIATION | PASS | STRUCTURALLY_DISTINCT | INSUFFICIENT_EVIDENCE (0) | 0/6 |
| SC24 | ADVERSARIAL | AMBIGUOUS_HUMAN_DECISION | LEGITIMATE_VARIATION | PASS | STRUCTURALLY_DISTINCT | INSUFFICIENT_EVIDENCE (0) | 0/6 |
| SC25 | ADVERSARIAL | LEGITIMATE_VARIATION | LEGITIMATE_VARIATION | PASS | STRUCTURALLY_DISTINCT | INSUFFICIENT_EVIDENCE (0) | 0/6 |
| SC26 | ADVERSARIAL | AMBIGUOUS_HUMAN_DECISION | LEGITIMATE_VARIATION | PASS | STRUCTURALLY_DISTINCT | INSUFFICIENT_EVIDENCE (0) | 0/6 |
| SC27 | ADVERSARIAL | LEGITIMATE_VARIATION | LEGITIMATE_VARIATION | PASS | STRUCTURALLY_DISTINCT | INSUFFICIENT_EVIDENCE (0) | 0/6 |
| SC28 | ADVERSARIAL | LEGITIMATE_VARIATION | LEGITIMATE_VARIATION | PASS | STRUCTURALLY_DISTINCT | INSUFFICIENT_EVIDENCE (0) | 0/6 |
| SC29 | ADVERSARIAL | AMBIGUOUS_HUMAN_DECISION | LEGITIMATE_VARIATION | PASS | STRUCTURALLY_DISTINCT | INSUFFICIENT_EVIDENCE (0) | 0/6 |
| SC30 | ADVERSARIAL | AMBIGUOUS_HUMAN_DECISION | LEGITIMATE_VARIATION | PASS | STRUCTURALLY_DISTINCT | INSUFFICIENT_EVIDENCE (0) | 0/6 |
| SC31 | INTERMEDIATE | LEGITIMATE_VARIATION | LEGITIMATE_VARIATION | PASS | STRUCTURALLY_DISTINCT | INSUFFICIENT_EVIDENCE (0) | 0/6 |
| SC32 | INTERMEDIATE | LEGITIMATE_VARIATION | LEGITIMATE_VARIATION | PASS | STRUCTURALLY_DISTINCT | INSUFFICIENT_EVIDENCE (0) | 0/6 |
| SC33 | INTERMEDIATE | LEGITIMATE_VARIATION | LEGITIMATE_VARIATION | PASS | STRUCTURALLY_DISTINCT | INSUFFICIENT_EVIDENCE (0) | 0/6 |
| SC34 | ADVERSARIAL | LEGITIMATE_VARIATION | LEGITIMATE_VARIATION | PASS | STRUCTURALLY_DISTINCT | INSUFFICIENT_EVIDENCE (0) | 0/6 |
| SC35 | INTERMEDIATE | LEGITIMATE_VARIATION | LEGITIMATE_VARIATION | PASS | STRUCTURALLY_DISTINCT | INSUFFICIENT_EVIDENCE (0) | 0/6 |
| SC36 | ADVERSARIAL | LEGITIMATE_VARIATION | LEGITIMATE_VARIATION | PASS | STRUCTURALLY_DISTINCT | INSUFFICIENT_EVIDENCE (0) | 0/6 |
| SC37 | ADVERSARIAL | LEGITIMATE_VARIATION | LEGITIMATE_VARIATION | PASS | STRUCTURALLY_DISTINCT | INSUFFICIENT_EVIDENCE (0) | 1/6 |
| SC38 | ADVERSARIAL | LEGITIMATE_VARIATION | LEGITIMATE_VARIATION | PASS | STRUCTURALLY_DISTINCT | INSUFFICIENT_EVIDENCE (0) | 0/6 |
| SC39 | ADVERSARIAL | LEGITIMATE_VARIATION | LEGITIMATE_VARIATION | PASS | STRUCTURALLY_DISTINCT | INSUFFICIENT_EVIDENCE (0) | 1/6 |
| SC40 | ADVERSARIAL | LEGITIMATE_VARIATION | LEGITIMATE_VARIATION | PASS | STRUCTURALLY_DISTINCT | INSUFFICIENT_EVIDENCE (0) | 0/6 |
| SC41 | ADVERSARIAL | FALSE_VARIATION_HIGH_RISK | LEGITIMATE_VARIATION | FAIL | STRUCTURALLY_DISTINCT | INSUFFICIENT_EVIDENCE (0) | 0/6 |
| SC42 | ADVERSARIAL | FALSE_VARIATION_HIGH_RISK | LEGITIMATE_VARIATION | FAIL | STRUCTURALLY_DISTINCT | INSUFFICIENT_EVIDENCE (0) | 0/6 |
| SC43 | ADVERSARIAL | FALSE_VARIATION_HIGH_RISK | LEGITIMATE_VARIATION | FAIL | STRUCTURALLY_DISTINCT | INSUFFICIENT_EVIDENCE (0) | 0/6 |
| SC44 | ADVERSARIAL | FALSE_VARIATION_HIGH_RISK | LEGITIMATE_VARIATION | FAIL | STRUCTURALLY_DISTINCT | INSUFFICIENT_EVIDENCE (0) | 0/6 |
| SC45 | ADVERSARIAL | LEGITIMATE_VARIATION | LEGITIMATE_VARIATION | PASS | STRUCTURALLY_DISTINCT | INSUFFICIENT_EVIDENCE (0) | 0/6 |
| SC46 | ADVERSARIAL | LEGITIMATE_VARIATION | LEGITIMATE_VARIATION | PASS | STRUCTURALLY_DISTINCT | INSUFFICIENT_EVIDENCE (0) | 0/6 |
| SC47 | ADVERSARIAL | AMBIGUOUS_HUMAN_DECISION | LEGITIMATE_VARIATION | PASS | STRUCTURALLY_DISTINCT | INSUFFICIENT_EVIDENCE (0) | 0/6 |
| SC48 | ADVERSARIAL | INSUFFICIENT_EVIDENCE | LEGITIMATE_VARIATION | FAIL | STRUCTURALLY_DISTINCT | INSUFFICIENT_EVIDENCE (0) | 0/6 |
| SC49 | ADVERSARIAL | INSUFFICIENT_EVIDENCE | LEGITIMATE_VARIATION | FAIL | STRUCTURALLY_DISTINCT | INSUFFICIENT_EVIDENCE (0) | 0/6 |
| SC50 | ADVERSARIAL | INSUFFICIENT_EVIDENCE | LEGITIMATE_VARIATION | FAIL | STRUCTURALLY_DISTINCT | INSUFFICIENT_EVIDENCE (0) | 0/6 |

**Totals: 33/50 PASS, 17/50 FAIL.**

## 5. Confusion matrix (by Ground Truth class)

| Ground Truth | PASS | FAIL | Note |
|---|---|---|---|
| FALSE_VARIATION_HIGH_RISK (14 cases: SC01-10, SC41-44) | 0 | 14 | **0% recall.** Every single case misclassified as LEGITIMATE_VARIATION. |
| LEGITIMATE_VARIATION (27 cases) | 27 | 0 | 100%. |
| AMBIGUOUS_HUMAN_DECISION (6 cases: SC21,24,26,29,30,47) | 6 | 0 | 100% under this audit's mapping (system never locked a False Variation verdict on these). |
| INSUFFICIENT_EVIDENCE (3 cases: SC48-50) | 0 | 3 | **0% recall.** All misclassified as LEGITIMATE_VARIATION (system overclaimed STRUCTURALLY_DISTINCT on single-sentence pairs instead of flagging insufficient evidence). |

**False positives (system said FALSE_VARIATION_HIGH_RISK when it should not have): 0.**
**False negatives (system missed a genuine FALSE_VARIATION_HIGH_RISK case): 14.**
**Dangerous overclaims on INSUFFICIENT_EVIDENCE ground truth: 0 (misses were the non-dangerous kind — LEGITIMATE_VARIATION, not a false lock).**

## 6. Category breakdown (order section 6 categories)

| Category | Scenarios | PASS |
|---|---|---|
| Same construction / low lexical | SC01-10 | 0/10 |
| High lexical / different construction (incl. HL4/HSB1) | SC11-20 | 10/10 |
| Near-threshold | SC21-30 | 10/10 |
| Human Situation Boundary | SC31-40 | 10/10 |
| OOV/paraphrase, movement-order, asymmetric sequence, short FULL/default | SC41-50 | 3/10 |
| HL4/HSB1-specific (SC11-18) | 8/8 | 8/8 |
| AMBIGUOUS_HUMAN_DECISION | SC21,24,26,29,30,47 | 6/6 |
| ADVERSARIAL-only (45 of 50) | — | 28/45 |

## 7. Root cause of the systematic failure

Every one of the 50 scenarios produced `movement_category = INSUFFICIENT_EVIDENCE` with `matched_positions
= 0`. The Structural Movement mechanism never contributed evidence to a single scenario in this challenge
set. This is not a fluke of a few short cases — it is the entire battery.

Cause: `_segment_sentences()` (`variation/profiler.py`) requires **at least 3 sentences** to produce a
movement sequence at all. The Challenge Pack's 50 pairs — like most real short-form editorial content — are
predominantly 1-2 sentence vignettes. With movement always `INSUFFICIENT_EVIDENCE`, every movement-dependent
tier in `_false_variation_verdict()` (`movement_strongly_corroborated`, `movement_partially_corroborated`,
`movement_uncontradicted`, `weakly_corroborated`) is structurally unreachable. Only two tiers remain live:
`flat_too_similar` (same_count ≥ 5) and `construction_majority` (≥4 of 5 non-lens construction dims
genuinely match). For the 14 FALSE_VARIATION_HIGH_RISK cases, `same_count` was 0 or 1 on all but one
(SC08=1) — the two texts in each pair deliberately share editorial construction while using different
concrete imagery, which also changes the surface-level heuristic reads of `entry_mode`, `narrative_distance`,
`rhetorical_pressure`, and `closure_mode` (all of which are themselves keyword/pattern-driven, per order
section 7 limitation 2). With movement inactive and construction dims not coinciding either, no tier fires
and the verdict falls through to `distinct` — LEGITIMATE_VARIATION.

This is the same mechanism, working exactly as designed and exactly as documented in
`V1C_FALSE_VARIATION_CORRECTION_2_REPORT.md` — the correction's D1-D3 and 40-scenario battery both happened
to contain ≥3-sentence texts, so movement corroboration was available there. This blind, independently
authored Challenge Pack uses shorter, arguably more realistic vignettes and exposes that **False Variation's
positive-evidence path depends almost entirely on Structural Movement corroboration, which has no fallback
when movement cannot be computed at all.**

**SC48-50 (INSUFFICIENT_EVIDENCE ground truth) fail for a related but distinct reason:** `overall` came back
`STRUCTURALLY_DISTINCT`, not `INSUFFICIENT_EVIDENCE`, even for one-sentence pairs like "Ingen svarade." vs.
"Ingen lyssnade." — `MIN_KNOWN_DIMENSIONS_FOR_COMPARISON` was still satisfied by default-fallback dimension
values, so the flat comparison did not recognize the pair as too thin to judge, even though the correct
editorial reading is "not enough text to say anything."

## 8. Section 7 known-limitations re-examination

1. **HL4/HSB1 pattern:** did NOT reproduce in this blind set — 8/8 HL4 cases (SC11-18) and 10/10 HSB cases
   (SC31-40) passed. This documented limitation remains non-blocking under blind testing.
2. **Movement classification is heuristic/keyword-driven:** confirmed **blocking**, not non-blocking. See
   section 7 above — this is the root cause of the 0/14 recall failure on the exact category (same
   construction, different concrete wording) that False Variation exists to catch.
3. **`lens` exclusion from corroboration:** not implicated in any of the 17 failures (all 17 have `same_count`
   0-1, well below any threshold where lens inclusion/exclusion would change the outcome). Remains
   non-blocking.

## 9. Hardcoding check

`grep` for `SC0[1-9]|SC[1-4][0-9]|SC50|blind.?challenge|challenge.?pack` (case-insensitive) across
`variation/`, `engine/`, `schema/`, `memory/`: **zero matches.** No production code changed during or after
the audit (`git diff 203405b -- editorial-engine/variation editorial-engine/engine editorial-engine/schema
editorial-engine/memory` is empty).

## 10. Regression after audit

- Full suite: **249/249 PASS** (unchanged from baseline — no production code touched)
- JSON Schema regenerated (`python3 -m schema.export_json_schema`): 17 files written, `git status` shows no
  diff — reproducible and unchanged
- Canonical Foundation, V1A, V1B: untouched (no files under their scope modified)
- Structural Movement: mechanism behaved exactly as documented in `V1C_REAUDIT_REPORT.md` (correctly reports
  `INSUFFICIENT_EVIDENCE` rather than guessing, on <3-sentence input) — no new blocking behavior of the
  movement classifier itself was discovered. The blocking finding is architectural: False Variation's
  evidence-combination has no path when movement is unavailable, not a defect in movement classification
  itself. **Structural Movement verdict remains ACCEPTABLE PROTOTYPE HEURISTIC.**

## 11. Verdicts

- **Structural Movement: ACCEPTABLE PROTOTYPE HEURISTIC** (unchanged, reconfirmed).
- **False Variation: PROTOTYPE LIMITATION REQUIRES CORRECTION.**
  - 0/14 recall on FALSE_VARIATION_HIGH_RISK, the category the mechanism exists to catch.
  - 0/3 on INSUFFICIENT_EVIDENCE (system overclaims certainty on very short text).
  - Root cause is systematic and architectural (no fallback evidence path when Structural Movement cannot
    be computed — true for any input under 3 sentences), not a scattering of unrelated edge cases.
  - Zero false positives — the mechanism is safe (never over-triggers) but has failed on the majority of the
    category it is meant to detect.

## 12. PR gate

**FAILS.** False Variation verdict is not `ACCEPTABLE PROTOTYPE HEURISTIC`; systematic blocking errors
remain in a redaktionellt central category (same construction / low lexical, and its OOV variant).
No PR created.
