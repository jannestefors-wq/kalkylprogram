from __future__ import annotations

from datetime import datetime, timezone

from schema.tool_trace import ToolTrace


def test_tool_trace_roundtrips_through_json(ai_provenance):
    trace = ToolTrace(
        session_id="sess-1",
        original_input="Tre personer kom sent till mötet.",
        observations=["c1"],
        interpretations=["c2"],
        assumptions=[],
        tools_considered=["luf-tool-0001", "luf-tool-0021"],
        tools_selected=["luf-tool-0021"],
        selection_reason="Trygghet/Tydlighet/Tyngd matchade den beskrivna situationen bäst.",
        tool_source_versions={"luf-tool-0021": "UNVERIFIED"},
        process_steps=["observe", "interpret", "open_question"],
        dimensions_detected=["punktlighet"],
        dimensions_missing=["kontext_om_orsak"],
        questions_opened=["Vad hände innan mötet?"],
        decisions=[],
        actions=[],
        timestamps={"started": datetime(2026, 8, 20, tzinfo=timezone.utc)},
        provenance=ai_provenance,
    )

    dumped = trace.model_dump_json()
    reloaded = ToolTrace.model_validate_json(dumped)

    assert reloaded == trace
    # Direktorder S17: must be able to answer "which tool, why, what did it open".
    assert reloaded.tools_selected == ["luf-tool-0021"]
    assert reloaded.selection_reason
    assert reloaded.questions_opened
