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

from .comparison import (
    MIN_KNOWN_DIMENSIONS_FOR_COMPARISON,
    _false_variation_verdict,
    category_for_value_dicts,
    compare_structural_movements,
    compare_variation_profiles,
)
from .models import (
    DIMENSION_EVIDENCE_STATUS,
    MAX_CONTROLLED_VARIATION_OPTIONS,
    OBSERVED_DIMENSIONS,
    ClosureMode,
    ControlledVariationOption,
    EntryMode,
    FalseVariationAssessment,
    Lens,
    MovementSimilarityCategory,
    MovementStage,
    MovementStep,
    NarrativeDistance,
    RhetoricalPressure,
    StructuralArc,
    StructuralMovementAssessment,
    StructuralMovementComparisonResult,
    VariationDistanceCategory,
    VariationProfile,
    VariationRecommendationOutcome,
    VariationRecommendationResult,
)

_DIMENSION_ENUMS = {
    "entry_mode": EntryMode,
    "lens": Lens,
    "narrative_distance": NarrativeDistance,
    "rhetorical_pressure": RhetoricalPressure,
    "closure_mode": ClosureMode,
}

_SWAP_PRIORITY = ("structural_movement", "entry_mode", "closure_mode", "narrative_distance", "rhetorical_pressure", "lens")
"""Fixed order (order section 12: no hidden preference logic) -- the "biggest
shape" dimension is considered first. order section 8 (V1C Correction):
`structural_arc` is no longer directly swappable here -- it is a derived
label, not an independent variable. `structural_movement` (the actual
sequence of observed editorial movements) takes its place as the
"biggest shape" swap target (order section 22's own example: "byt
rorelsen fran claim -> inventory -> reframing till scene -> distinction ->
unresolved consequence")."""

_PROTOTYPE_MOVEMENT_SEQUENCES: list[tuple[MovementStage, ...]] = [
    (MovementStage.CLAIM, MovementStage.REFRAMING),
    (MovementStage.CONCRETE_SITUATION, MovementStage.REFRAMING),
    (MovementStage.PRINCIPLE, MovementStage.DIRECTION),
    (MovementStage.CLAIM, MovementStage.TENSION, MovementStage.CONSEQUENCE),
    (MovementStage.QUESTION, MovementStage.DISTINCTION),
    (MovementStage.CONCRETE_SITUATION, MovementStage.SYMPTOM_INVENTORY, MovementStage.REFRAMING),
]
"""order section 7, 22 (V1C Correction): a small, fixed, deterministic set
of alternative movement shapes -- not a generator, not a scored search,
the same "no hidden preference logic" discipline `_next_value()` already
uses for the other five dimensions."""


def _next_movement_sequence(current: list[str]) -> list[str] | None:
    """Deterministically picks the first prototype sequence that differs
    from `current` (cyclic in spirit, not literally -- there are too few
    prototypes to need modular indexing). Returns None only if `current`
    already matches every prototype (cannot happen with the fixed list above)."""

    current_t = tuple(current)
    for candidate in _PROTOTYPE_MOVEMENT_SEQUENCES:
        candidate_values = tuple(s.value for s in candidate)
        if candidate_values != current_t:
            return list(candidate_values)
    return None


