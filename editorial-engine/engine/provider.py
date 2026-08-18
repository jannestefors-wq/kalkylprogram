"""
AnalysisProvider (order section 22): the one seam where a real LLM could
later be plugged in for interpretation or angle-text generation. Domain
logic (`interpretation.py`, `angles.py`, ...) depends only on this
`Protocol`, never on a specific vendor/model.

`RuleBasedAnalysisProvider` is the actual V1A implementation: small,
transparent, deterministic, keyword-based heuristics -- "regelbaserad
bedomning framfor falsk matematisk precision" (order section 13). It
requires no network access and no API key, so the full test suite runs
deterministically offline (order section 22).
"""

from __future__ import annotations

from typing import Protocol

from .models import AnalysisLayer, InsufficientContextError, LabeledStatement

MIN_WORDS_FOR_INTERPRETATION = 6

REPETITION_MARKERS = {"ganger", "gånger", "upprepade", "upprepat", "igen", "alltid", "varje", "flera"}
QUANTITY_WORDS = {"en", "ett", "tva", "två", "tre", "fyra", "fem"}
ROLE_WORDS = {
    "chef", "chefen", "medarbetare", "medarbetaren", "kollega", "kollegan",
    "ledare", "ledaren", "team", "teamet", "grupp", "gruppen", "person", "personen",
}
INTERRUPTION_WORDS = {"avbrot", "avbröt", "avbryta", "avbrott"}


def _normalize(text: str) -> list[str]:
    cleaned = "".join(ch.lower() if ch.isalnum() or ch.isspace() else " " for ch in text)
    return [w for w in cleaned.split() if w]


class AnalysisProvider(Protocol):
    """The seam. Anything on the other side of this interface may one day be an LLM call;
    nothing on this side of it may assume that."""

    def is_sufficient(self, raw_text: str) -> bool:
        ...

    def interpret(self, raw_text: str, analysis_logic_version: str) -> list[LabeledStatement]:
        """Return observation/interpretation/inference layers. Raise
        InsufficientContextError if `is_sufficient` would be False -- callers should
        check `is_sufficient` first, but this must not silently guess either."""
        ...

    def propose_angle_seeds(self, interpretation_texts: dict[str, str]) -> list[dict[str, str]]:
        """Return up to 3 angle seeds, each a dict with keys 'title', 'core',
        'why_relevant', 'differentiation', and 'evidence_keys' (comma-separated
        interpretation_texts keys this seed was actually built from). May legitimately
        return fewer than 3 if the interpretation doesn't support that many distinct
        seeds -- never pads with filler."""
        ...


