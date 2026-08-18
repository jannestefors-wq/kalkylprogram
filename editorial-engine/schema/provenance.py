"""
Provenance / evidence value objects (Beslut 23; V1.1 OQ-2 resolution).

`Provenance` is attached to any canonical record whose claim needs to be
traceable to: who/what made it, when, how certain it is, and which source(s)
back it up. It is a value object (embedded), not a top-level entity with its
own id, because provenance has no independent lifecycle of its own -- it
always describes exactly one owning record.

V1.1: OQ-2 resolved by project management -- `analysis_logic_version` is now
a HARD requirement whenever `created_by == Actor.AI_SYSTEM`, enforced below
by `_require_analysis_logic_version_for_ai_system`, not just documented as a
convention. When the record was human-created, the field may still be null
("om analysen ar manskligt skapad far faltet vara null om det ar logiskt").
This single validator on the shared value object enforces the rule
everywhere `Provenance` is embedded (IdeaInterpretation, ContentRecord,
QualityAssessment, VoiceCoreSnapshot, Territory, ...) without duplicating
the check per owning model.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, model_validator

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
        "interpretation, distinct from schema_version. REQUIRED (validated below) "
        "whenever created_by == Actor.AI_SYSTEM. May be null for human-created "
        "provenance.",
    )
    supporting_source_ids: list[str] = Field(
        default_factory=list,
        description="SOURCE.source_id values that back this claim, if any. "
        "Empty list, not a guess, when nothing supports it yet.",
    )
    schema_version: str = Field(default=SCHEMA_VERSION)
    notes: Optional[str] = None

    @model_validator(mode="after")
    def _require_analysis_logic_version_for_ai_system(self) -> "Provenance":
        if self.created_by == Actor.AI_SYSTEM and not self.analysis_logic_version:
            raise ValueError(
                "Provenance.analysis_logic_version is required when created_by == "
                "Actor.AI_SYSTEM (V1.1, OQ-2): an AI-produced interpretation must always "
                "be traceable to the analysis logic version that produced it."
            )
        return self
