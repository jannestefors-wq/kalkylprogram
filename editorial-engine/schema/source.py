"""
SOURCE (Beslut 7).

`Source` holds only what the source itself IS. Any editorial reading of it
(what it means, what it supports) lives on the record that cites it, via
`Provenance.supporting_source_ids` -- never inline on Source. This keeps
"kalla" (source) and "tolkning av kalla" (interpretation of source)
structurally separate, as required.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from .enums import SourceReliability, SourceType, UsageRights
from .versioning import SCHEMA_VERSION


class Source(BaseModel):
    model_config = {"extra": "forbid"}

    source_id: str
    schema_version: str = Field(default=SCHEMA_VERSION)
    source_type: SourceType
    title: str
    author: Optional[str] = None
    date: Optional[datetime] = None
    language: Optional[str] = None
    origin: Optional[str] = Field(default=None, description="Where/how this source was obtained.")
    content_reference: Optional[str] = Field(
        default=None, description="Pointer to the actual material -- file path, URL, or archive id. "
        "Not the material itself."
    )
    themes: list[str] = Field(default_factory=list)
    people: list[str] = Field(default_factory=list)
    models: list[str] = Field(default_factory=list)
    series: list[str] = Field(default_factory=list, description="Series.series_id values this source relates to.")
    reliability: Optional[SourceReliability] = None
    usage_rights: Optional[UsageRights] = None
    notes: Optional[str] = None
