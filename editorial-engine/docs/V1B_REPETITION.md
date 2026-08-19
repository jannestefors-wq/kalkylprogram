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
SAME, already-tested V1A arithmetic now runs on real data.

**V1B Correction Order (docs/V1B_CORRECTION_REPORT.md, Defect 2)**: V1B
Final Audit found that a LONE canonical-relation match (no content-level
corroboration) was enough to reach HIGH -- and, because V1A's rule-based
interpretation text uses the same handful of boilerplate words on most
sufficient inputs regardless of theme, that made HIGH nearly universal.
`memory/comparison.py::compare_to_editorial_memory()` now requires BOTH a
canonical signal AND a content signal (a real topic-label match, or at
least two literal shared words with the raw input -- never generated
interpretation boilerplate) before a match counts as `"strong"`:

- **HIGH**: a memory match is `"strong"` -- shares a Thesis Family or
  Territory with the classification AND shares real, named vocabulary
  (topic label or literal fulltext terms) with the RAW INPUT.
- **MEDIUM**: a memory match is `"weak"` WITH real content-level evidence
  (a topic label or 2+ literal terms) but no canonical relation --
  genuine lexical signal, just not canonical-corroborated.
- **LOW**: no memory match reaches either bar, or the corpus is empty. A
  lone canonical relation with no content corroboration, or a single
  incidental shared word, is excluded from scoring entirely (see
  `memory/bridge.py`) -- visible in the richer `MemoryComparisonResult`
  for transparency, but not counted toward HIGH/MEDIUM.

All three are directly tested against the real corpus in
`tests/test_v1b_pipeline.py::test_12/13/14_*` and permanently
regression-tested in `tests/test_v1b_correction_regression.py`.

## Corpus-bounded, not absolute (order section 15)

"LOW" means "low repetition against the available corpus that was
checked" -- it never means "this has never been done before." The same
boundary note that governs comparison/retrieval (see
`docs/V1B_MEMORY_BOUNDARY.md`) applies here; `RepetitionRiskLevel.LOW`
carries no separate, stronger claim of its own.

## Repetition actually changes the outcome (order section 16-17)

`tests/test_v1b_pipeline.py::test_17_memory_influences_candidate_angles_for_genuinely_relevant_input`
and `test_18_high_repetition_can_yield_no_strong_angle` prove this is not
inert metadata: a raw idea genuinely close to real memory, run with an
empty vs. the real corpus, produces different repetition risk AND a
different `RecommendationResult.outcome` (`RECOMMENDED` vs
`NO_STRONG_ANGLE`) -- and that difference is now traceable to a specific,
named, corroborated match, not a structural artifact.
