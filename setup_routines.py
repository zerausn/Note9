import time
from brain_agent import BrainAgent

def setup_bixby_routine():
    """
    Usa el BrainAgent para navegar y configurar la Bixby Routine.
    """
    # Usamos la API Key proporcionada por el usuario
    api_key = "AIzaSyC0qKWcOOo0efFZDCvqJ1tY0kjmwPaXGUw"
    brain = BrainAgent(api_key=api_key)
    
    print("Iniciando configuración automática de Bixby Routine...")
    
    # Meta 1: Ir a Ajustes y buscar Modos y Rutinas
    brain.analyze_and_act("Abrir Ajustes de Android, buscar 'Modos y Rutinas' y entrar en esa sección.")
    
    time.sleep(2)
    
    # Meta 2: Crear la rutina de Bypass
    brain.analyze_and_act("Crear una nueva rutina: SI 'Cargando por cable' ENTONCES 'Iniciar Samsung DeX'.")
    
    print("Proceso de configuración finalizado.")

if __name__ == "__main__":
    setup_bixby_routine()
