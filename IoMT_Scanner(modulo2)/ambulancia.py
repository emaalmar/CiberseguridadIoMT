"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  SCRIPT: La Ambulancia (ambulancia.py)                                      ║
║  PROPÓSITO: Enviar una imagen DICOM desde una "máquina médica" al PACS     ║
║  PROTOCOLO: DICOM C-STORE (Almacenamiento remoto de imágenes)              ║
╚══════════════════════════════════════════════════════════════════════════════╝

¿QUÉ SUCEDE AQUÍ?
─────────────────
Este script simula una máquina médica (como una tomografía o resonancia) que:
1. Prepara un estudio (imagen DICOM)
2. Se conecta a un servidor PACS remoto
3. Negocia el protocolo DICOM (Association)
4. Envía la imagen usando el comando C-STORE
5. Verifica que fue recibida correctamente

¿POR QUÉ ES IMPORTANTE?
───────────────────────
- En un hospital real, hay docenas de máquinas generando imágenes constantemente
- Todas deben coordinar su comunicación (por eso existe DICOM)
- Un error en la transmisión puede significar perder un diagnóstico
- Este script automatiza todo ese proceso

FLUJO DE EJECUCIÓN:
──────────────────
[1] Cargar imagen DICOM        → Lee el archivo .dcm anonimizado
[2] Crear Aplicación DICOM     → Define que somos una "máquina médica"
[3] Establecer Asociación      → Handshake con el servidor PACS
[4] Enviar imagen (C-STORE)    → Transmisión de la imagen
[5] Verificar respuesta        → Confirmar que el PACS la aceptó
[6] Cerrar Conexión            → Liberar recursos
"""

import pydicom
from pynetdicom import AE, debug_logger
from pynetdicom.sop_class import CTImageStorage

# ═══════════════════════════════════════════════════════════════════════════
# OPCIONAL: Descomenta para ver TODOS los detalles técnicos del envío
# (Útil para troubleshooting)
# ═══════════════════════════════════════════════════════════════════════════
# debug_logger()

print("=" * 80)
print("--- INICIANDO PROTOCOLO DE TRANSMISIÓN DICOM (C-STORE) ---")
print("=" * 80)

# ═══════════════════════════════════════════════════════════════════════════
# SECCIÓN 1: CONFIGURACIÓN
# ═══════════════════════════════════════════════════════════════════════════
"""
CONFIGURACIÓN CRÍTICA
─────────────────────
Estos parámetros definen DÓNDE está el servidor PACS y CÓMO conectarse.

IP_SERVIDOR = '127.0.0.1'
    └─ Localhost (tu propia máquina). En un hospital real sería algo como:
       '192.168.1.100' (IP del servidor PACS dentro de la red)

PUERTO_SERVIDOR = 4242
    └─ Puerto DICOM (estándar de la industria). El PACS "escucha" aquí.

AET_SERVIDOR = 'ORTHANC'
    └─ Application Entity Title del servidor (su "nombre" en la red DICOM)
       Orthanc viene con este nombre por defecto.
       En un hospital real podría ser: 'SERVIDOR_PACS_CENTRAL'

ARCHIVO_A_ENVIAR = 'paciente_anonimo.dcm'
    └─ El archivo que creaste en el Módulo 3 (medico.py)
       Debe estar en la misma carpeta que este script.
"""

# Dirección del Servidor PACS (Orthanc en Docker)
IP_SERVIDOR = '127.0.0.1'          # Localhost (tu propia máquina)
PUERTO_SERVIDOR = 4242              # Puerto estándar DICOM
AET_SERVIDOR = 'ORTHANC'            # Application Entity Title del servidor

# El archivo anonimizado que creaste en el módulo anterior
ARCHIVO_A_ENVIAR = 'paciente_anonimo.dcm'

# ═══════════════════════════════════════════════════════════════════════════
# SECCIÓN 2: CARGAR LA IMAGEN DICOM
# ═══════════════════════════════════════════════════════════════════════════
"""
PASO 1: PREPARAR EL PAQUETE
──────────────────────────
Leemos el archivo .dcm que contiene:
  - Metadatos del paciente (ya anonimizados)
  - La imagen médica en sí (datos de píxeles)

