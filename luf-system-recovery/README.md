# LUF System Recovery -- 2026-08-20

Deliverables for Direktorder "LUF SYSTEM RECOVERY & OWNERSHIP
CONSOLIDATION" (2026-08-20). This is a discovery/ownership audit, not new
functionality -- nothing here changes the public website, Adam, House
Engine, Editorial Engine, or LUF Core Engine's methodology.

## Read in this order

-2. `PUBLISHED_SITE_TECHNICAL_INSPECTION.md` -- a fourth pass (2026-08-20)
    attempting live technical inspection of the two published URLs given
    by the project owner (ledarskaputanfilter.se, leadershipwithoutfilter.com).
    Blocked at the network layer by this session's egress policy (confirmed
    two independent ways); no HTTP request to either host completed.
-1. `PUBLISHED_SITE_PROVENANCE_DISCOVERY.md` -- a third pass (2026-08-20)
    that stops treating prior orders' paths/hashes as evidence either way
    and instead searches deployment config, git remotes, domain
    references, and the GitHub account's own profile for where the
    published LUF website's source and hosting actually come from.
    Classifies every previously-cited item as
    VERIFIED_IN_CURRENT_ENVIRONMENT / EXTERNAL_BUT_PLAUSIBLE /
    UNVERIFIED_PRIOR_REPORT. Also surfaces genuinely new corroborating
    evidence: an earlier, independent session (predating any recovery
    order) already searched for and failed to find the same house/Adam
    material, recorded in Editorial Engine's own audit docs.
0. `WORKSPACE_ENVIRONMENT_VERIFICATION.md` -- a second, deeper pass
   (2026-08-20) checking specific `/workspace/...` paths, commit hashes,
   and artifact filenames named by a follow-up order, plus a direct check
   of this account's entire Claude Code Remote session/environment history
   to see whether persistent private LUF data could exist anywhere this
   account's sessions can reach. Conclusive: no session on this account,
   ever, has had access to anything beyond the two repos already covered
   below.
1. `DISCOVERY_LOG.md` -- exact commands run and their results (the
   evidence base for everything else here).
2. `LUF_SYSTEM_MAP.md` (+ machine-readable `LUF_SYSTEM_MAP.json`) -- what
   was found, where, and what wasn't.
3. `LUF_OWNERSHIP_MATRIX.md` -- the required component x ownership-question
   matrix.
4. `SINGLE_POINTS_OF_FAILURE.md` -- ranked risks among what's accessible.
5. `CLAUDE_INDEPENDENCE_ASSESSMENT_FULL_LUF.md`, `PROVIDER_INDEPENDENCE.md`.
6. `BACKUP_BUNDLE_RECORD.md`, `RESTORE_TEST_RESULTS.md` -- the verified
   git bundle (delivered directly to the project owner) and both restore
   tests.
7. `BYGGLEDNING_RELEVANCE.md` -- the one other repo on this account,
   confirmed unrelated to LUF.

## Headline result

Everything this session's GitHub access and container filesystem could
reach (Kalkylprogram, Editorial Engine, LUF Core Engine) is verified,
tested, and now backed up outside GitHub. Everything the order asked about
beyond that -- the public website, Physical House, Adam, House Engine,
Academy, Round Table, Dilemma Bank V1, and the specific "Historical Idea
Bank"/"Verified Editorial History" data layers -- was searched for
specifically and not found in any repository or location reachable this
session. Per the order's own hard rule (S26), none of it was rebuilt.
