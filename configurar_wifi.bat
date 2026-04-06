@echo off
setlocal enabledelayedexpansion

set "ROOT=%~dp0"
set "ADB=%ROOT%scrcpy\scrcpy-win64-v3.1\adb.exe"
if not exist "%ADB%" set "ADB=adb"

echo ======================================================
echo    Configurando ADB por Wi-Fi (Modo Inalambrico)
echo ======================================================
echo.
echo Requisitos:
echo 1. Conecta el Note 9 por USB ahora mismo.
echo 2. Asegura que la depuracion USB ya fue autorizada.
echo.
pause

set "PHONE="
for /f "skip=1 tokens=1,2,3,*" %%A in ('"%ADB%" devices -l') do (
  if /I "%%B"=="device" (
    echo %%C %%D | findstr /I /C:"model:SM_N9600" >nul
    if not errorlevel 1 set "PHONE=%%A"
  )
)

if not defined PHONE (
  echo No se encontro el Note 9 por ADB.
  echo Verifica el cable USB y vuelve a intentar.
  pause
  exit /b 1
)

echo.
echo [1/3] Usando dispositivo: %PHONE%
echo [2/3] Reiniciando ADB en modo TCP 5555...
"%ADB%" -s %PHONE% tcpip 5555

echo [3/3] Estado Wi-Fi actual del Note 9:
"%ADB%" -s %PHONE% shell dumpsys wifi | findstr /I "mWifiInfo SSID"
"%ADB%" -s %PHONE% shell ip -f inet addr show wlan0

echo.
echo Usa la IP actual de arriba con:
echo adb connect IP:5555
echo.
pause
