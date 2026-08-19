# V1C Purpose

**PROTOTYPE, NOT A CANONICAL VARIATION MODEL.** Work's Variation
Foundation report concluded the available 21-text corpus (12 full, 3
English) is sufficient to prototype and test controlled variation
analysis, but not sufficient to freeze a general or canonical variation
model. Project leadership approved that conclusion. V1C respects it: it
proves a mechanism, not a taxonomy.

## What V1C proves

> Kan systemet analysera hur en vald redaktionell vinkel skiljer sig
> strukturellt fran tidigare LUF-material och foresla kontrollerade
> variationsalternativ utan att skriva sjalva texten?

Concretely: given a V1A/V1B-selected `CandidateAngle`, V1C (1) builds a
`VariationProfile` describing how that angle's own analysis text is
structurally shaped across six dimensions, (2) compares that profile
against relevant Editorial Memory, (3) proposes up to three
`ControlledVariationOption`s -- named dimension changes, never text -- and
(4) leaves the decision to a human.

## Chain extension

```
Raw Idea -> Interpretation -> Canonical Classification ->
Editorial Memory Retrieval -> Existing Content Comparison ->
Candidate Angles -> Recommended Angle -> Human Decision ->
Variation Analysis -> Controlled Variation Options ->
Human Variation Decision
```

Everything before "Variation Analysis" is V1A/V1B, untouched. V1C adds
exactly the last three steps, reusing the rest by import, never by
rewrite (see `docs/V1C_DOES_NOT_DO.md`).

## Why "prototype" is a hard constraint here, not a hedge

Work's own evidence-status split (order section 5) means six of the nine
candidate dimensions are OBSERVED, two are SUPPORTED HYPOTHESIS, and one
(Sustained Narrative Form) is EXPLORATORY. V1C encodes that split as data
(`variation/models.py::DIMENSION_EVIDENCE_STATUS`), not just as
documentation, and structurally refuses to let a hypothesis-level
dimension decide anything on its own (see
`docs/V1C_VARIATION_BOUNDARY.md`). Sustained Narrative Form has no code
at all in `variation/`.
