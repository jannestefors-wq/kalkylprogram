# Published Site Provenance Discovery -- 2026-08-20 (third pass)

Response to "Fortsatt order. Undersök ursprung utan att anta något." Goal:
find where the actual published LUF website is deployed from and who owns
its source -- using only what's inspectable in the systems this session
already has legitimate access to. No assumption that prior orders'
paths/hashes are true; no assumption that they're false either -- just
evidence.

## A. New environments/sources examined this pass

- `render.yaml`, `INSTALLERA.md`, `PUSHA_NU.bat`, `bygg_exe.bat`,
  `requirements.txt`, `.streamlit/config.toml` (root-level config/docs not
  previously read in full).
- `git log --all -S <term>` (pickaxe -- finds which commits ever
  added/removed a given string, across full history, not just current tree).
- `mcp__github__get_me` -- the authenticated GitHub identity's own profile
  (account age, public repo count, followers).
- Full-tree `git grep` for the S3 keyword list across all 7 branches
  (already-known branches, re-scanned specifically for these terms).

## B. Actual LUF trace hits (verbatim, all of them)

Every hit for `physical-house`, `CharacterRoom`, `Adam`, `Akademin`,
`Runda bordet`, `Dilemma Bank`, `Historical Idea Bank` etc. across all
branches and all history resolves to one of two categories -- **there were
no other hits**:

1. **This session's own documentation** (`luf-core-engine/docs/*`,
   `luf-system-recovery/*`) -- written by this session, so not new
   evidence of anything external.
