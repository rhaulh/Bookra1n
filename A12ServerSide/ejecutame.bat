@echo off
setlocal enabledelayedexpansion

set DEVICES=devices
set CACHES=%DEVICES%\Caches
set GESTALT=com.apple.MobileGestalt.plist
set OUTPUT=asset.epub

echo ==========================================
echo   COMPRESOR DE GESTALT (DEFLATE MAX)
echo ==========================================

if not exist "%DEVICES%" (
    echo ❌ No existe la carpeta "devices"
    pause
    exit /b
)

if not exist "%CACHES%" (
    echo ❌ No existe "devices\Caches"
    pause
    exit /b
)

rem Recorremos todas las carpetas dentro de devices
for /d %%f in ("%DEVICES%\*") do (

    if /i not "%%~nxf"=="Caches" (

        if exist "%%f\%GESTALT%" (

            echo.
            echo 📌 Procesando carpeta: %%~nxf

            rem Limpiar Caches
            del /q "%CACHES%\*" 2>nul

            rem 1) Copiar Gestalt dentro de Caches
            copy /y "%%f\%GESTALT%" "%CACHES%\%GESTALT%" >nul
            echo ✔️ Gestalt copiado a Caches

            rem 2) Comprimir usando powershell en deflate máximo
            echo 📦 Comprimiendo Caches → asset.epub...

            powershell -command ^
                "Add-Type -Assembly 'System.IO.Compression.FileSystem';" ^
                "[System.IO.Compression.ZipFile]::CreateFromDirectory('%CACHES%', '%DEVICES%\%OUTPUT%', [System.IO.Compression.CompressionLevel]::Optimal, $false)"

            echo ✔️ asset.epub generado

            rem 3) Copiar asset.epub a carpeta original
            copy /y "%DEVICES%\%OUTPUT%" "%%f\%OUTPUT%" >nul
            echo ✔️ Copiado a %%f

        )
    )
)

echo.
echo 🎉 FINALIZADO!
pause
exit /b
