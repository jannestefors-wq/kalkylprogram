LMHM VERSION 3 HUMAN FIRST ARCHITECTURE 023
FINAL ARCHITECTURE CANDIDATE
DATUM: 2026-09-27
MARKERING: ERSÄTTER 022 EFTER FINAL JAN + CHATGPT REVIEW
ROLL: ARCHITECT. Ingen kod. Ingen commit. Ingen push. Ingen deployment. Ingen databasmigrering. Ingen förändring av Human Test eller produktion.


Detta dokument är fullständigt och fristående. Det kräver inte 021 eller 022 för att förstå vad som ska byggas. Språkligt granskat enligt order 023 §14; terminologin är konsekvent (Människan först · Se · Höra · Känna · Mät · Korrigera · Mät igen · Runda bordet · Spegeln 1 · Spegeln 2).


=== 0. VERIFIERAD TEKNISK BASELINE (U-1 LÖST) ===


Verifierad av Jan + ChatGPT direkt mot GitHub-repot:
- Branch: claude/lmhm-v2-build-014
- AKTUELL HEAD: 085f5aff80134d702aff95888257f863b3a70b02
- Commit: "LMHM version 2: overview clarity patch 020"
- 268cffd77c5a9d94bbf046461cb5ecc908b8a609 är exakt en commit bakom ("LMHM version 2: final clarity patch 019A"). GitHub compare: status ahead, 085f5af är 1 före 268cffd, behind 0.


BASELINE FÖR FRAMTIDA IMPLEMENTATION: 085f5aff80134d702aff95888257f863b3a70b02. STOPP-flaggan från 022 är borttagen. Ingen kod ändras i denna order. Eventuell framtida implementationorder verifierar baselinen på nytt vid start, som rutin.


=== 1. ÖVERORDNAD PRINCIP ===


MÄNNISKAN FÖRST. ALLTID. Kierkegaards tanke – att den som vill hjälpa en människa först måste finna henne där hon är och börja där – är systemets designprincip, inte dekoration. Affären kommer efter människan. Utbildningen optimeras för verklig positiv förändring hos människan som deltar, inte för skalbarhet, genomströmning, administration, teknik eller AI.


Arbetsmetod vid varje val: Vilken förändring hos deltagaren ska detta skapa? Varför måste detta vara obligatoriskt? Behöver människan skriva detta? Hjälper modellen deltagaren se tydligare, eller bara utbildningen större? Frigör funktionen mänsklig tid, eller tar den?


=== 2. DEFINITION ===


LMHM v3 är en personlig förändringsresa i ledarskap – inte en kurs. Centrum: människan + verkligheten + handlingen + återkopplingen + förändringen. Övergripande loop: Se · Höra · Känna → Varför? → Hitta rätt problem → Ta saken → Dela upp → Prioritera → Gör → Mät → Korrigera → Mät igen. 80/20 är prioriteringsprincip, aldrig matematiskt naturlag.


=== 3. RESANS YTTRE TIDSRAM (LÅST) ===


FÖRE START: Spegeln 1 (förenklad, avsnitt 7) + förberedelse. Spegeln blockerar aldrig start – Start 1:1 genomförs med det underlag som finns.
AKTIV KÄRNRESA: cirka sex veckor. Fasta principer, mjuka steg. Aldrig sex mekaniska kursmoduler.
30 DAGAR EFTER KÄRNRESANS SLUT: uppföljning + Runda bordet Återträff (avsnitt 12). Ingen automatisk individuell 1:1.
CIRKA TRE MÅNADER EFTER KÄRNRESANS SLUT: Spegeln 2 + egen jämförelse + 3-månaders 1:1.


=== 4. ETT PRIMÄRT FÖRÄNDRINGSFOKUS I TAGET (NYTT LÅST BESLUT) ===


V2 arbetar med tre förändringsområden. V3 börjar INTE med tre likvärdiga utvecklingsmål – det strider mot 80/20-principen och sprider deltagarens uppmärksamhet.


Efter Spegeln, start-1:1 och analysen väljs: ETT PRIMÄRT FÖRÄNDRINGSFOKUS. Frågan: Vilken förändring skulle sannolikt göra störst positiv skillnad just nu?


