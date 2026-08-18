# V1B Repetition

V1A's `RepetitionRiskLevel` (LOW/MEDIUM/HIGH, `engine/models.py`) is
unchanged (order section 15: "Behall V1A:s: LOW MEDIUM HIGH"). What V1B
changes is the EVIDENCE behind the assessment -- real Editorial Memory
instead of an empty or synthetic `existing_content` list.

## How memory feeds V1A's existing repetition logic, unmodified

`engine/angles.py::_repetition_risk_for()` was never touched. It already
derives HIGH/MEDIUM/LOW from a `ComparisonResult`'s matches and whether
their `shared_thesis_family_ids`/`shared_territory_ids` overlap the
candidate angle's own canonical relations. `memory/bridge.py::to_legacy_comparison_result()`
turns a real `MemoryComparisonResult` into exactly that shape, so the
SAME, already-tested V1A arithmetic now runs on real data:

- **HIGH**: a memory match shares a Thesis Family or Territory with the
  candidate angle's own classification (`repetition_signal_strength ==
  "strong"` in the richer `MemoryComparisonResult`).
- **MEDIUM**: a memory match exists only via topic/term overlap, with no
  shared canonical relation (`"weak"`).
- **LOW**: no memory match at all, or the corpus itself is empty.

All three are directly tested against the real corpus in
`tests/test_v1b_pipeline.py::test_12/13/14_repetition_*`.

## Corpus-bounded, not absolute (order section 15)

"LOW" means "low repetition against the available corpus that was
checked" -- it never means "this has never been done before." The same
boundary note that governs comparison/retrieval (see
`docs/V1B_MEMORY_BOUNDARY.md`) applies here; `RepetitionRiskLevel.LOW`
carries no separate, stronger claim of its own.

## Repetition actually changes the outcome (order section 16-17)

`tests/test_v1b_pipeline.py::test_17_memory_influences_candidate_angles`
and `test_18_high_repetition_can_yield_no_strong_angle` prove this is not
inert metadata: the identical raw idea, run with an empty vs. the real
corpus, produces different repetition risk AND a different
`RecommendationResult.outcome` (`RECOMMENDED` vs `NO_STRONG_ANGLE`).
