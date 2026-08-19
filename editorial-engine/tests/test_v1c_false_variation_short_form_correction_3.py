"""V1C False Variation Blocker 3: short text / INSUFFICIENT_EVIDENCE
Structural Movement (V1C_FALSE_VARIATION_SHORT_FORM_CORRECTION_REPORT.md).

The Blind Independent Re-Audit (V1C_FALSE_VARIATION_BLIND_REAUDIT_REPORT.md)
found that when Structural Movement is INSUFFICIENT_EVIDENCE (fewer than 3
sentences on either side -- the common case for realistic short-form text),
every False Variation tier that existed before this correction was
structurally unreachable, and the fall-through silently read externally as
a confident LEGITIMATE_VARIATION even when there was zero evidence for that
either. This file is entirely NEW, independently-authored adversarial
scenarios and negative controls -- none are copies or paraphrases of the
frozen SC01-SC50 Blind Challenge Pack (which stays regression evidence only,
read via `test_v1c_false_variation_blind_challenge_regression.py`)."""

from __future__ import annotations

import inspect

from variation.comparison import assess_false_variation, compare_variation_profiles
from variation.models import SourceKind
from variation.profiler import build_variation_profile


def _profile(text: str, source_id: str):
    return build_variation_profile(text, source_id, SourceKind.CANDIDATE_ANGLE)


# ---------------------------------------------------------------------------
# order section 8: >= 20 new, independent adversarial scenarios across the
# required categories. Every pair below was verified to trigger
# movement=INSUFFICIENT_EVIDENCE (the short-form path) before being locked
# in as a permanent assertion.
# ---------------------------------------------------------------------------


def test_short_same_construction_low_lexical_question_pattern():
    a = _profile("Varför fortsätter vi göra det som inte fungerar? Vem vågar säga det högt?", "A")
    b = _profile("Varför byter vi aldrig strategi när resultatet uteblir? Vem tar första steget?", "B")
    fv = assess_false_variation(a, b)
    assert fv.is_false_variation is True, fv.rationale
    assert fv.sufficient_evidence is True


def test_short_same_construction_low_lexical_imperative_pattern():
    a = _profile("Se helheten. Agera nu.", "A")
    b = _profile("Lyft blicken. Samla laget.", "B")
    fv = assess_false_variation(a, b)
    assert fv.is_false_variation is True, fv.rationale
    assert fv.sufficient_evidence is True


def test_short_oov_paraphrase_question_pattern():
    """Deliberately avoids common editorial keywords -- same construction
    (double-question opening/closing), unrelated vocabulary."""
    a = _profile("Varför blundar vi för det uppenbara? Vem törs bryta tystnaden?", "A")
    b = _profile("Varför förnekar vi det vi redan vet? Vem orkar ta första steget?", "B")
    fv = assess_false_variation(a, b)
    assert fv.is_false_variation is True, fv.rationale
    assert fv.sufficient_evidence is True


def test_short_oov_paraphrase_imperative_pattern():
    a = _profile("Prioritera sanningen. Agera direkt.", "A")
    b = _profile("Korrigera bilden. Be om hjälp.", "B")
    fv = assess_false_variation(a, b)
    assert fv.is_false_variation is True, fv.rationale
    assert fv.sufficient_evidence is True


def test_short_high_lexical_different_construction_not_flagged():
    """Shares its entire opening sentence verbatim; the second text simply
    continues into a materially different treatment. Must NOT be flagged."""
    a = _profile("Vi behöver mer ansvar i teamet.", "A")
    b = _profile("Vi behöver mer ansvar i teamet. Därför lät vi den mest erfarna avgöra sista ordet.", "B")
    fv = assess_false_variation(a, b)
    assert fv.is_false_variation is False, fv.rationale


def test_short_same_thesis_new_treatment_not_flagged():
    a = _profile("Ansvar utan mandat skapar bara skuld.", "A")
    b = _profile("Hon fick ansvar. Men fick hon nagonsin frågan om hon ville ha det?", "B")
    fv = assess_false_variation(a, b)
    assert fv.is_false_variation is False, fv.rationale


