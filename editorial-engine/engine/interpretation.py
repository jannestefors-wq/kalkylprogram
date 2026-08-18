"""
Step 1-2: Raw Idea -> Interpretation (order sections 4-6).

`RawInput` is never mutated (Beslut 5, enforced by `RawInput` being
`frozen=True` in schema/raw_input.py already -- this module simply never
writes to it). The AI-produced `IdeaInterpretation` is a separate object,
carrying `Provenance(created_by=Actor.AI_SYSTEM, analysis_logic_version=...)`
as Canonical Foundation V1 already requires (hard-validated on `Provenance`
itself, see schema/provenance.py).
"""

from __future__ import annotations

from datetime import datetime, timezone

from schema import Idea, IdeaInterpretation, Provenance, RawInput
from schema.enums import Actor, EvidenceCertainty, IdeaStatus, InputType

from .models import AnalysisLayer, InterpretationDraft, LabeledStatement
from .provider import AnalysisProvider

ANALYSIS_LOGIC_VERSION = "interpretation-v1a-1.0"
"""order section 6: 'Infor en explicit version for V1A:s analyslogik.' Reuses the existing
Provenance.analysis_logic_version field -- no parallel versioning system created."""


def build_interpretation_draft(raw_text: str, provider: AnalysisProvider) -> InterpretationDraft:
    """May raise InsufficientContextError -- callers (pipeline.py) turn that into
    PipelineOutcome.MORE_CONTEXT_REQUIRED. This function itself never guesses around it."""
    layers = provider.interpret(raw_text, ANALYSIS_LOGIC_VERSION)
    return InterpretationDraft(analysis_logic_version=ANALYSIS_LOGIC_VERSION, layers=layers)


def render_idea_interpretation(draft: InterpretationDraft, actor_id: str = "v1a_rule_based_provider") -> IdeaInterpretation:
    """Condense the layered draft into the canonical `IdeaInterpretation` shape. Every
    field stays hedged where it came from an INTERPRETATION/INFERENCE layer; nothing here
    upgrades a hypothesis into a fact."""

    observations = draft.texts_for(AnalysisLayer.OBSERVATION)
    interpretations = draft.texts_for(AnalysisLayer.INTERPRETATION)
    inferences = draft.texts_for(AnalysisLayer.INFERENCE)

    observed_situation = " ".join(observations) if observations else None
    power_dimension = next((t for t in interpretations if "makt" in t.lower() or "lyssnande" in t.lower()), None)
    hidden_conflict = next((t for t in interpretations if "definiera" in t.lower() or "verklighet" in t.lower()), None)
    relationship_dimension = next((t for t in interpretations if "relationell" in t.lower() or "spanning" in t.lower()), None)
    possible_consequence = next((t for t in inferences if "konsekvens" in t.lower()), None)
    system_dimension = next((t for t in inferences if "monstret" in t.lower() or "over tid" in t.lower()), None)

    visible_problem = None
    if observed_situation and "avbrott" in observed_situation.lower():
        visible_problem = "Ett beskrivet avbrott i kommunikationen (observerat, inte tolkat)."
    elif observed_situation:
        visible_problem = "Den konkret beskrivna handelsen (observerad, inte tolkad)."

    return IdeaInterpretation(
        observed_situation=observed_situation,
        human_subject=None,  # V1A does not assert who is centrally affected -- see docs/V1A_DOES_NOT_DO.md
        human_experience=None,
        visible_problem=visible_problem,
        hidden_conflict=hidden_conflict,
        possible_root_causes=[t for t in inferences if t != possible_consequence],
        power_dimension=power_dimension,
        relationship_dimension=relationship_dimension,
        system_dimension=system_dimension,
        possible_consequence=possible_consequence,
        provenance=Provenance(
            created_by=Actor.AI_SYSTEM,
            actor_id=actor_id,
            created_at=datetime.now(timezone.utc),
            certainty=EvidenceCertainty.ANALYTICAL_PROPOSAL,
            method="v1a_rule_based_interpretation",
            analysis_logic_version=draft.analysis_logic_version,
            supporting_source_ids=[],
        ),
    )


def build_raw_input(raw_input_id: str, text: str, language: str = "sv") -> RawInput:
    """Thin, honest wrapper -- exists so pipeline.py has one obvious place to construct the
    immutable RawInput. text is stored verbatim; nothing here transforms it."""
    return RawInput(
        raw_input_id=raw_input_id,
        captured_at=datetime.now(timezone.utc),
        text=text,
        input_type=InputType.OBSERVATION,
        language=language,
    )


def build_idea(idea_id: str, raw_input: RawInput, interpretation: IdeaInterpretation) -> Idea:
    return Idea(
        idea_id=idea_id,
        created_at=datetime.now(timezone.utc),
        raw_input_id=raw_input.raw_input_id,
        input_type=raw_input.input_type,
        language=raw_input.language,
        interpretation=interpretation,
        status=IdeaStatus.ANALYZED,
    )
