#!/bin/bash
# Lanzador de Falso DeX WiFi para Samsung Galaxy Note 9
# Replicando la lógica de éxito del S24 Ultra

IP_NOTE9="192.168.1.9"
PUERTO="5555"

echo "============================================="
echo "   NOTE 9: MODO FALSO DEX WIFI (PARROT OS)"
echo "============================================="

echo "[1/3] Conectando a $IP_NOTE9:$PUERTO..."
adb connect $IP_NOTE9:$PUERTO

# Asegurar modo escritorio
adb -s $IP_NOTE9:$PUERTO shell settings put global force_desktop_mode_on_external_displays 1

echo "[2/3] Limpiando sesiones previas..."
pkill -f "scrcpy -s $IP_NOTE9:$PUERTO" 2>/dev/null || true

echo "[3/3] Iniciando Espejo de Pantalla Secundaria (DeX)..."
# Usamos --new-display para disparar el modo escritorio en el Note 9
scrcpy -s $IP_NOTE9:$PUERTO --new-display=1920x1080 -b 8M --window-title "Galaxy Note 9 - Falso DeX WiFi" &

echo "---------------------------------------------"
echo "¡Listo! La ventana debería aparecer en breve."
echo "Si no ves el escritorio, toca el widget de Termux:X11 en el celular."
echo "---------------------------------------------"
