"""Beslut 29: 'raw_input kan inte tappas bort'."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from schema import RawInput
from schema.enums import InputType


def test_raw_input_is_frozen_after_construction():
    ri = RawInput(
        raw_input_id="RI-TEST",
        captured_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        text="En chef avbrot samma medarbetare tre ganger under motet.",
        input_type=InputType.OBSERVATION,
        language="sv",
    )
    with pytest.raises(ValidationError):
        ri.text = "Nagot annat."  # attempting to overwrite the original text must fail


def test_raw_input_hash_detects_any_text_difference():
    text_a = "En chef avbrot samma medarbetare tre ganger under motet."
    text_b = text_a + " "  # trivially different

    ri_a = RawInput(
        raw_input_id="RI-A", captured_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        text=text_a, input_type=InputType.OBSERVATION, language="sv",
    )
    ri_b = RawInput(
        raw_input_id="RI-B", captured_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        text=text_b, input_type=InputType.OBSERVATION, language="sv",
    )
    assert ri_a.content_hash != ri_b.content_hash


def test_idea_references_raw_input_rather_than_embedding_mutable_text(dataset):
    idea_1 = next(i for i in dataset["ideas"] if i.idea_id == "IDEA-001")
    raw_input_1 = next(r for r in dataset["raw_inputs"] if r.raw_input_id == "RI-001")

    assert idea_1.raw_input_id == raw_input_1.raw_input_id
    # Idea has no field that could hold a competing/edited copy of the raw text.
    assert not hasattr(idea_1, "raw_input_text")
    assert not hasattr(idea_1, "raw_input")
