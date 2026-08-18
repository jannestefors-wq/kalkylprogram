"""Order sections 29-31: Golden Path, Failure Path, Repetition Path.

Deterministic end-to-end tests using the RuleBasedAnalysisProvider (no LLM,
no network, no API key -- order section 22/29).
"""

from __future__ import annotations

from engine.human_decision import HumanAction, build_human_decision
from engine.models import ComparisonOutcome, PipelineOutcome, RecommendationOutcome, RepetitionRiskLevel
from engine.pipeline import run_v1a_pipeline

GOLDEN = "En chef avbröt samma medarbetare tre gånger under mötet."
THIN = "Dåligt möte idag."


def test_golden_path_full_chain(dataset):
    """Raw Idea -> Interpretation -> Classification -> Comparison -> Candidate Angles ->
    Recommendation -> Human Decision, deterministically, with no LLM."""
    result = run_v1a_pipeline(GOLDEN, raw_input_id="RI-GOLDEN", idea_id="IDEA-GOLDEN")

    # Raw Idea
    assert result.outcome == PipelineOutcome.COMPLETED
    assert result.raw_input.text == GOLDEN

    # Interpretation
    assert result.idea is not None
    assert result.idea.interpretation is not None
    assert result.idea.interpretation.provenance.analysis_logic_version.startswith("interpretation-v1a-")

    # Classification
    assert result.classification is not None
    assert result.classification.thesis_family_matches or result.classification.territory_matches

    # Comparison (empty corpus by default -> honest "no match in available memory")
    assert result.comparison is not None
    assert result.comparison.outcome == ComparisonOutcome.NO_MATCH_IN_AVAILABLE_MEMORY

    # Candidate Angles
    assert 1 <= len(result.candidate_angles) <= 3

    # Recommendation
    assert result.recommendation.outcome == RecommendationOutcome.RECOMMENDED
    assert result.recommendation.recommended_angle_id is not None

    # Human Decision
    hd = build_human_decision(
        "HD-GOLDEN", HumanAction.ACCEPT_RECOMMENDED, "Janne Stefors", result.idea.idea_id,
        chosen_angle_id=result.recommendation.recommended_angle_id,
    )
    assert hd.decided_by == "Janne Stefors"
    assert hd.target_id == result.recommendation.recommended_angle_id


def test_golden_path_is_deterministic_across_runs():
    r1 = run_v1a_pipeline(GOLDEN, raw_input_id="RI-A", idea_id="IDEA-A")
    r2 = run_v1a_pipeline(GOLDEN, raw_input_id="RI-A", idea_id="IDEA-A")

    assert r1.classification.thesis_family_matches == r2.classification.thesis_family_matches
    assert r1.classification.territory_matches == r2.classification.territory_matches
    assert [c.core for c in r1.candidate_angles] == [c.core for c in r2.candidate_angles]
    assert r1.recommendation.outcome == r2.recommendation.outcome


def test_failure_path_too_thin_input_stops_before_classification():
    result = run_v1a_pipeline(THIN)

    assert result.outcome == PipelineOutcome.MORE_CONTEXT_REQUIRED
    assert result.stopped_reason
    assert result.idea is None
    assert result.interpretation_draft is None
    assert result.classification is None
    assert result.comparison is None
    assert result.candidate_angles == []
    assert result.recommendation is None

    # The correct human action here is to request more context, not to force a decision on
    # a non-existent idea/angle.
    hd = build_human_decision("HD-THIN", HumanAction.REQUEST_MORE_CONTEXT, "Janne Stefors", "IDEA-THIN-PLACEHOLDER")
    assert hd.decision.value == "hold"


def test_repetition_path_near_identical_idea_yields_no_strong_angle(dataset):
    result = run_v1a_pipeline(GOLDEN, existing_content=dataset["content_records"])

    assert result.outcome == PipelineOutcome.COMPLETED  # it does complete the chain...
    assert result.comparison.outcome == ComparisonOutcome.MATCHES_FOUND
    assert any(c.repetition_risk == RepetitionRiskLevel.HIGH for c in result.candidate_angles)
    # ...but does not force a recommendation just to produce output
    assert result.recommendation.outcome == RecommendationOutcome.NO_STRONG_ANGLE
    assert result.recommendation.recommended_angle_id is None


def test_repetition_path_does_not_silently_reduce_candidate_count():
    """Repetition risk affects the RECOMMENDATION, not whether angles get proposed at all --
    the human should still see what was considered and why none was strong enough."""
    from fixtures.fixture_dataset import build_fixture_dataset

    ds = build_fixture_dataset()
    result = run_v1a_pipeline(GOLDEN, existing_content=ds["content_records"])
    assert len(result.candidate_angles) >= 1
    assert all(c.repetition_rationale for c in result.candidate_angles)
