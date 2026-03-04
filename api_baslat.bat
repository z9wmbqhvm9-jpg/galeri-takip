@echo off
echo ================================================
echo   API Server Baslatiliyor...
echo   Satildi/Aktif butonlari icin gerekli
echo ================================================
echo.

cd /d "%~dp0"
start /min cmd /c ".venv\Scripts\python.exe api_server.py"

timeout /t 2 /nobreak > nul
echo.
echo [OK] API Server basladi (Port 5000)
echo.
echo Dashboard'u kullanabilirsiniz!
echo.
pause
