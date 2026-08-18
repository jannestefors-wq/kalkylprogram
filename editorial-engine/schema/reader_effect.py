"""
READER EFFECT (Beslut 15) and reader reactions as evidence (Beslut 16).

Three related but distinct things:

    ReaderEffect            -- a taxonomy ENTRY (e.g. "recognition", under
                                EMOTIONAL). A definition, not an occurrence.
    ReaderEffectAssociation -- a value object linking ONE ContentRecord to
                                ONE ReaderEffect with a `mode` of INTENDED or
                                OBSERVED (never merged into a single flag --
                                Beslut 15 requires both to stay queryable
                                independently, and a content record may
                                carry 0..N of these, per the same Beslut).
    ReaderFeedback           -- a raw reader reaction (e.g. Parastoo's
                                review). It is evidence that MAY support an
                                OBSERVED ReaderEffectAssociation; it is never
                                itself a Voice Core input (Beslut 16: reader
                                reactions must not be hardcoded as Voice
                                Core -- they are evidence for a possible
                                effect, routed through ReaderEffectAssociation
                                + Provenance like any other claim).
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from .enums import FeedbackVerificationStatus, ReaderEffectCategory, ReaderEffectMode
from .provenance import Provenance
from .versioning import SCHEMA_VERSION


class ReaderEffect(BaseModel):
    """A taxonomy entry, e.g. category=EMOTIONAL, name='discomfort'."""

    model_config = {"extra": "forbid"}

    reader_effect_id: str
    schema_version: str = Field(default=SCHEMA_VERSION)
    category: ReaderEffectCategory
    name: str
    description: Optional[str] = None
    examples: list[str] = Field(default_factory=list)
    created_at: datetime
    provenance: Provenance
    active: bool = True


class ReaderEffectAssociation(BaseModel):
    """Embedded in ContentRecord. One row = one claimed effect, one mode."""

    model_config = {"extra": "forbid"}

    reader_effect_id: str = Field(description="FK -> ReaderEffect.reader_effect_id.")
    mode: ReaderEffectMode
    evidence_reader_feedback_ids: list[str] = Field(
        default_factory=list,
        description="ReaderFeedback.reader_feedback_id values supporting an OBSERVED claim. "
        "Always empty for INTENDED associations.",
    )
    notes: Optional[str] = None


class ReaderFeedback(BaseModel):
    model_config = {"extra": "forbid"}

    reader_feedback_id: str
    schema_version: str = Field(default=SCHEMA_VERSION)
    source_id: Optional[str] = Field(default=None, description="FK -> Source.source_id, if the feedback is filed as a Source.")
    content_reference: str = Field(description="FK -> ContentRecord.content_id this feedback responds to.")
    feedback_text: Optional[str] = Field(default=None, description="Verbatim or excerpted feedback text.")
    feedback_reference: Optional[str] = Field(
        default=None, description="Pointer to the full feedback elsewhere (e.g. a document), when not inlined."
    )
    effect_observations: list[str] = Field(
        default_factory=list, description="Free-text notes on what effect this feedback seems to evidence, "
        "prior to being formalized into a ReaderEffectAssociation."
    )
    verification_status: FeedbackVerificationStatus
    date: Optional[datetime] = None
    language: Optional[str] = None
    notes: Optional[str] = None
