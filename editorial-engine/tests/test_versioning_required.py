"""Beslut 29: 'versionsfalt kravs dar de ska kravas'."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from schema import RawInput, Source, VoicePrinciple
from schema.enums import EvidenceCertainty, InputType, SourceType, VoicePrincipleStatus
from schema.versioning import SCHEMA_VERSION


def test_every_top_level_record_in_fixture_carries_schema_version(dataset):
    flat = [
        obj
        for key, items in dataset.items()
        if key not in {"raw_inputs"}  # checked separately below with an explicit assertion too
        for obj in items
    ]
    for obj in flat:
        assert hasattr(obj, "schema_version"), f"{type(obj).__name__} is missing schema_version"
        assert obj.schema_version == SCHEMA_VERSION


def test_raw_input_carries_schema_version_too(dataset):
    for ri in dataset["raw_inputs"]:
        assert ri.schema_version == SCHEMA_VERSION


def test_voice_principle_version_and_valid_from_are_mandatory():
    base_kwargs = dict(
        voice_principle_id="VP-TEST",
        name="Test principle",
        definition="Test definition.",
        status=VoicePrincipleStatus.ANALYTICAL_PROPOSAL,
    )
    with pytest.raises(ValidationError):
        VoicePrinciple(**base_kwargs, valid_from=datetime(2026, 1, 1, tzinfo=timezone.utc))  # missing `version`
    with pytest.raises(ValidationError):
        VoicePrinciple(**base_kwargs, version="1.0")  # missing `valid_from`


def test_source_does_not_require_a_speculative_reliability_value():
    """Beslut 24: null is better than a made-up default -- Source.reliability
    may legitimately be None rather than forced to some invented enum value."""
    source = Source(
        source_id="SRC-NULLTEST",
        source_type=SourceType.WEBSITE,
        title="Untriaged source",
    )
    assert source.reliability is None
    assert source.usage_rights is None
