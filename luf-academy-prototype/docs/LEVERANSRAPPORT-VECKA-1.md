# Leveransrapport. Digital ledarskapsresa 001. Vecka 1

Datum: 2026-09-23. Status: **STOPP. Väntar på Jans eget test.**

| Punkt | Svar |
| --- | --- |
| CURRENT PRODUCTION VERSION | ledarskaputanfilter.se på ChatGPT Sites. Senast verifierade snapshot `ddb9d89393d4f28e4900f1372ee9dfe8427bd429` (arkiv v284 i `luf-house-audit-source`). Oförändrad. |
| DEVELOPMENT / PREVIEW VERSION | Branch `claude/ledarskap-vecka-1-prototype-7sy98p` i `jannestefors-wq/kalkylprogram`, mappen `luf-academy-prototype/`. Körs lokalt med `npm run seed && npm start`. Ingen publik förhandsvisning finns. |
| FILES CHANGED | Endast nya filer under `luf-academy-prototype/`. Inga befintliga filer i något repo ändrade. |
| DATABASE CHANGES | Ingen i produktion. Prototypen har en egen SQLite-fil. |
| NEW TABLES OR FIELDS | 15 nya tabeller plus en migrationslogg, alla med prefixet `lr_` i `server/migrations/0001_ledarskapsresa.sql`. Endast tillägg. D1-kompatibelt. Inte kört mot D1. |
| ROUTING CHANGES | Inga i produktion. Prototypen har egna routes: `/login`, `/api/*` och klientvyerna `#/`, `#/vecka-1/<moment>`, `#/jan`, `#/admin`. |
| AUTH / PERMISSION CHANGES | Inga i produktion. Prototypen: roller `platform_admin`, `program_admin`, `facilitator` samt inskrivning som deltagare. Identitet via Sites-headern eller personlig testlänk. Inga lösenord. |
| ANALYTICS CHANGES | Inga i produktion. Prototypen: egen händelsetabell med åtta tillåtna händelser, ingen fritext, ingen tredjepartsanalys. |
| WEEK 1 IMPLEMENTED | **YES** |
| WEEK 2–6 IMPLEMENTED | **NO**. Finns som låsta steg i registret och på översikten. Servern vägrar skriva till dem. |
| DESKTOP TEST | **PASS** (Chromium 1366×900, hela kedjan) |
| MOBILE TEST | **PASS** (Chromium, Pixel 7-emulering). Inte testat på fysisk iPhone eller Android. |
| AUTOSAVE TEST | **PASS**. Inklusive nätavbrott, varning innan sidan lämnas, återställning efter omladdning och konflikt mellan två enheter. |
| LOGOUT / RETURN TEST | **PASS** |
| CROSS USER PRIVACY TEST | **PASS**. API och webbläsare. Deltagare, admin och handledare prövade. |
| MULTI COHORT TEST | **PASS**. Två parallella grupper. Sjunde deltagaren stoppas i databasen. |
| BOOK REFERENCES VERIFIED | **HOLD**. Boken finns inte i Drive. Ingen läsanvisning visas för deltagare. Markerat HOLD FÖR JAN. |
| READY FOR JAN HUMAN TEST | **NO, blockerat av en sak.** Tekniskt klart. Jan behöver en förhandsvisning han kan öppna på sin dator och sin telefon. Se nedan. |

## Acceptance criteria

| # | Kriterium | Status | Bevis |
| --- | --- | --- | --- |
| 1 | Rätt deltagare når rätt program | Klart | api-test 1 |
| 2 | Ingen når en annans privata resa | Klart | api-test 2, admin, handledare. e2e direkt-URL |
| 3 | Flera grupper samtidigt | Klart | api-test 3 |
| 4 | All fritext autosparas | Klart | api-test 4, e2e desktop och sparfel |
| 5 | Kvar efter utloggning och inloggning | Klart | api-test 5, e2e desktop |
| 6 | Kvar vid byte av enhet | Klart | e2e mobil läser det som skrevs på desktop |
| 7 | Desktop | Klart | e2e desktop |
| 8 | Mobil | Klart i emulering | e2e mobil. Ingen sidscroll, tryckytor minst 40 px |
| 9 | Ledarskapskartan sparas | Klart | api-test 7, e2e mus och tangentbord |
| 10 | Tre förändringsmål | Klart | api-test 7, e2e |
| 11 | En verklig situation | Klart | e2e |
| 12 | Observation och tolkning åtskilda | Klart | Egna fält, egen färg, egen kant. e2e kontrollerar ordning och färg |
| 13 | Välja veckans handling | Klart | e2e |
| 14 | Handlingen visas tillbaka | Klart | Översikten och Vad hände? visar deltagarens egna ord |
| 15 | Vad hände? | Klart | e2e mobil. Planen låses när Vad hände? påbörjas |
| 16 | Ingen privat text till analys | Klart | api-test 16, e2e: inga externa anrop |
| 17 | Ingen PDF att ladda ner | Klart | Ingen finns |
| 18 | Ingen fil att ladda upp | Klart | Ingen uppladdning finns |
| 19 | Ingen Spara-knapp | Klart | Endast Teamslänken i admin har en knapp |
| 20 | Ingen produktion påverkas | Klart | Inga filer utanför mappen |
| 21 | Vecka 2 till 6 inte byggda | Klart | api-test 21 |
| 22 | Se. Höra. Känna. vänster till höger | Ej tillämpligt | Modellen används inte i Vecka 1. Regeln står i registret inför vecka 3 |
| 23 | Ingen Katalysatormetodik | Klart | Inga trianglar, inga Katalysatorbegrepp |
| 24 | Ingen påhittad bokhänvisning | Klart | HOLD FÖR JAN. e2e letar efter kapitel och sidnummer |
| 25 | Känns som LUF Academy | Jans bedömning | Skärmbilder i `docs/skarmbilder/`. Kan inte avgöras av ett test |

