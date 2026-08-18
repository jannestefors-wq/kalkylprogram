"""
Step 3: Canonical Classification (order section 7-8).

Transparent word-overlap matching against the REAL canonical registries
(canonical_data/) -- no embeddings, no vector search (order section 9/24
forbids those for V1A). Every match carries the exact overlapping words as
its rationale, so a human can check the reasoning by eye. If nothing
overlaps meaningfully, the result is
`ClassificationOutcome.NO_CONFIDENT_CANONICAL_MATCH` -- never a guessed
match, and never a new Thesis Family / Territory / Series (order section 7:
"Motorn far inte skapa: Thesis Family nummer 9, nytt Territory, ny Series").

A plain set-intersection over Swedish function words ("och", "det", "att",
"som", ...) would match almost everything against almost everything and
make the "transparent" comparison meaningless noise -- so those are
filtered out via `STOPWORDS` before any overlap is computed. This is the
only filtering step; there is no stemming, no fuzzy/substring matching, no
similarity scoring -- exact word match only, so every match is traceable to
literal shared vocabulary.
"""

from __future__ import annotations

from schema import Series, Territory, ThesisFamily

from .models import CanonicalMatch, CanonicalMatchKind, ClassificationOutcome, ClassificationResult, ConfidenceLevel
from .text_utils import normalize_words

SERIES_MATCH_MIN_TERMS = 2
"""order section 7: Series ska endast foreslas om det finns verklig relevans -- a stricter
bar than Thesis Family/Territory, which only need one overlapping term."""


def _related_terms_for_thesis_family(tf: ThesisFamily) -> set[str]:
    terms: set[str] = set()
    if tf.description and tf.description.lower().startswith("relaterade teman:"):
        raw = tf.description.split(":", 1)[1].strip().rstrip(".")
        terms |= {t.strip() for t in raw.split(",") if t.strip()}
    terms |= normalize_words(tf.core_statement)
    return terms


def _confidence_for(overlap_count: int) -> ConfidenceLevel:
    if overlap_count >= 3:
        return ConfidenceLevel.HIGH
    if overlap_count == 2:
        return ConfidenceLevel.MEDIUM
    return ConfidenceLevel.LOW


def classify(
    interpretation_text: str,
    series_registry: list[Series],
    thesis_family_registry: list[ThesisFamily],
    territory_registry: list[Territory],
) -> ClassificationResult:
    text_words = normalize_words(interpretation_text)

    thesis_family_matches: list[CanonicalMatch] = []
    for tf in thesis_family_registry:
        candidate_terms = _related_terms_for_thesis_family(tf)
        overlap = sorted(candidate_terms & text_words)
        if overlap:
            thesis_family_matches.append(
                CanonicalMatch(
                    kind=CanonicalMatchKind.THESIS_FAMILY,
                    canonical_id=tf.thesis_family_id,
                    canonical_name=tf.name,
                    confidence=_confidence_for(len(overlap)),
                    matched_terms=overlap,
                    rationale=f"{len(overlap)} overlappande term(er) med Thesis Familyns tema/karnformulering: {', '.join(overlap)}.",
                )
            )

    territory_matches: list[CanonicalMatch] = []
    for territory in territory_registry:
        name_words = normalize_words(territory.name)
        overlap = sorted(name_words & text_words)
        if overlap:
            territory_matches.append(
                CanonicalMatch(
                    kind=CanonicalMatchKind.TERRITORY,
                    canonical_id=territory.territory_id,
                    canonical_name=territory.name,
                    confidence=_confidence_for(len(overlap) + 1),  # a Territory name-hit is a strong signal on its own
                    matched_terms=overlap,
                    rationale=f"Territoryts namn ('{territory.name}') forekommer i interpretationstexten.",
                )
            )

    series_matches: list[CanonicalMatch] = []
    for series in series_registry:
        candidate_terms = normalize_words(series.description or "") | normalize_words(series.name)
        overlap = sorted(candidate_terms & text_words)
        if len(overlap) >= SERIES_MATCH_MIN_TERMS:
            series_matches.append(
                CanonicalMatch(
                    kind=CanonicalMatchKind.SERIES,
                    canonical_id=series.series_id,
                    canonical_name=series.name,
                    confidence=_confidence_for(len(overlap)),
                    matched_terms=overlap,
                    rationale=(
                        f"{len(overlap)} overlappande term(er) med seriens beskrivning "
                        f"(over tradskeln pa {SERIES_MATCH_MIN_TERMS} for verklig relevans): {', '.join(overlap)}."
                    ),
                )
            )

    outcome = (
        ClassificationOutcome.MATCHED
        if (thesis_family_matches or territory_matches or series_matches)
        else ClassificationOutcome.NO_CONFIDENT_CANONICAL_MATCH
    )

    return ClassificationResult(
        outcome=outcome,
        thesis_family_matches=thesis_family_matches,
        territory_matches=territory_matches,
        series_matches=series_matches,
        topic=None,  # topic stays open (order section 7) -- classification never assigns one
    )
