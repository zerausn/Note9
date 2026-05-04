@echo off
setlocal enabledelayedexpansion

set "ROOT=%~dp0"
set "ADB=%ROOT%scrcpy\scrcpy-win64-v3.1\adb.exe"
if not exist "%ADB%" set "ADB=adb"

echo [DeX Fix] Buscando Note 9...
set "PHONE="
for /f "skip=1 tokens=1,2,3,*" %%A in ('"%ADB%" devices -l') do (
  if /I "%%B"=="device" (
    echo %%C %%D | findstr /I /C:"model:SM_N9600" >nul
    if not errorlevel 1 set "PHONE=%%A"
  )
)

if not defined PHONE (
  echo [DeX Fix] No se encontro el Note 9 por ADB.
  pause
  exit /b 1
)

"%ADB%" -s %PHONE% wait-for-device

echo [DeX Fix] Estado USB y DeX actual:
"%ADB%" -s %PHONE% shell getprop | findstr /I "service.dexonpc.running sys.dockstate sys.usb.state"
"%ADB%" -s %PHONE% shell dumpsys usb | findstr /I "connected=true configured=true host_connected current_mode data_role"

echo [DeX Fix] Enviando tap a 'Iniciar ahora' (1020, 2603)...
"%ADB%" -s %PHONE% shell input tap 1020 2603

echo [DeX Fix] Nota: las actividades DeX viejas del script original ya no son validas.
echo [DeX Fix] Si DeX no entra, el problema no es el driver USB sino la negociacion DeX/Flow.
pause
