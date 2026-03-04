@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"

echo ================================================================
echo 📊 DASHBOARD ARKA PLAN SUNUCU

echo ================================================================

REM Port 8080 zaten dinleniyor mu kontrol et
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8080" ^| findstr LISTENING') do set PID=%%a

if defined PID (
    echo ✅ Sunucu zaten calisiyor (PID: %PID%)
) else (
    echo 🚀 Sunucu baslatiliyor (arka planda)...
    set "PYTHON_EXE="
    if exist ".\.venv\Scripts\python.exe" (
        set "PYTHON_EXE=.\.venv\Scripts\python.exe"
    ) else (
        where python >nul 2>&1
        if not errorlevel 1 (
            set "PYTHON_EXE=python"
        ) else (
            where py >nul 2>&1
            if not errorlevel 1 (
                set "PYTHON_EXE=py"
            )
        )
    )

    if not defined PYTHON_EXE (
        echo ❌ Python bulunamadi. Lutfen Python kurun veya .venv olusturun.
        echo.
        pause
        endlocal
        exit /b 1
    )

    if /I "%PYTHON_EXE%"=="py" (
        powershell -NoProfile -Command "Start-Process -WindowStyle Hidden -WorkingDirectory '%cd%' -FilePath 'py' -ArgumentList '-3','-m','http.server','8080'"
    ) else (
        powershell -NoProfile -Command "Start-Process -WindowStyle Hidden -WorkingDirectory '%cd%' -FilePath '%PYTHON_EXE%' -ArgumentList '-m','http.server','8080'"
    )
    timeout /t 2 /nobreak >nul

    set PID=
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8080" ^| findstr LISTENING') do set PID=%%a
    if not defined PID (
        echo ❌ Sunucu baslatilamadi. Lutfen terminalden manuel deneyin:
        if /I "%PYTHON_EXE%"=="py" (
            echo    py -3 -m http.server 8080
        ) else (
            echo    %PYTHON_EXE% -m http.server 8080
        )
        echo.
        pause
        endlocal
        exit /b 1
    )
)

echo 🌐 Dashboard aciliyor...
start "" http://localhost:8080/advanced_dashboard.html

echo.
echo ✅ Bu pencereyi kapatabilirsin.
echo ℹ️  Sunucu arka planda calismaya devam eder.

echo.
endlocal
