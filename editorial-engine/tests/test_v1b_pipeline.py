"""V1B TEST 12-14, 17-24 (order section 30)."""

from __future__ import annotations

from engine.models import PipelineOutcome, RecommendationOutcome, RepetitionRiskLevel
from engine.pipeline import run_v1a_pipeline
from memory.ingestion import load_editorial_memory
from memory.pipeline import run_v1b_pipeline

GOLDEN_LIKE_TEXT = "En chef avbrot samma medarbetare tre ganger under motet, men bad efteratt om arlig feedback."
THIN_TEXT = "Daligt mote idag."

# V1B Correction Order (Defect 2): GOLDEN_LIKE_TEXT alone shares no real,
# threshold-clearing content evidence with any single fulltext record (only
# canonical classification matches, which the correction no longer treats as
# sufficient on their own -- see memory/comparison.py). RELEVANT_TEXT is
# deliberately crafted to share real vocabulary with content-work-006's
# original_text AND topic_labels ("observation", "tolkning"), so it
# demonstrates genuine, explainable evidence-driven HIGH repetition, not a
# structural artifact.
RELEVANT_TEXT = (
    "Chefen gjorde en tydlig observation om vad som hande pa kontoret tre ganger, "
    "men var forsta tolkning av situationen visade sig vara helt fel."
)


def test_12_repetition_low_when_no_memory_overlap():
    r = run_v1b_pipeline(GOLDEN_LIKE_TEXT, memory_records=[])
    assert r.memory_comparison.outcome.value == "NO_MATCH_IN_AVAILABLE_MEMORY"
    assert all(c.repetition_risk == RepetitionRiskLevel.LOW for c in r.candidate_angles)
    assert r.candidate_angles  # LOW is motivated, not just "no candidates"


def test_13_repetition_medium_on_weak_topic_only_overlap():
    all_records = load_editorial_memory()
    weak_only_record = next(r for r in all_records if r.content_id == "content-work-002")
    # Shares content-work-002's own topic labels ("resultat", "ansvar", "konsekvens")
    # literally with the RAW INPUT, but the input's canonical classification does not
    # match content-work-002's thesis_family_id (thesis-symptom-cause-001) -- so this
    # is real content-level overlap with no canonical corroboration: genuinely "weak".
    text = "Chefen sag samma resultat tre ganger men forstod aldrig konsekvens och ansvar bakom."
    r = run_v1b_pipeline(text, memory_records=[weak_only_record])

    assert r.memory_comparison.outcome.value == "MATCHES_FOUND"
    match = r.memory_comparison.matches[0]
    assert match.repetition_signal_strength == "weak"
    assert match.topic_overlap  # real, named lexical evidence -- not a lone generic word
    assert any(c.repetition_risk == RepetitionRiskLevel.MEDIUM for c in r.candidate_angles)


def test_14_repetition_high_on_shared_canonical_relation_and_content_evidence():
    all_records = load_editorial_memory()
    strong_record = next(r for r in all_records if r.content_id == "content-work-001")
    # Shares content-work-001's topic label ("verklighet") literally with the raw
    # input AND triggers a genuine shared Thesis Family match -- both signals
    # together, per order section 8's "HIGH ska krava flera relevanta signaler".
    text = "Chefen pratade om verklighet pa kontoret tre ganger men ingen lyssnade pa vad som faktiskt hande."
    r = run_v1b_pipeline(text, memory_records=[strong_record])

    match = r.memory_comparison.matches[0]
    assert match.repetition_signal_strength == "strong"
    assert match.shared_thesis_family_ids  # canonical signal
    assert match.topic_overlap  # AND content signal -- neither alone would be enough
    assert any(c.repetition_risk == RepetitionRiskLevel.HIGH for c in r.candidate_angles)


def test_14b_lone_canonical_relation_without_content_evidence_is_not_high():
    """The exact scenario order section 8 named as the failure mode: a shared
    canonical relation with NO content-level corroboration must not drive HIGH."""
    all_records = load_editorial_memory()
    strong_record = next(r for r in all_records if r.content_id == "content-work-001")
    r = run_v1b_pipeline(GOLDEN_LIKE_TEXT, memory_records=[strong_record])

    assert r.memory_comparison.outcome.value == "MATCHES_FOUND"
    match = r.memory_comparison.matches[0]
    assert match.shared_thesis_family_ids  # canonical signal alone IS present
    assert not match.topic_overlap and not match.text_overlap_terms  # but no content signal
    assert match.repetition_signal_strength == "weak"
    assert all(c.repetition_risk == RepetitionRiskLevel.LOW for c in r.candidate_angles)


