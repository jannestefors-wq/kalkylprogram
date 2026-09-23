# Leveransrapport. Digital ledarskapsresa 002. Human Test Preview

Datum: 2026-09-23. Status: **STOPP. Klar för Jans eget test.**

## Vald previewlösning

| Alternativ | Utfall |
| --- | --- |
| 1. Separat Sites preview | Inte möjligt. Ingen åtkomst till ChatGPT Sites från den här miljön. |
| 2. Separat testserver | Inte möjligt härifrån. Utvecklingsmiljön tar inte emot trafik utifrån och jag kan inte skapa ett värdkonto. |
| **Vald:** privat sida på claude.ai med egen databas | Riktig adress. Fungerar i webbläsare och i Claude-appen på mobil. Helt skild från LUF-produktionen. Privat som standard. |

Samma arbetsyta som prototypen: samma innehållsregister, samma gränssnitt, samma stil. Enda skillnaden är ett transportlager (`preview/transport.js`) som sparar i sidans egen databas i stället för i Node-servern. Byggs med `node scripts/build-preview.mjs`.

## Rapport

| Punkt | Svar |
| --- | --- |
| PREVIEW URL | https://claude.ai/artifact/EWhqnURcS4QVh1a5uZDF7S |
| TEST LOGIN METHOD | Öppna länken inloggad på claude.ai med ditt konto (jannestefors@gmail.com). Tryck **Logga in som testdeltagare**. |
| TEST USER | Ditt eget claude.ai-konto, visat som **Testdeltagare**. Samma konto på dator och mobil ger samma resa. |
| TEST COHORT | **Testgrupp. Human Test**. Start 23 september 2026. Träffar tisdagar 16.00, första 29 september. Teamslänk tom. |
| DESKTOP READY | **PASS** |
| MOBILE READY | **PASS** i emulering (Chromium, Pixel 7) |
| PHYSICAL MOBILE TESTED | **NO**. Ingen fysisk telefon är testad. Inte heller Safari eller iPhone. |
| AUTOSAVE | **PASS**. Inklusive avbrott, varning innan sidan lämnas, omladdning under avbrott och återhämtning. |
| LOGOUT / RETURN | **PASS**. Se begränsning 2. |
| MULTI DEVICE | **PASS** i test: desktop och mobil med samma konto delar resa. |
| CROSS USER PRIVACY | **PASS**. En annan testperson ser inget av din resa och har ingen handledarvy. Den privata resan upprätthålls av plattformen, inte av sidans kod. |
| SHARE WITH JAN | **PASS**. Endast delat avsnitt syns i handledarvyn. Privat närvaroreflektion och ej delad handling syns inte. Verifierat mot den riktiga plattformens regler. |
| TEST DATA ISOLATED FROM PRODUCTION | **PASS**. Sidans egen databas på claude.ai. Ingen förbindelse med LUF:s D1-databas. Ingen analys. Inga anrop lämnar sidan. |
| PRODUCTION UNCHANGED | **PASS**. Inget i ledarskaputanfilter.se, Sites-projektet, nuvarande Academy, Katalysatorn, routing, konton, tabeller eller Google Analytics är berört. |
| WEEK 2–6 IMPLEMENTED | **NO** |
| BOOK REFERENCES | **HOLD** |
| FOUR OMITTED MOMENTS REVIEWED | **PASS**. Se nedan. |
| READY FOR JAN HUMAN TEST | **YES** |

## Testroller i förhandsvisningen

Som ägare av sidan har du tre vyer i menyn:

- **Min resa.** Du som deltagare.
- **Delat med mig.** Testrollen handledare. Visar bara avsnitt som aktivt delats.
- **Grupper.** Testrollen programadministratör. Visar status och datum, aldrig fritext.

Handledar- och administratörsvyn är knutna till ägarskapet av sidan. Om du delar sidan med Fredde eller någon annan får den personen en egen tom resa, men varken handledarvy, administratörsvy eller läsrätt till din text. Plattformen stoppar det. Det är det enda sättet att pröva integriteten med två verkliga människor.

## Så verifierades datagränserna på den riktiga plattformen

Regler som publicerades med sidan:

