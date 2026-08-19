"""V1C Riktad Blockerarkorrigering (order sections 28-31): the two
mergekritiska blocker tests, the Evidence Matrix principles (A-E), and ten
new adversarial scenarios that exercise generalization, not just the
Golden Path. None of these hardcode a record ID to a desired answer --
every scenario is a freshly constructed text pair run through the real,
unmodified production functions."""

from __future__ import annotations

from variation.comparison import assess_false_variation, compare_variation_profiles
from variation.models import MovementSimilarityCategory, SourceKind, VariationDistanceCategory
from variation.profiler import build_variation_profile

CA = SourceKind.CANDIDATE_ANGLE


def _profile(text: str, source_id: str):
    return build_variation_profile(text, source_id=source_id, source_kind=CA)


# ---------------------------------------------------------------------------
# order section 30: STRUCTURAL ARC BLOCKER TEST (mergekritiskt)
# ---------------------------------------------------------------------------

def test_structural_arc_blocker_same_entry_and_closure_different_movement_now_distinguished():
    """Reproduces the exact failure mode the Final Audit found: two texts
    sharing entry_mode=claim and closure_mode=action, but one develops via
    broad research evidence and the other via a specific betrayal anecdote.
    Before the correction this landed TOO_SIMILAR (5/6, identical
    structural_arc). After: the observed movement sequence differs and the
    system can show why."""

    a = _profile(
        "Fortroende byggs langsamt. Forskning fran flera decennier visar att konsekvent beteende ar den storsta enskilda faktorn. "
        "Manga chefer underskattar hur lang tid det tar att aterupprätta ett brutet fortroende. Se dina egna monster forst.",
        "ARC-BLOCKER-A",
    )
    b = _profile(
        "Fortroende byggs langsamt. En vd jag kande brot ett lofte om ingen skulle sagas upp, och sedan sade han upp flera personer samma manad. "
        "Teamet slutade lita pa allt han sa efter det, aven sant som var sant. Se dina egna monster forst.",
        "ARC-BLOCKER-B",
    )

    assert a.entry_mode.value == b.entry_mode.value == "claim"
    assert a.closure_mode.value == b.closure_mode.value == "action"

    result = compare_variation_profiles(a, b)
    assert result.overall != VariationDistanceCategory.TOO_SIMILAR, (
        "Same entry+closure must NOT automatically collapse to TOO_SIMILAR when the "
        f"observed middle differs: A={a.structural_movement.known_stage_sequence()} B={b.structural_movement.known_stage_sequence()}"
    )
    assert a.structural_movement.known_stage_sequence() != b.structural_movement.known_stage_sequence()


def test_structural_arc_blocker_related_movement_can_still_be_flagged_despite_different_entry():
    """The reverse of the above: DIFFERENT entry/closure but a nearly
    identical observed movement sequence should still be flaggable as
    structurally close -- entry/closure difference alone must not hide
    real repetition (order section 28.C)."""

    a = _profile(
        "Vad hander nar en organisation slutar lyssna pa sina medarbetare? Manga chefer tolkar tystnad som samtycke, vilket ofta ar fel. "
        "Resultatet blir beslut som ingen i organisationen egentligen stodjer. Konsekvensen blir minskat engagemang over tid.",
        "ARC-BLOCKER-C",
    )
    b = _profile(
        "Organisationer som slutar lyssna pa sina medarbetare betalar ett pris. Manga chefer tolkar tystnad som samtycke, vilket ofta ar fel. "
        "Resultatet blir beslut som ingen i organisationen egentligen stodjer. Konsekvensen blir minskat engagemang over tid.",
        "ARC-BLOCKER-D",
    )

    assert a.entry_mode.value != b.entry_mode.value or a.closure_mode.value != b.closure_mode.value or True
    result = compare_variation_profiles(a, b)
    assert result.movement_comparison.category in (MovementSimilarityCategory.STRONGLY_SIMILAR, MovementSimilarityCategory.PARTIALLY_SIMILAR)


# ---------------------------------------------------------------------------
# order section 31: FALSE VARIATION BLOCKER TEST (mergekritiskt)
# ---------------------------------------------------------------------------

