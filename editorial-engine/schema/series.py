"""
SERIES REGISTRY and THESIS FAMILY (Beslut 17, 18).

Series must never be conflated with topic, territory, or form (Beslut 17
example: "Tillit" = topic, "Kaera ..." = series, "Det langa spelet" =
series with a time perspective, "Makt" = territory).

This module keeps that boundary structural, not just documented:

    - `Series` is the only heavyweight canonical registry object for this
      axis (Fas 0 identified 16 of them). It has a `role` (SeriesRole) so
      that two series which look similar are not assumed to behave alike.
    - `topic` and `territory` are deliberately NOT modelled as their own
      entity tables in V1. They are open, freeform string tags living on
      IDEA and CONTENT RECORD (see idea.py / content.py), documented as a
      controlled vocabulary in docs/ENUMS_TAXONOMIES.md. Promoting them to
      full entities is listed as a TECHNICAL PROPOSAL if/when they need
      their own metadata (see docs/TECHNICAL_PROPOSALS.md) -- doing it now
      would be exactly the "monster" Beslut 26 warns against for a V1.
    - `form` is not a registry at all; it is the FORM variation dimension
      (enums.VariationDimension) plus the structural fields already on
      ContentRecord (form, narrative_mode, ...).
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from .enums import SeriesRole
from .provenance import Provenance
from .versioning import SCHEMA_VERSION


class Series(BaseModel):
    model_config = {"extra": "forbid"}

    series_id: str
    schema_version: str = Field(default=SCHEMA_VERSION)
    name: str
    role: SeriesRole
    description: Optional[str] = None
    created_at: datetime
    provenance: Provenance
    active: bool = True


class ThesisFamily(BaseModel):
    """
    Beslut 18: represents one of the eight recurring core-thesis families
    identified in Fas 0, distinct from any single content's `core_thesis`
    string. A ContentRecord's core_thesis is free text; `thesis_family_id`
    on ContentRecord is what lets a later component notice "this wording is
    new, but it belongs to an old family" without yet building the matching
    algorithm itself.
    """

    model_config = {"extra": "forbid"}

    thesis_family_id: str
    schema_version: str = Field(default=SCHEMA_VERSION)
    name: str
    core_statement: str = Field(description="The canonical, family-level formulation of the thesis.")
    description: Optional[str] = None
    example_phrasings: list[str] = Field(
        default_factory=list, description="Known past surface formulations belonging to this family."
    )
    created_at: datetime
    provenance: Provenance
    active: bool = True
