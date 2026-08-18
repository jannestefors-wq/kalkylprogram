"""V1A order TEST 7, 8 -- Existing Content Comparison + memory limitation."""

from __future__ import annotations

from canonical_data.series_registry import load_series_registry
from canonical_data.territory_registry import load_territory_registry
from canonical_data.thesis_family_registry import load_thesis_family_registry
from engine.classification import classify
from engine.comparison import compare_to_existing_content
from engine.interpretation import build_interpretation_draft, render_idea_interpretation
from engine.models import NEVER_PUBLISHED_CLAIM_FORBIDDEN_NOTE, ComparisonOutcome
from engine.provider import RuleBasedAnalysisProvider

GOLDEN = "En chef avbröt samma medarbetare tre gånger under mötet."

# These are the AFFIRMATIVE forms the note must never take (asserting non-publication as fact).
# "X is not evidence that it was never published" is fine -- it explicitly negates the claim.
FORBIDDEN_AFFIRMATIVE_PHRASES = ["har aldrig publicerats", "aldrig publicerat", "we have never published this"]


def _classification_and_text(raw: str):
    provider = RuleBasedAnalysisProvider()
    draft = build_interpretation_draft(raw, provider)
    interpretation = render_idea_interpretation(draft)
    text = " ".join(
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
    classification = classify(text, load_series_registry(), load_thesis_family_registry(), load_territory_registry())
    return classification, text


def test_7_existing_content_comparison_finds_relevant_nearby_material(dataset):
    classification, text = _classification_and_text(GOLDEN)
    result = compare_to_existing_content(text, classification, dataset["content_records"])

    assert result.outcome == ComparisonOutcome.MATCHES_FOUND
    assert result.matches
    valid_ids = {c.content_id for c in dataset["content_records"]}
    for m in result.matches:
        assert m.content_id in valid_ids
        assert m.shared_thesis_family_ids or m.shared_territory_ids or m.shared_terms  # traceable, not asserted blindly


def test_8_no_match_is_never_phrased_as_never_published(dataset):
    classification, text = _classification_and_text(GOLDEN)

    empty_result = compare_to_existing_content(text, classification, [])
    assert empty_result.outcome == ComparisonOutcome.NO_MATCH_IN_AVAILABLE_MEMORY

    note = empty_result.memory_limitation_note.lower()
    for phrase in FORBIDDEN_AFFIRMATIVE_PHRASES:
        assert phrase not in note

    # the note may discuss the forbidden claim, but only to explicitly negate it
    assert "not evidence" in note or "inte bevis" in note

    assert empty_result.memory_limitation_note == NEVER_PUBLISHED_CLAIM_FORBIDDEN_NOTE


def test_8_memory_limitation_note_present_even_when_matches_are_found(dataset):
    """The caveat travels with every result, not only the empty-corpus case."""
    classification, text = _classification_and_text(GOLDEN)
    result = compare_to_existing_content(text, classification, dataset["content_records"])
    assert result.memory_limitation_note == NEVER_PUBLISHED_CLAIM_FORBIDDEN_NOTE


def test_8_corpus_size_is_reported_so_the_scope_of_the_claim_is_visible():
    classification, text = _classification_and_text(GOLDEN)
    result = compare_to_existing_content(text, classification, [])
    assert result.corpus_size == 0
