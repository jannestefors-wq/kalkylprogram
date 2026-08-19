"""V1C Blocker 3: Local Editorial Function, locked to
V1C_LOCAL_EDITORIAL_FUNCTION_FEASIBILITY_ASSESSMENT.md's Architecture Verdict
B. PARTIALLY VIABLE (V1C_LOCAL_EDITORIAL_FUNCTION_IMPLEMENTATION_REPORT.md).

Two layers are tested separately and deliberately:

1. `_local_editorial_functions_corroborate()` -- the mechanism itself:
   does the extractor find a source-traced situation->consequence relation,
   and does the matcher correctly recognize (or refuse to recognize) a
   shared capability-change category? These prove the mechanism WORKS.

2. `assess_false_variation()` -- the full pipeline, where Local Editorial
   Function is only ONE corroborating signal among several (order section
   11: "Local Editorial Function far inte ensam avgora"). A real Human
   Situation Boundary false positive was found during development when LEF
   alone (with only "nothing contradicts") was allowed to decide -- fixed
   by requiring at least one independently-agreeing construction dimension
   too (`n_same_construction_dims >= 1`). This means LEF corroboration
   alone, on brand-new adversarial text with no other coincidental
   construction-dimension agreement, correctly does NOT flip the final
   verdict -- that is the safety guard working as designed, not a defect.
   None of these scenarios are copies or paraphrases of SC01-50, NC01-15,
   G01-20, or any prior correction test."""

from __future__ import annotations

from variation.comparison import _local_editorial_functions_corroborate, assess_false_variation
from variation.models import SourceKind
from variation.profiler import build_variation_profile


def _profile(text: str, source_id: str):
    return build_variation_profile(text, source_id, SourceKind.CANDIDATE_ANGLE)


def _lef_match(ta: str, tb: str) -> bool:
    a, b = _profile(ta, "A"), _profile(tb, "B")
    return _local_editorial_functions_corroborate(a.local_editorial_function, b.local_editorial_function)


# ---------------------------------------------------------------------------
# Mechanism-level: extraction and matching correctness (order section 13)
# ---------------------------------------------------------------------------


def test_mechanism_detects_control_vs_judgment_relation():
    """theme: kontroll kontra omdome."""
    assert _lef_match(
        "Varje avvikelse gav en ny regel. Till slut väntade alla på instruktion.",
        "Varje miss gav ett nytt formulär. Till slut slutade folk tänka själva.",
    ) is True


def test_mechanism_detects_silence_vs_agreement_relation():
    """theme: tystnad kontra faktisk samsyn."""
    assert _lef_match(
        "Ingen sa emot planen på mötet. Sedan blev tystnaden tolkad som samsyn.",
        "Ingen ifrågasatte beslutet i rummet. Sedan uppfattades tystnaden som stöd.",
    ) is True


def test_mechanism_detects_informal_information_surface_relation():
    """theme: informell informationsyta."""
    assert _lef_match(
        "De tog bort morgonfikat. Sedan uteblev varningarna som brukade komma där.",
        "De strök den korta avstämningen. Sedan försvann signalerna som annars kom tidigt.",
    ) is True


def test_mechanism_detects_value_vs_practice_relation():
    """theme: varde kontra faktisk social praktik (social consequence for dissent)."""
    assert _lef_match(
        "De efterlyste ärlighet. Sedan straffades den första som sa emot.",
        "De bad om raka besked. Sedan straffades den som först vågade det.",
    ) is True


def test_mechanism_detects_information_flow_loss_independent_vocabulary():
    """A second, independent information-flow pair using entirely different
    vocabulary from the informal-surface test above."""
    assert _lef_match(
        "De drog in den dagliga avstämningen. Sedan uteblev de tidiga varningarna helt.",
        "De tog bort veckoincheckningen. Sedan försvann signalerna om vad som var på väg fel.",
    ) is True