class RuleBasedAnalysisProvider:
    """The real V1A implementation. Deterministic, transparent, keyword-based. See module
    docstring. This is not a mock standing in for a 'real' provider -- for V1A, this *is*
    the provider; a future LLM-backed provider would implement the same Protocol."""

    def is_sufficient(self, raw_text: str) -> bool:
        words = _normalize(raw_text)
        if len(words) < MIN_WORDS_FOR_INTERPRETATION:
            return False
        has_concrete_marker = bool(
            (REPETITION_MARKERS | QUANTITY_WORDS) & set(words)
        )
        role_word_count = len(ROLE_WORDS & set(words))
        return has_concrete_marker or role_word_count >= 2

    def interpret(self, raw_text: str, analysis_logic_version: str) -> list[LabeledStatement]:
        if not self.is_sufficient(raw_text):
            raise InsufficientContextError(
                f"Raw input too thin for responsible interpretation under {analysis_logic_version}: {raw_text!r}"
            )

        words = set(_normalize(raw_text))
        layers: list[LabeledStatement] = []

        detected_roles = sorted(ROLE_WORDS & words)
        detected_repetition = bool(REPETITION_MARKERS & words) or bool(QUANTITY_WORDS & words)
        detected_interruption = bool(INTERRUPTION_WORDS & words)

        # --- OBSERVATION: literal, no judgment ---
        observation_bits = []
        if detected_roles:
            observation_bits.append(f"namnger roll(er): {', '.join(detected_roles)}")
        if detected_repetition:
            observation_bits.append("beskriver en upprepad handling")
        if detected_interruption:
            observation_bits.append("beskriver ett avbrott i kommunikation")
        observation_text = (
            "Raw input " + (", ".join(observation_bits) if observation_bits else "beskriver en enskild handelse")
            + "."
        )
        layers.append(LabeledStatement(layer=AnalysisLayer.OBSERVATION, text=observation_text))

        # --- INTERPRETATION: hedged readings, never settled fact ---
        # Parameterized by the actually-detected roles so two different raw inputs of the
        # same "shape" still produce distinguishable text -- not a fixed template.
        roles_phrase = " och ".join(detected_roles) if detected_roles else "de inblandade"
        if detected_interruption or detected_repetition:
            layers.append(
                LabeledStatement(
                    layer=AnalysisLayer.INTERPRETATION,
                    text=f"Mojlig makt- eller lyssnandedimension mellan {roles_phrase}. Avsikten bakom handlingen ar okand.",
                )
            )
            layers.append(
                LabeledStatement(
                    layer=AnalysisLayer.INTERPRETATION,
                    text=f"Mojlig fraga om vem av {roles_phrase} som far definiera situationens verklighet. Detta ar en hypotes, inte ett faststallt faktum.",
                )
            )
        if detected_roles and len(detected_roles) >= 2:
            layers.append(
                LabeledStatement(
                    layer=AnalysisLayer.INTERPRETATION,
                    text=f"Mojlig relationell spanning mellan {detected_roles[0]} och {detected_roles[-1]}. Ej faststallt.",
                )
            )

        # --- INFERENCE: further removed, explicitly hypothesis, never fact ---
        if detected_repetition:
            layers.append(
                LabeledStatement(
                    layer=AnalysisLayer.INFERENCE,
                    text="Om monstret upprepas over tid kan det (hypotes, ej faststallt) paverka viljan att tala fritt i rummet.",
                )
            )
        affected_party = detected_roles[-1] if detected_roles else "den som paverkas"
        layers.append(
            LabeledStatement(
                layer=AnalysisLayer.INFERENCE,
                text=f"Mojlig konsekvens (hypotes): {affected_party} kan over tid lagga fram farre ideer eller synpunkter. Inte verifierat.",
            )
        )

        return layers

    def propose_angle_seeds(self, interpretation_texts: dict[str, str]) -> list[dict[str, str]]:
        seeds: list[dict[str, str]] = []

        visible = interpretation_texts.get("visible_problem")
        power = interpretation_texts.get("power_dimension")
        consequence = interpretation_texts.get("possible_consequence")

        if visible and power:
            seeds.append(
                {
                    "title": "Det synliga och det underliggande",
                    "core": f"Det synliga problemet ar: {visible} Den djupare fragan galler {power.rstrip('.').lower()}",
                    "why_relevant": "Skiljer det observerbara fran den mojliga maktdimensionen utan att pasta avsikt.",
                    "differentiation": "Fokuserar pa sjalva definitionsratten i rummet, inte bara pa handelsen.",
                    "evidence_keys": "visible_problem,power_dimension",
                }
            )

        if consequence:
            seeds.append(
                {
                    "title": "Monster over tid",
                    "core": f"Enskilda handelser kan verka sma. Den redaktionella riktningen ar vad som byggs upp over tid: {consequence.rstrip('.').lower()}",
                    "why_relevant": "Flyttar blicken fran den enskilda handelsen till det upprepade monstret.",
                    "differentiation": "Betonar tidsdimensionen (uprepning) snarare an den enskilda incidenten.",
                    "evidence_keys": "possible_consequence",
                }
            )

        if power:
            seeds.append(
                {
                    "title": "Avsikt kontra konsekvens",
                    "core": f"Undersok skillnaden mellan avsikt och konsekvens i detta specifika fall: {power.rstrip('.').lower()} Konsekvensen kan bli densamma oavsett avsikt.",
                    "why_relevant": "Haller isar det vi vet (konsekvens, observerbart) fran det vi inte vet (avsikt, ej observerbart).",
                    "differentiation": "Explicit fokus pa epistemisk gräns -- vad kan vi faktiskt veta.",
                    "evidence_keys": "power_dimension",
                }
            )

        return seeds[:3]
