import os
import sys
from brain_agent import BrainAgent

print("Python version:", sys.version)
print("GOOGLE_API_KEY present:", "Yes" if os.environ.get("GOOGLE_API_KEY") else "No")

try:
    agent = BrainAgent()
    print("Agent initialized.")
    agent.analyze_and_act("Prueba de conexión: ¿Qué ves en la pantalla?")
except Exception as e:
    import traceback
    traceback.print_exc()