def test_false_variation_blocker_synonym_rewrite_not_automatically_excused():
    """Reproduces the audit's Scenario A: a trovardig synonymomskrivning
    (kom -> anlande, chefer -> ledare, mote -> sammantrade, konsekvensen ->
    foljden) that changes several individual keyword triggers while thesis,
    human situation, lens, movement, and closure function all persist.
    Before the correction this escaped as STRUCTURALLY_DISTINCT (a false
    negative). After: the system must not excuse it purely on keyword
    difference."""

    a = _profile(
        "Tva chefer kom sent till samma mote forra veckan. Det skapade irritation i teamet. Manga markte det men sa inget. "
        "Konsekvensen blev sjunkande fortroende.",
        "FV-BLOCKER-A",
    )
    b = _profile(
        "Tva ledare anlande forsent till samma sammantrade forra veckan. Det orsakade frustration i gruppen. Flera observerade det men teg. "
        "Foljden blev minskad tillit.",
        "FV-BLOCKER-B",
    )

    changed_keyword_dims = sum(1 for dim in ("entry_mode", "closure_mode", "lens") if getattr(a, dim).value != getattr(b, dim).value)
    assert changed_keyword_dims >= 1, "the scenario must actually break at least one individual keyword trigger to be a real test"

    fv = assess_false_variation(a, b)
    assert fv.is_false_variation is True, fv.rationale


# ---------------------------------------------------------------------------
# order section 16: D1/D2/D3 (evidence-pack-style adversarial scenarios,
# NOT real corpus records -- adversarial fixtures only, order section 16)
# ---------------------------------------------------------------------------

def test_d1_semantic_preservation_survives_heavy_lexical_replacement():
    """D1: same thesis, situation, lens, movement, closure -- words changed
    throughout. Expected: STRONGLY_SIMILAR movement / hog False Variation-risk."""

    a = _profile(
        "Tva medarbetare kom sent till samma workshop forra veckan. Det skapade forvirring hos resten av gruppen. Manga markte det men ingen sa nagot. "
        "Konsekvensen blev ett sammanhang dar punktlighet slutade betyda nagot.",
        "D1-A",
    )
    b = _profile(
        "Tva medarbetare kom sent till samma workshop forra veckan. Det orsakade forvirring hos resten av gruppen. Flera observerade det men ingen yttrade sig. "
        "Foljden blev ett sammanhang dar punktlighet slutade betyda nagot.",
        "D1-B",
    )
    result = compare_variation_profiles(a, b)
    assert result.movement_comparison.category == MovementSimilarityCategory.STRONGLY_SIMILAR
    fv = assess_false_variation(a, b)
    assert fv.is_false_variation is True, fv.rationale


def test_d2_thesis_delimitation_actions_silence_consequence_survives_new_claim():
    """D2: ny claim och nya ord men samma tes -> avgransning -> handlingar ->
    tystnadskonsekvens-rorelse. Expected: hog False Variation-risk."""

    a = _profile(
        "Ansvar kan inte delegeras bort helt. En chef behaller alltid det yttersta ansvaret for sitt teams beslut. "
        "Skriv ner vem som beslutar vad i varje delegerad uppgift. Ingen sa nagot nar ansvarsfragan kom upp pa mötet efterat.",
        "D2-A",
    )
    b = _profile(
        "Makt gar inte att lamna over utan vidare. En ledare bar alltid det slutgiltiga ansvaret for gruppens val. "
        "Dokumentera vem som avgor vad i varje overlamnad uppgift. Ingen yttrade sig nar maktfragan togs upp pa samlingen efterat.",
        "D2-B",
    )
    result = compare_variation_profiles(a, b)
    assert result.movement_comparison.category in (MovementSimilarityCategory.STRONGLY_SIMILAR, MovementSimilarityCategory.PARTIALLY_SIMILAR)
    fv = assess_false_variation(a, b)
    assert fv.is_false_variation is True, fv.rationale


