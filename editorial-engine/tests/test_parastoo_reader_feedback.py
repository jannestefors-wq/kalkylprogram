"""Final Canonical Data Closure -- Parastoo Ebrahimzadeh's real ReaderFeedback.

Covers the order's minimum tests A-F.
"""

from __future__ import annotations

import pytest

from canonical_data.reader_feedback_registry import (
    BOOK_SOURCE_ID,
    CONTENT_REFERENCE_GAP_SENTINEL,
    READER_FEEDBACK_ID,
    REVIEW_TEXT_PATH,
    load_book_source,
    load_parastoo_reader_feedback,
)
from schema import ReaderEffectAssociation, ReaderFeedback, Source
from schema.enums import FeedbackVerificationStatus, ReaderEffectMode, SourceType
from schema.integrity import check_relations


@pytest.fixture(scope="module")
def parastoo_feedback() -> ReaderFeedback:
    return load_parastoo_reader_feedback()


@pytest.fixture(scope="module")
def book_source() -> Source:
    return load_book_source()


# ---- TEST A: validates ----------------------------------------------------

def test_a_parastoo_reader_feedback_validates(parastoo_feedback):
    assert isinstance(parastoo_feedback, ReaderFeedback)
    # round-trip through JSON to prove full Schema V1.1 validation, not just construction
    assert ReaderFeedback.model_validate_json(parastoo_feedback.model_dump_json()) == parastoo_feedback


def test_a_book_source_validates(book_source):
    assert isinstance(book_source, Source)
    assert Source.model_validate_json(book_source.model_dump_json()) == book_source
    assert book_source.source_type == SourceType.BOOK
    assert book_source.title == "Leadership Without Filter"
    assert book_source.author == "Jan Stefors"


# ---- TEST B: original text preserved exactly -------------------------------

def test_b_original_text_preserved_verbatim(parastoo_feedback):
    raw = REVIEW_TEXT_PATH.read_text(encoding="utf-8").strip("\n")
    assert parastoo_feedback.feedback_text == raw


def test_b_original_text_not_shortened_summarized_or_translated(parastoo_feedback):
    text = parastoo_feedback.feedback_text
    # spot-check several verbatim phrases from across the full review, start to end
    assert text.startswith("Leadership Without Filter was more than just a book")
    assert "There are patterns behind them, and those patterns can be recognized and understood." in text
    assert "His style is sharp, direct, clear, and unapologetically unambiguous." in text
    assert text.endswith("may find something deeply familiar and genuinely illuminating in his writing.")
    # no translation: this is an English review and must stay English (no Swedish injected into the field itself)
    assert "recension" not in text.lower()


def test_b_no_summary_placed_in_the_original_field(parastoo_feedback):
    """The original field must hold the full text, not a shortened stand-in."""
    assert len(parastoo_feedback.feedback_text) > 3000  # the real review is ~3350 chars; a summary would not be


# ---- TEST C: observed, not intended ----------------------------------------

def test_c_reader_feedback_model_has_no_intended_or_mode_field():
    """ReaderFeedback structurally cannot be marked 'intended' -- that concept only exists on
    ReaderEffectAssociation (Beslut 15), which always lives on a ContentRecord, describing what
    the CONTENT creator hoped for. A reader's own feedback is definitionally observed evidence."""
    fields = ReaderFeedback.model_fields
    assert "mode" not in fields
    assert "intended" not in fields


def test_c_association_using_this_feedback_as_evidence_is_only_valid_under_observed(parastoo_feedback):
    """Constructing a ReaderEffectAssociation that cites Parastoo's feedback as evidence is
    semantically correct only under OBSERVED -- proven by building exactly that association
    (a standalone value object; no ContentRecord is fabricated to hold it, see module gap note
    in canonical_data/reader_feedback_registry.py)."""
    association = ReaderEffectAssociation(
        reader_effect_id="RE-002",
        mode=ReaderEffectMode.OBSERVED,
        evidence_reader_feedback_ids=[parastoo_feedback.reader_feedback_id],
    )
    assert association.mode == ReaderEffectMode.OBSERVED
    assert parastoo_feedback.reader_feedback_id in association.evidence_reader_feedback_ids


# ---- TEST D: links to existing Reader Effects -------------------------------

