# Approved Source (read-only reference)

`LUF_Editorial_Memory_Data_Pack_V1B.json` in this directory is a pristine,
never-edited copy of the exact data pack project leadership approved for
the original V1B order.

It exists ONLY so `tests/test_v1b_verbatim.py` has a permanent,
repo-local, portable file to check the live ingestion pack
(`memory/data/LUF_Editorial_Memory_Data_Pack_V1B.json`) against -- so a
future silent-normalization regression (the defect V1B Final Audit found:
`docs/V1B_AUDIT_REPORT.md`) fails a test instead of passing silently.

**Never edit this file.** If Work delivers a corrected or expanded data
pack in a future order, that becomes a NEW approved source (replace this
file entirely and note it in the corresponding order's correction
report) -- never hand-patch it.
