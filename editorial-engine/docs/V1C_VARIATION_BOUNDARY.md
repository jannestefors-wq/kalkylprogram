# V1C Variation Boundary

## Prototype analysis output, never canonical data

`variation/models.py::VariationProfile`, `ControlledVariationOption`, and
every other model in `variation/` are analysis output -- the same
discipline `engine/models.py` (V1A) and `memory/models.py` (V1B) already
established. None of it is exported from `schema/`, none of it is
written into `canonical_data/`, and none of it is written back onto an
Editorial Memory record's `original_text` or a `schema.ContentRecord`.
`tests/test_v1c_pipeline.py::test_27_canonical_foundation_unchanged_by_running_v1c`
verifies this by comparing every canonical registry byte-for-byte
before/after a full V1C run.

## Evidence status is data, not just prose

`DIMENSION_EVIDENCE_STATUS` (a fixed dict, not a per-analysis field) says
which of the eight implemented dimensions are OBSERVED versus SUPPORTED
HYPOTHESIS:

| Dimension | Evidence status |
|---|---|
| entry_mode, lens, narrative_distance, structural_arc, rhetorical_pressure, closure_mode | OBSERVED |
| disclosure_pace, emotional_temperature | SUPPORTED_HYPOTHESIS |
| (Sustained Narrative Form) | EXPLORATORY -- not implemented |

`OBSERVED_DIMENSIONS` (a tuple, not a convention) is the ONLY set of
dimensions `variation/comparison.py` and `variation/options.py` are
allowed to read when deciding structural similarity, false variation, or
which option to recommend --
`VariationProfile.observed_values()` is the single method that exposes
them, and every comparison/decision function in this package calls only
that method, never the two hypothesis fields directly.

## Hypothesis dimensions never decide anything alone

`disclosure_pace` and `emotional_temperature` are analyzed and carried on
every profile, but:
- their confidence is structurally capped at `ConfidenceLevel.LOW`
  (`tests/test_v1c_profiler.py::test_hypothesis_dimensions_never_exceed_low_confidence`),
- they are excluded from `observed_values()`, so `compare_variation_profiles()`,
  `assess_false_variation()`, and `generate_controlled_variation_options()`
  never see them at all.

## FULL/PARTIAL boundary, enforced not documented

`variation/profiler.py::build_variation_profile_for_memory_record()` is
the only function that turns an `EditorialMemoryRecord` into a
`VariationProfile`. It raises `PartialTextVariationError` if
`text_completeness != FULL` -- there is no code path anywhere in
`variation/` that builds a structural profile from a PARTIAL record's
text.

## No canonical taxonomy created

`EntryMode`, `Lens`, `NarrativeDistance`, `StructuralArc`,
`RhetoricalPressure`, `ClosureMode`, `DisclosurePace`,
`EmotionalTemperature` are plain Python enums living in `variation/models.py`
-- not `schema/enums.py`, not exported from `schema/`, not referenced by
any canonical model. They can change or be discarded entirely in a future
order without touching Canonical Foundation V1.

## Known, accepted limitation: default-value coincidence

Because the profiler is a small set of transparent keyword/structure
rules (order section 31/34 forbid anything larger), several dimensions
fall back to a low-confidence default when no stronger signal is present
(`entry_mode` -> `claim`, `narrative_distance` -> `observer`,
`rhetorical_pressure` -> `quiet_observation`, `closure_mode` ->
`still_statement`). Two otherwise-unrelated plain declarative texts can
both land on these same defaults and read as `TOO_SIMILAR` by
coincidence, not genuine repetition -- every such default carries
`ConfidenceLevel.LOW`, so the limitation is visible in the object, not
hidden. This is the same class of limitation V1B already accepted for
lexical word-overlap (`docs/V1B_CORRECTION_REPORT.md`'s LIMITATION
section) -- documented, not solved, per this order's explicit scope.
