"""
VOICE PRINCIPLE, STYLE ATTRIBUTE, REPETITION SIGNAL (Beslut 11-14).

Three separate registries, on purpose:

    VoicePrinciple   -- WHO LUF is (Voice Core + supported principles): a
                         canonical, versioned, evidence-bearing editorial
                         reference, obligatory input to any future traceable
                         assessment that uses it. (V1.1 correction: this
                         schema describes what the canonical data MEANS: it
                         does not prescribe how a not-yet-built generator
                         must consume it -- that is a future, separately
                         approved decision, not encoded here.)
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


class VoiceCoreSnapshot(BaseModel):
    """
    V1.1, OQ-1 resolution: a free-text label like "voice-core-1.0" was
    judged insufficient long-term -- we must later be able to state exactly
    which VoicePrinciple rows a text or analysis was judged against, not
    just which label was in fashion at the time.

    Design choice (documented per the order's explicit request): this
    REFERENCES existing `VoicePrinciple` rows by id
    (`voice_principle_ids`) rather than duplicating their `definition`/
    `anti_definition` text. A principle's canonical wording has exactly one
    home (`VoicePrinciple`); duplicating it into every snapshot that ever
    included it would recreate the Adam-style two-representations-that-
    drift-apart problem this schema exists to avoid (Beslut 27). Looking up
    "what did principle X actually say under snapshot Y" is a one-hop join
    (`VoicePrinciple.version`/`valid_from` already answers "as of when"),
    which is cheap enough that duplication buys nothing.

    Lifecycle: reuses the exact same `active` + `superseded_by` pattern
    already used by `VoicePrinciple` and the other registries, rather than
    introducing a new status enum -- see docs/TECHNICAL_PROPOSALS.md TP-8
    and docs/OPEN_QUESTIONS.md (Beslut 9 of the V1.1 order: no parallel
    status model unless the lifecycle genuinely differs, and a snapshot's
    does not).
    """

    model_config = {"extra": "forbid"}

    snapshot_id: str
    schema_version: str = Field(default=SCHEMA_VERSION)
    version: str = Field(description="e.g. '1.0' -- what ContentRecord/QualityAssessment refer to as the Voice Core version used.")
    created_at: datetime
    voice_principle_ids: list[str] = Field(
        min_length=1,
        description="FK -> VoicePrinciple.voice_principle_id. The exact set of principles in effect at this snapshot.",
    )
    active: bool = True
    superseded_by: Optional[str] = Field(
        default=None, description="snapshot_id of the snapshot that replaced this one as the current reference, if any."
    )
    provenance: Provenance
    notes: Optional[str] = None


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
