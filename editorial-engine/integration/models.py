"""
Editorial Engine V1 Integration models (EDITORIAL_ENGINE_V1_INTEGRATION_CONTRACT.md
section 5, 6). All models here are INTEGRATION-LEVEL and PROTOTYPE-DERIVED --
never canonical data, never a new Ground Truth, never persisted by default
(see `pipeline.py::run_evaluation`). They only re-express V1A/V1B/V1C's own
already-computed output; no new editorial judgment is made here.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field

MEMORY_LIMITATION_NOTE_FIELD = "memory_limitation_note"


class HumanDecisionPoint(BaseModel):
    """Contract section 6: 'The user must be able to see why the system is
    uncertain. Human Authority is a working decision point, not an
    exception handler.' No `schema.HumanDecision` is ever constructed here
    -- that model hard-requires `decided_by_actor == Actor.HUMAN` (Canonical
    Foundation V1), so a decision point only ever appears here as PENDING
    until a real caller supplies a real `schema.HumanDecision` object of
    their own (see `pipeline.run_editorial_engine_v1`'s `human_decision`
    parameter). Evaluation Mode never fabricates one (contract section 7's
    forbidden list: 'Human Authority is bypassed')."""

    model_config = {"extra": "forbid"}

    stage: str = Field(description="'after_v1a_v1b' or 'after_v1c'.")
    status: str = Field(description="'pending_human_input' or 'decided'.")
    available_actions: list[str] = Field(default_factory=list)
    system_recommendation: Optional[str] = None
    rationale: str
    decision_reference: Optional[str] = Field(
        default=None, description="schema.HumanDecision.decision_id, only set once status == 'decided'."
    )


class EngineSeesFields(BaseModel):
    """Contract 5.A: 'What the engine sees.' Every field is `None` when the
    available material does not support it -- never filled with a guess
    (contract 5.A's own 'UNKNOWN where the available material does not
    support a field')."""

    model_config = {"extra": "forbid"}

    input_reference: str
    language: str
    input_sufficient_for_interpretation: bool
    thesis_family: Optional[str] = None
    territory: Optional[str] = None
    series: Optional[str] = None
    topic: Optional[str] = None
    angle_core: Optional[str] = None
    observed_situation: Optional[str] = None
    lens: Optional[str] = None
    narrative_distance: Optional[str] = None
    entry_function: Optional[str] = None
    closure_function: Optional[str] = None
    structural_movement_sufficient: Optional[bool] = None
    structural_movement_sequence: list[str] = Field(default_factory=list)
    local_editorial_function_sufficient: Optional[bool] = None
    local_editorial_function_situation: Optional[str] = None
    local_editorial_function_consequence: Optional[str] = None


class RememberedRecord(BaseModel):
    """Contract 5.B, one row of 'What the engine remembers.'"""

    model_config = {"extra": "forbid"}

    content_id: str
    source: str
    text_completeness: str
    publication_status: str
    why_relevant: str
    repetition_signal_strength: Optional[str] = None


class EngineRemembersFields(BaseModel):
    model_config = {"extra": "forbid"}

    records: list[RememberedRecord] = Field(default_factory=list)
    corpus_size: int
    fulltext_corpus_size: int
    memory_boundary_note: str
    no_match: bool


class EngineAssessesFields(BaseModel):
    """Contract 5.C: uses the contract's own requested display vocabulary
    (`LEGITIMATE_VARIATION`, `FALSE_VARIATION_HIGH_RISK`, `PARTIAL_SIMILARITY`,
    `INSUFFICIENT_EVIDENCE`, `AMBIGUOUS_HUMAN_DECISION`) -- a read-only
    LABEL computed from V1C's own already-computed, unmodified fields
    (`FalseVariationAssessment`, `VariationDistanceCategory`). This function
    never re-decides anything V1C decided; it only renames the existing
    result for display (`pipeline.py::_label_v1c_assessment`)."""

    model_config = {"extra": "forbid"}

    label: Optional[str] = None
    rationale: Optional[str] = None
    sufficient_evidence: Optional[bool] = None


class EngineCouldChangeFields(BaseModel):
    """Contract 5.D: directions only, never generated prose."""

    model_config = {"extra": "forbid"}

    directions: list[str] = Field(default_factory=list)


class FinalEditorialAssessment(BaseModel):
    """Contract section 5: 'The integrated output must be understandable
    without exposing internal implementation details.' Sections A-D plus
    both Human Authority decision points, plus a provenance trail back to
    each component's own full result object (never duplicated data --
    callers needing the raw V1A/V1B/V1C trace read `sees`/`remembers`/
    `assesses`/`could_change` here, or the original result objects the
    pipeline also returns alongside this)."""

    model_config = {"extra": "forbid"}

    input_id: str
    sees: EngineSeesFields
    remembers: EngineRemembersFields
    assesses: EngineAssessesFields
    could_change: EngineCouldChangeFields
    human_decision_after_v1a_v1b: HumanDecisionPoint
    human_decision_after_v1c: Optional[HumanDecisionPoint] = None
    v1c_ran: bool = False
    provenance_note: str = (
        "V1A interpretation is runtime analysis, not a source fact. V1B memory match is bounded to the "
        "ingested corpus, never proof of novelty when absent. V1C output is prototype-derived and "
        "non-canonical. No field here is Ground Truth or permanent memory."
    )