- Andra saker deltagaren upptäcker sparas under "Det jag också ser" – de blir ALDRIG automatiskt parallella huvudmål.
- Fokuset får ändras. Om verkligheten visar att första problembilden var fel är det lärande, inte misslyckande.
- Arkitekturen stödjer loopen: Fokus → Prova → Se vad som händer → Ompröva → Behåll eller byt fokus.
- Detta är centralt för 80/20, rätt problem före snabb lösning, Mät · Korrigera · Mät igen och Människan först.


=== 5. HJÄRTA OCH MOD ===


Hjärta och Mod är primärt design- och handledarkompasser. De blir ALDRIG etiketter på varje deltagarskärm och aldrig poäng, badges eller kategorier att administrera. De får synas naturligt där de hjälper förståelsen. Jan använder dem i 1:1 och Runda bordet.


HJÄRTA: se människan, lyssna, förstå innan bedömning, trygghet, relation, värdighet, utveckla andra, närvaro, nyfikenhet, hjälpa utan att ta över, nåd även mot sig själv.
MOD: kliva fram, ta ansvar, säga det som behöver sägas, svåra samtal, besluta, säga nej, stå kvar, erkänna fel, säga "jag vet inte", utmana gamla sanningar, göra det rätta när det kostar.


=== 6. VARFÖR ===


Varför går in i kärnan på två nivåer: (A) deltagaren förstår varför en övning finns – inget viktigt moment visas utan sammanhang (Förstå först. Skriv sedan.); (B) deltagaren utforskar sitt eget varför: Varför reagerade jag så? Varför undviker jag detta? Varför tror jag att detta är problemet? Jan använder Varför diagnostiskt och nyfiket, aldrig som psykologisk diagnos. "Jag vet inte ännu" är giltigt svar. Jan talar aldrig om för deltagaren vad personens egentliga motiv är.


=== 7. SPEGELN 1 (LÅST, U-2 LÖST – EXAKTA FRÅGOR) ===


Syfte: Så ser jag mig själv. Så upplever andra mig. Vad behöver jag förstå?


FEM LÅSTA KÄRNFRÅGOR:
1. När fungerar personen som bäst i mötet med andra? Beskriv gärna en konkret situation du själv har sett eller hört.
2. Vad skulle personen vinna mest på att göra mer av? Vad bygger du det på?
3. Vad skulle personen vinna mest på att göra mindre av? Vad bygger du det på?
4. Finns det något i personens sätt att agera som personen själv kanske inte alltid ser? Beskriv gärna en konkret situation.
5. Om en enda sak förändrades under de kommande månaderna, vad tror du skulle göra störst positiv skillnad? Hur skulle du märka det? (80/20-FRÅGAN – kärnfråga, INTE frivillig.)


EN FRIVILLIG FRÅGA (max):
- Är det något annat du vill skicka med som kan hjälpa personen att utvecklas?


Spegeln är perspektiv och observation. Den är: inte diagnos, inte personlighetstest, inte betyg, inte poängsystem. Korta svarsfält, guidning mot konkreta exempel – genomtänkta svar, inte mycket text.


Partner/vän är frivilliga perspektiv, aldrig krav; de bedömer inte yrkesprestation utan kan observera mönster (lyssnande, tålamod, stressreaktioner, kontroll, närvaro, att erkänna fel).


=== 8. SPEGELN – ÄGANDE, DELNING, INFORMATION OCH GALLRING ===


ÄGANDE (korrigerad formulering, ersätter 022:s "deltagaren äger svaren"):
Spegeln är till för deltagarens utveckling. Deltagaren styr inom programmet om svar eller sammanfattningar delas med Jan. De juridiska rollerna och rättigheterna för personuppgifterna fastställs i det obligatoriska integritets-/juridiska gate (avsnitt 19).


LÅST:
- Jan ser inget automatiskt.
- Deltagaren kan aktivt dela valda svar eller en egen sammanfattning inför 1:1.
- Fredde (administratör) ser endast status – aldrig råsvar eller fritext.
- Arbetsgivaren får ingen individuell Spegel-data.
- Ingen Spegel-fritext till analytics.
- Inget löfte om full anonymitet när en relationsroll kan göra svaranden indirekt identifierbar; deltagaren informeras och väljer mottagare med det i åtanke.


