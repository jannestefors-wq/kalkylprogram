"""V1A order TEST 14, 15 -- Human Decision, AI != Human."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from engine.human_decision import HumanAction, build_human_decision
from engine.pipeline import run_v1a_pipeline
from schema import HumanDecision
from schema.enums import Actor, DecisionTargetType, HumanDecisionType

GOLDEN = "En chef avbröt samma medarbetare tre gånger under mötet."


def test_14_human_can_accept_the_recommended_angle():
    result = run_v1a_pipeline(GOLDEN)
    hd = build_human_decision(
        "HD-T14A", HumanAction.ACCEPT_RECOMMENDED, "Janne Stefors", result.idea.idea_id,
        chosen_angle_id=result.recommendation.recommended_angle_id,
    )
    assert isinstance(hd, HumanDecision)
    assert hd.decision == HumanDecisionType.APPROVE
    assert hd.target_type == DecisionTargetType.ANGLE
    assert hd.target_id == result.recommendation.recommended_angle_id


def test_14_human_can_choose_a_different_candidate():
    result = run_v1a_pipeline(GOLDEN)
    other_candidate = next(c for c in result.candidate_angles if c.angle.angle_id != result.recommendation.recommended_angle_id)
    hd = build_human_decision(
        "HD-T14B", HumanAction.CHOOSE_DIFFERENT_CANDIDATE, "Janne Stefors", result.idea.idea_id,
        chosen_angle_id=other_candidate.angle.angle_id,
    )
    assert hd.target_id == other_candidate.angle.angle_id
    assert hd.target_id != result.recommendation.recommended_angle_id


def test_14_human_can_reject_all_candidates():
    result = run_v1a_pipeline(GOLDEN)
    hd = build_human_decision("HD-T14C", HumanAction.REJECT_ALL, "Janne Stefors", result.idea.idea_id)
    assert hd.decision == HumanDecisionType.REJECT
    assert hd.target_type == DecisionTargetType.IDEA
    assert hd.target_id == result.idea.idea_id


def test_14_human_can_request_new_interpretation():
    result = run_v1a_pipeline(GOLDEN)
    hd = build_human_decision("HD-T14D", HumanAction.REQUEST_NEW_INTERPRETATION, "Janne Stefors", result.idea.idea_id)
    assert hd.decision == HumanDecisionType.REWORK
    assert hd.target_type == DecisionTargetType.IDEA


def test_14_human_can_request_more_context():
    hd = build_human_decision("HD-T14E", HumanAction.REQUEST_MORE_CONTEXT, "Janne Stefors", "IDEA-THIN")
    assert hd.decision == HumanDecisionType.HOLD
    assert hd.target_type == DecisionTargetType.IDEA


def test_14_choosing_an_angle_action_without_angle_id_is_rejected():
    with pytest.raises(ValueError):
        build_human_decision("HD-T14F", HumanAction.ACCEPT_RECOMMENDED, "Janne Stefors", "IDEA-X")


def test_15_ai_cannot_be_recorded_as_the_human_decision_maker():
    from datetime import datetime, timezone

    with pytest.raises(ValidationError):
        HumanDecision(
            decision_id="HD-T15",
            target_type=DecisionTargetType.ANGLE,
            target_id="ANGLE-X",
            decision=HumanDecisionType.APPROVE,
            decided_by="v1a_rule_based_provider",
            decided_by_actor=Actor.AI_SYSTEM,
            decided_at=datetime.now(timezone.utc),
        )


def test_15_human_decision_default_actor_is_human():
    result = run_v1a_pipeline(GOLDEN)
    hd = build_human_decision(
        "HD-T15B", HumanAction.ACCEPT_RECOMMENDED, "Janne Stefors", result.idea.idea_id,
        chosen_angle_id=result.recommendation.recommended_angle_id,
    )
    assert hd.decided_by_actor == Actor.HUMAN
