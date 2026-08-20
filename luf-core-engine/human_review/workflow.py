"""
Human Review workflow (Direktorder S13/S14).

An AI system may extract, structure, compare, source-track, and flag gaps.
It may NOT decide what is canonical LUF. This module is the one place that
is allowed to change a CanonicalTool's canonical_status to
CANONICAL_APPROVED, and it refuses to do so unless the decision was made by
a HUMAN actor.
`CanonicalTool` itself also validates this (schema/tool_registry.py), so
the rule holds even if a future caller bypasses this module -- this is the
convenience/audit-trail layer on top of that hard constraint.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, model_validator

from schema.enums import Actor, CanonicalStatus, HumanReviewStatus
from schema.tool_registry import CanonicalTool


class HumanReviewDecision(BaseModel):
    model_config = {"extra": "forbid"}

    target_tool_id: str
    reviewer_actor: Actor
    reviewer_id: str
    decision: HumanReviewStatus
    rationale: str
    reviewed_at: datetime

    @model_validator(mode="after")
    def _reviewer_must_be_human_for_approval(self) -> "HumanReviewDecision":
        if self.decision == HumanReviewStatus.APPROVED and self.reviewer_actor != Actor.HUMAN:
            raise ValueError(
                "HumanReviewDecision: decision=APPROVED requires reviewer_actor=HUMAN "
                "(Direktorder S13 -- Human Review can never be skipped or delegated to AI)."
            )
        if not self.rationale.strip():
            raise ValueError("HumanReviewDecision.rationale must not be empty.")
        return self


class HumanReviewQueue:
    """In-memory queue; a real deployment persists this in the owner's own data layer."""

    def __init__(self) -> None:
        self._pending: dict[str, CanonicalTool] = {}
        self._decisions: list[HumanReviewDecision] = []

    def submit_candidate(self, tool: CanonicalTool) -> None:
        if tool.canonical_status == CanonicalStatus.CANONICAL_APPROVED:
            raise ValueError(
                "HumanReviewQueue.submit_candidate: a tool must not already be "
                "CANONICAL_APPROVED when submitted for review."
            )
        self._pending[tool.stable_tool_id] = tool

    def list_pending(self) -> list[CanonicalTool]:
        return list(self._pending.values())

    def decide(self, decision: HumanReviewDecision) -> CanonicalTool:
        tool = self._pending.get(decision.target_tool_id)
        if tool is None:
            raise KeyError(f"No pending candidate with stable_tool_id={decision.target_tool_id!r}")
        self._decisions.append(decision)
        return promote_to_canonical(tool, decision) if decision.decision == HumanReviewStatus.APPROVED else tool.model_copy(
            update={"human_review_status": decision.decision}
        )

    @property
    def decisions(self) -> list[HumanReviewDecision]:
        return list(self._decisions)


def promote_to_canonical(tool: CanonicalTool, decision: HumanReviewDecision) -> CanonicalTool:
    """The only function in this codebase allowed to set CANONICAL_APPROVED."""

    if decision.target_tool_id != tool.stable_tool_id:
        raise ValueError("promote_to_canonical: decision.target_tool_id does not match tool.stable_tool_id.")
    if decision.decision != HumanReviewStatus.APPROVED:
        raise ValueError("promote_to_canonical: decision.decision must be APPROVED.")
    if decision.reviewer_actor != Actor.HUMAN:
        raise ValueError("promote_to_canonical: decision.reviewer_actor must be Actor.HUMAN.")

    return tool.model_copy(
        update={
            "canonical_status": CanonicalStatus.CANONICAL_APPROVED,
            "human_review_status": HumanReviewStatus.APPROVED,
        }
    )
