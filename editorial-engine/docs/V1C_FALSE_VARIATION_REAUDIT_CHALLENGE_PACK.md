# LUF Editorial Engine. V1C False Variation Independent Re-Audit Challenge Pack

**Status:** Fryst redaktionellt audit-underlag. Inte canonical data, inte kodspecifikation och inte en del av Editorial Memory.

**Ägarskap:** Work. **Blind princip:** Detta facit är satt före teknisk re-audit och får inte ändras efter att Claude Code fått paketet.

**Källintegritet:** Samtliga 50 par är nya syntetiska auditfall, skrivna för att pröva redaktionell bedömning. De är inte publicerade LUF-texter, inte D1–D3, inte N06 och inte correction-testfall. De härleder bara sina bedömningsprinciper från den frysta V1C Evidence Master.

## Facitnyckel

- **FALSE_VARIATION_HIGH_RISK:** samma redaktionella konstruktion i nya kläder.
- **LEGITIMATE_VARIATION:** samma Voice Core får bära en ny behandling.
- **AMBIGUOUS_HUMAN_DECISION:** evidens åt båda håll. Systemet bör flagga, inte låsa beslutet.
- **INSUFFICIENT_EVIDENCE:** texten är för kort eller underbestämd för en hård structural-dom.

Varje rad har: `ID | svårighet | text A | text B | facit | thesis | mänsklig situation | lens | movement | closure | lexical | grund`.

## A. Same construction. Low lexical. 10 scenarios

| ID | Svårighet | Text A | Text B | Facit | Relationer och redaktionell grund |
|---|---|---|---|---|---|
| SC01 | ADVERSARIAL | “Hon log när planen ändrades för tredje gången. Sedan slutade hon boka in folk.” | “Efter ännu en omritad vecka tackade hon ja till färre uppdrag. Till sist försvann hennes initiativ ur kalendern.” | FALSE_VARIATION_HIGH_RISK | Samma thesis: osäkerhet dränerar handlingskraft. Samma person, distans och lens. Rörelse: vardagsignal → upprepad instabilitet → tillbakadragande. Samma öppna sorgliga closure. Låg lexikal likhet. |
| SC02 | ADVERSARIAL | “När chefen sa ‘vi återkommer’ för sjätte gången blev frågan mindre. Till slut fanns den inte.” | “Beslutet sköts fram tills ingen längre tog upp det. Tystnaden såg ut som samsyn.” | FALSE_VARIATION_HIGH_RISK | Samma tystnadsmekanism, samma mötessituation, samma rörelse: uppskjutande → krympande röst → falsk enighet. |
| SC03 | ADVERSARIAL | “Han bar nycklarna till alla svar. När han var sjuk stannade våningen.” | “All kunskap hade fått ett namn. Den dagen namnet saknades stod arbetet still.” | FALSE_VARIATION_HIGH_RISK | Samma thesis och situation: personbunden kunskap. Rörelse: centralisering → frånvaro → driftstopp. |
| SC04 | ADVERSARIAL | “De mätte timmarna noga. Ingen frågade varför folk slutade stanna kvar.” | “Tavlan fylldes av siffror medan de erfarna försvann en i taget.” | FALSE_VARIATION_HIGH_RISK | Samma lens: mått före verklighet. Rörelse: synlig kontroll → osynlig förlust → implicit anklagelse. |
| SC05 | ADVERSARIAL | “Hon kom sent. Gruppen bestämde snabbt att hon inte brydde sig.” | “En försenad stol blev bevis för bristande vilja innan någon visste vad som hänt.” | FALSE_VARIATION_HIGH_RISK | Samma situation och slutsatsfunktion. Rörelse: händelse → motivtillskrivning → varning för förhastad dom. |
| SC06 | ADVERSARIAL | “De bad om mod. Sedan straffade de den som sa emot först.” | “I rummet uppmuntrades uppriktighet. Efteråt stod den rakaste personen ensam.” | FALSE_VARIATION_HIGH_RISK | Samma human situation och lens: uttalad öppenhet mot social bestraffning. Rörelse och closure är samma. |
| SC07 | ADVERSARIAL | “Varje fel fick en ny kontrollpunkt. Till slut behövde ingen tänka.” | “Efter varje miss byggdes ännu en spärr. Slutligen väntade alla på instruktion.” | FALSE_VARIATION_HIGH_RISK | Samma thesis. Rörelse: fel → kontrollökning → förlorat omdöme. |
| SC08 | ADVERSARIAL | “Han löste allt själv. Teamet blev lugnt. Och mindre.” | “När samma person alltid räddade dagen slutade resten att växa.” | FALSE_VARIATION_HIGH_RISK | Samma aktör, rörelse och slut: hjältebeteende → beroende → kapacitetsförlust. |
| SC09 | ADVERSARIAL | “De kallade det effektivisering. Först försvann pausen. Sedan samtalen som fångade upp det som höll på att gå fel.” | “Tid sparades genom att stryka mellanrummen. Det som försvann var platsen där små varningar brukade komma fram.” | FALSE_VARIATION_HIGH_RISK | Samma konstruktion: åtgärd → förlust av informellt informationsflöde → följdrisk. |
| SC10 | ADVERSARIAL | “Hon fick ansvar utan mandat. När det brast kallades det brist på ägarskap.” | “Uppdraget lades på henne, men besluten stannade någon annanstans. Efteråt fick hon bära etiketten.” | FALSE_VARIATION_HIGH_RISK | Samma makt/ansvar-missmatch och samma avslöjandeordning. |

