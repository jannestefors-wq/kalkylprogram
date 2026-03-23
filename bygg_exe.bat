@echo off
title Bygger Kalkylprogram.exe...
echo ============================================
echo  Bygger Kalkylprogram.exe med PyInstaller
echo ============================================

:: Kontrollera Python
python --version >nul 2>&1
if errorlevel 1 (
    echo FEL: Python hittades inte. Installera Python 3.10+ fran python.org
    pause & exit /b 1
)

:: Installera beroenden
echo.
echo [1/3] Installerar beroenden...
pip install pandas openpyxl reportlab pyinstaller -q
if errorlevel 1 ( echo FEL vid installation. & pause & exit /b 1 )

:: Bygg EXE
echo.
echo [2/3] Bygger EXE (kan ta 1-3 minuter)...
pyinstaller --onefile ^
            --windowed ^
            --name "Kalkylprogram" ^
            --icon NONE ^
            --hidden-import pandas ^
            --hidden-import openpyxl ^
            --hidden-import reportlab ^
            --hidden-import reportlab.graphics ^
            --hidden-import reportlab.platypus ^
            --hidden-import reportlab.lib ^
            kalkylprogram.py

if errorlevel 1 ( echo FEL vid byggning. & pause & exit /b 1 )

echo.
echo [3/3] Klar!
echo.
echo  EXE-filen finns i: dist\Kalkylprogram.exe
echo  Kopiera den till valfri mapp och dubbelklicka for att starta.
echo.
pause
