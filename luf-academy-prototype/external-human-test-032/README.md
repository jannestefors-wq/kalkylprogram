# LMHM V3 EXTERNAL HUMAN TEST 032

Approved source: 1f90620de7a04ddc35df2e261901c4a8557dae6a.
Hosting-only branch: claude/lmhm-v3-external-human-test-032.
Only allowed Site: appgprj_6ab5217fc85481919c0e43389df3d793.
Never target production Site appgprj_6a6e4b91c1c8819185280adfe9882cf6.

The four copied server/content/fixture modules are byte-identical to approved source.
build-assets.mjs derives the UI from public-v3 and changes only access, test notice,
test feedback and management links. It removes role switching and local bootstrap.
No pedagogical reducer/content changes.

D1 contains five new ht032_* tables: control, session, state, history, feedback.
State writes use revision compare-and-swap plus history in an atomic batch.
Jan sees only explicitly shared LMHM moments and separate test feedback.
Admin gets status only. Participants cannot select another identity.
Reset increments an epoch, invalidates sessions and removes state/history/feedback.
Delete additionally revokes the link. Revoke preserves data but blocks all access.
Revoked links cannot be reactivated via reset.

LMHM032_ACCESS is a Sites secret containing 12 {id,name,role,hash} entries:
10 participants, one facilitator and one program_admin. Only SHA-256 token hashes
are stored. Generate 256-bit random invite tokens outside source files and provide
only in the authorized chat. Browser fragment is immediately removed from the
address bar; session cookies are HttpOnly, Secure, SameSite=Strict, eight hours.
POST requires same-origin JSON. Noindex, no-store and restrictive CSP apply.
This is pseudonymous synthetic testing, not production identity management.

Build assets: node external-human-test-032/build-assets.mjs
Sync: node external-human-test-032/sync-site.mjs ABSOLUTE_VERIFIED_SITE_CHECKOUT
Schema: apply schema.ts through the Site's Drizzle generator; never modify old migrations.
The Site repository retains its framework, bindings and migration journal.
Internet verification uses hidden stdin; it must never receive credentials in arguments.
Temporary verifier is removed from the final runtime access catalog after revocation testing.
The ten final slots are reset before handoff.

Checks: security.test.mjs, browser.test.mjs (1280 and 390 pixels),
internet-check.mjs (actual HTTPS service). Approved v2/v3 regression and book checks
remain in ../tests and ../scripts. Set LHM_BOOK_TXT and CHROMIUM_PATH as required.
No external email, mirror invitation or third-party data collection is implemented.
