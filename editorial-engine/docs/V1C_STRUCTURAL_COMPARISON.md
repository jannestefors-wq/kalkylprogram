# V1C Structural Comparison

`variation/comparison.py::compare_variation_profiles()` -- the smallest
transparent mechanism that compares two `VariationProfile`s over the six
OBSERVED dimensions (order section 21). No embedding, no vector database,
no RAG, no similarity model, no fabricated precise score (order section
18, 21, 34) -- a plain field-by-field diff with a named category.

## Categories (order section 18)

- `TOO_SIMILAR` -- 5 or 6 of 6 OBSERVED dimensions match.
- `PARTIALLY_DISTINCT` -- 3 or 4 of 6 match.
- `STRUCTURALLY_DISTINCT` -- 0-2 of 6 match.
- `INSUFFICIENT_EVIDENCE` -- fewer than
  `MIN_KNOWN_DIMENSIONS_FOR_COMPARISON` (4) OBSERVED dimensions are known
  (not `unknown`) on either profile -- refuse to categorize thin evidence
  rather than force it.

## Multi-axis repetition (order section 19-20)

`assess_multi_axis_repetition()` keeps six repetition axes explicitly
separate -- they are never collapsed into one signal:

| Axis | Source of truth |
|---|---|
| THESIS | The caller's own V1A/V1B classification (shared canonical Thesis Family) |
| ANGLE | Whether the angle's own structural profile is near-identical (same_count >= 5) to relevant memory |
| STRUCTURAL | `compare_variation_profiles()`'s `overall` category |
| OPENING | Whether `entry_mode` alone matches (and is known) |
| ENDING | Whether `closure_mode` alone matches (and is known) |
| LEXICAL | Whatever raw word overlap the caller passes in (typically from V1B) |

**The critical rule (order section 20)**: the LEXICAL axis's value is
NEVER read by the STRUCTURAL axis's computation -- `assess_multi_axis_repetition()`
computes `structural` purely from `structural_comparison`, an argument
that itself came only from `compare_variation_profiles()`, which never
looks at raw words. A caller can therefore truthfully say "V1B found
lexical overlap here, but V1C's structural evidence does not support
repetition" -- see `tests/test_v1c_comparison.py::test_10_*` and
`tests/test_v1c_paths.py::test_lexical_collision_path_*`.

## False Variation (order section 17)

`assess_false_variation()` reuses `compare_variation_profiles()` directly
-- two treatments are false variation exactly when their category is
`TOO_SIMILAR`. Because the comparison only ever looks at the six
structural dimensions and never at raw words, a pure synonym/formatting/
hook change is invisible to it by construction: two texts that only
differ in wording will have identical `entry_mode`, `lens`,
`narrative_distance`, `structural_arc`, `rhetorical_pressure`, and
`closure_mode`, and will correctly be flagged false variation
(`tests/test_v1c_paths.py::test_false_variation_path_*`).
