"""
LUF Canonical Tool Registry schema (Direktorder LUF Core Engine V1, S5).

`CanonicalTool` carries every field the Direktorder lists as a minimum for a
real LUF tool entry. Nothing here decides that a tool IS canonical -- that
is `canonical_status` + `human_review_status`, gated by human_review/. This
module only defines the shape; `canonical_data/` holds the actual inventory
extracted from verified material, and every field that has no verified
value uses the explicit UNKNOWN/UNVERIFIED sentinels rather than a guess.
"""

from __future__ import annotations

from pydantic import BaseModel, Field, model_validator

from .enums import CanonicalStatus, ComponentOrderType, HumanReviewStatus, ToolConfidence, ToolType, UsageDirection
from .provenance import Provenance
from .sentinels import UNKNOWN


class CanonicalTool(BaseModel):
    model_config = {"extra": "forbid"}

    stable_tool_id: str = Field(description="Immutable identifier. Never reused for a different tool.")
    canonical_name: str
    tool_type: ToolType = ToolType.UNKNOWN

    components: list[str] = Field(
        default_factory=list,
        description="The named parts of the tool in source order, e.g. ['Se', 'Hoera', 'Kaenna']. "
        "Empty list, not a guess, if the component breakdown is not verified.",
    )
    component_order: ComponentOrderType = ComponentOrderType.UNVERIFIED

    usage_direction: UsageDirection = UsageDirection.UNVERIFIED
    alternative_direction: str = Field(
        default=UNKNOWN,
        description="Free-text description of a verified alternate usage direction (Direktorder S8), "
        "e.g. 'left-to-right teaches the model; right-to-left diagnoses reality'. "
        "Must stay UNKNOWN unless independently source-attested.",
    )

    purpose: str = UNKNOWN
    suitable_context: str = UNKNOWN
    unsuitable_context: str = UNKNOWN
    diagnostic_use: str = UNKNOWN
    developmental_use: str = UNKNOWN
    questions_it_can_open: list[str] = Field(default_factory=list)
    required_evidence: str = UNKNOWN
    known_boundaries: str = UNKNOWN
    relationship_to_other_tools: list[str] = Field(
        default_factory=list, description="Other CanonicalTool.stable_tool_id values, or free text if unresolved."
    )

    source_reference: str = Field(
        default=UNKNOWN, description="SourceReference.source_id this entry is drawn from, if any."
    )
    source_provenance: str = Field(
        description="Where this candidate entry actually came from (document, session, person). "
        "Required -- never UNKNOWN; if truly untraceable, say so explicitly in this field."
    )
    source_version: str = UNKNOWN

    confidence: ToolConfidence = ToolConfidence.UNVERIFIED
    canonical_status: CanonicalStatus = CanonicalStatus.HISTORICAL_LUF_MATERIAL
    human_review_status: HumanReviewStatus = HumanReviewStatus.PENDING

    provenance: Provenance

    @model_validator(mode="after")
    def _approved_requires_reviewed_status(self) -> "CanonicalTool":
        if self.canonical_status == CanonicalStatus.CANONICAL_APPROVED and self.human_review_status != HumanReviewStatus.APPROVED:
            raise ValueError(
                "CanonicalTool: canonical_status=CANONICAL_APPROVED requires "
                "human_review_status=APPROVED (Direktorder S13/S14). Use "
                "human_review.promote_to_canonical() rather than setting this field "
                "directly -- it enforces that a HUMAN actor made the decision."
            )
        return self

    @model_validator(mode="after")
    def _source_provenance_not_empty(self) -> "CanonicalTool":
        if not self.source_provenance.strip():
            raise ValueError("CanonicalTool.source_provenance must not be empty (Direktorder S5).")
        return self
