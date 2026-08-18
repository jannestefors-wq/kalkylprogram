"""
Editorial Memory ingestion (V1B order section 10).

Reads Work's data pack, validates it, and builds the bounded, in-memory
list of `EditorialMemoryRecord`s that retrieval/comparison operate over.
No database, no external storage (order section 10) -- a deterministic,
file-backed, in-memory representation is the whole implementation.

What this module guarantees:
    1. Every canonical Thesis Family / Series id referenced by the pack is
       checked against the REAL canonical_data/ registries (order section
       10 step 4 / TEST 7) -- an unknown id is a hard ingestion error, not
       a silent pass-through, since a broken FK would be worse than
       refusing to ingest.
    2. `source_facts.original_text` is copied verbatim -- never rewritten
       (order section 9).
    3. `publication_status` is preserved as one of its three real values,
       never collapsed into a boolean (order section 18).
    4. `text_completeness` is preserved and later respected by
       retrieval/comparison (order section 6).
    5. Territory relations are set ONLY via the same deterministic,
       transparent word-overlap check already used by
       `engine/classification.py` (order section 11) -- never free
       redactional interpretation. In this corpus it finds zero matches,
       which matches Work's own finding (0 territory relations possible)
       and is reported, not silently accepted as "done."
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from schema import Provenance, Territory
from schema.enums import Actor, EvidenceCertainty

from engine.text_utils import normalize_words

from .models import (
    EditorialMemoryRecord,
    MemoryAnalyticalEnrichment,
    MemoryDates,
    MemoryRelation,
    MemorySourceFacts,
    PublicationStatus,
    TextCompleteness,
)

DEFAULT_DATA_PACK_PATH = Path(__file__).parent / "data" / "LUF_Editorial_Memory_Data_Pack_V1B.json"

INGESTION_METHOD = "v1b_editorial_memory_ingestion"
INGESTION_ACTOR_ID = "work_editorial_memory_data_pack_v1b"
INGESTION_DATE = datetime(2026, 8, 18, tzinfo=timezone.utc)

_CONFIDENCE_MAP = {
    "strongly_supported": EvidenceCertainty.STRONGLY_SUPPORTED,
    "analytical_proposal": EvidenceCertainty.ANALYTICAL_PROPOSAL,
    "verified": EvidenceCertainty.VERIFIED,
    "unconfirmed": EvidenceCertainty.UNCONFIRMED,
}


class MemoryIngestionError(Exception):
    """Raised when the data pack fails structural or canonical-reference validation.
    Never caught-and-guessed -- an invalid pack must fail loudly (order section 10)."""


def load_raw_data_pack(path: Path = DEFAULT_DATA_PACK_PATH) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _dates_from_raw(raw: dict) -> MemoryDates:
    source_or_created = raw.get("source_created") or raw.get("created")
    return MemoryDates(
        source_or_created_date=source_or_created,
        verified_publication_date=raw.get("verified_publication_date"),
        publication_window=raw.get("publication_window"),
    )


def _confidence_from_raw(raw_value: str, content_id: str) -> EvidenceCertainty:
    mapped = _CONFIDENCE_MAP.get(raw_value)
    if mapped is None:
        raise MemoryIngestionError(
            f"{content_id}: unrecognized analytical_enrichment.confidence {raw_value!r} -- refusing to guess a mapping."
        )
    return mapped


def _territory_relation_for(
    original_text: str, topic_labels: list[str], territory_registry: list[Territory]
) -> str | None:
    """Order section 11: the ONLY territory-mapping mechanism allowed here is the
    same deterministic, transparent word-overlap check already used by
    engine/classification.py -- never free redactional interpretation. Checks the
    literal text and topic labels for an exact (case-insensitive, whole-word)
    match against a Territory's name."""

    candidate_words = normalize_words(original_text) | normalize_words(" ".join(topic_labels))
    for territory in territory_registry:
        if normalize_words(territory.name) & candidate_words:
            return territory.territory_id
    return None


