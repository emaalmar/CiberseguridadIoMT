import hl7
import datetime
import socket
import ssl

print("--- CLIENTE HL7 SEGURO (TLS) ---")

# 1. DATOS (Igual que siempre)
nombre = "EMANUEL"
apellido = "LEDESMA"
id_paciente = "999999" # Cambiamos el ID para notar la diferencia
timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

# Mensaje HL7
msh = f"MSH|^~\\&|SISTEMA_TLS|FEDORA|HOSPITAL_TLS|SERVER|{timestamp}||ADT^A01|MSG-{timestamp}|P|2.3"
pid = f"PID|||{id_paciente}||{apellido}^{nombre}||19991108|M"
mensaje_hl7 = f"{msh}\r{pid}"
# MLLP
SB = chr(11)
EB = chr(28) + chr(13)
mensaje_mllp = SB + mensaje_hl7 + EB

# 2. CONFIGURACIÓN DE RED SEGURA
IP_SERVIDOR = 'localhost'
PUERTO_SERVIDOR = 6662 # Puerto seguro
CERT_FILE = 'hospital.crt' # Necesitamos el certificado para verificar que el server es quien dice ser

try:
    print(f"[1] Preparando contexto de seguridad...")
    # Creamos un contexto para CLIENTE
    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    
    # IMPORTANTE: Como es un certificado "casero" (Self-signed), 
    # tenemos que decirle a Python que confíe explícitamente en este archivo.
    context.load_verify_locations(CERT_FILE)
    
    # Opcional: Desactivar chequeo de hostname si usaste algo distinto a 'localhost' en el certificado
    # context.check_hostname = False 

    print(f"[2] Conectando a {IP_SERVIDOR}:{PUERTO_SERVIDOR}...")
    
    # Conexión TCP pura
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # ¡EL ENVOLTORIO! Convertimos el socket normal en socket seguro
    conn_segura = context.wrap_socket(sock, server_hostname=IP_SERVIDOR)
    
    # Ahora nos conectamos usando el tubo seguro
    conn_segura.connect((IP_SERVIDOR, PUERTO_SERVIDOR))
    
    print(f"[+] ¡Túnel TLS establecido!")
    print(f"    Versión: {conn_segura.version()}")
    
    # Enviar datos
    conn_segura.send(mensaje_mllp.encode('utf-8'))
    print(" -> Datos encriptados enviados.")
    
    # Recibir ACK
    respuesta = conn_segura.recv(1024)
    print(f"[3] Respuesta del Servidor (Descifrada):\n {respuesta.decode('utf-8')}")
    
    conn_segura.close()

except ssl.SSLError as e:
    print(f"❌ Error de SSL (Certificado inválido o untrusted): {e}")
except ConnectionRefusedError:
    print("❌ No se puede conectar. ¿Está corriendo hospital_tls.py?")