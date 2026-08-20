"""
Observation / interpretation separation (Direktorder S9).

This is meant to be a load-bearing machine rule, not documentation: a Claim
of type INTERPRETATION, INFERENCE, or ASSUMPTION must declare what
observation(s) it was derived from, and a Claim of type OBSERVATION must
NOT claim to be derived from anything -- an observation is a direct report,
not a reading of other claims. This is enforced by a validator below, not
just by convention, so "an inference becomes an observation" is a type
error, not a discipline problem.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, model_validator

from .enums import ClaimType
from .provenance import Provenance


class Claim(BaseModel):
    model_config = {"extra": "forbid"}

    claim_id: str
    claim_type: ClaimType
    text: str
    derived_from_claim_ids: list[str] = Field(
        default_factory=list,
        description="Claim.claim_id values this claim was built on. Required (non-empty) for "
        "INTERPRETATION, INFERENCE, and ASSUMPTION. Must be empty for OBSERVATION.",
    )
    created_at: datetime
    provenance: Provenance
    tags: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _derivation_matches_claim_type(self) -> "Claim":
        derived_types = {ClaimType.INTERPRETATION, ClaimType.INFERENCE, ClaimType.ASSUMPTION}
        if self.claim_type in derived_types and not self.derived_from_claim_ids:
            raise ValueError(
                f"Claim: claim_type={self.claim_type.value} must declare at least one "
                "derived_from_claim_ids entry -- an interpretation/inference/assumption "
                "that names no observation it came from cannot be distinguished from a "
                "guess (Direktorder S9)."
            )
        if self.claim_type == ClaimType.OBSERVATION and self.derived_from_claim_ids:
            raise ValueError(
                "Claim: claim_type=OBSERVATION must not carry derived_from_claim_ids -- "
                "an observation is a direct report, not a reading of other claims. If "
                "this is actually a reading of other claims, its type is INTERPRETATION "
                "or INFERENCE, not OBSERVATION (Direktorder S9)."
            )
        return self