| Sökväg | Läsa | Skriva |
| --- | --- | --- |
| `data/users/<din id>/` | bara du | bara du |
| `shared/<id>/` | bara ägaren och personen själv | personen själv |
| `roster/<id>` | bara ägaren och personen själv | personen själv |
| `testdata/` | alla med åtkomst | bara ägaren |
| allt annat | alla med åtkomst | bara ägaren |

Prov mot den riktiga databasen, som vanlig deltagare (`interact`):

- Ett delat provdokument under `shared/` gick inte att läsa.
- `roster` gick inte att läsa.
- Försök att ändra testgruppen avvisades.
- Testgruppen gick att läsa.

Provdokumenten togs bort efteråt.

## De fyra utelämnade momenten

Källa: Min ledarskapsresa MASTER v2 (Word). Ingenting i prototypen är ändrat utifrån analysen.

### MITT STARTLÄGE

**Källans funktion.** Fyra frågor före första träffen: *Varför är jag här? Vad skaver mest? Vad vill jag bli bättre på? Vad vill jag att andra ska märka?* Arbetsboken säger: "Du återvänder hit i vecka 5 och vecka 10." Det är deltagarens utgångsläge i egna ord, med ett inbyggt löfte om att det ska läsas igen.

**Skäl till utelämning.** Ordern bad om en kort introduktion och angav startskattningen och tre förändringsmål som startbaslinje. Fyra frågor till före kartan hade gjort starten tung.

**Överlapp.** Fråga 4 finns redan nästan ordagrant som huvudfrågan i Tre saker jag vill förändra. Fråga 3 överlappar delvis med samma moment. Fråga 1 (motivet) och fråga 2 (det som tar mest energi) finns ingen annanstans.

**Rekommendation: SLÅ IHOP.** Lägg *Varför är jag här?* och *Vad skaver mest?* som två korta fält i Var är jag nu?, efter kartan. Då får startpunkten både siffra och ord. Frågorna 3 och 4 behövs inte. Tillbakablicken finns redan i datamodellen: slutet och 30 dagar.

### MIN PRIVATA REFLEKTION

**Källans funktion.** Fyra frågor varje vecka under rubriken "Delas inte med gruppen": *Vad undviker jag just nu? Vad försvarar jag hos mig själv? Vad vet jag egentligen redan? Vad behöver jag hjälp med i ett enskilt samtal?* På papper markerar sidan ett skyddat rum i en bok som annars används i gruppen.

**Skäl till utelämning.** Digitalt är allt privat tills deltagaren själv delar. En egen sida märkt "privat" antyder att resten inte är det. Det vore fel signal.

**Överlapp.** Skyddet finns redan överallt. Frågorna finns inte. Närvaro i mötet gäller en situation. De här frågorna gäller personen själv. *Vad undviker jag* ligger dessutom nära Vecka 2 (Mod, ansvar och det jag undviker). Den fjärde frågan är en bro till det enskilda samtalet, som inte är byggt ännu.

**Rekommendation: BEHÅLL.** Som ett kort avslutande moment varje vecka, efter Vad hände?, utan ordet "privat" i rubriken. *Vad vet jag egentligen redan?* är en av de starkaste frågorna i arbetsboken och passar som veckans sista rad. Frågan om hjälp i enskilt samtal kopplas till samtalet när det byggs.

### JAG ÄR MEDTRÄNARE

**Källans funktion.** Används under live-träffen när en annan deltagares case står i centrum: *Vad hör jag? Vad saknar jag? Min bästa fråga. Vad väcker caset i mig?* Tillsammans med Medtränarens fem regler (lyssna längre, skilj observation från antagande, en fråga i taget, diagnostisera inte, lämna tillbaka ansvaret). Deltagaren lär genom att hjälpa.

**Skäl till utelämning.** Momentet sker i Teams, i stunden, om någon annans situation. Att spara anteckningar om en annan deltagares case i sin egen arbetsyta skapar lagrade uppgifter om en tredje person och krockar med gruppens regel att det som delas stannar i gruppen.

**Överlapp.** Färdigheten övas delvis i Närvaro i mötet och i skillnaden mellan observation och tolkning. Rollen som medtränare finns inte någon annanstans.

