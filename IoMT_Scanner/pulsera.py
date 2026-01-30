import paho.mqtt.client as mqtt
import time
import random
import json

# CONFIGURACIÓN
BROKER = "localhost"
PUERTO = 1883 # Puerto estándar MQTT (Inseguro por defecto)
TEMA = "hospital/pacientes/emanuel/vitales"

print("--- PULSERA INTELIGENTE v1.0 (IoMT) ---")
print(f"[.] Conectando al broker en {BROKER}...")

cliente = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2) #explicar en .md
cliente.connect(BROKER, PUERTO, 60)

print("[+] Conectado. Iniciando monitoreo...")

try:
    while True:
        # 1. Simular Signos Vitales
        # Ritmo normal entre 60 y 100. A veces sube (arritmia).
        bpm = random.randint(55, 110)
        oxigeno = random.randint(90, 100)
        
        # Simulamos un evento crítico aleatorio (10% de probabilidad)
        if random.random() < 0.1:
            bpm = random.randint(150, 190) # Taquicardia
        
        # 2. Empaquetar en JSON (Estándar moderno)
        payload = {
            "id_paciente": "123456",
            "timestamp": time.time(),
            "bpm": bpm,
            "spo2": oxigeno,
            "bateria": 85
        }
        mensaje_json = json.dumps(payload) # Convertir a cadena JSON
        
        # 3. PUBLICAR (Gritar al aire)
        cliente.publish(TEMA, mensaje_json)
        
        # Feedback visual para ti
        estado = "❤️ NORMAL" if bpm < 120 else "⚠️ PELIGRO"
        print(f" -> Enviado: {bpm} BPM | {oxigeno}% SpO2 [{estado}]")
        
        time.sleep(1) # Esperar 1 segundo

except KeyboardInterrupt:
    print("\nApagando dispositivo...")
    cliente.disconnect()