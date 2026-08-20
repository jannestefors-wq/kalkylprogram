# Backup Bundle Record -- 2026-08-20

Direktorder S21. One relevant, exportable Git repository was found under
project control: `jannestefors-wq/kalkylprogram` (contains Kalkylprogram,
Editorial Engine, and LUF Core Engine -- all three live in one repo's
history, so one bundle covers all of them). `jannestefors-wq/byggledning`
was NOT bundled -- confirmed `NOT_LUF_RELEVANT`, out of this order's scope.

## Bundle

| Field | Value |
|---|---|
| Source repo | `jannestefors-wq/kalkylprogram` |
| Command | `git bundle create <file> --all` |
| Refs included | 10 (`main`, `claude/luf-core-engine-v1-p3uws7`, and their `origin/*` counterparts, plus the 5 stale pre-squash Editorial Engine branches and `HEAD`) |
| Verification | `git bundle verify` -> "the bundle records a complete history" |
| Size | 636,462 bytes |
| SHA-256 | `3f5fca5356f5b4cb401a7e749b011c64a94f41db7f19047f1d8865748a9952ea` |
| Created at commit | `a2be2b37e5479b741cf476bf38f488dbb6d1fd64` |
| Restore test | `git clone <bundle>` into an isolated scratch directory, then `editorial-engine` (336/336) and `luf-core-engine` (31/31) test suites both green -- see `RESTORE_TEST_RESULTS.md` |
| Delivery | Sent directly to the project owner via this session's file-transfer channel, 2026-08-20 |
| Stored in this repo? | No -- deliberately not committed (would duplicate GitHub's own history storage without adding real disaster-recovery value; see BACKUP_RESTORE_DESIGN.md in luf-core-engine/docs/ for the reasoning) |
| External storage confirmed? | **NOT YET** -- the project owner must save the delivered file somewhere independent of both GitHub and this Claude session (own drive, external disk, cloud storage they control) for this to count as true disaster recovery, not just a second copy in the same account's reach |

## Why this matters

Before this bundle, `kalkylprogram` had exactly one location: GitHub,
under one account. A full, verified, restorable copy now also exists
outside GitHub, in the project owner's hands directly -- closing the
CRITICAL/HIGH single-point-of-failure item raised in
`SINGLE_POINTS_OF_FAILURE.md`, conditional on where the owner stores it
next.

## Not done, and why

- **`byggledning` was not bundled.** Confirmed not LUF-relevant (S25); this
  order scopes bundling to relevant repos (S21) so it was left alone.
- **No cloud storage upload was performed.** This session has no
  established, owner-approved cloud storage target; delivering the file
  directly to the owner was the safest available action without guessing
  at infrastructure that doesn't exist yet.
