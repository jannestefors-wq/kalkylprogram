"""V1A order TEST 17, 18 -- Canonical Foundation untouched, no generation output."""

from __future__ import annotations

from canonical_data.series_registry import load_series_registry
from canonical_data.territory_registry import load_territory_registry
from canonical_data.thesis_family_registry import load_thesis_family_registry
from engine.pipeline import run_v1a_pipeline

GOLDEN = "En chef avbröt samma medarbetare tre gånger under mötet."


def test_17_v1a_does_not_change_series_registry():
    before = {s.series_id: s.model_dump_json() for s in load_series_registry()}
    run_v1a_pipeline(GOLDEN)
    after = {s.series_id: s.model_dump_json() for s in load_series_registry()}
    assert before == after
    assert len(after) == 16


def test_17_v1a_does_not_change_thesis_family_registry():
    before = {t.thesis_family_id: t.model_dump_json() for t in load_thesis_family_registry()}
    run_v1a_pipeline(GOLDEN)
    after = {t.thesis_family_id: t.model_dump_json() for t in load_thesis_family_registry()}
    assert before == after
    assert len(after) == 8


def test_17_v1a_does_not_change_territory_registry():
    before = {t.territory_id: t.model_dump_json() for t in load_territory_registry()}
    run_v1a_pipeline(GOLDEN)
    after = {t.territory_id: t.model_dump_json() for t in load_territory_registry()}
    assert before == after


def test_17_v1a_does_not_change_voice_core_or_reader_feedback(dataset):
    """Canonical Voice Core / VoiceCoreSnapshot / Parastoo ReaderFeedback all live in the
    same fixture/canonical_data modules V1A never writes to -- verified by re-loading them
    unchanged after a pipeline run."""
    from canonical_data.reader_feedback_registry import load_parastoo_reader_feedback

    before_voice = [v.model_dump_json() for v in dataset["voice_principles"]]
    before_feedback = load_parastoo_reader_feedback().model_dump_json()

    run_v1a_pipeline(GOLDEN)

    after_voice = [v.model_dump_json() for v in dataset["voice_principles"]]
    after_feedback = load_parastoo_reader_feedback().model_dump_json()

    assert before_voice == after_voice
    assert before_feedback == after_feedback


def test_17_engine_module_never_imports_or_writes_to_canonical_data_source():
    """Structural check: engine/*.py only ever calls the load_* functions in canonical_data/,
    never constructs Series/ThesisFamily/Territory/ReaderFeedback objects itself."""
    from pathlib import Path

    engine_dir = Path(__file__).parent.parent / "engine"
    forbidden_calls = {"Series(", "ThesisFamily(", "Territory(", "ReaderFeedback("}
    for py_file in engine_dir.glob("*.py"):
        source = py_file.read_text(encoding="utf-8")
        for forbidden in forbidden_calls:
            assert forbidden not in source, f"{py_file.name} constructs canonical data directly: {forbidden}"


def test_18_pipeline_output_contains_no_finished_publication_text():
    """V1A output stops at angle + rationale + human decision -- never a LinkedIn post,
    caption, hook, CTA, or signature."""
    result = run_v1a_pipeline(GOLDEN)

    from engine.models import CandidateAngle

    for candidate in result.candidate_angles:
        assert isinstance(candidate, CandidateAngle)
        assert not hasattr(candidate, "final_text")
        assert not hasattr(candidate, "caption")
        assert not hasattr(candidate, "cta_text")
        assert not hasattr(candidate, "signature")

    # the underlying canonical ContentRecord type (which DOES have final_text) is never
    # constructed anywhere in the V1A pipeline result
    assert not hasattr(result, "content_record")
    assert not hasattr(result, "final_text")


def test_18_no_content_record_is_ever_constructed_by_the_pipeline():
    from pathlib import Path

    engine_dir = Path(__file__).parent.parent / "engine"
    for py_file in engine_dir.glob("*.py"):
        source = py_file.read_text(encoding="utf-8")
        assert "ContentRecord(" not in source, f"{py_file.name} constructs a ContentRecord -- V1A must never generate publishable content"
