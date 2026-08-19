"""
V1C Variation Profiler (order sections 6, 11-14).

Smallest transparent, deterministic, rule-based analysis that works -- no
embeddings, no external NLP library, no LLM call required (order section
31). Every dimension value is derived from an explainable textual
signal, carries its own evidence string, and can legitimately be
`UNKNOWN` when the signal isn't there (order section 12: "Det ar battre
an falsk precision").

Only ever called on text a caller has already confirmed is safe to treat
as full, structurally-analyzable prose -- see
`build_variation_profile_for_memory_record()`, which is the one place
the FULL/PARTIAL boundary (order section 10) is technically enforced,
not just documented.
"""

from __future__ import annotations

import re
import uuid
from datetime import datetime, timezone

from schema import Provenance
from schema.enums import Actor, EvidenceCertainty

from engine.models import ConfidenceLevel
from memory.models import EditorialMemoryRecord, TextCompleteness

from .models import (
    DIMENSION_EVIDENCE_STATUS,
    ClosureMode,
    DimensionAssessment,
    DisclosurePace,
    EmotionalTemperature,
    EntryMode,
    Lens,
    LocalEditorialFunctionAssessment,
    MovementStage,
    MovementStep,
    NarrativeDistance,
    RhetoricalPressure,
    SourceKind,
    StructuralArc,
    StructuralMovementAssessment,
    VariationProfile,
)

ANALYSIS_LOGIC_VERSION = "variation-v1c-001"
"""order section 8: reuses Provenance.analysis_logic_version, no parallel versioning system."""

_IMPERATIVE_VERBS = {"se", "forsta", "agera", "prioritera", "mat", "matt", "korrigera", "lyft", "samla", "lat", "gor", "satt", "be"}
_ROLE_WORDS = {"person", "personer", "chef", "chefen", "medarbetare", "kollega", "kollegan", "ledare", "team", "teamet"}
_SECOND_PERSON = {"du", "dig", "din", "dina", "ni", "er", "era"}
_SYSTEM_WORDS = {"verksamheten", "organisationen", "system", "systemet"}
_QUANTITY_WORDS = {"tva", "tre", "fyra", "fem", "sex", "sju", "atta", "nio", "tio"}
_CONCRETE_EVENT_VERBS = {"kom", "sa", "hande", "gjorde", "kande"}

_LENS_KEYWORDS = [
    ("ansvar", Lens.RESPONSIBILITY),
    ("makt", Lens.POWER),
    ("konsekvens", Lens.CONSEQUENCE),
    ("relation", Lens.RELATION),
    ("tillit", Lens.RELATION),
    ("verksamheten", Lens.SYSTEM),
    ("organisationen", Lens.SYSTEM),
    ("jag ", Lens.INDIVIDUAL_EXPERIENCE),
]

_REFRAMING_MARKERS = ("egentligen", "i grunden", "handlar om", "i sjalva verket", "pa riktigt")
_DISTINCTION_MARKERS = ("skiljer sig", "till skillnad", "inte detsamma", "ar inte samma sak")
_PRINCIPLE_WORDS = {"ansvar", "princip", "roll", "grundregel", "princippen", "makt"}
_INVENTORY_WORDS = {"flera", "manga", "aterkommande"}


def _normalize(text: str) -> str:
    return "".join(ch.lower() if ch.isalnum() or ch.isspace() else " " for ch in text)


def _words(text: str) -> set[str]:
    return set(_normalize(text).split())


def _sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p for p in parts if p]


