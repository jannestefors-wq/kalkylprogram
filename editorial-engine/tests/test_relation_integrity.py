"""Beslut 29: 'invalid relation IDs fangas'."""

from __future__ import annotations

from schema.integrity import check_relations


def test_fixture_dataset_has_no_dangling_relations(dataset):
    violations = check_relations(dataset)
    assert violations == [], f"Unexpected dangling references in fixture dataset: {violations}"


def test_checker_catches_a_deliberately_broken_reference(dataset):
    broken = dict(dataset)
    broken_content = broken["content_records"][0].model_copy(update={"thesis_family_id": "TF-DOES-NOT-EXIST"})
    broken["content_records"] = [broken_content, *broken["content_records"][1:]]

    violations = check_relations(broken)

    assert len(violations) == 1
    assert violations[0].missing_id == "TF-DOES-NOT-EXIST"
    assert violations[0].object_type == "ContentRecord"


def test_checker_catches_a_broken_reader_effect_reference(dataset):
    from schema import ReaderEffectAssociation
    from schema.enums import ReaderEffectMode

    broken = dict(dataset)
    broken_content = broken["content_records"][0].model_copy(
        update={
            "reader_effects": [
                ReaderEffectAssociation(reader_effect_id="RE-DOES-NOT-EXIST", mode=ReaderEffectMode.INTENDED)
            ]
        }
    )
    broken["content_records"] = [broken_content, *broken["content_records"][1:]]

    violations = check_relations(broken)
    assert any(v.missing_id == "RE-DOES-NOT-EXIST" for v in violations)