2. **Editorial Engine's own historical audit documentation**
   (`editorial-engine/docs/ARCHITECTURE_NOTE.md`,
   `FINAL_REPORT.md`, `V1A_AUDIT_REPORT.md`, `V1A_DOES_NOT_DO.md`,
   `V1B_AUDIT_REPORT.md`, `V1B_DOES_NOT_DO.md`, `V1C_DOES_NOT_DO.md`,
   `V1C_STRUCTURAL_EVIDENCE_PACK.md`, `TECHNICAL_PROPOSALS.md`,
   `schema/voice.py`, `schema/json/VoiceCoreSnapshot.schema.json`) --
   written by an **earlier, independent session** (the one that produced
   commits `538729d` through `b8f004d`, before this session or the prior
   recovery sessions ever ran). These files record that session
   *also* being told to check for `physical-house.tsx`, `Adam`,
   `Akademin`, `Runda bordet`, and *also* finding nothing -- e.g.
   `V1A_AUDIT_REPORT.md:85`: "kontrollerat: inga träffar på `app/`, huset,
   Adam, `physical-house.tsx`" and `FINAL_REPORT.md:155`: "Repot innehåller
   ingen `physical-house.tsx`, Adam, ...". `git log --all -S
   "physical-house"` confirms exactly which commits introduced these
   mentions: `538729d`, `a1b68c8`, `bf9f8a5`, `2344e9f`, `37e643a`,
   `b8f004d` -- all Editorial Engine documentation commits, months before
   this order existed.

   **This is independent corroboration, not circular evidence**: a
   separate session, under presumably similar instructions, reached the
   same "not found" conclusion, on its own, at an earlier point in this
   project's history. `git log --all -S "CharacterRoom"`, `-S
   "leadershipwithoutfilter"`, and `-S "ledarskaputanfilter"` all return
   **zero commits** -- these exact terms have never appeared in this
   repository's history at all, not even in a doc-file mention.

## C. Deployment clues

`render.yaml` (repo root) is the only deployment configuration file found
anywhere in the repository:

```yaml
services:
  - type: web
    name: kalkylprogram
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true
```

This deploys **the Streamlit calculation tool** (`app.py`), service name
`kalkylprogram`. It contains no reference to a second service, a static
site, a Next.js app, a house, or Adam. `requirements.txt` lists only
`streamlit`, `pandas`, `openpyxl`, `reportlab` -- no web-framework
dependency (Next.js, React, etc.) that a house/room-based site would need.
`PUSHA_NU.bat` and `INSTALLERA.md` are both about this same calculation
tool, not a website.

**No second `render.yaml`, `vercel.json`, `netlify.toml`, `now.json`,
`.github/workflows/*deploy*`, `Dockerfile`, or any other deployment
descriptor exists anywhere in the repository.**

## D. Hosting clues

None found. No hosting-provider name, API token reference, or environment
variable template pointing at a hosting account exists anywhere in the
repository (beyond the `render.yaml` above, which is Render.com config for
the calculation tool).

## E. Git-provider clues

```
git remote -v   ->  origin  https://github.com/jannestefors-wq/kalkylprogram  (fetch/push)
```

Exactly one remote, exactly one provider (GitHub), exactly one repo. No
`.gitmodules`, no secondary remote ever configured (checked via
`PUSHA_NU.bat`, which explicitly does `git remote remove origin` then
re-adds the same single URL -- this script's whole purpose is pushing to
this one repo, nothing else).

`mcp__github__get_me` (the authenticated identity itself, independent of
any repo): account `jannestefors-wq`, **created 2026-03-13**, **1 public
repo**, 0 followers, 0 following, 0 gists. This is a small, young account
with no visible footprint beyond what this session already has access to
-- no organization membership surfaced, no additional public work.

## F. Domain references

None. A broad pattern search for `.se`/`.com`/`.io`/`.app`/`.net`-shaped
strings across the tracked tree returned only `jannestefors@gmail.com`
(an email address, not a domain reference) and Python attribute access
(`self.app`, a false-positive substring match, not a domain).
**No domain name for a published LUF website appears anywhere in this
repository.**

## G. Did `render.yaml` give relevant information?

**No.** It describes exactly one service (the calculation tool) and
nothing else. It is not evidence for or against a separately-hosted LUF
website -- it simply doesn't mention one.

## H. Can the website's source-location be verified?

**No.** Nothing inspectable from this session -- git history, git
remotes, deployment config, the GitHub account's own profile, or the
filesystem -- names, links to, or hints at where the published site's
source lives.

## I. Could any prior `/workspace` claim now be verified?

**No.** All four `/workspace/...` paths, both cited commit hashes, and all
eight cited artifact filenames remain exactly as reported in
`WORKSPACE_ENVIRONMENT_VERIFICATION.md` -- not found. This pass did not
re-run those checks (no new information changes their answer); it instead
searched an orthogonal set of clues (deployment/hosting/domain/git-provider),
which also came back empty.

## J. Classification of every previously-cited item

| Item | Classification | Basis |
|---|---|---|
| Kalkylprogram source, Editorial Engine source, LUF Core Engine source | **VERIFIED_IN_CURRENT_ENVIRONMENT** | Directly inspected, tested, restore-verified, twice |
| Editorial Engine's own historical "no house/Adam code" audit trail | **VERIFIED_IN_CURRENT_ENVIRONMENT** | Directly read in `editorial-engine/docs/`, an independent earlier session's own findings, git-blamed to specific commits |
| A real published LUF website exists somewhere (the order's own framing in this pass) | **EXTERNAL_BUT_PLAUSIBLE** | Cannot be confirmed or denied from here; no contradicting evidence either; entirely plausible a public site exists outside this account's GitHub footprint |
| `/workspace/sites/ledarskap-utan-filter-prototyp`, `/workspace/private/*` paths | **UNVERIFIED_PRIOR_REPORT** | Checked directly, twice; do not exist in any location this session can reach |
| Dilemma Bank V1 commit `86566842db2054d11b89cdf1bc8ae3ad840be64d` and files | **UNVERIFIED_PRIOR_REPORT** | Commit does not exist in the only relevant repo; files not found anywhere |
| Editorial Engine private commit `3b8271bb210d9509e891a53dbbb959b7e6e2436e` | **UNVERIFIED_PRIOR_REPORT** | Does not exist in the only relevant repo |
| "Historical Idea Bank" (4,589 / 4,544 SERIES / 45 TRIANGLE), "Verified Editorial History", "Private Bridge", "zero point 2026-08-19" | **UNVERIFIED_PRIOR_REPORT** | Phrases and figures appear nowhere in the repository; the only real, countable analog (Editorial Memory V1B) has 21 records under a different name |
| `app/physical-house.tsx`, `CharacterRoom.tsx`, `AcademyRoom.tsx`, `RoundTableRoom.tsx`, Adam state keys | **UNVERIFIED_PRIOR_REPORT** | Named as search leads by this order itself (correctly, per S2's "endast sökledtrådar" instruction); zero matches anywhere, including in an independent earlier session's own search for the same names |

## K. What is still actually verified and owned

Unchanged from the prior two passes: Kalkylprogram, LUF Editorial Engine
(336 tests), LUF Core Engine (31 tests) -- all git-tracked in
`jannestefors-wq/kalkylprogram`, all backed up in the delivered bundle
(SHA-256 `3f5fca5356f5b4cb401a7e749b011c64a94f41db7f19047f1d8865748a9952ea`),
all restore-verified twice.

## L. Exactly one recommended next step

**Ask the project owner directly for the published LUF website's live
URL** (if one currently exists). This session cannot guess or generate
that URL, but if given it, a fresh session can fetch the live page and
inspect its response headers, HTML source, and any linked asset domains
for hosting-provider fingerprints (Vercel/Netlify/Wix/custom
server/etc.) -- an entirely different, external evidence path that
doesn't depend on this GitHub account containing the source at all, and
would tell us for certain whether a live site exists and roughly where
it's served from, without requiring any repository access.
