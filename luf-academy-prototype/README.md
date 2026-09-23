# LUF Academy. Min ledarskapsresa. Prototyp

Utbildningen **Ledarskap med hjärta och mod**. Sex veckor, live i grupper om högst sex. Detta är en isolerad prototyp av deltagarens digitala arbetsyta. Hela programmet är byggt: sex veckor, 30 dagar och samtal med Jan.

Den ligger avsiktligt utanför LUF-produktionen. Se `docs/READ-ONLY-ANALYS.md` för varför.

## Förhandsvisning för Human Test

Privat sida på claude.ai: https://claude.ai/artifact/EWhqnURcS4QVh1a5uZDF7S

Öppna den inloggad på claude.ai och tryck Logga in som testdeltagare. Testläget på översikten flyttar dig genom veckorna. Byggs med `node --no-warnings scripts/build-preview.mjs`. Testas med `node --no-warnings --test tests/preview.test.mjs`. Se `docs/HUMAN-TEST-PREVIEW-002.md`.

## Köra lokalt

Kräver Node 22.13 eller senare. Inga beroenden att installera.

```bash
cd luf-academy-prototype
npm run seed     # skapar data/prototype.db och personliga inloggningslänkar
npm start        # http://127.0.0.1:4310
```

Länkarna skrivs ut och sparas i `data/inloggningslankar.txt`. En länk gäller i 21 dagar och kan användas på flera enheter.

| Testkonto | Visar |
| --- | --- |
| Testdeltagare Jan | Deltagare i Grupp A. Använd för testet. |
| Anna, Karim (fiktiva) | Andra deltagare i Grupp A |
| Lena, Oskar (fiktiva) | Deltagare i Grupp B |
| Jan Stefors | Handledare. Ser bara det som delats med honom. |
| Programadministratör | Grupper, datum, Teamslänkar. Ingen fritext. |

## Testa

```bash
npm test          # 23 tester mot servern
npm run test:e2e  # 7 tester i Chromium mot servern
node --no-warnings --test tests/preview.test.mjs  # 8 tester av förhandsvisningen, hela programmet på desktop och mobil
```

## Miljövariabler

| Variabel | Standard | Betydelse |
| --- | --- | --- |
| `PORT`, `HOST` | `4310`, `127.0.0.1` | Adress |
| `LR_DB` | `data/prototype.db` | Databasfil |
| `LR_IDENTITY_MODE` | `prototype-link` | `sites-header` följer produktionens ChatGPT Sites-identitet |
| `LR_SECURE_COOKIES` | av | Sätt `1` bakom HTTPS |
| `LR_PROTOTYPE` | på | `0` döljer prototypmarkeringar och testläget |
| `LR_BASE_URL` | `http://127.0.0.1:4310` | Används i utskrivna länkar |

## Struktur

```
server/content.mjs      Innehållsregistret. Alla steg, moment och fält. Enda källan.
server/migrations/      Datamodellen. SQLite, D1-kompatibel, prefix lr_.
server/app.mjs          Behörighet, autosparning, historik, delning, mätning.
public/                 Arbetsytan. Ingen extern kod.
docs/                   Analys, datagränser och GDPR, rollback, leveransrapport.
```

Allt innehåll står i `server/content.mjs`. Reglerna för öppna steg, lås och status står i `server/rules.mjs` och används av både servern och förhandsvisningen.

Källor och sidreferenser ligger internt i registret och skickas aldrig till deltagaren. Bokhänvisningar kontrolleras mot boken med `LHM_BOOK_TXT=<bokens text> node scripts/verify-book-references.mjs`. Boktexten läggs aldrig i repot.

## Dokument

- `docs/LEVERANSRAPPORT-004.md`. Rensning av deltagarvyn. Status enligt order 004.
- `docs/LEVERANSRAPPORT-003.md`. Hela utbildningen. Status enligt order 003.
- `docs/LHM-SIX-WEEK-SOURCE-CROSSWALK-001.md`. Källkarta från bok och arbetsbok till sex veckor.
- `docs/HUMAN-TEST-PREVIEW-002.md`. Förhandsvisningen och analysen av fyra utelämnade moment.
- `docs/LEVERANSRAPPORT-VECKA-1.md`. Status enligt order 001.
- `docs/READ-ONLY-ANALYS.md`. Vad som fanns före.
- `docs/DATAGRANSER-OCH-GDPR.md`. Vem ser vad. Öppna frågor.
- `docs/ROLLBACK.md`
