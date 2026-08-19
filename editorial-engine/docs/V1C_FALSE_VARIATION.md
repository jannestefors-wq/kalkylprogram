# V1C False Variation

A dedicated note because order section 17 and 39 single this concept out.

## Definition used by V1C

Two structural treatments are **false variation** when comparing their
`VariationProfile`s over the six OBSERVED dimensions returns
`VariationDistanceCategory.TOO_SIMILAR` (5 or 6 of 6 dimensions match).
See `docs/V1C_STRUCTURAL_COMPARISON.md`.

## What this catches

Because the comparison never inspects raw wording, it structurally
cannot be fooled by:
- synonym substitution ("mätte" -> "observerade", "resultat" -> "utfall"),
- a cosmetically different opening hook with the same underlying shape,
- formatting/line-break differences,
- a different CTA or signature.

`tests/test_v1c_paths.py::test_false_variation_path_detects_cosmetic_only_difference`
demonstrates this directly: two sentences sharing zero words in common
but an identical structural shape are correctly flagged `TOO_SIMILAR`.

## What this is NOT

An analysis judgment, never a generator rule. V1C never rewrites, blocks,
or "fixes" a false-variation pair -- it reports the category and the
named dimensions that are identical, and leaves the decision to whatever
consumes the result (ultimately a human, via Human Variation Decision).
`ControlledVariationOption.false_variation` is populated on every option
V1C proposes, so a human reviewing options can see this risk assessment
per option, not just as a pass/fail gate.

## Relationship to Controlled Variation Options

`variation/options.py::generate_controlled_variation_options()` only ever
proposes options that change at least one real OBSERVED dimension while
holding the rest stable -- by construction, a single such change is never
itself false variation relative to the original angle (order section 23's
"stable_dimensions" is the intended design, not an accident to guard
against). `false_variation` on an option instead describes its
relationship to the CLOSEST relevant memory profile: if the option would
still land `TOO_SIMILAR` to existing material even after the change, that
is surfaced honestly rather than hidden.
