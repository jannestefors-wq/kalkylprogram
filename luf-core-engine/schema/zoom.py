"""
Zoom in / zoom out representation (Direktorder S10).

`ZoomLevel` in enums.py is explicitly a CANDIDATE taxonomy, not a verified
canonical LUF level structure -- the Direktorder forbids the AI system
building this from locking it in as truth without Human Review. `ZoomFrame`
is deliberately generic
(a level tag plus a free-text description) so that when the real canonical
level structure is verified, this model does not need to change shape, only
the enum's Human Review status.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from .enums import ZoomLevel

LEVEL_TAXONOMY_STATUS = "UNVERIFIED_PENDING_HUMAN_REVIEW"


class ZoomFrame(BaseModel):
    model_config = {"extra": "forbid"}

    level: ZoomLevel
    level_taxonomy_status: str = Field(
        default=LEVEL_TAXONOMY_STATUS,
        frozen=True,
        description="Always UNVERIFIED_PENDING_HUMAN_REVIEW until a human explicitly approves "
        "the ZoomLevel taxonomy against verified LUF source material.",
    )
    description: str
    claim_ids: list[str] = Field(default_factory=list, description="Claim.claim_id values visible at this level.")
