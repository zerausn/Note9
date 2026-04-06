@echo off
setlocal enabledelayedexpansion

set "ROOT=%~dp0"
set "ADB=%ROOT%scrcpy\scrcpy-win64-v3.1\adb.exe"
if not exist "%ADB%" set "ADB=adb"

echo [DeX Bypass] Buscando Note 9...
set "PHONE="
for /f "skip=1 tokens=1,2,3,*" %%A in ('"%ADB%" devices -l') do (
  if /I "%%B"=="device" (
    echo %%C %%D | findstr /I /C:"model:SM_N9600" >nul
    if not errorlevel 1 set "PHONE=%%A"
  )
)

if not defined PHONE (
  echo [DeX Bypass] No se encontro el Note 9 por ADB.
  pause
  exit /b 1
)

"%ADB%" -s %PHONE% wait-for-device

echo [DeX Bypass] Intentando forzar el inicio de DeX...
"%ADB%" -s %PHONE% shell am start -n com.sec.android.app.desktoplauncher/com.sec.android.app.desktoplauncher.DesktopLauncher

echo [DeX Bypass] Esperando 3 segundos para que aparezca el dialogo...
timeout /t 3 /nobreak > nul

echo [DeX Bypass] Enviando clic de confirmacion en 1020, 2603...
"%ADB%" -s %PHONE% shell input tap 1020 2603

echo [DeX Bypass] Si DeX no inicio, prueba conectando el cable nuevamente.
pause
