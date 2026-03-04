@echo off
REM Basit İlan Kontrol Botu - Otomatik Zamanlama için
REM Bu dosya Görev Zamanlayıcı ile çalıştırılır
cd /d "%~dp0"
call .venv\Scripts\activate.bat
python simple_ad_checker.py
