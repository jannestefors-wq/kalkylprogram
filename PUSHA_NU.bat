@echo off
title Pushar Kalkylprogram till GitHub...
cd /d "%~dp0"

git config user.email "jannestefors@gmail.com"
git config user.name "Jan Stefors"

git init
git add .
git commit -m "Uppdatering kalkylprogram"
git remote remove origin 2>nul
git remote add origin https://github.com/jannestefors-wq/kalkylprogram.git
git branch -M main
git push -u origin main

echo.
echo ============================================
echo  Klart! Koden finns nu pa GitHub:
echo  https://github.com/jannestefors-wq/kalkylprogram
echo ============================================
pause
