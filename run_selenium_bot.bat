@echo off
REM Gelişmiş İlan Kontrol Botu - Selenium
REM İlk kullanımda gerekli paketleri yükler ve botu başlatır

cd /d "%~dp0"

echo ========================================
echo Gelismis Ilan Kontrol Botu (SELENIUM)
echo ========================================
echo.

REM Python environment kontrolü
if not exist ".venv\Scripts\activate.bat" (
    echo HATA: Virtual environment bulunamadi!
    echo Lutfen once "python -m venv .venv" komutunu calistirin.
    pause
    exit /b 1
)

REM Environment'i aktive et
call .venv\Scripts\activate.bat

echo [1/3] Gerekli paketler kontrol ediliyor...
echo.

REM Selenium ve undetected-chromedriver kurulumu
pip show selenium >nul 2>&1
if errorlevel 1 (
    echo Selenium yukleniyor...
    pip install selenium
)

pip show undetected-chromedriver >nul 2>&1
if errorlevel 1 (
    echo undetected-chromedriver yukleniyor...
    pip install undetected-chromedriver
)

echo.
echo [2/3] Paketler hazir!
echo.
echo [3/3] Bot baslatiyor...
echo.
echo ========================================
echo Baslatma: %date% %time%
echo ========================================
echo.

REM Botu çalıştır
python check_ads_selenium.py

echo.
echo ========================================
echo Tamamlandi: %date% %time%
echo ========================================
echo.
echo Log dosyasini acmak icin ENTER'a basin...
pause > nul

REM Log dosyasını aç
if exist "ad_check_log.txt" (
    notepad ad_check_log.txt
)