**Rekommendation: FLYTTA.** Till en vy för själva träffen: de fem reglerna och de fyra frågorna som stöd på skärmen. Endast *Vad väcker caset i mig?* sparas, eftersom den handlar om deltagaren själv. Inget om den andra personens case lagras.

### VECKANS TRIANGEL

**Källans funktion.** "Se vad som står mellan dig och ett ärligare möte. Skriv runt triangeln." En tom triangel där deltagaren placerar tankar i tre hörn.

**Skäl till utelämning.** Arbetsboken anger inte vilken triangel som avses i vecka 1. Hörnen saknar namn. Att välja en triangel själv hade varit att fabricera innehåll. Trianglarna ligger också nära Katalysatorns material, som inte får blandas in här.

**Överlapp.** Ingen direkt. Situationsmomentet strukturerar analysen i vecka 1 på annat sätt. Se. Höra. Känna. är planerad till vecka 3.

**Rekommendation: TA BORT** ur Vecka 1. Källan är tom för den här veckan. Om du anger vilken triangel och vilka hörn som ska användas, byggs den som interaktiv modell i den vecka där den hör hemma. Troligen vecka 3, med den låsta ordningen SE vänster, HÖRA mitten, KÄNNA höger.

## Kända testbegränsningar

1. **Ingen fysisk telefon testad.** Mobil är testad i emulerad Android Chrome. Safari och iPhone är otestade.
2. **Logga ut** avslutar testsessionen i den här webbläsaren. Det loggar inte ut dig från claude.ai. Svaren hämtas på nytt från databasen vid ny inloggning. För ett hårdare prov: logga ut från claude.ai, logga in igen och öppna länken.
3. **Integritet mellan två verkliga människor** kan bara prövas om du delar sidan med någon. Utan det har testet en användare. Plattformsreglerna är verifierade med sänkt behörighet.
4. **Förhandsvisningen bygger på en lokal modell av plattformen i de automatiska testerna.** Den riktiga plattformen verifierades med direkta läs- och skrivprov, inte genom att klicka igenom sidan.
5. **Teamslänken är tom.** Du kan lägga in en under Grupper.
6. **Ingen mätning i förhandsvisningen.** Den finns bara i prototypen.
7. **Den interna noten HOLD FÖR JAN syns** i momentet Inför veckan. Avsiktligt, eftersom du testar.
8. **Snabbhet.** Varje sparning läser resan från databasen. Märks det som tröghet på mobil vill jag veta det.

## Öppna GDPR-frågor

Oförändrade från 001 (se `DATAGRANSER-OCH-GDPR.md`), plus två som gäller förhandsvisningen:

- **Testtexten lagras hos Anthropic (claude.ai)**, inte hos LUF. Skriv därför påhittade eller avidentifierade situationer, inte verkliga kollegor med namn.
- **Radering.** Allt tas bort genom att ta bort sidan. Din egen resa kan bara du själv se. Inte ens sidans ägare kan läsa en annan användares resa.

Blockerande före riktiga deltagare: inloggningsmetod för deltagare, rättslig grund, lagringstid, vad som händer när programmet avslutas, export och radering, teknisk åtkomst och personuppgiftsbiträden, vad arbetsgivare får veta, integritetstext och undantag från Google Analytics.

## Ändringar i prototypen i denna order

Endast tekniska ändringar. Innehållet i Vecka 1 är orört.

- `public/app.js`
  - Transportkrok för förhandsvisningen.
  - Meddelanden i sidan i stället för `alert()`, som inte visas i en inbäddad sida.
  - Knapp för att logga in i förhandsvisningen.
  - Mänskligt besked när resan inte går att nå vid start, med knappen "Försök igen".
- `public/styles.css`: sidhuvudet ligger inte fast på mobil och tar inte skrivyta.
- Nya filer: `preview/transport.js`, `preview/testdata.mjs`, `preview/dist/min-ledarskapsresa.html`, `scripts/build-preview.mjs` och `tests/preview.test.mjs`.

Testsviter: 18 servertester, 7 webbläsartester och 5 tester av förhandsvisningen. Alla gröna. Förhandsvisningens tester kördes tre gånger i rad.

## Rollback

Ta bort sidan från claude.ai (Artifacts i menyn, eller be mig). Det raderar även testdata. Prototypen påverkas inte.
