"""
Integration boundary toward the existing LUF Editorial Engine
(../editorial-engine, Canonical Foundation V1 + V1A/V1B/V1C).

Direktorder S21: Editorial Engine is a separate, already-working motor with
its own Human Authority and canonical data. This order does not touch it.
This module defines a Protocol describing the narrow surface Core Engine
would call, without importing anything from editorial-engine/ -- there is
no runtime coupling in either direction (see
tests/test_editorial_engine_independence.py).

Editorial Engine's own provenance model (editorial-engine/schema/
provenance.py, Actor/EvidenceCertainty) is structurally close to this
engine's schema/provenance.py by design -- both were built to the same
"null is better than invention" principle -- but the two modules are
independent and neither imports the other.
"""

from __future__ import annotations

from typing import Protocol


class EditorialEngineBoundary(Protocol):
    """
    What Core Engine would need FROM Editorial Engine, if a future adapter
    wires them together. Not implemented -- interface only, per Direktorder
    S21/S33 (no unrelated change to Editorial Engine in this order).
    """

    def get_content_record_summary(self, content_id: str) -> dict[str, str]:
        """Return a read-only summary of an editorial-engine ContentRecord, keyed by field name."""
        ...
