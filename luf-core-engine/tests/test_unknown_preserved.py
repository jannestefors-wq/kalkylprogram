from __future__ import annotations

from canonical_data.tool_inventory import validate_all
from schema.sentinels import UNKNOWN


def test_framework_acronyms_keep_purpose_unknown():
    """Direktorder S7: a bare acronym name must never get an invented purpose/components."""
    tools = {t.stable_tool_id: t for t in validate_all() if t.tool_type.value == "framework_acronym"}
    assert len(tools) == 7
    for tool in tools.values():
        assert tool.purpose == UNKNOWN
        assert tool.components == []
        assert tool.suitable_context == UNKNOWN
        assert tool.diagnostic_use == UNKNOWN


def test_triangle_alternative_direction_stays_unknown_absent_evidence():
    tools = validate_all()
    for tool in tools:
        if tool.tool_type.value == "triangle":
            assert tool.alternative_direction == UNKNOWN
