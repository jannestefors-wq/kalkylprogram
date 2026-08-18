"""Beslut 29: 'intended och observed reader effect halls isar'."""

from __future__ import annotations

from schema.enums import ReaderEffectMode


def test_content_record_can_hold_zero_to_n_reader_effects(dataset):
    content_1 = next(c for c in dataset["content_records"] if c.content_id == "CONTENT-001")
    content_2 = next(c for c in dataset["content_records"] if c.content_id == "CONTENT-002")

    assert len(content_1.reader_effects) == 2
    assert len(content_2.reader_effects) == 1


def test_intended_and_observed_are_separately_queryable(dataset):
    content_1 = next(c for c in dataset["content_records"] if c.content_id == "CONTENT-001")

    intended = [e for e in content_1.reader_effects if e.mode == ReaderEffectMode.INTENDED]
    observed = [e for e in content_1.reader_effects if e.mode == ReaderEffectMode.OBSERVED]

    assert len(intended) == 1
    assert len(observed) == 1
    # Same underlying effect can be both intended AND (separately) observed --
    # that duality must survive, not collapse into one row.
    assert intended[0].reader_effect_id == observed[0].reader_effect_id
    assert intended[0].mode != observed[0].mode


def test_observed_effect_carries_evidence_intended_does_not_require_it(dataset):
    content_1 = next(c for c in dataset["content_records"] if c.content_id == "CONTENT-001")
    observed = next(e for e in content_1.reader_effects if e.mode == ReaderEffectMode.OBSERVED)
    intended = next(e for e in content_1.reader_effects if e.mode == ReaderEffectMode.INTENDED)

    assert len(observed.evidence_reader_feedback_ids) >= 1
    assert intended.evidence_reader_feedback_ids == []


def test_reader_feedback_is_evidence_not_a_voice_principle(dataset):
    """Beslut 16: reader reactions must never be hardcoded as Voice Core."""
    reader_feedback_ids = {r.reader_feedback_id for r in dataset["reader_feedback"]}
    voice_principle_ids = {v.voice_principle_id for v in dataset["voice_principles"]}

    assert reader_feedback_ids.isdisjoint(voice_principle_ids)
    for rf in dataset["reader_feedback"]:
        assert not hasattr(rf, "status")  # no VoicePrincipleStatus-shaped field exists on ReaderFeedback