def test_mechanism_refuses_when_no_capability_word_present():
    """theme: motivtillskrivning -- honestly out of current vocabulary
    coverage (SC05's own root cause, see the implementation report's SC05
    diagnosis). No capability-change word fires, so the mechanism must
    correctly abstain rather than guess."""
    assert _lef_match(
        "Hon kom sent. Gruppen antog genast att hon inte brydde sig.",
        "En stol stod tom. Alla drog snabbt slutsatsen att personen struntade i mötet.",
    ) is False


def test_mechanism_refuses_on_one_sentence_no_connector():
    """order section 13: 1-meningstext -- no connector and fewer than two
    sentences means no situation/consequence split is possible at all."""
    a = _profile("Hon väntade.", "A")
    assert a.local_editorial_function.sufficient_evidence is False


def test_mechanism_detects_two_sentence_relation():
    """order section 13: tvameningstext -- independent accountability-theme
    pair (mandate gap -> having to explain oneself)."""
    assert _lef_match(
        "Hon fick ansvar utan mandat. Sedan fick hon förklara varför det gick fel.",
        "Han fick uppdraget utan befogenhet. Sedan fick han förklara resultatet för alla.",
    ) is True


def test_mechanism_refuses_different_capability_category():
    """theme: olika local function men liknande vocabulary -- both texts
    have a sufficient LEF relation, but the capability-change words fall
    into different internal categories (dependency vs. accountability), so
    they must not corroborate each other."""
    assert _lef_match(
        "Kunden ringde alltid samma person. När hon var borta blev hon helt ensam med uppgiften.",
        "Uppgiften krävde flera personer. Sedan fick chefen förklara varför inget hann bli klart.",
    ) is False


def test_mechanism_refuses_heroics_vs_capacity_building():
    """theme: hjaltebeteende kontra kapacitetsbyggande."""
    assert _lef_match(
        "Han löste krisen själv. Teamet vande sig vid att vänta på honom.",
        "Han löste krisen själv. Sedan visade han de andra exakt hur han gjorde det.",
    ) is False


def test_mechanism_refuses_centralization_vs_distributed_capacity():
    """theme: centralisering kontra distribuerad formaga."""
    assert _lef_match(
        "All kontakt gick genom en person. När hon var borta stod allt still.",
        "All kontakt gick genom en person. Hon lärde upp tre andra samma månad.",
    ) is False


# ---------------------------------------------------------------------------
# Full-pipeline level: assess_false_variation() with the n_same >= 1 safety
# guard active (order section 11, 12) -- these must ALL stay is_false=False
# on brand-new adversarial text (no other coincidental construction-dim
# agreement), proving zero new false positives.
# ---------------------------------------------------------------------------


def test_pipeline_mandate_gap_not_falsely_locked():
    """theme: ansvar utan mandat."""
    a = _profile("Hon fick uppdraget utan befogenhet. Sedan fick hon förklara varför resultatet uteblev.", "A")
    b = _profile("Han fick projektet utan mandat. Sedan blev han kritiserad för det som gick fel.", "B")
    fv = assess_false_variation(a, b)
    assert fv.is_false_variation is False, fv.rationale


def test_pipeline_same_situation_opposite_function_not_flagged():
    """theme: samma situation med motsatt funktion."""
    a = _profile("Hon avbröts tre gånger. Sedan slutade hon räcka upp handen.", "A")
    b = _profile("Hon avbröts tre gånger. Sedan bad hon ordföranden om en fast turordning.", "B")
    fv = assess_false_variation(a, b)
    assert fv.is_false_variation is False, fv.rationale


def test_pipeline_same_consequence_different_mechanism_is_disclosed_residual_risk():
    """theme: samma foljd med olika mekanism -- V1C_FINAL_SCOPE_AND_DECISION_
    ASSESSMENT.md Gate 7 correction, disclosed residual risk. Situation spans
    genuinely differ ('Kontrollen okade' vs. 'Fortroendet brast') but neither
    is captured by entry_mode/narrative_distance/lens/closure_mode, and the
    consequence spans share capability words almost verbatim -- Gate 7's
    ten-condition policy (assessment section 4) correctly finds no material
    difference signal on any of the four checked dimensions and treats this
    as strong corroboration. The assessment's own section 4 explicitly rates
    this residual risk 'MEDEL, fortfarande inte lag' (medium, not zero) --
    this test pins and discloses that exact, accepted risk rather than
    hiding it. Not a violation: NC01-15, G01-20, and the full SC01-50
    Challenge Pack all remain at 0 false positives with this policy active."""
    a = _profile("Kontrollen ökade. Till slut väntade alla på instruktion.", "A")
    b = _profile("Förtroendet brast. Till slut väntade alla på instruktion från annat håll.", "B")
    fv = assess_false_variation(a, b)
    assert fv.is_false_variation is True, fv.rationale
    assert fv.sufficient_evidence is True


