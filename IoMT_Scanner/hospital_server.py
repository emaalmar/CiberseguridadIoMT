import socket
import hl7
import datetime

# --- CONFIGURACIÓN DEL SERVIDOR ---
HOST = '0.0.0.0'
PORT = 6661
SB = b'\x0b'
EB = b'\x1c'
CR = b'\x0d'

def iniciar_servidor():
    print(f"--- MOTOR DE INTEGRACIÓN PYTHON (HL7 LISTENER - V2 FINAL) ---")
    print(f"[.] Escuchando en el puerto {PORT}...")
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        
        while True:
            conn, addr = s.accept()
            with conn:
                print(f"\n[+] Conexión recibida desde: {addr[0]}")
                datos_crudos = conn.recv(4096)
                if not datos_crudos:
                    break
                
                # 1. DESEMPAQUETAR MLLP (CORREGIDO)
                # Usamos Slicing [1:-2] para quitar SB y EB+CR sin tocar el contenido interno.
                try:
                    mensaje_limpio = datos_crudos[1:-2]
                    mensaje_texto = mensaje_limpio.decode('utf-8')
                    
                    print(f"[Incoming] Mensaje recibido. Tamaño: {len(datos_crudos)} bytes")
                    
                    # 2. PARSEAR HL7
                    h = hl7.parse(mensaje_texto)
                    
                    # SAFETY CHECK: Verificamos que el mensaje tenga al menos 2 segmentos
                    if len(h) > 1:
                        tipo_mensaje = h[0][9]
                        id_control = h[0][10]
                        nombre_paciente = h[1][5] 
                        
                        print("-" * 40)
                        print(f" EVENTO:      {tipo_mensaje}")
                        print(f" PACIENTE:    {nombre_paciente}")
                        print(f" CONTROL ID:  {id_control}")
                        print("-" * 40)
                        
                        # 3. RESPONDER (ACK)
                        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                        ack_hl7 = f"MSH|^~\\&|PYTHON_SRV|LINUX|RECEPCION|HOSPITAL|{timestamp}||ACK|ACK{timestamp}|P|2.3\rMSA|AA|{id_control}"
                        ack_mllp = SB + ack_hl7.encode('utf-8') + EB + CR
                        conn.sendall(ack_mllp)
                        print("[Out] ACK enviado.")
                    else:
                        print("⚠️ ALERTA: El mensaje llegó, pero no se detectaron segmentos separados.")
                        print(f"Contenido crudo: {mensaje_texto}")

                except Exception as e:
                    print(f"❌ Error procesando mensaje: {e}")

if __name__ == "__main__":
    try:
        iniciar_servidor()
    except KeyboardInterrupt:
        print("\nApagando servidor...")