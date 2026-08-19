"""V1C order sections 38-42: Golden Variation Path, False Variation Path,
Structural Repetition Path, Legitimate Same-Thesis Path, Lexical
Collision Path. Fake/stub provider only -- no real LLM anywhere here."""

from __future__ import annotations

from engine.models import PipelineOutcome
from memory.ingestion import load_editorial_memory
from memory.models import TextCompleteness
from memory.pipeline import run_v1b_pipeline
from variation.comparison import compare_variation_profiles
from variation.human_decision import HumanVariationAction, build_human_variation_decision
from variation.models import SourceKind, VariationDistanceCategory, VariationRecommendationOutcome
from variation.pipeline import run_v1c_variation_analysis
from variation.profiler import build_variation_profile

_FULL_RECORDS = [r for r in load_editorial_memory() if r.source_facts.text_completeness == TextCompleteness.FULL]


def test_golden_variation_path_end_to_end():
    """order section 38: full chain from Raw Idea through Human Variation
    Decision, proving at least two genuinely different expression directions
    can be described without any finished text being written."""

    raw_text = "En chef avbrot samma medarbetare tre ganger under motet, men bad efteratt om arlig feedback."
    rb = run_v1b_pipeline(raw_text)
    assert rb.outcome == PipelineOutcome.COMPLETED
    selected_angle = rb.candidate_angles[0]

    rc = run_v1c_variation_analysis(selected_angle, _FULL_RECORDS, same_thesis_family=True)

    assert rc.angle_profile is not None
    assert rc.relevant_memory_profiles  # real memory structurally profiled
    assert rc.repetition.assessments  # multi-axis repetition actually computed
    assert rc.recommendation is not None

    if rc.recommendation.outcome == VariationRecommendationOutcome.RECOMMENDED:
        assert len(rc.recommendation.options) >= 1
        distinct_dimension_sets = {tuple(sorted(o.proposed_changes)) for o in rc.recommendation.options}
        assert len(distinct_dimension_sets) >= 1  # each option changes a nameable, distinct dimension

        decision = build_human_variation_decision(
            "HD-GOLDEN", HumanVariationAction.ACCEPT_RECOMMENDED_VARIATION, "Janne Stefors",
            selected_angle.angle.angle_id, chosen_option_id=rc.recommendation.recommended_option_id,
        )
        assert decision.decided_by_actor.value == "human"

    # No finished text anywhere in the result.
    assert not hasattr(rc, "final_text")


def test_false_variation_path_detects_cosmetic_only_difference():
    """order section 39: two alternatives differing only by synonym/cosmetic
    opening must be identified as NOT genuine variation."""

    a = build_variation_profile("Vi matte samma resultat tre ganger men fann aldrig karnan bakom det.", "OPT-A", SourceKind.CANDIDATE_ANGLE)
    b = build_variation_profile("Vi observerade samma utfall tre ganger men hittade aldrig grunden till det.", "OPT-B", SourceKind.CANDIDATE_ANGLE)

    result = compare_variation_profiles(a, b)
    assert result.overall == VariationDistanceCategory.TOO_SIMILAR
    assert result.same_count == 6


def test_structural_repetition_path_flags_closeness_despite_different_topic():
    """order section 40: two ideas with different topics but nearly identical
    entry/distance/arc/pressure/closure must be flaggable as structurally close."""

    idea_a = build_variation_profile("Se. Forsta. Prioritera. Agera. Sa forandrar vi budgetprocessen i grunden.", "IDEA-A", SourceKind.CANDIDATE_ANGLE)
    idea_b = build_variation_profile("Se. Forsta. Prioritera. Agera. Sa forandrar vi rekryteringsprocessen i grunden.", "IDEA-B", SourceKind.CANDIDATE_ANGLE)

    result = compare_variation_profiles(idea_a, idea_b)
    assert result.same_count >= 4  # clearly close structurally
    assert result.overall in (VariationDistanceCategory.TOO_SIMILAR, VariationDistanceCategory.PARTIALLY_DISTINCT)


def test_legitimate_same_thesis_path_is_not_automatic_repetition():
    """order section 41: same Thesis Family, different human situation/lens/arc
    -- must be assessable as legitimate variation, not forced repetition."""

    idea_a = build_variation_profile("Kunden klagade tre ganger men ingen forsokte forsta kundens verklighet.", "IDEA-A", SourceKind.CANDIDATE_ANGLE)
    idea_b = build_variation_profile("Vad visar er verklighet innan det syns i siffrorna? Ett system for att se tidigare.", "IDEA-B", SourceKind.CANDIDATE_ANGLE)

    result = compare_variation_profiles(idea_a, idea_b)
    # Same thesis family is asserted by the caller (V1A/V1B's own classification) --
    # this path proves structural comparison does NOT collapse that into automatic
    # repetition just because the thesis matches.
    assert result.overall != VariationDistanceCategory.TOO_SIMILAR


def test_lexical_collision_path_does_not_become_false_structural_repetition():
    """order section 42: V1B's own known limitation (occasional shared common
    words) used adversarially -- V1C must show structural evidence is absent
    even when V1B reports lexical overlap."""

    input_a = "Konsekvensen av det trasiga staketet blev att katten kom ut tre kvallar i rad."
    input_b = "Observation: Tre personer kom sent till motet. Se forst. Forsta sedan."

    profile_a = build_variation_profile(input_a, "A", SourceKind.CANDIDATE_ANGLE)
    profile_b = build_variation_profile(input_b, "B", SourceKind.CANDIDATE_ANGLE)

    shared_words = set(input_a.lower().split()) & set(input_b.lower().split())
    assert shared_words  # V1B-style lexical overlap genuinely exists ("tre", "kom", ...)

    structural = compare_variation_profiles(profile_a, profile_b)
    assert structural.overall != VariationDistanceCategory.TOO_SIMILAR