INFORMATION TILL DEN SOM SVARAR (explicit krav, enkel svenska, INGA DOLDA VILLKOR):
Innan en extern person svarar ska personen få veta:
- varför frågorna ställs
- att svaren är till för deltagarens utveckling
- att deltagaren kommer att kunna läsa svaret
- att Jan inte ser svaret automatiskt
- att det är frivilligt att svara
- ungefär hur länge svaret sparas
- att relationsrollen i vissa fall kan göra personen identifierbar för deltagaren
Människan först gäller även den människa som svarar på Spegeln.


Teknik (arkitektur, inte implementation): personliga engångslänkar, självvald relationsroll som enda identitet, inga konton, inga skalor.


=== 9. SPEGELN 2 (LÅST) ===


- Genomförs cirka tre månader efter kärnresans slut.
- Samma människor som Spegeln 1 när möjligt (bättre före/efter-jämförelse) – ALDRIG ett krav; deltagaren initierar en ny inbjudan. Spegel 2 får ALDRIG automatiskt kontakta tidigare svarande.
- Frågeordning (observationsbaserad, aldrig ledande):
1. "Vad, om något, har du märkt är annorlunda i hur personen leder eller möter andra?"
2. Be därefter om ett konkret exempel.
3. Vad verkar oförändrat?
4. Vad tycker du personen bör fortsätta träna på?
- Samma integritetsmodell, information till svarande, ägande och gallring som Spegeln 1.


=== 10. 1:1-MODELLEN (LÅST, MED RIKTVÄRDEN) ===


- START 1:1, cirka 60 minuter (efter att Spegeln hunnit ge användbart underlag när möjligt; Spegeln blockerar aldrig): nuläge, självbild, Spegeln, verklig situation, Varför, första problembild, rotproblem/symptom, första prioritering, handling – och val av det primära förändringsfokuset (avsnitt 4).
- MITT 1:1, cirka 45 minuter: verklig handling, mönster, motstånd, rätt/fel problem, korrigering.
- AVSLUTANDE 1:1, cirka 45 minuter: vad har faktiskt förändrats, vad bygger deltagaren det på, vad återstår, vad fortsätter.
- 3-MÅNADERS 1:1, cirka 30 minuter: Spegeln 2, då och nu, vad som hållit, nästa riktning.
- 30-dagarspunkten: Runda bordet Återträff – ingen automatisk individuell 1:1.


Tiderna är RIKTVÄRDEN. Människan får styra samtalet mer än klockan när det behövs. Jan har en facilitator-kompass, inte manus.


Systemstöd inför 1:1 – hjälpa Jan SE (aldrig tala om vilken slutsats han ska dra):
- deltagarens nuvarande primära fokus
- vad deltagaren har valt att dela
- senaste verkliga handlingen och vad som hände
- eventuella återkommande mönster i det deltagaren själv delat


Jan är inte terapeut och diagnostiserar aldrig. "Jag vet inte ännu" är giltigt svar.


=== 11. RUNDA BORDET – RYTM (LÅST) ===


Under den aktiva kärnresan (cirka sex veckor): ETT Runda bordet per vecka – normalt SEX Runda bordet under kärnresan. Format: cirka 90–120 minuter. Jan kan avsluta tidigare när rummet är klart – ingen träff fylls ut bara för att klockan säger två timmar.


- Verkliga case är huvudmaterialet. Skärm/material används endast när det hjälper samtalet. Riktvärde: huvuddelen av tiden är människor som pratar, lyssnar, frågar och arbetar med verkligheten.
- 30 dagar efter kärnresan: RUNDA BORDET ÅTERTRÄFF, cirka 60 minuter. Ingen ny undervisningsmodul.
- Max sex deltagare behålls tills annat beslutas. Extern beskrivning: "liten grupp". Inget tekniskt minimikrav – systemet kräver aldrig full grupp; 4–6 är önskvärd arbetsstorlek; start med färre möjlig när Jan bedömer att det skapar värde.


=== 12. RUNDA BORDET ÄR INTE SEX NYA MODULER (EXPLICIT) ===


