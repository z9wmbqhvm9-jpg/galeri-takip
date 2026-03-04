@echo off
echo ========================================
echo    GALERI TAKIP SISTEMI - WINDOWS
echo ========================================
echo.

REM Python kontrolü
python --version >nul 2>&1
if errorlevel 1 (
    echo [HATA] Python bulunamadi!
    echo Python yukleyin: https://www.python.org/downloads/
    pause
    exit
)

REM Gerekli paketleri yükle
echo [*] Gerekli paketler kontrol ediliyor...
pip install pychrome requests -q

REM Chrome'u kapat (varsa)
echo [*] Chrome kapatiliyor...
taskkill /F /IM chrome.exe >nul 2>&1

echo.
echo [!] ONEMLI: Cloudflare kontrolu gelirse ELLE gecin!
echo.
timeout /t 3

REM Scripti çalıştır
python chrome_scraper.py

pause
