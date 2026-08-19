"""
V1C Controlled Variation Options (order sections 22-25).

Never text. A `ControlledVariationOption` describes WHICH OBSERVED
dimensions would change and which stay stable -- a plan for possible
expression variation, not the expression itself (order section 22, 32).

Deterministic, small, and transparent: for each candidate dimension swap,
the SAME single next value is always chosen (order section 12's own
"avstaende battre an falsk precision" extends here -- no random choice,
no hidden scoring). At most `MAX_CONTROLLED_VARIATION_OPTIONS`.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from schema import Provenance
from schema.enums import Actor, EvidenceCertainty

from engine.models import ConfidenceLevel

from .comparison import MIN_KNOWN_DIMENSIONS_FOR_COMPARISON, category_for_value_dicts, compare_variation_profiles
from .models import (
    MAX_CONTROLLED_VARIATION_OPTIONS,
    OBSERVED_DIMENSIONS,
    ClosureMode,
    ControlledVariationOption,
    EntryMode,
    FalseVariationAssessment,
    Lens,
    NarrativeDistance,
    RhetoricalPressure,
    StructuralArc,
    VariationDistanceCategory,
    VariationProfile,
    VariationRecommendationOutcome,
    VariationRecommendationResult,
)

_DIMENSION_ENUMS = {
    "entry_mode": EntryMode,
    "lens": Lens,
    "narrative_distance": NarrativeDistance,
    "structural_arc": StructuralArc,
    "rhetorical_pressure": RhetoricalPressure,
    "closure_mode": ClosureMode,
}

_SWAP_PRIORITY = ("structural_arc", "entry_mode", "closure_mode", "narrative_distance", "rhetorical_pressure", "lens")
"""Fixed order (order section 12: no hidden preference logic) -- the "biggest
shape" dimensions are considered for variation first."""


def _next_value(dimension: str, current: str) -> str | None:
    """Deterministically picks the next non-UNKNOWN enum value after `current`
    (cyclic). Returns None if the dimension has no other known value to offer."""

    enum_cls = _DIMENSION_ENUMS[dimension]
    candidates = [v.value for v in enum_cls if v.value != "unknown"]
    if current not in candidates:
        return candidates[0] if candidates else None
    idx = candidates.index(current)
    for offset in range(1, len(candidates)):
        candidate = candidates[(idx + offset) % len(candidates)]
        if candidate != current:
            return candidate
    return None


def _new_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


