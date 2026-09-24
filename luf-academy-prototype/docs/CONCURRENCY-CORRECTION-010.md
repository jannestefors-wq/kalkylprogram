# Concurrency correction 010. Revisionskontroll för befintliga svar

Datum: 2026-09-24. Uppdrag: LUF ACADEMY LHM CONCURRENCY CORRECTION 010.

**Gammal baseline:** `edfda82`. **Ny Source of Truth för re-verifiering:** commiten som innehåller denna fil på branchen `claude/ledarskap-vecka-1-prototype-7sy98p`.

## Works fynd i verifiering 009
Servern accepterade en uppdatering av ett befintligt svar utan `baseRevision`. Ett sådant anrop kunde ersätta ett nyare svar utan konflikt.

## Rotorsak

**1. Servern** (`server/app.mjs`, `putEntry`).
- Revisionskontrollen var villkorad på att klienten skickade en revision: `if (baseRevision != null && Number(baseRevision) !== existing.revision)`. När `baseRevision` saknades hoppades jämförelsen över.
- Uppdateringen gjordes sedan ovillkorligt: `UPDATE lr_entry … WHERE id = ?`.
- Jämförelsen gjordes i applikationskod och skrivningen i en separat sats. I Node-prototypen skyddades det av att varje anrop körs synkront i en `BEGIN IMMEDIATE`-transaktion. Det skyddet finns inte i en miljö med flera processer eller i D1, som inte har interaktiva transaktioner.

**2. Klienten** (`public/app.js`). Samma fel kunde nås på en andra väg.
- Osparad text lagrades lokalt utan den revision den skrevs mot. Vid återställning, efter omladdning eller nätfel, användes i stället *serverns senaste* revision (`payload.baseRevision ?? known.revision`).
- En gammal lokal text kunde då skriva över en nyare version från en annan enhet, utan att servern kunde upptäcka det.
- Vid konflikt togs den lokala texten dessutom bort ur webbläsarens lagring. Den låg kvar i fältet men försvann vid omladdning.

## Lösning

**Servern**
- `baseRevision`, om den skickas, måste vara ett heltal ≥ 0. Annars svarar servern 400 `invalid_base_revision`.
- **Nytt svar** (ingen rad finns):
  - Skapas utan revision, eller med `baseRevision: 0`.
  - `baseRevision > 0` ger 409.
  - Insättningen är villkorlig: `INSERT … ON CONFLICT (enrollment_id, step_key, field_key) DO NOTHING`. Hann någon annan skapa svaret först blir det 409.
- **Befintligt svar**:
  - Saknad `baseRevision` ger **428 `base_revision_required`**. Ingenting skrivs och ingen text skickas tillbaka.
  - En `baseRevision` som skiljer sig från aktuell revision ger **409 `conflict`**.
- **Atomisk skrivning:** `UPDATE lr_entry SET … revision = revision + 1 … WHERE id = ? AND revision = ?`. Jämförelse och skrivning är en och samma sats. Uppdateras ingen rad blir det 409, och transaktionen rullas tillbaka, historikraden inräknad.
- Oförändrat:
  - Historik per skrivpass.
  - Lås (423).
  - Behörighet och integritetsmodellen.
  - Samma text som redan är sparad ger ingen ny revision.

**Klienten**
- Varje osparad text bär den revision den skrevs mot (`baseRevision`), från första tangenttryckningen och genom omladdning.
- Ingen reserv till serverns senaste revision.
- Efter en lyckad sparning får text som skrevs under sparningen den nya revisionen. Revisionen går 1, 2, 3.
- Vid 409 ligger texten kvar i fältet **och** i webbläsaren, märkt som konflikt. Den skickas inte igen av sig själv.
  - Konfliktrutan visas även om konflikten upptäcks innan fältet har ritats, till exempel efter omladdning.
  - Sparstatusen fastnar inte på "Sparar".
- *Behåll min text* sparar det som står i fältet nu, mot den nya revisionen. *Använd den sparade* tar bort den lokala texten först när deltagaren har valt.
- Valfält (ett klick) visar vid konflikt det sparade valet öppet, och deltagaren kan välja igen.
- Omladdning i konflikt: texten återställs, skickas mot sin ursprungliga revision, får konflikt och visas igen. Ingen tyst överskrivning.
- Retry vid nätfel använder alltid textens egen revision. Har den blivit gammal svarar servern 409.

**Förhandsvisningen** (`preview/transport.js`) har samma kontrakt: ett befintligt svar utan `baseRevision` ger 428.