Sex veckovisa träffar betyder INTE sex teman som alla måste igenom i samma ordning. Runda bordet följer deltagarnas verklighet. Facilitator-kompassen används när den behövs. Boken och modellerna aktiveras utifrån det som ligger på bordet.


Facilitator-kompass (inte obligatorisk mötesagenda): 1. verklig situation på bordet. 2. övriga lyssnar. 3. vad vet vi? 4. vad tror vi? 5. vad saknas? 6. varför? 7. är detta det verkliga problemet? 8. ta saken. 9. dela upp. 10. prioritera. 11. deltagaren väljer själv nästa steg. Jan får stanna (t.ex. vid fråga tre i tjugo minuter), byta ordning och följa det som uppstår. En vecka kan handla mycket om mod, en annan om relation, en tredje kan fastna i "är det här ens rätt problem?" – det är avsiktligt.


Jan stoppar: för snabba lösningar, råd innan förståelse, antaganden som fakta, etiketter på människor, deltagare som tar över någon annans problem. Återkommande frågor: Vad har du faktiskt sett? Vad har du faktiskt hört? Vad är din egen känsla eller tolkning? Vad vet vi inte? Varför tror du att det här händer? Är det här verkligen problemet?


=== 13. MEDTRÄNAREN ===


Medtränarrollen är central: mitt case = mitt ledarskap; andras case = träning i lyssnande, observation, nyfikenhet, att skilja fakta från antaganden, bättre frågor, att inte lösa åt andra, att hjälpa någon tänka. Grund från boken: att utveckla andra handlar om frågor, inte svar.


Systemstöd: ENDAST en kort, frivillig, privat reflektion efter Runda bordet: "Vad såg eller hörde du idag som förändrade hur du själv tänker?" Ingen obligatorisk arbetsbok, inget arbetsblock.


=== 14. REFLEKTIONSLOOPEN – TÄNKANDE, INTE FORMULÄR ===


Loopen Se · Höra · Känna → Varför → Mät · Korrigera · Mät igen är ett tänkande- och samtalsstöd, ALDRIG sju obligatoriska skrivfält efter varje handling.


Fast digital ryggrad efter varje handling:
- Blev det av?
- Vad hände?
- Vad bygger du det på?
- Vad gör du nu?
Vid Nej: Vad stoppade dig? (Nej är giltigt resultat.)


SE/HÖRA/KÄNNA/VARFÖR/MÄT/KORRIGERA/MÄT IGEN aktiveras endast där de skapar värde: digital fördjupning, 1:1, Runda bordet, privat reflektion. Ingen formulärinflation. KÄNNA är deltagarens egen signal – aldrig facit på vad en annan människa känner.


=== 15. BOKEN – TRE LAGER (LÅST) ===


Princip: Boken är kunskapsreserv och fördjupning. Den är INTE ett sexveckors lässchema.


GEMENSAM GRUND – ett begränsat urval som alla möter tidigt för att förstå språk och filosofi. Utvalda delar av: Människan först · Utan filter · Modet att kliva fram · Triangelmetodikens grund · Se · Höra · Känna. Hålls kort nog för att resan aldrig blir en läskurs.


CASEAKTIVERAD LÄSNING – Jan/plattformen pekar deltagaren till relevant kapitel/avsnitt när personens verkliga situation gör materialet användbart. Exempel: konflikt → Konflikt · Lösning · Ansvar; problem lagda på individen → Person · Process · Produkt / Individ · Team · Organisation; press → Stress, press och den inre kompassen; utveckla någon → coachande ledarskap.


FRIVILLIG FÖRDJUPNING – resten av boken läses i egen takt. Ingen deltagare ska behöva läsa ett kapitel bara för att kalendern säger att "det är vecka 4".


=== 16. BOKKARTA – KÄRNA / CASEAKTIVERAT / FORTSÄTTNING ===


