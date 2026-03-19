import pygetwindow as gw
import pyautogui
import time
import os
from PIL import Image

class DexAgent:
    def __init__(self, window_title="Samsung DeX"):
        self.window_title = window_title
        self.window = None
        self.update_window_info()

    def update_window_info(self):
        """Busca la ventana de Samsung DeX y actualiza sus coordenadas."""
        try:
            # Buscamos ventanas que contengan "Samsung DeX"
            windows = gw.getWindowsWithTitle(self.window_title)
            
            # Filtramos ventanas reales (con tamaño) y que coincidan con el título
            valid_windows = []
            for w in windows:
                if w.title == self.window_title and w.width > 100 and w.height > 100:
                    valid_windows.append(w)
            
            # Si hay varias, elegimos la más grande (la interfaz principal)
            if valid_windows:
                actual_app = max(valid_windows, key=lambda w: w.width * w.height)
                self.window = actual_app
                print(f"Ventana encontrada: {self.window.title} ({self.window.width}x{self.window.height})")
                return True
            
            # Fallback a coincidencia parcial si es necesario
            for w in windows:
                if "Edge" not in w.title and "Chrome" not in w.title and w.width > 100:
                    self.window = w
                    print(f"Ventana (coincidencia parcial) encontrada: {self.window.title}")
                    return True

            print(f"Error: No se encontró la ventana real de '{self.window_title}'")
            return False
        except Exception as e:
            print(f"Error buscando ventana: {e}")
            return False

    def focus(self):
        """Trae la ventana al frente."""
        if self.update_window_info():
            if self.window.isMinimized:
                self.window.restore()
            self.window.activate()
            time.sleep(0.5)
            return True
        return False

    def capture_screen(self, filename="dex_screen.png"):
        """Captura solo el contenido de la ventana de DeX."""
        if self.focus():
            # Aseguramos que la ventana esté dentro de la pantalla (1920x1080)
            if self.window.left < 0 or self.window.top < 0 or \
               (self.window.left + self.window.width) > 1920 or \
               (self.window.top + self.window.height) > 1080:
                print("Ventana fuera de límites, moviendo a (0,0)...")
                self.window.moveTo(0, 0)
                time.sleep(0.5)

            left, top, width, height = self.window.left, self.window.top, self.window.width, self.window.height
            # Clip coordinates to screen bounds for pyautogui
            left = max(0, left)
            top = max(0, top)
            width = min(width, 1920 - left)
            height = min(height, 1080 - top)
            
            screenshot = pyautogui.screenshot(region=(left, top, width, height))
            screenshot.save(filename)
            print(f"Captura guardada en {filename} ({width}x{height})")
            return filename
        return None

    def click(self, rel_x, rel_y):
        """Hace clic en coordenadas relativas (0.0 a 1.0) dentro de la ventana."""
        if self.focus():
            abs_x = self.window.left + int(rel_x * self.window.width)
            abs_y = self.window.top + int(rel_y * self.window.height)
            pyautogui.click(abs_x, abs_y)
            print(f"Clic en ({abs_x}, {abs_y})")
            return True
        return False

    def type_text(self, text):
        """Escribe texto en la ventana enfocada."""
        if self.focus():
            pyautogui.write(text, interval=0.05)
            print(f"Texto escrito: {text}")
            return True
        return False

if __name__ == "__main__":
    agent = DexAgent()
    if agent.focus():
        print("Agente conectado a Samsung DeX.")
        # Ejemplo: Capturar pantalla para análisis
        agent.capture_screen()
    else:
        print("Asegúrate de que Samsung DeX esté abierto.")
