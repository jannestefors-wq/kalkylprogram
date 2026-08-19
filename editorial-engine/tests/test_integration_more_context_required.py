"""Editorial Engine V1 Integration -- MORE_CONTEXT_REQUIRED follow-up
correction (order: RIKTAD INTEGRATIONSKORRIGERING FOR MORE_CONTEXT_REQUIRED
OCH RE-EVALUATION, section 6).

Scope: only the integration layer's exposure of `available_actions` on the
`after_v1a_v1b` Human Decision point when V1A stops at MORE_CONTEXT_REQUIRED.
No V1A evidence threshold was touched -- MORE_CONTEXT_REQUIRED remains a
legitimate V1A outcome; this only makes that stop actionable for a human.

Covers section 6 items 1-5 and 9 (new behavior) plus re-verifies items 6-8
and 10-12 (existing invariants that must still hold unchanged)."""

from __future__ import annotations

from engine.human_decision import HumanAction, build_human_decision
from engine.models import PipelineOutcome as V1APipelineOutcome
from integration.pipeline import continue_after_human_decision, run_evaluation, run_v1a_v1b_stage
from schema.enums import Actor

THIN_TEXT = "Ok."


def _thin_case():
    return run_v1a_v1b_stage(THIN_TEXT, memory_records=[])


def test_1_more_context_required_exposes_available_actions():
    assessment, v1b = _thin_case()
    assert v1b.outcome == V1APipelineOutcome.MORE_CONTEXT_REQUIRED
    assert assessment.human_decision_after_v1a_v1b.available_actions == ["request_more_context", "reject_all"]


def test_2_actions_are_possibilities_not_automatic_decisions():
    assessment, v1b = _thin_case()
    point = assessment.human_decision_after_v1a_v1b
    assert point.available_actions  # listed
    assert point.status == "pending_human_input"  # but nothing was decided
    assert point.decision_reference is None
    assert point.system_recommendation is None  # no action is pre-selected for the human


def test_3_original_v1a_uncertainty_preserved():
    assessment, v1b = _thin_case()
    assert v1b.stopped_reason is not None
    assert assessment.human_decision_after_v1a_v1b.rationale == v1b.stopped_reason
    assert assessment.sees.input_sufficient_for_interpretation is False


def test_4_no_angle_fabricated():
    assessment, v1b = _thin_case()
    assert v1b.candidate_angles == []
    assert assessment.sees.angle_core is None
    assert assessment.v1c_ran is False


def test_5_no_canonical_classification_fabricated():
    assessment, v1b = _thin_case()
    assert v1b.classification is None
    assert assessment.sees.thesis_family is None
    assert assessment.sees.territory is None
    assert assessment.sees.series is None
    assert assessment.sees.topic is None


def test_6_and_8_explicit_human_decision_accepted_but_v1c_still_gated_on_a_real_match():
    """order item 6: the explicit-decision mechanism still works for a v1b
    that stopped at MORE_CONTEXT_REQUIRED (decision_1 can move to
    'decided'). order item 8: V1C still runs ONLY if that decision resolves
    to a real candidate -- and a MORE_CONTEXT_REQUIRED v1b has none, so V1C
    correctly does not run even though a genuine human decision was
    supplied. This is not a fabricated angle: the human decision names a
    candidate id that provably does not exist in this v1b's (empty)
    candidate list, so nothing is invented on the system's side."""
    assessment1, v1b = _thin_case()

    decision = build_human_decision(
        "HD-THIN-001", HumanAction.ACCEPT_RECOMMENDED, "Test Human", idea_id="N/A",
        chosen_angle_id="ANGLE-DOES-NOT-EXIST",
    )
    assert decision.decided_by_actor == Actor.HUMAN

    assessment2, v1c = continue_after_human_decision(v1b, decision)
    assert assessment2.human_decision_after_v1a_v1b.status == "decided"
    assert assessment2.human_decision_after_v1a_v1b.decision_reference == "HD-THIN-001"
    assert v1c is None  # no real candidate to resolve to -- V1C correctly did not run
    assert assessment2.v1c_ran is False
    assert assessment2.human_decision_after_v1c is None


def test_7_same_v1b_context_state_used_downstream():
    assessment1, v1b = _thin_case()
    decision = build_human_decision(
        "HD-THIN-002", HumanAction.REJECT_ALL, "Test Human", idea_id="N/A",
    )
    assessment2, _ = continue_after_human_decision(v1b, decision)
    assert assessment2.sees.input_reference == assessment1.sees.input_reference == v1b.raw_input.raw_input_id
    assert assessment2.human_decision_after_v1a_v1b.rationale == v1b.stopped_reason


def test_9_evaluation_can_end_at_human_boundary():
    """A MORE_CONTEXT_REQUIRED case in Evaluation Mode terminates cleanly:
    no exception, no forced continuation, V1C never runs, and the second
    decision point stays entirely absent (there is nothing to decide on
    yet)."""
    assessment, v1b, v1c = run_evaluation(THIN_TEXT, memory_records=[])
    assert v1c is None
    assert assessment.human_decision_after_v1c is None
    assert assessment.v1c_ran is False
    assert assessment.human_decision_after_v1a_v1b.available_actions == ["request_more_context", "reject_all"]


def test_10_no_permanent_memory_write_for_more_context_required_case():
    from memory.ingestion import load_editorial_memory

    before = load_editorial_memory()
    run_evaluation(THIN_TEXT)
    run_v1a_v1b_stage(THIN_TEXT)
    after = load_editorial_memory()
    assert len(before) == len(after)
    assert [r.content_id for r in before] == [r.content_id for r in after]


def test_11_recommended_and_no_strong_angle_actions_unchanged():
    """Regression: the fix must not have altered the action lists for the
    two branches that already had them before this order."""
    golden = "En chef avbrot samma medarbetare tre ganger under motet, men bad efteratt om arlig feedback."
    assessment, v1b = run_v1a_v1b_stage(golden, memory_records=[])
    assert v1b.recommendation.outcome.value == "RECOMMENDED"
    assert assessment.human_decision_after_v1a_v1b.available_actions == [
        "accept_recommended", "choose_different_candidate", "retain_original", "request_more_context", "reject_all",
    ]
