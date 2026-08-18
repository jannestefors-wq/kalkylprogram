"""
Editorial Memory Comparison (V1B order section 14).

Takes retrieval's hits and turns them into a richer, still fully
explainable comparison result: WHY each match is relevant, which canonical
relations overlap, which text actually overlaps (only ever computed for
`text_completeness == FULL` records -- order section 5/6/15), and an
explicit per-match evidence boundary note driven by `publication_status`
(order section 18) so a caller can never conflate "we have full text of a
draft" with "we know this was published."

Reuses the same outcome vocabulary as V1A (`MATCHES_FOUND` /
`NO_MATCH_IN_AVAILABLE_MEMORY`, order section 7: "eller befintlig
V1A-representation") without importing engine/models.py's classes directly
-- this result carries strictly more fields than V1A's `ComparisonResult`,
so it is its own type. See `memory/bridge.py` for the adapter that lets the
UNCHANGED V1A `angles.py`/`recommendation.py` consume it.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field

from engine.models import NEVER_PUBLISHED_CLAIM_FORBIDDEN_NOTE, ClassificationResult
from engine.text_utils import normalize_words

from .models import EDITORIAL_MEMORY_BOUNDARY_NOTE, EditorialMemoryRecord, PublicationStatus, TextCompleteness

_EVIDENCE_BOUNDARY_BY_STATUS = {
    PublicationStatus.PUBLISHED_VERIFIED: (
        "Publiceringsstatus ar published_verified -- kan anvandas som verklig publiceringsevidens."
    ),
    PublicationStatus.UNVERIFIED_DRAFT_OR_WORK_MATERIAL: (
        "Publiceringsstatus ar unverified_draft_or_work_material -- kan anvandas som evidens for att "
        "innehallet finns i arbetsmaterialet, INTE som bevis for publicering."
    ),
    PublicationStatus.UNKNOWN: (
        "Publiceringsstatus ar unknown -- varken publicerat eller opublicerat far antas."
    ),
}


class MemoryComparisonOutcome(str, Enum):
    MATCHES_FOUND = "MATCHES_FOUND"
    NO_MATCH_IN_AVAILABLE_MEMORY = "NO_MATCH_IN_AVAILABLE_MEMORY"


class MemoryComparisonMatch(BaseModel):
    model_config = {"extra": "forbid"}

    content_id: str
    why_relevant: str
    shared_thesis_family_ids: list[str] = Field(default_factory=list)
    shared_territory_ids: list[str] = Field(default_factory=list)
    topic_overlap: list[str] = Field(default_factory=list)
    text_overlap_terms: list[str] = Field(
        default_factory=list, description="Only ever populated when text_completeness == FULL; empty for partial records, never guessed."
    )
    text_completeness: TextCompleteness
    publication_status: PublicationStatus
    evidence_boundary_note: str
    repetition_signal_strength: str = Field(description="'strong' (shared canonical relation), 'weak' (term/topic overlap only), or 'none'.")


class MemoryComparisonResult(BaseModel):
    model_config = {"extra": "forbid"}

    outcome: MemoryComparisonOutcome
    matches: list[MemoryComparisonMatch] = Field(default_factory=list)
    corpus_size: int
    fulltext_corpus_size: int = Field(description="How many of the compared records actually had text_completeness == FULL.")
    memory_limitation_note: str = Field(default=EDITORIAL_MEMORY_BOUNDARY_NOTE)
    canonical_memory_limitation_note: str = Field(
        default=NEVER_PUBLISHED_CLAIM_FORBIDDEN_NOTE,
        description="Reuses V1A's exact forbidden-claim note verbatim, not a rephrased copy.",
    )


def compare_to_editorial_memory(
    interpretation_text: str,
    classification: ClassificationResult,
    memory_records: list[EditorialMemoryRecord],
) -> MemoryComparisonResult:
    text_words = normalize_words(interpretation_text)
    classified_thesis_family_ids = {m.canonical_id for m in classification.thesis_family_matches}
    classified_territory_ids = {m.canonical_id for m in classification.territory_matches}

    matches: list[MemoryComparisonMatch] = []
    fulltext_considered = 0

    for record in memory_records:
        sf = record.source_facts
        ae = record.analytical_enrichment
        if sf.text_completeness == TextCompleteness.FULL:
            fulltext_considered += 1

        shared_thesis = {ae.thesis_family_id} & classified_thesis_family_ids if ae.thesis_family_id else set()
        shared_territory = {ae.territory_relation} & classified_territory_ids if ae.territory_relation else set()

        record_topic_words = {t.lower() for t in ae.topic_labels}
        topic_overlap = sorted(record_topic_words & text_words)

        text_overlap_terms: list[str] = []
        if sf.text_completeness == TextCompleteness.FULL:
            text_overlap_terms = sorted(normalize_words(sf.original_text) & text_words)

        if not (shared_thesis or shared_territory or topic_overlap or text_overlap_terms):
            continue

        reasons = []
        if shared_thesis:
            reasons.append(f"delad Thesis Family ({', '.join(sorted(shared_thesis))})")
        if shared_territory:
            reasons.append(f"delat Territory ({', '.join(sorted(shared_territory))})")
        if topic_overlap:
            reasons.append(f"delade topic labels ({', '.join(topic_overlap)})")
        if text_overlap_terms:
            reasons.append(f"delade termer i fulltext ({', '.join(text_overlap_terms)})")
        elif sf.text_completeness == TextCompleteness.PARTIAL:
            reasons.append("OBS: endast partiell text tillganglig -- ingen fulltext-jamforelse gjord")

        strength = "strong" if (shared_thesis or shared_territory) else ("weak" if (topic_overlap or text_overlap_terms) else "none")

        matches.append(
            MemoryComparisonMatch(
                content_id=record.content_id,
                why_relevant="Narliggande pa grund av: " + "; ".join(reasons) + ".",
                shared_thesis_family_ids=sorted(shared_thesis),
                shared_territory_ids=sorted(shared_territory),
                topic_overlap=topic_overlap,
                text_overlap_terms=text_overlap_terms,
                text_completeness=sf.text_completeness,
                publication_status=sf.publication_status,
                evidence_boundary_note=_EVIDENCE_BOUNDARY_BY_STATUS[sf.publication_status],
                repetition_signal_strength=strength,
            )
        )

    outcome = MemoryComparisonOutcome.MATCHES_FOUND if matches else MemoryComparisonOutcome.NO_MATCH_IN_AVAILABLE_MEMORY

    return MemoryComparisonResult(
        outcome=outcome,
        matches=matches,
        corpus_size=len(memory_records),
        fulltext_corpus_size=fulltext_considered,
    )
