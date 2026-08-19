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
    MultiAxisRepetitionResult,
    RepetitionAxis,
    RepetitionAxisAssessment,
    StructuralComparisonResult,
    VariationDistanceCategory,
    VariationProfile,
)

MIN_KNOWN_DIMENSIONS_FOR_COMPARISON = 4
"""If fewer than this many of the six OBSERVED dimensions are known (not
'unknown') on EITHER profile, the comparison itself is INSUFFICIENT_EVIDENCE
-- order section 18/25: refuse rather than force a category onto thin evidence."""


def category_for_value_dicts(a_values: dict[str, str], b_values: dict[str, str]) -> tuple[VariationDistanceCategory, int, int]:
    """Shared threshold logic, reused by `compare_variation_profiles()` (real
    profile-to-profile) and `variation/options.py` (hypothetical hand-edited
    value dicts, before any VariationProfile object is built for them)."""

    a_known = sum(1 for v in a_values.values() if v != "unknown")
    b_known = sum(1 for v in b_values.values() if v != "unknown")
    same_count = sum(1 for dim in OBSERVED_DIMENSIONS if a_values[dim] == b_values[dim])

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

    comparisons = [
        DimensionComparison(dimension=dim, profile_a_value=a_values[dim], profile_b_value=b_values[dim], same=a_values[dim] == b_values[dim])
        for dim in OBSERVED_DIMENSIONS
    ]
    overall, same_count, different_count = category_for_value_dicts(a_values, b_values)

    return StructuralComparisonResult(
        profile_a_id=a.profile_id, profile_b_id=b.profile_id,
        dimension_comparisons=comparisons, same_count=same_count, different_count=different_count, overall=overall,
    )


def assess_false_variation(a: VariationProfile, b: VariationProfile) -> FalseVariationAssessment:
    """order section 17: two treatments are FALSE VARIATION when their
    structural profile is identical (or near-identical) -- a difference
    that exists only in surface wording is invisible to this comparison by
    construction, since it never looks at raw words, only at the six
    OBSERVED structural dimensions."""

    result = compare_variation_profiles(a, b)
    identical = [c.dimension for c in result.dimension_comparisons if c.same]
    changed = [c.dimension for c in result.dimension_comparisons if not c.same]

    is_false = result.overall == VariationDistanceCategory.TOO_SIMILAR
    if result.overall == VariationDistanceCategory.INSUFFICIENT_EVIDENCE:
        rationale = "For fa kanda dimensioner pa endera profilen for att avgora -- INSUFFICIENT_EVIDENCE, inte falsk variation per automatik."
        is_false = False
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
