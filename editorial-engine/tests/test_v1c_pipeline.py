"""V1C TEST 7, 8, 27-30 (order section 37)."""

from __future__ import annotations

from engine.models import PipelineOutcome, RecommendationOutcome
from engine.pipeline import run_v1a_pipeline
from memory.ingestion import load_editorial_memory
from memory.models import TextCompleteness
from memory.pipeline import run_v1b_pipeline
from variation.pipeline import run_v1c_variation_analysis

_FULL_RECORDS = [r for r in load_editorial_memory() if r.source_facts.text_completeness == TextCompleteness.FULL]

GOLDEN_LIKE_TEXT = "En chef avbrot samma medarbetare tre ganger under motet, men bad efteratt om arlig feedback."


def test_7_same_angle_can_carry_different_expression_profiles():
    rb = run_v1b_pipeline(GOLDEN_LIKE_TEXT)
    angle = rb.candidate_angles[0]

    result_a = run_v1c_variation_analysis(angle, [])
    # Same angle_id, but a second, independently-built profile is a DIFFERENT
    # analysis-output object -- the angle itself never changes.
    result_b = run_v1c_variation_analysis(angle, [])
    assert result_a.angle_id == result_b.angle_id == angle.angle.angle_id
    assert result_a.angle_profile.profile_id != result_b.angle_profile.profile_id  # distinct analysis runs


def test_8_voice_core_and_variation_are_separate_layers():
    import ast
    from pathlib import Path

    variation_dir = Path(__file__).parent.parent / "variation"
    for py_file in variation_dir.glob("*.py"):
        tree = ast.parse(py_file.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                assert "voice" not in node.module.lower()


def test_27_canonical_foundation_unchanged_by_running_v1c():
    from canonical_data.series_registry import load_series_registry
    from canonical_data.territory_registry import load_territory_registry
    from canonical_data.thesis_family_registry import load_thesis_family_registry

    before = ([s.model_dump() for s in load_series_registry()], [t.model_dump() for t in load_thesis_family_registry()], [t.model_dump() for t in load_territory_registry()])

    rb = run_v1b_pipeline(GOLDEN_LIKE_TEXT)
    run_v1c_variation_analysis(rb.candidate_angles[0], _FULL_RECORDS)

    after = ([s.model_dump() for s in load_series_registry()], [t.model_dump() for t in load_thesis_family_registry()], [t.model_dump() for t in load_territory_registry()])
    assert before == after


def test_28_v1a_pipeline_still_works_unmodified():
    r = run_v1a_pipeline(GOLDEN_LIKE_TEXT)
    assert r.outcome == PipelineOutcome.COMPLETED
    assert r.recommendation.outcome == RecommendationOutcome.RECOMMENDED


def test_29_v1b_editorial_memory_still_works_unmodified():
    rb = run_v1b_pipeline(GOLDEN_LIKE_TEXT)
    assert rb.outcome == PipelineOutcome.COMPLETED
    assert rb.memory_comparison is not None
    assert rb.memory_retrieval is not None


def test_30_no_v1c_output_contains_finished_publication_text():
    rb = run_v1b_pipeline(GOLDEN_LIKE_TEXT)
    rc = run_v1c_variation_analysis(rb.candidate_angles[0], _FULL_RECORDS)
    assert not hasattr(rc, "final_text")
    assert not hasattr(rc, "generated_post")
    for option in rc.recommendation.options:
        assert not hasattr(option, "final_text")
        # proposed_changes only ever maps dimension names to short enum-style values,
        # never free-form prose long enough to be a caption/hook/opening.
        for value in option.proposed_changes.values():
            assert len(value) < 60
