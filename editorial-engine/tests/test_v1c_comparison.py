"""V1C TEST 9-14, 22-23 (order section 37)."""

from __future__ import annotations

from memory.ingestion import load_editorial_memory
from memory.models import TextCompleteness
from variation.comparison import assess_false_variation, assess_multi_axis_repetition, compare_variation_profiles
from variation.models import SourceKind, VariationDistanceCategory
from variation.profiler import build_variation_profile, build_variation_profile_for_memory_record


def test_9_structural_comparison_is_transparent():
    a = build_variation_profile("Se. Forsta. Agera. Sa flyttar vi verksamheten framat.", "A", SourceKind.CANDIDATE_ANGLE)
    b = build_variation_profile("Vad visar er verklighet innan det syns i siffrorna?", "B", SourceKind.CANDIDATE_ANGLE)
    result = compare_variation_profiles(a, b)
    assert len(result.dimension_comparisons) == 6
    for c in result.dimension_comparisons:
        assert c.dimension
        assert isinstance(c.same, bool)


def test_10_lexical_overlap_does_not_automatically_become_structural_repetition():
    a = build_variation_profile("Konsekvensen av det trasiga staketet blev att katten kom ut tre kvallar i rad.", "A", SourceKind.CANDIDATE_ANGLE)
    b = build_variation_profile("Observation: Tre personer kom sent till motet. Se forst. Forsta sedan.", "B", SourceKind.CANDIDATE_ANGLE)
    structural = compare_variation_profiles(a, b)
    assert structural.overall == VariationDistanceCategory.STRUCTURALLY_DISTINCT

    repetition = assess_multi_axis_repetition(
        same_thesis_family=False, same_angle_core_terms=False, structural_comparison=structural, lexical_overlap_terms=["tre", "kom"],
    )
    lexical = next(a_ for a_ in repetition.assessments if a_.axis.value == "lexical")
    structural_axis = next(a_ for a_ in repetition.assessments if a_.axis.value == "structural")
    assert lexical.detected is True
    assert structural_axis.detected is False


def test_11_false_variation_detected_for_synonym_only_change():
    """V1C Correction: both sentences here are a single sentence each (one
    period at the very end), below the 3-sentence movement-evidence floor
    (order section 10) -- structural_arc legitimately goes UNKNOWN on both
    (INSUFFICIENT_EVIDENCE on the movement comparison, not silently counted
    as "same"), so 5 of 6 -- not 6 of 6 -- OBSERVED dimensions are
    identical. 5/6 still clears the TOO_SIMILAR threshold (>=5)."""
    a = build_variation_profile("Vi matte samma resultat tre ganger men fann aldrig karnan bakom det.", "A", SourceKind.CANDIDATE_ANGLE)
    b = build_variation_profile("Vi observerade samma utfall tre ganger men hittade aldrig grunden till det.", "B", SourceKind.CANDIDATE_ANGLE)
    fv = assess_false_variation(a, b)
    assert fv.is_false_variation is True
    assert len(fv.identical_dimensions) == 5
    assert "structural_arc" in fv.changed_dimensions


def test_12_same_thesis_family_can_still_be_legitimate_variation():
    """Same underlying thesis, but structurally distinct because the human
    situation/expression differs (order section 12/41)."""
    a = build_variation_profile("Kunden klagade tre ganger men ingen forsokte forsta kundens verklighet.", "A", SourceKind.CANDIDATE_ANGLE)
    b = build_variation_profile("Vad visar er verklighet innan det syns i siffrorna? Ett system for att se tidigare.", "B", SourceKind.CANDIDATE_ANGLE)
    structural = compare_variation_profiles(a, b)
    assert structural.overall in (VariationDistanceCategory.STRUCTURALLY_DISTINCT, VariationDistanceCategory.PARTIALLY_DISTINCT)

    repetition = assess_multi_axis_repetition(
        same_thesis_family=True, same_angle_core_terms=False, structural_comparison=structural, lexical_overlap_terms=["verklighet"],
    )
    thesis_axis = next(a_ for a_ in repetition.assessments if a_.axis.value == "thesis")
    structural_axis = next(a_ for a_ in repetition.assessments if a_.axis.value == "structural")
    assert thesis_axis.detected is True  # shared thesis, named honestly
    assert structural_axis.detected is False  # but NOT automatically structural repetition


def test_13_different_topic_can_still_carry_structural_repetition_risk():
    a = build_variation_profile("Se. Forsta. Prioritera. Agera. Sa forandrar vi budgetprocessen helt.", "A", SourceKind.CANDIDATE_ANGLE)
    b = build_variation_profile("Se. Forsta. Prioritera. Agera. Sa forandrar vi rekryteringen helt.", "B", SourceKind.CANDIDATE_ANGLE)
    structural = compare_variation_profiles(a, b)
    # Different topics (budget vs recruitment) but the same structural shape --
    # structural comparison must be able to flag this regardless of topic words.
    assert structural.same_count >= 3


def test_14_same_structural_form_is_advisory_not_an_absolute_block():
    """order section 14/'TEST 14': identical structure is a flag for human
    judgment, not an automatic hard veto -- the option is still surfaced
    with its true distinctiveness category, never silently discarded.

    V1C Correction: these two texts genuinely have the same observed
    movement sequence (both read as observation -> concrete_situation),
    so all six OBSERVED dimensions -- including the now movement-derived
    structural_arc -- legitimately match."""
    a = build_variation_profile("Se. Forsta. Agera. Sa flyttar vi verksamheten snabbt framat.", "A", SourceKind.CANDIDATE_ANGLE)
    b = build_variation_profile("Se. Forsta. Agera. Sa flyttar vi verksamheten gradvis framat.", "B", SourceKind.CANDIDATE_ANGLE)
    structural = compare_variation_profiles(a, b)
    assert structural.overall == VariationDistanceCategory.TOO_SIMILAR
    # The comparison itself does not raise, block, or hide -- it reports the category
    # and leaves the decision to whatever calls it (ultimately a human).
    assert structural.same_count == 6


def test_22_lexical_collision_scenario_shows_structural_evidence_absent():
    records = load_editorial_memory()
    work_006 = next(r for r in records if r.content_id == "content-work-006")
    profile_006 = build_variation_profile_for_memory_record(work_006)

    noise = build_variation_profile("Konsekvensen av det trasiga staketet blev att katten kom ut tre kvallar i rad.", "NOISE", SourceKind.CANDIDATE_ANGLE)
    structural = compare_variation_profiles(noise, profile_006)
    assert structural.overall != VariationDistanceCategory.TOO_SIMILAR


def test_23_reader_feedback_never_referenced_in_variation_module():
    import ast
    from pathlib import Path

    variation_dir = Path(__file__).parent.parent / "variation"
    for py_file in variation_dir.glob("*.py"):
        tree = ast.parse(py_file.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                assert "reader_feedback" not in node.module.lower(), f"{py_file.name} imports {node.module!r}"
                assert "voice" not in node.module.lower(), f"{py_file.name} imports {node.module!r}"
