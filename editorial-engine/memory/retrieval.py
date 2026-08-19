"""
Editorial Memory Retrieval (V1B order section 13).

The smallest transparent retrieval logic that works: no embeddings, no
vector database, no RAG, no external search service (order section 13/28
-- a hard boundary). Every retrieved record carries an explicit,
human-readable reason built from the actual signals that fired, so
"why was this hit found?" is always answerable by reading the result, not
by trusting an opaque score.

Signals used (all explainable, order section 13):
    - shared Thesis Family id with the classification result
    - shared Territory id with the classification result
    - shared topic label (case-insensitive exact match against the memory
      record's own topic_labels)
    - shared literal word between the interpretation text and the memory
      record's original_text (same `normalize_words` approach already used
      by engine/classification.py and engine/comparison.py -- no new
      matching algorithm invented for V1B)

No fabricated precision: there is no numeric similarity score anywhere in
this module (order section 14: "Ingen dold 0.873 similarity score").
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from engine.models import ClassificationResult
from engine.text_utils import normalize_words

from .models import EDITORIAL_MEMORY_BOUNDARY_NOTE, EditorialMemoryRecord


class MemoryRetrievalMatch(BaseModel):
    model_config = {"extra": "forbid"}

    content_id: str
    matched_signals: list[str] = Field(default_factory=list, description="e.g. 'thesis_family:thesis-symptom-cause-001', 'term:symptom'.")
    why_retrieved: str


class MemoryRetrievalResult(BaseModel):
    model_config = {"extra": "forbid"}

    matches: list[MemoryRetrievalMatch] = Field(default_factory=list)
    corpus_size: int = Field(description="How many Editorial Memory records were actually considered.")
    boundary_note: str = Field(default=EDITORIAL_MEMORY_BOUNDARY_NOTE)


def retrieve_relevant_memory(
    raw_text: str,
    classification: ClassificationResult,
    memory_records: list[EditorialMemoryRecord],
) -> MemoryRetrievalResult:
    """V1B Correction Order (Defect 2): topic/term signals are matched against
    `raw_text` (what the human actually wrote), not the provider's generated
    interpretation text -- see memory/comparison.py's module-level note for why."""

    text_words = normalize_words(raw_text)
    classified_thesis_family_ids = {m.canonical_id for m in classification.thesis_family_matches}
    classified_territory_ids = {m.canonical_id for m in classification.territory_matches}

    matches: list[MemoryRetrievalMatch] = []
    for record in memory_records:
        signals: list[str] = []

        tf_id = record.analytical_enrichment.thesis_family_id
        if tf_id and tf_id in classified_thesis_family_ids:
            signals.append(f"thesis_family:{tf_id}")

        territory_id = record.analytical_enrichment.territory_relation
        if territory_id and territory_id in classified_territory_ids:
            signals.append(f"territory:{territory_id}")

        record_topic_words = {t.lower() for t in record.analytical_enrichment.topic_labels}
        shared_topics = record_topic_words & {w for w in text_words}
        if shared_topics:
            signals.extend(f"topic:{t}" for t in sorted(shared_topics))

        record_text_words = normalize_words(record.source_facts.original_text)
        shared_terms = sorted(record_text_words & text_words)
        if shared_terms:
            signals.extend(f"term:{t}" for t in shared_terms)

        if signals:
            matches.append(
                MemoryRetrievalMatch(
                    content_id=record.content_id,
                    matched_signals=signals,
                    why_retrieved="Hamtad pa grund av: " + "; ".join(signals) + ".",
                )
            )

    return MemoryRetrievalResult(matches=matches, corpus_size=len(memory_records))
