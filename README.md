# Kalkylprogram – Bygg & Entreprenad

Komplett kalkylverktyg för bygg- och entreprenadprojekt. Byggt i Python med tkinter-GUI.

## Funktioner

- Projekthantering med automatisk mappstruktur
- Kalkylrader (Material / Arbete / UE) med automatiska beräkningar
- Prisbank med Excel-import (BK2009 m.fl.)
- BKI-index för prisomräkning (2018–2026)
- Mallar – spara och återanvänd kalkylblock
- Byggdelar – summering per del
- Dokumenthantering
- Slutsida med full ekonomikalkyl (självkostnad, TB, marginal)
- Export till Excel och PDF

## Starta

```bash
pip install pandas openpyxl reportlab
python kalkylprogram.py
```

## Bygga EXE (Windows)

Dubbelklicka på `bygg_exe.bat` – skapar `dist/Kalkylprogram.exe`.

## Krav

- Python 3.10+
- pandas, openpyxl, reportlab

---
Utvecklat av Jan Stefors – Ledarskap utan filter
