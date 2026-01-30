import socket
import hl7
import datetime
import ssl  # <--- La librería mágica

# --- CONFIGURACIÓN SEGURA ---
HOST = '0.0.0.0'
PORT = 6662  # Nuevo puerto seguro
SB = b'\x0b'
EB = b'\x1c'
CR = b'\x0d'

# Rutas a las llaves que acabas de crear
CERT_FILE = 'hospital.crt'
KEY_FILE = 'hospital.key'

def iniciar_servidor_seguro():
    print("--- SERVIDOR HL7 SEGURO (TLS ENCRIPTADO) ---")
    
    # 1. CREAR CONTEXTO SSL
    # Le decimos: "Este contexto es para un SERVIDOR"
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    # Cargamos nuestra identidad
    context.load_cert_chain(certfile=CERT_FILE, keyfile=KEY_FILE)
    
    print("[.] Cargando certificados... OK")
    print(f"[.] Escuchando de forma segura en el puerto {PORT}...")
    
    # 2. CREAR SOCKET TCP NORMAL
    bindsocket = socket.socket()
    bindsocket.bind((HOST, PORT))
    bindsocket.listen(5)
    
    while True:
        try:
            newsocket, fromaddr = bindsocket.accept()
            
            # 3. EL "WRAP" (ENVOLTORIO) MÁGICO
            # Aquí ocurre el Handshake. Si el cliente no habla TLS, se corta.
            conn = context.wrap_socket(newsocket, server_side=True)
            
            print(f"\n[+] Conexión ENCRIPTADA establecida con: {fromaddr[0]}")
            # Imprimir info del cifrado (Para que veas que es real)
            print(f"    Cifrado: {conn.cipher()}")
            
            with conn:
                datos_crudos = conn.recv(4096)
                if not datos_crudos:
                    break
                
                # A partir de aquí, la lógica es IDÉNTICA al módulo anterior.
                # Python ya desencriptó los datos automáticamente en 'conn'.
                try:
                    mensaje_limpio = datos_crudos[1:-2]
                    mensaje_texto = mensaje_limpio.decode('utf-8')
                    
                    # Parsear
                    h = hl7.parse(mensaje_texto)
                    if len(h) > 1:
                        print("-" * 40)
                        print(" MENSAJE SEGURO RECIBIDO")
                        print(f" PACIENTE:    {h[1][5]}") # PID-5
                        print("-" * 40)
                        
                        # Responder ACK
                        id_control = h[0][10]
                        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                        ack_hl7 = f"MSH|^~\\&|PYTHON_TLS|LINUX|RECEPCION|HOSPITAL|{timestamp}||ACK|ACK{timestamp}|P|2.3\rMSA|AA|{id_control}"
                        ack_mllp = SB + ack_hl7.encode('utf-8') + EB + CR
                        conn.sendall(ack_mllp)
                        print("[Out] ACK Encriptado enviado.")
                        
                except (ValueError, UnicodeDecodeError, IndexError) as e:
                    print(f"❌ Error lógico: {e}")
                    
        except ssl.SSLError as e:
            print(f"⛔ Error de Seguridad (Handshake fallido): {e}")
        except OSError as e:
            print(f"Error general: {e}")

if __name__ == "__main__":
    try:
        iniciar_servidor_seguro()
    except KeyboardInterrupt:
        print("\nApagando servidor...")