def _assess_entry_mode(text: str) -> DimensionAssessment:
    sentences = _sentences(text)
    window = " ".join(sentences[:4])
    window_words = _words(window)

    if sentences and sentences[0].rstrip().endswith("?"):
        return DimensionAssessment(
            value=EntryMode.QUESTION.value, confidence=ConfidenceLevel.HIGH,
            evidence="Forsta meningen slutar med frageteck.",
            evidence_status=DIMENSION_EVIDENCE_STATUS["entry_mode"],
        )
    if (window_words & _QUANTITY_WORDS) and (window_words & (_CONCRETE_EVENT_VERBS | {"motet", "mote"})):
        return DimensionAssessment(
            value=EntryMode.SITUATION.value, confidence=ConfidenceLevel.MEDIUM,
            evidence=f"Konkret hande/antal-markor tidigt i texten: {sorted(window_words & (_QUANTITY_WORDS | _CONCRETE_EVENT_VERBS | {'motet','mote'}))}.",
            evidence_status=DIMENSION_EVIDENCE_STATUS["entry_mode"],
        )
    imperative_hits = window_words & _IMPERATIVE_VERBS
    if len(imperative_hits) >= 2:
        return DimensionAssessment(
            value=EntryMode.PROCESS.value, confidence=ConfidenceLevel.MEDIUM,
            evidence=f"Flera korta imperativ tidigt i texten: {sorted(imperative_hits)}.",
            evidence_status=DIMENSION_EVIDENCE_STATUS["entry_mode"],
        )
    if sentences and _normalize(sentences[0]).split()[:1] and _normalize(sentences[0]).startswith(("resultatet", "konsekvensen", "effekten")):
        return DimensionAssessment(
            value=EntryMode.CONSEQUENCE.value, confidence=ConfidenceLevel.MEDIUM,
            evidence="Forsta meningen inleds med ett resultat-/konsekvensord.",
            evidence_status=DIMENSION_EVIDENCE_STATUS["entry_mode"],
        )
    if sentences:
        return DimensionAssessment(
            value=EntryMode.CLAIM.value, confidence=ConfidenceLevel.LOW,
            evidence="Ingen konkret situation, process, fraga eller konsekvens-markor hittad -- generell paststaende antas som standard, lag confidence.",
            evidence_status=DIMENSION_EVIDENCE_STATUS["entry_mode"],
        )
    return DimensionAssessment(
        value=EntryMode.UNKNOWN.value, confidence=ConfidenceLevel.LOW,
        evidence="For lite text for att avgora.", evidence_status=DIMENSION_EVIDENCE_STATUS["entry_mode"],
    )


def _assess_lens(text: str) -> DimensionAssessment:
    lowered = _normalize(text)
    best: tuple[int, str, Lens] | None = None
    for keyword, lens in _LENS_KEYWORDS:
        idx = lowered.find(keyword)
        if idx != -1 and (best is None or idx < best[0]):
            best = (idx, keyword, lens)
    if best is None:
        return DimensionAssessment(
            value=Lens.UNKNOWN.value, confidence=ConfidenceLevel.LOW,
            evidence="Ingen av de kanda lens-nyckelorden hittades i texten.",
            evidence_status=DIMENSION_EVIDENCE_STATUS["lens"],
        )
    _, keyword, lens = best
    return DimensionAssessment(
        value=lens.value, confidence=ConfidenceLevel.MEDIUM,
        evidence=f"Forsta forekommande lens-nyckelordet i texten ar {keyword!r}.",
        evidence_status=DIMENSION_EVIDENCE_STATUS["lens"],
    )


def _assess_narrative_distance(text: str) -> DimensionAssessment:
    words = _words(text)
    if words & _SECOND_PERSON:
        return DimensionAssessment(
            value=NarrativeDistance.DIRECT_ADDRESS.value, confidence=ConfidenceLevel.HIGH,
            evidence=f"Andra person-tilltal hittat: {sorted(words & _SECOND_PERSON)}.",
            evidence_status=DIMENSION_EVIDENCE_STATUS["narrative_distance"],
        )
    if words & _ROLE_WORDS:
        return DimensionAssessment(
            value=NarrativeDistance.CLOSE_HUMAN.value, confidence=ConfidenceLevel.MEDIUM,
            evidence=f"Namngiven mansklig roll i texten: {sorted(words & _ROLE_WORDS)}.",
            evidence_status=DIMENSION_EVIDENCE_STATUS["narrative_distance"],
        )
    if words & _SYSTEM_WORDS:
        return DimensionAssessment(
            value=NarrativeDistance.SYSTEM_LEVEL.value, confidence=ConfidenceLevel.MEDIUM,
            evidence=f"Systemniva-ord i texten: {sorted(words & _SYSTEM_WORDS)}.",
            evidence_status=DIMENSION_EVIDENCE_STATUS["narrative_distance"],
        )
    return DimensionAssessment(
        value=NarrativeDistance.OBSERVER.value, confidence=ConfidenceLevel.LOW,
        evidence="Varken tilltal, namngiven roll eller systemord hittades -- observatorsposition antas som standard, lag confidence.",
        evidence_status=DIMENSION_EVIDENCE_STATUS["narrative_distance"],
    )


