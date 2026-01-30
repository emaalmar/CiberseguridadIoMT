import paho.mqtt.client as mqtt
import json
import ssl

# CONFIGURACIÓN SEGURA
BROKER = "localhost"
PUERTO = 8883
TEMA = "hospital/pacientes/+/vitales"
USUARIO = "enfermero"
CLAVE = "5678"
CA_CERT = "hospital.crt"

print("--- CENTRAL DE MONITOREO SEGURA (MQTTS) ---")

def al_recibir(client, userdata, msg):
    try:
        datos = json.loads(msg.payload.decode())
        bpm = datos.get("bpm", 0)
        protocolo = datos.get("seguridad", "INSEGURO")
        
        estado = "🚨 ALERTA" if bpm > 120 else "✅ Normal"
        print(f"[{protocolo}] Paciente: {bpm} BPM -> {estado}")
            
    except Exception as e:
        print(f"Error: {e}")

cliente = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
cliente.on_message = al_recibir

# SEGURIDAD
cliente.username_pw_set(USUARIO, CLAVE)
cliente.tls_set(ca_certs=CA_CERT, tls_version=ssl.PROTOCOL_TLSv1_2)
cliente.tls_insecure_set(True)

try:
    print(f"[.] Conectando al bunker seguro...")
    cliente.connect(BROKER, PUERTO, 60)
    cliente.subscribe(TEMA)
    cliente.loop_forever()
except KeyboardInterrupt:
    print("\nDesconectando...")
except Exception as e:
    print(f"❌ Acceso Denegado: {e}")