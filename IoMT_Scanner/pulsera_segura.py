import json
import random
import ssl
import time

import paho.mqtt.client as mqtt

# CONFIGURACIÓN SEGURA
BROKER = "localhost"
PUERTO = 8883 # Puerto TLS
TEMA = "hospital/pacientes/emanuel/vitales"
USUARIO = "paciente"
CLAVE = "1234"
CA_CERT = "hospital.crt" # Certificado para validar al servidor

print("--- PULSERA BLINDADA (MQTTS) ---")

cliente = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

# 1. AUTENTICACIÓN
cliente.username_pw_set(USUARIO, CLAVE)

# 2. ENCRIPTACIÓN (TLS)
cliente.tls_set(ca_certs=CA_CERT, tls_version=ssl.PROTOCOL_TLSv1_2)
# Desactivamos check de hostname porque es localhost y certificado self-signed
cliente.tls_insecure_set(True) 

try:
    print(f"[.] Conectando de forma segura a {BROKER}:{PUERTO}...")
    cliente.connect(BROKER, PUERTO, 60)
    print("[+] Conexión Cifrada y Autenticada EXITOSA.")
    
    while True:
        bpm = random.randint(60, 100)
        # Taquicardia aleatoria
        if random.random() < 0.1: bpm = 160  # explicar en .md que es este código y como funcina
        payload = {"id": "123456", "bpm": bpm, "seguridad": "TLS_1.2"}
        cliente.publish(TEMA, json.dumps(payload))
        
        print(f" -> Dato cifrado enviado: {bpm} BPM")
        time.sleep(1)

except Exception as e:
    print(f"❌ Error de conexión: {e}")