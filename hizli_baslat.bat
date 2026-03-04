@echo off
echo ========================================
echo   SUNUCULARI BASLATILIYOR...
echo ========================================
echo.

cd /d "%~dp0"

echo [1/2] API Sunucusu baslatiliyor...
start /min "API Server" cmd /c ".venv\Scripts\python.exe api_server.py"
timeout /t 2 /nobreak > nul

echo [2/2] Dashboard baslatiliyor...
start /min "Dashboard" cmd /c ".venv\Scripts\python.exe -m http.server 8080"
timeout /t 2 /nobreak > nul

echo.
echo ========================================
echo   TAMAMLANDI!
echo ========================================
echo.
echo Dashboard: http://localhost:8080/advanced_dashboard.html
echo.
start http://localhost:8080/advanced_dashboard.html