## Vad Vecka 1 innehåller

Nio moment i ordning:

1. **Människan först.** Fem korta rader. Ingen undervisningstext.
2. **Inför veckan.** Läsanvisning HOLD. Deltagaren ser: "Jan anger veckans läsning i boken före första träffen."
3. **Var är jag nu?** Sex dimensioner, sex steg, samma poler som arbetsboken. Självskattning, uttryckligen inget test.
4. **Tre saker jag vill förändra.** Med arbetsbokens följdfråga: hur märker jag att något faktiskt har förändrats?
5. **Människorna runt mig.** Upp till sex. Roll eller initial.
6. **En situation från min verklighet.** Sju frågor i fyra band: det som hände, min tolkning, mitt agerande, efteråt.
7. **Närvaro i mötet.** Sex frågor. Deltagaren svarar på dem som biter.
8. **Det här ska jag prova.** Fem frågor och ett datum. Inget facit.
9. **Vad hände?** Visar först: "Du bestämde dig för att prova" med deltagarens egen text. Därefter sex frågor.

## Medvetna val du bör pröva

- **Planen låses när Vad hände? börjar skrivas.** Beslutet står kvar som det var, så att jämförelsen blir ärlig. Deltagaren kan fortfarande skriva vidare i Vad hände?.
- **Startskattningen låses när gruppen går till vecka 2.** Startpunkten ska vara en startpunkt.
- **Dela med Jan är levande.** Jan ser texten som den ser ut nu, inte en kopia från delningsögonblicket. Det sägs rakt ut i bekräftelsen. Deltagaren kan ta tillbaka delningen.
- **Utelämnat ur arbetsboken:** "Mitt startläge" (fyra frågor), "Min privata reflektion", "Jag är medtränare" och "Veckans triangel". Ordern bad om en kort vecka. Medtränaren hör till live-träffen. Triangeln saknar innehåll i arbetsboken.

## Kända brister

1. Ingen publik förhandsvisning. Blockerar Jans test.
2. Enbart Chromium testat. Safari på iPhone är otestat.
3. Konfliktskydd mellan enheter finns för text. För ledarskapskartan gäller senaste klick.
4. Individuella samtal: datamodell och visning på översikten finns. Formulären före och efter samtalet är inte byggda.
5. Programadmin kan bara ändra Teamslänk. Grupper och deltagare skapas med skript.
6. Engelska finns inte. Masterplanens krav på svensk och engelsk version är inte uppfyllt för den här produkten.
7. Typsnittet Geist laddas inte. Systemets typsnitt används i brödtext. Georgia i rubriker som i huset.
8. Historiken sparar en version per skrivpass (paus över 30 minuter). Ändringar inom samma pass slås ihop.

## Det som behövs för att Jan ska kunna testa

En av två vägar. Beslutet är ditt.

- **A. Förhandsvisning i Sites-projektet.** Portera prototypen till vinext och D1 i ett separat Sites-projekt eller en preview, aldrig i produktionsprojektet. Datamodellen går att köra direkt. Kräver åtkomst till Sites som jag inte har härifrån.
- **B. Tillfällig testserver.** Prototypen kör som den är på valfri Node 22-värd bakom HTTPS med `LR_SECURE_COOKIES=1`. Snabbast. Kräver att någon sätter upp värden.

## Rollback

Se `docs/ROLLBACK.md`. Kort: radera branchen eller mappen. Inget annat finns att återställa.