Si el archivo no existe, significa que no ejecutaste medico.py primero.
"""

try:
    # pydicom.dcmread() carga la imagen completa en memoria como un objeto Dataset
    ds = pydicom.dcmread(ARCHIVO_A_ENVIAR)
    print(f"[✓] Archivo cargado: {ARCHIVO_A_ENVIAR}")
    print(f"    Información de la imagen:")
    print(f"    - ID Paciente: {ds.PatientID}")
    print(f"    - Tipo de estudio: {ds.Modality if hasattr(ds, 'Modality') else 'Desconocido'}")
except FileNotFoundError:
    print(f"[✗] Error: No encuentro '{ARCHIVO_A_ENVIAR}'")
    print(f"    → Ejecuta primero: python medico.py")
    print(f"    → Esto generará el archivo anonimizado necesario.")
    exit(1)  # Salir con código de error

# ═══════════════════════════════════════════════════════════════════════════
# SECCIÓN 3: CREAR LA "APLICACIÓN DICOM" (AE = Application Entity)
# ═══════════════════════════════════════════════════════════════════════════
"""
PASO 2: DEFINIR QUIÉN ERES TÚ EN LA RED DICOM
──────────────────────────────────────────────
Una "Aplicación DICOM" es cualquier software/máquina que habla DICOM:
  - Una tomografía
  - Una resonancia
  - Un servidor PACS
  - Un script Python (como este)

El AE (Application Entity) de tu script puede tener cualquier nombre.
En pynetdicom, por defecto es 'PYNETDICOM' pero podría ser 'MI_SCRIPT', etc.

¿QUÉ SIGNIFICA add_requested_context?
→ Le dices al servidor: "Yo puedo enviar imágenes CTImageStorage"
→ Es como decir: "Tengo una tomografía para guardar"

CTImageStorage = Imágenes de TAC/Tomografía
Otros ejemplos:
  - RTImageStorage = Imágenes de Radioterapia
  - MRImageStorage = Imágenes de Resonancia Magnética
  - XCImageStorage = Radiografías
"""

print("\n[.] Preparando comunicación DICOM...")

# Crear una aplicación DICOM (nosotros somos una "máquina médica" simulada)
ae = AE()

# Declarar: "Soy capaz de ENVIAR imágenes de Tomografía"
ae.add_requested_context(CTImageStorage)

print(f"[✓] Aplicación DICOM creada")
print(f"    - Puedo enviar: CT (Tomografía)")

# ═══════════════════════════════════════════════════════════════════════════
# SECCIÓN 4: ESTABLECER LA ASOCIACIÓN (HANDSHAKE)
# ═══════════════════════════════════════════════════════════════════════════
"""
PASO 3: CONECTAR CON EL PACS
─────────────────────────────
ASSOCIATION = "Apretón de manos" entre dos máquinas DICOM

Proceso:
1. Tu script: "¡Hola! Soy una aplicación DICOM"
2. Orthanc:  "¡Hola! Soy Orthanc PACS"
3. Tu script: "¿Aceptas imágenes CT?"
4. Orthanc:  "Sí, aceptaré tus imágenes CT"
5. CONEXIÓN ESTABLECIDA ✓

Si algo falla (firewall, puerto cerrado, servidor caído), verás:
  "Falló la conexión. ¿Está Docker corriendo?"