def test_17_memory_influences_candidate_angles_for_genuinely_relevant_input():
    r_empty = run_v1b_pipeline(RELEVANT_TEXT, memory_records=[])
    r_loaded = run_v1b_pipeline(RELEVANT_TEXT)  # real, full corpus

    empty_risks = [c.repetition_risk for c in r_empty.candidate_angles]
    loaded_risks = [c.repetition_risk for c in r_loaded.candidate_angles]
    assert empty_risks != loaded_risks
    assert r_empty.recommendation.outcome != r_loaded.recommendation.outcome

    # The difference must be explainable by real evidence, not a structural artifact:
    # at least one LOADED match must be "strong" (canonical + content signal together).
    strong_matches = [m for m in r_loaded.memory_comparison.matches if m.repetition_signal_strength == "strong"]
    assert strong_matches
    for m in strong_matches:
        assert m.shared_thesis_family_ids or m.shared_territory_ids
        assert m.topic_overlap or m.text_overlap_terms


def test_18_high_repetition_can_yield_no_strong_angle():
    r = run_v1b_pipeline(RELEVANT_TEXT)  # full real corpus -- genuine, corroborated overlap
    assert r.recommendation.outcome == RecommendationOutcome.NO_STRONG_ANGLE
    assert r.recommendation.recommended_angle_id is None
    # Candidates are still shown -- high repetition does not hide them from the human.
    assert len(r.candidate_angles) >= 1


def test_19_thin_input_still_returns_more_context_required():
    r = run_v1b_pipeline(THIN_TEXT)
    assert r.outcome == PipelineOutcome.MORE_CONTEXT_REQUIRED
    assert r.stopped_reason
    assert r.memory_retrieval is None
    assert r.memory_comparison is None
    assert r.candidate_angles == []


def test_20_parastoo_reader_feedback_is_not_in_editorial_memory():
    records = load_editorial_memory()
    content_ids = {r.content_id for r in records}
    assert not any("parastoo" in cid.lower() for cid in content_ids)

    for r in records:
        assert "parastoo" not in r.source_facts.original_text.lower()
        assert "parastoo" not in r.source_facts.source.lower()


def test_21_editorial_memory_never_imports_voice_core():
    import ast
    from pathlib import Path

    memory_dir = Path(__file__).parent.parent / "memory"
    for py_file in memory_dir.glob("*.py"):
        tree = ast.parse(py_file.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                assert "voice" not in node.module.lower(), f"{py_file.name} imports from {node.module!r}"


def test_22_no_v1b_output_contains_finished_publication_text():
    r = run_v1b_pipeline(GOLDEN_LIKE_TEXT)
    for candidate in r.candidate_angles:
        assert not hasattr(candidate.angle, "final_text") or candidate.angle.__class__.__name__ != "ContentRecord"
    # V1BPipelineResult itself has no ContentRecord/final_text field at all.
    assert not hasattr(r, "final_text")
    assert not hasattr(r, "generated_post")


def test_23_canonical_foundation_unchanged_by_running_v1b():
    from canonical_data.series_registry import load_series_registry
    from canonical_data.thesis_family_registry import load_thesis_family_registry
    from canonical_data.territory_registry import load_territory_registry

    before_series = [s.model_dump() for s in load_series_registry()]
    before_tf = [t.model_dump() for t in load_thesis_family_registry()]
    before_territory = [t.model_dump() for t in load_territory_registry()]

    run_v1b_pipeline(GOLDEN_LIKE_TEXT)
    run_v1b_pipeline(THIN_TEXT)

    after_series = [s.model_dump() for s in load_series_registry()]
    after_tf = [t.model_dump() for t in load_thesis_family_registry()]
    after_territory = [t.model_dump() for t in load_territory_registry()]

    assert before_series == after_series
    assert before_tf == after_tf
    assert before_territory == after_territory


def test_24_v1a_pipeline_still_works_unmodified():
    r = run_v1a_pipeline(GOLDEN_LIKE_TEXT)
    assert r.outcome == PipelineOutcome.COMPLETED
    assert r.comparison.outcome.value == "NO_MATCH_IN_AVAILABLE_MEMORY"  # V1A's own empty-default behavior, unchanged
    assert r.recommendation.outcome == RecommendationOutcome.RECOMMENDED

    r_thin = run_v1a_pipeline(THIN_TEXT)
    assert r_thin.outcome == PipelineOutcome.MORE_CONTEXT_REQUIRED
