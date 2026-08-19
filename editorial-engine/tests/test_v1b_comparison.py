"""V1B TEST 2, 3, 15, 16 (order section 30)."""

from __future__ import annotations

from engine.models import ClassificationOutcome, ClassificationResult
from memory.comparison import compare_to_editorial_memory
from memory.ingestion import load_editorial_memory
from memory.models import TextCompleteness

_NO_MATCH_CLASSIFICATION = ClassificationResult(outcome=ClassificationOutcome.NO_CONFIDENT_CANONICAL_MATCH)


def test_2_fulltext_comparison_corpus_is_exactly_the_12_work_records():
    records = load_editorial_memory()
    fulltext_ids = {r.content_id for r in records if r.source_facts.text_completeness == TextCompleteness.FULL}
    expected = {f"content-work-{i:03d}" for i in range(1, 13)}
    assert fulltext_ids == expected


def test_3_partial_records_never_produce_text_overlap_terms():
    records = load_editorial_memory()
    partial_record = next(r for r in records if r.content_id == "content-other-001")
    assert partial_record.source_facts.text_completeness == TextCompleteness.PARTIAL

    # "manniska" appears literally in content-other-001's partial original_text,
    # but partial text must never be used for literal text-overlap comparison.
    raw_text = "En manniska kande sig osedd i mötet."
    result = compare_to_editorial_memory(raw_text, _NO_MATCH_CLASSIFICATION, [partial_record])

    for match in result.matches:
        assert match.text_overlap_terms == []


def test_15_fulltext_overlap_only_computed_for_full_records():
    records = load_editorial_memory()
    full_record = next(r for r in records if r.content_id == "content-work-006")  # "Observation fore tolkning..."
    partial_record = next(r for r in records if r.content_id == "content-other-001")

    raw_text = "Observation och tolkning skiljer sig at i motet."
    result = compare_to_editorial_memory(raw_text, _NO_MATCH_CLASSIFICATION, [full_record, partial_record])

    full_match = next((m for m in result.matches if m.content_id == "content-work-006"), None)
    assert full_match is not None
    assert full_match.text_overlap_terms  # real literal overlap computed for a FULL record

    assert result.fulltext_corpus_size == 1


def test_16_version_revision_relation_is_preserved_as_one_record():
    records = load_editorial_memory()
    matching = [r for r in records if r.content_id == "content-other-005"]
    assert len(matching) == 1  # not split into two independent ideas
    record = matching[0]
    assert len(record.relations) == 1
    assert record.relations[0].type == "version_revision"


def test_evidence_boundary_note_differs_by_publication_status():
    records = load_editorial_memory()
    work = next(r for r in records if r.content_id == "content-work-001")
    published = next(r for r in records if r.content_id == "content-published-003")
    unknown = next(r for r in records if r.content_id == "content-other-001")

    raw_text = "foretagsutveckling verklighet rost tystnad truth leadership"
    result = compare_to_editorial_memory(raw_text, _NO_MATCH_CLASSIFICATION, [work, published, unknown])

    notes = {m.content_id: m.evidence_boundary_note for m in result.matches}
    if "content-work-001" in notes:
        assert "INTE" in notes["content-work-001"] or "arbetsmaterialet" in notes["content-work-001"]
    if "content-published-003" in notes:
        assert "publiceringsevidens" in notes["content-published-003"]
    if "content-other-001" in notes:
        assert "unknown" in notes["content-other-001"].lower() or "varken" in notes["content-other-001"]
