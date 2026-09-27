# LMHM v3 · isolerad Human Test 024

Detta är ett lokalt test med påhittade personer. Inget publiceras. Använd inte riktig persondata.

## Start

Node.js 22.13 eller senare behövs; verifierat med 24.14.
Från luf-academy-prototype:

```
node scripts/build-preview-v3.mjs
node --no-warnings scripts/start-v3.mjs --human-test
```

Öppna den lokala länk som skrivs ut. Länken innehåller en tillfällig testnyckel.
Standardporten är 3024. V3_PORT kan ändra porten. Servern binder enbart till
127.0.0.1. Ingen extern hosting eller deployment behövs.
Det byggda paketet i preview/dist-v3 kan också köras med samma startkommando
från den katalogen.

## Genomgång för Jan + ChatGPT

1. Välj Alex. Före start: öppna syntetisk Spegeln 1. Testa också att Start 1:1
   fungerar utan Spegel-svar.
2. Förbered Start 1:1. Skriv bara det som hjälper. Välj ett primärt fokus under
   Min riktning och en handling under Det jag provar nu.
3. Besök Vad hände?. Prova Ja, Delvis och Nej. Vid Nej visas Vad stoppade dig?
   Nästa handling läggs till separat; tidigare handlingar finns kvar.
4. Ompröva fokus. Behåll eller byt, med en förklaring till bytet. Tidigare fokus
   och kopplade handlingar ligger kvar.
5. Besök Runda bordet: sex träffar och en återträff. Efter varje träff kan du
   skriva en frivillig medtränarreflektion som aldrig kan delas eller visas för admin.
6. Testa Mitt 1:1, fler handlingar och Avslutande 1:1. Välj därefter
   Kärnresans slut i den tydligt märkta testlisten. Första gången slutet passeras
   fryses slutbilden (fokus, sista handling, det du tänkte fortsätta göra).
7. Flytta testtiden till 30 dagar efter slutet. Min resa visar slutbilden och
   Vad blev faktiskt kvar?. Besök Runda bordet Återträff.
8. Flytta till tre månader. Jämför fokus, handlingar, 30 dagar och Spegeln 1 med
   syntetisk Spegeln 2. Förbered 3-månaders 1:1.
9. Dela ett enskilt moment eller valt Spegel-perspektiv med Jan. Byt till Jan-vyn
   och kontrollera att bara valt material syns. Återkalla som Alex och kontrollera
   Jan-vyn igen. Delning av en egen Spegel-sammanfattning finns separat.
10. Kontrollera Fredde-vyn: bara Spegel-status. Sam kan inte läsa Alex resa.
    Arbetsgivare saknar individuell läsväg.
11. Öppna Boken som stöd i Min riktning. Tre lager utan veckoläsning; Jan kan
    ge en manuell, verifierad läshänvisning.

## Sparande och gränser

Privat som standard, även fokus. Jan får aktuellt fokus först när deltagaren delar
just det momentet. Det följer 023:s övergripande regel om aktiv återkallelig delning.
Ett aktivt delat moment visar fortsatta ändringar tills delningen återkallas.
Utkast delas aldrig. Ett nytt fokus är ett nytt moment och delas inte automatiskt.

Text autosparas. Handlings- och fokusutkast bekräftas med knappen för att bli
handling respektive primärt fokus. Hela resan har en revisionsnyckel; samtidiga
skrivningar med samma baseRevision ger exakt en accepterad skrivning. Vid konflikt
stannar lokal text i formuläret. Kopiera osparad text innan du öppnar testvyn igen.
Vid ett sparfel visas fel och texten ligger kvar. Efter nätavbrott finns knappen
Försök spara igen. Valideringsfel kan rättas i formuläret utan att låsa autosparandet.
Ingen tyst överskrivning sker.
Privat sparhistorik finns i Min resa.

