"""
Tool Trace schema (Direktorder S17 -- explicit core requirement).

Must be able to answer: which LUF tool was used, why, what it did to the
reasoning, and what new question it opened. Every field the Direktorder
lists by name is present below.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from .provenance import Provenance


class ToolTrace(BaseModel):
    model_config = {"extra": "forbid"}

    session_id: str
    original_input: str

    observations: list[str] = Field(default_factory=list, description="Claim.claim_id values, type OBSERVATION.")
    interpretations: list[str] = Field(default_factory=list, description="Claim.claim_id values, type INTERPRETATION.")
    assumptions: list[str] = Field(default_factory=list, description="Claim.claim_id values, type ASSUMPTION.")

    tools_considered: list[str] = Field(default_factory=list, description="CanonicalTool.stable_tool_id values.")
    tools_selected: list[str] = Field(default_factory=list, description="CanonicalTool.stable_tool_id values.")
    selection_reason: str

    tool_source_versions: dict[str, str] = Field(
        default_factory=dict, description="tool_id -> CanonicalTool.source_version at time of use."
    )

    process_steps: list[str] = Field(default_factory=list)
    dimensions_detected: list[str] = Field(default_factory=list)
    dimensions_missing: list[str] = Field(default_factory=list)
    questions_opened: list[str] = Field(default_factory=list)
    follow_up_input: str = Field(default="")

    decisions: list[str] = Field(default_factory=list)
    actions: list[str] = Field(default_factory=list)
    calibration: str = Field(default="")
    final_reflection: str = Field(default="")

    timestamps: dict[str, datetime] = Field(default_factory=dict)
    provenance: Provenance
