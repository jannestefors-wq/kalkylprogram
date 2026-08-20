# LUF System Map -- 2026-08-20

Human-readable companion to `LUF_SYSTEM_MAP.json` (Direktorder "LUF System
Recovery & Ownership Consolidation", S16). Read `DISCOVERY_LOG.md` for the
exact commands behind every claim here.

## What this session could reach

- GitHub: `jannestefors-wq/kalkylprogram` (full read/write, this session's
  primary scope) and `jannestefors-wq/byggledning` (read, added this
  session specifically to check LUF relevance per S25).
- Local container filesystem: `/home`, `/root`, `/workspace`, `/mnt`,
  `/var`, `/tmp` -- a fresh container with only `kalkylprogram` pre-cloned;
  no `/workspace/private`, no prior exports, no bundles, no backup folders
  existed before this session created them.
- All 7 branches of `kalkylprogram` (`main`, this session's
  `claude/luf-core-engine-v1-p3uws7`, and 5 stale pre-squash Editorial
  Engine feature branches) were fetched and searched.

**No other repository, hosting account, database, or external system was
reachable.** This is the single fact that shapes almost every status below.

## Verified and owned

| Component | Where | Status |
|---|---|---|
| Kalkylprogram (Bygg & Entreprenad) | `kalkylprogram/kalkylprogram.py`, `/app.py` | VERIFIED |
| LUF Editorial Engine (V1, V1A, V1B, V1C) | `kalkylprogram/editorial-engine/` | VERIFIED, 336/336 tests, restore-tested twice |
| Editorial Memory (V1B) | `editorial-engine/memory/` | VERIFIED -- **21 records**, not the 4,589 cited by this order (see Discrepancies below) |
| LUF Core Engine V1 Foundation | `kalkylprogram/luf-core-engine/` | VERIFIED, 31/31 tests, restore-tested twice, branch `claude/luf-core-engine-v1-p3uws7` |
| Canonical Tool Registry | `luf-core-engine/canonical_data/` | PARTIAL -- structure owned, content still 30/30 UNVERIFIED candidates, 0 improved this session |

## Not accessible (genuinely unknown, not "missing")

| Component | Search performed | Result |
|---|---|---|
| Public LUF website | Filename search for `app/physical-house.tsx`, `app/content/house-memory.ts`, `app/components/CharacterRoom.tsx`, `app/components/AcademyRoom.tsx`, `app/components/RoundTableRoom.tsx` across all 7 branches + local filesystem | Zero matches |
| Physical House | Same search (website is presumed host) | Zero matches |
| Adam | Search for `luf-adam-journey`, `luf-journey-adam-001`, and the word "Adam" (word-boundary) across repo + filesystem | Zero matches |
| House Engine | Same as website -- per S7, reported as `DISTRIBUTED_FUNCTIONALITY`, not `MISSING`, since the underlying house logic may live inside the (unreached) website code | Cannot confirm either way |
| Akademin (Academy room) | `AcademyRoom.tsx` filename search | Zero matches |
| Runda bordet (Round Table room) | `RoundTableRoom.tsx` filename search | Zero matches |
| Dilemma Bank V1 | Commit `86566842db2054d11b89cdf1bc8ae3ad840be64d` looked up directly (`git cat-file -t`) after fetching every remote branch; filename search for `LUF_DILEMMA_BANK_CANDIDATES_V1.json`, `_APPROVED_V1.json`, `_V1_REPORT.md`, `_V1_VALIDATION.json` | Commit not found; zero file matches |

**Note on `byggledning`**: this repo was checked per S25 and ruled
`NOT_LUF_RELEVANT` -- it is a construction-site management tool
("Byggledning och garantiärenden -- mobilt arbetsnav för byggledare"),
confirmed by README, `package.json`, and a full keyword grep (zero hits for
luf/dilemma/adam/house/tänkarstolen). No further action taken on it.

## Discrepancies vs. this order's cited "previously verified" facts

These are reported, not resolved -- S9 requires investigating a mismatch
before drawing a conclusion, which is what follows:

1. **"4,589 Historical Idea Bank units"** -- no file, docstring, README, or
   commit message anywhere in the searched scope uses the phrase
   "Historical Idea Bank". The only real, countable content-unit corpus
   found is Editorial Memory (V1B): **21 records**
   (`editorial-engine/memory/data/LUF_Editorial_Memory_Data_Pack_V1B.json`,
   counted directly this session). 21 and 4,589 cannot both describe the
   same corpus in the same repository.
2. **"Verified Editorial History"** and **"Private Bridge"** -- neither
   phrase appears anywhere in `editorial-engine/`. The closest real
   analogs are `EvidenceCertainty`/`VoicePrincipleStatus` (evidence tiers)
   and `memory/bridge.py` (a V1B-to-V1A technical adapter, not a named
   cross-engine bridge to Dilemma Bank).
3. **Dilemma Bank V1's cited commit** does not exist in this repository's
   history, on any of its 7 branches, after a full fetch.
4. **The public website, Physical House, Adam, House Engine, Academy,
   Round Table** -- none locatable under the cited names, paths, or state
   keys anywhere this session could search.

**Conclusion offered, not asserted as fact**: either these components live
in a repository, hosting account, or export this session's GitHub
connector was never given access to (most likely, given the account only
exposes 2 repositories total), or the specific figures/hashes/paths cited
came from material this session cannot independently verify. Both are
real possibilities; only the project owner can resolve which. See
`AR`/next-step recommendation in the final report.

## What this session did NOT do

- Did not build a new website, Adam, House Engine, or Dilemma Bank to fill
  the gap (Direktorder S26, hard rule).
- Did not merge Historical Idea Bank and Verified Editorial History into
  one tier (Direktorder S11).
- Did not promote any Tool Registry candidate (still 0/30 approved).
- Did not modify Editorial Engine, Core Engine methodology, or any public
  surface.
