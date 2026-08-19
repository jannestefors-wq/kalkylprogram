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

from .models import (
    OBSERVED_DIMENSIONS,
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

    compared_length = min(len(seq_a), len(seq_b))
    matched = _longest_common_subsequence_length(seq_a, seq_b)

    if compared_length < 2:
        # A single shared (often generic) step is too little evidence for a
        # firm similarity claim -- order section 12/25's "ingen falsk
        # precision" extends to movement comparison too.
        return StructuralMovementComparisonResult(
            profile_a_id=profile_a_id, profile_b_id=profile_b_id,
            profile_a_sequence=seq_a, profile_b_sequence=seq_b,
            matched_positions=matched, compared_length=compared_length,
            category=MovementSimilarityCategory.INSUFFICIENT_EVIDENCE,
            rationale=f"Endast {compared_length} jamforbart rorelsesteg pa den kortare sekvensen -- for lite for att bedoma rorelselikhet med rimlig sakerhet.",
        )

    ratio = matched / compared_length
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
        rationale=f"{matched}/{compared_length} rorelsesteg ingar i en gemensam delsekvens, i samma inbordes ordning ({seq_a} mot {seq_b}).",
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
    a_values = a.observed_values()
    b_values = b.observed_values()

    movement_comparison = compare_structural_movements(a.structural_movement, b.structural_movement, a.profile_id, b.profile_id)
    structural_arc_same = movement_comparison.category == MovementSimilarityCategory.STRONGLY_SIMILAR

    comparisons = [
        DimensionComparison(
            dimension=dim, profile_a_value=a_values[dim], profile_b_value=b_values[dim],
            same=(structural_arc_same if dim == "structural_arc" else a_values[dim] == b_values[dim]),
        )
        for dim in OBSERVED_DIMENSIONS
    ]
    overall, same_count, different_count = category_for_value_dicts(a_values, b_values, structural_arc_same_override=structural_arc_same)

    return StructuralComparisonResult(
        profile_a_id=a.profile_id, profile_b_id=b.profile_id,
        dimension_comparisons=comparisons, same_count=same_count, different_count=different_count, overall=overall,
        movement_comparison=movement_comparison,
    )


def _corroborated_false_variation_verdict(
    flat_category: VariationDistanceCategory, movement_category: MovementSimilarityCategory, lens_same: bool, narrative_distance_same: bool,
) -> tuple[bool, str]:
    """order section 15 (V1C Correction), the second blocker's actual fix:
    False Variation may NOT be decided by keywords alone (order: "keywords
    far inte ensamma bara beslutet"). A synonym-heavy rewrite can break
    entry_mode's/closure_mode's individual keyword triggers while the
    editorial CONSTRUCTION -- the movement sequence, the lens, the human
    situation -- stays intact. When the movement sequence is itself
    STRONGLY_SIMILAR and at least one other corroborating signal (lens or
    narrative_distance) also matches, that is treated as sufficient
    evidence of False Variation even if the flat six-dimension count falls
    short of TOO_SIMILAR -- exactly the order's "Om dessa i huvudsak
    bestar kan text B fortfarande vara False Variation av text A."
    Returns (is_false_variation, reason_code) for rationale text."""

    if flat_category == VariationDistanceCategory.TOO_SIMILAR:
        # Already confidently TOO_SIMILAR on the flat six-dimension count --
        # an inconclusive movement comparison (e.g. too little text for a
        # reliable movement read) does not un-confirm an otherwise solid
        # verdict.
        return True, "flat_too_similar"
    if flat_category == VariationDistanceCategory.INSUFFICIENT_EVIDENCE or movement_category == MovementSimilarityCategory.INSUFFICIENT_EVIDENCE:
        return False, "insufficient_evidence"
    if movement_category == MovementSimilarityCategory.STRONGLY_SIMILAR and (lens_same or narrative_distance_same):
        return True, "movement_corroborated"
    return False, "distinct"


def assess_false_variation(a: VariationProfile, b: VariationProfile) -> FalseVariationAssessment:
    """order section 17: two treatments are FALSE VARIATION when their
    structural profile is identical (or near-identical) -- a difference
    that exists only in surface wording is invisible to this comparison by
    construction, since it never looks at raw words, only at the six
    OBSERVED structural dimensions plus the observed movement sequence
    (order section 15, V1C Correction)."""

    result = compare_variation_profiles(a, b)
    identical = [c.dimension for c in result.dimension_comparisons if c.same]
    changed = [c.dimension for c in result.dimension_comparisons if not c.same]

    lens_same = a.lens.value == b.lens.value and a.lens.value != "unknown"
    distance_same = a.narrative_distance.value == b.narrative_distance.value and a.narrative_distance.value != "unknown"
    is_false, reason = _corroborated_false_variation_verdict(result.overall, result.movement_comparison.category, lens_same, distance_same)

    if reason == "insufficient_evidence":
        rationale = "For fa kanda dimensioner eller for kort observerad rorelsesekvens pa endera profilen for att avgora -- INSUFFICIENT_EVIDENCE, inte falsk variation per automatik."
    elif reason == "movement_corroborated":
        rationale = (
            f"Rorelsesekvensen ar {result.movement_comparison.category.value} ({result.movement_comparison.rationale}) och "
            f"{'lens' if lens_same else 'narrative_distance'} delas -- redaktionell konstruktion bestar aven om ytliga nyckelord "
            f"skiljer sig i {', '.join(changed) or 'inga andra dimensioner'}."
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
