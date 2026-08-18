"""
The V1B vertical chain (order section 1, 2):

    Raw Idea -> Interpretation -> Canonical Classification ->
    Editorial Memory Retrieval -> Existing Content Comparison ->
    Candidate Angles -> Recommended Angle
    -> [Human Decision, called separately -- see engine/human_decision.py]

This module ADDS a new pipeline function, `run_v1b_pipeline`. It does not
modify `engine/pipeline.py::run_v1a_pipeline` in any way (order section 22:
"V1A far inte skrivas om") -- V1A's own pipeline, and all 127 tests that
exercise it, are completely untouched by this file's existence.

`run_v1b_pipeline` reuses V1A's own step functions directly (interpretation,
classification, angle proposal, recommendation) rather than reimplementing
them, and only adds the two new steps order section 1 asks for: Editorial
Memory Retrieval and a memory-driven comparison. The memory comparison is
bridged into the exact `ComparisonResult` shape `engine/angles.py` already
consumes (see `memory/bridge.py`), so repetition risk and candidate-angle
differentiation are computed by the SAME, unmodified V1A scoring logic --
now fed real data instead of an empty corpus.
"""

from __future__ import annotations

import uuid
from typing import Optional

from pydantic import BaseModel, Field

from engine.angles import propose_candidate_angles
from engine.classification import classify
from engine.interpretation import ANALYSIS_LOGIC_VERSION, build_idea, build_interpretation_draft, build_raw_input, render_idea_interpretation
from engine.models import CandidateAngle, ClassificationResult, InterpretationDraft, PipelineOutcome, RecommendationResult
from engine.provider import AnalysisProvider, RuleBasedAnalysisProvider
from engine.recommendation import recommend
from schema import Idea, RawInput, Series, Territory, ThesisFamily

from .bridge import to_legacy_comparison_result
from .comparison import MemoryComparisonResult, compare_to_editorial_memory
from .ingestion import load_editorial_memory
from .models import EditorialMemoryRecord
from .retrieval import MemoryRetrievalResult, retrieve_relevant_memory

_INTERPRETATION_FIELD_KEYS = [
    "observed_situation",
    "visible_problem",
    "hidden_conflict",
    "power_dimension",
    "relationship_dimension",
    "system_dimension",
    "possible_consequence",
]


def _new_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


class V1BPipelineResult(BaseModel):
    """Same shape as V1A's `V1APipelineResult`, plus the two new memory
    steps (order section 1). `comparison` is the legacy-adapted result (so
    it reads exactly like a V1A `ComparisonResult` for any caller that only
    cares about that) -- `memory_comparison` is the richer, V1B-only view
    with text completeness, publication status and evidence boundaries."""

    model_config = {"extra": "forbid", "arbitrary_types_allowed": True}

    outcome: PipelineOutcome
    raw_input: RawInput
    idea: Optional[Idea] = None
    interpretation_draft: Optional[InterpretationDraft] = None
    classification: Optional[ClassificationResult] = None
    memory_retrieval: Optional[MemoryRetrievalResult] = None
    memory_comparison: Optional[MemoryComparisonResult] = None
    candidate_angles: list[CandidateAngle] = Field(default_factory=list)
    recommendation: Optional[RecommendationResult] = None
    stopped_reason: Optional[str] = None


def run_v1b_pipeline(
    raw_text: str,
    raw_input_id: str | None = None,
    idea_id: str | None = None,
    language: str = "sv",
    memory_records: list[EditorialMemoryRecord] | None = None,
    provider: AnalysisProvider | None = None,
    series_registry: list[Series] | None = None,
    thesis_family_registry: list[ThesisFamily] | None = None,
    territory_registry: list[Territory] | None = None,
) -> V1BPipelineResult:
    provider = provider or RuleBasedAnalysisProvider()
    memory_records = load_editorial_memory() if memory_records is None else memory_records

    if series_registry is None:
        from canonical_data.series_registry import load_series_registry

        series_registry = load_series_registry()
    if thesis_family_registry is None:
        from canonical_data.thesis_family_registry import load_thesis_family_registry

        thesis_family_registry = load_thesis_family_registry()
    if territory_registry is None:
        from canonical_data.territory_registry import load_territory_registry

        territory_registry = load_territory_registry()

    raw_input = build_raw_input(raw_input_id or _new_id("RI-V1B"), raw_text, language=language)

    if not provider.is_sufficient(raw_text):
        return V1BPipelineResult(
            outcome=PipelineOutcome.MORE_CONTEXT_REQUIRED,
            raw_input=raw_input,
            stopped_reason=(
                "Rainput ar for tunt for ansvarsfull interpretation (for fa ord och/eller inga "
                "konkreta markorer for handling/roll/upprepning). Mer kontext kravs."
            ),
        )

    draft = build_interpretation_draft(raw_text, provider)
    interpretation = render_idea_interpretation(draft)
    idea = build_idea(idea_id or _new_id("IDEA-V1B"), raw_input, interpretation)

    interpretation_texts = {k: getattr(interpretation, k) for k in _INTERPRETATION_FIELD_KEYS}
    combined_text = " ".join(v for v in interpretation_texts.values() if v)

    classification = classify(combined_text, series_registry, thesis_family_registry, territory_registry)

    memory_retrieval = retrieve_relevant_memory(combined_text, classification, memory_records)
    memory_comparison = compare_to_editorial_memory(combined_text, classification, memory_records)
    legacy_comparison = to_legacy_comparison_result(memory_comparison)

    candidates = propose_candidate_angles(
        idea.idea_id, interpretation_texts, classification, legacy_comparison, provider, ANALYSIS_LOGIC_VERSION
    )

    recommendation = recommend(candidates)

    return V1BPipelineResult(
        outcome=PipelineOutcome.COMPLETED,
        raw_input=raw_input,
        idea=idea,
        interpretation_draft=draft,
        classification=classification,
        memory_retrieval=memory_retrieval,
        memory_comparison=memory_comparison,
        candidate_angles=candidates,
        recommendation=recommendation,
    )