def test_short_different_thesis_similar_construction_detected():
    """Different topics entirely (helping colleagues vs. abandoning projects)
    but the same double-question construction -- False Variation is about
    construction, not thesis, so this SHOULD be flagged."""
    a = _profile("Varför slutar vi fråga varandra om hjälp? Vem märker det första tecknet?", "A")
    b = _profile("Varför stannar vi kvar i projekt som inte längre fungerar? Vem säger stopp?", "B")
    fv = assess_false_variation(a, b)
    assert fv.is_false_variation is True, fv.rationale
    assert fv.sufficient_evidence is True


def test_short_human_situation_boundary_workplace_vs_family_not_flagged():
    a = _profile("På kontoret nickade alla åt planen. Efteråt ändrade chefen allt själv.", "A")
    b = _profile("Vid middagsbordet nickade alla åt planen. Efteråt bokade pappan om allt själv.", "B")
    fv = assess_false_variation(a, b)
    assert fv.is_false_variation is False, fv.rationale


def test_short_human_situation_boundary_school_vs_sport_not_flagged():
    a = _profile("Läraren höjde rösten och eleven tystnade.", "A")
    b = _profile("Tränaren höjde rösten och spelaren tystnade.", "B")
    fv = assess_false_variation(a, b)
    assert fv.is_false_variation is False, fv.rationale


def test_short_ambiguous_evidence_not_locked_as_false_variation():
    """Same surface action, opposite underlying motive -- genuinely
    ambiguous. Must not be confidently locked as False Variation."""
    a = _profile("Hon sa ja för att slippa konflikt.", "A")
    b = _profile("Hon sa ja för att hon faktiskt höll med.", "B")
    fv = assess_false_variation(a, b)
    assert fv.is_false_variation is False, fv.rationale


def test_one_sentence_pair_genuinely_insufficient():
    """order section 6, Short FULL/default: a true one-sentence fragment
    pair with essentially no propositional content must read as
    INSUFFICIENT_EVIDENCE, not a confident LEGITIMATE_VARIATION."""
    a = _profile("Ingen kom.", "A")
    b = _profile("Ingen stannade.", "B")
    fv = assess_false_variation(a, b)
    assert fv.is_false_variation is False
    assert fv.sufficient_evidence is False, fv.rationale


def test_one_sentence_pair_genuinely_substantive_not_insufficient():
    """A real single sentence with actual content (order section 8's own
    '1-meningstext' category) must NOT be swept into INSUFFICIENT_EVIDENCE
    just because it triggered no keyword heuristic -- that would be the same
    'absence of evidence treated as evidence' defect this correction fixes,
    just relabeled (see the length-gate rationale in comparison.py)."""
    a = _profile("När kunden höjde rösten slutade säljaren att lyssna på vad som faktiskt sades.", "A")
    b = _profile("När kollegan höjde rösten slutade chefen att lyssna på vad som faktiskt sades.", "B")
    fv = assess_false_variation(a, b)
    assert fv.sufficient_evidence is True, fv.rationale


def test_two_sentence_pair_same_construction_detected():
    a = _profile("Se helheten. Agera nu, prioritera rätt.", "A")
    b = _profile("Lyft blicken. Samla laget, korrigera kursen.", "B")
    fv = assess_false_variation(a, b)
    assert fv.is_false_variation is True, fv.rationale
    assert fv.sufficient_evidence is True


def test_asymmetric_evidence_rich_vs_truncated_not_flagged():
    """order section 3/4's asymmetric-richness finding: a long, evidence-rich
    text and a truncated fragment that only shares the generic opening
    sentence must NOT be treated as corroborated -- the truncated side never
    got a chance to confirm or contradict A's other dimensions."""
    a = _profile(
        "Tre säljare kom sent till samma möte. Ingen sa något. "
        "Men tystnaden kändes som ett beslut i sig. Konsekvensen blev sjunkande förtroende.",
        "A",
    )
    b = _profile("Tre säljare kom sent till samma möte.", "B")
    fv = assess_false_variation(a, b)
    assert fv.is_false_variation is False, fv.rationale


def test_unknown_default_collision_unrelated_topics_not_flagged_1():
    a = _profile("Det regnade den dagen.", "A")
    b = _profile("Kaffet var kallt igen.", "B")
    fv = assess_false_variation(a, b)
    assert fv.is_false_variation is False, fv.rationale


