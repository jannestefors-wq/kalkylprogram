"""
Editorial Engine V1 Integration pipeline
(EDITORIAL_ENGINE_V1_INTEGRATION_CONTRACT.md sections 3, 7).

    RAW IDEA / INPUT TEXT
      -> V1A Editorial Judgment
      -> V1B Editorial Memory lookup and comparison
      -> Human Decision: selected angle / retained original / needs context
      -> V1C Controlled Variation
      -> Human Variation Decision
      -> Final Editorial Assessment

`run_v1b_pipeline` already reuses V1A's own interpretation/classification/
angle steps directly (memory/pipeline.py's own docstring), so this module
never re-implements or re-decides anything V1A or V1B already computed --
it only reads their result objects and, where a human has actually decided,
carries the selected angle into V1C.

Two entry points:

- `run_editorial_engine_v1()`: the real, human-terminated flow. Runs V1A/V1B,
  stops and returns a `FinalEditorialAssessment` with `human_decision_after_v1a_v1b`
  PENDING unless the caller supplies an already-made `schema.HumanDecision`
  (`human_decision` parameter) naming which candidate angle was selected --
  only then does it run V1C, and only then can `human_decision_after_v1c`
  be resolved the same way via `human_variation_decision`.
- `run_evaluation()`: the non-persistent Evaluation Mode (contract section 7).
  Never constructs a `schema.HumanDecision` (that would fabricate a human
  actor -- forbidden, contract section 7/8's "Human Authority is bypassed").
  Instead it runs the FULL V1A->V1B->V1C chain along the SYSTEM's own
  recommended path purely to produce observable output for human evaluation,
  and reports both decision points as still PENDING in the returned
  assessment, with a clearly labeled note that no human decision was made.
"""

from __future__ import annotations

from typing import Optional

from schema import ContentRecord, HumanDecision, Series, Territory, ThesisFamily
from schema.enums import DecisionTargetType

from engine.models import CandidateAngle, PipelineOutcome, RecommendationOutcome
from engine.provider import AnalysisProvider

from memory.models import EditorialMemoryRecord, TextCompleteness
from memory.pipeline import V1BPipelineResult, run_v1b_pipeline

from variation.models import (
    FalseVariationAssessment,
    VariationDistanceCategory,
    VariationRecommendationOutcome,
)
from variation.pipeline import V1CVariationResult, run_v1c_variation_analysis

from .models import (
    EngineAssessesFields,
    EngineCouldChangeFields,
    EngineRemembersFields,
    EngineSeesFields,
    FinalEditorialAssessment,
    HumanDecisionPoint,
    RememberedRecord,
)


def _label_v1c_assessment(
    false_variation: Optional[FalseVariationAssessment], distinctiveness: Optional[VariationDistanceCategory]
) -> tuple[Optional[str], Optional[str], Optional[bool]]:
    """Read-only display-label mapping onto the contract's own requested
    vocabulary (`LEGITIMATE_VARIATION`, `FALSE_VARIATION_HIGH_RISK`,
    `PARTIAL_SIMILARITY`, `INSUFFICIENT_EVIDENCE`, `AMBIGUOUS_HUMAN_DECISION`).
    Never re-decides anything: it only renames V1C's own already-computed
    `FalseVariationAssessment`/`VariationDistanceCategory` for display.
    `sufficient_evidence == False` maps to `AMBIGUOUS_HUMAN_DECISION` per
    V1C_FINAL_SCOPE_AND_DECISION_ASSESSMENT_70B94AF.md's locked policy
    (SC48/SC49-style cases: evidence cannot separate the alternatives, so
    the human decides, never a hard `INSUFFICIENT_EVIDENCE` claim of
    novelty)."""

    if false_variation is None or distinctiveness is None:
        return None, None, None
    if not false_variation.sufficient_evidence:
        return "AMBIGUOUS_HUMAN_DECISION", false_variation.rationale, False
    if false_variation.is_false_variation:
        return "FALSE_VARIATION_HIGH_RISK", false_variation.rationale, True
    if distinctiveness == VariationDistanceCategory.PARTIALLY_DISTINCT:
        return "PARTIAL_SIMILARITY", false_variation.rationale, True
    if distinctiveness == VariationDistanceCategory.INSUFFICIENT_EVIDENCE:
        return "INSUFFICIENT_EVIDENCE", false_variation.rationale, True
    return "LEGITIMATE_VARIATION", false_variation.rationale, True


