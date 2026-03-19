@echo off
cd scrcpy\scrcpy-win64-v3.1
echo Iniciando Scrcpy en Modo Bajo Consumo...
echo.
echo Parametros: 30 FPS, Max Size 1024, Bitrate 4M
echo Conecta el Note 9 por USB si es la primera vez.
echo.
scrcpy.exe --max-fps 30 --max-size 1024 --video-bit-rate 4M --window-title "Note 9 - Modo Frio"
pause