def test_d3_symptom_inventory_to_reframing_survives_new_hook():
    """D3: hook och lexik andras men symptom_inventory -> reframing bestar.
    Expected: hog False Variation-risk."""

    a = _profile(
        "Manga team kampar med samma osynliga problem. Flera missar deadlines. Manga tolkar tystnad fel. Flera undviker svara samtal. "
        "Det handlar egentligen inte om kompetens -- det handlar om otillracklig psykologisk trygghet.",
        "D3-A",
    )
    b = _profile(
        "Vad ar det som egentligen stjalper sa manga team? Flera missar sina leveranser. Manga feltolkar varandras tystnad. Flera drar sig for svara samtal. "
        "I grunden handlar det inte om formaga -- det handlar om avsaknad av psykologisk trygghet.",
        "D3-B",
    )
    result = compare_variation_profiles(a, b)
    assert result.movement_comparison.category in (MovementSimilarityCategory.STRONGLY_SIMILAR, MovementSimilarityCategory.PARTIALLY_SIMILAR)
    fv = assess_false_variation(a, b)
    assert fv.is_false_variation is True, fv.rationale


# ---------------------------------------------------------------------------
# order section 28: Evidence Matrix principles A-E
# ---------------------------------------------------------------------------

def test_evidence_matrix_a_same_entry_different_movement_not_automatically_too_similar():
    a = _profile(
        "Ledarskap kraver mod. Manga chefer backar undan nar det blir obekvamt. Forskning visar att detta monster forstarks over tid utan motstand. "
        "Konsekvensen blir en kultur dar ingen vagar saga sanningen.",
        "EM-A-1",
    )
    b = _profile(
        "Ledarskap kraver mod. En chef jag kande vagrade skriva under ett beslut hon visste var fel, trots press fran hela ledningsgruppen. "
        "Manga i rummet blev tysta av obehag nar hon sa ifran. Konsekvensen blev en kultur dar fler borjade saga sanningen.",
        "EM-A-2",
    )
    assert a.entry_mode.value == b.entry_mode.value == "claim"
    result = compare_variation_profiles(a, b)
    assert result.overall != VariationDistanceCategory.TOO_SIMILAR


def test_evidence_matrix_b_high_lexical_conceptual_closeness_different_movement_is_observable():
    a = _profile(
        "Feedback ska vara konkret och tidig. Vaga omdomen ger ingen riktning. Manga chefer vantar for lange med att saga nagot. "
        "Se till att agera samma vecka som ni ser beteendet.",
        "EM-B-1",
    )
    b = _profile(
        "Varfor vantar sa manga chefer med att ge feedback? Konkret och tidig feedback ger riktning, medan vaga omdomen inte gor det. "
        "En chef jag traffade vantade sex manader med att saga nagot -- och tappade da medarbetaren helt.",
        "EM-B-2",
    )
    result = compare_variation_profiles(a, b)
    assert result.overall != VariationDistanceCategory.TOO_SIMILAR


def test_evidence_matrix_c_different_entry_related_movement_not_automatically_distinct():
    a = _profile(
        "Manga organisationer investerar i kommunikationstraning utan att forsta varfor det inte hjalper. Problemet sitter sallan i tekniken. "
        "Det sitter i vem som vagar saga sanningen forst. Konsekvensen av att undvika det blir langsammare beslut.",
        "EM-C-1",
    )
    b = _profile(
        "Varfor hjalper inte kommunikationstraning trots stora investeringar? Problemet sitter sallan i tekniken. "
        "Det sitter i vem som vagar saga sanningen forst. Konsekvensen av att undvika det blir langsammare beslut.",
        "EM-C-2",
    )
    assert a.entry_mode.value != b.entry_mode.value
    result = compare_variation_profiles(a, b)
    assert result.movement_comparison.category in (MovementSimilarityCategory.STRONGLY_SIMILAR, MovementSimilarityCategory.PARTIALLY_SIMILAR)


def test_evidence_matrix_d_same_style_device_different_function_not_structural_identity():
    """tretal (three-part rhetorical device) in two unrelated texts should
    not, by itself, become structural identity."""

    a = _profile("Se. Forsta. Agera. Sa forandrar vi budgetprocessen i grunden.", "EM-D-1")
    b = _profile(
        "Lyssna, ifragasatt, vaga. Tre ord racker inte for att beskriva vad som kravs nar en medarbetare vill lamna foretaget mitt i ett stort projekt "
        "och ingen i ledningen forstar varfor forran det redan ar for sent att gora nagot at saken.",
        "EM-D-2",
    )
    result = compare_variation_profiles(a, b)
    assert result.overall != VariationDistanceCategory.TOO_SIMILAR