## B. High lexical. Different construction. 10 scenarios, including HL4/HSB1

| ID | Svårighet | Text A | Text B | Facit | Relationer och redaktionell grund |
|---|---|---|---|---|---|
| SC11 | ADVERSARIAL | “Det började med att ingen sa något på mötet. Efteråt gick alla hem med samma fråga.” | “Det började med att ingen sa något på mötet. Men efteråt ringde två personer chefen och ändrade beslutet.” | LEGITIMATE_VARIATION | HL4. Identisk opening. A går tystnad → kvarstående osäkerhet. B går tystnad → privat motmakt → faktisk förflyttning. Olika closure och läsarresa. |
| SC12 | ADVERSARIAL | “Det började med att ingen sa något på mötet. Frågan dog innan den hann bli obekväm.” | “Det började med att ingen sa något på mötet. Den nya medarbetaren skrev ner allt och tog upp det sex veckor senare.” | LEGITIMATE_VARIATION | HL4. Samma start, men A visar försvinnande. B visar minne, tid och återkomst. |
| SC13 | ADVERSARIAL | “Vi behöver mer ansvar. Men först måste någon kunna fatta beslut.” | “Vi behöver mer ansvar. Därför lät vi den som var närmast kundens vardag skriva nästa veckas prioritering.” | LEGITIMATE_VARIATION | HL4. Samma ord, olika lens. A blottar mandatglapp. B visar delegerad praktik. |
| SC14 | ADVERSARIAL | “Kulturen syns i det som händer när någon gör fel.” | “Kulturen syns i det som händer när någon gör fel. I vår grupp blev felet början på ett bättre arbetssätt.” | LEGITIMATE_VARIATION | HL4. A är definition och öppen fråga. B är efterhandsreflektion och lärande. |
| SC15 | ADVERSARIAL | “Det som inte sägs styr mer än det som sägs.” | “Det som inte sägs styr mer än det som sägs. Ibland är det också det som skyddar en människa tills hon själv vill tala.” | LEGITIMATE_VARIATION | HL4. Gemensam opening. A bär maktkritik. B bär omsorg och autonomi. |
| SC16 | ADVERSARIAL | “Ingen ville vara den som bromsade.” | “Ingen ville vara den som bromsade. Därför stannade alla fem minuter och frågade vad farten dolde.” | LEGITIMATE_VARIATION | HL4. A kan leda till flockdynamik. B går mot ritual för omdöme. |
| SC17 | ADVERSARIAL | “När siffrorna blev röda började de leta syndabockar.” | “När siffrorna blev röda började de leta syndabockar. Det visade sig att den största bristen fanns i anbudet från två år tidigare.” | LEGITIMATE_VARIATION | HL4. Samma öppning och ord. A stannar i mänsklig mekanism. B flyttar till tidsfördröjd systemorsak. |
| SC18 | ADVERSARIAL | “Han sa att dörren alltid var öppen.” | “Han sa att dörren alltid var öppen. Därför skrev hon ett brev i stället för att gå in.” | LEGITIMATE_VARIATION | HL4. Samma phrase. A kan handla om tillit. B gör den mänskliga distansen central och använder brevform. |
| SC19 | INTERMEDIATE | “Ansvar, tillit och tydlighet behöver hållas ihop.” | “Ansvar, tillit och tydlighet behöver hållas ihop. Först berättar en lärling varför han aldrig frågar.” | LEGITIMATE_VARIATION | Hög lexikal och samma thesis. A är syntes. B är scen → personlig kostnad → därefter princip. |
| SC20 | ADVERSARIAL | “Vi såg samma problem. Vi gjorde olika saker åt det.” | “Vi såg samma problem. Vi gjorde olika saker åt det. Den ena gruppen räknade avvikelser. Den andra satte sig med den som alltid gick tyst från mötet.” | LEGITIMATE_VARIATION | Samma opening och topic. Den andra texten kontrasterar två lenses och ger ny situation. |

