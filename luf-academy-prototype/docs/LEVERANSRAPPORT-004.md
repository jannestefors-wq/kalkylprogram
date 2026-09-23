# Leveransrapport. Digital ledarskapsresa 004. Rensning av deltagarvyn

Datum: 2026-09-23. Status: **STOPP. Klar för Jans granskning.**

Intern spårbarhet. Ren deltagarupplevelse.

| Punkt | Svar |
| --- | --- |
| PARTICIPANT SOURCE LABELS REMOVED | **JA**. Alla fem källrader i gränssnittet är borta. Citat visas med "Ur Ledarskap med hjärta och mod", utan sidnummer. Hjälptexter som började med "Bokens övning (s. N)" eller "Boken (s. N)" är omskrivna utan källa. |
| BOOK PURCHASE TEXT REMOVED | **JA**. Raden om att boken köps separat finns inte längre. |
| BOOK READING INSTRUCTIONS PRESERVED | **JA**. Varje vecka har momentet *Inför den här veckan* med rubriken *Läs:*, kapitlets rubrik och *Sidor XX–XX*. Valfri läsning står under *Om du vill läsa mer*. |
| BOOK REFERENCES STILL VERIFIED | **JA**. 92 kontroller mot boktexten, 0 fel. Rubriker, sidintervall, citat, de fem principerna och varje intern sidreferens. |
| INTERNAL SOURCE TRACEABILITY PRESERVED | **JA**. Källa per moment, sidreferenser och PDF-sidor ligger kvar i `server/content.mjs`. Servern tar bort dem innan programmet skickas till deltagaren. Ett test kräver att de finns internt och att de aldrig når deltagaren. |
| VISIBLE HOLD/TODO/DEV LABELS | **INGA**. Diplomets interna not skickas inte längre till klienten, inte heller i testversionen. |
| WEEK 1–6 CHECKED | **JA** |
| 30-DAY FOLLOW-UP CHECKED | **JA** |
| SAMTAL MED JAN CHECKED | **JA** |
| DESKTOP | **PASS**. Chromium 1366×900. |
| MOBILE | **PASS**. Emulerad Android (Pixel 7). Ingen fysisk telefon. |
| PRODUCTION UNCHANGED | **PASS**. Inga filer utanför `luf-academy-prototype/`. Ingen deploy, ingen migrering, ingen databasändring. |
| PREVIEW URL | https://claude.ai/artifact/EWhqnURcS4QVh1a5uZDF7S (version 3, samma adress) |
| READY FOR JAN REVIEW | **YES** |

## Hur det är kontrollerat

Varje moment i alla sex veckor, 30 dagar och Samtal med Jan öppnas i gränssnittet. Texten söks igenom efter:
Källa, arbetsbok, köper du, PDF, Word, HOLD, TODO, TBD, master, crosswalk, provenance, Source, PASS, FAIL, DEV, TEST DATA, SOURCE VERIFIED, "(s. N)", "Bokens övning", "Boken (" och intern.
Samma sökning görs på översikten och på Jans vy.

Spärren är prövad åt andra hållet. En inlagd "Källa: Boken s. 73" i vecka 3 fälldes direkt, med exakt moment angivet.

Den publicerade sidan är också genomsökt efter publicering. Inga träffar.

## Det som ändrades i texten

Bara källhänvisningen är borttagen. Övningarna står kvar. Där "Bokens övning" stod står nu "Ett förslag".

I vecka 3 är "Boken (s. 73): Börja alltid med Se." borttaget. Kvar står "Beskriv situationen konkret. Utan värderingar. Utan tolkningar."

## Det som finns kvar och är avsiktligt

Följande syns bara i testversionen och försvinner i produktion:
- *TESTVERSION. EJ PRODUKTION.*
- Testlägeskortet på översikten.
- Gruppnamnet *Testgrupp. Human Test*.

## OPEN HOLDS

Oförändrade från 003:
- Diplom.
- Hörnfrågorna i trianglarna.
- Läsmängd.
- PDF-masterns ordning för Se, Höra, Känna.
- Bokens "åtta trianglar".
- Det publika repot.

## Rollback

Förhandsvisningen: publicera version 2 igen. Prototypen: gå tillbaka till commit före 004 på branchen.