Data lagras i data/v3-human-test/synthetic.sqlite, aldrig i v2-databasen.
Testroller väljs endast via den lokala testnyckeln; de är ingen produktionsinloggning.
Sessioner upphör när servern startas om. Den syntetiska resan finns kvar.
Testtiden och syntetiska svar kan inte aktiveras genom någon produktionsstart.

## Migrering och rollback

server/migrations-v3/0001_foundation.sql är separat från v2:s migrationskatalog.
Den skapar endast lr_v3_meta, lr_v3_state och lr_v3_history i en egen databas.
Databaser med andra tabeller avvisas innan någon migrering körs.
Ingen v2-data konverteras eller raderas.
Rollback i den egna v3-databasen: ta bort lr_v3_history, lr_v3_state och
lr_v3_meta i den ordningen. Detta raderar enbart Human Test-data.
Avsluta v3-servern före rollback. SQL-kommandon finns i migreringsfilen.

## Verifiering

```
node --no-warnings --test tests/api.test.mjs tests/v2.test.mjs tests/content.test.mjs tests/journey019.test.mjs
node --no-warnings --test tests/v3.test.mjs
node scripts/verify-book-references.mjs
node scripts/verify-book-v3.mjs
node scripts/build-preview.mjs
node scripts/build-preview-v3.mjs
node --no-warnings --test tests/v3-browser.test.mjs
```

Boktesten kräver LHM_BOOK_TXT: text ur Ledarskap_A5.pdf, med LF-radbrytningar och
markören =====PDFPAGE n===== på en egen rad före varje PDF-sida.
Tryckt sida = PDF-sida minus 7. Boktexten ingår aldrig i Git.
Webbläsartesten kräver Playwright. CHROMIUM_PATH kan ange installerad Chrome.
NODE_PATH kan ange en befintlig Playwright-installation.
På Windows körs de oförändrade v2-webbläsartesten med:

```
node --no-warnings --import ./scripts/v2-browser-platform.mjs --test tests/e2e.test.mjs tests/preview.test.mjs
```

Anpassningen ändrar endast testsökvägar, katalogskapande och webbläsarstart.
Inga assertions ändras. Skärmbilder skrivs till test-results, inte över v2:s bilder.

## Human First QA

- Min riktning hjälper deltagaren att välja och ompröva ett fokus. Inga poäng eller
  prestationsfärger. Historik ligger bakom ett frivilligt utfällbart avsnitt.
- Det jag provar nu har tre enkla fält kopplade till en verklig handling.
- Vad hände? visar fyra frågor vid Ja/Delvis och tre vid Nej. Inga sju modellfält.
- Det jag börjar se är privat och frivilligt. En observation skapar inget huvudmål.
- Runda bordet visar nästa mänskliga möte. Ingen temamodul, completion eller
  obligatorisk medtränararbetsbok. Reflektionen är en enda fråga.
- Mina samtal med Jan har enkla, frivilliga förberedelser och eftertankar.
  Startens fokus och första handling länkar till samma arbetsytor, utan dubbla formulär.
- Min resa återvisar deltagarens underlag utan poäng eller påstådd kausal effekt.
  Uppföljningarna finns vid 30 dagar och tre månader i testtiden.
- Jan får en kompass, aldrig manus eller automatiska slutsatser. Admin saknar fritext.
- Gemensam bokgrund är ett kort urval: två inledande sidor från vart och ett av fem
  angivna områden. Caseaktiverad läsning och frivillig fördjupning har inga kalenderkrav.
- Hjärta och Mod lever i språk och handledarstöd, utan nya menyer eller obligatoriska fält.

Ingen blockerande pedagogisk konflikt identifierad i implementation review.
Den mänskliga bedömningen av språk, tempo och mötesstöd återstår för Jan + ChatGPT.

## Uttryckligen utanför 024

Inga externa Spegel-inbjudningar, kontaktlänkar, mejl, riktig tredjepartsdata,
produktionssamtycken, produktionsretention, gallringsjobb, Efterrummet, Runda bordet
Live, AI-casebibliotek, AI-diagnostik, fortsättningsprogram, Sites-integration,
produktion eller deployment. Ingen merge.