def _assess_rhetorical_pressure(text: str) -> DimensionAssessment:
    lowered = _normalize(text)
    words = set(lowered.split())
    if "?" in text:
        return DimensionAssessment(
            value=RhetoricalPressure.QUESTION.value, confidence=ConfidenceLevel.HIGH,
            evidence="Texten innehaller ett frageteck.", evidence_status=DIMENSION_EVIDENCE_STATUS["rhetorical_pressure"],
        )
    if "men" in words:
        return DimensionAssessment(
            value=RhetoricalPressure.CONTRAST.value, confidence=ConfidenceLevel.MEDIUM,
            evidence="Texten innehaller kontrastordet 'men'.", evidence_status=DIMENSION_EVIDENCE_STATUS["rhetorical_pressure"],
        )
    if "konsekvens" in lowered:
        return DimensionAssessment(
            value=RhetoricalPressure.CONSEQUENCE.value, confidence=ConfidenceLevel.MEDIUM,
            evidence="Texten innehaller ordet 'konsekvens'.", evidence_status=DIMENSION_EVIDENCE_STATUS["rhetorical_pressure"],
        )
    imperative_hits = words & _IMPERATIVE_VERBS
    if len(imperative_hits) >= 2:
        return DimensionAssessment(
            value=RhetoricalPressure.IMPERATIVE.value, confidence=ConfidenceLevel.MEDIUM,
            evidence=f"Flera imperativ i texten: {sorted(imperative_hits)}.", evidence_status=DIMENSION_EVIDENCE_STATUS["rhetorical_pressure"],
        )
    return DimensionAssessment(
        value=RhetoricalPressure.QUIET_OBSERVATION.value, confidence=ConfidenceLevel.LOW,
        evidence="Inga kontrast-, fraga-, konsekvens- eller imperativsignaler hittades.",
        evidence_status=DIMENSION_EVIDENCE_STATUS["rhetorical_pressure"],
    )


def _assess_closure_mode(text: str) -> DimensionAssessment:
    sentences = _sentences(text)
    if not sentences:
        return DimensionAssessment(
            value=ClosureMode.UNKNOWN.value, confidence=ConfidenceLevel.LOW,
            evidence="For lite text.", evidence_status=DIMENSION_EVIDENCE_STATUS["closure_mode"],
        )
    tail = " ".join(sentences[-2:])
    if sentences[-1].rstrip().endswith("?"):
        return DimensionAssessment(
            value=ClosureMode.OPEN_QUESTION.value, confidence=ConfidenceLevel.HIGH,
            evidence="Sista meningen slutar med frageteck.", evidence_status=DIMENSION_EVIDENCE_STATUS["closure_mode"],
        )
    tail_words = _words(tail)
    imperative_hits = tail_words & _IMPERATIVE_VERBS
    if imperative_hits:
        return DimensionAssessment(
            value=ClosureMode.ACTION.value, confidence=ConfidenceLevel.MEDIUM,
            evidence=f"Imperativ nara slutet: {sorted(imperative_hits)}.", evidence_status=DIMENSION_EVIDENCE_STATUS["closure_mode"],
        )
    if "konsekvens" in _normalize(tail):
        return DimensionAssessment(
            value=ClosureMode.CONSEQUENCE.value, confidence=ConfidenceLevel.MEDIUM,
            evidence="Ordet 'konsekvens' nara slutet.", evidence_status=DIMENSION_EVIDENCE_STATUS["closure_mode"],
        )
    if sentences[-1].strip().lower().startswith("men") and len(sentences[-1].split()) <= 6:
        return DimensionAssessment(
            value=ClosureMode.UNRESOLVED_TENSION.value, confidence=ConfidenceLevel.LOW,
            evidence="Sista, korta meningen inleds med kontrastordet 'men' -- olost spanning.",
            evidence_status=DIMENSION_EVIDENCE_STATUS["closure_mode"],
        )
    return DimensionAssessment(
        value=ClosureMode.STILL_STATEMENT.value, confidence=ConfidenceLevel.LOW,
        evidence="Ingen fraga, imperativ, konsekvens- eller spanningsmarkor nara slutet -- stilla paststaende antas som standard.",
        evidence_status=DIMENSION_EVIDENCE_STATUS["closure_mode"],
    )


_MIN_SENTENCES_FOR_MOVEMENT = 3
"""order section 10 (V1C Correction): a text with fewer sentences than this
has no room for anything between an opening and a closing -- it cannot
support a genuine movement observation, regardless of FULL/PARTIAL text
completeness (order section 11: these are two different boundaries)."""

