"""V1.1, OQ-3: Territory is its own canonical register.

TEST E: ContentRecord with a valid Territory reference passes.
TEST F: an invalid Territory reference is caught.
"""

from __future__ import annotations

from schema.integrity import check_relations


def test_e_content_record_with_valid_territory_reference_passes(dataset):
    content_1 = next(c for c in dataset["content_records"] if c.content_id == "CONTENT-001")
    territory_ids = {t.territory_id for t in dataset["territories"]}

    assert content_1.territory_ids
    assert set(content_1.territory_ids).issubset(territory_ids)

    violations = check_relations(dataset)
    assert not any(v.object_type == "ContentRecord" and "territory" in v.field for v in violations)


def test_f_content_record_with_invalid_territory_reference_is_caught(dataset):
    broken = dict(dataset)
    broken_content = broken["content_records"][0].model_copy(update={"territory_ids": ["TER-DOES-NOT-EXIST"]})
    broken["content_records"] = [broken_content, *broken["content_records"][1:]]

    violations = check_relations(broken)

    assert any(v.field == "territory_ids" and v.missing_id == "TER-DOES-NOT-EXIST" for v in violations)


def test_territory_is_not_a_series_or_a_free_topic_string(dataset):
    """Beslut 17 / V1.1 OQ-3: territory must never be conflated with series or with the
    open 'topic' free-text field."""
    content_1 = next(c for c in dataset["content_records"] if c.content_id == "CONTENT-001")
    series_ids = {s.series_id for s in dataset["series"]}
    territory_ids = {t.territory_id for t in dataset["territories"]}

    assert territory_ids.isdisjoint(series_ids)
    assert set(content_1.territory_ids).isdisjoint(set(content_1.series_ids))
    # topic stays a free string, never a territory_id
    assert content_1.what.topic not in territory_ids


def test_topic_remains_open_free_text_in_v1_1(dataset):
    """Section 12 of the V1.1 order: 'topic' far fortsatt vara oppet/fri text."""
    content_1 = next(c for c in dataset["content_records"] if c.content_id == "CONTENT-001")
    content_2 = next(c for c in dataset["content_records"] if c.content_id == "CONTENT-002")

    assert isinstance(content_1.what.topic, str)
    assert isinstance(content_2.what.topic, str)
    # no enum/registry backs `topic` -- any string is accepted, including one never seen before
    from schema import ContentWhat

    novel = ContentWhat(topic="Ett helt nytt, aldrig tidigare anvant amne")
    assert novel.topic == "Ett helt nytt, aldrig tidigare anvant amne"