def test_d_feedback_links_to_an_existing_reader_effect(parastoo_feedback, dataset):
    reader_effect_ids = {r.reader_effect_id for r in dataset["reader_effects"]}
    assert "RE-002" in reader_effect_ids  # the effect actually referenced below must exist in the catalog
    assert any("RE-002" in obs for obs in parastoo_feedback.effect_observations)


def test_d_no_effect_asserted_beyond_what_the_text_supports(parastoo_feedback):
    """Only RE-002 is referenced -- RE-001 ('obehag'/discomfort) is NOT asserted, because the
    review's tone is validation/clarity/hope, not discomfort; and no new ReaderEffect (e.g. for
    'reconnecting with one's own judgment', which the text does support but the 2-entry catalog
    has no matching entry for) was invented -- see docs/PARASTOO_INTEGRATION_GAP_REPORT.md."""
    assert len(parastoo_feedback.effect_observations) == 1
    assert "RE-001" not in parastoo_feedback.effect_observations[0]


# ---- TEST E: cannot be mistaken for a VoicePrinciple via relations ----------

def test_e_feedback_id_and_source_id_never_collide_with_voice_principle_ids(parastoo_feedback, book_source, dataset):
    voice_principle_ids = {v.voice_principle_id for v in dataset["voice_principles"]}
    voice_core_snapshot_ids = {s.snapshot_id for s in dataset["voice_core_snapshots"]}
    assert parastoo_feedback.reader_feedback_id not in voice_principle_ids
    assert parastoo_feedback.reader_feedback_id not in voice_core_snapshot_ids
    assert book_source.source_id not in voice_principle_ids


def test_e_no_relation_points_from_voice_core_snapshot_to_this_feedback(parastoo_feedback, dataset):
    """VoiceCoreSnapshot.voice_principle_ids is the only relation VoiceCoreSnapshot has outward;
    it cannot be made to include a ReaderFeedback id without violating check_relations."""
    from schema import VoiceCoreSnapshot

    for snapshot in dataset["voice_core_snapshots"]:
        assert parastoo_feedback.reader_feedback_id not in snapshot.voice_principle_ids

    tampered = VoiceCoreSnapshot.model_validate(
        {**dataset["voice_core_snapshots"][0].model_dump(), "voice_principle_ids": [parastoo_feedback.reader_feedback_id]}
    )
    violations = check_relations({"voice_core_snapshots": [tampered], "voice_principles": dataset["voice_principles"]})
    assert any(v.missing_id == parastoo_feedback.reader_feedback_id for v in violations)


# ---- TEST F: placeholder is separated from canonical data -------------------

def test_f_test_only_placeholder_is_disjoint_from_canonical_reader_feedback(dataset):
    test_only = next(r for r in dataset["reader_feedback"] if r.reader_feedback_id == "RF-TEST-ONLY-001")
    real = next(r for r in dataset["reader_feedback"] if r.reader_feedback_id == READER_FEEDBACK_ID)

    assert test_only.reader_feedback_id != real.reader_feedback_id
    assert "TEST_ONLY" in (test_only.notes or "") or "TEST_ONLY" in (test_only.feedback_text or "")
    assert test_only.feedback_text != real.feedback_text
    assert real.feedback_text not in (test_only.feedback_text or "")


def test_f_no_leftover_rf_001_id_anywhere_in_canonical_data(dataset):
    all_ids = {r.reader_feedback_id for r in dataset["reader_feedback"]}
    assert "RF-001" not in all_ids  # old ambiguous placeholder id fully retired


def test_f_real_reader_feedback_id_is_unambiguous(dataset):
    ids = [r.reader_feedback_id for r in dataset["reader_feedback"]]
    assert ids.count(READER_FEEDBACK_ID) == 1


# ---- content_reference gap: documented, not silently swallowed -------------

def test_content_reference_holds_the_documented_gap_sentinel_not_a_fabricated_id(parastoo_feedback):
    assert parastoo_feedback.content_reference == CONTENT_REFERENCE_GAP_SENTINEL == "UNDERLAG SAKNAS"


def test_source_id_links_to_the_real_book_source(parastoo_feedback, book_source):
    assert parastoo_feedback.source_id == book_source.source_id == BOOK_SOURCE_ID
