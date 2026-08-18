"""
V1A analysis-output models (order section 12: "Analysis output ar inte
canonical data").

Everything in this module is ENGINE OUTPUT, not canonical truth. None of it
is exported from `schema/__init__.py`, none of it is written into
`canonical_data/`, and none of it changes Canonical Foundation V1. Where an
existing canonical model already fits (`Idea`, `IdeaInterpretation`,
`Angle`, `Provenance`, `HumanDecision`), it is reused directly rather than
duplicated -- see each field's docstring below for which canonical model it
wraps or references by id.

Confidence and status vocabularies here (`ConfidenceLevel`,
`RepetitionRiskLevel`) are intentionally NOT the same enums as canonical
`EvidenceCertainty`/`VoicePrincipleStatus` -- conflating "how sure is this
one-off analysis run" with "how editorially confirmed is this canonical
fact" would be exactly the mixing Beslut 23/Canonical Foundation V1
forbids (order section 8: "confidence ska inte bli sanning... hall
canonical status och analysis confidence separata").
"""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from schema import Angle, Idea, RawInput


class InsufficientContextError(Exception):
    """Raised by an AnalysisProvider when raw input is too thin to interpret
    responsibly. Caught by the pipeline and turned into MORE_CONTEXT_REQUIRED
    (order section 17) -- never silently forced into a full interpretation."""


# ---------------------------------------------------------------------------
# Interpretation: observation -> interpretation -> inference (order section 5)
# ---------------------------------------------------------------------------


class AnalysisLayer(str, Enum):
    OBSERVATION = "observation"      # restates only what the raw input literally says
    INTERPRETATION = "interpretation"  # a hedged reading of what this might mean
    INFERENCE = "inference"          # a further-removed hypothesis; never stated as settled fact


class LabeledStatement(BaseModel):
    model_config = {"extra": "forbid"}

    layer: AnalysisLayer
    text: str


class InterpretationDraft(BaseModel):
    """The engine-only working record behind a canonical `IdeaInterpretation`.
    Keeps the observation/interpretation/inference layers separately
    inspectable BEFORE they are condensed into the canonical model's fields,
    so the distinction required by order section 5 is data, not just prose
    style. `rendered` is the canonical `schema.IdeaInterpretation` produced
    from these layers -- that object, not this draft, is what an `Idea`
    actually stores."""

    model_config = {"extra": "forbid"}

    analysis_logic_version: str
    layers: list[LabeledStatement]

    def texts_for(self, layer: AnalysisLayer) -> list[str]:
        return [s.text for s in self.layers if s.layer == layer]


# ---------------------------------------------------------------------------
# Classification (order section 7-8)
# ---------------------------------------------------------------------------


class ConfidenceLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class CanonicalMatchKind(str, Enum):
    THESIS_FAMILY = "thesis_family"
    TERRITORY = "territory"
    SERIES = "series"


class CanonicalMatch(BaseModel):
    model_config = {"extra": "forbid"}

    kind: CanonicalMatchKind
    canonical_id: str = Field(description="FK into the existing canonical_data/ registry -- never a new id.")
    canonical_name: str
    confidence: ConfidenceLevel = Field(
        description="Confidence of THIS ANALYSIS RUN's match, never a canonical status. See module docstring."
    )
    matched_terms: list[str] = Field(default_factory=list, description="The exact overlapping words the match rests on.")
    rationale: str


class ClassificationOutcome(str, Enum):
    MATCHED = "MATCHED"
    NO_CONFIDENT_CANONICAL_MATCH = "NO_CONFIDENT_CANONICAL_MATCH"


class ClassificationResult(BaseModel):
    model_config = {"extra": "forbid"}

    outcome: ClassificationOutcome
    thesis_family_matches: list[CanonicalMatch] = Field(default_factory=list)
    territory_matches: list[CanonicalMatch] = Field(default_factory=list)
    series_matches: list[CanonicalMatch] = Field(
        default_factory=list, description="Only populated when there is real relevance -- Series is not proposed by default."
    )
    topic: Optional[str] = Field(default=None, description="Free text, per Beslut: topic stays open, never a registry id.")


# ---------------------------------------------------------------------------
# Existing Content Comparison (order section 9-10)
# ---------------------------------------------------------------------------

NEVER_PUBLISHED_CLAIM_FORBIDDEN_NOTE = (
    "Absence of a match in available canonical memory is not evidence the idea was never "
    "published -- Canonical Foundation V1 is not a complete publication history."
)
"""Order section 10: 'Avsaknad av evidens ar inte evidens for avsaknad.' This exact note is
attached to every ComparisonResult so the limitation travels with the result, not just in docs."""


