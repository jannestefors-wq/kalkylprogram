"""
QUALITY ASSESSMENT (Beslut 21).

Represents a future Quality Gate's output. Nothing here implements a rule
engine -- `triggered_rule` is a free identifier a future component will
define; this schema only fixes the shape of the verdict.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from .enums import QualityAssessmentResult, QualitySeverity, ReturnPoint
from .provenance import Provenance
from .versioning import SCHEMA_VERSION


class QualityRuleFinding(BaseModel):
    model_config = {"extra": "forbid"}

    triggered_rule: str = Field(description="Identifier of the rule that fired, e.g. 'repetition.closing_question.overused'.")
    evidence: Optional[str] = None
    severity: QualitySeverity


class QualityAssessment(BaseModel):
    model_config = {"extra": "forbid"}

    quality_assessment_id: str
    schema_version: str = Field(default=SCHEMA_VERSION)
    content_id: str = Field(description="FK -> ContentRecord.content_id.")
    created_at: datetime

    result: QualityAssessmentResult
    findings: list[QualityRuleFinding] = Field(default_factory=list)
    recommended_return_point: Optional[ReturnPoint] = Field(
        default=None,
        description="Where the work should go back to if result != PASS, e.g. REANGLE -> Angle, REWORK -> Generation.",
    )

    voice_core_snapshot_id: Optional[str] = Field(
        default=None,
        description="FK -> VoiceCoreSnapshot.snapshot_id this assessment checked the content against. "
        "V1.1: replaces the earlier free-text label (OQ-1).",
    )

    provenance: Provenance
    notes: Optional[str] = None
