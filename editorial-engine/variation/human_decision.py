"""
V1C Human Variation Decision (order section 26-27).

Reuses `schema.HumanDecision` directly -- no canonical model change. The
six actions map onto the EXISTING `HumanDecisionType`/`DecisionTargetType`
enums (order section 26: "Om befintlig HumanDecision-modell maste andras
semantiskt: STOPP"), exactly the disambiguate-via-`reason` pattern
`engine/human_decision.py` already established for V1A. `target_type` is
always `DecisionTargetType.ANGLE` -- the human is deciding how the
SELECTED angle's expression should proceed, never a new target kind.

`HumanDecision.decided_by_actor` inherits Canonical Foundation V1's
existing hard validation (`Actor.HUMAN` required) -- an AI cannot be
recorded as the variation decision-maker, the same guarantee V1A/V1B
already rely on, not reimplemented here.

No automatic loop (order section 27): this module only ever constructs
ONE `HumanDecision`. A new variation analysis after rejection is a
separate, explicit call by whatever code owns the pipeline.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from schema import HumanDecision
from schema.enums import DecisionTargetType, HumanDecisionType


class HumanVariationAction(str, Enum):
    ACCEPT_RECOMMENDED_VARIATION = "accept_recommended_variation"
    CHOOSE_DIFFERENT_VARIATION = "choose_different_variation"
    KEEP_ORIGINAL_EXPRESSION = "keep_original_expression"
    REJECT_ALL_VARIATIONS = "reject_all_variations"
    REQUEST_NEW_VARIATION_ANALYSIS = "request_new_variation_analysis"
    REQUEST_MORE_CONTEXT = "request_more_context"


_ACTION_TO_DECISION: dict[HumanVariationAction, HumanDecisionType] = {
    HumanVariationAction.ACCEPT_RECOMMENDED_VARIATION: HumanDecisionType.APPROVE,
    HumanVariationAction.CHOOSE_DIFFERENT_VARIATION: HumanDecisionType.APPROVE,
    HumanVariationAction.KEEP_ORIGINAL_EXPRESSION: HumanDecisionType.HOLD,
    HumanVariationAction.REJECT_ALL_VARIATIONS: HumanDecisionType.REJECT,
    HumanVariationAction.REQUEST_NEW_VARIATION_ANALYSIS: HumanDecisionType.REWORK,
    HumanVariationAction.REQUEST_MORE_CONTEXT: HumanDecisionType.HOLD,
}


def build_human_variation_decision(
    decision_id: str,
    action: HumanVariationAction,
    decided_by: str,
    angle_id: str,
    chosen_option_id: Optional[str] = None,
    reason: Optional[str] = None,
) -> HumanDecision:
    decision_type = _ACTION_TO_DECISION[action]

    if action in (HumanVariationAction.ACCEPT_RECOMMENDED_VARIATION, HumanVariationAction.CHOOSE_DIFFERENT_VARIATION) and not chosen_option_id:
        raise ValueError(f"{action.value} requires chosen_option_id (which ControlledVariationOption the human picked).")

    return HumanDecision(
        decision_id=decision_id,
        target_type=DecisionTargetType.ANGLE,
        target_id=angle_id,
        decision=decision_type,
        decided_by=decided_by,
        decided_at=datetime.now(timezone.utc),
        based_on_quality_assessment_id=None,
        reason=reason or (f"{action.value}" + (f" ({chosen_option_id})" if chosen_option_id else "")),
    )