KÄRNRESAN (måste): Människan först; Utan filter; Se · Höra · Känna; Trygghet · Relation · Utveckling; Konflikt · Lösning · Ansvar; Person · Process · Produkt; Individ · Team · Organisation (kärndel); egna mönster och skuggsidor; Vad som formar en ledare (utvalda delar); Modet att kliva fram; stress, press och inre kompassen; kommunikation/svåra samtal; När det kostar att göra rätt; Ta saken · Dela upp · Prioritera; Mät · Korrigera · Mät igen; Den dag du gör allt fel (nåd). PLUS (flyttat till kärnan i 022, oförändrat): Triangelmetodikens grundprincip – se flera perspektiv, välja relevant triangel/perspektiv, förstå att ett problem kan behöva undersökas från flera håll (trianglarna som gemensamt språk); coachande ledarskap första nivån – fråga före råd, hjälpa någon tänka, lämna tillbaka ansvaret, inte skapa beroende.


CASEAKTIVERAT: övriga trianglar; Sägs · Görs · Tystas; valda sanningar; delar av Att bygga team som håller.


FORTSÄTTNING/FÖRDJUPNING (arkitektoniskt utrymme, ingen produktifiering nu): utveckla andra ledare (systematisk ledarutveckling), succession, fördjupad delegering, rekrytering, onboarding, avrekrytering med värdighet, leda uppåt, förändring, trianglarna som sammanhängande system, Ledarskapet framåt (delvis).


=== 17. DIGITALA ARBETSRUMMET – SPEGLAR RESAN, INTE VECKOKURSEN (ARKITEKTURFÖRSLAG) ===


Arbetsrummet = deltagarens privata arbetsrum för förändringsresan (inte kursportal). Organiserat runt deltagarens förändringsloop. Föreslagna huvudytor (arkitektur, inte färdig UI-design):


- MIN RIKTNING: primärt förändringsfokus; varför detta; hur skulle någon kunna märka skillnad?
- DET JAG PROVAR NU: vad ska jag göra? i vilken verklig situation? när?
- VAD HÄNDE?: Blev det av? Vad hände? Vad bygger du det på? Vad gör du nu? Vid Nej: Vad stoppade dig?
- DET JAG BÖRJAR SE: frivilliga privata reflektioner; annat som blir synligt (inklusive "Det jag också ser", avsnitt 4).
- RUNDA BORDET: nästa träff; enkel förberedelse; frivillig medtränarreflektion.
- MINA SAMTAL MED JAN: förberedelse; vad tar jag med mig?; nästa steg.
- MIN RESA: förändring över tid; Spegeln när relevant; 30 dagar; tre månader.


Plattformen hjälper deltagaren minnas, reflektera, följa sin förändring, se tidigare handlingar, förbereda 1:1 och Runda bordet. Den gör Jan friare i det mänskliga mötet, aldrig styrdare.


=== 18. VAD SOM BETYDER ATT KÄRNRESAN HAR LYCKATS (TRE NIVÅER) ===


1. DELTAGAREN SER NÅGOT TYDLIGARE: personen har fått en bättre bild av sitt eget ledarskap och vad som faktiskt behöver förändras.
2. DELTAGAREN GÖR NÅGOT ANNORLUNDA: förändringen har lämnat skärmen och blivit beteende i verkligheten.
3. NÅGON ANNAN KAN MÄRKA NÅGOT: det finns observationer från människor runt deltagaren som kan tyda på förändring.


Ingen nivå ensam används som bevis för kausal effekt. Tillsammans ger de en starkare bild av förflyttningen. Språk i system och marknadsföring: "observerad förändring", "upplevd förändring", "flera datapunkter som tillsammans ger en starkare bild". Datapunkter: startbild · Spegeln 1 · verkliga handlingar · Vad hände? · vardagsobservationer · 1:1-reflektion · Runda bordet · 30 dagar · Spegeln 2 · tre månader. Ingen poängjakt. Kärnformulering: Jag leder annorlunda än när jag började och människorna omkring mig kan märka det.


=== 19. INTEGRITETSMODELL ===


Bevarat från v2 (oföränderligt): privat fritext som standard; deltagaren ser bara sin egen resa; aktiv, återkallelig delning med Jan; administratör utan fritext; arbetsgivare utan automatisk individuell rapport; ingen privat fritext till analytics; intern källmärkning osynlig för deltagaren; inga påhittade kapitel/citat/modeller; SE=vänster, HÖRA=mitten, KÄNNA=höger (alltid); bokkontroll; revisionskontroll (baseRevision) och concurrency-kontraktet; Förstå först. Skriv sedan.; exempel, inte facit.


