"""Beslut 29: 'content kan lanka till thesis family'."""

from __future__ import annotations


def test_content_record_links_to_a_thesis_family(dataset):
    content_1 = next(c for c in dataset["content_records"] if c.content_id == "CONTENT-001")
    thesis_family_ids = {t.thesis_family_id for t in dataset["thesis_families"]}

    assert content_1.thesis_family_id is not None
    assert content_1.thesis_family_id in thesis_family_ids


def test_content_core_thesis_text_is_independent_of_thesis_family_id(dataset):
    """
    Beslut 18: a content's own `core_thesis` wording must be able to differ
    from the thesis family's canonical `core_statement` while still linking
    to it -- that's the whole point ('den har formuleringen ar ny, men den
    tillhor samma gamla tesfamilj').
    """
    content_1 = next(c for c in dataset["content_records"] if c.content_id == "CONTENT-001")
    family = next(t for t in dataset["thesis_families"] if t.thesis_family_id == content_1.thesis_family_id)

    assert content_1.what.core_thesis != family.core_statement
    assert content_1.thesis_family_id == family.thesis_family_id
