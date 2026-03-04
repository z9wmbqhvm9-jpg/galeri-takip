@echo off
REM İlan Kontrol Botu - Günlük Çalıştırma
REM Bu dosyayı Windows Task Scheduler ile program zamanlayın

cd /d "%~dp0"

echo ===================================
echo İlan Kontrol Botu
echo Başlatılıyor: %date% %time%
echo ===================================

REM Python environment'ı aktive et
call .venv\Scripts\activate.bat

REM Botu çalıştır
python check_ads_daily.py

echo.
echo ===================================
echo Tamamlandı: %date% %time%
echo ===================================

REM Log dosyasını aç (opsiyonel)
REM notepad ad_check_log.txt

pause