## C. Near-threshold and ambiguous cases. 10 scenarios

| ID | Svårighet | Text A | Text B | Facit | Relationer och redaktionell grund |
|---|---|---|---|---|---|
| SC21 | ADVERSARIAL | “De ville höja motivationen. Först tog de bort allt som gjorde jobbet omöjligt.” | “De ville höja motivationen. Först frågade de varför ingen längre kände sig behövd.” | AMBIGUOUS_HUMAN_DECISION | Samma topic och systemblick. A går hinder → kapacitet. B går tillhörighet → mening. Tydlig behandling skillnad, men samma diagnosprincip. |
| SC22 | ADVERSARIAL | “Han avbröt henne tre gånger. Fjärde gången sa hon ingenting.” | “Han avbröt henne tre gånger. Fjärde gången började gruppen se på sina egna händer.” | LEGITIMATE_VARIATION | Samma scen, ny lens. A följer den tystnade personen. B följer åskådarnas delaktighet. |
| SC23 | ADVERSARIAL | “Vi behövde få fart på projektet. Så vi tog bort varje fråga som inte hade en ägare.” | “Vi behövde få fart på projektet. Så vi lät varje obesvarad fråga ligga kvar på väggen en vecka.” | LEGITIMATE_VARIATION | Samma råläge, motsatt movement och closure. |
| SC24 | ADVERSARIAL | “Hon var lojal. Därför sa hon inget när beslutet skadade gruppen.” | “Hon var lojal. Därför tog hon upp beslutet först med den som hade fattat det.” | AMBIGUOUS_HUMAN_DECISION | Båda handlar om lojalitet i maktrelation. A visar tystnad. B visar lågmäld invändning. Gränsfall. |
| SC25 | ADVERSARIAL | “De sa att alla fick komma till tals. Sedan gick ordet alltid samma väg runt bordet.” | “De sa att alla fick komma till tals. Sedan lät de den yngsta börja.” | LEGITIMATE_VARIATION | Identiskt språkligt anslag. A avtäcker ritualiserad makt. B ändrar ordningen som åtgärd. |
| SC26 | ADVERSARIAL | “När han slutade svara på kvällarna trodde de att han tappat engagemanget.” | “När han slutade svara på kvällarna förstod de till sist att arbetet hade ätit upp hans gränser.” | AMBIGUOUS_HUMAN_DECISION | Samma händelse och perspektivskifte, men B landar i arbetsmiljö snarare än feltolkning. Risk men legitimt argument finns. |
| SC27 | ADVERSARIAL | “De kallade honom motståndare eftersom han bad om en ritning som gick att bygga.” | “De kallade honom motståndare. Han använde ordet och berättade vad han var rädd att de skulle missa.” | LEGITIMATE_VARIATION | Samma ord och figur. A systemets etikettering. B personen tar tillbaka berättelsen. |
| SC28 | ADVERSARIAL | “Vi har en kulturfråga, sa de. Men ingen kunde nämna ett enda återkommande beteende.” | “Vi har en kulturfråga, sa de. Därför följde de tre veckors vardag innan de satte namn på den.” | LEGITIMATE_VARIATION | Samma thesis family. A diagnostisk kritik. B metodisk observation. |
| SC29 | ADVERSARIAL | “Det var inte ett dåligt beslut. Det var ett beslut som ingen längre förstod varför det fanns.” | “Det var inte ett dåligt beslut. Det var ett beslut som blev dyrt därför att ingen vågade ändra det.” | AMBIGUOUS_HUMAN_DECISION | Delar omramning och objekt. A fokuserar organisatoriskt minne. B fokuserar rädsla och eskalerande kostnad. |
| SC30 | ADVERSARIAL | “Hon ville göra rätt. Därför följde hon processen fast kunden stod bredvid och väntade.” | “Hon ville göra rätt. Därför bad hon om lov att tillfälligt lämna processen.” | AMBIGUOUS_HUMAN_DECISION | Samma människa och dilemma, motsatt handlingsrörelse. Båda kan vara samma kärnfråga om omdöme. |

## D. Human Situation Boundary. 10 scenarios

