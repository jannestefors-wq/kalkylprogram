"""
Triangulation representation (Direktorder S4).

Explicit non-goal, quoting the Direktorder directly: this must NOT be built
as `choose_triangle() -> generate_answer()`. A TriangulationSession applies
one or more CanonicalTool perspectives to the SAME situation and records,
per perspective, what was confirmed, contradicted, still missing, and what
pattern is emerging -- so the output is a structured investigation, not a
single lookup.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from .provenance import Provenance


class PerspectiveApplication(BaseModel):
    """One CanonicalTool applied as an observation lens within a session."""

    model_config = {"extra": "forbid"}

    tool_id: str = Field(description="CanonicalTool.stable_tool_id used as this perspective's lens.")
    tool_source_version: str = Field(description="CanonicalTool.source_version at the time it was applied.")
    selection_reason: str

    claim_ids_produced: list[str] = Field(default_factory=list, description="Claim.claim_id values opened by this lens.")
    confirmed: list[str] = Field(default_factory=list)
    contradicted: list[str] = Field(default_factory=list)
    missing: list[str] = Field(default_factory=list, description="What this lens shows we still don't know.")
    patterns_emerging: list[str] = Field(default_factory=list)
    further_information_needed: list[str] = Field(default_factory=list)


class TriangulationSession(BaseModel):
    model_config = {"extra": "forbid"}

    session_id: str
    situation_description: str
    perspectives_applied: list[PerspectiveApplication] = Field(
        default_factory=list,
        description="One or more perspectives on the SAME situation. A session with a single "
        "perspective is legal (not every input needs multiple lenses) but the schema "
        "must never collapse to a single-perspective-only shape.",
    )
    created_at: datetime
    provenance: Provenance
