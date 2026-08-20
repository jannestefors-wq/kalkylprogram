from __future__ import annotations

from datetime import datetime, timezone

from schema.triangulation import PerspectiveApplication, TriangulationSession


def test_session_supports_multiple_simultaneous_perspectives(ai_provenance):
    """Direktorder S4: explicitly not choose_triangle() -> generate_answer()."""
    session = TriangulationSession(
        session_id="tri-1",
        situation_description="Tre personer kom sent till mötet.",
        perspectives_applied=[
            PerspectiveApplication(
                tool_id="luf-tool-0021",
                tool_source_version="UNVERIFIED",
                selection_reason="Undersöker trygghet/tydlighet/tyngd i situationen.",
                confirmed=["Tre personer var sena"],
                contradicted=[],
                missing=["Varför de var sena"],
                patterns_emerging=[],
                further_information_needed=["Historik för dessa tre personer"],
            ),
            PerspectiveApplication(
                tool_id="luf-tool-0006",
                tool_source_version="UNVERIFIED",
                selection_reason="Undersöker person/process/produkt i samma situation.",
                confirmed=["Tre personer var sena"],
                contradicted=["Ingen verifierad koppling till bristande engagemang"],
                missing=["Processrelaterad orsak"],
            ),
        ],
        created_at=datetime(2026, 8, 20, tzinfo=timezone.utc),
        provenance=ai_provenance,
    )

    assert len(session.perspectives_applied) >= 2
    tool_ids_used = {p.tool_id for p in session.perspectives_applied}
    assert len(tool_ids_used) == 2, "one situation examined through more than one distinct lens"
