"""
V1C Structural Comparison, False Variation, and Multi-Axis Repetition
(order sections 15-21).

No embedding, no vector database, no similarity model (order section 21,
34) -- comparison is a plain field-by-field diff over the six OBSERVED
dimensions (order section 28: hypothesis dimensions never decide this
alone). Every result names exactly which dimensions matched and which
differed.
"""

from __future__ import annotations

from engine.models import ConfidenceLevel

from .models import (
    OBSERVED_DIMENSIONS,
    DimensionAssessment,
    DimensionComparison,
    FalseVariationAssessment,
    MovementSimilarityCategory,
    MultiAxisRepetitionResult,
    RepetitionAxis,
    RepetitionAxisAssessment,
    StructuralComparisonResult,
    StructuralMovementAssessment,
    StructuralMovementComparisonResult,
    VariationDistanceCategory,
    VariationProfile,
)

MIN_KNOWN_DIMENSIONS_FOR_COMPARISON = 4
"""If fewer than this many of the six OBSERVED dimensions are known (not
'unknown') on EITHER profile, the comparison itself is INSUFFICIENT_EVIDENCE
-- order section 18/25: refuse rather than force a category onto thin evidence."""

_MOVEMENT_STRONGLY_SIMILAR_RATIO = 0.75
_MOVEMENT_PARTIALLY_SIMILAR_RATIO = 0.34
"""order section 12 (V1C Correction): thresholds over a plain positional
match ratio -- transparent and explainable, not a fabricated precise score
(order section 12's own "Ingen falsk exakt similarity score")."""

_NON_MOVEMENT_OBSERVED_DIMENSIONS = tuple(d for d in OBSERVED_DIMENSIONS if d != "structural_arc")
"""order section 7 (V1C Correction 2): entry_mode, lens, narrative_distance,
rhetorical_pressure, closure_mode -- the five dimensions still compared by
naive keyword-derived value, structural_arc excluded since its "same" slot
is always movement-derived (see `compare_variation_profiles()`). Used for
the flat six-slot `same_count`/`overall` contract -- unchanged in meaning
from V1C Correction 1, still what `NO_MEANINGFUL_VARIATION`, options
ranking, and the multi-axis STRUCTURAL axis all read."""

_CONSTRUCTION_CORROBORATION_DIMENSIONS = tuple(d for d in _NON_MOVEMENT_OBSERVED_DIMENSIONS if d != "lens")
"""order section 6 (V1C Correction 2): entry_mode, narrative_distance,
rhetorical_pressure, closure_mode -- the subset of construction dimensions
`_false_variation_verdict()` treats as corroborating/contradicting
evidence. `lens` is deliberately excluded here (though still part of the
flat six-slot comparison above): it is derived from a single
topic-keyword match (ansvar/makt/konsekvens/relation/...) and reflects
THEME, not editorial CONSTRUCTION -- order section 14's own "Thesis
similarity ≠ Structural repetition" extends to lens, which is
thesis-adjacent. Empirically, letting a shared topic keyword alone
corroborate a weak movement signal produced false positives (two
`ansvar`-themed texts with a genuinely different construction reading as
False Variation) that a genuinely structural match (closure_mode,
narrative_distance, entry_mode, rhetorical_pressure) did not."""


def _dimension_match_is_evidence(a: DimensionAssessment, b: DimensionAssessment) -> bool:
    """order section 7 (V1C Correction 2), the short-text false-positive
    fix: 'UNKNOWN == UNKNOWN' and 'default == default' must NOT count as
    positive similarity evidence. Every dimension's own fallback branch
    (`entry_mode='claim'`, `narrative_distance='observer'`,
    `rhetorical_pressure='quiet_observation'`, `closure_mode='still_statement'`)
    is *always* assigned `ConfidenceLevel.LOW` by construction (see
    `profiler.py`) -- exactly the mechanism that let two unrelated short
    texts coincidentally share five low-confidence defaults and read as
    TOO_SIMILAR (documented in `V1C_AUDIT_REPORT.md`, still open after
    V1C Correction 1). A value match only counts as real evidence of
    similarity when it is known on both sides AND at least one side
    reached that value with more than LOW confidence -- i.e. a genuine
    detected signal, not two coincidental fallbacks. A genuine DIFFERENCE
    is always real evidence regardless of confidence -- only MATCHES need
    this extra scrutiny."""

    if a.value != b.value:
        return False
    if a.value == "unknown":
        return False
    if a.confidence == ConfidenceLevel.LOW and b.confidence == ConfidenceLevel.LOW:
        return False
    return True


