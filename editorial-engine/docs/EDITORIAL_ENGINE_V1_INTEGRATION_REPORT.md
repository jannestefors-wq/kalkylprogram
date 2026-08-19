# Editorial Engine V1. Integration Report

**Status:** Executor report per `EDITORIAL_ENGINE_V1_INTEGRATION_HANDOFF.md` section 8.
**Scope:** `editorial-engine/integration/` (new connective package) + `editorial-engine/tests/test_integration_v1.py` (new tests) only. No file under `engine/`, `memory/`, `variation/`, `schema/` or `canonical_data/` was modified.

## 1. Verified baseline and final regression

- Branch: `claude/editorial-engine-v1-integration`, branched from `claude/editorial-variation-v1c`. Merge-base with `origin/main` (`34e3fda`) is exact -- V1A + V1B are already on `main`; V1C's full frozen history (through commit `5311743`) is present unmodified on this branch.
- Baseline regression before this work: 314/314 (`editorial-engine/tests`, pre-existing V1A/V1B/V1C suites).
- Final regression after this work: **326/326** (`python3 -m pytest tests/ -q`) -- the 314 pre-existing tests plus 12 new integration-contract tests, all green. No pre-existing test was edited.
- Canonical JSON Schema regenerates byte-identical (`python3 -m schema.export_json_schema`, diffed against committed `schema/json/*.schema.json` -- no diff).
- No forbidden capability present: grepped the new code for generator/Quality-Gate/V1D/RAG/embedding/vector-database/LLM-classifier/UI/API/website/autonomous-publishing patterns -- zero matches.

## 2. Actual files changed

New files only (nothing pre-existing edited):

- `editorial-engine/integration/__init__.py`
- `editorial-engine/integration/models.py`
- `editorial-engine/integration/pipeline.py`
- `editorial-engine/tests/test_integration_v1.py`
- `editorial-engine/docs/EDITORIAL_ENGINE_V1_INTEGRATION_REPORT.md` (this file)

## 3. V1A / V1B / V1C contract mapping

The required flow (`RAW INPUT -> V1A -> V1B -> Human Decision -> V1C -> Human Variation Decision -> Final Editorial Assessment`) is implemented without re-implementing any editorial logic:

