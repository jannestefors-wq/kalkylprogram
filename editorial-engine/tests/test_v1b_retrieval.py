"""V1B TEST 9, 10, 11 (order section 30)."""

from __future__ import annotations

from engine.models import CanonicalMatch, CanonicalMatchKind, ClassificationOutcome, ClassificationResult, ConfidenceLevel
from memory.ingestion import load_editorial_memory
from memory.retrieval import retrieve_relevant_memory

_CLASSIFICATION_REALITY_BEFORE_STORY = ClassificationResult(
    outcome=ClassificationOutcome.MATCHED,
    thesis_family_matches=[
        CanonicalMatch(
            kind=CanonicalMatchKind.THESIS_FAMILY,
            canonical_id="thesis-reality-before-story-001",
            canonical_name="Verklighet fore berattelse",
            confidence=ConfidenceLevel.HIGH,
            matched_terms=["verklighet"],
            rationale="test fixture",
        )
    ],
)

_NO_MATCH_CLASSIFICATION = ClassificationResult(outcome=ClassificationOutcome.NO_CONFIDENT_CANONICAL_MATCH)


def test_9_retrieval_returns_defensible_relevant_records():
    records = load_editorial_memory()
    result = retrieve_relevant_memory("verklighet fore berattelse och tolkning", _CLASSIFICATION_REALITY_BEFORE_STORY, records)

    matched_ids = {m.content_id for m in result.matches}
    # content-work-001/005/006/012 all carry thesis_family_id == thesis-reality-before-story-001
    assert {"content-work-001", "content-work-005", "content-work-006", "content-work-012"} <= matched_ids


def test_10_every_retrieval_match_explains_why():
    records = load_editorial_memory()
    result = retrieve_relevant_memory("verklighet fore berattelse och tolkning", _CLASSIFICATION_REALITY_BEFORE_STORY, records)

    assert result.matches  # sanity: this scenario does retrieve something
    for match in result.matches:
        assert match.why_retrieved
        assert match.matched_signals
        for signal in match.matched_signals:
            assert signal in match.why_retrieved


def test_11_memory_boundary_note_present_and_never_a_never_published_claim():
    records = load_editorial_memory()
    result = retrieve_relevant_memory("helt ovidkommande text utan overlapp", _NO_MATCH_CLASSIFICATION, records)

    assert result.matches == []
    assert result.boundary_note
    assert "Editorial Memory" in result.boundary_note
    # The note may NAME the forbidden claim in order to forbid it ("never means X"), but must
    # never assert it as a standalone fact ("X.") -- check it appears only inside a negation.
    lowered = result.boundary_note.lower()
    assert "never that the idea was" in lowered  # the negation that makes this safe to name
    assert "never written about" in lowered  # named, so the reader knows exactly what's forbidden
    assert not lowered.rstrip(".").endswith("never written about'")