def _direction_string(option) -> str:
    """Contract 5.D example shape: 'scene -> distinction -> unresolved
    consequence'. Built only from `proposed_changes` values (dimension ->
    new value), in the dict's own insertion order -- never generated prose,
    never text."""

    return " -> ".join(option.proposed_changes.values()) if option.proposed_changes else ""


def _build_sees(v1b: V1BPipelineResult, v1c: Optional[V1CVariationResult], input_sufficient: bool) -> EngineSeesFields:
    classification = v1b.classification
    thesis_family = classification.thesis_family_matches[0].canonical_name if classification and classification.thesis_family_matches else None
    territory = classification.territory_matches[0].canonical_name if classification and classification.territory_matches else None
    series = classification.series_matches[0].canonical_name if classification and classification.series_matches else None
    topic = classification.topic if classification else None

    angle_core = None
    observed_situation = None
    if v1b.idea and v1b.idea.interpretation:
        observed_situation = v1b.idea.interpretation.observed_situation
    if v1b.recommendation and v1b.recommendation.recommended_angle_id:
        match = next((c for c in v1b.candidate_angles if c.angle.angle_id == v1b.recommendation.recommended_angle_id), None)
        if match:
            angle_core = match.core

    lens = narrative_distance = entry_function = closure_function = None
    movement_sufficient: Optional[bool] = None
    movement_sequence: list[str] = []
    lef_sufficient: Optional[bool] = None
    lef_situation = lef_consequence = None

    if v1c is not None:
        profile = v1c.angle_profile
        lens = profile.lens.value if profile.lens.value != "unknown" else None
        narrative_distance = profile.narrative_distance.value if profile.narrative_distance.value != "unknown" else None
        entry_function = profile.entry_mode.value if profile.entry_mode.value != "unknown" else None
        closure_function = profile.closure_mode.value if profile.closure_mode.value != "unknown" else None
        movement_sufficient = profile.structural_movement.sufficient_evidence
        movement_sequence = profile.structural_movement.known_stage_sequence()
        if profile.local_editorial_function is not None:
            lef_sufficient = profile.local_editorial_function.sufficient_evidence
            lef_situation = profile.local_editorial_function.situation_span
            lef_consequence = profile.local_editorial_function.consequence_span

    return EngineSeesFields(
        input_reference=v1b.raw_input.raw_input_id,
        language=v1b.raw_input.language,
        input_sufficient_for_interpretation=input_sufficient,
        thesis_family=thesis_family,
        territory=territory,
        series=series,
        topic=topic,
        angle_core=angle_core,
        observed_situation=observed_situation,
        lens=lens,
        narrative_distance=narrative_distance,
        entry_function=entry_function,
        closure_function=closure_function,
        structural_movement_sufficient=movement_sufficient,
        structural_movement_sequence=movement_sequence,
        local_editorial_function_sufficient=lef_sufficient,
        local_editorial_function_situation=lef_situation,
        local_editorial_function_consequence=lef_consequence,
    )


def _build_remembers(v1b: V1BPipelineResult) -> EngineRemembersFields:
    mc = v1b.memory_comparison
    if mc is None:
        return EngineRemembersFields(
            records=[], corpus_size=0, fulltext_corpus_size=0,
            memory_boundary_note="V1B did not run (input insufficient for interpretation).", no_match=True,
        )
    records = [
        RememberedRecord(
            content_id=m.content_id, source=m.why_relevant, text_completeness=m.text_completeness.value,
            publication_status=m.publication_status.value, why_relevant=m.why_relevant,
            repetition_signal_strength=m.repetition_signal_strength,
        )
        for m in mc.matches
    ]
    return EngineRemembersFields(
        records=records, corpus_size=mc.corpus_size, fulltext_corpus_size=mc.fulltext_corpus_size,
        memory_boundary_note=mc.memory_limitation_note, no_match=(len(mc.matches) == 0),
    )


def _build_assesses_and_could_change(v1c: Optional[V1CVariationResult]) -> tuple[EngineAssessesFields, EngineCouldChangeFields]:
    if v1c is None or v1c.recommendation.outcome != VariationRecommendationOutcome.RECOMMENDED or not v1c.recommendation.options:
        return EngineAssessesFields(), EngineCouldChangeFields()

    option = next(
        (o for o in v1c.recommendation.options if o.option_id == v1c.recommendation.recommended_option_id),
        v1c.recommendation.options[0],
    )
    label, rationale, sufficient = _label_v1c_assessment(option.false_variation, option.distinctiveness)
    directions = [_direction_string(o) for o in v1c.recommendation.options if _direction_string(o)]
    return (
        EngineAssessesFields(label=label, rationale=rationale, sufficient_evidence=sufficient),
        EngineCouldChangeFields(directions=directions),
    )


