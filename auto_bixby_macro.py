import time
from dex_agent import DexAgent

def setup_macro():
    agent = DexAgent()
    print("Iniciando Macro de Configuración...")
    
    if not agent.focus():
        print("Error: No se encontró Samsung DeX abierto.")
        return

    # 1. Abrir Ajustes (Coordenadas aproximadas identificadas en logs previos)
    # En step_0.png Ajustes estaba cerca de (60, 320)
    print("Abriendo Ajustes...")
    agent.click(0.04, 0.35) 
    time.sleep(2)

    # 2. Click en la barra de búsqueda (Suele estar arriba a la derecha en Ajustes)
    print("Buscando 'Modos y Rutinas'...")
    agent.click(0.95, 0.25)
    time.sleep(1)
    
    # 3. Escribir el texto
    agent.type_text("Modos y Rutinas")
    print("Por favor, selecciona 'Modos y Rutinas' en los resultados y configura:")
    print("SI: Cargando -> Por cable")
    print("ENTONCES: Samsung DeX -> Iniciar DeX")

if __name__ == "__main__":
    setup_macro()
