"""V1B TEST 1, 4, 5, 6, 7, 8 (order section 30)."""

from __future__ import annotations

import pydantic
import pytest

from canonical_data.territory_registry import load_territory_registry
from canonical_data.thesis_family_registry import load_thesis_family_registry
from canonical_data.series_registry import load_series_registry
from memory.ingestion import MemoryIngestionError, _territory_relation_for, load_editorial_memory, validate_and_build_memory_records
from memory.models import PublicationStatus, TextCompleteness


def test_1_ingestion_reads_and_validates_all_21_records():
    records = load_editorial_memory()
    assert len(records) == 21
    ids = {r.content_id for r in records}
    assert len(ids) == 21  # no duplicates
    for r in records:
        assert r.source_facts.original_text
        assert r.source_facts.text_completeness in (TextCompleteness.FULL, TextCompleteness.PARTIAL)
        assert r.source_facts.publication_status in (
            PublicationStatus.PUBLISHED_VERIFIED,
            PublicationStatus.UNVERIFIED_DRAFT_OR_WORK_MATERIAL,
            PublicationStatus.UNKNOWN,
        )


def test_4_unverified_work_material_is_not_treated_as_published():
    records = load_editorial_memory()
    work_records = [r for r in records if r.content_id.startswith("content-work-")]
    assert len(work_records) == 12
    for r in work_records:
        assert r.source_facts.publication_status == PublicationStatus.UNVERIFIED_DRAFT_OR_WORK_MATERIAL
        assert r.source_facts.publication_status != PublicationStatus.PUBLISHED_VERIFIED


def test_5_unknown_status_is_not_auto_published_or_unpublished():
    records = load_editorial_memory()
    unknown_records = [r for r in records if r.source_facts.publication_status == PublicationStatus.UNKNOWN]
    assert len(unknown_records) == 6
    for r in unknown_records:
        # The type system itself forbids collapsing this into a boolean -- there is no
        # boolean "published" field anywhere on MemorySourceFacts.
        assert not hasattr(r.source_facts, "published")


def test_6_source_facts_are_immutable():
    records = load_editorial_memory()
    record = records[0]
    with pytest.raises(pydantic.ValidationError):
        record.source_facts.original_text = "Nagot annat."


def test_6_analytical_enrichment_can_change_without_touching_source_facts():
    records = load_editorial_memory()
    record = records[0]
    original_text_before = record.source_facts.original_text
    # Re-classification is a NEW object, never a mutation of the existing one.
    from memory.models import EvidenceCertainty, MemoryAnalyticalEnrichment

    new_enrichment = MemoryAnalyticalEnrichment(
        thesis_family_id=record.analytical_enrichment.thesis_family_id,
        series_id=None,
        territory_relation=None,
        topic_labels=["ny_klassificering"],
        confidence=EvidenceCertainty.ANALYTICAL_PROPOSAL,
    )
    assert record.source_facts.original_text == original_text_before
    assert new_enrichment.topic_labels != record.analytical_enrichment.topic_labels


def test_7_canonical_references_are_validated_against_real_registries():
    thesis_family_registry = load_thesis_family_registry()
    series_registry = load_series_registry()
    territory_registry = load_territory_registry()
    known_tf_ids = {tf.thesis_family_id for tf in thesis_family_registry}
    known_series_ids = {s.series_id for s in series_registry}

    records = load_editorial_memory()
    for r in records:
        if r.analytical_enrichment.thesis_family_id:
            assert r.analytical_enrichment.thesis_family_id in known_tf_ids
        if r.analytical_enrichment.series_id:
            assert r.analytical_enrichment.series_id in known_series_ids


def test_7_unknown_canonical_reference_raises_ingestion_error():
    bad_pack = {
        "records": [
            {
                "content_id": "content-fake-001",
                "text_completeness": "full",
                "source_facts": {
                    "original_text": "Text.",
                    "language": "sv",
                    "channel": "work_deck",
                    "publication_status": "unknown",
                    "dates": {},
                },
                "analytical_enrichment": {
                    "thesis_family_id": "thesis-does-not-exist-999",
                    "series_id": None,
                    "territory_relation": None,
                    "topic_labels": [],
                    "confidence": "strongly_supported",
                },
            }
        ]
    }
    with pytest.raises(MemoryIngestionError):
        validate_and_build_memory_records(
            bad_pack,
            thesis_family_registry=load_thesis_family_registry(),
            series_registry=load_series_registry(),
            territory_registry=load_territory_registry(),
        )


def test_8_territory_relation_null_when_no_deterministic_match():
    records = load_editorial_memory()
    for r in records:
        assert r.analytical_enrichment.territory_relation is None


def test_8_territory_deterministic_check_actually_works():
    """Proves test_8 above passes because there is genuinely no match in this
    corpus -- not because the checker function is broken."""
    territory_registry = load_territory_registry()
    result = _territory_relation_for("Detta handlar om makt i organisationen.", [], territory_registry)
    assert result == "TER-001"

    result_no_match = _territory_relation_for("Detta handlar om ingenting relevant.", [], territory_registry)
    assert result_no_match is None
