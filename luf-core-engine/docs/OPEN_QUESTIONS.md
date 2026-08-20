# Open Questions -- LUF Core Engine V1 Foundation

Flagged for Human Review / project management, per Direktorder S13. None of
these are answered by this delivery -- they are structural gaps that the
Foundation is built to hold explicitly, not to paper over.

## OQ-1: Where does the actual LUF source corpus live?

Direktorder S6/S7 ask for an inventory verified "mot källorna" (against the
sources). No such corpus -- original workshop documents, books, slide decks,
prior tool registries -- was found in any repository accessible to this
session (only `jannestefors-wq/kalkylprogram`). `canonical_data/source/
inventory_candidates.json` therefore only contains what the Direktorder text
itself stated, marked UNVERIFIED. **Action needed:** point Core Engine at
the real source corpus (a repo, a document store, a folder) before any
Human Review of these candidates can meaningfully happen.

## OQ-2: `luf-tool-0009` -- "Syfte • Påhöraren • Budskap"

"Påhöraren" was preserved verbatim from the Direktorder text. It may be a
typo for "Åhöraren" (the listener), which would make more sense next to
"Syfte" (purpose) and "Budskap" (message) as a communication triad. Not
corrected, because correcting spelling based on a guess is itself a form of
fabrication under S5. **Action needed:** confirm the intended spelling
against source material.

## OQ-3: `ZoomLevel` taxonomy (schema/enums.py, schema/zoom.py)

The individual → relation → team → process → verksamhet → culture → system
sequence in Direktorder S10 is used as-is in `ZoomLevel`, but every
`ZoomFrame.level_taxonomy_status` is hard-set to
`UNVERIFIED_PENDING_HUMAN_REVIEW` and frozen so no code path can silently
promote it. **Action needed:** Human Review of the level taxonomy itself
against source material, independent of any individual ZoomFrame usage.

## OQ-4: Framework acronyms (RACE, RISE, STAR, SOAP, CLEAR, GROW, PASTOR)

Direktorder S7 lists these as *candidates to inventory if verified LUF
material exists*. None was found. These acronyms have well-known generic
meanings in the broader coaching/leadership industry (e.g. GROW = Goal,
Reality, Options, Will), but populating `components`/`purpose` from that
generic meaning would misrepresent industry-generic content as verified
LUF-specific material -- exactly what S7 forbids. All seven entries are
therefore `HISTORICAL_LUF_MATERIAL` / `UNVERIFIED` with every field but the
name left `UNKNOWN`. **Action needed:** either supply the LUF-specific
source material for these, or confirm they should be removed from the
inventory as not actually LUF tools.

## OQ-5: Website, Tänkarstolen, Runda bordet, Akademin, Dilemma Bank, House
Engine, Adam -- repository location

None of these exist in any repository accessible to this session. See
`OWNERSHIP_AUDIT.md` and `CLAUDE_INDEPENDENCE_ASSESSMENT.md`. **Action
needed:** project management must identify and grant access to the actual
repositories/hosting for the public website, Adam, House Engine, and
Dilemma Bank before their ownership can be audited or their integration
contracts implemented beyond the interface-only stubs in `adapters/`.

## OQ-6: `byggledning` repository

A second private repository owned by the same GitHub account,
`jannestefors-wq/byggledning`, was discovered via the repository listing
tool but was NOT opened or inventoried -- its name suggests construction
project management, unrelated to LUF, and opening it was outside this
order's scope. **Action needed:** confirm with the owner whether this repo
is relevant to LUF (e.g. hosts the website) before it is either included in
or definitively excluded from future LUF ownership audits.
