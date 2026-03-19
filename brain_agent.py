import os
import time
from PIL import Image
from dex_agent import DexAgent

# Nota: Para usar el cerebro, necesitaremos una API Key de Google Gemini (Gratuita)
# o configurar un modelo local como Ollama con soporte de Vision (Llava/Moondream).
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

class BrainAgent:
    def __init__(self, api_key=None):
        self.hand = DexAgent()
        self.api_key = api_key or os.environ.get("GOOGLE_API_KEY")
        if GEMINI_AVAILABLE and self.api_key:
            safe_key = str(self.api_key)
            print(f"Configurando Gemini con API Key: {safe_key[:5]}...{safe_key[-4:]}")
            self.model = genai.GenerativeModel('models/gemini-2.0-flash-lite-001')
            print("Cerebro (Gemini 2.0 Flash Lite) listo.")
        else:
            self.model = None
            key_status = "OK" if self.api_key else "Missing"
            lib_status = "OK" if GEMINI_AVAILABLE else "Missing"
            print(f"Aviso: Gemini no está configurado (API Key: {key_status}, Library: {lib_status}). El agente funcionará en modo manual/debug.")

    def analyze_and_act(self, goal):
        """El bucle principal: Observar -> Pensar -> Actuar."""
        print(f"\n--- Nueva Meta: {goal} ---")
        
        for step in range(15): # Aumentado a 15 pasos para flujos largos
            # 1. Observar
            screenshot_path = self.hand.capture_screen(f"step_{step}.png")
            if not screenshot_path:
                print("No se pudo capturar la pantalla.")
                break
            
            if not self.model:
                print(f"Modo Debug: Captura {screenshot_path} creada. (Sin IA para analizar)")
                break

            # 2. Pensar (Enviamos imagen + meta a Gemini)
            prompt = f"""
            Eres un agente que controla un Samsung Galaxy Note 9 a través de Samsung DeX.
            Tu meta actual es: {goal}
            
            Analiza la imagen adjunta. 
            Responde ÚNICAMENTE en formato JSON con la siguiente estructura:
            {{
                "pensamiento": "explicación de lo que ves y lo que vas a hacer",
                "accion": "click" | "type" | "wait" | "done",
                "rel_x": 0.5, (coordenadas relativas 0.0 a 1.0, solo si es click)
                "rel_y": 0.5, (solo si es click)
                "texto": "texto a escribir", (solo si es type)
                "finalizado": true/false (pon true SOLO cuando la meta se haya cumplido totalmente)
            }}
            
            IMPORTANTE:
            - Si necesitas buscar algo, usa el icono de lupa.
            - Si terminaste la meta, usa la acción "done" y finalizado: true.
            - Si la pantalla está cargando, usa "wait".
            """
            
            try:
                img = Image.open(screenshot_path)
                
                # Manejo de cuota con reintentos
                retry_wait = 15
                for attempt in range(3):
                    try:
                        print(f"Consultando al cerebro (IA) - Paso {step}... (Intento {attempt+1})", flush=True)
                        response = self.model.generate_content([prompt, img])
                        text_response = response.text
                        break
                    except Exception as e:
                        if "429" in str(e) or "quota" in str(e).lower():
                            print(f"Límite de cuota alcanzado. Esperando {retry_wait}s...", flush=True)
                            time.sleep(retry_wait)
                            retry_wait *= 2
                        else:
                            raise e
                else:
                    print("No se pudo obtener respuesta de la IA por falta de cuota.", flush=True)
                    break
                if "```json" in text_response:
                    text_response = text_response.split("```json")[1].split("```")[0].strip()
                elif "{" in text_response:
                    text_response = text_response[text_response.find("{"):text_response.rfind("}")+1]
                
                import json
                try:
                    res = json.loads(text_response)
                except Exception:
                    print(f"Error parseando JSON. Respuesta cruda: {text_response}")
                    raise

                print(f"IA Pensamiento: {res.get('pensamiento')}", flush=True)
                print(f"IA Acción: {res.get('accion')} {res.get('texto', '')}", flush=True)
                
                accion = res.get("accion")
                if accion == "click":
                    self.hand.click(res.get("rel_x"), res.get("rel_y"))
                elif accion == "type":
                    self.hand.type_text(res.get("texto"))
                elif accion == "wait":
                    print("Esperando 2 segundos...", flush=True)
                    time.sleep(2)
                elif accion == "done":
                    print("Tarea completada según la IA.", flush=True)
                    break
                
                if res.get("finalizado"):
                    break
                    
                time.sleep(2) # Pausa entre acciones
                
            except Exception as e:
                import traceback
                print(f"Error en el razonamiento (Paso {step}):", flush=True)
                traceback.print_exc()
                break

if __name__ == "__main__":
    # Para probar la estructura
    brain = BrainAgent()
    brain.analyze_and_act("Abrir la aplicación de Mensajes")
