from __future__ import annotations

from canonical_data.tool_inventory import validate_all
from schema.enums import CanonicalStatus, HumanReviewStatus, ToolConfidence


def test_inventory_loads_and_validates():
    tools = validate_all()
    assert len(tools) == 30


def test_stable_tool_ids_are_unique_and_non_empty():
    tools = validate_all()
    ids = [t.stable_tool_id for t in tools]
    assert all(ids)
    assert len(ids) == len(set(ids))


def test_every_entry_has_source_provenance():
    for tool in validate_all():
        assert tool.source_provenance.strip()
        assert tool.source_provenance != "UNKNOWN"


def test_no_inventory_entry_is_canonical_approved():
    for tool in validate_all():
        assert tool.canonical_status in {
            CanonicalStatus.CANONICAL_CANDIDATE,
            CanonicalStatus.HISTORICAL_LUF_MATERIAL,
            CanonicalStatus.SOURCE_ORIGINAL,
        }
        assert tool.human_review_status == HumanReviewStatus.PENDING
        assert tool.confidence != ToolConfidence.VERIFIED
