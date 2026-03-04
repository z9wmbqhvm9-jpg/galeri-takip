@echo off
title Galeri Takip - Tam Sistem
echo ################################################
echo   GALERI TAKIP SISTEMI BASLATILIYOR
echo ################################################
echo.

cd /d "%~dp0"

REM API sunucusunu baslat (terminalden bagimsiz)
echo [1/2] API Server kontrol ediliyor (Port 5000)...
set "API_PID="
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5000" ^| findstr LISTENING') do set "API_PID=%%a"
if defined API_PID (
	echo       [OK] API zaten calisiyor (PID: %API_PID%)
) else (
	powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process -WindowStyle Hidden -FilePath '.\.venv\Scripts\python.exe' -ArgumentList 'api_server.py'"
	timeout /t 2 /nobreak > nul
	echo       [OK] API Server baslatildi
)

REM Dashboard sunucusunu baslat (terminalden bagimsiz)
echo [2/2] Dashboard sunucusu kontrol ediliyor (Port 8080)...
set "DASH_PID="
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8080" ^| findstr LISTENING') do set "DASH_PID=%%a"
if defined DASH_PID (
	echo       [OK] Dashboard zaten calisiyor (PID: %DASH_PID%)
) else (
	powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process -WindowStyle Hidden -FilePath '.\.venv\Scripts\python.exe' -ArgumentList '-m','http.server','8080'"
	timeout /t 2 /nobreak > nul
	echo       [OK] Dashboard baslatildi
)

echo.
echo ================================================
echo   SISTEM HAZIR!
echo ================================================
echo.
echo   Dashboard: http://localhost:8080/advanced_dashboard.html
echo   API:       http://localhost:5000
echo.
echo   Telefon:   http://192.168.1.103:8080/advanced_dashboard.html
echo.
echo ================================================

REM Tarayiciyi ac
start http://localhost:8080/advanced_dashboard.html

echo.
echo Sunucular arka planda calisiyor.
echo Kapatmak icin: dashboard_stop.bat calistir
echo.
exit /b 0