Nytt i v3: Spegelns ägande/delning (avsnitt 8), information till svarande (avsnitt 8), engångslänkar, ärlig information om indirekt identifierbarhet, resultatspråket (avsnitt 18), juridiskt gate (avsnitt 22).


=== 20. CASEBIBLIOTEK – SKYDDA TREDJE PERSON (FÖRTYDLIGAT) ===


Inget generellt samtycke – aldrig. Deltagarens godkännande är NÖDVÄNDIGT men INTE ALLTID TILLRÄCKLIGT: case kan innehålla uppgifter om andra människor. Före framtida publicering måste:
1. identifierande detaljer tas bort
2. onödiga personuppgifter tas bort
3. situationen inte rimligen kunna kopplas tillbaka till en tredje person genom kombinationen av detaljer
4. deltagaren ser och godkänner slutversionen
Om rimlig avidentifiering inte går: PUBLICERA INTE CASET.


AI-roll (framtida, hårda gränser oförändrade): strukturering, taggning, sökning, relevanta case, sammanställning, administration, påminnelser; koppling av case till perspektiv och verktyg. AI diagnostiserar aldrig människor; behandlar aldrig KÄNNA som fakta om andra; självpublicerar aldrig känsliga case; avlastar människan men ersätter aldrig det mänskliga mötet.


=== 21. EFTERRUMMET ===


"Fortsätt din resa" finns kvar i arkitekturen men INTE i första v3-implementationen: nya case, övningar, Runda bordet, fortsatt reflektion, eget tidigare material, växande erfarenhetsbank; erfarna deltagare kan på sikt bidra som medtränare. Runda bordet Live är framtida pilot (nästa fas), inte första bygge. Ingen produkt skapas för att fylla en katalog. Ingen produktifiering av fortsättning/fördjupning nu – kärnresan ska först bli exceptionellt bra.


=== 22. JURIDISK GATE (OBLIGATORISK, PRE-PRODUCTION) ===


Integritets-/juridisk granskning av Spegeln (inklusive externa tredjepartsuppgifter och informationen till svarande) är ett OBLIGATORISKT GATE FÖRE ANVÄNDNING MED RIKTIGA DELTAGARE. GDPR-frågorna i v2 löses före riktiga deltagare. Gallringstid (avsnitt 8) fastställs inom detta gate.


=== 23. BEHÅLL / FÖRÄNDRA / FLYTTA / TA BORT (FRÅN V2) ===


BEHÅLL: hela integritetsmodellen (avsnitt 19); SE/HÖRA/KÄNNA-positioner; KÄNNA som signal; den digitala reflektionsryggraden (Blev det av? Vad hände? Vad bygger du det på? Vad gör du nu?; Nej som giltigt; Vad stoppade dig?; Märkte någon något?); Förstå först. Skriv sedan.; verktygen Se · Höra · Känna och Mät · Korrigera · Mät igen (HUMAN_APPROVED); medtränarreglerna; 30-dagarsuppföljningen; bokkontroll och källmärkning; revisionskontroll och concurrency; autosparning och historik; testsviterna och content-registret som teknisk bas – mot VERIFIERAD baseline 085f5aff80134d702aff95888257f863b3a70b02.


FÖRÄNDRA: startsamtalet + första 1:1 → sammanslagen Start 1:1 (60 min); "Samtal med Jan vid behov" → fyra definierade 1:1-platser (Start/Mitt/Avslutande/3 månader, riktvärden); tre likvärdiga utvecklingsmål → ett primärt förändringsfokus i taget; veckostyrning → aktiv kärnperiod med mjuka steg; gruppträffar → Runda bordet (en träff per vecka, 90–120 min, facilitator-kompass, medtränarroll, start utan full grupp); boken → tre lager (gemensam grund, caseaktiverad, frivillig); arbetsrummet → organiserat runt förändringsloopen (avsnitt 17), inte veckomoduler.


