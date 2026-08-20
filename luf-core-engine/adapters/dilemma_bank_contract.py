"""
Integration boundary toward "Dilemma Bank V1" (Direktorder S22).

INVENTORY GAP: no Dilemma Bank source, schema, or data was found in any
repository accessible to the AI system building this (only
jannestefors-wq/kalkylprogram was in scope; a repo-wide search found no "dilemma bank"
code -- see docs/OWNERSHIP_AUDIT.md). This module therefore defines the
integration contract SHAPE the Direktorder asks for, without any concrete
wiring, and without moving or copying any Dilemma Bank data into this
repo (which would violate S22's provenance requirement even if the data
were available). Confirm the actual Dilemma Bank repository/location with
project management before implementing the concrete adapter.
"""

from __future__ import annotations

from typing import Protocol


class DilemmaBankBoundary(Protocol):
    """
    What Core Engine would need FROM Dilemma Bank, if a future adapter wires
    them together. Not implemented -- interface only.
    """

    def get_dilemma_summary(self, dilemma_id: str) -> dict[str, str]:
        """Return a read-only summary of a Dilemma Bank entry, keyed by field name."""
        ...
