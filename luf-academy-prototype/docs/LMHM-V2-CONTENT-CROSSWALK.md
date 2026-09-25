# LMHM version 2. Content crosswalk

Order 014. FINAL CONTENT SPEC (docs/LMHM-V2-FINAL-CONTENT-SPEC.md) mot faktisk implementation.

Maskinell kontroll: `tests/content.test.mjs` läser specifikationen och kräver att varje citatblock och varje text inom citattecken i deltagardelarna finns ordagrant i det deltagaren ser (297 texter). Text för Jan, bokningsvillkor och interna källor hoppas över eftersom de aldrig visas i appen.

## Avsnitt för avsnitt

| Spec | Implementation | Kontroll |
|---|---|---|
| 3. Format, sex träffar, återträff 60 min | `scripts/seed.mjs` (träff d30, 60 min), `preview/testdata.mjs` | v2.test: återträffen är 60 minuter |
| 4. Startsamtalet, integritetstext, Inför och Efter | `content.mjs` START_SECTIONS, PRIVACY_TEXT. Steget `start`, alltid öppet. Integritetstexten överst i resan och på Inför startsamtalet | v2.test, content.test, preview.test |
| 4. Jans text, bokningsvillkor | Visas inte i appen, enligt specifikationen | content.test hoppar över |
| 5. Integritetsregler 1 till 8 | `app.mjs` facilitatorShared, adminOverview, supportState. `rules.mjs` supportPromptFor. Inga händelser för startsamtal, samtal eller vägledning | v2.test integritet, api.test, preview.test |
| 6. Rummets regler, medtränare | LIVE_SUPPORT, oförändrad | content.test |
| 7.1 Förra veckan | `app.js` renderBridge. Nej-texten och deltagarens egna ord | preview.test två Nej |
| 7.2 Det här ska jag prova, I1 till I4 | PLAN_FIELDS, `action()`. Område som val med egna ord, Något nytt villkorat | v2.test motorn, preview.test |
| 7.3 Vad hände?, J0 till L1 | `whatHappened()`. Klarstatus räknar bara synliga fält | v2.test Ja, Delvis, Nej |
| 7.4 till 7.6 | `privat()`, `live()`, `stanna()` | content.test |
| 8. Tre förändringsområden | Vecka 1 `forandring`, återanvänds i översikten, I1, halvvägs, Hela resan och 30 dagar | preview.test |
| 9. Vecka 1 | WEEK_1_SECTIONS. Högst fyra personer, två räcker | preview.test, v2.test |
| 10. Vecka 2 | WEEK_2_SECTIONS. G4 villkorad och frivillig | v2.test |
| 11. Vecka 3 | WEEK_3_SECTIONS. Min återkoppling ny | content.test |
| 12. Vecka 4 | WEEK_4_SECTIONS. Halvvägs och Spegeln före Inför veckan. När stödet inte räcker villkorat | v2.test |
| 13. Vecka 5 | WEEK_5_SECTIONS. Triangeln utan hörnfält. Tre vägar villkorade. P4 i jag-form | v2.test, content.test |
| 14. Vecka 6 | WEEK_6_SECTIONS. Tryck · Val · Riktning med ett fält. Återhämtningen frivillig i Stanna upp. Ingen Vad hände?, inget löfte | v2.test |
| 15. Spegeln | `spegel()`. Val: Medarbetare, Kollega, Egen chef, Annan | v2.test |
| 16. Samtal med Jan och två Nej | TALK_SECTIONS, SUPPORT_PROMPT, `rules.supportPromptFor`, `/support`, `/talk-request` | v2.test, preview.test |
| 17. 30 dagar | DAY_30_SECTIONS. Vecka 6:s plan låses när D2 besvaras | v2.test |
| 18. Återträffen | Moment `atertraff`: inbjudan, tid, 60 minuter. Ingen kurslogik | preview.test |
| 19. Läsanvisningar | `reading()` per vecka. Avsnitt i kapitel märkta internt med inChapter | content.test, bokkontrollen 156 av 156 |
| 20. Trianglar | `triangle()`. Vänster, mitten, höger. Trygghet digital | preview.test på fyra bredder, bokkontrollen |
| 21 och 22. Delning och privat | `shareable` bara på momenten i 21 | v2.test |
| 23. Villkorade flöden | `showWhen`, `hintWhen`, `rules.fieldVisible` | v2.test regler |
| 24. Borttaget | Nya nycklar, se LMHM-V2-FIELD-MAP.md | content.test gamla texter |
| 25. Fältantal | Se nedan | |

## Text i appen som inte står i specifikationen

Det här är systemtext eller navigering. Ingen av texterna är en fråga. Jan bör läsa dem vid Human Test.

**Ny i version 2**
- "Frivilligt" efter frivilliga frågor.
- "Förfrågan skickad" och datum, efter Be om ett samtal. Specifikationen säger inte vad deltagaren ser efteråt.
- Rubriker i återblickarna: "Från starten", "Från vecka 6", "Vecka N. Blev det av?". Övriga rubriker där är momentens och frågornas egna texter.
- "Inga svar ännu." och "Du har inte skrivit dina tre saker ännu." när det inte finns något att visa.
- I Jans vy: "Vill boka ett samtal." och datum. I Jans vy visas området som "Förändringsområde 1", eftersom områdets text står i ett privat moment.
- Översiktens kort: "Det som skavde mest" och "Tre saker jag vill förändra".

**Kvar från nuvarande kurs, inte ändrad av specifikationen**
- 30 dagar: momenttitlarna "Det här skrev du", "Kartan en gång till", "Vad blev kvar?" och deras ledtexter.
- Läsningens rubrik "Inför den här veckan", delningsrutan, sparstatus, konflikttexter, testläget.
- "Du bestämde dig för att prova", "Efteråt skrev du att det här hände", "Planerat till".

## Fältantal (spec avsnitt 25)

Specifikationen räknar skrivfält. Implementationen har samma frågor. Två interna räkningar i specifikationen stämmer inte helt med dess egna tabeller och påverkar inte bygget:
- Avsnitt 20 anger "7 digitala hörnfrågor och 2 nya". Tabellen i samma avsnitt ger 8 digitala hörnfrågor, varav 2 nya. Registret följer tabellen: 18 hörnfrågor, 10 ur boken och 8 digitala.
- Avsnitt 25 är en sammanfattning. Frågorna i avsnitt 9 till 17 är det som byggts.
