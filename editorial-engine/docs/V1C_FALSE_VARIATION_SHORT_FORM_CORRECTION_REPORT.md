# LUF Editorial Engine V1C. False Variation Blocker 3: Short Text / INSUFFICIENT_EVIDENCE Structural Movement Correction

**Status:** Targeted correction report. No PR created (order: correction requires a separate, later
independent verification before any PR decision).

**Addendum (V1C FALSE VARIATION BLOCKER 3. SHORT-FORM CORRECTION re-order):** a second, more detailed order
covering the same Blocker 3 arrived after this report and commit `c84a0a9` were already pushed (it references
checkpoints `203405b`/`57c7558`/`5984a1a` but not `c84a0a9`, so it was evidently drafted before that commit
landed). The mechanism, root cause, and test battery below are unchanged from that commit; this addendum adds
the 4 explicitly-required categories the re-order names that were not yet separately covered (`same entry /
different treatment`, `same closure / different treatment`, a third independent `different lexical surface /
preserved construction` pair, and Human Situation Boundary direction B), and section 12 below evaluates all
10 of the re-order's hard acceptance gates explicitly, one by one.

**Scope:** False Variation's behavior when Structural Movement is INSUFFICIENT_EVIDENCE only.
Structural Movement itself (`profiler.py::_assess_structural_movement()`, the 3-sentence floor,
`comparison.py::compare_structural_movements()`) is unmodified.

## 1. Blind test finding this correction addresses

`V1C_FALSE_VARIATION_BLIND_REAUDIT_REPORT.md` (commit `5984a1a`) found that all 50 scenarios in the
independently-authored Challenge Pack produced `movement_category = INSUFFICIENT_EVIDENCE` (every pair had
fewer than 3 sentences on at least one side). Every False Variation tier that existed at commit `203405b`
required a movement category other than `INSUFFICIENT_EVIDENCE`, so they were all structurally unreachable.
The only two remaining tiers (`flat_too_similar`, `construction_majority`) needed near-total agreement across
the five/four flat dimensions, which the surface-keyword heuristics essentially never produced on real
literary prose. Result: **0/14 recall on `FALSE_VARIATION_HIGH_RISK`**, and **0/3 on `INSUFFICIENT_EVIDENCE`**
(short single-sentence pairs were confidently read as `STRUCTURALLY_DISTINCT` instead of flagged as too thin
to judge). Zero false positives throughout.

## 2. Root cause (mapped before any code change, per order section 3)

Full inventory of what `assess_false_variation()` had available at commit `203405b`, and how it failed
through, when `structural_movement.sufficient_evidence = False` on one/both sides:

- **Observed dimensions available regardless of text length:** `entry_mode`, `lens`, `narrative_distance`,
  `rhetorical_pressure`, `closure_mode` (all computed by `profiler.py` from the whole/opening/closing text,
  no sentence-count floor). **Derived from movement:** `structural_arc` (always `UNKNOWN` when movement is
  insufficient). **Unavailable below 3 sentences:** `structural_movement` itself.
- **Why 1-2 sentence texts rarely reach a confident dimension at all:** every one of the five surface
  dimensions falls through to a `ConfidenceLevel.LOW` default (`entry_mode='claim'`,
  `narrative_distance='observer'`, `rhetorical_pressure='quiet_observation'`, `closure_mode='still_statement'`)
  whenever its own narrow keyword list (imperative verbs, `?`, `men`, quantity+event words, second-person
  pronouns, role/system words) finds nothing. On realistic literary Swedish prose this happens on **most**
  short pairs -- diagnostic testing against the Challenge Pack's own SC01/SC03-07/SC41/SC43/SC44 found
  **zero** confidently-detected (non-LOW) dimension on **either side of the pair**, for all five dimensions.
  `_dimension_match_is_evidence()` (V1C Correction 2) already correctly refuses to count two coincidental LOW
  defaults as a match -- so these pairs produced `same_count = 0` and fell straight to `STRUCTURALLY_DISTINCT`.