def validate_and_build_memory_records(
    raw_pack: dict,
    thesis_family_registry: list,
    series_registry: list,
    territory_registry: list[Territory],
) -> list[EditorialMemoryRecord]:
    known_thesis_family_ids = {tf.thesis_family_id for tf in thesis_family_registry}
    known_series_ids = {s.series_id for s in series_registry}

    records: list[dict] = raw_pack.get("records", [])
    if not records:
        raise MemoryIngestionError("Data pack contains zero records -- refusing to build an empty Editorial Memory silently.")

    seen_ids: set[str] = set()
    result: list[EditorialMemoryRecord] = []

    for raw in records:
        content_id = raw["content_id"]
        if content_id in seen_ids:
            raise MemoryIngestionError(f"Duplicate content_id in data pack: {content_id!r}.")
        seen_ids.add(content_id)

        raw_sf = raw["source_facts"]
        raw_ae = raw["analytical_enrichment"]

        try:
            text_completeness = TextCompleteness(raw["text_completeness"])
        except ValueError as exc:
            raise MemoryIngestionError(f"{content_id}: unrecognized text_completeness {raw['text_completeness']!r}.") from exc

        try:
            publication_status = PublicationStatus(raw_sf["publication_status"])
        except ValueError as exc:
            raise MemoryIngestionError(f"{content_id}: unrecognized publication_status {raw_sf['publication_status']!r}.") from exc

        thesis_family_id = raw_ae.get("thesis_family_id")
        if thesis_family_id and thesis_family_id not in known_thesis_family_ids:
            raise MemoryIngestionError(
                f"{content_id}: thesis_family_id {thesis_family_id!r} is not a known canonical Thesis Family -- "
                "refusing to ingest an unverifiable reference."
            )

        series_id = raw_ae.get("series_id")
        if series_id and series_id not in known_series_ids:
            raise MemoryIngestionError(
                f"{content_id}: series_id {series_id!r} is not a known canonical Series -- refusing to ingest an "
                "unverifiable reference."
            )

        topic_labels = list(raw_ae.get("topic_labels") or [])

        # order section 11: Work left territory_relation null. Only a deterministic
        # check may fill it in; a pack-supplied non-null value is trusted as-is if
        # ever present (it is not, in this pack), but we never invent one ourselves
        # beyond what the deterministic check finds.
        territory_relation = raw_ae.get("territory_relation")
        if territory_relation is None:
            territory_relation = _territory_relation_for(raw_sf["original_text"], topic_labels, territory_registry)

        source_facts = MemorySourceFacts(
            original_text=raw_sf["original_text"],
            text_completeness=text_completeness,
            language=raw_sf["language"],
            channel=raw_sf["channel"],
            source=raw_sf["source"],
            publication_status=publication_status,
            publication_evidence=raw_sf.get("publication_evidence"),
            dates=_dates_from_raw(raw_sf.get("dates") or {}),
            url=raw_sf.get("url"),
            post_id=raw_sf.get("post_id"),
        )

        analytical_enrichment = MemoryAnalyticalEnrichment(
            thesis_family_id=thesis_family_id,
            series_id=series_id,
            territory_relation=territory_relation,
            topic_labels=topic_labels,
            confidence=_confidence_from_raw(raw_ae["confidence"], content_id),
        )

        relations = [MemoryRelation(type=r["type"], target=r["target"]) for r in raw.get("relations", [])]

        provenance = Provenance(
            created_by=Actor.IMPORT,
            actor_id=INGESTION_ACTOR_ID,
            created_at=INGESTION_DATE,
            certainty=EvidenceCertainty.STRONGLY_SUPPORTED,
            method=INGESTION_METHOD,
            analysis_logic_version=None,
            supporting_source_ids=[],
            notes=f"Ingested verbatim from {DEFAULT_DATA_PACK_PATH.name}, record {content_id!r}.",
        )

        result.append(
            EditorialMemoryRecord(
                content_id=content_id,
                source_facts=source_facts,
                analytical_enrichment=analytical_enrichment,
                relations=relations,
                provenance=provenance,
            )
        )

    return result


def load_editorial_memory(path: Path = DEFAULT_DATA_PACK_PATH) -> list[EditorialMemoryRecord]:
    """The one entry point callers (memory/retrieval.py, pipeline.py, tests) should use."""

    from canonical_data.series_registry import load_series_registry
    from canonical_data.territory_registry import load_territory_registry
    from canonical_data.thesis_family_registry import load_thesis_family_registry

    raw_pack = load_raw_data_pack(path)
    return validate_and_build_memory_records(
        raw_pack,
        thesis_family_registry=load_thesis_family_registry(),
        series_registry=load_series_registry(),
        territory_registry=load_territory_registry(),
    )


if __name__ == "__main__":
    records = load_editorial_memory()
    print(f"Loaded {len(records)} Editorial Memory records")
    full = [r for r in records if r.source_facts.text_completeness == TextCompleteness.FULL]
    print(f"  full text: {len(full)}")
    print(f"  territory relations found: {[r.content_id for r in records if r.analytical_enrichment.territory_relation]}")
