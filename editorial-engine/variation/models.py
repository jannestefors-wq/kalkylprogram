"""
V1C Variation Analysis models (order sections 3-4, 7-8, 17-25).

Everything here is PROTOTYPE ANALYSIS OUTPUT, not canonical data -- mirrors
`engine/models.py`'s own module docstring discipline. None of it is
exported from `schema/`, none of it is written into `canonical_data/`,
and none of it changes Canonical Foundation V1. `VariationProfile` is
built from real text but is itself never mistaken for content metadata:
it lives only in `variation/`, is never written back onto
`schema.ContentRecord` or an Editorial Memory record's `original_text`.

Work's Variation Foundation report identified 9 candidate dimensions with
DIFFERENT evidence strength (order section 5). This module encodes that
distinction as DATA (`DIMENSION_EVIDENCE_STATUS`), not just prose, so
downstream logic can structurally refuse to treat an EXPLORATORY
dimension the same as an OBSERVED one. Sustained Narrative Form
(EXPLORATORY) is not implemented at all (order section 6, 29) -- there is
no enum, no field, no code path for it anywhere in `variation/`.

Reuses existing engine-output vocabulary rather than inventing parallel
ones: `engine.models.ConfidenceLevel` (LOW/MEDIUM/HIGH) for per-field
analysis confidence, and `schema.Provenance` for who/when/how each
profile was produced.
"""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from schema import Provenance

from engine.models import ConfidenceLevel


class DimensionEvidenceStatus(str, Enum):
    """How well-supported a VARIATION DIMENSION ITSELF is by Work's Variation
    Foundation analysis -- a fixed property of the dimension, not of any one
    analysis run. Distinct from `ConfidenceLevel`, which is per-field,
    per-analysis. A dimension can be OBSERVED while one particular analysis
    of it is still LOW confidence (little evidence in that specific text)."""

    OBSERVED = "observed"
    SUPPORTED_HYPOTHESIS = "supported_hypothesis"
    EXPLORATORY = "exploratory"


DIMENSION_EVIDENCE_STATUS: dict[str, DimensionEvidenceStatus] = {
    "entry_mode": DimensionEvidenceStatus.OBSERVED,
    "lens": DimensionEvidenceStatus.OBSERVED,
    "narrative_distance": DimensionEvidenceStatus.OBSERVED,
    "structural_arc": DimensionEvidenceStatus.OBSERVED,
    "rhetorical_pressure": DimensionEvidenceStatus.OBSERVED,
    "closure_mode": DimensionEvidenceStatus.OBSERVED,
    "disclosure_pace": DimensionEvidenceStatus.SUPPORTED_HYPOTHESIS,
    "emotional_temperature": DimensionEvidenceStatus.SUPPORTED_HYPOTHESIS,
}
"""order section 5. Sustained Narrative Form (EXPLORATORY) is deliberately
absent -- order section 29 forbids implementing it as a stable dimension."""

OBSERVED_DIMENSIONS: tuple[str, ...] = (
    "entry_mode",
    "lens",
    "narrative_distance",
    "structural_arc",
    "rhetorical_pressure",
    "closure_mode",
)
"""order section 6: the six-dimension prototype core. Only these may ever
drive repetition/recommendation decisions on their own (order section 28)."""


class EntryMode(str, Enum):
    SITUATION = "situation"
    CLAIM = "claim"
    QUESTION = "question"
    PROCESS = "process"
    CONSEQUENCE = "consequence"
    UNKNOWN = "unknown"


class Lens(str, Enum):
    RESPONSIBILITY = "responsibility"
    POWER = "power"
    RELATION = "relation"
    SYSTEM = "system"
    CONSEQUENCE = "consequence"
    INDIVIDUAL_EXPERIENCE = "individual_experience"
    UNKNOWN = "unknown"


class NarrativeDistance(str, Enum):
    CLOSE_HUMAN = "close_human"
    DIRECT_ADDRESS = "direct_address"
    OBSERVER = "observer"
    SYSTEM_LEVEL = "system_level"
    UNKNOWN = "unknown"


class StructuralArc(str, Enum):
    SCENE_TO_INSIGHT = "scene_to_insight"
    CLAIM_TO_EVIDENCE = "claim_to_evidence"
    FRAMEWORK_TO_DIRECTION = "framework_to_direction"
    ESCALATION_TO_CONSEQUENCE = "escalation_to_consequence"
    DILEMMA_TO_OPEN_END = "dilemma_to_open_end"
    UNKNOWN = "unknown"


class RhetoricalPressure(str, Enum):
    CONTRAST = "contrast"
    QUESTION = "question"
    CONSEQUENCE = "consequence"
    IMPERATIVE = "imperative"
    QUIET_OBSERVATION = "quiet_observation"
    UNKNOWN = "unknown"


class ClosureMode(str, Enum):
    ACTION = "action"
    CONSEQUENCE = "consequence"
    OPEN_QUESTION = "open_question"
    STILL_STATEMENT = "still_statement"
    UNRESOLVED_TENSION = "unresolved_tension"
    UNKNOWN = "unknown"


class DisclosurePace(str, Enum):
    GRADUAL = "gradual"
    IMMEDIATE = "immediate"
    UNKNOWN = "unknown"


class EmotionalTemperature(str, Enum):
    WARM = "warm"
    COOL = "cool"
    NEUTRAL = "neutral"
    UNKNOWN = "unknown"