def _movement_sequence_comparison(seq_a: list[str], seq_b: list[str]) -> StructuralMovementComparisonResult:
    """order section 23 (V1C Correction): lets an option's False-Variation
    risk be judged against relevant memory using the REAL observed (or
    hypothetically proposed) movement sequence, even when the swapped
    dimension is something else entirely -- so a proposal that changes
    only the opening word but keeps the same movement, lens, and closure
    can still be correctly flagged as risky."""

    if not seq_a or not seq_b:
        return StructuralMovementComparisonResult(
            profile_a_id="OPT-A", profile_b_id="OPT-B", profile_a_sequence=seq_a, profile_b_sequence=seq_b,
            matched_positions=0, compared_length=0, category=MovementSimilarityCategory.INSUFFICIENT_EVIDENCE,
            rationale="Ingen rorelsesekvens att jamfora.",
        )
    assessment_a = StructuralMovementAssessment(
        steps=[MovementStep(stage=MovementStage(s), confidence=ConfidenceLevel.MEDIUM, evidence="Harledd for jamforelse.") for s in seq_a],
        sufficient_evidence=True, evidence_status=DIMENSION_EVIDENCE_STATUS["structural_movement"],
    )
    assessment_b = StructuralMovementAssessment(
        steps=[MovementStep(stage=MovementStage(s), confidence=ConfidenceLevel.MEDIUM, evidence="Harledd for jamforelse.") for s in seq_b],
        sufficient_evidence=True, evidence_status=DIMENSION_EVIDENCE_STATUS["structural_movement"],
    )
    return compare_structural_movements(assessment_a, assessment_b, "OPT-A", "OPT-B")


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

    angle_movement_sequence = angle_profile.structural_movement.known_stage_sequence()

    options: list[ControlledVariationOption] = []
    for dimension in _SWAP_PRIORITY:
        if len(options) >= MAX_CONTROLLED_VARIATION_OPTIONS:
            break

        if dimension == "structural_movement":
            if not angle_movement_sequence:
                continue
            new_sequence = _next_movement_sequence(angle_movement_sequence)
            if new_sequence is None:
                continue
            current_display = "->".join(angle_movement_sequence)
            new_display = "->".join(new_sequence)
            effective_movement_sequence = new_sequence
            proposed_changes = {dimension: new_display}
            stable = {d: angle_values[d] for d in OBSERVED_DIMENSIONS if d != "structural_arc"}
            evidence_line = f"structural_movement: {current_display!r} -> {new_display!r}, ovriga fem OBSERVED-dimensioner oforandrade (structural_arc harleds om fran den nya sekvensen)."
        else:
            current_value = angle_values[dimension]
            if current_value == "unknown":
                continue
            new_value = _next_value(dimension, current_value)
            if new_value is None:
                continue
            effective_movement_sequence = angle_movement_sequence
            proposed_changes = {dimension: new_value}
            stable = {d: angle_values[d] for d in OBSERVED_DIMENSIONS if d != dimension}
            stable["structural_movement"] = "->".join(angle_movement_sequence) if angle_movement_sequence else "unknown"
            evidence_line = f"{dimension}: {current_value!r} -> {new_value!r}, structural_movement och ovriga OBSERVED-dimensioner oforandrade."

        # False-variation risk is assessed against relevant MEMORY, not against the
        # original angle -- changing one real structural dimension while holding the
        # other five stable is exactly the intended, legitimate design of a
        # Controlled Variation Option (order section 23's "stable_dimensions"), not
        # cosmetic repetition. Cosmetic/false variation (order section 17) is about
        # two treatments having an IDENTICAL structure, which is what still being
        # TOO_SIMILAR to existing memory after the change would mean.
        #
        # order section 23 (V1C Correction): the movement comparison uses the
        # REAL/proposed movement sequence even when a DIFFERENT dimension was
        # swapped -- so an option that only changes entry_mode but keeps the
        # same movement, lens, and closure can still be correctly flagged as
        # False Variation risk against memory that shares that movement.
        if closest_memory is not None:
            memory_values = closest_memory.observed_values()
            memory_movement_sequence = closest_memory.structural_movement.known_stage_sequence()
            movement_comparison = _movement_sequence_comparison(effective_movement_sequence, memory_movement_sequence)
            movement_category = movement_comparison.category
            movement_same = movement_category == MovementSimilarityCategory.STRONGLY_SIMILAR

            hypothetical_values = dict(angle_values)
            if dimension != "structural_movement":
                hypothetical_values[dimension] = proposed_changes[dimension]

            memory_category, _, _ = category_for_value_dicts(hypothetical_values, memory_values, structural_arc_same_override=movement_same)
            memory_relation = (
                f"Jamfort mot narmaste relevanta memory-profil ({closest_memory.source_id}): {memory_category.value} "
                f"(rorelsesekvens: {effective_movement_sequence} mot {memory_movement_sequence})."
            )
            false_variation = assess_false_variation_from_values(
                hypothetical_values, memory_values, structural_arc_same_override=movement_same,
                movement_category=movement_category, movement_matched_positions=movement_comparison.matched_positions,
            )
        else:
            memory_category = VariationDistanceCategory.STRUCTURALLY_DISTINCT
            memory_relation = "Inget relevant memory att jamfora mot -- distinkthet bedomd enbart mot ursprunglig angle-profil."
            false_variation = FalseVariationAssessment(
                is_false_variation=False,
                rationale=f"Ingen relevant memory-profil att jamfora mot; dimensionen {dimension!r} andras verkligen fran den ursprungliga angle-profilen.",
                identical_dimensions=[d for d in OBSERVED_DIMENSIONS if d != dimension],
                changed_dimensions=[dimension],
            )

        options.append(
            ControlledVariationOption(
                option_id=_new_id("VOPT-V1C"),
                relates_to_angle_id=angle_id,
                proposed_changes=proposed_changes,
                stable_dimensions=stable,
                memory_relation=memory_relation,
                distinctiveness=memory_category,
                false_variation=false_variation,
                confidence=ConfidenceLevel.MEDIUM,
                evidence=[evidence_line],
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


_NON_MOVEMENT_DIMS_FOR_VALUES = tuple(d for d in OBSERVED_DIMENSIONS if d != "structural_arc")
_CONSTRUCTION_CORROBORATION_DIMS_FOR_VALUES = tuple(d for d in _NON_MOVEMENT_DIMS_FOR_VALUES if d != "lens")
"""order section 6 (V1C Correction 2), mirrors `comparison.py`'s
`_CONSTRUCTION_CORROBORATION_DIMENSIONS` -- `lens` reflects topic/theme,
not construction, and is excluded from corroboration (kept only in the
flat six-slot `identical`/`changed` reporting above)."""


def assess_false_variation_from_values(
    a_values: dict[str, str],
    b_values: dict[str, str],
    structural_arc_same_override: bool | None = None,
    movement_category: MovementSimilarityCategory | None = None,
    movement_matched_positions: int = 0,
) -> FalseVariationAssessment:
    """Hypothetical value-dict path (option previews have no recomputed
    `DimensionAssessment.confidence`, only a plain proposed string value)
    -- falls back to naive value equality per dimension, unlike the real
    profile-to-profile `assess_false_variation()` which is evidence-aware
    (order section 7, V1C Correction 2)."""

    category, same_count, different_count = category_for_value_dicts(a_values, b_values, structural_arc_same_override=structural_arc_same_override)
    identical = [
        d for d in OBSERVED_DIMENSIONS
        if (structural_arc_same_override if (d == "structural_arc" and structural_arc_same_override is not None) else a_values[d] == b_values[d])
    ]
    changed = [d for d in OBSERVED_DIMENSIONS if d not in identical]

    construction_same = [d for d in identical if d in _CONSTRUCTION_CORROBORATION_DIMS_FOR_VALUES]
    construction_diff = [
        d for d in _CONSTRUCTION_CORROBORATION_DIMS_FOR_VALUES
        if a_values.get(d) != "unknown" and b_values.get(d) != "unknown" and a_values.get(d) != b_values.get(d)
    ]
    movement_cat = movement_category if movement_category is not None else MovementSimilarityCategory.INSUFFICIENT_EVIDENCE
    # order section 6 (V1C False Variation Blocker 3): this value-dict path has
    # no per-dimension confidence at all (plain strings, "naive value equality"
    # per this function's own docstring) -- it cannot distinguish a genuinely
    # detected signal from a coincidental default, nor apply the
    # asymmetric-richness guard the real profile path uses
    # (`a_confident_construction_dims == n_same_construction_dims`), so the
    # two new Blocker 3 short-form tiers are both kept permanently
    # unreachable here by passing an impossible sentinel count (-1, which
    # can never equal `n_same_construction_dims` or 0) -- exact prior
    # behavior preserved for this path, out of scope for Blocker 3.
    is_false, reason = _false_variation_verdict(
        category, movement_cat, movement_matched_positions, len(construction_same), len(construction_diff),
        -1, -1, 999, 999,
    )

    if reason in ("movement_strongly_corroborated", "movement_partially_corroborated", "movement_uncontradicted", "weakly_corroborated"):
        rationale = (
            f"Rorelsesekvensen ar {movement_cat.value} och {len(construction_same)} av {len(_CONSTRUCTION_CORROBORATION_DIMS_FOR_VALUES)} "
            f"konstruktionsdimensioner ({', '.join(construction_same) or 'inga'}) bekraftar oberoende "
            f"-- redaktionell konstruktion bestar aven om {', '.join(construction_diff) or 'inga andra dimensioner'} skiljer sig."
        )
    elif reason == "construction_majority":
        rationale = f"{len(construction_same)} av {len(_CONSTRUCTION_CORROBORATION_DIMS_FOR_VALUES)} konstruktionsdimensioner ar lika ({', '.join(construction_same)}) -- overvagande bevis for samma konstruktion."
    elif is_false:
        rationale = f"{len(identical)} av {len(OBSERVED_DIMENSIONS)} OBSERVED-dimensioner identiska ({', '.join(identical)})."
    else:
        rationale = f"{len(changed)} av {len(OBSERVED_DIMENSIONS)} OBSERVED-dimensioner skiljer sig ({', '.join(changed)})."
    return FalseVariationAssessment(is_false_variation=is_false, rationale=rationale, identical_dimensions=identical, changed_dimensions=changed)