**Begränsning.** Förhandsvisningen lagrar i claude.ai:s databas, och den har ingen villkorlig skrivning. Den atomiska garantin gäller servern. Förhandsvisningen är en testmiljö, inte produktionsvägen.

## API-kontrakt efter fix
`PUT /api/journey/:enrollmentId/entry`, body `{ step, field, value, baseRevision }`.

| Läge | baseRevision | Svar |
| --- | --- | --- |
| Inget svar finns | saknas eller 0 | 200 `{ revision: 1, savedAt }`. Tom text sparas inte: `{ revision: 0 }` |
| Inget svar finns | > 0 | 409 `{ error: "conflict", revision: 0, value: "", updatedAt: null }` |
| Svar finns | saknas | 428 `{ error: "base_revision_required" }` |
| Svar finns | = aktuell | 200 `{ revision: aktuell + 1, savedAt }` |
| Svar finns | ≠ aktuell | 409 `{ error: "conflict", revision, value, updatedAt }`. Deltagarens egen text, för att kunna välja. |
| Valfritt läge | inte heltal ≥ 0 | 400 `{ error: "invalid_base_revision" }` |

Konflikter och avvisningar (409, 428, 400) loggas inte. Servern skriver bara ut oväntade fel (500) som stackspår.

## Filer ändrade
- `server/app.mjs`: `putEntry`.
- `public/app.js`: autosparningen, återställning och konfliktvisning för text och val.
- `preview/transport.js`: samma kontrakt.
- `tests/api.test.mjs`: sju nya tester och ett ändrat.
- `tests/e2e.test.mjs`: ett nytt test.
- `README.md` och denna fil.
- **Oförändrat:**
  - `server/content.mjs` och allt deltagarinnehåll. Diffen mot `edfda82` är tom.
  - Schema och migreringar.
  - Roller, delning, analytics, design och routing.

## Nya tester
| Test | Verifierar |
| --- | --- |
| 010 test 1 | Nytt svar utan revision, och med revision 0, skapas |
| 010 test 2 och autosparning | Rätt revision. Revisionen går 1, 2, 3 |
| 010 test 3 | Revision 4 mot 5 ger konflikt. Databasen har kvar revision 5 och dess text |
| 010 test 4 | Befintligt svar utan revision ger 428, också med `null`. Felaktig typ ger 400. Text, revision och historik är oförändrade. **Täcker Works fynd direkt.** |
| 010 test 5 och 6 | Scenariot med revision 7 och texterna A, B och C: B lyckas, C får konflikt, B ligger kvar |
| 010 samtidiga anrop | Fem samtidiga uppdateringar mot samma revision: exakt en lyckas, fyra får konflikt. Tre samtidiga skapanden: exakt ett lyckas |
| 010 test 8 | En konflikt efter ett avslutat skrivpass skapar ingen historikrad. En verklig skrivning gör det |
| e2e, order 010 | Två webbläsare. Konflikten visas och den lokala texten ligger kvar i fältet och i lagringen. Efter omladdning finns text och konflikt kvar. Servern är orörd tills deltagaren väljer. *Behåll min text* och *Använd den sparade* fungerar båda |

**Ändrat gammalt test.** *historik sparas per skrivpass* skrev om samma fält tre gånger utan revision och byggde alltså på felet. Det skickar nu revisionerna 0, 1 och 2 och kontrollerar att svaren ger 1, 2 och 3. Förväntningen på historiken är oförändrad.

**Prövat mot gammal kod**
- Med serverkoden från `edfda82` faller *010 test 4*.
- Med klientkoden från `edfda82` faller e2e-testet för order 010.
- Samtidighetstestet går igenom även med den gamla servern. Node kör varje anrop synkront inom en transaktion, så i en och samma process flätas två anrop aldrig ihop. Den villkorliga SQL-satsen är skyddet för miljöer med flera processer eller D1.

## Testresultat
| Svit | Resultat |
| --- | --- |
| API, `npm test` | 35 av 35, tidigare 28 |
| E2E i Chromium, `npm run test:e2e` | 8 av 8, tidigare 7 |
| Förhandsvisningen i Chromium | 10 av 10 |
| Bokkontrollen | 108 av 108 |
| Bygget av förhandsvisningen | Utan fel. Inte publicerad, eftersom korrigeringen inte kräver det för att testas. |

## Kvarstående
- Förhandsvisningen saknar atomisk skrivning, eftersom claude.ai:s databas inte har villkorlig skrivning. Se ovan.
- Webbläsartesterna kräver Chromium. Works verifieringsmiljö saknade det i 009.
- Nästa steg är **WORK INDEPENDENT REVERIFICATION 011** mot den nya commiten.