def generate_controlled_variation_options(
    angle_id: str,
    angle_profile: VariationProfile,
    relevant_memory_profiles: list[VariationProfile],
    actor_id: str = "v1c_rule_based_options",
) -> VariationRecommendationResult:
    angle_values = angle_profile.observed_values()
    angle_known = sum(1 for v in angle_values.values() if v != "unknown")

    if angle_known < MIN_KNOWN_DIMENSIONS_FOR_COMPARISON:
        return VariationRecommendationResult(
            outcome=VariationRecommendationOutcome.INSUFFICIENT_VARIATION_EVIDENCE,
            options=[],
            rationale=(
                f"Endast {angle_known} av {len(OBSERVED_DIMENSIONS)} OBSERVED-dimensioner kanda for angle-profilen "
                "-- otillrackligt underlag for att foresla ansvarsfull variation."
            ),
        )

    # The memory profile most structurally similar to the angle (if any) -- the
    # one variation genuinely needs to differentiate from.
    closest_memory = None
    closest_category = None
    if relevant_memory_profiles:
        scored = [(compare_variation_profiles(angle_profile, m), m) for m in relevant_memory_profiles]
        scored.sort(key=lambda pair: pair[0].same_count, reverse=True)
        closest_comparison, closest_memory = scored[0]
        closest_category = closest_comparison.overall

    options: list[ControlledVariationOption] = []
    for dimension in _SWAP_PRIORITY:
        if len(options) >= MAX_CONTROLLED_VARIATION_OPTIONS:
            break
        current_value = angle_values[dimension]
        if current_value == "unknown":
            continue
        new_value = _next_value(dimension, current_value)
        if new_value is None:
            continue

        hypothetical_values = dict(angle_values)
        hypothetical_values[dimension] = new_value

        # False-variation risk is assessed against relevant MEMORY, not against the
        # original angle -- changing one real structural dimension while holding the
        # other five stable is exactly the intended, legitimate design of a
        # Controlled Variation Option (order section 23's "stable_dimensions"), not
        # cosmetic repetition. Cosmetic/false variation (order section 17) is about
        # two treatments having an IDENTICAL structure, which is what still being
        # TOO_SIMILAR to existing memory after the change would mean.
        if closest_memory is not None:
            memory_values = closest_memory.observed_values()
            memory_category, _, _ = category_for_value_dicts(hypothetical_values, memory_values)
            memory_relation = (
                f"Jamfort mot narmaste relevanta memory-profil ({closest_memory.source_id}): {memory_category.value}."
            )
            false_variation = assess_false_variation_from_values(hypothetical_values, memory_values)
        else:
            memory_category = VariationDistanceCategory.STRUCTURALLY_DISTINCT
            memory_relation = "Inget relevant memory att jamfora mot -- distinkthet bedomd enbart mot ursprunglig angle-profil."
            false_variation = FalseVariationAssessment(
                is_false_variation=False,
                rationale=f"Ingen relevant memory-profil att jamfora mot; dimensionen {dimension!r} andras verkligen fran den ursprungliga angle-profilen.",
                identical_dimensions=[d for d in OBSERVED_DIMENSIONS if d != dimension],
                changed_dimensions=[dimension],
            )

        stable = {d: angle_values[d] for d in OBSERVED_DIMENSIONS if d != dimension}
        options.append(
            ControlledVariationOption(
                option_id=_new_id("VOPT-V1C"),
                relates_to_angle_id=angle_id,
                proposed_changes={dimension: new_value},
                stable_dimensions=stable,
                memory_relation=memory_relation,
                distinctiveness=memory_category,
                false_variation=false_variation,
                confidence=ConfidenceLevel.MEDIUM,
                evidence=[f"{dimension}: {current_value!r} -> {new_value!r}, ovriga fem OBSERVED-dimensioner oforandrade."],
                provenance=Provenance(
                    created_by=Actor.AI_SYSTEM, actor_id=actor_id, created_at=datetime.now(timezone.utc),
                    certainty=EvidenceCertainty.ANALYTICAL_PROPOSAL, method="v1c_rule_based_controlled_variation",
                    analysis_logic_version=angle_profile.analysis_logic_version, supporting_source_ids=[],
                ),
            )
        )

    if not options:
        return VariationRecommendationResult(
            outcome=VariationRecommendationOutcome.INSUFFICIENT_VARIATION_EVIDENCE,
            options=[],
            rationale="Inga OBSERVED-dimensioner med bade ett kant nuvarande varde och ett alternativt varde kunde konstrueras.",
        )

    rank = {VariationDistanceCategory.STRUCTURALLY_DISTINCT: 2, VariationDistanceCategory.PARTIALLY_DISTINCT: 1, VariationDistanceCategory.TOO_SIMILAR: 0, VariationDistanceCategory.INSUFFICIENT_EVIDENCE: -1}
    best = max(options, key=lambda o: rank[o.distinctiveness])

    if rank[best.distinctiveness] <= 0:
        return VariationRecommendationResult(
            outcome=VariationRecommendationOutcome.NO_MEANINGFUL_VARIATION,
            options=options,
            recommended_option_id=None,
            rationale="Samtliga konstruerade alternativ forblir for lika relevant memory (TOO_SIMILAR) -- ingen rekommenderas.",
        )

    return VariationRecommendationResult(
        outcome=VariationRecommendationOutcome.RECOMMENDED,
        options=options,
        recommended_option_id=best.option_id,
        rationale=f"{best.option_id} rekommenderas: {best.distinctiveness.value} mot relevant memory, {len(options)} alternativ totalt.",
    )


def assess_false_variation_from_values(a_values: dict[str, str], b_values: dict[str, str]) -> FalseVariationAssessment:
    category, same_count, different_count = category_for_value_dicts(a_values, b_values)
    identical = [d for d in OBSERVED_DIMENSIONS if a_values[d] == b_values[d]]
    changed = [d for d in OBSERVED_DIMENSIONS if a_values[d] != b_values[d]]
    is_false = category == VariationDistanceCategory.TOO_SIMILAR
    if is_false:
        rationale = f"{len(identical)} av {len(OBSERVED_DIMENSIONS)} OBSERVED-dimensioner identiska ({', '.join(identical)})."
    else:
        rationale = f"{len(changed)} av {len(OBSERVED_DIMENSIONS)} OBSERVED-dimensioner skiljer sig ({', '.join(changed)})."
    return FalseVariationAssessment(is_false_variation=is_false, rationale=rationale, identical_dimensions=identical, changed_dimensions=changed)