def _dimension_diff_is_evidence(a: DimensionAssessment, b: DimensionAssessment) -> bool:
    """order section 7 (V1C Correction 2): the mirror image of
    `_dimension_match_is_evidence()`. A dimension only counts as genuine
    evidence of DIFFERENCE when both sides are known, differ, AND neither
    side is a LOW-confidence default fallback -- a default value (e.g.
    `entry_mode='claim'`, always assigned whenever no stronger signal
    fired) disagreeing with a confidently-detected value on the other side
    is not confident evidence the construction actually diverges there; it
    may simply mean this dimension's heuristic found nothing on one side."""

    if a.value == b.value:
        return False
    if a.value == "unknown" or b.value == "unknown":
        return False
    if a.confidence == ConfidenceLevel.LOW or b.confidence == ConfidenceLevel.LOW:
        return False
    return True


def _longest_common_subsequence_length(a: list[str], b: list[str]) -> int:
    """order section 12 (V1C Correction): order-preserving but
    insertion/deletion-tolerant comparison -- a hook inserted at the start,
    or one extra step in the middle, must not throw off an otherwise
    matching movement sequence (a rigid position-by-position compare
    would). Still a small, exact, explainable count -- not a fabricated
    similarity score (order's own "Ingen falsk exakt similarity score")."""

    dp = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    return dp[len(a)][len(b)]


def compare_structural_movements(
    a: StructuralMovementAssessment, b: StructuralMovementAssessment, profile_a_id: str, profile_b_id: str,
) -> StructuralMovementComparisonResult:
    """order section 12 (V1C Correction), the central fix: compares the
    OBSERVED SEQUENCE of movements, position by position, not a single
    derived label. Two texts sharing the same entry_mode/closure_mode can
    now land STRUCTURALLY_DISTINCT here if their middle differs (order
    section 5-6 of the audit); two texts with different entry_mode can
    still land STRONGLY_SIMILAR if the rest of the journey matches (order
    section 28.C)."""

    seq_a = a.known_stage_sequence()
    seq_b = b.known_stage_sequence()

    if not a.sufficient_evidence or not b.sufficient_evidence or not seq_a or not seq_b:
        return StructuralMovementComparisonResult(
            profile_a_id=profile_a_id, profile_b_id=profile_b_id,
            profile_a_sequence=seq_a, profile_b_sequence=seq_b,
            matched_positions=0, compared_length=0,
            category=MovementSimilarityCategory.INSUFFICIENT_EVIDENCE,
            rationale="Otillrackligt observerad rorelsesekvens pa endera profilen (kravs minst 3 meningar text) -- kan inte bedoma rorelselikhet.",
        )

    matched = _longest_common_subsequence_length(seq_a, seq_b)
    compared_length = min(len(seq_a), len(seq_b))
    coverage_denominator = max(len(seq_a), len(seq_b))
    """order section 8 (V1C Correction 2), the asymmetric-sequence fix: the
    OLD ratio was `matched / min(len_a, len_b)` -- which is mathematically
    just "how much of the SHORTER sequence is covered", and hits 1.0
    (falsely STRONGLY_SIMILAR) whenever a short sequence happens to be a
    subsequence of a much longer one, even though the longer sequence's
    remainder (a genuinely different continuation) is never weighed at
    all. The new ratio divides by the LONGER sequence's length instead,
    so an unmatched tail on either side pulls the ratio down -- coverage
    of BOTH journeys, not just the shorter one."""

    ratio = matched / coverage_denominator if coverage_denominator else 0.0
    if ratio >= _MOVEMENT_STRONGLY_SIMILAR_RATIO:
        category = MovementSimilarityCategory.STRONGLY_SIMILAR
    elif ratio >= _MOVEMENT_PARTIALLY_SIMILAR_RATIO:
        category = MovementSimilarityCategory.PARTIALLY_SIMILAR
    else:
        category = MovementSimilarityCategory.STRUCTURALLY_DISTINCT

    return StructuralMovementComparisonResult(
        profile_a_id=profile_a_id, profile_b_id=profile_b_id,
        profile_a_sequence=seq_a, profile_b_sequence=seq_b,
        matched_positions=matched, compared_length=compared_length, category=category,
        rationale=(
            f"{matched}/{coverage_denominator} rorelsesteg (av den langre sekvensen) ingar i en gemensam delsekvens, "
            f"i samma inbordes ordning ({seq_a} mot {seq_b})."
        ),
    )