def _resolve_relevant_full_records(
    v1b: V1BPipelineResult, memory_records: list[EditorialMemoryRecord]
) -> tuple[list[EditorialMemoryRecord], bool, list[str]]:
    if v1b.memory_comparison is None:
        return [], False, []
    by_id = {r.content_id: r for r in memory_records}
    relevant = [by_id[m.content_id] for m in v1b.memory_comparison.matches if m.content_id in by_id]
    same_thesis_family = any(m.shared_thesis_family_ids for m in v1b.memory_comparison.matches)
    lexical_overlap_terms: list[str] = []
    for m in v1b.memory_comparison.matches:
        lexical_overlap_terms.extend(m.text_overlap_terms)
    return relevant, same_thesis_family, sorted(set(lexical_overlap_terms))


def run_v1a_v1b_stage(
    raw_text: str,
    raw_input_id: Optional[str] = None,
    idea_id: Optional[str] = None,
    language: str = "sv",
    memory_records: Optional[list[EditorialMemoryRecord]] = None,
    provider: Optional[AnalysisProvider] = None,
    series_registry: Optional[list[Series]] = None,
    thesis_family_registry: Optional[list[ThesisFamily]] = None,
    territory_registry: Optional[list[Territory]] = None,
) -> tuple[FinalEditorialAssessment, V1BPipelineResult]:
    """Phase 1 of the real, human-terminated flow (contract section 3, 6).
    Runs V1A/V1B exactly once and returns the assessment with Human Decision
    point 1 PENDING and V1C not yet run. A real caller shows this to a human,
    waits for their actual decision (which may arrive much later -- a new
    browser session, a different process), and then calls
    `continue_after_human_decision()` with the SAME `v1b` result returned
    here and the human's `schema.HumanDecision` -- never by calling this
    function again, which would re-run V1A/V1B and mint new candidate-angle
    ids the original decision's `target_id` would no longer match."""

    v1b = run_v1b_pipeline(
        raw_text, raw_input_id=raw_input_id, idea_id=idea_id, language=language, memory_records=memory_records,
        provider=provider, series_registry=series_registry, thesis_family_registry=thesis_family_registry,
        territory_registry=territory_registry,
    )
    input_sufficient = v1b.outcome == PipelineOutcome.COMPLETED

    decision_1_status = "pending_human_input"
    decision_1_recommendation = None
    decision_1_actions: list[str] = []
    if not input_sufficient:
        decision_1_rationale = v1b.stopped_reason or "Input insufficient for interpretation."
    elif v1b.recommendation is None or v1b.recommendation.outcome != RecommendationOutcome.RECOMMENDED:
        decision_1_rationale = "No strong angle -- human must choose retain-original, request context, or reject."
        decision_1_actions = ["retain_original", "request_more_context", "reject_all"]
    else:
        decision_1_recommendation = v1b.recommendation.recommended_angle_id
        decision_1_rationale = v1b.recommendation.rationale
        decision_1_actions = ["accept_recommended", "choose_different_candidate", "retain_original", "request_more_context", "reject_all"]

    sees = _build_sees(v1b, None, input_sufficient)
    remembers = _build_remembers(v1b)
    decision_1 = HumanDecisionPoint(
        stage="after_v1a_v1b", status=decision_1_status, available_actions=decision_1_actions,
        system_recommendation=decision_1_recommendation, rationale=decision_1_rationale,
    )
    assessment = FinalEditorialAssessment(
        input_id=v1b.raw_input.raw_input_id, sees=sees, remembers=remembers,
        assesses=EngineAssessesFields(), could_change=EngineCouldChangeFields(),
        human_decision_after_v1a_v1b=decision_1, human_decision_after_v1c=None, v1c_ran=False,
    )
    return assessment, v1b