"""

print(f"\n[.] Conectando con PACS en {IP_SERVIDOR}:{PUERTO_SERVIDOR}...")
print(f"    (Si se cuelga aquí, el servidor PACS no está disponible)")

# ae.associate() intenta conectar con el servidor DICOM remoto
assoc = ae.associate(IP_SERVIDOR, PUERTO_SERVIDOR, ae_title=AET_SERVIDOR)

# ═══════════════════════════════════════════════════════════════════════════
# SECCIÓN 5: VERIFICAR QUE LA ASOCIACIÓN FUNCIONÓ
# ═══════════════════════════════════════════════════════════════════════════

if assoc.is_established:
    print("[✓] Conexión establecida (Handshake OK)")
    print(f"    → Servidor reconoce que somos {AET_SERVIDOR}")
    print(f"    → La negociación DICOM fue exitosa")
    
    # ═════════════════════════════════════════════════════════════════════
    # SECCIÓN 6: ENVIAR LA IMAGEN (C-STORE)
    # ═════════════════════════════════════════════════════════════════════
    """
    PASO 4: TRANSMITIR LA IMAGEN
    ────────────────────────────
    C-STORE = "Guardar en el servidor remoto"
    
    assoc.send_c_store(dataset) hace:
      1. Empaqueta la imagen DICOM
      2. La envía por TCP/IP al puerto 4242
      3. El servidor DICOM procesa el paquete
      4. Devuelve un código de estado
      
    Códigos de estado comunes:
      0x0000 = SUCCESS (La imagen fue aceptada)
      0x0122 = SOP Class Not Supported (Servidor no acepta este tipo de imagen)
      0x0124 = SOP Instance Not Recognized (Archivo corrompido o inválido)
      0xC000 = General Error (Error genérico del servidor)
    """
    
    print(f"\n[.] Enviando imagen al PACS...")
    
    # Enviar la imagen usando C-STORE
    status = assoc.send_c_store(ds)
    
    # ═════════════════════════════════════════════════════════════════════
    # SECCIÓN 7: VERIFICAR LA RESPUESTA DEL SERVIDOR
    # ═════════════════════════════════════════════════════════════════════
    
    # Verificar si el servidor aceptó la imagen (0x0000 = Éxito)
    if status and status.Status == 0x0000:
        print("[✓] ¡ÉXITO! La imagen fue aceptada por el PACS")
        print(f"    → El servidor Orthanc guardó la imagen correctamente")
        print(f"    → Ahora está disponible en la base de datos PACS")
        print(f"    → Puedes verla en: http://127.0.0.1:8042")
        print("\n[✓✓✓] TRANSMISIÓN COMPLETADA EXITOSAMENTE ✓✓✓")
    else:
        # El servidor rechazó la imagen
        error_code = status.Status if status else "Desconocido"
        print(f"[✗] El servidor RECHAZÓ la imagen")
        print(f"    → Código de error: {hex(error_code)}")
        print(f"    → Posibles causas:")
        print(f"       - El archivo DICOM está corrompido")
        print(f"       - El servidor no acepta este tipo de imagen")
        print(f"       - Error en la configuración del PACS")
    
    # ═════════════════════════════════════════════════════════════════════
    # SECCIÓN 8: CERRAR LA CONEXIÓN
    # ═════════════════════════════════════════════════════════════════════
    """
    PASO 5: LIBERAR RECURSOS
    ────────────────────────
    assoc.release() cierra la conexión de forma ordenada.
    Es como colgar el teléfono después de una llamada.
    """
    
    print(f"\n[.] Cerrando conexión...")
    assoc.release()
    print("[✓] Conexión cerrada correctamente")

else:
    # La asociación falló desde el principio
    print("[✗] FALLÓ LA CONEXIÓN CON EL PACS")
    print("\nPosibles causas (en orden de probabilidad):")
    print("  1. Docker no está corriendo:")
    print("     → Ejecuta: sudo docker ps")
    print("     → Si 'mi-pacs' no aparece, inicia: sudo docker run -p 4242:4242 -p 8042:8042 --name mi-pacs -d jodogne/orthanc-plugins")
    print("\n  2. El firewall bloquea el puerto 4242:")
    print("     → Verifica: sudo firewall-cmd --list-all")
    print("     → Si 4242 no está abierto, abre: sudo firewall-cmd --add-port=4242/tcp --permanent")
    print("\n  3. El servidor DICOM está en otra IP/puerto:")
    print("     → Verifica los valores de IP_SERVIDOR y PUERTO_SERVIDOR")
    print("\n  4. Problemas de red:")
    print("     → Prueba: ping 127.0.0.1")
    print("     → Prueba: telnet 127.0.0.1 4242")

print("\n" + "=" * 80)
