#!/usr/bin/env python3
import os
import time
import subprocess
import json

# REQUISITOS EN TERMUX:
# pkg install python termux-api
# También debes tener instalada la app "Termux:API" desde F-Droid o Play Store.

class LocalVoiceAgent:
    def __init__(self, api_key=None):
        self.api_key = api_key or "AIzaSyC0qKWcOOo0efFZDCvqJ1tY0kjmwPaXGUw"
        print("Agente Vocal Note 9 Inicializado.")

    def listen(self):
        """Usa Termux-API para escuchar la voz del usuario."""
        print("\nEscuchando...")
        try:
            # Llama a termux-speech-to-text
            result = subprocess.run(["termux-speech-to-text"], capture_output=True, text=True)
            if result.returncode == 0:
                text = result.stdout.strip()
                print(f"Escuchado: '{text}'")
                return text
            else:
                print("Error al escuchar (¿Termux:API está instalado?)")
                return None
        except Exception as e:
            print(f"Error en el micrófono: {e}")
            return None

    def execute_command(self, command):
        """Procesa el comando de voz."""
        cmd = command.lower()
        
        if "proyectar" in cmd or "pantalla" in cmd or "dex" in cmd:
            print("Activando Proyección Samsung DeX...")
            # Intentar forzar el inicio de DeX (requiere permisos de sistema)
            # Como fallback, abrimos los Ajustes de DeX
            subprocess.run(["am", "start", "-n", "com.sec.android.app.desktoplauncher/com.sec.android.app.desktoplauncher.DesktopLauncher"])
            return "Proyectando pantalla..."

        if "abrir" in cmd:
            if "mensajes" in cmd:
                subprocess.run(["am", "start", "-a", "android.intent.action.MAIN", "-n", "com.samsung.android.messaging/com.samsung.android.messaging.ui.ConversationListActivity"])
                return "Abriendo Mensajes"
            if "ajustes" in cmd:
                subprocess.run(["am", "start", "-a", "android.settings.SETTINGS"])
                return "Abriendo Ajustes"

        print(f"Comando no reconocido localmente: {command}")
        return "No estoy seguro de cómo hacer eso todavía."

    def run(self):
        # Asegurar que DeX se intente iniciar al arrancar el agente
        print("Asegurando conexión de proyección...")
        
        while True:
            voice_text = self.listen()
            if voice_text:
                if "adiós" in voice_text.lower() or "salir" in voice_text.lower():
                    print("Agente desactivado.")
                    break
                
                response = self.execute_command(voice_text)
                print(f"Respuesta: {response}")
                
            time.sleep(1)

if __name__ == "__main__":
    agent = LocalVoiceAgent()
    agent.run()