class DimensionAssessment(BaseModel):
    """One dimension's analysis result. `evidence_status` is copied from the
    fixed `DIMENSION_EVIDENCE_STATUS` table (order section 5) -- never set
    per-analysis -- so a SUPPORTED_HYPOTHESIS field can never silently read
    as though it were OBSERVED."""

    model_config = {"extra": "forbid"}

    value: str = Field(description="One of the dimension's enum values, or 'unknown'.")
    confidence: ConfidenceLevel = Field(description="Confidence of THIS analysis run. Never a canonical status.")
    evidence: str = Field(description="Human-readable reason the analysis reached this value. No black box.")
    evidence_status: DimensionEvidenceStatus


class SourceKind(str, Enum):
    EDITORIAL_MEMORY_RECORD = "editorial_memory_record"
    CANDIDATE_ANGLE = "candidate_angle"


class VariationProfile(BaseModel):
    """PROTOTYPE ANALYSIS OUTPUT (order section 4, 7) -- never canonical
    content metadata. `source_id` is an Editorial Memory `content_id` or a
    V1A `CandidateAngle.angle.angle_id`, never a new canonical id."""

    model_config = {"extra": "forbid"}

    profile_id: str
    source_id: str
    source_kind: SourceKind

    entry_mode: DimensionAssessment
    lens: DimensionAssessment
    narrative_distance: DimensionAssessment
    structural_arc: DimensionAssessment
    rhetorical_pressure: DimensionAssessment
    closure_mode: DimensionAssessment

    disclosure_pace: Optional[DimensionAssessment] = None
    emotional_temperature: Optional[DimensionAssessment] = None

    analysis_logic_version: str
    provenance: Provenance

    def observed_values(self) -> dict[str, str]:
        """The six OBSERVED dimensions only -- what repetition/comparison logic
        is allowed to use (order section 28: hypothesis dimensions never decide
        anything alone)."""
        return {name: getattr(self, name).value for name in OBSERVED_DIMENSIONS}


class DimensionComparison(BaseModel):
    model_config = {"extra": "forbid"}

    dimension: str
    profile_a_value: str
    profile_b_value: str
    same: bool


class VariationDistanceCategory(str, Enum):
    """order section 18: explainable categories, never a fabricated precise
    score."""

    TOO_SIMILAR = "TOO_SIMILAR"
    PARTIALLY_DISTINCT = "PARTIALLY_DISTINCT"
    STRUCTURALLY_DISTINCT = "STRUCTURALLY_DISTINCT"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


class StructuralComparisonResult(BaseModel):
    model_config = {"extra": "forbid"}

    profile_a_id: str
    profile_b_id: str
    dimension_comparisons: list[DimensionComparison] = Field(default_factory=list)
    same_count: int
    different_count: int
    overall: VariationDistanceCategory


class RepetitionAxis(str, Enum):
    """order section 19: these must never collapse into one signal."""

    THESIS = "thesis"
    ANGLE = "angle"
    STRUCTURAL = "structural"
    OPENING = "opening"
    ENDING = "ending"
    LEXICAL = "lexical"


class RepetitionAxisAssessment(BaseModel):
    model_config = {"extra": "forbid"}

    axis: RepetitionAxis
    detected: bool
    rationale: str


class MultiAxisRepetitionResult(BaseModel):
    model_config = {"extra": "forbid"}

    assessments: list[RepetitionAxisAssessment] = Field(default_factory=list)

    def detected_axes(self) -> list[RepetitionAxis]:
        return [a.axis for a in self.assessments if a.detected]


class FalseVariationAssessment(BaseModel):
    """order section 17: is a proposed alternative genuinely structurally
    different, or the same construction in new words?"""

    model_config = {"extra": "forbid"}

    is_false_variation: bool
    rationale: str
    identical_dimensions: list[str] = Field(default_factory=list)
    changed_dimensions: list[str] = Field(default_factory=list)


class ControlledVariationOption(BaseModel):
    model_config = {"extra": "forbid"}

    option_id: str
    relates_to_angle_id: str
    proposed_changes: dict[str, str] = Field(description="OBSERVED dimension name -> new proposed value.")
    stable_dimensions: dict[str, str] = Field(description="OBSERVED dimension name -> value held constant.")
    memory_relation: str = Field(description="How this option relates to/differs from relevant Editorial Memory.")
    distinctiveness: VariationDistanceCategory
    false_variation: FalseVariationAssessment
    confidence: ConfidenceLevel
    evidence: list[str] = Field(default_factory=list)
    provenance: Provenance


class VariationRecommendationOutcome(str, Enum):
    RECOMMENDED = "RECOMMENDED"
    NO_MEANINGFUL_VARIATION = "NO_MEANINGFUL_VARIATION"
    INSUFFICIENT_VARIATION_EVIDENCE = "INSUFFICIENT_VARIATION_EVIDENCE"


MAX_CONTROLLED_VARIATION_OPTIONS = 3
"""order section 24: never more, and 0/1/2 are all legitimate."""


class VariationRecommendationResult(BaseModel):
    model_config = {"extra": "forbid"}

    outcome: VariationRecommendationOutcome
    options: list[ControlledVariationOption] = Field(default_factory=list)
    recommended_option_id: Optional[str] = None
    rationale: str
