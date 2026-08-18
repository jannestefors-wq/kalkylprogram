"""V1A order TEST 9, 10 -- Candidate Angles + Repetition Risk."""

from __future__ import annotations

from canonical_data.series_registry import load_series_registry
from canonical_data.territory_registry import load_territory_registry
from canonical_data.thesis_family_registry import load_thesis_family_registry
from engine.angles import MAX_CANDIDATE_ANGLES, propose_candidate_angles
from engine.classification import classify
from engine.comparison import compare_to_existing_content
from engine.interpretation import ANALYSIS_LOGIC_VERSION, build_interpretation_draft, render_idea_interpretation
from engine.models import RepetitionRiskLevel
from engine.provider import RuleBasedAnalysisProvider

GOLDEN = "En chef avbröt samma medarbetare tre gånger under mötet."
_FIELDS = ["observed_situation", "visible_problem", "hidden_conflict", "power_dimension", "relationship_dimension", "system_dimension", "possible_consequence"]


def _run_to_angles(raw: str, existing_content: list):
    provider = RuleBasedAnalysisProvider()
    draft = build_interpretation_draft(raw, provider)
    interpretation = render_idea_interpretation(draft)
    interp_texts = {k: getattr(interpretation, k) for k in _FIELDS}
    text = " ".join(v for v in interp_texts.values() if v)
    classification = classify(text, load_series_registry(), load_thesis_family_registry(), load_territory_registry())
    comparison = compare_to_existing_content(text, classification, existing_content)
    return propose_candidate_angles("IDEA-T9", interp_texts, classification, comparison, provider, ANALYSIS_LOGIC_VERSION)


def test_9_never_more_than_three_candidate_angles():
    angles = _run_to_angles(GOLDEN, [])
    assert len(angles) <= MAX_CANDIDATE_ANGLES
    assert len(angles) == MAX_CANDIDATE_ANGLES  # golden path has enough material for all 3


def test_9_candidate_angles_are_not_hardcoded_text():
    """Two different raw inputs must produce different angle text -- proving the seeds are
    parameterized from the actual interpretation, not fixed strings."""
    other_input = "En kollega fick aldrig kredit for sin ide trots att den lyftes fram tre ganger senare av chefen."
    angles_golden = _run_to_angles(GOLDEN, [])
    angles_other = _run_to_angles(other_input, [])

    golden_cores = {a.core for a in angles_golden}
    other_cores = {a.core for a in angles_other}
    assert golden_cores.isdisjoint(other_cores)


def test_9_each_candidate_angle_carries_required_fields():
    angles = _run_to_angles(GOLDEN, [])
    for a in angles:
        assert a.angle.angle_id
        assert a.core
        assert a.why_relevant
        assert a.differentiation
        assert a.repetition_risk in (RepetitionRiskLevel.LOW, RepetitionRiskLevel.MEDIUM, RepetitionRiskLevel.HIGH)
        assert a.repetition_rationale
        assert a.evidence_basis  # golden path is grounded in real interpretation text


def test_9_candidate_angles_reuse_canonical_angle_model_not_a_duplicate():
    from schema import Angle

    angles = _run_to_angles(GOLDEN, [])
    for a in angles:
        assert isinstance(a.angle, Angle)


def test_10_repetition_risk_is_low_with_no_nearby_material():
    angles = _run_to_angles(GOLDEN, [])
    assert all(a.repetition_risk == RepetitionRiskLevel.LOW for a in angles)
    for a in angles:
        assert a.repetition_rationale  # motiverad, per order section 16


def test_10_repetition_risk_is_high_with_near_identical_existing_material(dataset):
    angles = _run_to_angles(GOLDEN, dataset["content_records"])
    assert any(a.repetition_risk == RepetitionRiskLevel.HIGH for a in angles)
    high_risk = [a for a in angles if a.repetition_risk == RepetitionRiskLevel.HIGH]
    for a in high_risk:
        assert "HIGH" in a.repetition_rationale
        assert a.canonical_relations  # rationale references what was actually shared
