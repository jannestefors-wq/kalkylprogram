"""
Step 4: Existing Content Comparison (order section 9-10).

Compares the interpreted idea against whatever `ContentRecord`s are
actually passed in as the "available canonical memory" -- V1A has no
publication-history corpus of its own, so callers (pipeline.py, tests)
supply whichever corpus is relevant to the scenario being run. No
embeddings, no vector database, no external retrieval service (order
section 9/24) -- just the same transparent word-overlap approach as
classification.py, plus explicit thesis-family/territory id overlap.

CRITICAL (order section 10): absence of a match must never be phrased as
"never published before" -- Canonical Foundation V1 is not a complete
publication history. See `ComparisonOutcome.NO_MATCH_IN_AVAILABLE_MEMORY`
and `NEVER_PUBLISHED_CLAIM_FORBIDDEN_NOTE` in models.py, which every
`ComparisonResult` carries.
"""

from __future__ import annotations

from schema import ContentRecord

from .models import ClassificationResult, ComparisonMatch, ComparisonOutcome, ComparisonResult
from .text_utils import normalize_words


def compare_to_existing_content(
    interpretation_text: str,
    classification: ClassificationResult,
    existing_content: list[ContentRecord],
) -> ComparisonResult:
    text_words = normalize_words(interpretation_text)
    classified_thesis_family_ids = {m.canonical_id for m in classification.thesis_family_matches}
    classified_territory_ids = {m.canonical_id for m in classification.territory_matches}

    matches: list[ComparisonMatch] = []
    for content in existing_content:
        shared_thesis = ({content.thesis_family_id} & classified_thesis_family_ids) if content.thesis_family_id else set()
        shared_territory = set(content.territory_ids) & classified_territory_ids
        content_words = normalize_words(
            " ".join(
                filter(
                    None,
                    [content.what.core_thesis, content.what.hidden_pattern, content.what.root_cause, content.what.human_conflict],
                )
            )
        )
        shared_terms = sorted(content_words & text_words)

        if shared_thesis or shared_territory or shared_terms:
            reasons = []
            if shared_thesis:
                reasons.append(f"delad Thesis Family ({', '.join(sorted(shared_thesis))})")
            if shared_territory:
                reasons.append(f"delat Territory ({', '.join(sorted(shared_territory))})")
            if shared_terms:
                reasons.append(f"delade termer ({', '.join(shared_terms)})")
            matches.append(
                ComparisonMatch(
                    content_id=content.content_id,
                    shared_thesis_family_ids=sorted(shared_thesis),
                    shared_territory_ids=sorted(shared_territory),
                    shared_terms=shared_terms,
                    rationale="Narliggande pa grund av: " + "; ".join(reasons) + ".",
                )
            )

    outcome = ComparisonOutcome.MATCHES_FOUND if matches else ComparisonOutcome.NO_MATCH_IN_AVAILABLE_MEMORY

    return ComparisonResult(
        outcome=outcome,
        matches=matches,
        corpus_size=len(existing_content),
    )
