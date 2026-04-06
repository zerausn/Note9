@echo off
setlocal

set "ROOT=%~dp0"
set "ADB=%ROOT%scrcpy\scrcpy-win64-v3.1\adb.exe"
set "SCRCPY=%ROOT%scrcpy\scrcpy-win64-v3.1\scrcpy.exe"
set "NOTE9_SERIAL=29396e8c1e3f7ece"

if not exist "%ADB%" (
  echo [scrcpy] No se encontro adb en:
  echo %ADB%
  pause
  exit /b 1
)

if not exist "%SCRCPY%" (
  echo [scrcpy] No se encontro scrcpy en:
  echo %SCRCPY%
  pause
  exit /b 1
)

echo ======================================================
echo   Abrir Note9 por scrcpy
echo ======================================================
echo.
echo Serial objetivo: %NOTE9_SERIAL%
echo Titulo de ventana: Note9 via scrcpy
echo.

"%ADB%" start-server >nul 2>nul
"%ADB%" -s %NOTE9_SERIAL% wait-for-device

for /f "delims=" %%A in ('"%ADB%" -s %NOTE9_SERIAL% get-state 2^>nul') do set "STATE=%%A"
if /I not "%STATE%"=="device" (
  echo [scrcpy] El Note9 no esta listo por ADB.
  echo Conectalo por USB y autoriza la depuracion si hace falta.
  pause
  exit /b 1
)

start "" "%SCRCPY%" ^
  -s %NOTE9_SERIAL% ^
  --window-title "Note9 via scrcpy" ^
  --stay-awake ^
  --always-on-top ^
  --window-x 40 ^
  --window-y 40 ^
  --window-width 500 ^
  --window-height 980 ^
  --max-fps 30 ^
  --video-bit-rate 6M

exit /b 0
