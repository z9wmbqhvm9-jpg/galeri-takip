@echo off
chcp 65001 >nul
echo ================================================================
echo 🗃️  VERİTABANI BAŞLATMA VE İLK KURULUM
echo ================================================================
echo.

REM Virtual environment'i aktive et
call .venv\Scripts\activate.bat

echo 📦 Veritabanı başlatılıyor...
echo.

REM Veritabanını başlat ve JSON verisini import et
python database.py

echo.
echo ================================================================
echo ✅ KURULUM TAMAMLANDI!
echo ================================================================
echo.
echo 📁 Oluşturulan dosyalar:
echo    - galeri_takip.db (SQLite veritabanı)
echo.
echo 🚀 Artık şunları yapabilirsin:
echo    1. Bot çalıştır: run_selenium_bot.bat
echo    2. Dashboard aç: advanced_dashboard.html
echo    3. CSV export et: python database.py
echo.
echo ================================================================
pause
