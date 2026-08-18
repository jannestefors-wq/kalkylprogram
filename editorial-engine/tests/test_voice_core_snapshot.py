"""V1.1, OQ-1: VoiceCoreSnapshot.

TEST C: a VoiceCoreSnapshot with valid VoicePrinciple references passes.
TEST D: a VoiceCoreSnapshot with an invalid VoicePrinciple id is caught.
"""

from __future__ import annotations

from schema.integrity import check_relations


def test_c_fixture_voice_core_snapshot_has_valid_principle_references(dataset):
    snapshot = next(s for s in dataset["voice_core_snapshots"] if s.snapshot_id == "SNAP-001")
    voice_principle_ids = {p.voice_principle_id for p in dataset["voice_principles"]}

    assert snapshot.voice_principle_ids, "snapshot must reference at least one principle"
    assert set(snapshot.voice_principle_ids).issubset(voice_principle_ids)

    violations = check_relations(dataset)
    assert not any(v.object_type == "VoiceCoreSnapshot" for v in violations)


def test_c_snapshot_references_exactly_the_eight_canonical_principles(dataset):
    from schema.enums import VoicePrincipleStatus

    snapshot = next(s for s in dataset["voice_core_snapshots"] if s.snapshot_id == "SNAP-001")
    canonical_ids = {p.voice_principle_id for p in dataset["voice_principles"] if p.status == VoicePrincipleStatus.CANONICAL}
    assert set(snapshot.voice_principle_ids) == canonical_ids
    assert len(snapshot.voice_principle_ids) == 8


def test_d_snapshot_with_invalid_principle_id_is_caught_by_integrity_checker(dataset):
    broken = dict(dataset)
    broken_snapshot = broken["voice_core_snapshots"][0].model_copy(
        update={"voice_principle_ids": ["VP-DOES-NOT-EXIST"]}
    )
    broken["voice_core_snapshots"] = [broken_snapshot]

    violations = check_relations(broken)

    assert any(v.object_type == "VoiceCoreSnapshot" and v.missing_id == "VP-DOES-NOT-EXIST" for v in violations)


def test_snapshot_does_not_duplicate_principle_text(dataset):
    """Beslut (V1.1, section 2): snapshot must reference, not duplicate, principle content."""
    snapshot = next(s for s in dataset["voice_core_snapshots"] if s.snapshot_id == "SNAP-001")
    assert not hasattr(snapshot, "definitions")
    assert not hasattr(snapshot, "principle_texts")
    # only ids are carried
    assert all(isinstance(pid, str) for pid in snapshot.voice_principle_ids)


def test_content_record_and_quality_assessment_reference_snapshot_not_a_free_label(dataset):
    content_1 = next(c for c in dataset["content_records"] if c.content_id == "CONTENT-001")
    qa = dataset["quality_assessments"][0]
    snapshot_ids = {s.snapshot_id for s in dataset["voice_core_snapshots"]}

    assert content_1.voice_core_snapshot_id in snapshot_ids
    assert qa.voice_core_snapshot_id in snapshot_ids
