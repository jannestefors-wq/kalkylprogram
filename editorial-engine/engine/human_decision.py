"""
Step 7: Human Decision (order section 18-19).

Thin wrapper over the existing, unmodified `schema.HumanDecision` --
Canonical Foundation V1 already hard-validates `decided_by_actor ==
Actor.HUMAN` (schema/decision.py), so an AI can never be recorded as the
decision-maker here; that guarantee is inherited, not reimplemented.

No new `HumanDecisionType` values were added (order section 33 would
require a STOP for that). The five actions order section 18 lists map onto
the existing enum as follows -- each disambiguated by the free-text
`reason` field, since the enum alone doesn't distinguish e.g. "reject all
candidates" from "request a new interpretation":

    accept recommended angle   -> APPROVE, target=ANGLE (the recommended one)
    choose a different angle   -> APPROVE, target=ANGLE (the chosen one)
    reject all candidates      -> REJECT,  target=IDEA
    request new interpretation -> REWORK,  target=IDEA
    request more context       -> HOLD,    target=IDEA

Order section 19 ("ingen automatisk loop"): this module only ever
constructs ONE `HumanDecision` per call. It never re-invokes the pipeline
itself -- a new interpretation/angle run is a separate, explicit call by
whatever code holds the pipeline, never triggered from here.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from schema import HumanDecision
from schema.enums import DecisionTargetType, HumanDecisionType


class HumanAction(str, Enum):
    ACCEPT_RECOMMENDED = "accept_recommended"
    CHOOSE_DIFFERENT_CANDIDATE = "choose_different_candidate"
    REJECT_ALL = "reject_all"
    REQUEST_NEW_INTERPRETATION = "request_new_interpretation"
    REQUEST_MORE_CONTEXT = "request_more_context"


_ACTION_TO_DECISION: dict[HumanAction, tuple[HumanDecisionType, DecisionTargetType]] = {
    HumanAction.ACCEPT_RECOMMENDED: (HumanDecisionType.APPROVE, DecisionTargetType.ANGLE),
    HumanAction.CHOOSE_DIFFERENT_CANDIDATE: (HumanDecisionType.APPROVE, DecisionTargetType.ANGLE),
    HumanAction.REJECT_ALL: (HumanDecisionType.REJECT, DecisionTargetType.IDEA),
    HumanAction.REQUEST_NEW_INTERPRETATION: (HumanDecisionType.REWORK, DecisionTargetType.IDEA),
    HumanAction.REQUEST_MORE_CONTEXT: (HumanDecisionType.HOLD, DecisionTargetType.IDEA),
}


def build_human_decision(
    decision_id: str,
    action: HumanAction,
    decided_by: str,
    idea_id: str,
    chosen_angle_id: Optional[str] = None,
    reason: Optional[str] = None,
    based_on_quality_assessment_id: Optional[str] = None,
) -> HumanDecision:
    decision_type, target_type = _ACTION_TO_DECISION[action]

    if target_type == DecisionTargetType.ANGLE:
        if not chosen_angle_id:
            raise ValueError(f"{action.value} requires chosen_angle_id (which angle the human is deciding on).")
        target_id = chosen_angle_id
    else:
        target_id = idea_id

    return HumanDecision(
        decision_id=decision_id,
        target_type=target_type,
        target_id=target_id,
        decision=decision_type,
        decided_by=decided_by,
        decided_at=datetime.now(timezone.utc),
        based_on_quality_assessment_id=based_on_quality_assessment_id,
        reason=reason or action.value,
    )