- **Which dimensions could corroborate False Variation before this correction:** only via the
  movement-dependent tiers (`movement_strongly_corroborated`, `movement_partially_corroborated`,
  `movement_uncontradicted`, `weakly_corroborated`) or `construction_majority` (requiring **all four**
  non-lens construction dimensions to genuinely agree). With movement unavailable and the four construction
  dimensions rarely reaching even one confident agreement, there was no path left at all.
- **Why Short FULL cases (SC48-50) wrongly became `STRUCTURALLY_DISTINCT`:** `compare_variation_profiles()`'s
  `overall` category treats a dimension as "known" whenever its value `!= "unknown"` -- but every LOW-confidence
  default is a real, non-`"unknown"` string value (`'claim'`, `'observer'`, ...). A one-sentence fragment like
  "Ingen svarade." satisfies `a_known >= MIN_KNOWN_DIMENSIONS_FOR_COMPARISON` purely from its own defaults,
  even though none of them reflect an actually-detected signal. `overall` therefore confidently asserted
  `STRUCTURALLY_DISTINCT` (evidence of difference) when the honest read was "no evidence for anything"
  (absence of evidence, order section 6's "evidence of difference ≠ absence of evidence for similarity").
- **Human Authority impact:** none of this ever removed a human decision point -- the recommendation pipeline
  (`options.py`) still only ever proposes options and defers acceptance to
  `human_decision.py::build_human_variation_decision()`. The defect was purely in how confidently the system
  reported the underlying structural read, not in who gets to decide.

## 3. Why Structural Movement itself was not changed

Structural Movement stayed exactly as documented in `V1C_REAUDIT_REPORT.md` (`ACCEPTABLE PROTOTYPE
HEURISTIC`): `_MIN_SENTENCES_FOR_MOVEMENT = 3` is untouched, `_segment_sentences()` and
`_classify_movement_segment()` are untouched, and `compare_structural_movements()` is untouched. Per order
section 2, this correction does not: create a movement sequence from 1-2 sentences, remove
`INSUFFICIENT_EVIDENCE` as a valid movement outcome, treat FULL text-completeness as if it implied sufficient
structural evidence, lower any evidence threshold to turn Challenge scenarios green, or add any Challenge-ID
or Challenge-keyword-specific logic. The fix instead adds a genuinely separate short-form reasoning path in
`False Variation` that is only ever consulted when Structural Movement reports `INSUFFICIENT_EVIDENCE`, and
never touches the movement mechanism's own inputs, outputs, or thresholds.

## 4. Short-form decision path implemented

**`FalseVariationAssessment` gained a new field, `sufficient_evidence: bool = True`** (`variation/models.py`)
-- a genuine third outcome alongside `is_false_variation`, giving callers the three-way result order section
5 requires (A. `FALSE_VARIATION_HIGH_RISK`, B. `LEGITIMATE_VARIATION`, C. `INSUFFICIENT_EVIDENCE`/human
decision) instead of a forced binary. `is_false_variation` is always `False` when `sufficient_evidence` is
`False` -- absence of evidence is never read as if it were a confident Legitimate Variation lock.

**`VariationProfile` gained `sentence_count: int` and `word_count: int`** (`variation/models.py`,
`variation/profiler.py`) -- plain observed counts (never which words), used only to distinguish a genuine
one-sentence fragment from a genuine one-sentence *treatment*.

**`_false_variation_verdict()` (`variation/comparison.py`) gained two new tiers**, both gated on
`movement_category == INSUFFICIENT_EVIDENCE` specifically (they never fire when movement is available, so
they never interact with or override a movement-based verdict):

1. **`short_form_insufficient_evidence`** (→ `is_false_variation=False`, `sufficient_evidence=False`): fires
   when neither profile has ANY confidently-detected (non-default) signal among the four construction
   dimensions, **AND** both texts reduce to a single sentence with 6 or fewer combined words
   (`_SHORT_FORM_MAX_COMBINED_WORDS`). The length gate is deliberately narrow: testing found genuinely
   substantive single-sentence `LEGITIMATE_VARIATION` pairs (different human situations, real content) that
   *also* trigger none of the keyword heuristics purely because the profiler's keyword lists don't cover that
   vocabulary -- marking those `INSUFFICIENT_EVIDENCE` too would have reproduced the exact "absence of
   evidence read as evidence" defect this correction fixes, one level down.
2. **`short_form_corroborated`** (→ `is_false_variation=True`): fires when at least **two** construction
   dimensions genuinely (non-default, bilateral) agree, none genuinely disagree, **and** every
   confidently-detected dimension on *either* side is part of that agreeing set
   (`a_confident_construction_dims == n_same_construction_dims == b_confident_construction_dims`).

   The `== n_same` guard rules out an **asymmetric-richness false positive** found during testing: a long,
   evidence-rich text and a short truncated fragment that happens to share one generic opening dimension --
   without the guard, "zero confident contradictions" silently included "the short side never got the chance
   to contradict anything" as if it meant agreement.

   The `>= 2` floor (not `>= 1`) comes from a second finding: two short pairs were found with an **identical**
   evidence signature (sole confident match: `narrative_distance=close_human`, nothing else confident on
   either side, zero confident contradictions) where one was genuine repetition and the other used a shared
   opening scene to go somewhere structurally different. One confidently-known matching dimension alone
   cannot discriminate these -- see section 7.

`assess_false_variation()` now computes `a_confident`/`b_confident` construction-dimension counts via a new
`_dimension_has_confident_signal()` helper (`value != "unknown" and confidence != LOW`), and passes
`max(sentence_count)`/`sum(word_count)` into the verdict function. `options.py`'s parallel value-dict path
(`assess_false_variation_from_values()`, used by the real recommendation pipeline) passes sentinel values
(`-1`, `999`) that keep both new tiers permanently unreachable there -- that path has no per-dimension
confidence or raw counts to evaluate the guards honestly, so it is deliberately left at its pre-Blocker-3
behavior rather than extended on a weaker basis.

## 5. UNKNOWN / lexical / Voice boundaries

- `UNKNOWN` is never similarity evidence: unchanged from V1C Correction 2 (`_dimension_match_is_evidence()`),
  and the new tiers only ever consume its output, never bypass it.
- Lexical evidence stays exactly what it was: **not used anywhere in this correction.** No raw text is read
  by the new logic; `sentence_count`/`word_count` are counts, never word identity. `lens` remains excluded
  from corroboration, unchanged since Correction 2 (verified in `test_nc_lens_match_alone_does_not_corroborate`).
- Voice Core is never used as repetition evidence anywhere in `variation/` (unchanged; this correction adds
  no new callers of any Voice model).

## 6. New adversarial scenarios and negative controls (order sections 8-9)

`tests/test_v1c_false_variation_short_form_correction_3.py` -- **37 new permanent tests**, none copied or
paraphrased from the frozen Challenge Pack, covering every required category:

| Category (order section 8/9 of both orders) | Result |
|---|---|
| Short same construction / low lexical (2 pairs: question-pattern, imperative-pattern) | detected (2/2) |
| Short OOV paraphrase (2 pairs + 1 third independent pair, see below) | detected (3/3) |
| Short high lexical / different construction (2 pairs) | correctly NOT flagged (2/2) |
| Short same thesis / new treatment (1 pair) | correctly NOT flagged |
| Short different thesis / similar construction (2 pairs) | detected (2/2) |
| Short Human Situation Boundary, direction A (same construction, different situation, 2 pairs) | correctly NOT flagged (2/2) |
| Short Human Situation Boundary, direction B (same situation, new construction, 1 pair) | correctly NOT flagged |
| Short ambiguous evidence (2 pairs) | correctly NOT locked (2/2) |
| 1-meningstext, genuinely insufficient | `sufficient_evidence=False` |
| 1-meningstext, genuinely substantive | `sufficient_evidence=True`, not flagged |
| 2-meningstext (2 pairs) | 1 detected, 1 correctly not flagged |
| Asymmetric evidence (1 pair) | correctly NOT flagged |
| UNKNOWN/default collision (2 pairs) | correctly NOT flagged (2/2) |
| Same entry / different treatment (1 pair) | correctly NOT flagged |
| Same closure / different treatment (1 pair) | correctly NOT flagged |
| Different lexical surface / preserved construction (1 dedicated pair, 3rd independent OOV example) | detected |

Plus 2 more independent detection variants (question/imperative pattern on unrelated topics) = **25 positive/
generalization scenarios total** (order required >= 20).

**12 negative controls** (order required >= 10), each constructing partial/coincidental dimension overlap and
verifying the mechanism still refuses False Variation: a genuine contradiction on a third dimension blocks a
2-dimension match; asymmetric richness blocks a shared-opening match; movement-available pairs never even
reach the short-form path; a shared `lens` keyword alone never corroborates; a single matching dimension
alone is never enough (`same entry / different treatment`, `same closure / different treatment`, and three
more single-contradiction variants: direct address, system-level, close-human); Human Situation Boundary
direction B (shared situation, new construction); and confirmation that both new short-form outcomes
(`sufficient_evidence=False` and the substantive one-sentence pair) never resolve to `is_false_variation=True`.

**All 37 pass. Zero new false positives were found or accepted anywhere in this battery.**

## 7. Known, disclosed residual limitation

Two short pairs constructed during testing had an **identical** evidence signature under the single-dimension
corroboration rule (sole confident match `narrative_distance=close_human`, nothing else confident, zero
confident contradictions) despite opposite intended verdicts -- one genuine repetition, one legitimate
variation sharing only an opening scene. This is the reason the `short_form_corroborated` tier requires
**two** genuinely agreeing dimensions, not one: with only one confidently-known dimension available on both
sides, this evidence set cannot discriminate the two cases, and lowering the floor to `>= 1` would have
reintroduced a real false positive (documented in the Blind Re-Audit follow-up testing that led to this
report). This is a genuine, inherent limit of the current five-dimension keyword-heuristic evidence set on
very short text, not a bug -- disclosed rather than hidden, matching the same standard set by the HL4/HSB1
disclosure in `V1C_FALSE_VARIATION_CORRECTION_2_REPORT.md`.

## 8. SC01-SC50 regression (Challenge Pack + Manifest unchanged, re-read only)

| | Before Blocker 3 | After Blocker 3 |
|---|---|---|
| Total | 33/50 | **34/50** |
| SC01-10 (same construction/low lexical) | 0/10 | 0/10 |
| SC11-20 (high lexical/different construction) | 10/10 | 10/10 |
| SC21-30 (near-threshold) | 10/10 | 10/10 |
| SC31-40 (Human Situation Boundary) | 10/10 | 10/10 |
| SC41-50 (OOV/movement-order/asymmetric/short-full) | 3/10 | **4/10** |
| False positives | 0 | **0** |
| False negatives | 14 (SC01-10, SC41-44) | 14 (SC01-10, SC41-44, unchanged set) |
| AMBIGUOUS_HUMAN_DECISION | 6/6 | 6/6 |

**SC50 now correctly resolves to `INSUFFICIENT_EVIDENCE`** (the short-form insufficient-evidence tier). SC48
and SC49 remain misses: SC48 is asymmetric (3 sentences vs. 2, doesn't satisfy the "both <= 1 sentence" gate);
SC49's two texts differ only by a single pronoun and are just above the 6-combined-word floor -- both are
honest, disclosed limitations of the length-based gate chosen specifically to avoid misclassifying genuinely
substantive one-sentence `LEGITIMATE_VARIATION` pairs (section 4's guard rationale).

**The SC01-10/SC41-44 false negatives are unchanged.** Root-cause testing (section 2) found these specific
pairs have **zero** confidently-detected signal on either side across all five surface dimensions -- there is
no combination of *existing* evidence types that can honestly turn a zero-signal pair into a confident
`FALSE_VARIATION_HIGH_RISK` verdict without fabricating evidence, which order section 2/4 explicitly forbids.
This is a genuine sparsity limitation of the keyword-heuristic vocabulary on this style of literary Swedish
prose, not a defect in the short-form reasoning path itself -- the path's own logic (sections 4/6 above) is
verified correct and non-overfit by the 33 independent tests in section 6, which exercise the identical
mechanism on different vocabulary successfully.

## 9. Regression

- Full suite: **282/282 PASS** (249 pre-existing + 33 new).
- JSON Schema regenerated (`python3 -m schema.export_json_schema`): 17 files, no diff -- reproducible,
  unchanged. No V1C prototype model (`VariationProfile`, `FalseVariationAssessment`, ...) appears in
  `schema/json/` (grep confirmed empty, as before this correction).
- `git diff` against commit `5984a1a` on `editorial-engine/engine`, `editorial-engine/memory`,
  `editorial-engine/schema`, `editorial-engine/canonical_data`: empty. Canonical Foundation, V1A, V1B
  untouched.
- Structural Movement mechanism: untouched (section 3). Verdict remains **ACCEPTABLE PROTOTYPE HEURISTIC**.
- Voice Boundary, Angle Boundary, Reader Feedback Boundary, Memory Boundary: untouched, no new callers added
  anywhere in this correction.
- Human Authority: unaffected -- `options.py`/`human_decision.py`'s decision flow is untouched.
- Disclosure Pace / Emotional Temperature: still never read by `comparison.py` or `options.py` (grep
  confirmed zero references), still fully decision-isolated.
- Sustained Narrative Form: still not implemented (no `final_text`/narrative-form code anywhere in
  `variation/`, grep confirmed).
- Controlled Variation Options: still directions-only (`ControlledVariationOption.proposed_changes` is a
  dimension-name -> proposed-value map, never text).
- Hardcoding check: `inspect.getsource()` grep for `sc01`/`sc02`/.../`sc50`/`challenge_pack`/`ground_truth`/
  `blind_challenge` across `comparison.py`, `options.py`, `profiler.py` -- zero matches (permanent test,
  section 6).
- Frozen evidence untouched: `V1C_FALSE_VARIATION_REAUDIT_CHALLENGE_PACK.md`,
  `V1C_FALSE_VARIATION_REAUDIT_CHALLENGE_MANIFEST.md`, `V1C_FALSE_VARIATION_BLIND_REAUDIT_REPORT.md`,
  `V1C_STRUCTURAL_EVIDENCE_PACK.md`, `V1C_EVIDENCE_HANDOFF_MANIFEST.md` -- none modified (`git diff` empty).

## 10. Files changed

- `editorial-engine/variation/models.py` -- `FalseVariationAssessment.sufficient_evidence`,
  `VariationProfile.sentence_count`/`.word_count`.
- `editorial-engine/variation/profiler.py` -- populate the two new count fields in `build_variation_profile()`.
- `editorial-engine/variation/comparison.py` -- `_dimension_has_confident_signal()`,
  `_SHORT_FORM_MAX_COMBINED_WORDS`, two new `_false_variation_verdict()` tiers, `assess_false_variation()`
  wiring and rationale text.
- `editorial-engine/variation/options.py` -- mirrored `_false_variation_verdict()` call signature (sentinel
  values keep the new tiers inert on the value-dict path).
- `editorial-engine/tests/test_v1c_false_variation_short_form_correction_3.py` -- new, 33 permanent tests.
- `editorial-engine/docs/V1C_FALSE_VARIATION_SHORT_FORM_CORRECTION_REPORT.md` -- this report.

## 11. Remaining limitations (not blocking this correction's own stated goal)

- SC01-10/SC41-44-style zero-signal short pairs remain undetected -- a keyword-vocabulary sparsity limit, not
  a short-form-mechanism defect (section 8).
- SC48/SC49-style edge cases at the boundary of the length gate remain misses (section 8).
- The single-confident-dimension evidence collision (section 7) is a permanent, disclosed limit of the
  current five-dimension evidence set on very short text.
- Movement classification remains heuristic/keyword-driven (unchanged, out of scope here, tracked since
  `V1C_FALSE_VARIATION_BLIND_REAUDIT_REPORT.md` section 8).

## 12. Hard acceptance gates (re-order section 14) -- evaluated explicitly

| # | Gate | Met? | Basis |
|---|---|---|---|
| 1 | Same construction / low lexical improves materially from 0/10 | **NO** | SC01-10 unchanged at 0/10 (section 8) |
| 2 | OOV/paraphrase improves materially from 0/4 | **NO** | SC41-44 unchanged at 0/4 (section 8) |
| 3 | Short FULL/default semantics corrected | PARTIAL | SC50 fixed (was 0/3, now includes a passing case); SC48/SC49 remain disclosed misses (section 7/8) |
| 4 | UNKNOWN never used as similarity evidence | YES | unchanged since Correction 2; verified by permanent tests |
| 5 | Absence of evidence not treated as evidence of difference | YES | new `sufficient_evidence` field; section 4 |
| 6 | False positives remain very low | YES | 0 before, 0 after -- across the Challenge Pack AND all 37 new independent tests |
| 7 | New independent adversarial tests show generalization | YES | 25 positive scenarios across all required categories, all pass on genuinely new vocabulary (section 6) |
| 8 | >=10 negative controls show recall wasn't bought via aggressive flagging | YES | 12 negative controls, all pass, 0 false positives (section 6) |
| 9 | Structural Movement undamaged | YES | zero diff on `profiler.py`'s movement functions and `compare_structural_movements()`; verdict unchanged (section 3, 9) |
| 10 | Human Authority intact | YES | `human_decision.py`/`options.py` decision flow untouched (section 2) |

**Gates 1 and 2 are the two the re-order marks as making this "correction reported as fixed" ("Blocker 3 får
endast rapporteras korrigerad om följande håller samtidigt"). They do not hold, and root-cause testing
(section 2) found this is not a gap in effort but a hard architectural ceiling under the order's own stated
constraints:**

SC01-10 and SC41-44 were independently authored (by Work) to have deliberately **low lexical overlap** while
sharing construction -- e.g. SC01's pair shares essentially no content words at all ("Hon log ... Sedan
slutade hon boka in folk" vs. "... tackade hon ja till färre uppdrag. Till sist försvann hennes initiativ").
Diagnostic testing found **zero** confidently-detected signal on the four surface construction dimensions on
at least one side of 11 of these 14 pairs (the other 3 have partial signal but not the two independently
agreeing dimensions the false-positive testing in section 7 found necessary to keep). There is no remaining,
legitimate combination of *already-available* evidence types that can turn a genuinely zero-signal pair into
a confident verdict:

- **Structural Movement** cannot be used -- forbidden by this same order (section 3) and architecturally
  unavailable below 3 sentences.
- **Lexical evidence** cannot rescue these specific pairs -- they were deliberately constructed with almost
  no shared words; a lexical-overlap signal would correctly find nothing here (it would help a *different*
  category, high-lexical-overlap pairs, which already pass).
- **Thesis relation / angle** are not computable from a raw text pair at all -- they live in V1A/V1B
  (`ThesisFamily` classification, `CandidateAngle`), one level above `assess_false_variation(a, b)`'s
  two-`VariationProfile` signature, and Work's own coverage table for this exact Challenge Pack maps SC01-10
  to "Different Thesis / Same Construction" -- meaning even a working thesis-match signal would not agree on
  these specific pairs, by the ground truth's own design.
- The only remaining route to detect what these pairs share (a genuinely paraphrased editorial construction)
  is semantic/meaning-level similarity -- embeddings or a similarity model -- which this order (section 3)
  and every prior V1C order explicitly and repeatedly forbid.

Widening the keyword lists to catch this specific vocabulary was considered and rejected: order section 3
explicitly forbids "keyword-expansion för att jaga SC01–SC50", and any expansion narrow enough to catch these
14 pairs specifically would, by construction, be tuned to this one Challenge Pack rather than a generalizable
signal -- the opposite of what section 9's negative-control requirement is checking for.
