"""
Bridge: MemoryComparisonResult -> engine.models.ComparisonResult (V1B order
section 14, 16, 22).

This is what lets Editorial Memory actually influence Candidate Angles
(order section 16) WITHOUT rewriting a single line of `engine/angles.py`
or `engine/recommendation.py` (order section 22: "V1A far inte skrivas
om"). `propose_candidate_angles()` already derives repetition risk from a
`ComparisonResult`'s `matches` (shared thesis family / territory ids,
shared terms) -- so feeding it a `ComparisonResult` built FROM a real
`MemoryComparisonResult` makes memory-driven repetition risk and
candidate-angle differentiation happen through the EXACT SAME, already
tested V1A logic, unmodified.

The richer `MemoryComparisonResult` (text completeness, publication status,
evidence boundary, ...) is never lost -- `V1BPipelineResult` (memory/pipeline.py)
carries it alongside the adapted legacy result, so nothing that order
section 14 asked for is dropped; it is just not what feeds the angle-scoring
arithmetic (which order section 22 forbids touching).
"""

from __future__ import annotations

from engine.models import ComparisonMatch, ComparisonOutcome, ComparisonResult

from .comparison import MemoryComparisonOutcome, MemoryComparisonResult

_OUTCOME_MAP = {
    MemoryComparisonOutcome.MATCHES_FOUND: ComparisonOutcome.MATCHES_FOUND,
    MemoryComparisonOutcome.NO_MATCH_IN_AVAILABLE_MEMORY: ComparisonOutcome.NO_MATCH_IN_AVAILABLE_MEMORY,
}


def to_legacy_comparison_result(memory_result: MemoryComparisonResult) -> ComparisonResult:
    matches = [
        ComparisonMatch(
            content_id=m.content_id,
            shared_thesis_family_ids=m.shared_thesis_family_ids,
            shared_territory_ids=m.shared_territory_ids,
            shared_terms=m.text_overlap_terms or m.topic_overlap,
            rationale=m.why_relevant,
        )
        for m in memory_result.matches
    ]
    return ComparisonResult(
        outcome=_OUTCOME_MAP[memory_result.outcome],
        matches=matches,
        corpus_size=memory_result.corpus_size,
    )
