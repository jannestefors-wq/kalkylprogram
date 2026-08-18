"""
VOICE PRINCIPLE, STYLE ATTRIBUTE, REPETITION SIGNAL (Beslut 11-14).

Three separate registries, on purpose:

    VoicePrinciple   -- WHO LUF is (Voice Core + supported principles).
                         Never optional; a generator cannot "turn these off".
    StyleAttribute   -- HOW a text may choose to sound (Style Options).
                         All of them are optional simultaneously (Beslut 13:
                         a future component must be able to reject every
                         single Style Option and still produce something
                         that satisfies Voice Core).
    RepetitionSignal -- WHAT PATTERN to watch for overuse of. Repetition
                         Signals mostly name the same surface techniques as
                         Style Options (e.g. "kort tesoppning" is both a
                         style choice and a repetition risk), which is
                         expected -- a technique becomes a *risk* through
                         overuse, not through existing. They are still
                         modelled as two separate catalogues because "this
                         is an available style choice" and "this is
                         currently over-used" are different kinds of claims
                         with different lifecycles; conflating them would
                         make it impossible to mark a signal as a live risk
                         without also silently deprecating the style choice.

`VoicePrinciple.status` is the field that keeps canonical vs.
strongly_supported vs. analytical_proposal distinguishable in the DATA, not
only across two different documents (Beslut 12). Canonical Voice Core V1
principles (Beslut 11, all eight) and Supported Voice Principles (Beslut 12,
all five) are both instances of this one model, differing only in `status`
-- this is intentional: it is the same kind of object, at a different
confirmation stage, not two different object types.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from .enums import RepetitionSignalType, StyleAttributeCategory, VoicePrincipleStatus
from .provenance import Provenance
from .versioning import SCHEMA_VERSION


class VoicePrinciple(BaseModel):
    model_config = {"extra": "forbid"}

    voice_principle_id: str
    schema_version: str = Field(default=SCHEMA_VERSION)
    name: str
    definition: str
    anti_definition: Optional[str] = Field(
        default=None, description="What this principle explicitly rules out -- makes the boundary testable."
    )
    status: VoicePrincipleStatus
    evidence: list[Provenance] = Field(
        default_factory=list, description="What Fas 0B material grounds this principle."
    )
    version: str = Field(description="Version of this principle's own definition, independent of SCHEMA_VERSION.")
    valid_from: datetime
    superseded_by: Optional[str] = Field(
        default=None, description="voice_principle_id of a newer version, if this one has been superseded."
    )


class StyleAttribute(BaseModel):
    model_config = {"extra": "forbid"}

    style_attribute_id: str
    schema_version: str = Field(default=SCHEMA_VERSION)
    name: str
    category: StyleAttributeCategory
    description: Optional[str] = None
    example: Optional[str] = None
    created_at: datetime
    provenance: Provenance
    active: bool = True


class RepetitionSignal(BaseModel):
    model_config = {"extra": "forbid"}

    repetition_signal_id: str
    schema_version: str = Field(default=SCHEMA_VERSION)
    signal_type: RepetitionSignalType
    related_style_attribute_id: Optional[str] = Field(
        default=None, description="StyleAttribute.style_attribute_id this risk pattern is derived from, if any."
    )
    description: Optional[str] = None
    detection_notes: Optional[str] = Field(
        default=None,
        description="Human-readable notes on how this MIGHT be measured later. No measurement is implemented here.",
    )
    created_at: datetime
    provenance: Provenance
    active: bool = True
