"""
The V1C vertical chain (order section 3, 38):

    Selected Angle -> Variation Analysis -> Memory Structural Comparison
    -> Controlled Variation Options -> Recommended Variation
    -> [Human Variation Decision, called separately -- see human_decision.py]

Reuses V1A/V1B directly: `run_v1c_variation_analysis()` takes an already
V1A/V1B-produced `CandidateAngle` and a list of Editorial Memory records
(normally the FULL-text records V1B's own comparison found relevant) and
adds ONLY the new analysis layer. Nothing in `engine/` or `memory/` is
imported for modification -- only for reuse.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from engine.models import CandidateAngle
from memory.models import EditorialMemoryRecord, TextCompleteness

from .comparison import assess_multi_axis_repetition, compare_variation_profiles
from .models import (
    MovementSimilarityCategory,
    MultiAxisRepetitionResult,
    SourceKind,
    StructuralComparisonResult,
    StructuralMovementComparisonResult,
    VariationDistanceCategory,
    VariationProfile,
    VariationRecommendationResult,
)
from .options import generate_controlled_variation_options
from .profiler import build_variation_profile, build_variation_profile_for_memory_record


class V1CVariationResult(BaseModel):
    """Full, inspectable trace of one V1C run -- mirrors V1A/V1B's own
    `V1APipelineResult`/`V1BPipelineResult` discipline of keeping every
    intermediate step visible, not just the final recommendation."""

    model_config = {"extra": "forbid", "arbitrary_types_allowed": True}

    angle_id: str
    angle_profile: VariationProfile
    relevant_memory_profiles: list[VariationProfile] = Field(default_factory=list)
    structural_comparisons: list[StructuralComparisonResult] = Field(default_factory=list)
    repetition: MultiAxisRepetitionResult
    recommendation: VariationRecommendationResult


def run_v1c_variation_analysis(
    candidate_angle: CandidateAngle,
    relevant_memory_records: list[EditorialMemoryRecord],
    same_thesis_family: bool = False,
    lexical_overlap_terms: list[str] | None = None,
) -> V1CVariationResult:
    """`relevant_memory_records` should be whatever FULL-text records V1B's own
    comparison already flagged as relevant to the selected angle (order
    section 10/20) -- PARTIAL records are silently skipped here, not used as
    if they were structurally analyzable (order section 10)."""

    angle_text = " ".join(filter(None, [candidate_angle.core, candidate_angle.why_relevant, candidate_angle.differentiation]))
    angle_profile = build_variation_profile(
        text=angle_text, source_id=candidate_angle.angle.angle_id, source_kind=SourceKind.CANDIDATE_ANGLE,
    )

    full_records = [r for r in relevant_memory_records if r.source_facts.text_completeness == TextCompleteness.FULL]
    memory_profiles = [build_variation_profile_for_memory_record(r) for r in full_records]

    structural_comparisons = [compare_variation_profiles(angle_profile, mp) for mp in memory_profiles]

    same_angle_core_terms = any(
        c.same_count >= 5 for c in structural_comparisons
    )  # order section 19: angle-level repetition is judged structurally here, never from raw word overlap alone

    if structural_comparisons:
        closest_comparison = max(structural_comparisons, key=lambda c: c.same_count)
    else:
        # No relevant memory to compare against -- explicitly NOT a self-comparison
        # (which would trivially and falsely read as TOO_SIMILAR/repetitive).
        closest_comparison = StructuralComparisonResult(
            profile_a_id=angle_profile.profile_id, profile_b_id="", dimension_comparisons=[],
            same_count=0, different_count=0, overall=VariationDistanceCategory.INSUFFICIENT_EVIDENCE,
            movement_comparison=StructuralMovementComparisonResult(
                profile_a_id=angle_profile.profile_id, profile_b_id="",
                profile_a_sequence=angle_profile.structural_movement.known_stage_sequence(), profile_b_sequence=[],
                matched_positions=0, compared_length=0, category=MovementSimilarityCategory.INSUFFICIENT_EVIDENCE,
                rationale="Inget relevant memory att jamfora rorelsesekvens mot.",
            ),
        )

    repetition = assess_multi_axis_repetition(
        same_thesis_family=same_thesis_family,
        same_angle_core_terms=same_angle_core_terms,
        structural_comparison=closest_comparison,
        lexical_overlap_terms=lexical_overlap_terms or [],
    )

    recommendation = generate_controlled_variation_options(
        angle_id=candidate_angle.angle.angle_id, angle_profile=angle_profile, relevant_memory_profiles=memory_profiles,
    )

    return V1CVariationResult(
        angle_id=candidate_angle.angle.angle_id,
        angle_profile=angle_profile,
        relevant_memory_profiles=memory_profiles,
        structural_comparisons=structural_comparisons,
        repetition=repetition,
        recommendation=recommendation,
    )
