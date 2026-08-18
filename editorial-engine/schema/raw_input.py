"""
RAW INPUT immutability (Beslut 5).

`RawInput` is its own top-level entity, not an embedded string field on
`Idea`, even though Beslut 6 lists `raw_input` among Idea's minimum fields.
This is a deliberate, flagged normalization (permitted by Beslut 6: "Du far
normalisera eller dela upp detta tekniskt om det ger battre dataintegritet").

Why: if `raw_input` were a plain string field living on the same record that
also carries the AI's interpretation, nothing in the data model stops a
future write from overwriting it "by mistake" during a re-analysis. Making
it a separate, append-only entity (referenced by `Idea.raw_input_id`) means
the interpretation literally cannot be saved over the original text -- they
are different rows. `IdeaInterpretation` (see idea.py) is the mutable/
versionable side; `RawInput` never changes after creation.

`content_hash` is a technical addition (TECHNICAL PROPOSAL, see
docs/TECHNICAL_PROPOSALS.md) used only by tests to assert byte-for-byte
immutability -- it carries no editorial meaning.
"""

from __future__ import annotations

import hashlib
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, model_validator

from .enums import InputType
from .versioning import SCHEMA_VERSION


class RawInput(BaseModel):
    model_config = {"extra": "forbid", "frozen": True}  # frozen: immutable after construction

    raw_input_id: str
    schema_version: str = Field(default=SCHEMA_VERSION)
    captured_at: datetime
    text: str = Field(description="Verbatim material exactly as it was received. Never edited in place.")
    input_type: InputType
    origin_note: Optional[str] = Field(
        default=None, description="Freeform note on who/where this came from, e.g. 'Janne, observation from meeting'."
    )
    language: str = Field(description="ISO 639-1 code, e.g. 'sv', 'en'.")
    content_hash: str = Field(
        default="",
        description="sha256 of `text`, computed at construction. Used only to let tests detect "
        "accidental mutation; carries no editorial meaning.",
    )

    @model_validator(mode="after")
    def _stamp_hash(self) -> "RawInput":
        if not self.content_hash:
            object.__setattr__(self, "content_hash", hashlib.sha256(self.text.encode("utf-8")).hexdigest())
        return self