def category_for_value_dicts(
    a_values: dict[str, str], b_values: dict[str, str], structural_arc_same_override: bool | None = None,
) -> tuple[VariationDistanceCategory, int, int]:
    """Shared threshold logic, reused by `compare_variation_profiles()` (real
    profile-to-profile) and `variation/options.py` (hypothetical hand-edited
    value dicts, before any VariationProfile object is built for them).

    `structural_arc_same_override` (V1C Correction, order section 12): when
    given, the "structural_arc" dimension slot's same/different verdict is
    taken from this (movement-sequence-based) value instead of naive label
    equality -- naive label equality on a single derived arc string is
    exactly the mechanism the audit found produced both false positives and
    false negatives (audit sections 5-6, 8). When `None` (the default,
    used for hypothetical option value-dicts that have no recomputed
    movement sequence of their own), falls back to plain equality."""

    a_known = sum(1 for v in a_values.values() if v != "unknown")
    b_known = sum(1 for v in b_values.values() if v != "unknown")

    same_count = 0
    for dim in OBSERVED_DIMENSIONS:
        if dim == "structural_arc" and structural_arc_same_override is not None:
            same = structural_arc_same_override
        else:
            same = a_values[dim] == b_values[dim]
        same_count += int(same)

    if a_known < MIN_KNOWN_DIMENSIONS_FOR_COMPARISON or b_known < MIN_KNOWN_DIMENSIONS_FOR_COMPARISON:
        category = VariationDistanceCategory.INSUFFICIENT_EVIDENCE
    elif same_count >= 5:
        category = VariationDistanceCategory.TOO_SIMILAR
    elif same_count >= 3:
        category = VariationDistanceCategory.PARTIALLY_DISTINCT
    else:
        category = VariationDistanceCategory.STRUCTURALLY_DISTINCT
    return category, same_count, len(OBSERVED_DIMENSIONS) - same_count


