@echo off
chcp 65001 >nul
echo ================================================================
echo 📊 GELİŞMİŞ DASHBOARD BAŞLATILIYOR
echo ================================================================
echo.
echo 🚀 Arka plan sunucu aciliyor...
echo 🌐 Dashboard aciliyor: http://localhost:8080/advanced_dashboard.html
echo.
echo ✅ Bu pencereyi kapatabilirsin.
echo ================================================================
echo.

REM Arka plan sunucuyu baslat ve dashboard'u ac
call dashboard_background.bat
