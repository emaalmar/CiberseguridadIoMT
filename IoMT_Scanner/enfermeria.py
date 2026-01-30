import paho.mqtt.client as mqtt
import json

# CONFIGURACIÓN
BROKER = "localhost"
PUERTO = 1883
TEMA = "hospital/pacientes/+/vitales"

print("--- CENTRAL DE MONITOREO (SUSCRIPTOR - FIXED) ---")

def al_recibir_mensaje(client, userdata, msg):
    try:
        # 1. Decodificar el mensaje (Bytes -> Texto)
        contenido = msg.payload.decode()
        
        # 2. Parsear JSON (Texto -> Diccionario Python)
        datos = json.loads(contenido)
            
        bpm = datos.get("bpm", 0)
        paciente = datos.get("id_paciente", "?")
        
        # 3. Análisis de Riesgo
        if bpm > 120:
            print(f"🚨 ALERTA CRÍTICA: Paciente {paciente} con TAQUICARDIA ({bpm} BPM)")
        else:
            print(f"✅ Paciente {paciente}: Estable ({bpm} BPM)")
            
    except json.JSONDecodeError:
        print("⚠️ Error: El mensaje recibido no es un JSON válido.")
    except Exception as e:
        print(f"❌ Error procesando datos: {e}")

# Configuración del Cliente
cliente = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
cliente.on_message = al_recibir_mensaje

print(f"[.] Conectando a {BROKER} y suscribiendo a {TEMA}...")
cliente.connect(BROKER, PUERTO, 60)
cliente.subscribe(TEMA)

try:
    cliente.loop_forever()
except KeyboardInterrupt:
    print("\nDesconectando central...")