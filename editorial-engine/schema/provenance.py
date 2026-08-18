"""
Provenance / evidence value objects (Beslut 23).

`Provenance` is attached to any canonical record whose claim needs to be
traceable to: who/what made it, when, how certain it is, and which source(s)
back it up. It is a value object (embedded), not a top-level entity with its
own id, because provenance has no independent lifecycle of its own -- it
always describes exactly one owning record.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from .enums import Actor, EvidenceCertainty
from .versioning import SCHEMA_VERSION


class Provenance(BaseModel):
    model_config = {"extra": "forbid"}

    created_by: Actor
    actor_id: Optional[str] = Field(
        default=None,
        description="Free identifier for the actor, e.g. a human's name/initials "
        "or an AI system+model name. None only if genuinely unrecorded.",
    )
    created_at: datetime
    certainty: EvidenceCertainty
    method: Optional[str] = Field(
        default=None,
        description="How the value was produced, e.g. 'manual_entry', "
        "'fas_0a_analysis', 'fas_0b_analysis', 'ai_inference'.",
    )
    analysis_logic_version: Optional[str] = Field(
        default=None,
        description="Version identifier of whatever analysis logic produced an "
        "interpretation, distinct from schema_version. Required whenever "
        "created_by == AI_SYSTEM (see tests/test_relation_integrity.py).",
    )
    supporting_source_ids: list[str] = Field(
        default_factory=list,
        description="SOURCE.source_id values that back this claim, if any. "
        "Empty list, not a guess, when nothing supports it yet.",
    )
    schema_version: str = Field(default=SCHEMA_VERSION)
    notes: Optional[str] = None
