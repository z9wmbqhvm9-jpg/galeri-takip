@echo off
chcp 65001 >nul
setlocal

echo ================================================================
echo 🛑 TÜM SUNUCULARI DURDURMA
echo ================================================================

REM 8080 portunu kapat (Dashboard)
echo [1/2] Dashboard sunucusu kapatiliyor (Port 8080)...
set PID=
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8080" ^| findstr LISTENING') do set PID=%%a

if defined PID (
    taskkill /PID %PID% /F >nul 2>&1
    echo       [OK] Dashboard durduruldu
) else (
    echo       [--] Zaten kapali
)

REM 5000 portunu kapat (API)
echo [2/2] API sunucusu kapatiliyor (Port 5000)...
set PID2=
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5000" ^| findstr LISTENING') do set PID2=%%a

if defined PID2 (
    taskkill /PID %PID2% /F >nul 2>&1
    echo       [OK] API durduruldu
) else (
    echo       [--] Zaten kapali
)

echo.
echo ================================================
echo   SISTEM KAPATILDI
echo ================================================
echo.
endlocal