def test_unknown_default_collision_unrelated_topics_not_flagged_2():
    a = _profile("Byggnaden stod tom i flera år.", "A")
    b = _profile("Trädgården växte igen på sommaren.", "B")
    fv = assess_false_variation(a, b)
    assert fv.is_false_variation is False, fv.rationale


def test_question_pattern_variant_workplace_topic_detected():
    a = _profile("Varför väntar vi alltid till sist med det svåra samtalet? Vem tar första ordet?", "A")
    b = _profile("Varför skjuter vi upp det obekväma beslutet varje gång? Vem bryter tystnaden?", "B")
    fv = assess_false_variation(a, b)
    assert fv.is_false_variation is True, fv.rationale
    assert fv.sufficient_evidence is True


def test_imperative_pattern_variant_health_topic_detected():
    a = _profile("Se symtomen. Agera tidigt.", "A")
    b = _profile("Samla fakta. Prioritera vilan.", "B")
    fv = assess_false_variation(a, b)
    assert fv.is_false_variation is True, fv.rationale
    assert fv.sufficient_evidence is True


def test_short_different_thesis_similar_construction_imperative_variant():
    a = _profile("Se problemet. Agera direkt.", "A")
    b = _profile("Lyft frågan. Be om hjälp.", "B")
    fv = assess_false_variation(a, b)
    assert fv.is_false_variation is True, fv.rationale


def test_two_sentence_pair_high_lexical_different_construction_not_flagged():
    a = _profile("Kulturen syns när någon gör fel.", "A")
    b = _profile("Kulturen syns när någon gör fel. I vårt team blev felet en lärdom för alla.", "B")
    fv = assess_false_variation(a, b)
    assert fv.is_false_variation is False, fv.rationale


def test_short_ambiguous_evidence_second_pair_not_locked():
    a = _profile("Han tackade nej för att skydda familjen.", "A")
    b = _profile("Han tackade nej för att han inte trodde på planen.", "B")
    fv = assess_false_variation(a, b)
    assert fv.is_false_variation is False, fv.rationale


# ---------------------------------------------------------------------------
# order section 9: >= 10 new negative controls. False positives are a hard
# gate -- these deliberately construct partial/coincidental overlap and
# verify the mechanism still refuses to call False Variation.
# ---------------------------------------------------------------------------


def test_nc_partial_match_with_direct_address_contradiction():
    """Both open/close on a question (2 dims would match), but narrative
    distance genuinely, confidently contradicts (you/vi) -- must block."""
    a = _profile("Varför slutar du fråga om hjälp? Märker du inte längre tecknen?", "A")
    b = _profile("Varför slutar vi fråga om hjälp? Märker ingen längre tecknen?", "B")
    fv = assess_false_variation(a, b)
    assert fv.is_false_variation is False, fv.rationale


def test_nc_asymmetric_richness_second_independent_example():
    a = _profile(
        "Fyra kunder klagade samma vecka. Ingen agerade. "
        "Men klagomålen byggde en bild ingen ville se. Konsekvensen blev en förlorad kontrakt.",
        "A",
    )
    b = _profile("Fyra kunder klagade samma vecka.", "B")
    fv = assess_false_variation(a, b)
    assert fv.is_false_variation is False, fv.rationale


def test_nc_movement_available_short_form_path_does_not_apply():
    """Three sentences on both sides -- Structural Movement CAN be computed,
    so the short-form path must not fire at all; the texts genuinely diverge
    (imperative sequence vs. a question interrupting it)."""
    a = _profile("Se problemet. Förstå orsaken. Agera på riktig grund.", "A")
    b = _profile("Se problemet. Men vem äger egentligen lösningen? Fråga innan du agerar.", "B")
    comparison = compare_variation_profiles(a, b)
    assert comparison.movement_comparison.category.value != "INSUFFICIENT_EVIDENCE"
    fv = assess_false_variation(a, b)
    assert fv.is_false_variation is False, fv.rationale


