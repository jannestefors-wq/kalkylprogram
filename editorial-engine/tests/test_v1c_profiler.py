"""V1C TEST 1-6, 26 (order section 37)."""

from __future__ import annotations

import pytest

from engine.models import ConfidenceLevel
from memory.ingestion import load_editorial_memory
from memory.models import TextCompleteness
from variation.models import DIMENSION_EVIDENCE_STATUS, OBSERVED_DIMENSIONS, DimensionEvidenceStatus, SourceKind
from variation.profiler import ANALYSIS_LOGIC_VERSION, PartialTextVariationError, build_variation_profile, build_variation_profile_for_memory_record

_FULL_RECORDS = [r for r in load_editorial_memory() if r.source_facts.text_completeness == TextCompleteness.FULL]
_PARTIAL_RECORDS = [r for r in load_editorial_memory() if r.source_facts.text_completeness == TextCompleteness.PARTIAL]


def test_1_variation_profile_built_from_full_text():
    record = next(r for r in _FULL_RECORDS if r.content_id == "content-work-006")
    profile = build_variation_profile_for_memory_record(record)
    assert profile.source_id == "content-work-006"
    assert profile.source_kind == SourceKind.EDITORIAL_MEMORY_RECORD
    for dim in OBSERVED_DIMENSIONS:
        assert getattr(profile, dim).value  # every observed dimension has a value


def test_2_variation_analysis_does_not_change_original_text():
    record = next(r for r in _FULL_RECORDS if r.content_id == "content-work-006")
    text_before = record.source_facts.original_text
    build_variation_profile_for_memory_record(record)
    assert record.source_facts.original_text == text_before


def test_3_partial_record_cannot_be_used_for_full_structural_analysis():
    partial = _PARTIAL_RECORDS[0]
    with pytest.raises(PartialTextVariationError):
        build_variation_profile_for_memory_record(partial)


def test_4_six_observed_dimensions_represented_separately():
    profile = build_variation_profile("Nagot text som ar tillrackligt lang for analys.", "X", SourceKind.CANDIDATE_ANGLE)
    values = profile.observed_values()
    assert set(values) == set(OBSERVED_DIMENSIONS)
    assert len(OBSERVED_DIMENSIONS) == 6


def test_5_unknown_supported_when_evidence_is_thin():
    profile = build_variation_profile("Kort.", "X", SourceKind.CANDIDATE_ANGLE)
    values = profile.observed_values()
    assert "unknown" in values.values()


def test_6_analysis_confidence_is_not_canonical_status():
    profile = build_variation_profile("En chef sa nagot till en medarbetare en gang.", "X", SourceKind.CANDIDATE_ANGLE)
    assert isinstance(profile.entry_mode.confidence, ConfidenceLevel)
    # Confidence lives on the engine-output ConfidenceLevel enum, never on schema.EvidenceCertainty --
    # structurally impossible to confuse with canonical status.
    assert not hasattr(profile.entry_mode, "certainty")


def test_dimension_evidence_status_distinguishes_observed_from_hypothesis():
    assert DIMENSION_EVIDENCE_STATUS["entry_mode"] == DimensionEvidenceStatus.OBSERVED
    assert DIMENSION_EVIDENCE_STATUS["disclosure_pace"] == DimensionEvidenceStatus.SUPPORTED_HYPOTHESIS
    assert "sustained_narrative_form" not in DIMENSION_EVIDENCE_STATUS

    profile = build_variation_profile("Se. Forsta. Agera. Tre ganger hande samma sak pa kontoret.", "X", SourceKind.CANDIDATE_ANGLE)
    assert profile.entry_mode.evidence_status == DimensionEvidenceStatus.OBSERVED
    assert profile.disclosure_pace.evidence_status == DimensionEvidenceStatus.SUPPORTED_HYPOTHESIS


def test_26_analysis_logic_version_present_and_correct():
    profile = build_variation_profile("En text for versionstest med tillrackligt manga ord.", "X", SourceKind.CANDIDATE_ANGLE)
    assert profile.analysis_logic_version == ANALYSIS_LOGIC_VERSION == "variation-v1c-001"
    assert profile.provenance.analysis_logic_version == ANALYSIS_LOGIC_VERSION


def test_hypothesis_dimensions_never_exceed_low_confidence():
    """order section 28: disclosure_pace/emotional_temperature must read as
    less certain than OBSERVED dimensions, structurally, not just by convention."""
    for record in _FULL_RECORDS:
        profile = build_variation_profile_for_memory_record(record)
        assert profile.disclosure_pace.confidence == ConfidenceLevel.LOW
        assert profile.emotional_temperature.confidence == ConfidenceLevel.LOW


def test_all_12_fulltext_records_can_be_profiled():
    assert len(_FULL_RECORDS) == 12
    for record in _FULL_RECORDS:
        profile = build_variation_profile_for_memory_record(record)
        assert profile.source_id == record.content_id
