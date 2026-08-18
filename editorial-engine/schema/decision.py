"""
HUMAN DECISION (Beslut 20).

The one entity in this schema where `decided_by` MUST identify a human.
This is enforced (not just documented) in a validator: a HumanDecision can
never claim `Actor.AI_SYSTEM` as its decider. AI output belongs on
QualityAssessment (schema/quality.py) instead -- an AI can recommend, it
cannot BE the human decision.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from .enums import Actor, DecisionTargetType, HumanDecisionType
from .versioning import SCHEMA_VERSION


class HumanDecision(BaseModel):
    model_config = {"extra": "forbid"}

    decision_id: str
    schema_version: str = Field(default=SCHEMA_VERSION)

    target_type: DecisionTargetType
    target_id: str

    decision: HumanDecisionType
    decided_by: str = Field(description="Name/id of the human who made this decision. Never 'AI' or a system id.")
    decided_by_actor: Actor = Field(
        default=Actor.HUMAN,
        description="Always Actor.HUMAN for a valid HumanDecision -- kept explicit so the invariant is "
        "checkable on the object itself, not only by convention.",
    )
    decided_at: datetime

    based_on_quality_assessment_id: Optional[str] = Field(
        default=None, description="FK -> QualityAssessment.quality_assessment_id, if this decision followed one. "
        "The AI assessment is input; this field never substitutes for decided_by."
    )

    reason: Optional[str] = None
    notes: Optional[str] = None

    @field_validator("decided_by_actor")
    @classmethod
    def _must_be_human(cls, v: Actor) -> Actor:
        if v is not Actor.HUMAN:
            raise ValueError(
                "HumanDecision.decided_by_actor must be Actor.HUMAN -- an AI recommendation is a "
                "QualityAssessment, never a HumanDecision."
            )
        return v