def compare_variation_profiles(a: VariationProfile, b: VariationProfile) -> StructuralComparisonResult:
    """order section 7 (V1C Correction 2): the "same" verdict for the five
    non-movement OBSERVED dimensions is now evidence-aware
    (`_dimension_match_is_evidence()`) instead of naive value equality --
    two coincidental low-confidence defaults no longer count as a match.
    `structural_arc`'s slot remains movement-derived (V1C Correction 1)."""

    a_values = a.observed_values()
    b_values = b.observed_values()

    movement_comparison = compare_structural_movements(a.structural_movement, b.structural_movement, a.profile_id, b.profile_id)
    structural_arc_same = movement_comparison.category == MovementSimilarityCategory.STRONGLY_SIMILAR

    comparisons = [
        DimensionComparison(
            dimension=dim, profile_a_value=a_values[dim], profile_b_value=b_values[dim],
            same=(structural_arc_same if dim == "structural_arc" else _dimension_match_is_evidence(getattr(a, dim), getattr(b, dim))),
        )
        for dim in OBSERVED_DIMENSIONS
    ]
    same_count = sum(1 for c in comparisons if c.same)
    different_count = len(OBSERVED_DIMENSIONS) - same_count

    a_known = sum(1 for v in a_values.values() if v != "unknown")
    b_known = sum(1 for v in b_values.values() if v != "unknown")
    if a_known < MIN_KNOWN_DIMENSIONS_FOR_COMPARISON or b_known < MIN_KNOWN_DIMENSIONS_FOR_COMPARISON:
        overall = VariationDistanceCategory.INSUFFICIENT_EVIDENCE
    elif same_count >= 5:
        overall = VariationDistanceCategory.TOO_SIMILAR
    elif same_count >= 3:
        overall = VariationDistanceCategory.PARTIALLY_DISTINCT
    else:
        overall = VariationDistanceCategory.STRUCTURALLY_DISTINCT

    return StructuralComparisonResult(
        profile_a_id=a.profile_id, profile_b_id=b.profile_id,
        dimension_comparisons=comparisons, same_count=same_count, different_count=different_count, overall=overall,
        movement_comparison=movement_comparison,
    )


def _false_variation_verdict(
    flat_category: VariationDistanceCategory,
    movement_category: MovementSimilarityCategory,
    movement_matched_positions: int,
    n_same_construction_dims: int,
    n_diff_construction_dims: int,
) -> tuple[bool, str]:
    """order section 6, 15 (V1C Correction 2), the second blocker's actual
    fix: False Variation reasons over a COMBINATION of evidence -- the
    observed movement sequence and however many of the five construction
    dimensions (entry_mode, lens, narrative_distance, rhetorical_pressure,
    closure_mode) genuinely corroborate (order section 6's "väga samman
    relevant evidens"), never a single narrow requirement. `n_same_*`/
    `n_diff_*` already exclude UNKNOWN/default-coincidence evidence on
    BOTH the match side (`_dimension_match_is_evidence()`) and the
    difference side (a LOW-confidence default value on either side is not
    treated as confident evidence of a genuine difference either -- order
    section 7's "frånvaro av information är inte likhet" cuts both ways).

    Root cause this replaces (see V1C_FALSE_VARIATION_CORRECTION_2_REPORT.md):
    V1C Correction 1 required movement to be STRONGLY_SIMILAR specifically,
    corroborated by exactly one of two named dimensions. Realistic
    out-of-vocabulary paraphrase (the Evidence Pack's own D1-D3) routinely
    collapses the movement sequence to a single generic step on one side,
    which can never reach STRONGLY_SIMILAR (and often not even
    PARTIALLY_SIMILAR) under any ratio -- so genuine repetition was missed
    even when other construction dimensions still agreed and nothing
    genuinely contradicted. This version lets a large enough
    construction-dimension majority stand on its own, lets a
    PARTIALLY_SIMILAR movement count when corroborated by at least one
    dimension, and lets even a weak (STRUCTURALLY_DISTINCT-level) but
    non-zero movement overlap count when there IS at least one genuine
    corroborating dimension and at most one genuine contradicting one --
    while still refusing to decide on thin/insufficient evidence."""

    if flat_category == VariationDistanceCategory.TOO_SIMILAR:
        # Already confidently TOO_SIMILAR on the flat six-slot count -- an
        # inconclusive movement comparison does not un-confirm a solid verdict.
        return True, "flat_too_similar"
    if flat_category == VariationDistanceCategory.INSUFFICIENT_EVIDENCE and movement_category == MovementSimilarityCategory.INSUFFICIENT_EVIDENCE:
        # Neither the construction dimensions nor the movement sequence carry
        # enough real evidence -- refuse to guess (order section 7's "Frånvaro
        # av information är inte likhet" extends to refusing a verdict too).
        return False, "insufficient_evidence"
    if movement_category == MovementSimilarityCategory.STRONGLY_SIMILAR and n_diff_construction_dims <= 1:
        return True, "movement_strongly_corroborated"
    if movement_category in (MovementSimilarityCategory.STRONGLY_SIMILAR, MovementSimilarityCategory.PARTIALLY_SIMILAR) and n_same_construction_dims >= 2:
        return True, "movement_partially_corroborated"
    if movement_category in (MovementSimilarityCategory.STRONGLY_SIMILAR, MovementSimilarityCategory.PARTIALLY_SIMILAR) and n_diff_construction_dims == 0:
        # A genuine, substantial (>= 34% coverage of the longer sequence)
        # movement match, with nothing else confidently contradicting it,
        # stands on its own -- order section 6's "structural movement
        # sequence ska vara primär evidens": the construction dimensions
        # may simply have too little confident signal on this particular
        # pair (e.g. every match happened to be a low-confidence default,
        # every difference happened to involve one), which is an absence
        # of counter-evidence, not evidence against.
        return True, "movement_uncontradicted"
    if movement_matched_positions >= 1 and n_same_construction_dims >= 1 and n_diff_construction_dims <= 1:
        # Weak movement overlap (not enough alone to reach even
        # PARTIALLY_SIMILAR, typically because one side's sequence
        # under-classified to a short/generic reading) still counts when
        # it is genuinely uncontradicted: at least one independent
        # construction signal agrees, and at most one disagrees.
        return True, "weakly_corroborated"
    if n_same_construction_dims >= 4:
        # Overwhelming construction-dimension agreement even without a
        # confident movement read -- e.g. movement itself was inconclusive
        # but four of five other real (non-default) signals agree.
        return True, "construction_majority"
    return False, "distinct"


