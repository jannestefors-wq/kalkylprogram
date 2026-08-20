from __future__ import annotations

from datetime import datetime, timezone

import pytest

from human_review.workflow import HumanReviewDecision, HumanReviewQueue, promote_to_canonical
from schema.enums import Actor, CanonicalStatus, HumanReviewStatus, ToolConfidence, ToolType
from schema.tool_registry import CanonicalTool


def _candidate(ai_provenance) -> CanonicalTool:
    return CanonicalTool(
        stable_tool_id="promo-test-1",
        canonical_name="Test Candidate",
        tool_type=ToolType.UNKNOWN,
        source_provenance="unit test fixture",
        provenance=ai_provenance,
    )


def test_ai_actor_cannot_approve(ai_provenance):
    tool = _candidate(ai_provenance)
    with pytest.raises(Exception, match="reviewer_actor=HUMAN"):
        HumanReviewDecision(
            target_tool_id=tool.stable_tool_id,
            reviewer_actor=Actor.AI_SYSTEM,
            reviewer_id="claude",
            decision=HumanReviewStatus.APPROVED,
            rationale="looks fine",
            reviewed_at=datetime(2026, 8, 20, tzinfo=timezone.utc),
        )


def test_promote_to_canonical_rejects_non_human(ai_provenance):
    tool = _candidate(ai_provenance)
    decision = HumanReviewDecision(
        target_tool_id=tool.stable_tool_id,
        reviewer_actor=Actor.HUMAN,
        reviewer_id="jan.stefors",
        decision=HumanReviewStatus.NEEDS_MORE_EVIDENCE,
        rationale="not enough source material yet",
        reviewed_at=datetime(2026, 8, 20, tzinfo=timezone.utc),
    )
    with pytest.raises(ValueError, match="decision.decision must be APPROVED"):
        promote_to_canonical(tool, decision)


def test_promote_to_canonical_with_human_approval_succeeds(ai_provenance):
    tool = _candidate(ai_provenance)
    decision = HumanReviewDecision(
        target_tool_id=tool.stable_tool_id,
        reviewer_actor=Actor.HUMAN,
        reviewer_id="jan.stefors",
        decision=HumanReviewStatus.APPROVED,
        rationale="verified against original LUF workshop material",
        reviewed_at=datetime(2026, 8, 20, tzinfo=timezone.utc),
    )
    promoted = promote_to_canonical(tool, decision)
    assert promoted.canonical_status == CanonicalStatus.CANONICAL_APPROVED
    assert promoted.human_review_status == HumanReviewStatus.APPROVED
    # original candidate object is untouched (immutable update pattern)
    assert tool.canonical_status == CanonicalStatus.HISTORICAL_LUF_MATERIAL


def test_queue_end_to_end(ai_provenance):
    queue = HumanReviewQueue()
    tool = _candidate(ai_provenance)
    queue.submit_candidate(tool)
    assert tool.stable_tool_id in {t.stable_tool_id for t in queue.list_pending()}

    decision = HumanReviewDecision(
        target_tool_id=tool.stable_tool_id,
        reviewer_actor=Actor.HUMAN,
        reviewer_id="jan.stefors",
        decision=HumanReviewStatus.APPROVED,
        rationale="verified",
        reviewed_at=datetime(2026, 8, 20, tzinfo=timezone.utc),
    )
    result = queue.decide(decision)
    assert result.canonical_status == CanonicalStatus.CANONICAL_APPROVED
    assert len(queue.decisions) == 1
