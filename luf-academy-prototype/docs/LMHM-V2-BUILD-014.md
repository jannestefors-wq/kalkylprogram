# LMHM version 2. Build 014

## Utgångsläge, dokumenterat före första kodändringen

| | |
|---|---|
| Gren | `claude/ledarskap-vecka-1-prototype-7sy98p` |
| Commit | `0242434` Fix optimistic concurrency for existing journey entries. Samma som fjärrgrenen och handoff v2 |
| Source of Truth, kod | `luf-academy-prototype/` i jannestefors-wq/kalkylprogram |
| Source of Truth, innehåll | LMHM VERSION 2 FINAL CONTENT SPEC (order 013), sparad ordagrant i `docs/LMHM-V2-FINAL-CONTENT-SPEC.md` |
| Datamodell | lr_program, lr_cohort, lr_live_session, lr_user, lr_role_grant, lr_enrollment (+ test_step), lr_entry, lr_entry_history, lr_self_assessment, lr_share, lr_one_on_one, lr_auth_session, lr_prototype_login, lr_event, lr_admin_audit |
| Teststatus | api 35 av 35, e2e 8 av 8, förhandsvisning 10 av 10. Bokkontroll 108 godkända, 0 fel |

Arbetsgren för version 2: `claude/lmhm-v2-build-014`, skapad från 0242434.

## Vad som byggts

- Innehållsregistret (`server/content.mjs`) följer specifikationen: startsamtal, vecka 1 till 6, 30 dagar, återträff, Samtal med Jan.
- Gemensam motor: Vilket av mina förändringsområden, med deltagarens egna ord och Något nytt. Vad hände? med Ja, Delvis och Nej. Nej räknas som klart med Vad stoppade dig? och Vad gör du nu?.
- Villkorade fält (`showWhen`, `hintWhen`). Klarstatus räknar bara fält som syns (`server/rules.mjs`).
- Privat vägledning efter två Nej i rad. Räknas fram ur deltagarens egna svar, bara i deltagarens egen vy. Ingenting registreras när rutan visas.
- Be om ett samtal. Enda vägen till Jan. Bara namn, grupp och tidpunkt.
- Integritet: Jan ser bara aktivt delat material och samtalsförfrågningar. Admin ser grupper, datum, deltagare, status, påbörjade veckor och träffar. Startsamtal och samtal ger inga händelser.
- Additiv migration 0003. Inga befintliga svar ändras. Se `docs/LMHM-V2-FIELD-MAP.md`.
- Bokkontrollen klarar avsnitt inom kapitel och kräver inte längre den gamla trygghetsfrågan, men kontrollerar att bokens fråga finns kvar på s. 60 och att Relation och Utveckling fortfarande verifieras.
- Egen förhandsvisning: `preview/dist/lmhm-v2-human-test.html`, publicerad som en ny privat artefakt.

## Tester

| Svit | Antal | Resultat |
|---|---|---|
| `tests/api.test.mjs` (tidigare regressionstester, anpassade till nya nycklar) | 35 | 35 godkända |
| `tests/v2.test.mjs` (flöden, villkor, två Nej, samtal, integritet, migration) | 25 | 25 godkända |
| `tests/content.test.mjs` (maskinell kontroll mot specifikationen) | 6 | 6 godkända |
| `tests/e2e.test.mjs` (webbläsare mot servern) | 8 | 8 godkända |
| `tests/preview.test.mjs` (webbläsare mot förhandsvisningen) | 13 | 13 godkända |
| Bokkontroll | 156 kontroller | 156 godkända, 0 fel |

Köra: `npm test`, `npm run test:e2e`, `npm run test:preview`, `LHM_BOOK_TXT=... npm run verify:book`.

## Skärmbilder

`docs/skarmbilder-v2/`. Version 1:s bilder i `docs/skarmbilder/` är orörda.

## Ingen deployment

Ingen deployment till produktion, LUF Site eller Human Test Site. Den befintliga Human Test-artefakten är inte ombyggd eller ompublicerad.