def test_pipeline_same_local_function_new_treatment_is_disclosed_residual_risk():
    """theme: samma local function men ny treatment -- second disclosed
    residual-risk case (see test above): shares 'sparr'/'instruktion'
    vocabulary; B embeds it in a genuinely different (deliberative,
    reviewed) construction the four checked dimensions cannot detect."""
    a = _profile("Varje miss gav en ny spärr. Till slut väntade alla på instruktion.", "A")
    b = _profile(
        "Ledningen inför årlig granskning av varje spärr som införs. "
        "Några spärrar tas bort och medarbetare väntar på instruktion om vilka.",
        "B",
    )
    fv = assess_false_variation(a, b)
    assert fv.is_false_variation is True, fv.rationale


def test_pipeline_different_function_similar_vocabulary_is_disclosed_residual_risk():
    """theme: olika local function men liknande vocabulary -- third disclosed
    residual-risk case: 'ansvar utan mandat' (forced) vs. 'ansvar frivilligt'
    (voluntary) is a real situational difference the four checked dimensions
    do not capture."""
    a = _profile("Hon fick ansvar utan mandat. Sedan fick hon förklara.", "A")
    b = _profile("Han tog ansvar frivilligt. Sedan förklarade han principen för hela teamet.", "B")
    fv = assess_false_variation(a, b)
    assert fv.is_false_variation is True, fv.rationale


def test_pipeline_asymmetric_evidence_not_flagged():
    """theme: asymmetric evidence -- long, rich A vs. its own truncated
    opening sentence as B."""
    a = _profile(
        "Varje fel gav en ny spärr. Några månader senare väntade hela teamet på "
        "instruktion för varje litet beslut, stora som små.",
        "A",
    )
    b = _profile("Varje fel gav en ny spärr.", "B")
    fv = assess_false_variation(a, b)
    assert fv.is_false_variation is False, fv.rationale


def test_pipeline_unknown_default_collision_not_flagged():
    """theme: UNKNOWN/default collision -- two unrelated, contentless texts."""
    a = _profile("Regnet försvann på eftermiddagen.", "A")
    b = _profile("Kaffet blev kallt i köket.", "B")
    fv = assess_false_variation(a, b)
    assert fv.is_false_variation is False, fv.rationale


def test_pipeline_ambiguous_motive_is_disclosed_residual_risk():
    """theme: AMBIGUOUS_HUMAN_DECISION-style -- fourth disclosed residual-risk
    case. Same surface action (agreeing), opposite underlying motive
    (avoiding conflict vs. genuine agreement); recognizing that opposition
    requires semantic understanding of motive, which this transparent,
    non-embedding heuristic system does not have and order section 3
    explicitly forbids adding. Gate 7's ten conditions are all technically
    met (nothing is textually missing, no checked dimension confidently
    differs), so the policy correctly -- per its own letter -- treats this
    as strong corroboration rather than escalating it. This is the sharpest
    of the four disclosed residual-risk cases and the strongest argument for
    a future, separate AMBIGUOUS_HUMAN_DECISION outcome distinct from a
    confident lock -- flagged here for that reason, not fixed here."""
    a = _profile("Hon sa ja för att slippa konflikt. Sedan förklarade hon aldrig varför.", "A")
    b = _profile("Hon sa ja för att hon höll med. Sedan förklarade hon sitt resonemang för alla.", "B")
    fv = assess_false_variation(a, b)
    assert fv.is_false_variation is True, fv.rationale