| ID | Svårighet | Text A | Text B | Facit | Relationer och redaktionell grund |
|---|---|---|---|---|---|
| SC31 | INTERMEDIATE | “På byggmötet nickade alla åt tidsplanen. Efteråt ritade platschefen om den ensam.” | “Vid köksbordet nickade alla åt semesterplanen. Efteråt bokade mamman om allt själv.” | LEGITIMATE_VARIATION | HSB-A. Samma movement: offentlig samsyn → privat korrigering. Mänsklig situation och konsekvensrum är genuint olika. |
| SC32 | INTERMEDIATE | “När kunden höjde rösten slutade montören förklara.” | “När läraren höjde rösten slutade eleven räcka upp handen.” | LEGITIMATE_VARIATION | HSB-A. Samma tystnadsrörelse men olika beroende, makt och läsarupplevelse. |
| SC33 | INTERMEDIATE | “Hon stannade kvar efter mötet för att förstå varför ritningen ändrats.” | “Han stannade kvar efter middagen för att förstå varför sonen slutat berätta.” | LEGITIMATE_VARIATION | HSB-A. Samma disposition mot avstånd, men arbetsrelation och familjerelation är inte utbytbara behandlingar. |
| SC34 | ADVERSARIAL | “Ingen ifrågasatte den nye vd:n under första kvartalet.” | “Ingen ifrågasatte den nye tränaren under första säsongen.” | LEGITIMATE_VARIATION | HSB-A. Samma formella startmakt, men kollektivets kontrakt och insats skiljer situationerna. |
| SC35 | INTERMEDIATE | “När kalkylen sprack letade de efter den som räknat fel.” | “När festen blev för dyr letade familjen efter den som bokat fel.” | LEGITIMATE_VARIATION | HSB-A. Strukturell likhet men olika mänsklig verklighet och ansvarsfördelning. |
| SC36 | ADVERSARIAL | “Hon avbröts tre gånger. Fjärde gången sa hon ingenting.” | “Hon avbröts tre gånger. Fjärde gången bad hon alla andra skriva ner vems frågor som aldrig fick plats.” | LEGITIMATE_VARIATION | HSB-B. Samma situation. A tystnad och förlust. B gör scenen till kollektiv observation och handling. |
| SC37 | ADVERSARIAL | “Chefen kom sent. Gruppen tänkte att han inte brydde sig.” | “Chefen kom sent. Gruppen började med vad de faktiskt visste och frågade sedan om brandlarmet i hans hus.” | LEGITIMATE_VARIATION | HSB-B. Samma situation. A narrativ om avsikt. B observation → omsorg → kontext. |
| SC38 | ADVERSARIAL | “Projektet var försenat. Alla bad om en ny plan.” | “Projektet var försenat. Den yngsta i gruppen berättade vad hon hade slutat rapportera för tre veckor sedan.” | LEGITIMATE_VARIATION | HSB-B. Samma råläge. A processfix. B informationens mänskliga förlust. |
| SC39 | ADVERSARIAL | “Han fick mer ansvar. Sedan satt han ensam med besluten.” | “Han fick mer ansvar. Sedan samlade han dem som bar följderna innan han bestämde något.” | LEGITIMATE_VARIATION | HSB-B. Samma mandat. A isolering. B relationell beslutskraft. |
| SC40 | ADVERSARIAL | “Hon såg felet först. Ingen lyssnade.” | “Hon såg felet först. Hon visade tre små tecken innan hon sa vad hon trodde.” | LEGITIMATE_VARIATION | HSB-B. Samma utgång. A makt/tystnad. B evidens och pedagogisk förflyttning. |

## E. OOV, movement order, asymmetry and short-full cases. 10 scenarios

