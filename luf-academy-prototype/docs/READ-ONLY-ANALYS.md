# READ ONLY-analys före kod

Genomförd 2026-09-23. Ingenting i produktion har ändrats.

## Källor som lästes

| Källa | Var |
| --- | --- |
| Produktionskod, verifierad snapshot | `jannestefors-wq/luf-house-audit-source`, arkiv v284, commit `ddb9d893` enligt README. Uttryckligen en read-only spegel. |
| 00_MASTERPLAN. LUF Akademin från ax till limpa | Drive |
| ACADEMY DOCUMENT STATUS MAP 001 | Drive |
| WEBBARKITEKTUR. Nycklar, behörigheter, konton, progression | Drive |
| KVALITET, GDPR OCH PUBLICERINGSGRINDAR | Drive |
| TEKNISKT NULÄGE. Befintlig Sites Akademi före nyckelsystem | Drive |
| Min ledarskapsresa MASTER v2 (Word) | Drive, primär källa för innehållet |
| Boken Ledarskap med hjärta och mod | **Finns inte i Drive.** Kunde inte läsas. |

PDF-versionen av arbetsboken lästes inte visuellt. Wordfilen är primär källa enligt ordern.

## Fakta om nuvarande produktion

| Område | Fakta |
| --- | --- |
| Plattform | ChatGPT Sites. vinext 0.0.50 (Next 16 API) på Cloudflare Workers. |
| Databas | Cloudflare D1 (SQLite) via Drizzle. Åtta tabeller: messages, reviews, silence_wall_entries, round_table_dilemmas, site_settings, editorial_notes, content_cases, house_content. |
| Inloggning | Sign in with ChatGPT. Plattformen sätter headern `oai-authenticated-user-email`. |
| Konton | **Inga deltagarkonton finns.** Ingen användartabell. Ingen behörighetsmodell. |
| Admin | `/admin` och `/akademi` släpper bara igenom en hårdkodad lista med Jans två adresser (`isJanAdmin`). |
| Nuvarande /akademi | Platshållare för Jan. Sju moduler och ett triangelbibliotek med Katalysatorinriktning. Hör inte till den här utbildningen. |
| Routing | `middleware.ts` styr svenska och engelska domäner och gamla omdirigeringar. `/akademi` och `/en/academy` finns. |
| Analys | Google Analytics 4 laddas i rotlayouten på varje sida och skickar `page_location` och `page_title`. |
| Ändringskontroll | `docs/LUF-CHANGE-CONTROL.md` låser hallens geometri, kamera, ljus och navigation mot baseline `LUF-BASELINE-2026-08-11`. |
| Designsystem | Färgvariabler i `app/globals.css`: bläck `#0b2034`, papper `#faf7ef`, bärnsten `#d4711e`. Georgia i rubriker, Geist i brödtext. |

## Tolkning

1. Det finns ingen deltagararkitektur att bygga vidare på. Både TEKNISKT NULÄGE och WEBBARKITEKTUR förbjuder att bygga ett medlemsområde innan en förstudie har besvarat frågorna A till J. Den här prototypen är därför själva förstudien i körbar form. Den läggs inte i produktionskoden.
2. Den enda inloggning som finns är ChatGPT-identiteten. Om den räcker för riktiga deltagare är ett affärsbeslut. En deltagare skulle behöva ett ChatGPT-konto för att logga in.
3. Google Analytics i rotlayouten skickar sidans URL och titel. Deltagarsidor i produktion måste undantas, annars kan avsnittsnamn och annan information hamna hos Google.
4. Arbetsboken är byggd för **tio veckor**. Ordern gäller **sex veckor**. Vecka 1 går att föra över rakt. Vecka 2 till 6 kräver att Jan bestämmer hur tio veckor blir sex.
5. Arbetsbokens läsanvisning för vecka 1 ("Utan filter + Människan först") är en kapiteltitel, inte kontrollerad mot den tryckta boken. Den visas därför inte för deltagare. Den står som HOLD FÖR JAN.

## Beslut som följer av analysen

- Prototypen byggs isolerat på branchen `claude/ledarskap-vecka-1-prototype-7sy98p` i en egen mapp. Inget i LUF-produktionen, i Sites-projektet eller i kalkylprogrammet berörs.
- Datamodellen skrivs som SQLite-migration med prefixet `lr_`. Den kan köras mot D1 utan att röra befintliga tabeller.
- Identitetslagret har två lägen. `sites-header` följer exakt produktionens kontrakt. `prototype-link` används bara för test, med personliga länkar i stället för lösenord.
- Ingen Google Analytics i prototypen. Mätningen är egen, förstapart och tar aldrig emot fritext.
- Ingen Katalysatormetodik, inga trianglar och inget från nuvarande /akademi återanvänds.