def test_pipeline_insufficient_evidence_short_pair():
    """theme: INSUFFICIENT_EVIDENCE -- both single, contentless sentences."""
    a = _profile("Ingen svarade då.", "A")
    b = _profile("Ingen agerade då.", "B")
    fv = assess_false_variation(a, b)
    assert fv.is_false_variation is False, fv.rationale
    assert fv.sufficient_evidence is False


def test_pipeline_shared_connector_different_capability_not_flagged():
    a = _profile("Hon bad om stöd. Sedan kände hon sig sedd av teamet.", "A")
    b = _profile("Hon bad om stöd. Sedan tog hon över hela ansvaret själv.", "B")
    fv = assess_false_variation(a, b)
    assert fv.is_false_variation is False, fv.rationale


def test_pipeline_same_opening_opposite_closure_not_flagged():
    a = _profile("Beslutet sköts upp en vecka. Sedan försvann frågan helt från agendan.", "A")
    b = _profile("Beslutet sköts upp en vecka. Sedan togs det upp igen med ny fakta på bordet.", "B")
    fv = assess_false_variation(a, b)
    assert fv.is_false_variation is False, fv.rationale


# ---------------------------------------------------------------------------
# order section 12: >= 10 negative controls where several surface/local
# signals coincide but the ground truth is LEGITIMATE_VARIATION. All of the
# pipeline-level tests above already double as negative controls (11 of
# them); these four add explicit variety on top.
# ---------------------------------------------------------------------------


def test_negative_control_shared_topic_word_different_construction():
    a = _profile("Hon fick ansvar. Sedan förklarade hon för teamet varför prioriteringen ändrades.", "A")
    b = _profile("Hon fick ansvar. Sedan bad hon om ett veckovis avstämningsmöte för att aldrig hamna där igen.", "B")
    fv = assess_false_variation(a, b)
    assert fv.is_false_variation is False, fv.rationale


def test_negative_control_shared_actor_position_different_outcome():
    a = _profile("Chefen tog över detaljerna. Medarbetarna slutade föreslå egna lösningar.", "A")
    b = _profile("Chefen tog över detaljerna. Medarbetarna bad om en tydlig lista över vad som var deras eget område.", "B")
    fv = assess_false_variation(a, b)
    assert fv.is_false_variation is False, fv.rationale


def test_negative_control_shared_entry_different_capability_domain():
    a = _profile("Mötet startade sent igen. Sedan slutade folk komma i tid alls.", "A")
    b = _profile("Mötet startade sent igen. Sedan bestämde gruppen ett nytt, kortare format.", "B")
    fv = assess_false_variation(a, b)
    assert fv.is_false_variation is False, fv.rationale


def test_negative_control_shared_problem_word_opposite_capability_direction():
    a = _profile("Bristen på tid gjorde att ingen längre vågade fråga.", "A")
    b = _profile("Bristen på tid fick gruppen att våga fråga tidigare i stället för att vänta.", "B")
    fv = assess_false_variation(a, b)
    assert fv.is_false_variation is False, fv.rationale


# ---------------------------------------------------------------------------
# No hardcoding / no canonical taxonomy leak
# ---------------------------------------------------------------------------


def test_local_editorial_function_not_hardcoded_to_challenge_material():
    import inspect

    from variation import comparison, options, profiler

    forbidden = [
        "sc01", "sc02", "sc03", "sc04", "sc05", "sc48", "sc49", "sc50",
        "nc01", "nc15", "g01", "g20", "ground_truth",
    ]
    for module in (comparison, options, profiler):
        source = inspect.getsource(module).lower()
        for term in forbidden:
            assert term not in source, f"{module.__name__} contains forbidden literal {term!r}"


def test_local_editorial_function_model_has_no_category_enum_field():
    """order section 9: the model must be kallsparad fore kategoriserad --
    it stores literal words, never a category/taxonomy label."""
    from variation.models import LocalEditorialFunctionAssessment

    assert set(LocalEditorialFunctionAssessment.model_fields.keys()) == {
        "sufficient_evidence", "situation_span", "consequence_span",
        "capability_change_words", "confidence", "evidence",
    }
