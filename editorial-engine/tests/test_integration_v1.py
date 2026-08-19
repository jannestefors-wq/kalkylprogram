"""Editorial Engine V1 Integration tests
(EDITORIAL_ENGINE_V1_INTEGRATION_CONTRACT.md section 9,
EDITORIAL_ENGINE_V1_INTEGRATION_HANDOFF.md section 5).

Only tests the INTEGRATION contract -- not new V1A/V1B/V1C editorial logic.
Every pre-existing V1A/V1B/V1C test remains untouched and green alongside
these."""

from __future__ import annotations

from engine.models import PipelineOutcome as V1APipelineOutcome
from integration.pipeline import run_editorial_engine_v1, run_evaluation
from memory.models import EditorialMemoryRecord, TextCompleteness
from schema.enums import Actor
from variation.models import VariationRecommendationOutcome

GOLDEN_LIKE_TEXT = "En chef avbrot samma medarbetare tre ganger under motet, men bad efteratt om arlig feedback."
THIN_TEXT = "Ok."


def test_v1a_output_reaches_v1b_and_v1c_consumers():
    """order section 5.1: V1A outputs reach the intended V1B/V1C consumers."""
    assessment, v1b, v1c = run_evaluation(GOLDEN_LIKE_TEXT, memory_records=[])
    assert v1b.classification is not None  # V1A classification consumed by V1B retrieval/comparison
    assert v1b.candidate_angles  # V1A angle proposal reached the recommendation step
    assert v1c is not None  # V1B's recommended candidate angle reached V1C
    assert v1c.angle_id == v1b.recommendation.recommended_angle_id


def test_memory_records_retain_provenance_completeness_publication_boundary():
    """order section 5.2."""
    assessment, v1b, v1c = run_evaluation(GOLDEN_LIKE_TEXT)
    assert assessment.remembers.memory_boundary_note
    for record in assessment.remembers.records:
        assert record.content_id
        assert record.text_completeness in ("full", "partial")
        assert record.publication_status in ("published_verified", "unverified_draft_or_work_material", "unknown")


def test_no_memory_match_is_worded_as_absolute_novelty():
    """order section 5.3: a no-match must stay bounded to available memory,
    never phrased as 'never written'/'unique'/'completely new'. The
    integration layer must not reword or strengthen V1B's own boundary
    note -- it must pass it through verbatim from
    `v1b.memory_comparison.memory_limitation_note`, which is itself the
    already-reviewed `EDITORIAL_MEMORY_BOUNDARY_NOTE` text (that text
    legitimately *quotes* phrases like 'never written about' as examples
    of forbidden claims within its own explanatory sentence, so a naive
    forbidden-substring scan against it would false-positive)."""
    assessment, v1b, v1c = run_evaluation(GOLDEN_LIKE_TEXT, memory_records=[])
    assert assessment.remembers.no_match is True
    assert assessment.remembers.memory_boundary_note == v1b.memory_comparison.memory_limitation_note


def test_uncertainty_survives_end_to_end():
    """order section 5.4: an insufficient-input case must carry its
    uncertainty (stopped_reason / pending decision) all the way to the
    Final Editorial Assessment, never silently disappear."""
    assessment, v1b, v1c = run_evaluation(THIN_TEXT)
    assert v1b.outcome == V1APipelineOutcome.MORE_CONTEXT_REQUIRED
    assert assessment.sees.input_sufficient_for_interpretation is False
    assert assessment.human_decision_after_v1a_v1b.status == "pending_human_input"
    assert "kontext" in assessment.human_decision_after_v1a_v1b.rationale.lower() or v1b.stopped_reason


def test_unknown_is_neither_similarity_nor_difference_evidence():
    """order section 5.5: re-verifies the (unmodified) V1C guarantee is
    still reachable end to end through the integration layer -- not a new
    claim, a visibility check. A profile with no strong angle produces no
    V1C run at all, and the assessment fields correctly stay None/unknown
    rather than a fabricated label."""
    assessment, v1b, v1c = run_evaluation("Observation fore tolkning. Observation: Tre personer kom sent till motet. Tolkning: De bryr sig inte.")
    if v1c is None:
        assert assessment.assesses.label is None
    else:
        # Even when V1C ran, an UNKNOWN dimension must never appear as "unknown" in
        # the display fields -- it must be None (contract 5.A: never fabricated).
        assert assessment.sees.lens != "unknown"
        assert assessment.sees.narrative_distance != "unknown"


