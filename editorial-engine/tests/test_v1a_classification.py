"""V1A order TEST 4, 5, 6 -- Canonical Classification."""

from __future__ import annotations

from canonical_data.series_registry import load_series_registry
from canonical_data.territory_registry import load_territory_registry
from canonical_data.thesis_family_registry import load_thesis_family_registry
from engine.classification import classify
from engine.interpretation import build_interpretation_draft, render_idea_interpretation
from engine.models import ClassificationOutcome, ConfidenceLevel
from engine.provider import RuleBasedAnalysisProvider

GOLDEN = "En chef avbröt samma medarbetare tre gånger under mötet."
THIN_GENERIC = "Ett generellt allmant kort meddelande utan konkret innehall alls har."


def _interpretation_text(raw: str) -> str:
    provider = RuleBasedAnalysisProvider()
    draft = build_interpretation_draft(raw, provider)
    interpretation = render_idea_interpretation(draft)
    return " ".join(
        filter(
            None,
            [
                interpretation.observed_situation,
                interpretation.power_dimension,
                interpretation.hidden_conflict,
                interpretation.relationship_dimension,
                interpretation.system_dimension,
                interpretation.possible_consequence,
                *interpretation.possible_root_causes,
            ],
        )
    )


def test_4_thesis_family_match_found_for_golden_path():
    text = _interpretation_text(GOLDEN)
    result = classify(text, load_series_registry(), load_thesis_family_registry(), load_territory_registry())

    assert result.outcome == ClassificationOutcome.MATCHED
    assert result.thesis_family_matches, "expected at least one Thesis Family match"
    valid_ids = {tf.thesis_family_id for tf in load_thesis_family_registry()}
    for match in result.thesis_family_matches:
        assert match.canonical_id in valid_ids
        assert match.matched_terms  # rationale is traceable to real shared words


def test_5_territory_match_found_for_golden_path():
    text = _interpretation_text(GOLDEN)
    result = classify(text, load_series_registry(), load_thesis_family_registry(), load_territory_registry())

    assert result.territory_matches, "expected the 'Makt' territory to match"
    valid_ids = {t.territory_id for t in load_territory_registry()}
    for match in result.territory_matches:
        assert match.canonical_id in valid_ids
    assert any(m.canonical_name == "Makt" for m in result.territory_matches)


def test_6_no_confident_canonical_match_for_generic_text():
    result = classify(THIN_GENERIC, load_series_registry(), load_thesis_family_registry(), load_territory_registry())
    assert result.outcome == ClassificationOutcome.NO_CONFIDENT_CANONICAL_MATCH
    assert result.thesis_family_matches == []
    assert result.territory_matches == []
    assert result.series_matches == []


def test_classification_never_invents_a_new_thesis_family_series_or_territory():
    text = _interpretation_text(GOLDEN)
    result = classify(text, load_series_registry(), load_thesis_family_registry(), load_territory_registry())

    real_thesis_ids = {tf.thesis_family_id for tf in load_thesis_family_registry()}
    real_series_ids = {s.series_id for s in load_series_registry()}
    real_territory_ids = {t.territory_id for t in load_territory_registry()}

    for m in result.thesis_family_matches:
        assert m.canonical_id in real_thesis_ids
    for m in result.series_matches:
        assert m.canonical_id in real_series_ids
    for m in result.territory_matches:
        assert m.canonical_id in real_territory_ids


def test_topic_stays_open_classification_never_assigns_one():
    text = _interpretation_text(GOLDEN)
    result = classify(text, load_series_registry(), load_thesis_family_registry(), load_territory_registry())
    assert result.topic is None


def test_confidence_levels_are_valid_and_distinct_from_canonical_status():
    text = _interpretation_text(GOLDEN)
    result = classify(text, load_series_registry(), load_thesis_family_registry(), load_territory_registry())
    for match in result.thesis_family_matches + result.territory_matches:
        assert match.confidence in (ConfidenceLevel.LOW, ConfidenceLevel.MEDIUM, ConfidenceLevel.HIGH)
        # ConfidenceLevel is a wholly separate enum type from canonical EvidenceCertainty/VoicePrincipleStatus
        from schema.enums import EvidenceCertainty

        assert not isinstance(match.confidence, EvidenceCertainty)