FLYTTA: utveckla andra ledare (systematisk), succession, fördjupad delegering, teambygge i bredare mening, Sägs · Görs · Tystas, valda sanningar, förändring, rekrytering/onboarding/avrekrytering, leda uppåt, trianglarna som sammanhängande system → Fortsättning (vissa caseaktiverade).


TA BORT: sex mekaniska kursmoduler; dubbla inledande samtal; tre parallella huvudmål; poäng-/statusfokus som motverkar förändringsmålet; permanent lagring av Spegel-råsvar (ersätts av gallring); formulärinflation i reflektionen.


=== 24. GRÄNSER ===


Katalysatorgränsen bevaras: LMHM tränar perspektiv, diagnostiskt tänkande inom eget ledarskap, fler nivåer, ifrågasättande av första problembilden; avancerad systemdiagnostik och Katalysatorrollen ligger i specialistspåret. Kommersiell princip: annorlunda där det förbättrar deltagarens resultat; möjlig positionering "Många utbildningar börjar med innehållet. Vi börjar med människan och hennes verklighet" – ingen säljtext här. LUF Academy är huset: göra verklig skillnad för människor och sprida Människan först; affären behövs men får aldrig bli utgångspunkt för hur människan behandlas. Nåd och att vända tillbaka: se det, erkänna, lära, korrigera, vända tillbaka – självreflektion är aldrig självbestraffning; Hjärta gäller också förhållandet till sig själv.


=== LOCKED FOR IMPLEMENTATION ===


Samtliga låsta arkitekturbeslut i 023 (avsnitt 0–24): verifierad baseline 085f5af; yttre tidsram (före start / sexveckorskärnperiod med mjuka steg / 30 dagar / tre månader efter kärnresans slut); ett primärt förändringsfokus i taget med loopen Fokus → Prova → Se vad som händer → Ompröva → Behåll eller byt; Hjärta och Mod som design- och handledarkompasser; Varför på två nivåer; Spegeln 1:s fem låsta kärnfrågor + en frivillig fråga; ägandeformulering, delning och information till svarande; Spegeln 2:s fyra frågor, samma personer när möjligt, aldrig automatisk kontakt; fyra 1:1 med riktvärden och facilitator-kompass, systemstöd som visar underlag men aldrig drar slutsatsen åt Jan; Runda bordets rytm (sex träffar, 90–120 min, återträff 60 min), max sex, inget tekniskt minimikrav, facilitator-kompassen, aldrig sex temamoduler; medtränarreflektionen som enda systemstöd; reflektionsryggradens fyra frågor + Vad stoppade dig?; bokens tre lager; bokkartan (kärna med triangelgrund och coachande första nivå / caseaktiverat / fortsättning); arbetsrummets huvudytor; framgångens tre nivåer och resultatspråket; integritetsmodellen v2+v3; casebibliotekets tredjepersonsskydd och per-case-godkännande; Efterrummet i arkitekturen men ej i första bygget; Katalysatorgränsen; BEHÅLL/FÖRÄNDRA/FLYTTA/TA BORT-listan.


=== PRE-PRODUCTION GATES (ENDAST SÅDANT SOM MÅSTE LÖSAS FÖRE RIKTIGA DELTAGARE) ===


- GATE 1: Juridisk/integritetsgranskning av Spegeln (ägarroller, tredjepartsuppgifter, information till svarande, GDPR) – obligatorisk före riktiga deltagare.
- GATE 2: Exakt gallringstid för Spegelns råsvar – fastställs inom Gate 1. Arkitekturen är låst: råsvaren är tillfälliga och gallras efter avslutad tremånadersuppföljning plus en kort, fastställd administrativ period; retention konfigurerbar, inget evigt standardvärde, produktionsstart med riktiga deltagare blockeras tills perioden är fastställd. (U-3 flyttat hit från olöst arkitektur.)


Inga ytterligare olåsta arkitekturval kvarstår. Inga konflikter mellan Människan först, integriteten och dessa beslut har identifierats.


=== SLUTSTATUS ===


ARKITEKTUR LÅST. REDO FÖR SEPARAT IMPLEMENTATIONORDER.


Ingen kod, ingen commit, ingen push, ingen deployment, ingen databasmigrering, ingen förändring av Human Test eller produktion har skett i denna order.
