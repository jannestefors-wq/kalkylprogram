"""
Provenance value objects for LUF Core Engine.

Mirrors editorial-engine's schema/provenance.py pattern deliberately, so a
developer who already knows that engine recognizes this one. `Provenance`
never exists as a standalone entity; it is always embedded in the record it
describes.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, model_validator

from .enums import Actor, ToolConfidence
from .sentinels import UNKNOWN


class SourceReference(BaseModel):
    """
    A named, inspectable source document or artifact. Deliberately minimal:
    this is a pointer, not a copy of the material. `locator` should be a
    path, URL, or other identifier a human can actually go check.
    """

    model_config = {"extra": "forbid"}

    source_id: str
    description: str = UNKNOWN
    locator: str = UNKNOWN
    source_version: str = UNKNOWN


class Provenance(BaseModel):
    model_config = {"extra": "forbid"}

    created_by: Actor
    actor_id: Optional[str] = Field(
        default=None,
        description="Free identifier for the actor, e.g. a human's name/initials "
        "or an AI system+model name. None only if genuinely unrecorded.",
    )
    created_at: datetime
    confidence: ToolConfidence
    method: str = Field(
        default=UNKNOWN,
        description="How the value was produced, e.g. 'manual_entry', 'directorder_extraction', "
        "'ai_inference'.",
    )
    supporting_source_ids: list[str] = Field(
        default_factory=list,
        description="SourceReference.source_id values that back this claim, if any. "
        "Empty list, not a guess, when nothing supports it yet.",
    )
    notes: str = UNKNOWN

    @model_validator(mode="after")
    def _ai_system_claims_require_disclosure(self) -> "Provenance":
        if self.created_by == Actor.AI_SYSTEM and self.confidence == ToolConfidence.VERIFIED:
            raise ValueError(
                "Provenance: an AI_SYSTEM actor may not mark its own claim as "
                "ToolConfidence.VERIFIED (Direktorder S13 -- an AI system may not "
                "decide that an inference is ground truth). Use STRONGLY_SUPPORTED, "
                "CANDIDATE, or UNVERIFIED, or attribute the claim to a HUMAN actor "
                "who independently checked it."
            )
        return self