_MAX_MOVEMENT_STEPS = 5
"""order section 6, 9: three to five observed movements is the target
granularity -- small and bounded, not an attempt at full narrative analysis."""


def _segment_sentences(sentences: list[str], max_steps: int = _MAX_MOVEMENT_STEPS) -> list[list[str]]:
    """Splits sentences into up to `max_steps` contiguous, roughly equal
    groups -- e.g. 4 sentences -> 4 one-sentence segments, 12 sentences ->
    5 groups of ~2-3. Guarantees at least one segment strictly between the
    first and last for any text with >= 3 sentences (order section 9)."""

    n = len(sentences)
    if n == 0:
        return []
    k = min(max_steps, n)
    return [sentences[(i * n) // k : ((i + 1) * n) // k] for i in range(k)]


def _classify_movement_segment(window_text: str) -> tuple[MovementStage, ConfidenceLevel, str]:
    """order section 6-7: the same small, keyword-explainable style already
    used for entry/closure/pressure, but applied to EVERY segment of the
    text (order section 9), not just the first/last window -- so the middle
    of the text can now actually change the observed sequence."""

    lowered = _normalize(window_text)
    words = set(lowered.split())

    if "?" in window_text:
        return MovementStage.QUESTION, ConfidenceLevel.HIGH, "Segmentet innehaller ett frageteck."
    if "men" in words:
        return MovementStage.TENSION, ConfidenceLevel.MEDIUM, "Segmentet innehaller kontrastordet 'men'."
    imperative_hits = words & _IMPERATIVE_VERBS
    if len(imperative_hits) >= 2:
        return MovementStage.DIRECTION, ConfidenceLevel.MEDIUM, f"Flera imperativ i segmentet: {sorted(imperative_hits)}."
    if "konsekvens" in lowered:
        return MovementStage.CONSEQUENCE, ConfidenceLevel.MEDIUM, "Ordet 'konsekvens' i segmentet."
    if words & _CONCRETE_EVENT_VERBS or ((words & _QUANTITY_WORDS) and (words & _ROLE_WORDS)):
        return MovementStage.CONCRETE_SITUATION, ConfidenceLevel.MEDIUM, "Konkret handelse-/rollmarkor i segmentet."
    if any(marker in lowered for marker in _REFRAMING_MARKERS):
        return MovementStage.REFRAMING, ConfidenceLevel.MEDIUM, "Omramningsmarkor (t.ex. 'egentligen'/'i grunden') i segmentet."
    if any(marker in lowered for marker in _DISTINCTION_MARKERS):
        return MovementStage.DISTINCTION, ConfidenceLevel.MEDIUM, "Distinktionsmarkor (t.ex. 'skiljer sig fran') i segmentet."
    if words & _INVENTORY_WORDS:
        return MovementStage.SYMPTOM_INVENTORY, ConfidenceLevel.LOW, f"Uppräkningsord i segmentet: {sorted(words & _INVENTORY_WORDS)}."
    if words & _PRINCIPLE_WORDS:
        return MovementStage.PRINCIPLE, ConfidenceLevel.MEDIUM, f"Princip-/rollord i segmentet: {sorted(words & _PRINCIPLE_WORDS)}."
    return MovementStage.OBSERVATION, ConfidenceLevel.LOW, "Ingen stark rorelsesignal i segmentet -- neutral observation antagen, lag confidence."


def _assess_structural_movement(text: str) -> StructuralMovementAssessment:
    """order section 6, 8, 9, 10 (V1C Correction, the central fix): the
    PRIMARY structural-truth signal. Segments the WHOLE text (not just the
    first-4/last-2-sentence windows entry_mode/closure_mode use) and
    classifies each segment independently, so genuinely different
    mid-text construction is now observable and comparable -- see
    `comparison.py::compare_structural_movements()`."""

    sentences = _sentences(text)
    if len(sentences) < _MIN_SENTENCES_FOR_MOVEMENT:
        return StructuralMovementAssessment(
            steps=[], sufficient_evidence=False, evidence_status=DIMENSION_EVIDENCE_STATUS["structural_movement"],
        )

    segments = _segment_sentences(sentences)
    steps: list[MovementStep] = []
    for segment in segments:
        stage, confidence, evidence = _classify_movement_segment(" ".join(segment))
        if steps and steps[-1].stage == stage:
            continue  # order section 7: collapse consecutive duplicates, no padding for its own sake
        steps.append(MovementStep(stage=stage, confidence=confidence, evidence=evidence))

    return StructuralMovementAssessment(
        steps=steps, sufficient_evidence=True, evidence_status=DIMENSION_EVIDENCE_STATUS["structural_movement"],
    )


_ARC_FROM_FIRST_MOVEMENT = {
    MovementStage.CONCRETE_SITUATION: StructuralArc.SCENE_TO_INSIGHT,
    MovementStage.PRINCIPLE: StructuralArc.FRAMEWORK_TO_DIRECTION,
    MovementStage.CONSEQUENCE: StructuralArc.ESCALATION_TO_CONSEQUENCE,
    MovementStage.CLAIM: StructuralArc.CLAIM_TO_EVIDENCE,
    MovementStage.QUESTION: StructuralArc.DILEMMA_TO_OPEN_END,
}
"""order section 8 (V1C Correction): `structural_arc` is now a SECONDARY,
small summary label derived from the observed movement sequence's
endpoints -- never the primary source of structural truth. The primary
comparison (`comparison.py::compare_structural_movements()`) uses the full
`StructuralMovementAssessment.steps` sequence, not this label."""


def _assess_structural_arc(movement: StructuralMovementAssessment) -> DimensionAssessment:
    if not movement.sufficient_evidence or not movement.steps:
        return DimensionAssessment(
            value=StructuralArc.UNKNOWN.value, confidence=ConfidenceLevel.LOW,
            evidence="Otillrackligt observerad rorelsesekvens (kravs minst 3 meningar) -- kan inte harleda en sekundar arc-etikett.",
            evidence_status=DIMENSION_EVIDENCE_STATUS["structural_arc"],
        )

    step_labels = " -> ".join(s.stage.value for s in movement.steps)
    last_stage = movement.steps[-1].stage
    if last_stage == MovementStage.QUESTION:
        return DimensionAssessment(
            value=StructuralArc.DILEMMA_TO_OPEN_END.value, confidence=ConfidenceLevel.MEDIUM,
            evidence=f"Sekundar etikett harledd fran observerad rorelsesekvens ({step_labels}) -- avslutas med en oppen fraga.",
            evidence_status=DIMENSION_EVIDENCE_STATUS["structural_arc"],
        )

    first_step = movement.steps[0]
    arc = _ARC_FROM_FIRST_MOVEMENT.get(first_step.stage, StructuralArc.CLAIM_TO_EVIDENCE)
    confidence = ConfidenceLevel.LOW if first_step.confidence == ConfidenceLevel.LOW else ConfidenceLevel.MEDIUM
    return DimensionAssessment(
        value=arc.value, confidence=confidence,
        evidence=f"Sekundar etikett harledd fran observerad rorelsesekvens: {step_labels}.",
        evidence_status=DIMENSION_EVIDENCE_STATUS["structural_arc"],
    )


_LOCAL_FUNCTION_CONNECTORS = ("till slut", "till sist", "sedan", "därför", "efteråt", "men")
"""V1C Blocker 3 (feasibility assessment section 2's minimal form: 'observerad
situation eller handling -> funktionell forandring -> observerbar foljd'):
small, generic Swedish discourse connectives marking a shift from an opening
situation to its consequence -- not Challenge-specific, the same class of
generic connective already used elsewhere in this file (`men` for
rhetorical_pressure, `_REFRAMING_MARKERS`, `_DISTINCTION_MARKERS`)."""

_CAPABILITY_CHANGE_STEMS = (
    "tystnad", "tyst", "röst", "våga",
    "omdöm", "tänk", "instruktion", "bedöm", "ansvar", "mandat", "skuld", "förklar", "kritik",
    "beroend", "ensam",
    "initiativ", "kapacitet", "kapabel",
    "signal", "varning",
    "straff",
    "slutad", "sluta", "upphör", "vänta",
)
"""V1C Blocker 3: a small, general vocabulary of Swedish words about a change
in voice, judgment/accountability, dependency, initiative, information flow,
social consequence for dissent, or cessation of an activity -- derived from
the feasibility assessment's own named concepts (section 2: 'vad situationen
gor i lasarens forstaelse och vilken mojlighet som darmed minskar, oppnas
eller forskjuts'), not from any single challenge scenario text. Prefix-matched to absorb
ordinary Swedish inflection (tystnad/tystnaden/tystnadens). This is NOT a
canonical taxonomy -- it is only ever used to find literal, source-quotable
words in the analyzed text; any grouping of these words into related concepts
for comparison purposes lives in `comparison.py`, never persisted as a label
on `LocalEditorialFunctionAssessment` (order section 9: 'kallsparad fore
kategoriserad')."""


def _capability_change_words(words: set[str]) -> list[str]:
    return sorted(w for w in words if any(w.startswith(stem) for stem in _CAPABILITY_CHANGE_STEMS))


def _assess_local_editorial_function(text: str) -> LocalEditorialFunctionAssessment:
    """V1C Blocker 3, locked scope per
    V1C_LOCAL_EDITORIAL_FUNCTION_FEASIBILITY_ASSESSMENT.md (Architecture
    Verdict B. PARTIALLY VIABLE): extracts the smallest defensible local
    relation -- a situation/handling span and a consequence span, split at
    the earliest generic connector (or, absent one, at the first sentence
    boundary) -- and only asserts `sufficient_evidence=True` when the
    consequence span itself contains a source-quotable capability-change
    word. No inference, no filling gaps with what the text 'probably'
    means (order section 8): absence of a connector, absence of a second
    part, or absence of a capability-change word in the consequence span
    all fall through to `sufficient_evidence=False`, never a guess."""

    lowered = _normalize(text)
    connector_idx = None
    for connector in _LOCAL_FUNCTION_CONNECTORS:
        idx = lowered.find(connector)
        if idx != -1 and (connector_idx is None or idx < connector_idx):
            connector_idx = idx

    if connector_idx is not None:
        situation = text[:connector_idx].strip()
        consequence = text[connector_idx:].strip()
    else:
        sentences = _sentences(text)
        if len(sentences) < 2:
            return LocalEditorialFunctionAssessment(
                sufficient_evidence=False, confidence=ConfidenceLevel.LOW,
                evidence="Ingen konnektor och for lite text (under tva meningar) for att urskilja en situation- och en foljd-del.",
            )
        situation, consequence = sentences[0], " ".join(sentences[1:])

    if not situation or not consequence:
        return LocalEditorialFunctionAssessment(
            sufficient_evidence=False, confidence=ConfidenceLevel.LOW,
            evidence="Situation- eller foljd-delen ar tom efter uppdelning -- ingen relation kan kallsparas.",
        )

    hits = _capability_change_words(_words(consequence))
    if not hits:
        return LocalEditorialFunctionAssessment(
            sufficient_evidence=False, confidence=ConfidenceLevel.LOW,
            situation_span=situation, consequence_span=consequence,
            evidence="Situation- och foljd-delar identifierade, men foljd-delen innehaller inget kallsparbart ord om formaga, rost, ansvar, beroende eller informationsflode -- INSUFFICIENT_EVIDENCE, ingen gissning.",
        )

    return LocalEditorialFunctionAssessment(
        sufficient_evidence=True, confidence=ConfidenceLevel.MEDIUM,
        situation_span=situation, consequence_span=consequence, capability_change_words=hits,
        evidence=f"Situation ({situation!r}) foljs av en observerbar konsekvens ({consequence!r}) som innehaller kallsparbara ord: {hits}.",
    )


_WARM_WORDS = {"manniskor", "manniska", "hjalp", "tillit", "stod", "manskligt"}
_COOL_WORDS = {"system", "systemet", "verksamheten", "organisationen", "modellen", "process"}


def _assess_disclosure_pace(text: str) -> DimensionAssessment:
    sentence_count = len(_sentences(text))
    if sentence_count >= 6:
        value, confidence, evidence = DisclosurePace.GRADUAL.value, ConfidenceLevel.LOW, f"Manga korta meningar ({sentence_count}) antyder gradvis uppbyggnad. Hypotesniva -- lag confidence per design."
    elif sentence_count <= 2:
        value, confidence, evidence = DisclosurePace.IMMEDIATE.value, ConfidenceLevel.LOW, f"Fa meningar ({sentence_count}) antyder ett omedelbart paststaende. Hypotesniva -- lag confidence per design."
    else:
        value, confidence, evidence = DisclosurePace.UNKNOWN.value, ConfidenceLevel.LOW, "Otillrackligt tydligt signal for gradvis kontra omedelbar upplysning."
    return DimensionAssessment(value=value, confidence=confidence, evidence=evidence, evidence_status=DIMENSION_EVIDENCE_STATUS["disclosure_pace"])


def _assess_emotional_temperature(text: str) -> DimensionAssessment:
    words = _words(text)
    if words & _WARM_WORDS:
        return DimensionAssessment(
            value=EmotionalTemperature.WARM.value, confidence=ConfidenceLevel.LOW,
            evidence=f"Manskligt/varmt ordval: {sorted(words & _WARM_WORDS)}. Hypotesniva -- lag confidence per design.",
            evidence_status=DIMENSION_EVIDENCE_STATUS["emotional_temperature"],
        )
    if words & _COOL_WORDS:
        return DimensionAssessment(
            value=EmotionalTemperature.COOL.value, confidence=ConfidenceLevel.LOW,
            evidence=f"Systeminriktat/svalt ordval: {sorted(words & _COOL_WORDS)}. Hypotesniva -- lag confidence per design.",
            evidence_status=DIMENSION_EVIDENCE_STATUS["emotional_temperature"],
        )
    return DimensionAssessment(
        value=EmotionalTemperature.UNKNOWN.value, confidence=ConfidenceLevel.LOW,
        evidence="Ingen tydlig varm/sval markor hittad. Hypotesniva.",
        evidence_status=DIMENSION_EVIDENCE_STATUS["emotional_temperature"],
    )


def _new_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


def build_variation_profile(
    text: str,
    source_id: str,
    source_kind: SourceKind,
    actor_id: str = "v1c_rule_based_profiler",
    include_hypothesis_dimensions: bool = True,
) -> VariationProfile:
    """Builds a VariationProfile from raw text. Callers are responsible for
    only ever passing text that is safe to analyze structurally in full --
    see `build_variation_profile_for_memory_record()` for the one enforced
    FULL/PARTIAL gate (order section 10)."""

    entry = _assess_entry_mode(text)
    lens = _assess_lens(text)
    distance = _assess_narrative_distance(text)
    pressure = _assess_rhetorical_pressure(text)
    closure = _assess_closure_mode(text)
    movement = _assess_structural_movement(text)
    arc = _assess_structural_arc(movement)

    disclosure_pace = _assess_disclosure_pace(text) if include_hypothesis_dimensions else None
    emotional_temperature = _assess_emotional_temperature(text) if include_hypothesis_dimensions else None
    local_editorial_function = _assess_local_editorial_function(text)

    return VariationProfile(
        profile_id=_new_id("VPROF-V1C"),
        source_id=source_id,
        source_kind=source_kind,
        entry_mode=entry,
        lens=lens,
        narrative_distance=distance,
        structural_arc=arc,
        structural_movement=movement,
        rhetorical_pressure=pressure,
        closure_mode=closure,
        disclosure_pace=disclosure_pace,
        emotional_temperature=emotional_temperature,
        sentence_count=len(_sentences(text)),
        word_count=len(_words(text)),
        local_editorial_function=local_editorial_function,
        analysis_logic_version=ANALYSIS_LOGIC_VERSION,
        provenance=Provenance(
            created_by=Actor.AI_SYSTEM,
            actor_id=actor_id,
            created_at=datetime.now(timezone.utc),
            certainty=EvidenceCertainty.ANALYTICAL_PROPOSAL,
            method="v1c_rule_based_variation_profiling",
            analysis_logic_version=ANALYSIS_LOGIC_VERSION,
            supporting_source_ids=[],
        ),
    )


class PartialTextVariationError(Exception):
    """Raised when a caller attempts to build a full structural VariationProfile
    from a PARTIAL Editorial Memory record (order section 10). Structurally
    enforced, not just documented."""


def build_variation_profile_for_memory_record(record: EditorialMemoryRecord) -> VariationProfile:
    if record.source_facts.text_completeness != TextCompleteness.FULL:
        raise PartialTextVariationError(
            f"{record.content_id}: text_completeness is "
            f"{record.source_facts.text_completeness.value!r}, not FULL -- refusing to build a "
            "structural VariationProfile from partial text (order section 10)."
        )
    return build_variation_profile(
        text=record.source_facts.original_text,
        source_id=record.content_id,
        source_kind=SourceKind.EDITORIAL_MEMORY_RECORD,
    )
