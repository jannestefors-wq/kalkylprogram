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

from .comparison import MIN_FULLTEXT_OVERLAP_TERMS_FOR_CONTENT_SIGNAL, MemoryComparisonResult


def to_legacy_comparison_result(memory_result: MemoryComparisonResult) -> ComparisonResult:
    """V1B Correction Order (Defect 2): a match is only passed through as a
    canonical-relation match (which V1A's engine/angles.py::_repetition_risk_for()
    treats as HIGH-eligible) when it is `strong` -- i.e. corroborated by BOTH a
    shared canonical relation AND real raw-input content overlap
    (memory/comparison.py). A `weak` match with only a lone canonical relation and
    NO content-level corroboration is too generic to drive repetition scoring on
    its own (order section 8: "ett enskilt svagt/generiskt ord far inte ensamt...")
    and is dropped from the legacy result entirely -- it remains fully visible in
    the richer `MemoryComparisonResult`/`MemoryRetrievalResult` for transparency,
    just not counted toward V1A's HIGH/MEDIUM arithmetic. A `weak` match that DOES
    have real content-level overlap (topic/text) but no canonical relation is kept,
    surfaced only via `shared_terms` -- genuine lexical evidence, still MEDIUM-
    eligible under V1A's existing (unmodified) scoring, never HIGH on its own."""

    matches = []
    for m in memory_result.matches:
        # Recompute whether content-level overlap actually clears the same
        # specificity threshold comparison.py used (a single incidental shared
        # word is never enough) -- consistent rather than re-deriving a looser
        # "any overlap at all" check here.
        content_signal = bool(m.topic_overlap) or len(m.text_overlap_terms) >= MIN_FULLTEXT_OVERLAP_TERMS_FOR_CONTENT_SIGNAL
        content_terms = sorted(set(m.text_overlap_terms) | set(m.topic_overlap)) if content_signal else []

        if m.repetition_signal_strength == "strong":
            matches.append(
                ComparisonMatch(
                    content_id=m.content_id,
                    shared_thesis_family_ids=m.shared_thesis_family_ids,
                    shared_territory_ids=m.shared_territory_ids,
                    shared_terms=content_terms,
                    rationale=m.why_relevant,
                )
            )
        elif content_signal:
            matches.append(
                ComparisonMatch(
                    content_id=m.content_id,
                    shared_thesis_family_ids=[],
                    shared_territory_ids=[],
                    shared_terms=content_terms,
                    rationale=m.why_relevant,
                )
            )
        # else: either a canonical-relation-only weak match with no content-level
        # corroboration, or a sub-threshold incidental overlap (e.g. one shared
        # common word) -- neither is excluded from the richer MemoryComparisonResult,
        # but neither is strong enough to feed V1A's repetition scoring.

    # Outcome is recomputed from the FILTERED matches, not copied from
    # memory_result.outcome -- a memory_result that only had canonical-only weak
    # matches (now excluded above) must legitimately read as NO_MATCH here, not as
    # MATCHES_FOUND with an empty match list.
    outcome = ComparisonOutcome.MATCHES_FOUND if matches else ComparisonOutcome.NO_MATCH_IN_AVAILABLE_MEMORY

    return ComparisonResult(
        outcome=outcome,
        matches=matches,
        corpus_size=memory_result.corpus_size,
    )
