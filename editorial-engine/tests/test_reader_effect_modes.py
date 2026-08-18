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


def test_g_reader_feedback_can_carry_observed_effects_without_becoming_voice_core(dataset):
    """
    TEST G (V1.1 order): a rich, full-length ReaderFeedback -- standing in for a future
    real review such as Parastoo's -- must be able to (a) carry substantial original text,
    (b) back one or more OBSERVED ReaderEffectAssociations on a ContentRecord, and (c) still
    have no path into the VoicePrinciple/VoiceCoreSnapshot registries. No schema change was
    needed to support a much longer feedback_text than the fixture placeholder currently uses
    (see docs/OPEN_QUESTIONS.md OQ-5 and docs/FINAL_REPORT_V1_1.md item F).
    """
    from schema import ReaderFeedback
    from schema.enums import FeedbackVerificationStatus

    long_feedback = ReaderFeedback(
        reader_feedback_id="RF-TEST-LONG",
        source_id=None,
        content_reference="CONTENT-001",
        feedback_text=(
            "A substantially longer piece of original reader feedback text than the fixture "
            "placeholder uses, to prove no length/shape constraint blocks a real full review "
            "from being attached later. " * 5
        ),
        verification_status=FeedbackVerificationStatus.VERIFIED_VERBATIM,
        effect_observations=["recognition", "discomfort at seeing the pattern named"],
    )
    assert len(long_feedback.feedback_text) > 200

    content_1 = next(c for c in dataset["content_records"] if c.content_id == "CONTENT-001")
    observed = [e for e in content_1.reader_effects if e.mode.value == "observed"]
    assert observed, "content must have at least one OBSERVED reader effect association backed by feedback"
    assert "RF-TEST-ONLY-001" in observed[0].evidence_reader_feedback_ids

    # No field on ReaderFeedback or its usage can register it as a VoicePrinciple/VoiceCoreSnapshot.
    voice_principle_ids = {v.voice_principle_id for v in dataset["voice_principles"]}
    voice_core_snapshot_ids = {s.snapshot_id for s in dataset["voice_core_snapshots"]}
    assert long_feedback.reader_feedback_id not in voice_principle_ids
    assert long_feedback.reader_feedback_id not in voice_core_snapshot_ids
    assert not hasattr(long_feedback, "voice_principle_ids")
    assert not hasattr(long_feedback, "created_by")  # ReaderFeedback carries no Actor/Provenance-shaped field
