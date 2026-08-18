"""V1.1, OQ-2: 'analysis_logic_version' is mandatory when created_by == AI_SYSTEM.

TEST A: AI-created analysis without analysis_logic_version must fail.
TEST B: Human-created analysis may follow the decided null-rule (field stays None).
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from schema import Provenance
from schema.enums import Actor, EvidenceCertainty

T0 = datetime(2026, 1, 1, tzinfo=timezone.utc)


def test_a_ai_created_analysis_without_analysis_logic_version_fails():
    with pytest.raises(ValidationError):
        Provenance(
            created_by=Actor.AI_SYSTEM,
            actor_id="fas0a_pipeline_v1",
            created_at=T0,
            certainty=EvidenceCertainty.ANALYTICAL_PROPOSAL,
            analysis_logic_version=None,
        )


def test_a_ai_created_analysis_with_empty_string_also_fails():
    with pytest.raises(ValidationError):
        Provenance(
            created_by=Actor.AI_SYSTEM,
            actor_id="fas0a_pipeline_v1",
            created_at=T0,
            certainty=EvidenceCertainty.ANALYTICAL_PROPOSAL,
            analysis_logic_version="",
        )


def test_a_ai_created_analysis_with_analysis_logic_version_succeeds():
    prov = Provenance(
        created_by=Actor.AI_SYSTEM,
        actor_id="fas0a_pipeline_v1",
        created_at=T0,
        certainty=EvidenceCertainty.ANALYTICAL_PROPOSAL,
        analysis_logic_version="fas0a-analysis-logic-1.0",
    )
    assert prov.analysis_logic_version == "fas0a-analysis-logic-1.0"


def test_b_human_created_analysis_may_have_null_analysis_logic_version():
    prov = Provenance(
        created_by=Actor.HUMAN,
        actor_id="Janne Stefors",
        created_at=T0,
        certainty=EvidenceCertainty.VERIFIED,
        analysis_logic_version=None,
    )
    assert prov.analysis_logic_version is None


def test_fixture_ai_provenances_all_carry_analysis_logic_version(dataset):
    """Every AI-attributed Provenance actually present in the fixture obeys the rule --
    not just isolated unit constructions above."""

    def _walk_provenances(obj):
        found = []
        if hasattr(obj, "provenance") and isinstance(getattr(obj, "provenance"), Provenance):
            found.append(obj.provenance)
        interpretation = getattr(obj, "interpretation", None)
        if interpretation is not None:
            found.append(interpretation.provenance)
        return found

    checked = 0
    for items in dataset.values():
        for obj in items:
            for prov in _walk_provenances(obj):
                if prov.created_by == Actor.AI_SYSTEM:
                    assert prov.analysis_logic_version, f"AI provenance on {type(obj).__name__} missing analysis_logic_version"
                    checked += 1
    assert checked > 0, "fixture should contain at least one AI-attributed provenance to exercise this rule"