class ComparisonMatch(BaseModel):
    model_config = {"extra": "forbid"}

    content_id: str = Field(description="FK -> ContentRecord.content_id in the compared-against corpus.")
    shared_thesis_family_ids: list[str] = Field(default_factory=list)
    shared_territory_ids: list[str] = Field(default_factory=list)
    shared_terms: list[str] = Field(default_factory=list)
    rationale: str


class ComparisonOutcome(str, Enum):
    MATCHES_FOUND = "MATCHES_FOUND"
    NO_MATCH_IN_AVAILABLE_MEMORY = "NO_MATCH_IN_AVAILABLE_MEMORY"


class ComparisonResult(BaseModel):
    model_config = {"extra": "forbid"}

    outcome: ComparisonOutcome
    matches: list[ComparisonMatch] = Field(default_factory=list)
    corpus_size: int = Field(description="How many existing ContentRecords were actually compared against.")
    memory_limitation_note: str = Field(default=NEVER_PUBLISHED_CLAIM_FORBIDDEN_NOTE)


# ---------------------------------------------------------------------------
# Candidate Angles (order section 11-14)
# ---------------------------------------------------------------------------


class RepetitionRiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class VoiceAlignmentCheck(BaseModel):
    """Beslut 11 (Canonical Voice Core V1) used as an assessment REFERENCE, never a style
    generator (order section 14). Each flag is a simple, transparent, rule-based check --
    not a style/prose judgment."""

    model_config = {"extra": "forbid"}

    stays_close_to_the_human: bool
    makes_a_pattern_visible: bool
    distinguishes_symptom_from_possible_cause: bool
    avoids_unnecessary_abstraction: bool
    leaves_room_for_reader_judgment: bool
    notes: str = ""

    @property
    def score(self) -> int:
        return sum(
            [
                self.stays_close_to_the_human,
                self.makes_a_pattern_visible,
                self.distinguishes_symptom_from_possible_cause,
                self.avoids_unnecessary_abstraction,
                self.leaves_room_for_reader_judgment,
            ]
        )


class CandidateAngle(BaseModel):
    """Wraps a canonical `schema.Angle` (reused, not duplicated) with the analysis-output
    fields order section 12 requires. The `Angle` itself is NOT written into canonical_data/
    -- it is only ever analysis output until a human approves it (see human_decision.py)."""

    model_config = {"extra": "forbid", "arbitrary_types_allowed": True}

    angle: Angle
    core: str = Field(description="One-sentence core of the angle -- 'karna'.")
    why_relevant: str
    canonical_relations: list[str] = Field(default_factory=list, description="Thesis Family / Territory / Series ids this angle relates to.")
    differentiation: str = Field(description="What distinguishes this angle from nearby existing material.")
    repetition_risk: RepetitionRiskLevel
    repetition_rationale: str
    evidence_basis: list[str] = Field(default_factory=list, description="Which interpretation observations this angle rests on.")
    confidence: ConfidenceLevel
    voice_alignment: VoiceAlignmentCheck


# ---------------------------------------------------------------------------
# Recommendation (order section 13, 17)
# ---------------------------------------------------------------------------


class RecommendationOutcome(str, Enum):
    RECOMMENDED = "RECOMMENDED"
    NO_STRONG_ANGLE = "NO_STRONG_ANGLE"


class AngleScore(BaseModel):
    model_config = {"extra": "forbid"}

    angle_id: str
    score: int
    breakdown: dict[str, int] = Field(description="Named criterion -> point contribution. Fully transparent, no hidden math.")


class RecommendationResult(BaseModel):
    model_config = {"extra": "forbid"}

    outcome: RecommendationOutcome
    recommended_angle_id: Optional[str] = None
    scores: list[AngleScore] = Field(default_factory=list)
    rationale: str


# ---------------------------------------------------------------------------
# Pipeline (order section 2, 17)
# ---------------------------------------------------------------------------


class PipelineOutcome(str, Enum):
    MORE_CONTEXT_REQUIRED = "MORE_CONTEXT_REQUIRED"
    COMPLETED = "COMPLETED"


class V1APipelineResult(BaseModel):
    """The full, inspectable trace of one pipeline run. Every intermediate step's output is
    kept, not just the final recommendation -- order section 32 (PIPELINE doc) requires each
    step's responsibility to be visible, and this is what makes that concretely true rather
    than just documented."""

    model_config = {"extra": "forbid", "arbitrary_types_allowed": True}

    outcome: PipelineOutcome
    raw_input: RawInput
    idea: Optional[Idea] = None
    interpretation_draft: Optional[InterpretationDraft] = None
    classification: Optional[ClassificationResult] = None
    comparison: Optional[ComparisonResult] = None
    candidate_angles: list[CandidateAngle] = Field(default_factory=list)
    recommendation: Optional[RecommendationResult] = None
    stopped_reason: Optional[str] = Field(
        default=None, description="Set when outcome == MORE_CONTEXT_REQUIRED, explaining why."
    )
