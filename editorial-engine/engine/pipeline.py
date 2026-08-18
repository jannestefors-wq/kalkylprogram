"""
The V1A vertical chain, wired end to end (order section 2):

    Raw Idea -> Interpretation -> Canonical Classification ->
    Existing Content Comparison -> Candidate Angles -> Recommended Angle
    -> [Human Decision, called separately -- see human_decision.py]

`run_v1a_pipeline` stops early and returns `PipelineOutcome.MORE_CONTEXT_REQUIRED`
when the raw input is too thin (order section 17) -- it never forces the
remaining steps to run on insufficient material. Every other step always
runs and always returns a real result object (possibly a "no match" /
"no strong angle" sentinel outcome, never a fabricated positive one).

Reuses `canonical_data/` registries by default (real Series/ThesisFamily/
Territory), and defaults `existing_content` to an empty list -- callers
that want to exercise repetition detection pass in whatever `ContentRecord`s
they want compared against (see docs/V1A_MEMORY_LIMITATION.md for why V1A
has no corpus of its own to default to).
"""

from __future__ import annotations

import uuid

from schema import ContentRecord, Series, Territory, ThesisFamily

from .angles import propose_candidate_angles
from .classification import classify
from .comparison import compare_to_existing_content
from .human_decision import HumanAction, build_human_decision  # noqa: F401 -- re-exported for pipeline callers
from .interpretation import ANALYSIS_LOGIC_VERSION, build_idea, build_interpretation_draft, build_raw_input, render_idea_interpretation
from .models import PipelineOutcome, V1APipelineResult
from .provider import AnalysisProvider, RuleBasedAnalysisProvider
from .recommendation import recommend

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


def run_v1a_pipeline(
    raw_text: str,
    raw_input_id: str | None = None,
    idea_id: str | None = None,
    language: str = "sv",
    existing_content: list[ContentRecord] | None = None,
    provider: AnalysisProvider | None = None,
    series_registry: list[Series] | None = None,
    thesis_family_registry: list[ThesisFamily] | None = None,
    territory_registry: list[Territory] | None = None,
) -> V1APipelineResult:
    provider = provider or RuleBasedAnalysisProvider()
    existing_content = existing_content if existing_content is not None else []

    if series_registry is None:
        from canonical_data.series_registry import load_series_registry

        series_registry = load_series_registry()
    if thesis_family_registry is None:
        from canonical_data.thesis_family_registry import load_thesis_family_registry

        thesis_family_registry = load_thesis_family_registry()
    if territory_registry is None:
        from canonical_data.territory_registry import load_territory_registry

        territory_registry = load_territory_registry()

    raw_input = build_raw_input(raw_input_id or _new_id("RI-V1A"), raw_text, language=language)

    if not provider.is_sufficient(raw_text):
        return V1APipelineResult(
            outcome=PipelineOutcome.MORE_CONTEXT_REQUIRED,
            raw_input=raw_input,
            stopped_reason=(
                "Rainput ar for tunt for ansvarsfull interpretation (for fa ord och/eller inga "
                "konkreta markorer for handling/roll/upprepning). Mer kontext kravs."
            ),
        )

    draft = build_interpretation_draft(raw_text, provider)
    interpretation = render_idea_interpretation(draft)
    idea = build_idea(idea_id or _new_id("IDEA-V1A"), raw_input, interpretation)

    interpretation_texts = {k: getattr(interpretation, k) for k in _INTERPRETATION_FIELD_KEYS}
    combined_text = " ".join(v for v in interpretation_texts.values() if v)

    classification = classify(combined_text, series_registry, thesis_family_registry, territory_registry)
    comparison = compare_to_existing_content(combined_text, classification, existing_content)
    candidates = propose_candidate_angles(
        idea.idea_id, interpretation_texts, classification, comparison, provider, ANALYSIS_LOGIC_VERSION
    )

    recommendation = recommend(candidates)

    return V1APipelineResult(
        outcome=PipelineOutcome.COMPLETED,
        raw_input=raw_input,
        idea=idea,
        interpretation_draft=draft,
        classification=classification,
        comparison=comparison,
        candidate_angles=candidates,
        recommendation=recommendation,
    )
