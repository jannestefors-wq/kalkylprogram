"""
Canonical enums for LUF Core Engine V1 Foundation.

Design rule (inherited from editorial-engine's Beslut 24, "NULL AR BATTRE AN
PAHITT" -- and restated explicitly by Direktorder LUF Core Engine V1 SS 5, 9,
14): nothing in this module hides uncertainty behind a plausible-looking
default. Where a piece of data has genuinely not been verified against
source material, the model must say so with UNKNOWN or UNVERIFIED -- never
with a value invented because it "sounds right" for a leadership model.

Two sentinels used across schema/ and canonical_data/ (see also
`sentinels.py`):
    UNKNOWN    -- the fact itself is not known / not recorded.
    UNVERIFIED -- a candidate value exists (e.g. from the Direktorder text)
                  but has not been checked against independent LUF source
                  material.
"""

from __future__ import annotations

from enum import Enum


class Actor(str, Enum):
    """Who or what produced a piece of data. Mirrors editorial-engine's Actor."""

    HUMAN = "human"
    AI_SYSTEM = "ai_system"
    IMPORT = "import"  # bulk/legacy data migration, not a live actor


class ToolConfidence(str, Enum):
    """
    How solid is a given Canonical Tool Registry entry, distinct from its
    lifecycle status (CanonicalStatus). A HISTORICAL_LUF_MATERIAL entry can
    be VERIFIED as a faithful transcription of an old document while still
    being nowhere near CANONICAL_APPROVED.
    """

    VERIFIED = "verified"                    # checked against a named, inspectable source
    STRONGLY_SUPPORTED = "strongly_supported"  # multiple converging references, not fully checked
    CANDIDATE = "candidate"                    # plausible but only single-sourced
    UNVERIFIED = "unverified"                  # no independent source check has been possible


class CanonicalStatus(str, Enum):
    """
    Evidence/lifecycle boundary (Direktorder S14). Historical material is
    valuable and must be preserved, but must never silently become today's
    canonical method.
    """

    SOURCE_ORIGINAL = "source_original"                # a primary document, not yet interpreted
    HISTORICAL_LUF_MATERIAL = "historical_luf_material"  # older working material, superseded status unclear
    CANONICAL_CANDIDATE = "canonical_candidate"          # proposed for canonical status, not yet reviewed
    CANONICAL_APPROVED = "canonical_approved"            # promoted via Human Review (see human_review/)
    DEPRECATED = "deprecated"


class HumanReviewStatus(str, Enum):
    PENDING = "pending"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_MORE_EVIDENCE = "needs_more_evidence"


class ToolType(str, Enum):
    """Direktorder S7: Core Engine is not limited to triangles."""

    TRIANGLE = "triangle"                # three-component observation model
    N_PART_MODEL = "n_part_model"        # two-, four-, or more-component model
    PROCESS_MODEL = "process_model"      # sequential process (e.g. Maeta-Korrigera-Maeta igen)
    FRAMEWORK_ACRONYM = "framework_acronym"  # named framework (RACE, GROW, ...) -- see note in registry
    QUESTION_SET = "question_set"
    UNKNOWN = "unknown"


class ComponentOrderType(str, Enum):
    """
    Whether a tool's `components` list has a meaningful, fixed order and, if
    so, what kind. Kept separate from `components` itself so ordering
    semantics don't have to be inferred from list position alone.
    """

    SEQUENTIAL_FIXED = "sequential_fixed"        # must be read/applied in the given order
    SEQUENTIAL_REVERSIBLE = "sequential_reversible"  # order matters but direction is a design choice (S8)
    CYCLIC = "cyclic"                            # loops back (e.g. Maeta-Korrigera-Maeta igen)
    NON_SEQUENTIAL = "non_sequential"            # co-equal, no fixed order
    UNVERIFIED = "unverified"


class UsageDirection(str, Enum):
    """
    Direktorder S8: a tool's components may be walked in more than one
    direction depending on purpose (teach a model vs. diagnose reality).
    Never assume a single canonical direction without source evidence.
    """

    LEFT_TO_RIGHT = "left_to_right"
    RIGHT_TO_LEFT = "right_to_left"
    BIDIRECTIONAL_VERIFIED = "bidirectional_verified"  # both directions independently source-attested
    UNVERIFIED = "unverified"


class ClaimType(str, Enum):
    """
    Direktorder S9: the machine-enforced separation between what was
    observed and what a human (or the system) made of it.
    """

    OBSERVATION = "observation"
    INTERPRETATION = "interpretation"
    INFERENCE = "inference"
    ASSUMPTION = "assumption"
    UNKNOWN = "unknown"
    REQUIRES_MORE_CONTEXT = "requires_more_context"


class ZoomLevel(str, Enum):
    """
    Direktorder S10: a CANDIDATE level taxonomy only. The Direktorder is
    explicit that the AI system building this may not lock it in as LUF
    truth without Human Review -- see docs/OPEN_QUESTIONS.md. Do not add call sites that treat
    this enum as settled canonical structure.
    """

    INDIVIDUAL = "individual"
    RELATION = "relation"
    TEAM = "team"
    PROCESS = "process"
    VERKSAMHET = "verksamhet"  # organization / operation
    CULTURE = "culture"
    SYSTEM = "system"


class AccessTier(str, Enum):
    """
    Direktorder S23: a generic entitlement boundary, deliberately kept out
    of schema/ and canonical_data/ so methodology never depends on it.
    Lives only in adapters/entitlement.py.
    """

    FREE = "free"
    DEEP = "deep"


class HouseEventType(str, Enum):
    """
    Direktorder S24: semantic events only. No presentation/visual fields
    belong on these events -- House Engine owns translation to light,
    projection, sound, etc.
    """

    REFLECTION_STARTED = "reflection_started"
    DIMENSION_OPENED = "dimension_opened"
    DEEP_REFLECTION = "deep_reflection"
    TOOL_DISCOVERED = "tool_discovered"
    SESSION_COMPLETED = "session_completed"
