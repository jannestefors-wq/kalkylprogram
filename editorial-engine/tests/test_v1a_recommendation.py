"""V1A order TEST 11, 12, 13 -- Recommended Angle, NO_STRONG_ANGLE, MORE_CONTEXT_REQUIRED."""

from __future__ import annotations

from engine.models import RecommendationOutcome
from engine.pipeline import run_v1a_pipeline

GOLDEN = "En chef avbröt samma medarbetare tre gånger under mötet."
THIN = "Dåligt möte idag."


def test_11_recommendation_is_explainable(dataset):
    result = run_v1a_pipeline(GOLDEN)
    rec = result.recommendation

    assert rec.outcome == RecommendationOutcome.RECOMMENDED
    assert rec.recommended_angle_id is not None
    assert rec.rationale
    assert rec.scores  # transparent breakdown, not a black box
    recommended_ids = {c.angle.angle_id for c in result.candidate_angles}
    assert rec.recommended_angle_id in recommended_ids

    best = max(rec.scores, key=lambda s: s.score)
    assert best.angle_id == rec.recommended_angle_id
    assert best.breakdown  # every point is named


def test_12_no_strong_angle_when_everything_is_near_identical_to_existing_material(dataset):
    result = run_v1a_pipeline(GOLDEN, existing_content=dataset["content_records"])
    assert result.recommendation.outcome == RecommendationOutcome.NO_STRONG_ANGLE
    assert result.recommendation.recommended_angle_id is None
    assert result.recommendation.rationale


def test_12_no_strong_angle_when_there_are_no_candidates_at_all():
    from engine.recommendation import recommend

    rec = recommend([])
    assert rec.outcome == RecommendationOutcome.NO_STRONG_ANGLE
    assert rec.recommended_angle_id is None
    assert rec.scores == []


def test_13_more_context_required_for_thin_input():
    from engine.models import PipelineOutcome

    result = run_v1a_pipeline(THIN)
    assert result.outcome == PipelineOutcome.MORE_CONTEXT_REQUIRED
    assert result.stopped_reason
    assert result.idea is None
    assert result.candidate_angles == []
    assert result.recommendation is None


def test_13_more_context_required_never_forces_a_recommendation():
    from engine.models import PipelineOutcome

    result = run_v1a_pipeline(THIN)
    assert result.outcome != PipelineOutcome.COMPLETED
