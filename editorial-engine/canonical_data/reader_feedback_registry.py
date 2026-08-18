"""
Canonical Reader Feedback Registry -- Final Canonical Data Closure.

Loads Parastoo Ebrahimzadeh's full original review of "Leadership Without
Filter" (Jan Stefors) verbatim from
`canonical_data/source/parastoo_ebrahimzadeh_review_leadership_without_filter.txt`
and represents it as a real `ReaderFeedback` (schema/reader_effect.py),
plus a `Source(source_type=BOOK)` record for the reviewed work so
`ReaderFeedback.source_id` has something real to point at.

REPORTED SCHEMA GAP (NOT fixed here -- see docs/PARASTOO_INTEGRATION_GAP_REPORT.md
and this order's own section 7/15: "STOPPA. Andra inte Schema V1.1. Rapportera
exakt vilket falt eller vilken relation som saknas."):

`ReaderFeedback.content_reference` is a REQUIRED `str`, documented on the
field itself as "FK -> ContentRecord.content_id this feedback responds to."
Parastoo's review is evidence about a BOOK, not any `ContentRecord` in this
system (a LinkedIn post, a draft, etc.) -- there is no ContentRecord for
"Leadership Without Filter" and inventing one would be fabrication,
forbidden by this order. Because the field is a required, non-Optional
`str` with no legitimate value available, it is set to the literal
sentinel `"UNDERLAG SAKNAS"` -- this project's established convention
(used throughout docs/OPEN_QUESTIONS.md since V1) for an explicitly
flagged, deliberately-not-guessed gap, applied here as a field value
rather than only as prose. It is NOT a fabricated reference and must not
be read as one.

The same root cause blocks full formalization of "which ReaderEffect this
review evidences" as a structured `ReaderEffectAssociation` (Beslut 15):
that association type is only ever embedded on `ContentRecord.reader_effects`,
which -- for the same reason -- has no book-level home here. The one
Reader Effect genuinely supported by the review text (RE-002,
"perspektivskifte") is therefore recorded in `ReaderFeedback.effect_observations`
(free text) instead -- which is exactly what that field is documented to be
for: "Free-text notes on what effect this feedback seems to evidence,
PRIOR TO being formalized into a ReaderEffectAssociation." No new field,
enum, or association was invented to work around this.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from schema import ReaderFeedback, Source
from schema.enums import FeedbackVerificationStatus, SourceType

REVIEW_TEXT_PATH = Path(__file__).parent / "source" / "parastoo_ebrahimzadeh_review_leadership_without_filter.txt"

BOOK_SOURCE_ID = "source-book-leadership-without-filter"
READER_FEEDBACK_ID = "reader-feedback-parastoo-ebrahimzadeh-leadership-without-filter-001"

DATE_RECEIVED = datetime(2026, 8, 18, tzinfo=timezone.utc)

CONTENT_REFERENCE_GAP_SENTINEL = "UNDERLAG SAKNAS"
"""Literal value stored in ReaderFeedback.content_reference -- see module docstring.
Deliberately NOT a real ContentRecord id. Recognizable, project-wide convention for
an explicitly-flagged gap, not a guess."""


def load_book_source() -> Source:
    """The reviewed work, as bibliographic metadata directly transcribed from what
    project management supplied (title, author) -- nothing inferred or invented."""
    return Source(
        source_id=BOOK_SOURCE_ID,
        source_type=SourceType.BOOK,
        title="Leadership Without Filter",
        author="Jan Stefors",
        date=None,  # publication date not supplied -- null, not guessed
        language=None,  # the book's own language was not supplied (only the review's was) -- null, not guessed
        origin=None,
        content_reference=None,
        themes=[],
        people=[],
        models=[],
        series=[],
        reliability=None,
        usage_rights=None,
        notes=(
            "Bibliographic stub created to give ReaderFeedback.source_id a real target for "
            f"{READER_FEEDBACK_ID!r}, without fabricating a ContentRecord. See "
            "canonical_data/reader_feedback_registry.py module docstring."
        ),
    )


def load_parastoo_reader_feedback(review_text_path: Path = REVIEW_TEXT_PATH) -> ReaderFeedback:
    """Build the real ReaderFeedback record. `feedback_text` is the source file's content,
    read verbatim -- no editing, shortening, translation, or normalization of any kind."""

    original_text = review_text_path.read_text(encoding="utf-8").strip("\n")

    return ReaderFeedback(
        reader_feedback_id=READER_FEEDBACK_ID,
        source_id=BOOK_SOURCE_ID,
        content_reference=CONTENT_REFERENCE_GAP_SENTINEL,
        feedback_text=original_text,
        feedback_reference=None,
        effect_observations=[
            "RE-002 (perspektivskifte / 'sprak for monster') -- stott direkt av originaltexten: "
            "\"those experiences are not necessarily invisible or impossible to explain. "
            "There are patterns behind them, and those patterns can be recognized and understood.\" "
            "och \"Jan Stefors' writing can help the reader recognize these patterns more clearly.\" "
            "Inte formaliserad som ReaderEffectAssociation (kraver en ContentRecord, som saknas for "
            "denna bokrecension) -- se modulens docstring.",
        ],
        verification_status=FeedbackVerificationStatus.VERIFIED_VERBATIM,
        date=DATE_RECEIVED,
        language="en",
        notes=(
            "Reviewer: Parastoo Ebrahimzadeh. Reviewed work: 'Leadership Without Filter' by Jan Stefors. "
            "Source type: Direct message from reviewer. Verification: Verified from original direct message "
            "and screenshots supplied by project leadership. "
            "content_reference intentionally holds an explicit gap marker, not a real reference -- see "
            "canonical_data/reader_feedback_registry.py module docstring and "
            "docs/PARASTOO_INTEGRATION_GAP_REPORT.md."
        ),
    )


if __name__ == "__main__":
    book = load_book_source()
    feedback = load_parastoo_reader_feedback()
    print(f"Source: {book.source_id} -- {book.title!r} by {book.author}")
    print(f"ReaderFeedback: {feedback.reader_feedback_id}")
    print(f"  verification_status={feedback.verification_status.value} language={feedback.language}")
    print(f"  feedback_text length={len(feedback.feedback_text)} chars")
    print(f"  content_reference={feedback.content_reference!r} (gap marker, see docstring)")
    print(f"  effect_observations={feedback.effect_observations}")