def assess_false_variation(a: VariationProfile, b: VariationProfile) -> FalseVariationAssessment:
    """order section 17: two treatments are FALSE VARIATION when their
    structural profile is identical (or near-identical) -- a difference
    that exists only in surface wording is invisible to this comparison by
    construction, since it never looks at raw words, only at the OBSERVED
    structural dimensions plus the observed movement sequence, combined
    as evidence (order section 6/15, V1C Correction 2)."""

    result = compare_variation_profiles(a, b)
    identical = [c.dimension for c in result.dimension_comparisons if c.same]
    changed = [c.dimension for c in result.dimension_comparisons if not c.same]

    construction_same = [d for d in identical if d in _CONSTRUCTION_CORROBORATION_DIMENSIONS]
    construction_diff = [d for d in _CONSTRUCTION_CORROBORATION_DIMENSIONS if _dimension_diff_is_evidence(getattr(a, d), getattr(b, d))]
    is_false, reason = _false_variation_verdict(
        result.overall, result.movement_comparison.category, result.movement_comparison.matched_positions,
        len(construction_same), len(construction_diff),
    )

    if reason == "insufficient_evidence":
        rationale = "For fa kanda/genuint sakra dimensioner eller for kort observerad rorelsesekvens pa endera profilen for att avgora -- INSUFFICIENT_EVIDENCE, inte falsk variation per automatik."
    elif reason in ("movement_strongly_corroborated", "movement_partially_corroborated", "movement_uncontradicted", "weakly_corroborated"):
        rationale = (
            f"Rorelsesekvensen ar {result.movement_comparison.category.value} ({result.movement_comparison.rationale}) och "
            f"{len(construction_same)} av {len(_CONSTRUCTION_CORROBORATION_DIMENSIONS)} konstruktionsdimensioner ({', '.join(construction_same) or 'inga'}) "
            f"bekraftar oberoende -- redaktionell konstruktion bestar aven om ytliga nyckelord skiljer sig i {', '.join(construction_diff) or 'inga andra dimensioner'}."
        )
    elif reason == "construction_majority":
        rationale = (
            f"{len(construction_same)} av {len(_CONSTRUCTION_CORROBORATION_DIMENSIONS)} konstruktionsdimensioner ar genuint (ej standardvarde-) lika "
            f"({', '.join(construction_same)}) -- overvagande bevis for samma redaktionella konstruktion."
        )
    elif is_false:
        rationale = (
            f"{len(identical)} av {len(OBSERVED_DIMENSIONS)} OBSERVED-dimensioner ar identiska "
            f"({', '.join(identical)}) -- for likt for att rakna som genuin strukturell variation."
        )
    else:
        rationale = f"{len(changed)} av {len(OBSERVED_DIMENSIONS)} OBSERVED-dimensioner skiljer sig ({', '.join(changed)}) -- genuin strukturell skillnad."

    return FalseVariationAssessment(is_false_variation=is_false, rationale=rationale, identical_dimensions=identical, changed_dimensions=changed)


