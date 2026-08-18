"""V1A order TEST 1, 2, 3, 16 -- Raw Idea -> Interpretation."""

from __future__ import annotations

from engine.interpretation import ANALYSIS_LOGIC_VERSION, build_idea, build_interpretation_draft, build_raw_input, render_idea_interpretation
from engine.models import AnalysisLayer, InsufficientContextError
from engine.provider import RuleBasedAnalysisProvider

GOLDEN = "En chef avbröt samma medarbetare tre gånger under mötet."

# Phrases that would assert the manager's intent as settled fact -- must never appear unhedged.
UNHEDGED_INTENT_PHRASES = [
    "forsoker tysta",
    "vill tysta",
    "avsikten ar att tysta",
    "chefen tystar",
]
HEDGE_MARKERS = ["mojlig", "hypotes", "okand", "ej faststallt", "kan", "inte verifierat"]


def test_1_raw_input_is_preserved_after_analysis():
    raw = build_raw_input("RI-T1", GOLDEN)
    provider = RuleBasedAnalysisProvider()
    draft = build_interpretation_draft(GOLDEN, provider)
    render_idea_interpretation(draft)  # run full analysis
    assert raw.text == GOLDEN  # unchanged after analysis ran


def test_1_raw_input_object_is_frozen():
    import pytest
    from pydantic import ValidationError

    raw = build_raw_input("RI-T1B", GOLDEN)
    with pytest.raises(ValidationError):
        raw.text = "changed"


def test_2_interpretation_is_a_separate_object_from_raw_idea():
    raw = build_raw_input("RI-T2", GOLDEN)
    provider = RuleBasedAnalysisProvider()
    draft = build_interpretation_draft(GOLDEN, provider)
    interpretation = render_idea_interpretation(draft)
    idea = build_idea("IDEA-T2", raw, interpretation)

    assert idea.raw_input_id == raw.raw_input_id
    assert not hasattr(idea, "raw_input_text")  # Idea can never hold a competing copy of the text
    assert idea.interpretation is interpretation
    assert idea.interpretation is not raw  # cannot literally be confused with the raw object


def test_2_ai_interpretation_cannot_overwrite_raw_input_field():
    """There is no method/field path from IdeaInterpretation back onto RawInput.text."""
    from schema import IdeaInterpretation

    assert "text" not in IdeaInterpretation.model_fields


def test_3_no_ungrounded_intent_claims_in_interpretation():
    provider = RuleBasedAnalysisProvider()
    draft = build_interpretation_draft(GOLDEN, provider)
    interpretation = render_idea_interpretation(draft)

    all_text = " ".join(
        filter(
            None,
            [
                interpretation.observed_situation,
                interpretation.hidden_conflict,
                interpretation.power_dimension,
                interpretation.relationship_dimension,
                interpretation.system_dimension,
                interpretation.possible_consequence,
                *interpretation.possible_root_causes,
            ],
        )
    ).lower()

    for phrase in UNHEDGED_INTENT_PHRASES:
        assert phrase not in all_text, f"unhedged intent claim found: {phrase!r}"


def test_3_interpretation_and_inference_layers_are_hedged():
    provider = RuleBasedAnalysisProvider()
    layers = provider.interpret(GOLDEN, ANALYSIS_LOGIC_VERSION)

    for statement in layers:
        if statement.layer in (AnalysisLayer.INTERPRETATION, AnalysisLayer.INFERENCE):
            lowered = statement.text.lower()
            assert any(marker in lowered for marker in HEDGE_MARKERS), (
                f"{statement.layer.value} statement lacks a hedge marker: {statement.text!r}"
            )


def test_3_observation_interpretation_inference_are_distinguishable_layers():
    provider = RuleBasedAnalysisProvider()
    layers = provider.interpret(GOLDEN, ANALYSIS_LOGIC_VERSION)
    present_layers = {s.layer for s in layers}
    assert AnalysisLayer.OBSERVATION in present_layers
    assert AnalysisLayer.INTERPRETATION in present_layers
    assert AnalysisLayer.INFERENCE in present_layers


def test_16_ai_interpretation_carries_analysis_logic_version():
    provider = RuleBasedAnalysisProvider()
    draft = build_interpretation_draft(GOLDEN, provider)
    interpretation = render_idea_interpretation(draft)

    assert interpretation.provenance.analysis_logic_version == ANALYSIS_LOGIC_VERSION
    assert ANALYSIS_LOGIC_VERSION.startswith("interpretation-v1a-")


def test_16_ai_interpretation_without_analysis_logic_version_is_rejected():
    """Inherited from Canonical Foundation V1 (Provenance's own validator) -- not
    reimplemented here, just relied on."""
    import pytest
    from pydantic import ValidationError

    from schema import Provenance
    from schema.enums import Actor, EvidenceCertainty
    from datetime import datetime, timezone

    with pytest.raises(ValidationError):
        Provenance(
            created_by=Actor.AI_SYSTEM,
            actor_id="v1a_rule_based_provider",
            created_at=datetime.now(timezone.utc),
            certainty=EvidenceCertainty.ANALYTICAL_PROPOSAL,
            analysis_logic_version=None,
        )


def test_insufficient_input_raises_before_any_interpretation_is_built():
    provider = RuleBasedAnalysisProvider()
    import pytest

    with pytest.raises(InsufficientContextError):
        build_interpretation_draft("Daligt mote idag.", provider)
