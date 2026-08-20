# Integration Contract: LUF Core Engine <-> Editorial Engine

Direktorder S21. Editorial Engine (`../editorial-engine/`) is a separate,
already-working motor with its own Canonical Foundation, Human Authority,
and Historical Idea Bank / Verified Editorial History concepts. This order
does not touch it. This document defines the boundary; no code in either
engine imports the other (enforced by
`tests/test_editorial_engine_and_dilemma_bank_independence.py`).

## What Core Engine offers to Editorial Engine (future)

Editorial Engine's `IdeaInterpretation` (see `editorial-engine/schema/
idea.py`) already performs a human-subject / hidden-conflict / root-cause
reading of a raw idea -- structurally similar to what Core Engine's
`schema/claims.py` does generically. A future adapter could let an editor
apply a `TriangulationSession` (Core Engine) to an Editorial Engine `Idea`
as one more analysis lens, surfaced back as an `Angle` candidate. Not
implemented in this order.

## What Editorial Engine would offer to Core Engine (future)

`adapters/editorial_engine_contract.py` declares `EditorialEngineBoundary`,
a `Protocol` with one illustrative method,
`get_content_record_summary(content_id) -> dict[str, str]`, standing in for
"Core Engine can read a summary of an Editorial Engine content record
without importing Editorial Engine's models directly." No concrete
implementation is provided.

## Why a Protocol, not a shared base class

Editorial Engine's `Provenance`/`Actor`/`EvidenceCertainty` and Core
Engine's `Provenance`/`Actor`/`ToolConfidence` were built independently to
the same design principle ("null is better than invention") but are
deliberately NOT unified into one shared schema package. Editorial Engine's
Human Authority rules are about editorial judgment; Core Engine's are about
methodological canonicity. Collapsing them risks silently importing one
domain's assumptions into the other -- exactly the kind of unverified
equivalence Direktorder S13 forbids Claude from asserting on its own
authority.

## Status

Interface-only. No runtime coupling exists. Revisit once a concrete use
case (e.g. Tänkarstolen needing both engines in one session) is approved.
