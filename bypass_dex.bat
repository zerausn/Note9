@echo off
:: Script para Bypass de Confirmacion Samsung DeX
:: Este script simula un clic en el boton "Iniciar ahora" de la pantalla del Note 9

echo [DeX Bypass] Buscando dispositivo...
adb wait-for-device

echo [DeX Bypass] Intentando forzar el inicio de DeX...
:: Intentamos lanzar la actividad de DeX directamente (a veces esto reduce los popups)
adb shell am start -n com.sec.android.app.desktoplauncher/com.sec.android.app.desktoplauncher.DesktopLauncher

echo [DeX Bypass] Esperando 3 segundos para que aparezca el dialogo...
timeout /t 3 /nobreak > nul

:: Simulamos el toque en la posicion real detectada por XML para Note 9
echo [DeX Bypass] Enviando clic de confirmacion en 1020, 2603...
adb shell input tap 1020 2603

echo [DeX Bypass] Si DeX no inicio, prueba conectando el cable nuevamente.
pause