- `run_v1b_pipeline()` (existing, unmodified) already reuses V1A's own interpretation/classification/angle/recommendation steps directly, per its own docstring, then adds Editorial Memory retrieval and comparison. The integration layer calls this once per flow and never re-derives any of its fields.
- `run_v1c_variation_analysis()` (existing, unmodified) is called only once a real candidate angle has been selected, with the memory records resolved back from `v1b.memory_comparison.matches` (FULL-completeness records only -- PARTIAL records are never passed as structural evidence, satisfying contract section 3's "Partial memory records must not be used as full structural evidence").
- `_label_v1c_assessment()` is a pure, read-only re-labeling function: it maps V1C's own already-computed `FalseVariationAssessment` / `VariationDistanceCategory` onto the contract's requested display vocabulary (`LEGITIMATE_VARIATION`, `FALSE_VARIATION_HIGH_RISK`, `PARTIAL_SIMILARITY`, `INSUFFICIENT_EVIDENCE`, `AMBIGUOUS_HUMAN_DECISION`). It never re-decides anything. `sufficient_evidence == False` maps to `AMBIGUOUS_HUMAN_DECISION` per the locked `70b94af` policy (SC48/SC49-style cases go to Human Decision, never to a hard novelty claim).
- Two-phase real API: `run_v1a_v1b_stage()` runs V1A/V1B once and returns the assessment with decision point 1 pending, plus the `V1BPipelineResult` object itself; `continue_after_human_decision()` takes that exact object back with a genuine `schema.HumanDecision` and only then runs V1C. `run_editorial_engine_v1()` is a one-shot convenience wrapper that delegates to both in sequence. This two-phase split exists because `schema.HumanDecision` hard-validates `decided_by_actor == Actor.HUMAN` (unmodified Canonical Foundation V1 constraint) and candidate-angle ids are freshly minted on every V1B run -- a decision captured from one run can never be resolved against a different run's ids.
- `run_evaluation()` is the non-persistent Evaluation Mode: it runs the full V1A->V1B->V1C chain along the system's own recommended path (never constructing a `schema.HumanDecision`, which would fabricate a human actor), and returns both decision points as `pending_human_input` with a `system_recommendation` but no `decision_reference`.

## 4. Final Editorial Assessment shape

`FinalEditorialAssessment` (in `integration/models.py`) implements contract section 5 A-D plus both Human Authority decision points:

- **A. Sees** (`EngineSeesFields`): input reference, language, sufficiency flag, V1A/V1B classification (thesis family / territory / series / topic), interpretation (`observed_situation`), selected angle core, and V1C's construction dimensions (lens, narrative distance, entry/closure function, Structural Movement sufficiency + sequence, Local Editorial Function sufficiency + situation/consequence spans). Every field is `None`, never a guessed value, when the source data does not support it -- including V1C's own `"unknown"` dimension values, which are translated to `None` rather than passed through as a string (verified by `test_unknown_is_neither_similarity_nor_difference_evidence`).
- **B. Remembers** (`EngineRemembersFields`): one `RememberedRecord` per V1B match, each carrying `content_id`, `text_completeness`, `publication_status`, `why_relevant`, `repetition_signal_strength`, plus `corpus_size`, `fulltext_corpus_size`, `memory_boundary_note` (passed through **verbatim** from `v1b.memory_comparison.memory_limitation_note`, never reworded), and `no_match`.
- **C. Assesses** (`EngineAssessesFields`): `label`/`rationale`/`sufficient_evidence`, populated only when V1C actually ran and produced a recommended option; otherwise all `None`.
- **D. Could change** (`EngineCouldChangeFields`): `directions`, built only from `ControlledVariationOption.proposed_changes` values joined with `" -> "` -- dimension tokens, never generated prose.
- **Human Authority**: `human_decision_after_v1a_v1b` (always present) and `human_decision_after_v1c` (present only once V1C has run), each a `HumanDecisionPoint` with `stage`, `status`, `available_actions`, `system_recommendation`, `rationale`, `decision_reference`. `decision_reference` is populated only when a genuine `schema.HumanDecision` was supplied and validated as `decided_by_actor == Actor.HUMAN`.
- `provenance_note` is a fixed, always-present sentence stating that V1A interpretation is runtime analysis, V1B absence-of-match is bounded (never proof of novelty), V1C output is prototype-derived and non-canonical, and nothing here is Ground Truth or permanent memory.

## 5. Human Authority and uncertainty propagation

- Evaluation Mode never constructs a `schema.HumanDecision`; both decision points always come back `pending_human_input` with `decision_reference=None` (`test_human_authority_remains_explicit_evaluation_mode_never_decides`, and confirmed across all 14 real cases below -- 0/14 fabricated a decision).
- The real entry point resolves a decision point to `"decided"` only when handed a genuine, human-authored `schema.HumanDecision` naming a real candidate from the *same* V1B run (`test_human_authority_real_decision_is_honored_when_supplied`).
- `MORE_CONTEXT_REQUIRED` (V1A/V1B insufficient input) propagates all the way to the assessment: `sees.input_sufficient_for_interpretation = False`, the decision-1 rationale carries V1B's own `stopped_reason`, and no field downstream is fabricated (`test_uncertainty_survives_end_to_end`).
- V1C's `sufficient_evidence == False` (SC48/SC49-style ambiguity) maps to `AMBIGUOUS_HUMAN_DECISION`, never to a hard claim, per the frozen `70b94af` policy.

## 6. Evaluation results -- the 14 real cases

Run via `run_evaluation()` against the real `memory.ingestion.load_editorial_memory()` corpus (21 records). For each case, the memory pool passed to that case's own run excludes that case's own record (the case text *is* an existing memory item; comparing it against a corpus that already contains itself would produce a trivial self-match rather than a genuine test of retrieval against the rest of the corpus, which is what the Evaluation Set's own questions -- e.g. EV03/EV04 "same thesis family, different treatment" -- are actually asking). No source text was altered. No run wrote to `memory/data/` (confirmed by `test_evaluation_mode_writes_no_permanent_memory_or_canonical_data`, and independently by an identical before/after `load_editorial_memory()` diff across all 14 real runs plus the harness itself).

| Case | Source | V1A/V1B outcome | V1C ran | Assesses label | Usefulness | Key observation |
|---|---|---|---|---|---|---|
| EV01 | content-work-001 | MORE_CONTEXT_REQUIRED | No | -- | PARTIALLY_USEFUL | Correct Human Decision, but generic stop rationale + empty `available_actions` (obs-PATTERN-002/003) |
| EV02 | content-work-002 | MORE_CONTEXT_REQUIRED | No | -- | PARTIALLY_USEFUL | Same pattern; 30-word consequence-chain text still gated as "too thin" |
| EV03 | content-work-003 | MORE_CONTEXT_REQUIRED | No | -- | PARTIALLY_USEFUL | Series-relation integration question never reached (V1B never ran) |
| EV04 | content-work-004 | MORE_CONTEXT_REQUIRED | No | -- | PARTIALLY_USEFUL | Same-thesis-different-treatment question never reached |
| EV05 | content-work-005 | COMPLETED, RECOMMENDED | **Yes** | FALSE_VARIATION_HIGH_RISK (sufficient_evidence=True) | PARTIALLY_USEFUL | Only case reaching V1C; hard high-risk verdict sits next to memory matches all only "weak" repetition signal (obs-EV05-001, isolated) |
| EV06 | content-work-006 | COMPLETED, NO_STRONG_ANGLE | No | -- | USEFUL | 9 memory matches surfaced with attribution; correct explicit Human Decision |
| EV07 | content-work-007 | COMPLETED, NO_STRONG_ANGLE | No | -- | USEFUL | 7 memory matches surfaced; longer/procedural text preserved uncertainty and provenance |
| EV08 | content-work-008 | COMPLETED, NO_STRONG_ANGLE | No | -- | USEFUL | 8 matches, several "strong" repetition signal -- real, traceable evidence even without V1C |
| EV09 | content-work-009 | MORE_CONTEXT_REQUIRED | No | -- | PARTIALLY_USEFUL | Same pattern as EV01-04 |
| EV10 | content-work-010 | MORE_CONTEXT_REQUIRED | No | -- | PARTIALLY_USEFUL | System-lens integration question never reached |
| EV11 | content-work-011 | MORE_CONTEXT_REQUIRED | No | -- | PARTIALLY_USEFUL | Human-near-treatment question never reached |
| EV12 | content-work-012 | MORE_CONTEXT_REQUIRED | No | -- | PARTIALLY_USEFUL | Correctly stayed uncertain rather than forcing `INSUFFICIENT_EVIDENCE`/label -- but via V1A gate, not V1C, so the specific question ("does V1C prefer INSUFFICIENT_EVIDENCE") was not exercised |
| EV13 | content-published-003 (en, partial, published_verified) | MORE_CONTEXT_REQUIRED | No | -- | PARTIALLY_USEFUL | Cross-language / partial-published-evidence question never reached (V1B never ran); no crash on English input |
| EV14 | content-published-002 (sv, partial, published_verified) | MORE_CONTEXT_REQUIRED | No | -- | PARTIALLY_USEFUL | Voice-register-vs-construction question never reached |

**Totals: USEFUL 3, PARTIALLY_USEFUL 11, NOT_USEFUL 0.**

Full per-case V1A/V1B/V1C output (classification, interpretation, memory matches, V1C options, and the complete `FinalEditorialAssessment`) was captured to a scratch JSON dump during evaluation and is summarized here; it is not committed (not a required artifact and not source material).

## 7. Observation log

| Observation ID | Case ID(s) | Observed behavior | Human editorial reading | Component | Category | Severity | Pattern scope | Recommendation |
|---|---|---|---|---|---|---|---|---|
| obs-PATTERN-001 | EV05, EV06, EV07, EV08 | The 4 cases that reach `COMPLETED` all receive an *identical* `interpretation.observed_situation` string ("Raw input beskriver en upprepad handling.") and near-identical classification (same two thesis families, same territory "Makt") despite materially different content (a triangulation model, a scene-observation text, a 7-step process, a 4-word framework). | Looks like V1A's interpretation/classification step may fall back to a shared generic template rather than differentiating per text; an editor could be misled into thinking the system read the specific content when it may not have. This is existing, frozen V1A behavior surfaced by the integration layer, not something introduced by it. | V1A (pre-existing) | JUDGMENT_MISS | Medium | Systematic (4/4 completed cases) | INVESTIGATE |
| obs-PATTERN-002 | EV01, EV02, EV03, EV04, EV09, EV10, EV11, EV12, EV13, EV14 | 10 of 14 real cases (71%) stop at `MORE_CONTEXT_REQUIRED` with the same templated rationale ("for fa ord ... Mer kontext kravs"), including texts of 20-30 words with clear thesis content (e.g. EV02's consequence chain, EV11's direct-address responsibility text). | A human editor would likely consider several of these substantive, decision-ready drafts, not "too thin." The gate may be calibrated for shorter synthetic inputs and may be over-conservative on real short-form LinkedIn-style material -- this is V1A's existing threshold, not something the integration layer can or should retune. | V1A (pre-existing) | JUDGMENT_MISS | Medium | Systematic (10/14 real cases) | INVESTIGATE |
| obs-PATTERN-003 | EV01, EV02, EV03, EV04, EV09, EV10, EV11, EV12, EV13, EV14 | For every `MORE_CONTEXT_REQUIRED` case, `human_decision_after_v1a_v1b.available_actions` is an empty list -- only the `RECOMMENDED` and `NO_STRONG_ANGLE` branches populate an action menu. | The decision point's `status`/`rationale` are visible (contract requirement met literally), but the human is not given an explicit menu of what they can do (e.g. "provide_more_context", "reject_all") for the single most common outcome in this real dataset. | integration (`run_v1a_v1b_stage` / `run_evaluation`, this task's own code) | OTHER | Medium | Systematic (10/14 real cases) | INVESTIGATE |
| obs-PATTERN-004 | all 14 | Across all 14 real, materially different inputs, both decision points were returned `pending_human_input` with `decision_reference=None` in every Evaluation Mode run -- Human Authority was never bypassed once. | Confirms the integration contract's core Human Authority guarantee holds under real data variety, not only synthetic tests. | integration | CORRECT_HUMAN_ESCALATION | Low | Systematic (14/14) | ACCEPT |
| obs-EV05-001 | EV05 | The only case reaching V1C produces `FALSE_VARIATION_HIGH_RISK` with `sufficient_evidence=True`, but every one of its 5 supporting memory matches carries `repetition_signal_strength: "weak"` (none "strong"). | The hard high-risk verdict and the weak underlying repetition signal are not reconciled anywhere in the assessment; a human trusting the label at face value could reject a treatment that the same assessment's own memory evidence only weakly supports. Matches the residual risk the `70b94af` Gate 7 policy already predicted ("MEDEL, inte lag") for the loosened LEF-corroboration tier -- this appears to be a live instance of that disclosed risk, not a new defect. | V1C (frozen) | FALSE_POSITIVE | High | Local (only 1/14 cases reached V1C in this run; echoes a previously-disclosed systemic risk) | INVESTIGATE |

Per the Handoff's explicit instruction, none of these were repaired during the evaluation run -- they are logged and reported here for the project lead's disposition.

## 8. Measurement summary

(Counting distinct observed patterns/instances, not per-affected-case tallies -- see column "Pattern scope" above for how many real cases each one touches.)

- Total cases: 14
- USEFUL: 3 -- PARTIALLY_USEFUL: 11 -- NOT_USEFUL: 0
- False Positives: 1 (obs-EV05-001)
- False Negatives: 0
- Memory Misses: 0
- Judgment Misses: 2 (obs-PATTERN-001, obs-PATTERN-002)
- Structural Misses: 0
- Uncertainty Misses: 0
- Bad Variation Directions: 0
- Correct Human Escalations: 1 pattern, holding on 14/14 cases (obs-PATTERN-004)
- Integration Defects: 0 confirmed contract/handoff/provenance failures; 1 completeness gap logged as OTHER (obs-PATTERN-003)
- Repeated (systematic) patterns: 4 (obs-PATTERN-001 through 004)
- Isolated (local) observations: 1 (obs-EV05-001)

## 9. Systematic vs. isolated

Three of the four logged patterns are systematic and concern **existing, frozen V1A/V1C behavior surfaced by running real data through the new integration layer for the first time** -- not integration defects. The fourth (obs-PATTERN-003) is systematic and *is* inside the integration layer's own code, and is the one item this report recommends acting on. Only one finding (obs-EV05-001) is local/isolated to a single case, though it corroborates a risk already disclosed in the locked `70b94af` V1C decision record rather than surfacing a new one.

## 10. Integration blocker vs. expected prototype limitation

No integration blocker was found under the Handoff's own table (section 7 of the Rubric): V1A output was always readable by V1B/V1C; provenance and uncertainty never disappeared; no run wrote permanent memory or canonical data; no V1C prototype field leaked into canonical schema (`test_v1c_prototype_models_do_not_leak_into_canonical_schema`); Human Authority was never bypassed. Every logged observation falls on the "accepted prototype limitation" / "investigate" side of that table, not the blocker side.

## 11. Canonical / schema status

Unchanged and reproducible. `python3 -m schema.export_json_schema` regenerates all 17 files byte-identical to the committed versions. No V1C or integration prototype type name (`VariationProfile`, `LocalEditorialFunctionAssessment`, `FalseVariationAssessment`, `StructuralMovementAssessment`, or any `integration.models` type) appears anywhere in `schema/json/*.schema.json`.

## 12. What worked, what did not, one recommended next step

**Worked:** the smallest-possible connective layer was sufficient -- no V1A/V1B/V1C production code needed changing. The two-phase Human Decision API correctly resolves the "decision must survive to a later, independent call" requirement without ever fabricating a `schema.HumanDecision`. Provenance, memory boundary wording, and the `UNKNOWN`-is-not-evidence guarantee all survived unmodified end to end across 14 materially different real texts, not just the synthetic contract tests. Evaluation Mode ran the full chain and wrote nothing to permanent state on every one of the 14 real cases plus the 12 integration tests.

**Did not work / open questions:** 10 of 14 real cases never got far enough to exercise V1B or V1C at all, which means the Evaluation Set's cross-language, partial-publication, and same-thesis-different-treatment integration questions (EV03/04, EV07/08 pairing questions, EV13, EV14) are largely **untested by this run**, through no fault of the integration layer -- V1A's own "too thin" gate stopped them first. This is the single biggest limiter on how much of the Evaluation Set's intent could actually be exercised.

**One recommended next step:** fix obs-PATTERN-003 (populate `available_actions` on the `after_v1a_v1b` decision point for the `MORE_CONTEXT_REQUIRED` branch, e.g. `["provide_more_context", "reject_all"]`) -- it is a small, integration-layer-only, non-editorial change squarely inside this task's own new code, touches no frozen V1A/V1B/V1C logic, and directly improves usefulness for the majority (10/14) real-case outcome observed in this run. Everything else logged here (obs-PATTERN-001, 002, and obs-EV05-001) concerns frozen or pre-existing component behavior and is reported to the project lead for disposition, not acted on, per the Handoff's explicit instruction not to repair findings during evaluation.
