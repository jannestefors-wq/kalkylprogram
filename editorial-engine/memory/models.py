"""
Editorial Memory Record models (V1B order section 8-9).

An `EditorialMemoryRecord` is NOT canonical data (order section 8: "Skapa
inte ett parallellt canonical schema bara for Editorial Memory") -- it is a
bounded, technical representation of the 21 content units Work identified in
`LUF_Editorial_Memory_Corpus_Inventory_V1B.md` / `..._Data_Pack_V1B.json`,
built to be as small as possible while keeping `source_facts` (evidence)
structurally separate from `analytical_enrichment` (analysis) -- order
section 9: "Source evidence far aldrig skrivas over av analys."

Reuses existing canonical/engine value objects wherever the data actually
fits them, per order section 8:
    - `schema.Provenance`      -- this record's own ingestion provenance
    - `schema.enums.EvidenceCertainty` -- exactly matches the data pack's
      "strongly_supported" / "analytical_proposal" confidence vocabulary,
      so no parallel confidence enum was created.
    - Thesis Family / Series / Territory relations are plain canonical id
      strings (FKs), never copies of the canonical objects themselves.

Dates (order section 19: "Gissa inga datum") are kept as the raw strings
the data pack already carries -- never parsed into `datetime`, never
back-filled from file/creation metadata. A `None` date means genuinely no
date, not an invitation to estimate one.
"""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from schema import Provenance
from schema.enums import EvidenceCertainty


class TextCompleteness(str, Enum):
    FULL = "full"
    PARTIAL = "partial"


class PublicationStatus(str, Enum):
    """Order section 18: these three states must never collapse into a
    boolean `published = true/false` -- that would destroy real source
    uncertainty. Values match the data pack literally."""

    PUBLISHED_VERIFIED = "published_verified"
    UNVERIFIED_DRAFT_OR_WORK_MATERIAL = "unverified_draft_or_work_material"
    UNKNOWN = "unknown"


class MemoryDates(BaseModel):
    """Every field is a raw string exactly as recorded, or None. No field
    here is ever computed, estimated, or derived from file/conversation
    metadata (order section 19)."""

    model_config = {"extra": "forbid"}

    source_or_created_date: Optional[str] = Field(
        default=None, description="Raw 'source_created' or 'created' date string from the data pack, verbatim."
    )
    verified_publication_date: Optional[str] = Field(
        default=None, description="Only ever set from an explicit verified date in the source data. None in this pack (0 verified dates)."
    )
    publication_window: Optional[str] = Field(
        default=None, description="A free-text approximate window when a source states one (e.g. a screenshot date), "
        "kept separate from verified_publication_date so the two are never confused (order section 19)."
    )


class MemorySourceFacts(BaseModel):
    """Evidence. Immutable once ingested -- `analytical_enrichment` may be
    recomputed/reclassified later without ever touching this object
    (order section 9). `frozen=True` makes this a real technical guarantee.
    not just a documented convention -- mirrors `schema.RawInput`'s own
    `frozen=True` for the identical reason."""

    model_config = {"extra": "forbid", "frozen": True}

    original_text: str = Field(description="Verbatim text as supplied by Work. Never rewritten, shortened, or corrected.")
    text_completeness: TextCompleteness
    language: str
    channel: str = Field(description="e.g. 'work_deck', 'conversation_draft', 'linkedin'.")
    source: str = Field(description="Free-text attribution string, e.g. 'WORK LinkedIn, slide 3'.")
    publication_status: PublicationStatus
    publication_evidence: Optional[str] = None
    dates: MemoryDates = Field(default_factory=MemoryDates)
    url: Optional[str] = Field(default=None, description="Not available in this data pack for any record.")
    post_id: Optional[str] = Field(default=None, description="Not available in this data pack for any record.")


class MemoryRelation(BaseModel):
    """Duplicate/version/adaptation relation between memory records (order
    section 20). Only one instance exists in this corpus: content-other-005's
    documented earlier draft / revised opening."""

    model_config = {"extra": "forbid"}

    type: str
    target: str


class MemoryAnalyticalEnrichment(BaseModel):
    """Analysis. Replaceable, confidence-bound, and structurally separate
    from `MemorySourceFacts` (order section 9). `territory_relation` is
    only ever a real canonical Territory.territory_id or None -- never a
    free-text guess (order section 11)."""

    model_config = {"extra": "forbid"}

    thesis_family_id: Optional[str] = Field(default=None, description="FK -> canonical ThesisFamily.thesis_family_id, or None.")
    series_id: Optional[str] = Field(default=None, description="FK -> canonical Series.series_id, or None.")
    territory_relation: Optional[str] = Field(
        default=None, description="FK -> canonical Territory.territory_id, set only when a deterministic check "
        "(see memory/ingestion.py) actually finds one. Never fabricated."
    )
    topic_labels: list[str] = Field(default_factory=list)
    confidence: EvidenceCertainty = Field(description="Reuses the canonical EvidenceCertainty vocabulary -- no parallel enum.")


class EditorialMemoryRecord(BaseModel):
    model_config = {"extra": "forbid"}

    content_id: str
    source_facts: MemorySourceFacts
    analytical_enrichment: MemoryAnalyticalEnrichment
    relations: list[MemoryRelation] = Field(default_factory=list)
    provenance: Provenance = Field(description="This record's OWN ingestion provenance (who/when/how it entered Editorial Memory).")


EDITORIAL_MEMORY_BOUNDARY_NOTE = (
    "Comparison and retrieval here cover ONLY the bounded Editorial Memory corpus actually "
    "ingested (order section 7) -- not a complete LUF publication history. A result of no match "
    "means no match was found in the available Editorial Memory, never that the idea was 'never "
    "written about' or 'this angle has never been used'."
)
"""Order section 7: 'Detta ska vara tekniskt skyddat, inte bara dokumenterat.' Attached to every
MemoryComparisonResult and MemoryRetrievalResult so the boundary travels with the data, not just
with prose documentation."""
