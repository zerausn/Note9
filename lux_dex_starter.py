import time
import os
import pygetwindow as gw
import pyautogui

def auto_confirm_dex():
    """
    Intenta automatizar el inicio de DeX detectando la ventana de confirmación 
    en Windows si DeX está configurado para pedir permiso desde el PC, 
    o simplemente asegura que la ventana de DeX esté maximizada.
    """
    print("Iniciando monitor de Samsung DeX...")
    while True:
        # 1. Buscar la ventana de Samsung DeX
        # A veces cuando se conecta, Windows muestra un diálogo de "Samsung DeX" 
        # para confirmar el inicio desde el PC.
        windows = gw.getWindowsWithTitle("Samsung DeX")
        if windows:
            dex_win = windows[0]
            if dex_win.isMinimized:
                dex_win.restore()
            dex_win.activate()
            
            # Si existiera un botón de "Iniciar ahora" en el PC (algunas versiones lo tienen)
            # aquí podríamos buscarlo. Pero generalmente la confirmación es en el CELULAR.
            
            print("Ventana de DeX detectada y activada.")
            break
        
        time.sleep(2)

if __name__ == "__main__":
    auto_confirm_dex()
