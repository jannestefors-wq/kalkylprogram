"""Beslut 29: 'human decision halls isar fran AI assessment'."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from schema import HumanDecision, Provenance, QualityAssessment
from schema.enums import (
    Actor,
    DecisionTargetType,
    EvidenceCertainty,
    HumanDecisionType,
    QualityAssessmentResult,
)


def test_human_decision_and_quality_assessment_are_different_types(dataset):
    assert dataset["human_decisions"], "fixture must contain at least one HumanDecision"
    assert dataset["quality_assessments"], "fixture must contain at least one QualityAssessment"
    assert type(dataset["human_decisions"][0]) is not type(dataset["quality_assessments"][0])


def test_human_decision_references_but_does_not_inherit_ai_assessment(dataset):
    hd = dataset["human_decisions"][0]
    qa = dataset["quality_assessments"][0]

    assert hd.based_on_quality_assessment_id == qa.quality_assessment_id
    # A human can disagree with the AI result -- nothing forces hd.decision to mirror qa.result.
    assert hasattr(hd, "decision")
    assert not hasattr(qa, "decided_by")


def test_human_decision_cannot_be_attributed_to_an_ai_system():
    with pytest.raises(ValidationError):
        HumanDecision(
            decision_id="HD-BAD",
            target_type=DecisionTargetType.CONTENT_RECORD,
            target_id="CONTENT-001",
            decision=HumanDecisionType.APPROVE,
            decided_by="quality-gate-v1",
            decided_by_actor=Actor.AI_SYSTEM,
            decided_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )


def test_quality_assessment_has_no_human_decision_fields():
    qa = QualityAssessment(
        quality_assessment_id="QA-CHECK",
        content_id="CONTENT-001",
        created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        result=QualityAssessmentResult.PASS,
        provenance=Provenance(
            created_by=Actor.AI_SYSTEM,
            actor_id="quality-gate-v1",
            created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
            certainty=EvidenceCertainty.ANALYTICAL_PROPOSAL,
            analysis_logic_version="qg-0.1",
        ),
    )
    assert not hasattr(qa, "decided_by")
    assert not hasattr(qa, "decision")
