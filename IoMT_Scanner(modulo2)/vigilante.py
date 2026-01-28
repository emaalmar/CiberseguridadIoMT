import nmap
import json
import os
import datetime

# --- CONFIGURACIÓN ---
RED_OBJETIVO = "192.168.1.0/24"
ARCHIVO_WHITELIST = "whitelist.json"
# ---------------------

def cargar_whitelist():
    if not os.path.exists(ARCHIVO_WHITELIST):
        return None # No existe, es la primera vez
    with open(ARCHIVO_WHITELIST, 'r') as f:
        return json.load(f)

def guardar_whitelist(dispositivos):
    with open(ARCHIVO_WHITELIST, 'w') as f:
        json.dump(dispositivos, f, indent=4)
    print(f"\n[INFO] Lista blanca guardada con {len(dispositivos)} dispositivos.")

def escanear_red():
    nm = nmap.PortScanner()
    print(f"--- Escaneando {RED_OBJETIVO} ... ---")
    nm.scan(hosts=RED_OBJETIVO, arguments='-sn')
    
    # Convertimos el resultado complejo de nmap a un diccionario simple:
    # { 'MAC_ADDRESS': 'IP_ADDRESS' }
    resultado = {}
    for host in nm.all_hosts():
        if 'mac' in nm[host]['addresses']:
            mac = nm[host]['addresses']['mac']
            resultado[mac] = host
        else:
            # Si es la propia máquina (localhost), a veces no da MAC. Usamos una fake.
            if host == "192.168.1.75": # Tu IP local
                 resultado["00:00:00:00:00:00"] = host
            
    return resultado

# --- LÓGICA PRINCIPAL ---
def main():
    # 1. Escanear la red actual
    dispositivos_actuales = escanear_red()
    
    # 2. Cargar la memoria (Whitelist)
    whitelist = cargar_whitelist()

    # CASO A: Primera ejecución (Entrenamiento)
    if whitelist is None:
        print("\n[MODO ENTRENAMIENTO]")
        print("No se encontró base de datos. Asumiendo que la red actual es segura.")
        guardar_whitelist(dispositivos_actuales)
    
    # CASO B: Ejecución normal (Patrulla)
    else:
        print("\n[MODO PATRULLA]")
        intrusos = []
        
        for mac, ip in dispositivos_actuales.items():
            if mac not in whitelist:
                # ¡AJÁ! Esta MAC no estaba en el archivo
                intrusos.append((ip, mac))
        
        if len(intrusos) > 0:
            print("\n" + "!"*40)
            print(f" ALERTA DE SEGURIDAD: {len(intrusos)} INTRUSO(S) DETECTADO(S)")
            print("!"*40)
            for ip, mac in intrusos:
                print(f" -> IP: {ip} | MAC: {mac}")
                # Aquí podrías agregar código para enviar un email o bloquear el puerto
        else:
            print("\n[OK] Red segura. No hay dispositivos nuevos.")

if __name__ == "__main__":
    main()