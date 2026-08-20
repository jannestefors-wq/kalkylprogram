from __future__ import annotations

import pytest
from pydantic import ValidationError

from schema.enums import CanonicalStatus, HumanReviewStatus, ToolConfidence, ToolType
from schema.tool_registry import CanonicalTool


def _minimal_kwargs(provenance):
    return dict(
        stable_tool_id="test-tool-x",
        canonical_name="Test Tool",
        tool_type=ToolType.UNKNOWN,
        source_provenance="unit test fixture",
        provenance=provenance,
    )


def test_historical_material_stays_historical_by_default(ai_provenance):
    tool = CanonicalTool(**_minimal_kwargs(ai_provenance))
    assert tool.canonical_status == CanonicalStatus.HISTORICAL_LUF_MATERIAL
    assert tool.human_review_status == HumanReviewStatus.PENDING


def test_cannot_set_canonical_approved_without_human_review_status_approved(ai_provenance):
    with pytest.raises(ValidationError, match="CANONICAL_APPROVED requires human_review_status=APPROVED"):
        CanonicalTool(
            **_minimal_kwargs(ai_provenance),
            canonical_status=CanonicalStatus.CANONICAL_APPROVED,
            human_review_status=HumanReviewStatus.PENDING,
        )


def test_canonical_approved_requires_matching_review_status_is_consistent(human_provenance):
    # Even with a matching human_review_status, direct construction is legal at the
    # schema level (the workflow-level guarantee that a HUMAN actually decided this
    # lives in human_review/workflow.py -- see test_human_review_required_for_promotion.py).
    tool = CanonicalTool(
        **_minimal_kwargs(human_provenance),
        canonical_status=CanonicalStatus.CANONICAL_APPROVED,
        human_review_status=HumanReviewStatus.APPROVED,
    )
    assert tool.canonical_status == CanonicalStatus.CANONICAL_APPROVED
