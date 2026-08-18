"""
Canonical enums / taxonomies for the LUF Editorial Engine schema.

Design rule (Beslut 24 -- "NULL AR BATTRE AN PAHITT"):
    None of these enums include a hidden "unknown" catch-all value that a
    producer could reach for instead of admitting uncertainty. Where a field
    may genuinely be unset, the FIELD is declared Optional (-> None) on the
    model. Where a degree of confidence must be expressed, the explicit
    `EvidenceCertainty` enum is used, which distinguishes real uncertainty
    ("unconfirmed") from a value that was verified or strongly supported.
    "unknown" as a silent default is never used anywhere in this schema.

Design rule (separation of authority):
    Enums that encode REDACTORIAL truth (Voice Core status, Reader Effect
    categories, Repetition Risk catalogue, Style Option catalogue) are
    transcriptions of Fas 0A / Fas 0B findings. They must not be edited to
    change meaning without flagging the change to project management -- see
    docs/OPEN_QUESTIONS.md and docs/TECHNICAL_PROPOSALS.md for anything that
    was added for technical reasons rather than derived directly from the
    approved editorial material.
"""

from __future__ import annotations

from enum import Enum


class Actor(str, Enum):
    """Who or what produced a piece of data."""

    HUMAN = "human"
    AI_SYSTEM = "ai_system"
    IMPORT = "import"  # bulk/legacy data migration, not a live actor


class EvidenceCertainty(str, Enum):
    """
    How solid is a given piece of editorial data.

    Mirrors Beslut 23's required three-way split, plus an explicit
    "unconfirmed" state so that uncertainty is a first-class value rather
    than an absent field or a disguised default.
    """

    VERIFIED = "verified"
    STRONGLY_SUPPORTED = "strongly_supported"
    ANALYTICAL_PROPOSAL = "analytical_proposal"
    UNCONFIRMED = "unconfirmed"


class VoicePrincipleStatus(str, Enum):
    """
    Beslut 12: canonical vs. supported vs. analytical must never collapse
    into one bucket. This is the enum that keeps that distinction load-bearing
    in the data rather than only in documentation.
    """

    CANONICAL = "canonical"
    STRONGLY_SUPPORTED = "strongly_supported"
    ANALYTICAL_PROPOSAL = "analytical_proposal"
    DEPRECATED = "deprecated"  # TECHNICAL PROPOSAL: lifecycle exit for a principle later retired


class InputType(str, Enum):
    """Shape of the raw material an Idea originated from."""

    OBSERVATION = "observation"
    OVERHEARD = "overheard"
    QUOTE = "quote"
    QUESTION = "question"
    PATTERN_NOTE = "pattern_note"
    RESEARCH_SNIPPET = "research_snippet"
    PERSONAL_EXPERIENCE = "personal_experience"
    READER_REACTION = "reader_reaction"
    OTHER = "other"


class SourceType(str, Enum):
    BOOK = "book"
    STORY_BIBLE = "story_bible"
    RESEARCH = "research"
    EXPERIENCE = "experience"
    REVIEW = "review"
    COMMENT = "comment"
    PHOTOGRAPH = "photograph"
    INTERVIEW = "interview"
    MODEL = "model"
    WEBSITE = "website"
    PREVIOUS_CONTENT = "previous_content"


class SourceReliability(str, Enum):
    """Distinct from EvidenceCertainty: this rates the SOURCE, not a claim."""

    VERIFIED = "verified"
    STRONGLY_SUPPORTED = "strongly_supported"
    REPORTED = "reported"  # secondhand / not independently checked
    UNVERIFIED = "unverified"


class UsageRights(str, Enum):
    OWNED = "owned"
    LICENSED = "licensed"
    FAIR_USE_CLAIMED = "fair_use_claimed"
    PERMISSION_GRANTED = "permission_granted"
    RESTRICTED = "restricted"
    UNCLEAR = "unclear"


class SeriesRole(str, Enum):
    """
    Beslut 17: Series must never be conflated with topic / territory / form.
    This enum classifies WHAT KIND of editorial pillar a series is, so two
    series that look similar structurally aren't assumed to behave alike.
    """

    FORM_BEARING_PILLAR = "form_bearing_pillar"  # e.g. "Kaera ..." -- defined by a recurring form
    TIME_PERSPECTIVE = "time_perspective"  # e.g. "Det langa spelet" -- defined by temporal lens
    RECURRING_CHARACTER_OR_VOICE = "recurring_character_or_voice"
    THEMATIC_TRACK = "thematic_track"
    OTHER = "other"


class VariationDimension(str, Enum):
    """Beslut 10: the four axes that must never be collapsed into one."""

    CONTENT = "content"          # vad sager texten
    PERSPECTIVE = "perspective"  # vems verklighet betraktar vi
    FORM = "form"                # hur beraettas det
    EFFECT = "effect"            # vad ska/kan folja med lasaren


class StyleAttributeCategory(str, Enum):
    """Beslut 13: Style Options catalogue from Fas 0B, kept separate from Voice Core."""

    OPENING = "opening"
    STRUCTURE = "structure"
    RHETORICAL_DEVICE = "rhetorical_device"
    SCENE_OR_DIALOGUE = "scene_or_dialogue"
    FRAMING = "framing"
    ENDING = "ending"


