"""
Versioning strategy (Beslut 22).

Three independent things can each evolve on their own timeline:
    1. The CANONICAL EDITORIAL SCHEMA itself (this codebase's shape).
    2. The VOICE CORE (which principles are canonical / supported, their
       definitions).
    3. Registries that grow without changing shape: Series Registry,
       Thesis Family Registry, Reader Effect taxonomy, Repetition Signal
       catalogue, Style Attribute catalogue.

Strategy (kept deliberately simple -- "undvik overengineering"):

    - SCHEMA_VERSION (schema/__init__.py) is a single semver string for the
      whole canonical schema package. Every record that is schema-shaped
      (i.e. every top-level canonical object) carries a `schema_version`
      field stamped at creation time with the SCHEMA_VERSION that was in
      effect. This answers "which contract was this analysed/generated
      under" even after the schema moves on.

    - VOICE CORE is versioned separately, because it changes for editorial
      reasons on its own schedule, not because the data shape changed. Each
      VoicePrinciple carries its own `version` + `valid_from` (Beslut 11).
      A ContentRecord / QualityAssessment additionally stamps
      `voice_core_version_ref`, a free string like "voice-core-1.0", so we
      can always answer "this text was judged against Voice Core 1.0" even
      after individual principles are edited or added later. There is no
      single global "Voice Core version number" object in V1 -- the
      version reference is a label convention (see docs/VERSIONING_STRATEGY.md),
      not a new canonical entity, to avoid a second source of truth that
      could drift from the principle records themselves.

    - Registries (Series, Thesis Family, Reader Effect definitions,
      Repetition Signal, Style Attribute) are NOT globally versioned as a
      set. Each row carries its own `status` + `created_at` (and
      `superseded_by` where relevant). Growth is expected and is not a
      breaking change; only a change in an existing row's *meaning* is
      (and that must be flagged, see docs/OPEN_QUESTIONS.md).

    Rule of thumb: version the CONTRACT (schema) and the EDITORIAL TRUTH
    (voice core) explicitly, because both are things a past record must be
    checked against later. Do not version things that only grow.
"""

from __future__ import annotations

SCHEMA_VERSION = "1.0.0"
"""Re-exported from schema/__init__.py for convenient importing from model
modules without a circular import back through the package __init__."""
