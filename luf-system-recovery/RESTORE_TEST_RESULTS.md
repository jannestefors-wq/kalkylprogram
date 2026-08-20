# Restore Test Results -- 2026-08-20

Direktorder S22: safe, isolated restore tests only, never over production.
Both tests below ran in ephemeral scratch directories, deleted immediately
after; nothing was restored over `/home/user/kalkylprogram`.

| Component | Test performed | Result |
|---|---|---|
| Kalkylprogram + Editorial Engine + LUF Core Engine (live GitHub clone) | `git clone` from the live repo into scratch, install deps, run both test suites, compile the calculation tool | RESTORE_VERIFIED -- 336 + 31 tests passed, both files compile (repeat of the test from the prior session, re-confirmed) |
| Kalkylprogram + Editorial Engine + LUF Core Engine (from the new git bundle) | `git clone <bundle-file>` into a separate scratch dir, install deps, run both test suites | RESTORE_VERIFIED -- 336 + 31 tests passed. This is the stronger test: it proves the bundle itself (not just GitHub) is a working restore artifact. |
| Website / Physical House / Adam / House Engine / Academy / Round Table | n/a | RESTORE_BLOCKED -- nothing to test; component not located |
| Dilemma Bank V1 | n/a | RESTORE_BLOCKED -- cited commit not found in any reachable repository; nothing to test |
| "Historical Idea Bank" (4,589 units) | n/a | RESTORE_BLOCKED -- not located; see discrepancy note in `LUF_SYSTEM_MAP.md` |
| `byggledning` | Not attempted | RESTORE_NOT_TESTED -- out of scope, not LUF-relevant |

## Commands (for reproducibility)

```bash
# Live clone
git clone /home/user/kalkylprogram <scratch>/live-clone
cd <scratch>/live-clone/editorial-engine && pip install -r requirements.txt && python3 -m pytest -q
cd ../luf-core-engine && pip install -r requirements.txt && python3 -m pytest -q

# Bundle clone
git clone <scratch>/luf-kalkylprogram-full-20260820-a2be2b3.bundle <scratch>/restored
cd <scratch>/restored/editorial-engine && pip install -r requirements.txt && python3 -m pytest -q
cd ../luf-core-engine && pip install -r requirements.txt && python3 -m pytest -q
```

Both scratch directories were removed after the tests completed.
