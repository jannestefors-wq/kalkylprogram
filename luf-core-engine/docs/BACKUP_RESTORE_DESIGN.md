# Backup & Disaster Recovery Design -- LUF (Direktorder S30)

## Scope

Covers everything accessible to this session: `kalkylprogram.py`/`app.py`,
`editorial-engine/`, `luf-core-engine/`. Does **not** cover the public
website, Adam, House Engine, or Dilemma Bank -- their backup status is
`NOT_ASSESSABLE` (see `OWNERSHIP_AUDIT.md`), and no backup action was
taken or attempted for anything outside session scope.

## Primary backup mechanism (already in place)

The GitHub repository `jannestefors-wq/kalkylprogram` itself, with full git
history, IS the backup for source, canonical data (JSON is git-tracked, not
gitignored inside `editorial-engine/` and `luf-core-engine/` -- see each
directory's local `.gitignore` override), configuration, and documentation.
Every commit is a recoverable point in time.

## Gap: single point of failure on one GitHub account

A GitHub-only backup is a single point of failure if the account is lost,
suspended, or compromised. **Recommendation** (not implemented in this
order -- requires an owner decision about where a second copy lives):
periodically run `git bundle create luf-backup-<date>.bundle --all` and
store the bundle in storage the project owner controls independently of
GitHub (their own cloud drive, an external disk). A bundle is a single file
that can fully restore the repository, including all branches and history,
with `git clone luf-backup-<date>.bundle`.

## Secrets

None found anywhere in the accessible repository (grep for
`anthropic|claude|openai|api[_-]?key` across all `.py` files: zero matches;
filename search for `.env`/`secret`/`credential`: zero matches).
`.gitignore` already excludes `.env`. Nothing to back up separately today;
if secrets are introduced later, they must NOT go into git and need their
own backup mechanism (e.g. a password manager or secrets vault), documented
separately when that need arises.

## Restore Test (Direktorder S30: "Backup utan verifierad restore är inte
## tillräckligt")

Performed this session, safely, into an isolated scratch directory --
**no production system was touched.**

Procedure: `git clone` the repository at its current commit into a fresh
directory, install each component's declared dependencies from
`requirements.txt`, run each component's test suite, confirm green.

Result: see `docs/RESTORE_TEST_RESULT.md` for the actual command output
captured this session (commit hash, pass counts, timestamp).

**This proves**: source + canonical data + tests can be fully reconstructed
from the git repository alone, with no dependency on this Claude session,
using only `pip` and public PyPI packages.

**This does NOT prove**: recovery of the public website, Adam, House
Engine, or Dilemma Bank -- out of scope, not attempted (S30: "Gör ingen
riskabel återställning över produktion" also means: don't extend a restore
test into systems this session doesn't understand well enough to touch
safely).

## Restore path, summarized

1. `git clone https://github.com/jannestefors-wq/kalkylprogram.git`
2. `cd kalkylprogram/editorial-engine && pip install -r requirements.txt &&
   python3 -m pytest -q`
3. `cd ../luf-core-engine && pip install -r requirements.txt && python3 -m
   pytest -q`
4. `cd .. && pip install pandas openpyxl reportlab` (for the calculation
   tool; no test suite exists for it today -- see Known Blockers in the
   manifest as a future gap, not one this order was asked to close).

If all pass, the repository has been proven self-sufficient for restore.
