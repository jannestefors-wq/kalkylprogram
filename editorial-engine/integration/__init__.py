"""Editorial Engine V1 Integration (EDITORIAL_ENGINE_V1_INTEGRATION_CONTRACT.md).

Connects the three already-established, independently frozen components --
V1A Editorial Judgment (`engine/`), V1B Editorial Memory (`memory/`), V1C
Controlled Variation (`variation/`) -- into one advisory, human-terminated
flow. This package adds ONLY the connective layer: it imports V1A/V1B/V1C
for reuse and never edits their modules, models, or decision logic.
"""
