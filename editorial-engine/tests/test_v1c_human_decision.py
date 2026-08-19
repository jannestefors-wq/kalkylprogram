"""V1C TEST 24-25 (order section 26-27, 37)."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from schema.enums import Actor, DecisionTargetType, HumanDecisionType
from variation.human_decision import HumanVariationAction, build_human_variation_decision


def test_24_human_can_accept_choose_or_keep_original():
    accept = build_human_variation_decision("D1", HumanVariationAction.ACCEPT_RECOMMENDED_VARIATION, "Janne", "ANGLE-1", chosen_option_id="VOPT-1")
    assert accept.decision == HumanDecisionType.APPROVE
    assert accept.target_type == DecisionTargetType.ANGLE

    choose = build_human_variation_decision("D2", HumanVariationAction.CHOOSE_DIFFERENT_VARIATION, "Janne", "ANGLE-1", chosen_option_id="VOPT-2")
    assert choose.decision == HumanDecisionType.APPROVE

    keep = build_human_variation_decision("D3", HumanVariationAction.KEEP_ORIGINAL_EXPRESSION, "Janne", "ANGLE-1")
    assert keep.decision == HumanDecisionType.HOLD

    reject = build_human_variation_decision("D4", HumanVariationAction.REJECT_ALL_VARIATIONS, "Janne", "ANGLE-1")
    assert reject.decision == HumanDecisionType.REJECT

    rework = build_human_variation_decision("D5", HumanVariationAction.REQUEST_NEW_VARIATION_ANALYSIS, "Janne", "ANGLE-1")
    assert rework.decision == HumanDecisionType.REWORK

    more_context = build_human_variation_decision("D6", HumanVariationAction.REQUEST_MORE_CONTEXT, "Janne", "ANGLE-1")
    assert more_context.decision == HumanDecisionType.HOLD
    assert more_context.reason != keep.reason  # disambiguated even though both map to HOLD


def test_accept_and_choose_require_a_chosen_option_id():
    with pytest.raises(ValueError):
        build_human_variation_decision("D7", HumanVariationAction.ACCEPT_RECOMMENDED_VARIATION, "Janne", "ANGLE-1")


def test_25_ai_cannot_be_recorded_as_human_variation_decision_maker():
    decision = build_human_variation_decision("D8", HumanVariationAction.KEEP_ORIGINAL_EXPRESSION, "Janne", "ANGLE-1")
    assert decision.decided_by_actor == Actor.HUMAN
    with pytest.raises(ValidationError):
        decision.decided_by_actor = Actor.AI_SYSTEM
        decision.model_validate(decision.model_dump())
