# Kalkylprogram – Bygg & Entreprenad

## Starta direkt (utan att bygga EXE)

1. Installera Python 3.10+ från [python.org](https://python.org)
2. Öppna ett terminalfönster i den här mappen
3. Kör:
   ```
   pip install pandas openpyxl reportlab
   python kalkylprogram.py
   ```

---

## Bygga en EXE-fil (Windows)

1. Dubbelklicka på `bygg_exe.bat`
2. Vänta 1–3 minuter
3. Din EXE finns i mappen `dist\Kalkylprogram.exe`
4. Kopiera EXE-filen vart du vill – den är fristående

---

## Funktioner

### Flikar
| Flik | Innehåll |
|------|----------|
| Start | Projektöversikt, senaste projekt |
| Projekt | Projektinfo, mappstruktur |
| Kalkyl | Alla kalkylrader med beräkningar |
| Prisbank | Artikelregister, BKI-index |
| Mallar | Sparade radmallar |
| Byggdelar | Summering per byggdel |
| Dokument | Filhantering |
| Slutsida | Full ekonomikalkyl |

### Kalkylrader
- **Material**: Mängd × Á-pris
- **Arbete**: Timmar × Á-pris
- **Försäljningspris**: Kostnad × (1 + Påslag%)
- Dubbeklicka en rad för att redigera

### Export
- Excel: kalkyl + byggdelar / slutsida
- PDF: kalkyl / slutsida

### BKI-index
Räknar om priser mellan basår och målår.
Välj typ (Flerbostadshus / Småhus / ROT) och år.

---

## Datafiler (skapas automatiskt i programmappens katalog)
- `settings.json` – senaste projekt, inställningar
- `prisbank.json` – sparad prisbank
- `mallar.json` – sparade kalkylmallar
- `*.json` – ett projekt per fil (spara var du vill)

---

## Krav
- Windows 10/11 (EXE)
- Python 3.10+ (källkod)
- pandas, openpyxl, reportlab (installeras via pip)
