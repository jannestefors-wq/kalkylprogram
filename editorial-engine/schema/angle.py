"""
ANGLE (Beslut 4 canonical object list).

An Angle is a possible editorial perspective ON an Idea -- the layer
between ANALYSIS and VARIATION in the chain
    RAW INPUT -> IDEA -> ANALYSIS -> SOURCES -> ANGLES -> VARIATION -> ...
It is deliberately thin in V1: enough to let a ContentRecord point back at
"which angle was this written from" and let a QualityAssessment recommend
"reangle" as a return point, without yet building the Angle Engine that
would generate or rank these.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from .enums import AngleStatus, VariationDimension
from .provenance import Provenance
from .versioning import SCHEMA_VERSION


class Angle(BaseModel):
    model_config = {"extra": "forbid"}

    angle_id: str
    schema_version: str = Field(default=SCHEMA_VERSION)
    idea_id: str = Field(description="FK -> Idea.idea_id.")
    created_at: datetime

    title: str
    description: str
    thesis_family_id: Optional[str] = Field(default=None, description="FK -> ThesisFamily.thesis_family_id.")
    primary_variation_dimension: Optional[VariationDimension] = Field(
        default=None,
        description="Which of the four Beslut-10 dimensions this angle most distinctly varies "
        "relative to prior treatments of the same idea/thesis family.",
    )

    status: AngleStatus = AngleStatus.PROPOSED
    rejected_reason: Optional[str] = None
    superseded_by: Optional[str] = Field(default=None, description="angle_id of the angle that replaced this one.")

    provenance: Provenance
    notes: Optional[str] = None