class RepetitionSignalType(str, Enum):
    """Beslut 14: known repetition risks identified in Fas 0A / 0B."""

    SHORT_THESIS_OPENING = "short_thesis_opening"
    THESIS_PLUS_CONTRAST = "thesis_plus_contrast"
    TRIAD_OR_QUARTET = "triad_or_quartet"
    OPPOSING_PAIR = "opposing_pair"
    VISUALLY_STRUCTURED_FRAME = "visually_structured_frame"
    CLOSING_QUESTION = "closing_question"
    REPEATED_SHORT_LINE_RHYTHM = "repeated_short_line_rhythm"


class ReaderEffectCategory(str, Enum):
    """Beslut 15."""

    IMMEDIATE = "immediate"
    COGNITIVE = "cognitive"
    EMOTIONAL = "emotional"
    AFTEREFFECT = "aftereffect"


class ReaderEffectMode(str, Enum):
    """Beslut 15: intended vs. observed must stay distinguishable."""

    INTENDED = "intended"
    OBSERVED = "observed"


class FeedbackVerificationStatus(str, Enum):
    """Beslut 16: a reader reaction is evidence, not automatically canonical."""

    VERIFIED_VERBATIM = "verified_verbatim"
    PARAPHRASED = "paraphrased"
    UNVERIFIED = "unverified"


class NarrativeMode(str, Enum):
    SCENE = "scene"
    ARGUMENT = "argument"
    ANALYSIS = "analysis"
    LETTER = "letter"
    LIST = "list"
    DIALOGUE = "dialogue"
    OTHER = "other"


class PointOfView(str, Enum):
    FIRST_PERSON = "first_person"
    OBSERVER = "observer"
    SECOND_PERSON = "second_person"
    COLLECTIVE = "collective"
    OTHER = "other"


class LengthClass(str, Enum):
    SHORT = "short"
    MEDIUM = "medium"
    LONG = "long"


class RhythmPattern(str, Enum):
    UNIFORM = "uniform"
    MIXED = "mixed"
    STACCATO = "staccato"
    FLOWING = "flowing"


class EmotionalRegister(str, Enum):
    DISCOMFORT = "discomfort"
    RECOGNITION = "recognition"
    STILLNESS = "stillness"
    DIGNITY = "dignity"
    RELIEF = "relief"
    URGENCY = "urgency"
    OTHER = "other"


class DegreeLevel(str, Enum):
    """Generic low/medium/high scale used where Fas 0 material speaks in degrees,
    not numbers (e.g. personal_presence, solution_degree, contrast_usage)."""

    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class EndingType(str, Enum):
    UNRESOLVED_SCENE = "unresolved_scene"
    RESOLVED_SCENE = "resolved_scene"
    OPEN_QUESTION = "open_question"
    DIRECTIVE = "directive"
    REFLECTION = "reflection"
    OTHER = "other"


class CtaType(str, Enum):
    NONE = "none"
    IMPLICIT_REFLECTION = "implicit_reflection"
    EXPLICIT_QUESTION = "explicit_question"
    EXPLICIT_ACTION = "explicit_action"
    OTHER = "other"


class IdeaStatus(str, Enum):
    """Own lifecycle -- see docs/ARCHITECTURE_NOTE.md Beslut 19 rationale."""

    RAW = "raw"
    ANALYZED = "analyzed"
    CANDIDATE = "candidate"
    ANGLED = "angled"          # at least one Angle has been derived
    ON_HOLD = "on_hold"
    ARCHIVED = "archived"


class AngleStatus(str, Enum):
    PROPOSED = "proposed"
    SELECTED = "selected"
    REJECTED = "rejected"
    SUPERSEDED = "superseded"


class ContentStatus(str, Enum):
    """
    Own lifecycle, deliberately close to the shared vocabulary listed in
    Beslut 19, because CONTENT RECORD is the one object that genuinely
    passes through all of these stages in roughly this order.
    """

    DRAFT = "draft"
    QUALITY_REVIEW = "quality_review"
    REWORK = "rework"
    REANGLE = "reangle"
    HOLD = "hold"
    HUMAN_APPROVED = "human_approved"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class QualityAssessmentResult(str, Enum):
    PASS = "pass"
    REWORK = "rework"
    REANGLE = "reangle"
    HOLD = "hold"


class QualitySeverity(str, Enum):
    MINOR = "minor"
    MODERATE = "moderate"
    MAJOR = "major"
    BLOCKING = "blocking"


class ReturnPoint(str, Enum):
    """Where in the RAW INPUT -> ... -> HUMAN DECISION chain a failed
    Quality Assessment should send the work back to (Beslut 21)."""

    SOURCE = "source"
    IDEA = "idea"
    ANGLE = "angle"
    GENERATION = "generation"  # i.e. redo the content draft under the same angle
    HUMAN_REVIEW = "human_review"


class HumanDecisionType(str, Enum):
    APPROVE = "approve"
    REJECT = "reject"
    REWORK = "rework"
    REANGLE = "reangle"
    HOLD = "hold"
    PUBLISH = "publish"
    ARCHIVE = "archive"


class DecisionTargetType(str, Enum):
    """What kind of canonical object a HumanDecision or QualityAssessment
    can be attached to."""

    IDEA = "idea"
    ANGLE = "angle"
    CONTENT_RECORD = "content_record"
    QUALITY_ASSESSMENT = "quality_assessment"


class EditorialPotential(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class NoveltyRisk(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
