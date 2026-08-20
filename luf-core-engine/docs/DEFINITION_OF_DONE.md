# Definition of Done -- Global LUF Engineering Principle

Established by Direktorder LUF Core Engine V1 (2026-08-20), S31. Applies to
every LUF deliverable from this date forward, not only luf-core-engine/.

> A feature is not done because it works. It is done when relevant parts of
> the following all exist:
>
> **SOURCE + DATA + TEST + DOCUMENTATION + BACKUP + RESTORE PATH + OWNERSHIP**

| Element | Meaning |
|---|---|
| SOURCE | Code lives in a repository the project owner controls, not only in a chat session. |
| DATA | Any data the feature depends on is stored in the owner's own structure, with provenance. |
| TEST | Automated tests exist and pass, proving the behavior, not just describing it. |
| DOCUMENTATION | A developer without access to the building AI session can understand and operate it. |
| BACKUP | The source and data have a defined, reproducible backup path. |
| RESTORE PATH | It is documented (and where safe, demonstrated) how to rebuild the system from that backup. |
| OWNERSHIP | No part of the delivery requires a specific AI vendor, person, or external service to keep existing. |

"Relevant parts" means: not every feature needs a disaster-recovery drill,
but every feature must be able to explain, in one sentence each, how each
element applies or explicitly does not apply to it.
