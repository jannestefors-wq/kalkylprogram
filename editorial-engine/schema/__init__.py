"""
Canonical Editorial Schema V1 -- LUF Editorial Engine.

This package is the CANONICAL SCHEMA (source of truth). It is intentionally
isolated from the rest of this repository (the "kalkylprogram" house app)
and has no import relationship with it in either direction.

Do not import anything from outside `editorial-engine/` into this package,
and do not import this package from the house app.

See docs/ARCHITECTURE_NOTE.md for the rationale.
"""

SCHEMA_VERSION = "1.0.0"

from .angle import Angle  # noqa: E402
from .content import (  # noqa: E402
    ContentForm,
    ContentRecord,
    ContentWhat,
    VariationFingerprint,
    build_variation_fingerprint,
)
from .decision import HumanDecision  # noqa: E402
from .idea import Idea, IdeaInterpretation  # noqa: E402
from .provenance import Provenance  # noqa: E402
from .quality import QualityAssessment, QualityRuleFinding  # noqa: E402
from .raw_input import RawInput  # noqa: E402
from .reader_effect import ReaderEffect, ReaderEffectAssociation, ReaderFeedback  # noqa: E402
from .series import Series, ThesisFamily  # noqa: E402
from .source import Source  # noqa: E402
from .territory import Territory  # noqa: E402
from .voice import RepetitionSignal, StyleAttribute, VoiceCoreSnapshot, VoicePrinciple  # noqa: E402

__all__ = [
    "SCHEMA_VERSION",
    "Angle",
    "ContentForm",
    "ContentRecord",
    "ContentWhat",
    "VariationFingerprint",
    "build_variation_fingerprint",
    "HumanDecision",
    "Idea",
    "IdeaInterpretation",
    "Provenance",
    "QualityAssessment",
    "QualityRuleFinding",
    "RawInput",
    "ReaderEffect",
    "ReaderEffectAssociation",
    "ReaderFeedback",
    "Series",
    "ThesisFamily",
    "Source",
    "Territory",
    "RepetitionSignal",
    "StyleAttribute",
    "VoiceCoreSnapshot",
    "VoicePrinciple",
]