def continue_after_human_decision(
    v1b: V1BPipelineResult,
    human_decision: HumanDecision,
    memory_records: Optional[list[EditorialMemoryRecord]] = None,
    human_variation_decision: Optional[HumanDecision] = None,
) -> tuple[FinalEditorialAssessment, Optional[V1CVariationResult]]:
    """Phase 2: takes the EXACT `v1b` result the human decision was made
    against (from `run_v1a_v1b_stage`) and, only if `human_decision` is a
    genuine human-authored `schema.HumanDecision` naming a real candidate
    angle, runs V1C. Never infers or defaults the selection."""

    input_sufficient = v1b.outcome == PipelineOutcome.COMPLETED
    v1c: Optional[V1CVariationResult] = None
    decision_2: Optional[HumanDecisionPoint] = None

    selected_angle: Optional[CandidateAngle] = None
    decision_1_status = "pending_human_input"
    if human_decision is not None and human_decision.decided_by_actor.value == "human" and human_decision.target_type == DecisionTargetType.ANGLE:
        decision_1_status = "decided"
        selected_angle = next((c for c in v1b.candidate_angles if c.angle.angle_id == human_decision.target_id), None)

    if selected_angle is not None:
        memory_pool = memory_records if memory_records is not None else _default_memory_records()
        relevant_full, same_thesis_family, lexical_overlap_terms = _resolve_relevant_full_records(v1b, memory_pool)
        v1c = run_v1c_variation_analysis(
            selected_angle, relevant_full, same_thesis_family=same_thesis_family, lexical_overlap_terms=lexical_overlap_terms,
        )
        decision_2_status = "pending_human_input"
        decision_2_recommendation = None
        decision_2_actions = ["accept_recommended_variation", "choose_different_variation", "keep_original_expression", "reject_all_variations", "request_more_context"]
        decision_2_rationale = v1c.recommendation.rationale
        if human_variation_decision is not None and human_variation_decision.decided_by_actor.value == "human":
            decision_2_status = "decided"
        elif v1c.recommendation.outcome == VariationRecommendationOutcome.RECOMMENDED:
            decision_2_recommendation = v1c.recommendation.recommended_option_id
        decision_2 = HumanDecisionPoint(
            stage="after_v1c", status=decision_2_status, available_actions=decision_2_actions,
            system_recommendation=decision_2_recommendation, rationale=decision_2_rationale,
            decision_reference=human_variation_decision.decision_id if (human_variation_decision is not None and decision_2_status == "decided") else None,
        )

    sees = _build_sees(v1b, v1c, input_sufficient)
    remembers = _build_remembers(v1b)
    assesses, could_change = _build_assesses_and_could_change(v1c)

    decision_1_recommendation = v1b.recommendation.recommended_angle_id if v1b.recommendation else None
    decision_1_rationale = v1b.recommendation.rationale if v1b.recommendation else (v1b.stopped_reason or "")
    decision_1 = HumanDecisionPoint(
        stage="after_v1a_v1b", status=decision_1_status, available_actions=[],
        system_recommendation=decision_1_recommendation, rationale=decision_1_rationale,
        decision_reference=human_decision.decision_id if decision_1_status == "decided" else None,
    )

    assessment = FinalEditorialAssessment(
        input_id=v1b.raw_input.raw_input_id, sees=sees, remembers=remembers, assesses=assesses, could_change=could_change,
        human_decision_after_v1a_v1b=decision_1, human_decision_after_v1c=decision_2, v1c_ran=(v1c is not None),
    )
    return assessment, v1c


def run_editorial_engine_v1(
    raw_text: str,
    raw_input_id: Optional[str] = None,
    idea_id: Optional[str] = None,
    language: str = "sv",
    memory_records: Optional[list[EditorialMemoryRecord]] = None,
    provider: Optional[AnalysisProvider] = None,
    series_registry: Optional[list[Series]] = None,
    thesis_family_registry: Optional[list[ThesisFamily]] = None,
    territory_registry: Optional[list[Territory]] = None,
    human_decision: Optional[HumanDecision] = None,
    human_variation_decision: Optional[HumanDecision] = None,
) -> tuple[FinalEditorialAssessment, V1BPipelineResult, Optional[V1CVariationResult]]:
    """Convenience one-shot wrapper over `run_v1a_v1b_stage()` +
    `continue_after_human_decision()`, for callers that already have a real
    `schema.HumanDecision` in hand before calling (e.g. a decision recorded
    out-of-band and passed in synchronously). Internally runs V1A/V1B
    exactly ONCE, so `human_decision.target_id` must reference an angle id
    from THIS SAME call's candidates -- never from a separate prior call
    (see `run_v1a_v1b_stage()`'s docstring for the two-phase alternative
    when the decision genuinely arrives later)."""

    _stage_assessment, v1b = run_v1a_v1b_stage(
        raw_text, raw_input_id=raw_input_id, idea_id=idea_id, language=language, memory_records=memory_records,
        provider=provider, series_registry=series_registry, thesis_family_registry=thesis_family_registry,
        territory_registry=territory_registry,
    )
    if human_decision is None:
        return _stage_assessment, v1b, None

    assessment, v1c = continue_after_human_decision(
        v1b, human_decision, memory_records=memory_records, human_variation_decision=human_variation_decision,
    )
    return assessment, v1b, v1c


