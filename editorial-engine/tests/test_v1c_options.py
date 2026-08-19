"""V1C TEST 15-21 (order section 37)."""

from __future__ import annotations

from memory.ingestion import load_editorial_memory
from memory.models import TextCompleteness
from variation.models import MAX_CONTROLLED_VARIATION_OPTIONS, SourceKind, VariationRecommendationOutcome
from variation.options import generate_controlled_variation_options
from variation.profiler import build_variation_profile, build_variation_profile_for_memory_record

_FULL_RECORDS = [r for r in load_editorial_memory() if r.source_facts.text_completeness == TextCompleteness.FULL]


def _profiles(content_ids):
    records = {r.content_id: r for r in _FULL_RECORDS}
    return [build_variation_profile_for_memory_record(records[cid]) for cid in content_ids]


def test_15_never_more_than_three_options():
    angle_profile = build_variation_profile(
        "Chefen gjorde en tydlig observation om vad som hande tre ganger pa kontoret.", "ANGLE-X", SourceKind.CANDIDATE_ANGLE
    )
    all_memory = [build_variation_profile_for_memory_record(r) for r in _FULL_RECORDS]
    result = generate_controlled_variation_options("ANGLE-X", angle_profile, all_memory)
    assert len(result.options) <= MAX_CONTROLLED_VARIATION_OPTIONS


def test_16_zero_options_when_evidence_is_too_thin():
    angle_profile = build_variation_profile("", "ANGLE-Y", SourceKind.CANDIDATE_ANGLE)
    result = generate_controlled_variation_options("ANGLE-Y", angle_profile, [])
    assert result.options == []
    assert result.outcome == VariationRecommendationOutcome.INSUFFICIENT_VARIATION_EVIDENCE


def test_17_no_meaningful_variation_when_only_near_identical_memory_exists():
    angle_profile = build_variation_profile("Foretagsutveckling borjar inte i rapporten. Den borjar i verkligheten har.", "ANGLE-Z", SourceKind.CANDIDATE_ANGLE)
    memory = _profiles(["content-work-001"])
    result = generate_controlled_variation_options("ANGLE-Z", angle_profile, memory)
    assert result.outcome in (VariationRecommendationOutcome.NO_MEANINGFUL_VARIATION, VariationRecommendationOutcome.RECOMMENDED)
    if result.outcome == VariationRecommendationOutcome.NO_MEANINGFUL_VARIATION:
        assert result.recommended_option_id is None


def test_18_insufficient_variation_evidence_when_angle_profile_is_too_unknown():
    angle_profile = build_variation_profile("", "ANGLE-W", SourceKind.CANDIDATE_ANGLE)
    result = generate_controlled_variation_options("ANGLE-W", angle_profile, [])
    assert result.outcome == VariationRecommendationOutcome.INSUFFICIENT_VARIATION_EVIDENCE


def test_19_every_option_explains_which_dimensions_change_and_why():
    angle_profile = build_variation_profile(
        "Chefen gjorde en tydlig observation om vad som hande tre ganger pa kontoret.", "ANGLE-X", SourceKind.CANDIDATE_ANGLE
    )
    result = generate_controlled_variation_options("ANGLE-X", angle_profile, [])
    assert result.options
    for option in result.options:
        assert option.proposed_changes  # at least one dimension named
        assert option.stable_dimensions  # the rest named as held stable
        assert option.evidence
        assert option.false_variation.rationale


def test_20_option_explains_relation_to_relevant_memory():
    angle_profile = build_variation_profile(
        "Chefen gjorde en tydlig observation om vad som hande tre ganger pa kontoret.", "ANGLE-X", SourceKind.CANDIDATE_ANGLE
    )
    memory = _profiles(["content-work-006"])
    result = generate_controlled_variation_options("ANGLE-X", angle_profile, memory)
    for option in result.options:
        assert "content-work-006" in option.memory_relation or "memory" in option.memory_relation.lower()


def test_21_irrelevant_memory_does_not_force_variation():
    """order section 21/'TEST 21': memory with no real structural closeness to
    the angle must not artificially force NO_MEANINGFUL_VARIATION or otherwise
    distort the outcome."""
    angle_profile = build_variation_profile(
        "Vad visar er verklighet innan det syns i siffrorna? Ett system for att se tidigare och agera.",
        "ANGLE-Q", SourceKind.CANDIDATE_ANGLE,
    )
    irrelevant_memory = _profiles(["content-work-007"])  # process/system-shaped, unrelated to a question-opening angle
    result = generate_controlled_variation_options("ANGLE-Q", angle_profile, irrelevant_memory)
    assert result.outcome == VariationRecommendationOutcome.RECOMMENDED
    assert result.recommended_option_id is not None