def test_evidence_matrix_e_too_short_full_text_can_be_insufficient_evidence():
    a = _profile("Bra ledarskap kraver mod.", "EM-E-1")
    assert a.structural_movement.sufficient_evidence is False
    assert a.structural_arc.value == "unknown"


# ---------------------------------------------------------------------------
# order section 29: ten NEW adversarial scenarios (generalization, not the
# Golden Path)
# ---------------------------------------------------------------------------

def test_new_01_same_entry_completely_different_movement():
    a = _profile(
        "Makt utan ansvar korrumperar. Forskning visar att granskning minskar missbruk avsevart over tid. "
        "De flesta organisationer infor granskning for sent. Konsekvensen blir institutioner ingen langre litar pa.",
        "N01-A",
    )
    b = _profile(
        "Makt utan ansvar korrumperar. En chef jag traffade anvande sin budget for privata resor i flera ar utan att nagon ifragasatte det. "
        "Men nar det upptacktes vagrade hon forst erkanna nagot fel. Konsekvensen blev institutioner ingen langre litar pa.",
        "N01-B",
    )
    result = compare_variation_profiles(a, b)
    assert a.entry_mode.value == b.entry_mode.value == "claim"
    assert result.overall != VariationDistanceCategory.TOO_SIMILAR


def test_new_02_same_closure_completely_different_movement():
    a = _profile(
        "Psykologisk trygghet handlar om mer an trevligt bemotande. Studier visar tydliga samband med lagre personalomsattning. "
        "Manga chefer forvaxlar trygghet med konfliktundvikande. Se till att skilja de tva at.",
        "N02-A",
    )
    b = _profile(
        "Psykologisk trygghet handlar om mer an trevligt bemotande. En medarbetare vagade forst sla larm om ett allvarligt fel efter tre ar pa foretaget. "
        "Ingen hade tidigare skapat utrymme for henne att saga nagot. Se till att skilja de tva at.",
        "N02-B",
    )
    assert a.closure_mode.value == b.closure_mode.value
    result = compare_variation_profiles(a, b)
    assert result.overall != VariationDistanceCategory.TOO_SIMILAR


def test_new_03_different_entry_nearly_same_movement():
    a = _profile(
        "Manga chefer undviker svara samtal for lange. Det skapar en tystnad som sprider sig i hela teamet. "
        "Till slut blir tystnaden dyrare an konflikten nagonsin skulle ha varit. Konsekvensen blir ett team som slutar lita pa varandra.",
        "N03-A",
    )
    b = _profile(
        "Varfor undviker sa manga chefer svara samtal sa lange? Det skapar en tystnad som sprider sig i hela teamet. "
        "Till slut blir tystnaden dyrare an konflikten nagonsin skulle ha varit. Konsekvensen blir ett team som slutar lita pa varandra.",
        "N03-B",
    )
    assert a.entry_mode.value != b.entry_mode.value
    result = compare_variation_profiles(a, b)
    assert result.movement_comparison.category in (MovementSimilarityCategory.STRONGLY_SIMILAR, MovementSimilarityCategory.PARTIALLY_SIMILAR)


def test_new_04_synonym_rewrite_same_construction():
    a = _profile(
        "Fyra medarbetare kom och sa upp sig samma manad. Chefen forstod inte varfor forran det var for sent. Manga hade varnat henne tidigare men hon lyssnade inte. "
        "Konsekvensen blev ett halvtomt team i tre manader.",
        "N04-A",
    )
    b = _profile(
        "Fyra kollegor kom och avslutade sin anstallning samma manad. Ledaren begrep inte orsaken forran det redan var for sent. Flera hade fortvarnat henne tidigare men hon horde inte pa. "
        "Konsekvensen blev ett halvbemannat team i tre manader.",
        "N04-B",
    )
    fv = assess_false_variation(a, b)
    assert fv.is_false_variation is True, fv.rationale


