"""
IDEA (Beslut 6).

NORMALIZATION FLAG (per permission in Beslut 6 to normalize for data
integrity, without changing meaning):

    The flat field list in Beslut 6 is split into three parts here:

    1. `Idea.raw_input_id` -- a reference to the immutable RawInput row
       (schema/raw_input.py). The literal text never lives mutably on Idea.
    2. `Idea.interpretation` -- an `IdeaInterpretation` sub-object holding
       every analyzed field (observed_situation, human_subject, ...
       possible_consequence). It carries its own provenance so we always
       know *when* the interpretation was made and *which analysis logic
       version* made it (Beslut 5's requirement).
    3. `Idea` itself -- identity, status, and the relational/meta fields
       (related_series, editorial_potential, novelty_risk, status, ...).

    No field from Beslut 6's list was dropped or renamed in meaning; every
    one of them appears below. This split is flagged here and in
    docs/TECHNICAL_PROPOSALS.md for project management sign-off.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from .enums import EditorialPotential, IdeaStatus, InputType, NoveltyRisk
from .provenance import Provenance
from .versioning import SCHEMA_VERSION


class IdeaInterpretation(BaseModel):
    """
    The system's reading of a raw input. Always secondary to, and never a
    substitute for, RawInput.text. Re-analysis creates a NEW
    IdeaInterpretation-bearing Idea revision rather than overwriting this
    object in place -- see docs/VERSIONING_STRATEGY.md.
    """

    model_config = {"extra": "forbid"}

    observed_situation: Optional[str] = None
    human_subject: Optional[str] = Field(
        default=None, description="Who this idea is fundamentally about."
    )
    human_experience: Optional[str] = None
    visible_problem: Optional[str] = None
    hidden_conflict: Optional[str] = None
    possible_root_causes: list[str] = Field(default_factory=list)
    power_dimension: Optional[str] = None
    relationship_dimension: Optional[str] = None
    system_dimension: Optional[str] = None
    possible_consequence: Optional[str] = None

    provenance: Provenance = Field(
        description="Who/what produced this interpretation, when, and under which analysis_logic_version."
    )


class Idea(BaseModel):
    model_config = {"extra": "forbid"}

    idea_id: str
    schema_version: str = Field(default=SCHEMA_VERSION)
    created_at: datetime

    raw_input_id: str = Field(description="FK -> RawInput.raw_input_id. Never an inline copy of the text.")
    input_type: InputType
    source_id: Optional[str] = Field(
        default=None, description="FK -> Source.source_id, if this idea originated from a tracked source."
    )
    language: str = Field(description="ISO 639-1 code of the raw input, e.g. 'sv'.")
    intended_market: Optional[str] = Field(
        default=None, description="Free market code, e.g. 'SE', 'US'. None if not yet decided."
    )

    interpretation: Optional[IdeaInterpretation] = Field(
        default=None,
        description="None until the first analysis pass has run; presence of this object is what "
        "IdeaStatus.ANALYZED means.",
    )

    related_series: list[str] = Field(default_factory=list, description="Series.series_id values.")
    related_thesis_families: list[str] = Field(default_factory=list, description="ThesisFamily.thesis_family_id values.")
    related_models: list[str] = Field(default_factory=list, description="Free identifiers for photo/story models involved.")
    related_characters: list[str] = Field(default_factory=list)
    related_books: list[str] = Field(default_factory=list)
    related_previous_content: list[str] = Field(default_factory=list, description="ContentRecord.content_id values.")

    editorial_potential: Optional[EditorialPotential] = None
    novelty_risk: Optional[NoveltyRisk] = None
    status: IdeaStatus = IdeaStatus.RAW

    notes: Optional[str] = None
