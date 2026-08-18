"""
CONTENT RECORD and VARIATION FINGERPRINT (Beslut 8, 9, 10, 25).

NORMALIZATION FLAG: the flat field list in Beslut 8 is grouped into two
sub-objects here, `ContentWhat` (what the text says) and `ContentForm` (how
it is built), because Beslut 8 itself says this split "ar avgorande for
framtida repetitionskontroll." No field was dropped; `series` was renamed
`series_ids` (still a list of Series.series_id) and `reader_effect`
(singular in Beslut 8) became `reader_effects: list[ReaderEffectAssociation]`
per Beslut 15's explicit 0..N + intended/observed requirement, which
supersedes the singular field named in Beslut 8.

TECHNICAL PROPOSAL: `idea_id`, `angle_id` and `voice_core_version_ref` were
added -- not present in Beslut 8's list -- because without them a
ContentRecord cannot be traced back through ANGLE to IDEA, or checked
against a specific Voice Core version, both of which the chain in Beslut 2
and the versioning requirement in Beslut 22 depend on. Flagged in
docs/TECHNICAL_PROPOSALS.md.

Beslut 10 (four variation dimensions) maps onto this module as:
    CONTENT     -> ContentWhat
    PERSPECTIVE -> ContentWhat.perspective (kept inside "what", since whose
                   reality we see is part of what is being said, not how)
    FORM        -> ContentForm
    EFFECT      -> ContentRecord.reader_effects

Beslut 25 (language/market): `language` and `market` live on ContentRecord,
not on Idea alone, so a Swedish and a US ContentRecord can share one
`idea_id` while being two separate, non-translation content_ids.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from .enums import (
    ContentStatus,
    CtaType,
    DegreeLevel,
    EmotionalRegister,
    EndingType,
    LengthClass,
    NarrativeMode,
    PointOfView,
    RhythmPattern,
)
from .provenance import Provenance
from .reader_effect import ReaderEffectAssociation
from .versioning import SCHEMA_VERSION


class ContentWhat(BaseModel):
    """The CONTENT + PERSPECTIVE variation dimensions (Beslut 10)."""

    model_config = {"extra": "forbid"}

    topic: Optional[str] = Field(default=None, description="Open vocabulary tag, e.g. 'Tillit'. Never a series_id.")
    subtopics: list[str] = Field(default_factory=list)
    core_thesis: Optional[str] = None
    human_conflict: Optional[str] = None
    hidden_pattern: Optional[str] = None
    root_cause: Optional[str] = None
    perspective: Optional[str] = Field(default=None, description="Whose reality this text is told from.")


class ContentForm(BaseModel):
    """The FORM variation dimension (Beslut 10) -- how the text is built."""

    model_config = {"extra": "forbid"}

    form: Optional[str] = Field(default=None, description="Open vocabulary format tag, e.g. 'linkedin_post', 'letter'.")
    narrative_mode: Optional[NarrativeMode] = None
    point_of_view: Optional[PointOfView] = None

    opening_type: Optional[str] = Field(default=None, description="Open vocabulary, may reference a StyleAttribute.")
    opening_text: Optional[str] = None

    dramaturgy: Optional[str] = None
    paragraph_pattern: Optional[str] = None
    sentence_rhythm: Optional[RhythmPattern] = None
    length_class: Optional[LengthClass] = None

    emotional_register: Optional[EmotionalRegister] = None
    personal_presence: Optional[DegreeLevel] = None
    solution_degree: Optional[DegreeLevel] = None

    question_count: Optional[int] = Field(default=None, ge=0)
    contrast_usage: Optional[DegreeLevel] = None
    metaphor_usage: Optional[DegreeLevel] = None
    dialogue_usage: Optional[DegreeLevel] = None
    scene_usage: Optional[DegreeLevel] = None

    ending_type: Optional[EndingType] = None
    cta_type: Optional[CtaType] = None
    signature_type: Optional[str] = None

    key_phrases: list[str] = Field(default_factory=list)
    rhetorical_patterns: list[str] = Field(default_factory=list)


class VariationFingerprint(BaseModel):
    """
    Compact per-text fingerprint (Beslut 9). Deliberately just a labelled
    snapshot of ContentForm -- no comparison logic. A future component can
    diff `VariationFingerprint` instances across the last N publications;
    this schema only fixes what the labels are and how they are spelled.
    """

    model_config = {"extra": "forbid"}

    content_id: str = Field(description="FK -> ContentRecord.content_id this fingerprint was taken from.")
    schema_version: str = Field(default=SCHEMA_VERSION)
    computed_at: datetime

    form: Optional[NarrativeMode] = None
    opening: Optional[str] = None
    pov: Optional[PointOfView] = None
    length: Optional[LengthClass] = None
    rhythm: Optional[RhythmPattern] = None
    emotion: Optional[EmotionalRegister] = None
    personal: Optional[DegreeLevel] = None
    question: Optional[DegreeLevel] = None
    contrast: Optional[DegreeLevel] = None
    solution: Optional[DegreeLevel] = None
    ending: Optional[EndingType] = None
    cta: Optional[CtaType] = None


def build_variation_fingerprint(content: "ContentRecord", computed_at: datetime) -> VariationFingerprint:
    """Derive a VariationFingerprint from a ContentRecord's ContentForm. Pure
    mapping, no scoring/comparison -- that is explicitly out of scope for V1."""

    f = content.form_detail
    question_bucket: Optional[DegreeLevel]
    if f.question_count is None:
        question_bucket = None
    elif f.question_count == 0:
        question_bucket = DegreeLevel.NONE
    elif f.question_count == 1:
        question_bucket = DegreeLevel.LOW
    else:
        question_bucket = DegreeLevel.MEDIUM

    return VariationFingerprint(
        content_id=content.content_id,
        computed_at=computed_at,
        form=f.narrative_mode,
        opening=f.opening_type,
        pov=f.point_of_view,
        length=f.length_class,
        rhythm=f.sentence_rhythm,
        emotion=f.emotional_register,
        personal=f.personal_presence,
        question=question_bucket,
        contrast=f.contrast_usage,
        solution=f.solution_degree,
        ending=f.ending_type,
        cta=f.cta_type,
    )


class ContentRecord(BaseModel):
    model_config = {"extra": "forbid"}

    content_id: str
    schema_version: str = Field(default=SCHEMA_VERSION)
    created_at: datetime
    published_at: Optional[datetime] = None

    language: str = Field(description="ISO 639-1 code.")
    market: Optional[str] = None
    platform: Optional[str] = None
    status: ContentStatus = ContentStatus.DRAFT

    idea_id: Optional[str] = Field(default=None, description="TECHNICAL PROPOSAL field -- FK -> Idea.idea_id.")
    angle_id: Optional[str] = Field(default=None, description="TECHNICAL PROPOSAL field -- FK -> Angle.angle_id.")
    voice_core_version_ref: Optional[str] = Field(
        default=None,
        description="TECHNICAL PROPOSAL field -- label like 'voice-core-1.0' this text was authored/judged against.",
    )

    series_ids: list[str] = Field(default_factory=list, description="Series.series_id values.")
    thesis_family_id: Optional[str] = None

    what: ContentWhat = Field(default_factory=ContentWhat)
    form_detail: ContentForm = Field(default_factory=ContentForm)

    reader_effects: list[ReaderEffectAssociation] = Field(default_factory=list)
    variation_fingerprint: Optional[VariationFingerprint] = None

    style_attributes_used: list[str] = Field(default_factory=list, description="StyleAttribute.style_attribute_id values.")
    repetition_signals_observed: list[str] = Field(
        default_factory=list, description="RepetitionSignal.repetition_signal_id values noted present in this text. "
        "Observation storage only -- no measurement is computed here."
    )

    related_content_ids: list[str] = Field(default_factory=list)
    source_ids: list[str] = Field(default_factory=list)

    final_text: Optional[str] = Field(default=None, description="None until the text is finalized.")

    provenance: Provenance
    notes: Optional[str] = None