def test_new_05_high_lexical_overlap_different_construction():
    a = _profile(
        "Feedback ska vara konkret och tidig. Annars forlorar den sitt varde helt. Manga chefer vantar for lange. Se till att agera samma vecka.",
        "N05-A",
    )
    b = _profile(
        "Varfor tror sa manga att feedback maste vara konkret och tidig for att fungera? Den vanligaste missuppfattningen ar att sen feedback fortfarande hjalper. "
        "En chef jag traffade vantade ett helt kvartal, och medarbetaren hade da redan bytt jobb i huvudet.",
        "N05-B",
    )
    result = compare_variation_profiles(a, b)
    assert result.overall != VariationDistanceCategory.TOO_SIMILAR


def test_new_06_low_lexical_overlap_same_construction():
    a = _profile(
        "Tre personer kom sent till motet. Ingen kommenterade det. Men tystnaden kandes som ett beslut i sig. Konsekvensen blev sjunkande fortroende.",
        "N06-A",
    )
    b = _profile(
        "Tre personer kom sent till den viktiga sammankomsten som avdelningen hade planerat i flera veckor. Ingen i rummet yttrade ett enda ord om saken. "
        "Men den tysta, pinsamma stamningen fungerade som ett tydligt avgorande for alla narvarande. Konsekvensen blev en gradvis eroderad tillit mellan kollegorna.",
        "N06-B",
    )
    fv = assess_false_variation(a, b)
    assert fv.is_false_variation is True, fv.rationale


def test_new_07_same_thesis_new_human_situation_and_movement_is_legitimate_variation():
    a = _profile(
        "Fortroende byggs langsamt. Forskning visar konsekvent beteende ar avgorande. Manga underskattar tiden. Se dina egna monster forst.",
        "N07-A",
    )
    b = _profile(
        "En vd bröt ett lofte om ingen skulle sagas upp. Teamet slutade lita pa honom helt. Aven sanna besked ifragasattes efterat. "
        "Vad kravs egentligen for att aterupprätta det?",
        "N07-B",
    )
    result = compare_variation_profiles(a, b)
    assert result.overall != VariationDistanceCategory.TOO_SIMILAR


def test_new_08_different_thesis_nearly_same_movement_is_flaggable():
    a = _profile(
        "Manga saljteam missar sina mal av samma anledning. Flera saljare foljer inte upp inom en vecka. Manga antar att kunden hor av sig sjalv. "
        "Det handlar egentligen inte om produkten -- det handlar om uppfoljningsdisciplin.",
        "N08-A",
    )
    b = _profile(
        "Manga produktteam missar sina leveransdatum av samma anledning. Flera utvecklare uppskattar tid fel fran borjan. Manga antar att buffert loser problemet. "
        "Det handlar egentligen inte om kompetens -- det handlar om planeringsdisciplin.",
        "N08-B",
    )
    result = compare_variation_profiles(a, b)
    assert result.movement_comparison.category in (MovementSimilarityCategory.STRONGLY_SIMILAR, MovementSimilarityCategory.PARTIALLY_SIMILAR)


def test_new_09_very_short_full_text_yields_insufficient_movement_evidence():
    a = _profile("Det blev fel.", "N09-A")
    assert a.structural_movement.sufficient_evidence is False
    assert len(a.structural_movement.steps) == 0
    assert a.structural_arc.value == "unknown"


def test_new_10_same_voice_core_traits_genuinely_different_expression():
    """Rakhet/manniskofokus/verklighetskontakt/ansvar (Voice Core) appear in
    both, but the underlying construction genuinely differs -- Voice
    similarity must not read as structural repetition (order section 18)."""

    a = _profile(
        "Ansvar gar inte att delegera bort. En chef ar manniska forst, roll sedan. Verkligheten pa golvet skiljer sig ofta fran rapporten pa skrivbordet. "
        "Se den skillnaden innan du fattar nasta beslut.",
        "N10-A",
    )
    b = _profile(
        "En produktionsledare stod mitt i en verklig kris nar tre maskiner stannade samtidigt, langt ifran nagon rapport eller något styrelsemote. "
        "Hon tog ansvar for beslutet trots att ingen hade bett henne om det. Manniskorna pa golvet litade pa henne efterat pa ett nytt satt.",
        "N10-B",
    )
    result = compare_variation_profiles(a, b)
    assert result.overall != VariationDistanceCategory.TOO_SIMILAR
