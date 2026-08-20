"""
Explicit gap sentinels (Direktorder S5: "fabricera inte... anvand explicit
UNKNOWN/UNVERIFIED"). Free-text fields across this schema default to one of
these two literal strings rather than to None, so a data gap is greppable
and shows up identically in JSON exports, not just in Python-side Optionals.

UNKNOWN     -- the fact itself was not stated by any source we have.
UNVERIFIED  -- a candidate value exists but has not been checked against an
               independent, named LUF source document.
"""

from __future__ import annotations

UNKNOWN = "UNKNOWN"
UNVERIFIED = "UNVERIFIED"