def _default_memory_records() -> list[EditorialMemoryRecord]:
    from memory.ingestion import load_editorial_memory

    return load_editorial_memory()


def run_evaluation(
    raw_text: str,
    raw_input_id: Optional[str] = None,
    idea_id: Optional[str] = None,
    language: str = "sv",
    memory_records: Optional[list[EditorialMemoryRecord]] = None,
    provider: Optional[AnalysisProvider] = None,
    series_registry: Optional[list[Series]] = None,
    thesis_family_registry: Optional[list[ThesisFamily]] = None,
    territory_registry: Optional[list[Territory]] = None,
) -> tuple[FinalEditorialAssessment, V1BPipelineResult, Optional[V1CVariationResult]]:
    """Non-persistent Evaluation Mode (contract section 7). Runs the full
    V1A->V1B->V1C chain along the SYSTEM's own recommended path -- NEVER by
    constructing a `schema.HumanDecision` (contract section 7/8: 'Human
    Authority is bypassed' is a blocking integration problem, not an
    accepted shortcut). Both decision points are returned PENDING; the
    system's own recommendation is shown as `system_recommendation`, never
    recorded as a decision.

    Writes nothing: `run_v1b_pipeline`/`run_v1c_variation_analysis` are
    pure functions with no persistence side effect by construction -- this
    function calls neither a memory-write nor a canonical-data-write path,
    so there is nothing to disable, only nothing to call."""

    v1b = run_v1b_pipeline(
        raw_text, raw_input_id=raw_input_id, idea_id=idea_id, language=language, memory_records=memory_records,
        provider=provider, series_registry=series_registry, thesis_family_registry=thesis_family_registry,
        territory_registry=territory_registry,
    )
    input_sufficient = v1b.outcome == PipelineOutcome.COMPLETED

    decision_1_actions: list[str] = []
    decision_1_recommendation = None
    if not input_sufficient:
        decision_1_rationale = v1b.stopped_reason or "Input insufficient for interpretation."
    elif v1b.recommendation is None or v1b.recommendation.outcome != RecommendationOutcome.RECOMMENDED:
        decision_1_rationale = "No strong angle -- human must choose retain-original, request context, or reject."
        decision_1_actions = ["retain_original", "request_more_context", "reject_all"]
    else:
        decision_1_recommendation = v1b.recommendation.recommended_angle_id
        decision_1_rationale = v1b.recommendation.rationale
        decision_1_actions = ["accept_recommended", "choose_different_candidate", "retain_original", "request_more_context", "reject_all"]

    v1c: Optional[V1CVariationResult] = None
    decision_2: Optional[HumanDecisionPoint] = None

    if input_sufficient and v1b.recommendation is not None and v1b.recommendation.outcome == RecommendationOutcome.RECOMMENDED:
        selected_angle = next((c for c in v1b.candidate_angles if c.angle.angle_id == v1b.recommendation.recommended_angle_id), None)
        if selected_angle is not None:
            memory_pool = memory_records if memory_records is not None else _default_memory_records()
            relevant_full, same_thesis_family, lexical_overlap_terms = _resolve_relevant_full_records(v1b, memory_pool)
            v1c = run_v1c_variation_analysis(
                selected_angle, relevant_full, same_thesis_family=same_thesis_family, lexical_overlap_terms=lexical_overlap_terms,
            )
            decision_2_recommendation = v1c.recommendation.recommended_option_id if v1c.recommendation.outcome == VariationRecommendationOutcome.RECOMMENDED else None
            decision_2 = HumanDecisionPoint(
                stage="after_v1c", status="pending_human_input",
                available_actions=["accept_recommended_variation", "choose_different_variation", "keep_original_expression", "reject_all_variations", "request_more_context"],
                system_recommendation=decision_2_recommendation, rationale=v1c.recommendation.rationale,
            )

    sees = _build_sees(v1b, v1c, input_sufficient)
    remembers = _build_remembers(v1b)
    assesses, could_change = _build_assesses_and_could_change(v1c)

    decision_1 = HumanDecisionPoint(
        stage="after_v1a_v1b", status="pending_human_input", available_actions=decision_1_actions,
        system_recommendation=decision_1_recommendation, rationale=decision_1_rationale,
    )

    assessment = FinalEditorialAssessment(
        input_id=v1b.raw_input.raw_input_id, sees=sees, remembers=remembers, assesses=assesses, could_change=could_change,
        human_decision_after_v1a_v1b=decision_1, human_decision_after_v1c=decision_2, v1c_ran=(v1c is not None),
    )
    return assessment, v1b, v1c