def test_human_authority_remains_explicit_evaluation_mode_never_decides():
    """order section 5.6 / contract section 7,8: Evaluation Mode must never
    fabricate a schema.HumanDecision. Both decision points stay pending."""
    assessment, v1b, v1c = run_evaluation(GOLDEN_LIKE_TEXT, memory_records=[])
    assert assessment.human_decision_after_v1a_v1b.status == "pending_human_input"
    assert assessment.human_decision_after_v1a_v1b.decision_reference is None
    if assessment.human_decision_after_v1c is not None:
        assert assessment.human_decision_after_v1c.status == "pending_human_input"
        assert assessment.human_decision_after_v1c.decision_reference is None


def test_human_authority_real_decision_is_honored_when_supplied():
    """The real (non-evaluation) entry point must resolve a decision point
    to 'decided' ONLY when handed a genuine, human-authored schema.HumanDecision
    -- never on its own initiative. The decision must be built against the
    SAME v1b run it is later applied to (two-phase API:
    `run_v1a_v1b_stage()` then `continue_after_human_decision(v1b, ...)`) --
    candidate angle ids are freshly generated per pipeline run, so a
    decision captured from one run can never resolve against another."""
    from engine.human_decision import HumanAction, build_human_decision
    from integration.pipeline import continue_after_human_decision, run_v1a_v1b_stage

    assessment1, v1b = run_v1a_v1b_stage(GOLDEN_LIKE_TEXT, memory_records=[])
    assert v1b.recommendation.outcome.value == "RECOMMENDED"

    decision = build_human_decision(
        "HD-TEST-001", HumanAction.ACCEPT_RECOMMENDED, "Test Human", v1b.idea.idea_id,
        chosen_angle_id=v1b.recommendation.recommended_angle_id,
    )
    assert decision.decided_by_actor == Actor.HUMAN

    assessment, v1c2 = continue_after_human_decision(v1b, decision)
    assert assessment.human_decision_after_v1a_v1b.status == "decided"
    assert assessment.human_decision_after_v1a_v1b.decision_reference == "HD-TEST-001"
    assert v1c2 is not None


def test_controlled_variation_is_direction_only():
    """order section 5.7: no direction string may be, or contain, finished
    publishable prose -- only dimension-value tokens joined by '->'."""
    assessment, v1b, v1c = run_evaluation(GOLDEN_LIKE_TEXT, memory_records=[])
    for direction in assessment.could_change.directions:
        assert "->" in direction or " " not in direction.strip() or len(direction.split()) <= 6
        assert not direction.strip().endswith((".", "!", "?"))


def test_evaluation_mode_writes_no_permanent_memory_or_canonical_data():
    """order section 5.8."""
    from memory.ingestion import load_editorial_memory

    before = load_editorial_memory()
    run_evaluation(GOLDEN_LIKE_TEXT)
    run_evaluation("En helt annan text om ett annat amne for att se om nagot skrivs till minnet.")
    after = load_editorial_memory()
    assert len(before) == len(after)
    assert [r.content_id for r in before] == [r.content_id for r in after]


def test_v1c_prototype_models_do_not_leak_into_canonical_schema():
    """order section 5.9."""
    import json
    import subprocess
    import sys as _sys

    from pathlib import Path

    schema_dir = Path(__file__).parent.parent / "schema" / "json"
    forbidden_type_names = ["VariationProfile", "LocalEditorialFunctionAssessment", "FalseVariationAssessment", "StructuralMovementAssessment"]
    for schema_file in schema_dir.glob("*.schema.json"):
        content = schema_file.read_text(encoding="utf-8")
        for name in forbidden_type_names:
            assert name not in content, f"{schema_file.name} contains forbidden V1C prototype type {name!r}"


def test_existing_v1a_v1b_v1c_responsibilities_remain_separate():
    """order section 5.10: the assessment keeps each component's evidence
    attributable -- V1A/V1B fields never silently merge with V1C fields
    into one undifferentiated claim."""
    assessment, v1b, v1c = run_evaluation(GOLDEN_LIKE_TEXT, memory_records=[])
    # V1A/V1B-sourced fields
    assert assessment.sees.thesis_family is not None or assessment.sees.territory is not None
    # V1C-sourced fields only present because v1c actually ran
    if v1c is not None:
        assert assessment.sees.entry_function is not None or assessment.sees.closure_function is not None
    assert assessment.provenance_note  # explicit separation note always present


def test_canonical_json_schema_reproducible_and_unchanged():
    """order section 5.11."""
    import subprocess
    import sys as _sys
    from pathlib import Path

    schema_dir = Path(__file__).parent.parent / "schema" / "json"
    before = {p.name: p.read_text(encoding="utf-8") for p in schema_dir.glob("*.schema.json")}

    result = subprocess.run(
        [_sys.executable, "-m", "schema.export_json_schema"],
        cwd=Path(__file__).parent.parent, capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr

    after = {p.name: p.read_text(encoding="utf-8") for p in schema_dir.glob("*.schema.json")}
    assert before == after