def test_nc_lens_match_alone_does_not_corroborate():
    """Both mention 'ansvar' (shared lens keyword, thesis-adjacent) but the
    construction itself genuinely differs -- lens must stay excluded from
    corroboration exactly as in V1C Correction 2."""
    a = _profile("Ansvar kräver mod att säga nej.", "A")
    b = _profile("Varför är ansvar så svårt att bära? Vem vågar erkänna det?", "B")
    fv = assess_false_variation(a, b)
    assert fv.is_false_variation is False, fv.rationale


def test_nc_single_dimension_coincidence_not_enough():
    """Only entry_mode coincides (both SITUATION via quantity+event words);
    closure genuinely differs -- one matching dimension alone must never be
    enough (the >= 2 floor found necessary during Blocker 3 testing)."""
    a = _profile("Tre kunder hörde av sig samma vecka. Vi noterade det och gick vidare.", "A")
    b = _profile("Tre kunder hörde av sig samma vecka. Konsekvensen blev ett nytt rutin.", "B")
    fv = assess_false_variation(a, b)
    assert fv.is_false_variation is False, fv.rationale


def test_nc_direct_address_shared_but_pressure_contradicts():
    a = _profile("Du vet redan svaret. Du väljer att inte agera på det.", "A")
    b = _profile("Du vet redan svaret. Väljer du verkligen att inte agera på det?", "B")
    fv = assess_false_variation(a, b)
    assert fv.is_false_variation is False, fv.rationale


def test_nc_system_level_shared_but_entry_contradicts():
    a = _profile("Organisationen bar på en tystnad ingen ville nämna.", "A")
    b = _profile("Tre chefer i organisationen slutade svara på frågor samma manad.", "B")
    fv = assess_false_variation(a, b)
    assert fv.is_false_variation is False, fv.rationale


def test_nc_close_human_shared_but_consequence_contradicts():
    a = _profile("Chefen sa inget under mötet. Ingen vågade fråga varför.", "A")
    b = _profile("Chefen sa inget under mötet. Konsekvensen blev ett skriftligt klagomål.", "B")
    fv = assess_false_variation(a, b)
    assert fv.is_false_variation is False, fv.rationale


def test_nc_one_sentence_substantive_pair_not_flagged_as_false_variation():
    """The genuinely-substantive one-sentence pair (sufficient_evidence=True
    elsewhere in this file) must also not be confidently flagged as False
    Variation -- it shares no confidently-detected construction dimension."""
    a = _profile("När kunden höjde rösten slutade säljaren att lyssna på vad som faktiskt sades.", "A")
    b = _profile("När kollegan höjde rösten slutade chefen att lyssna på vad som faktiskt sades.", "B")
    fv = assess_false_variation(a, b)
    assert fv.is_false_variation is False, fv.rationale


def test_nc_short_form_insufficient_never_reads_as_false_variation():
    """The genuinely-insufficient one-sentence pair must resolve to
    NOT-false-variation, never a false lock in either direction."""
    a = _profile("Ingen kom.", "A")
    b = _profile("Ingen stannade.", "B")
    fv = assess_false_variation(a, b)
    assert fv.is_false_variation is False


# ---------------------------------------------------------------------------
# Root cause / no-hardcoding verification
# ---------------------------------------------------------------------------


def test_short_form_mechanism_not_hardcoded_to_challenge_pack():
    """order section 7/8: no SC-ID, Challenge phrase, or Ground Truth lookup
    may appear anywhere in the production short-form logic."""
    from variation import comparison, options, profiler

    forbidden = ["sc01", "sc02", "sc48", "sc49", "sc50", "challenge_pack", "ground_truth", "blind_challenge"]
    for module in (comparison, options, profiler):
        source = inspect.getsource(module).lower()
        for term in forbidden:
            assert term not in source, f"{module.__name__} contains forbidden literal {term!r}"


def test_sufficient_evidence_field_defaults_true_for_normal_cases():
    """Boundary check: a completely ordinary, evidence-rich comparison must
    not accidentally be marked insufficient by the new field."""
    a = _profile("Se problemet. Förstå orsaken tydligt. Agera pa riktig grund, inte pa symptom.", "A")
    b = _profile("Se problemet. Förstå orsaken tydligt. Agera pa riktig grund, inte pa symptom.", "B")
    fv = assess_false_variation(a, b)
    assert fv.sufficient_evidence is True
    assert fv.is_false_variation is True
