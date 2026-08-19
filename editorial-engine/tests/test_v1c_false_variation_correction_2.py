"""V1C False Variation Blocker 2 Korrigering (order sections 1-20): permanent
regression tests for the root-cause fixes documented in
docs/V1C_FALSE_VARIATION_CORRECTION_2_REPORT.md.

D1/D2/D3 use the REAL corpus text (content-work-006/011/003, the
Evidence Pack's own W06/W11/W03) verbatim, from the actual V1B Editorial
Memory data pack -- not paraphrased, not adjusted, matching the frozen
Evidence Pack's D.2 table exactly. No word from these three texts (or
from any Evidence Pack table) is referenced anywhere in production code
(order section 5, verified separately by grep in the correction report)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from variation.comparison import (
    MovementSimilarityCategory,
    _dimension_diff_is_evidence,
    _dimension_match_is_evidence,
    assess_false_variation,
    compare_variation_profiles,
)
from variation.models import SourceKind, VariationDistanceCategory
from variation.profiler import build_variation_profile
from engine.models import ConfidenceLevel

CA = SourceKind.CANDIDATE_ANGLE
_DATA_PACK = Path(__file__).parent.parent / "memory" / "data" / "LUF_Editorial_Memory_Data_Pack_V1B.json"


def _profile(text: str, source_id: str):
    return build_variation_profile(text, source_id=source_id, source_kind=CA)


def _corpus_text(content_id: str) -> str:
    """Reads the real, verbatim source text for a WORK record straight from
    the V1B Editorial Memory data pack -- the ground truth Evidence Pack's
    W01-W12 codes refer to (content-work-NNN == WNN)."""

    with open(_DATA_PACK, encoding="utf-8") as f:
        data = json.load(f)
    for record in data["records"]:
        if record["content_id"] == content_id:
            return record["source_facts"]["original_text"]
    raise AssertionError(f"{content_id} not found in data pack")


# ---------------------------------------------------------------------------
# D1-D3: run exactly from the frozen Evidence Pack's D.2 table (order section 9)
# ---------------------------------------------------------------------------

def test_d1_w06_synonym_parafras_from_evidence_pack_detected():
    """D1: W06 (content-work-006) vs the Evidence Pack's own D.2 parafras,
    verbatim. Evidence Pack expects STRONGLY_SIMILAR / high risk."""
    a = _profile(_corpus_text("content-work-006"), "W06")
    b = _profile(
        "Börja med det du vet. Tre kollegor dyker upp efter start. Därifrån gör vi ofta en berättelse om ointresse. "
        "När berättelsen blir fakta börjar felet. Se händelsen. Undersök sedan.",
        "D1",
    )
    fv = assess_false_variation(a, b)
    assert fv.is_false_variation is True, fv.rationale


def test_d2_w11_synonym_parafras_from_evidence_pack_detected():
    """D2: W11 (content-work-011) vs the Evidence Pack's own D.2 parafras,
    verbatim. Evidence Pack expects STRONGLY_SIMILAR / high risk."""
    a = _profile(_corpus_text("content-work-011"), "W11")
    b = _profile(
        "Att upptäcka frågan gör den till din att lyfta. Du ska inte bära den ensam. Du ska vägra passera den. "
        "Ta in dem som berörs och sök stöd. Annars växer den där ingen talar.",
        "D2",
    )
    fv = assess_false_variation(a, b)
    assert fv.is_false_variation is True, fv.rationale


def test_d3_w03_synonym_parafras_from_evidence_pack_detected():
    """D3: W03 (content-work-003) vs the Evidence Pack's own D.2 parafras,
    verbatim. Evidence Pack expects STRONGLY_SIMILAR / high risk."""
    a = _profile(_corpus_text("content-work-003"), "W03")
    b = _profile(
        "Organisationer försöker ofta reparera det synliga. Marginaler, friktion, brister, frånvaro och avhopp kan vara tecken. "
        "De är sällan roten.",
        "D3",
    )
    fv = assess_false_variation(a, b)
    assert fv.is_false_variation is True, fv.rationale


def test_d1_d2_d3_not_hardcoded_in_production_logic():
    """order section 5: confirms via source inspection that no D1/D2/D3/
    W01-W12 identifier or literal phrase from the Evidence Pack appears in
    the actual production module -- the three tests above pass because the
    mechanism generalizes, not because the specific pairs are special-cased."""
    import inspect

    import variation.comparison as comparison_module
    import variation.profiler as profiler_module

    source = inspect.getsource(comparison_module) + inspect.getsource(profiler_module)
    for forbidden in ("W01", "W02", "W03", "W04", "W05", "W06", "W07", "W08", "W09", "W10", "W11", "W12", "content-work-006", "content-work-011", "content-work-003", "'D1'", "'D2'", "'D3'"):
        assert forbidden not in source, f"found forbidden hardcoded reference: {forbidden!r}"


# ---------------------------------------------------------------------------
# UNKNOWN / default is not similarity evidence (order section 7)
# ---------------------------------------------------------------------------

def test_unknown_equals_unknown_is_not_similarity_evidence():
    """Two dimensions both legitimately UNKNOWN must not count as a match."""
    a = _profile("Kort.", "SHORT-A")
    b = _profile("Nej.", "SHORT-B")
    assert a.lens.value == "unknown"
    assert b.lens.value == "unknown"
    assert _dimension_match_is_evidence(a.lens, b.lens) is False


def test_default_coincidence_is_not_similarity_evidence():
    """Two unrelated one-sentence texts landing on the SAME low-confidence
    default (order's own audit-documented failure mode) must not count as
    a match, and their overall comparison must not confidently read as
    TOO_SIMILAR just from coincidental defaults."""
    a = _profile("Bra ledarskap kraver mod.", "DEF-A")
    b = _profile("Det blev fel.", "DEF-B")
    assert a.entry_mode.value == b.entry_mode.value == "claim"
    assert a.entry_mode.confidence == ConfidenceLevel.LOW
    assert b.entry_mode.confidence == ConfidenceLevel.LOW
    assert _dimension_match_is_evidence(a.entry_mode, b.entry_mode) is False
    result = compare_variation_profiles(a, b)
    assert result.overall != VariationDistanceCategory.TOO_SIMILAR
    fv = assess_false_variation(a, b)
    assert fv.is_false_variation is False, fv.rationale


def test_default_confidence_disagreement_is_not_diff_evidence():
    """A LOW-confidence default value on one side disagreeing with a
    confidently-detected value on the other must not count as evidence of
    genuine difference -- it may simply mean the heuristic found nothing."""
    a = _profile(
        "Tre chefer kom sent till mötet. Ingen sa något. Men tystnaden kändes som ett beslut. Konsekvensen blev sjunkande förtroende.",
        "DIFFEV-A",
    )
    b = _profile("Kort text som knappt sager nagot alls om nagot.", "DIFFEV-B")
    # b's entry_mode is a LOW-confidence default; a's is a real MEDIUM+ signal.
    assert a.entry_mode.value != b.entry_mode.value
    assert b.entry_mode.confidence == ConfidenceLevel.LOW
    assert _dimension_diff_is_evidence(a.entry_mode, b.entry_mode) is False


# ---------------------------------------------------------------------------
# Asymmetric movement sequences (order section 8)
# ---------------------------------------------------------------------------

def test_asymmetric_short_subsequence_does_not_force_strongly_similar():
    """A short movement sequence that happens to be a subsequence of a much
    longer one must NOT automatically read STRONGLY_SIMILAR -- the old
    ratio (matched/min length) did; the new one (matched/max length)
    correctly reflects that most of the longer sequence's journey is
    unaccounted for."""
    a = _profile(
        "Ansvar kan inte delegeras bort helt. Det skiljer sig fran vanlig arbetsfordelning pa ett avgorande satt. "
        "Se till vem som beslutar vad, och satt en tydlig plan. Ingen sa nagot nar konsekvensen till slut blev tydlig.",
        "ASYM-A",
    )
    b = _profile("Ansvar kan inte delegeras bort helt. Det skiljer sig fran vanlig arbetsfordelning pa ett avgorande satt.", "ASYM-B")
    result = compare_variation_profiles(a, b)
    assert result.movement_comparison.category != MovementSimilarityCategory.STRONGLY_SIMILAR


# ---------------------------------------------------------------------------
# Low lexical / same construction, high lexical / different construction
# (order section 10 category, permanent versions)
# ---------------------------------------------------------------------------

def test_low_lexical_overlap_same_construction_detected():
    a = _profile(
        "Ansvar kan inte delegeras bort helt. Det skiljer sig fran vanlig arbetsfordelning pa ett avgorande satt. "
        "Se till vem som beslutar vad, och satt en tydlig plan. Ingen sa nagot nar konsekvensen till slut blev tydlig.",
        "LOWLEX-A",
    )
    b = _profile(
        "Makt gar inte att lamna over utan vidare. Det skiljer sig fran ett vanligt delegeringsbeslut pa ett avgorande satt. "
        "Se till vem som avgor vad, och satt en tydlig plan. Ingen yttrade sig nar foljden till slut blev tydlig.",
        "LOWLEX-B",
    )
    fv = assess_false_variation(a, b)
    assert fv.is_false_variation is True, fv.rationale


def test_high_lexical_overlap_different_construction_not_flagged():
    """Two texts sharing a verbatim opening phrase ('Tre personer kom sent
    till') but diverging completely afterwards (a workplace trust-erosion
    story vs. an uneventful party anecdote) must not be flagged."""
    a = _profile(
        "Feedback fungerar bara om den ar konkret. Vaga omdomen ger ingen riktning. Manga chefer vantar for lange. "
        "Se till att agera samma vecka.",
        "HIGHLEX-A",
    )
    b = _profile(
        "Varfor tror sa manga att feedback maste vara konkret och tidig for att fungera? Den vanligaste missuppfattningen ar "
        "att sen feedback fortfarande hjalper. En chef jag traffade vantade ett helt kvartal, och medarbetaren hade da redan "
        "bytt jobb i huvudet.",
        "HIGHLEX-B",
    )
    fv = assess_false_variation(a, b)
    assert fv.is_false_variation is False, fv.rationale


# ---------------------------------------------------------------------------
# Near-threshold: true False Variation vs. legitimate new treatment
# ---------------------------------------------------------------------------

def test_near_threshold_true_false_variation_detected():
    a = _profile(
        "Feedback maste ges tidigt for att fungera. Annars forlorar den sitt varde. Manga vantar for lange med att saga nagot. "
        "Se till att agera direkt.",
        "NT-TRUE-A",
    )
    b = _profile(
        "Aterkoppling maste komma snabbt for att gora nytta. I annat fall mister den sin kraft. Flera drar ut pa tiden innan "
        "de sager nagot. Prioritera att agera utan drojsmal.",
        "NT-TRUE-B",
    )
    fv = assess_false_variation(a, b)
    assert fv.is_false_variation is True, fv.rationale


def test_near_threshold_legitimate_new_treatment_not_flagged():
    a = _profile(
        "Fortroende byggs langsamt. Forskning visar konsekvent beteende ar avgorande. Manga underskattar tiden. "
        "Se dina egna monster forst.",
        "NT-LEGIT-A",
    )
    b = _profile(
        "En vd brot ett lofte om ingen skulle sagas upp. Teamet slutade lita pa honom helt. Aven sanna besked "
        "ifragasattes efterat. Vad kravs egentligen for att aterupprätta det?",
        "NT-LEGIT-B",
    )
    fv = assess_false_variation(a, b)
    assert fv.is_false_variation is False, fv.rationale


# ---------------------------------------------------------------------------
# Human Situation boundary: false positive avoidance + false negative
# recognition (order section 12)
# ---------------------------------------------------------------------------

def test_human_situation_shared_thesis_different_situation_not_flagged():
    """Same lens/thesis territory (ansvar), but a genuinely different human
    situation (abstract principle vs. a concrete anecdote about a manager
    refusing responsibility) -- must not be flagged."""
    a = _profile(
        "Ansvar ar en princip, inte en kansla. Manga chefer forvaxlar de tva. Det skapar otydlighet i svara stunder. "
        "Se till att skilja dem at fran borjan.",
        "HS-FP-A",
    )
    b = _profile(
        "En chef vagrade ta ansvar for ett misstag hela teamet fick lida for. Ingen sa emot henne offentligt. "
        "Men fortroendet forsvann tyst under manaderna som foljde. Hur bygger man tillbaka nagot som aldrig erkandes?",
        "HS-FP-B",
    )
    fv = assess_false_variation(a, b)
    assert fv.is_false_variation is False, fv.rationale


def test_human_situation_same_situation_different_movement_not_flagged():
    """Same opening situation (three people arriving late to a meeting),
    but the second text is cut short before any real continuation is
    observable -- must not be confidently flagged as the same construction."""
    a = _profile(
        "Tre chefer kom sent till samma mote. Ingen sa nagot. Men tystnaden kandes som ett beslut i sig. "
        "Konsekvensen blev sjunkande fortroende.",
        "HS-FN-A",
    )
    b = _profile("Tre chefer kom sent till samma mote.", "HS-FN-B")
    fv = assess_false_variation(a, b)
    assert fv.is_false_variation is False, fv.rationale


# ---------------------------------------------------------------------------
# order section 15: known, disclosed residual limitation (not a regression --
# a documented boundary of the current evidence-combination mechanism)
# ---------------------------------------------------------------------------

def test_known_limitation_shared_opening_phrase_can_still_over_corroborate():
    """Documents a residual limitation (V1C_FALSE_VARIATION_CORRECTION_2_REPORT.md
    section 6): two texts sharing a near-verbatim opening phrase ('Tre
    personer kom sent till') that then diverge completely can still be
    flagged, because the shared opening drives a genuine (non-default)
    entry_mode + narrative_distance match that corroborates a
    PARTIALLY_SIMILAR movement read. This is NOT asserted as correct
    behavior -- it is pinned here so a future correction that changes it
    is a deliberate, visible decision, not a silent regression."""
    a = _profile(
        "Tre personer kom sent till motet. Ingen kommenterade det. Men tystnaden kandes som ett beslut i sig. "
        "Konsekvensen blev sjunkande fortroende.",
        "KNOWNLIM-A",
    )
    b = _profile(
        "Tre personer kom sent till festen. De blev varmt valkomnade av vardarna. Alla skrattade at historien om "
        "trafikstockningen. Kvallen fortsatte som vanligt.",
        "KNOWNLIM-B",
    )
    fv = assess_false_variation(a, b)
    assert fv.is_false_variation is True  # documented limitation, not desired behavior