def assess_multi_axis_repetition(
    same_thesis_family: bool,
    same_angle_core_terms: bool,
    structural_comparison: StructuralComparisonResult,
    lexical_overlap_terms: list[str],
) -> MultiAxisRepetitionResult:
    """order section 19-20: six axes kept explicitly separate. Lexical overlap
    alone (V1B's own signal) never becomes an automatic STRUCTURAL verdict --
    structural repetition is decided ONLY from `structural_comparison`, never
    from `lexical_overlap_terms`."""

    assessments: list[RepetitionAxisAssessment] = []

    assessments.append(
        RepetitionAxisAssessment(
            axis=RepetitionAxis.THESIS, detected=same_thesis_family,
            rationale="Delad canonical Thesis Family." if same_thesis_family else "Ingen delad Thesis Family.",
        )
    )
    assessments.append(
        RepetitionAxisAssessment(
            axis=RepetitionAxis.ANGLE, detected=same_angle_core_terms,
            rationale="Angle-kärnan uttrycker samma redaktionella grepp." if same_angle_core_terms else "Angle-kärnan skiljer sig.",
        )
    )

    structural_detected = structural_comparison.overall == VariationDistanceCategory.TOO_SIMILAR
    assessments.append(
        RepetitionAxisAssessment(
            axis=RepetitionAxis.STRUCTURAL, detected=structural_detected,
            rationale=f"Strukturell jamforelse: {structural_comparison.overall.value} ({structural_comparison.same_count}/{len(OBSERVED_DIMENSIONS)} dimensioner lika).",
        )
    )

    opening_comparison = next((c for c in structural_comparison.dimension_comparisons if c.dimension == "entry_mode"), None)
    opening_detected = bool(opening_comparison and opening_comparison.same and opening_comparison.profile_a_value != "unknown")
    assessments.append(
        RepetitionAxisAssessment(
            axis=RepetitionAxis.OPENING, detected=opening_detected,
            rationale=f"entry_mode {'delas' if opening_detected else 'skiljer sig eller ar okant'}.",
        )
    )

    ending_comparison = next((c for c in structural_comparison.dimension_comparisons if c.dimension == "closure_mode"), None)
    ending_detected = bool(ending_comparison and ending_comparison.same and ending_comparison.profile_a_value != "unknown")
    assessments.append(
        RepetitionAxisAssessment(
            axis=RepetitionAxis.ENDING, detected=ending_detected,
            rationale=f"closure_mode {'delas' if ending_detected else 'skiljer sig eller ar okant'}.",
        )
    )

    assessments.append(
        RepetitionAxisAssessment(
            axis=RepetitionAxis.LEXICAL, detected=bool(lexical_overlap_terms),
            rationale=(f"Delade ord: {lexical_overlap_terms}." if lexical_overlap_terms else "Ingen ordoverlappning.")
            + " Detta axel paverkar INTE structural-axeln -- de halls medvetet atskilda (order sektion 20).",
        )
    )

    return MultiAxisRepetitionResult(assessments=assessments)
