"""
TERRITORY (V1.1, OQ-3 resolution).

Project management confirmed territory is a real editorial dimension of its
own -- distinct from topic (open, free text), series (a formal registry with
its own SeriesRole), and form (the FORM variation dimension). Beslut 17's
own example: "Makt" = territory, "Tillit" = topic, "Kara ..." = series.

`Territory` follows the exact same lightweight registry pattern as `Series`
and `ThesisFamily` (`schema/series.py`): a flat canonical list with
`active` + `Provenance`, no dedicated status enum. Per the V1.1 order
(Beslut 9: "atervanand befintliga canonical statusbegrepp dar de passar"),
introducing a new status enum here would create exactly the parallel status
model the order warns against, when the existing `active: bool` pattern
already fits territory's lifecycle (grows, occasionally retired -- never a
multi-stage workflow). See docs/TECHNICAL_PROPOSALS.md TP-8.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from .provenance import Provenance
from .versioning import SCHEMA_VERSION


class Territory(BaseModel):
    model_config = {"extra": "forbid"}

    territory_id: str
    schema_version: str = Field(default=SCHEMA_VERSION)
    name: str
    description: Optional[str] = None
    created_at: datetime
    provenance: Provenance
    active: bool = True