| ID | Svårighet | Text A | Text B | Facit | Relationer och redaktionell grund |
|---|---|---|---|---|---|
| SC41 | ADVERSARIAL | “När dörrarna låstes lite tidigare försvann de små samtalen först. Sen började folk gå hem med sådant de annars hade lagt på bordet.” | “En kvart drogs bort från dagen. Det var inte minuterna som saknades utan platsen där halvfärdiga tankar brukade bli hörda.” | FALSE_VARIATION_HIGH_RISK | OOV. Samma thesis, situation och rörelse: tidspress → förlorat mellanrum → undanhållen information. Undviker vanliga triggerord. |
| SC42 | ADVERSARIAL | “Hon höll i trådarna tills trådarna höll i henne.” | “Allt gick genom honom. När han tappade fotfästet tappade avdelningen riktning.” | FALSE_VARIATION_HIGH_RISK | OOV. Personcentralisering → ömsesidigt beroende → kollektiv sårbarhet. |
| SC43 | ADVERSARIAL | “De putsade på tavlan varje fredag. Det som skavde i korridoren följde aldrig med in.” | “Veckans bild blev renare och renare. Samtidigt slutade de tala om det som gjorde jobbet tyngre.” | FALSE_VARIATION_HIGH_RISK | OOV. Synlig uppföljning → utesluten vardagsverklighet → tystnad. |
| SC44 | ADVERSARIAL | “Han blev den som alla frågade. Till sist hörde ingen längre sin egen tanke.” | “Varje väg pekade mot samma skrivbord. När skrivbordet var tomt stod resten stilla.” | FALSE_VARIATION_HIGH_RISK | OOV. Samma konstruktion som beroende-fallen men ny bildvärld. |
| SC45 | ADVERSARIAL | “Först kom notan. Sedan förklaringen. Sist berättade de om morgonen då ingen orkade ringa kunden.” | “De började med en trött röst vid kaffemaskinen, följde den till en utebliven återkoppling och landade i siffran på sista raden.” | LEGITIMATE_VARIATION | Movement-order. Samma element kan finnas, men A går utfall → orsak → människa. B går människa → kedja → utfall. Olika upptäcktsordning och upplevelse. |
| SC46 | ADVERSARIAL | “Hon såg stolens tomrum. Hon antog att han hade gett upp. Först senare förstod hon att han satt på akuten.” | “Akuten kom först i berättelsen. Sedan visade texten hur ett tomt säte blev till en snabb dom.” | LEGITIMATE_VARIATION | Movement-order. Samma situation och insikt, men A låter läsaren göra misstaget. B ger kunskap före domen. |
| SC47 | ADVERSARIAL | “De såg tre sena leveranser och tänkte att allt var på väg åt fel håll.” | “Tre sena leveranser. Ett mönster. En riktning.” | AMBIGUOUS_HUMAN_DECISION | Asymmetri. B kan vara en genuin kort sammanfattning av A, men saknar A:s tolkning och osäkerhet. Människa avgör. |
| SC48 | ADVERSARIAL | “Hon sa nej till ännu en genväg. Först blev hon ensam. Sedan slapp hela laget rätta felet i efterhand.” | “Hon stod fast. Det räckte.” | INSUFFICIENT_EVIDENCE | Asymmetri/short full. B delar möjligt motiv men kan inte säkert bedömas som samma konstruktion. |
| SC49 | ADVERSARIAL | “Han tittade ner när frågan kom.” | “Hon tittade ner när frågan kom.” | INSUFFICIENT_EVIDENCE | Short FULL/default. Samma yta, ingen observerbar movement, ingen hård similarity-dom får följa av UNKNOWN. |
| SC50 | ADVERSARIAL | “Ingen svarade.” | “Ingen lyssnade.” | INSUFFICIENT_EVIDENCE | Short FULL/default. Orden antyder närhet men saknar situation, lens, rörelse och closure. |

## Coverage and frozen ground truth

| Krav | Täcks av |
|---|---|
| Same construction / low lexical, minst 10 | SC01–SC10. 10 |
| High lexical / different construction, minst 10 | SC11–SC20. 10 |
| Near-threshold, minst 10 | SC21–SC30. 10 |
| Human Situation Boundary, minst 10 | SC31–SC40. 10 |
| OOV / unusual paraphrase, minst 10 | SC01–SC10 och SC41–SC44. 14 |
| HL4/HSB1, minst 8 | SC11–SC18. 8 |
| Motsatt opening, minst 5 | SC01–SC10 och SC41–SC44. 14 |
| Same Thesis / New Treatment, minst 5 | SC11–SC20, SC22–SC28, SC36–SC40. 21 |
| Different Thesis / Same Construction, minst 5 | SC01–SC10, SC31–SC35, SC41–SC44. 19. Detta betyder structural närhet, inte automatiskt same claim. |
| Movement-order, minst 5 | SC21–SC23, SC36–SC40, SC45–SC46. 10 |
| Asymmetric sequence, minst 6 | SC41–SC44, SC47–SC48. 6 |
| Short FULL/default, minst 5 | SC12, SC29–SC30, SC47–SC50. 7 |
| AMBIGUOUS_HUMAN_DECISION, minst 5 | SC21, SC24, SC26, SC29, SC30, SC47. 6 |
| ADVERSARIAL, minst 25 | SC01–SC18, SC21–SC30, SC36–SC50. 45 |

## Re-audit use boundary

Claude Code may read the inputs, compare its results to the frozen editorial relation and report deviations. Claude Code may not modify, normalize, enrich or replace this packet. A mismatch is evidence for audit discussion, not a reason to revise the frozen ground truth.

**SLUTSTATUS: V1C FALSE VARIATION BLIND CHALLENGE PACK FRYST. REDO FÖR OBEROENDE RE-AUDIT**
