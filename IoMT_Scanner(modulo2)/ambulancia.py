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
import sys
import os
import glob
from pynetdicom import AE, debug_logger
from pynetdicom.sop_class import CTImageStorage

# ═══════════════════════════════════════════════════════════════════════════
# OPCIONAL: Descomenta para ver TODOS los detalles técnicos del envío
# (Útil para troubleshooting)
# ═══════════════════════════════════════════════════════════════════════════
# debug_logger()

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
       
    NUEVO: Ahora puedes pasar:
       - Un archivo: python ambulancia.py paciente_anonimo.dcm
       - Una carpeta: python ambulancia.py Anonymized_20260129
"""

# Dirección del Servidor PACS (Orthanc en Docker)
IP_SERVIDOR = '127.0.0.1'          # Localhost (tu propia máquina)
PUERTO_SERVIDOR = 4242              # Puerto estándar DICOM
AET_SERVIDOR = 'ORTHANC'            # Application Entity Title del servidor

# El archivo anonimizado que creaste en el módulo anterior (por defecto)
ARCHIVO_A_ENVIAR = 'Anonymized_20260129'  # Puede ser archivo o carpeta

# ═══════════════════════════════════════════════════════════════════════════
# SECCIÓN 1.1: FUNCIONES AUXILIARES
# ═══════════════════════════════════════════════════════════════════════════

def obtener_archivos_dcm(ruta):
    """
    Obtiene lista de archivos DICOM desde:
    - Un archivo específico (.dcm)
    - Una carpeta (busca recursivamente todos los .dcm)
    
    Retorna: lista de rutas absolutas a archivos .dcm
    """
    archivos = []
    
    if os.path.isfile(ruta):
        # Es un archivo individual
        if ruta.lower().endswith('.dcm'):
            archivos.append(ruta)
        else:
            print(f"[✗] Error: '{ruta}' no es un archivo DICOM (.dcm)")
            exit(1)
    
    elif os.path.isdir(ruta):
        # Es una carpeta, buscar recursivamente
        patron = os.path.join(ruta, '**', '*.dcm')
        archivos = glob.glob(patron, recursive=True)
        
        if not archivos:
            print(f"[✗] No se encontraron archivos DICOM en: {ruta}")
            exit(1)
    
    else:
        print(f"[✗] Ruta no válida: {ruta}")
        print(f"    (No es un archivo ni una carpeta existente)")
        exit(1)
    
    return sorted(archivos)


def procesar_archivo_dicom(archivo_dicom, ae, ip_servidor, puerto_servidor, aet_servidor):
    """
    Procesa un archivo DICOM individual:
    1. Carga el archivo
    2. Se conecta al PACS
    3. Envía la imagen
    4. Verifica la respuesta
    
    Retorna: True si fue exitoso, False si falló
    """
    try:
        # Cargar imagen DICOM
        ds = pydicom.dcmread(archivo_dicom)
        print(f"\n[→] Procesando: {archivo_dicom}")
        print(f"    - ID Paciente: {ds.PatientID}")
        print(f"    - Tipo de estudio: {ds.Modality if hasattr(ds, 'Modality') else 'Desconocido'}")
        
    except Exception as e:
        print(f"[✗] Error al cargar {archivo_dicom}")
        print(f"    → {str(e)}")
        return False
    
    # Establecer conexión DICOM
    try:
        assoc = ae.associate(ip_servidor, puerto_servidor, ae_title=aet_servidor)
        
        if assoc.is_established:
            # Enviar imagen usando C-STORE
            status = assoc.send_c_store(ds)
            
            # Verificar respuesta
            if status and status.Status == 0x0000:
                print(f"    [✓] Enviado exitosamente")
                assoc.release()
                return True
            else:
                error_code = status.Status if status else "Desconocido"
                print(f"    [✗] Rechazado por PACS (Código: {hex(error_code)})")
                assoc.release()
                return False
        else:
            print(f"    [✗] No se pudo conectar al PACS")
            return False
            
    except Exception as e:
        print(f"    [✗] Error de conexión: {str(e)}")
        return False


# ═══════════════════════════════════════════════════════════════════════════
# SECCIÓN 1.2: PARSEAR ARGUMENTOS DE LÍNEA DE COMANDOS
# ═══════════════════════════════════════════════════════════════════════════

if len(sys.argv) > 1:
    # Si se pasó un argumento, usarlo
    ARCHIVO_A_ENVIAR = sys.argv[1]
    print(f"[i] Usando argumento: {ARCHIVO_A_ENVIAR}")
else:
    # Si no, usar el valor por defecto
    print(f"[i] Usando ruta por defecto: {ARCHIVO_A_ENVIAR}")

print("\n" + "=" * 80)
print("--- INICIANDO PROTOCOLO DE TRANSMISIÓN DICOM (C-STORE) ---")
print("=" * 80)

# ═══════════════════════════════════════════════════════════════════════════
# SECCIÓN 2: OBTENER LISTA DE ARCHIVOS DICOM A PROCESAR
# ═══════════════════════════════════════════════════════════════════════════

archivos_dicom = obtener_archivos_dcm(ARCHIVO_A_ENVIAR)
cantidad_archivos = len(archivos_dicom)

print(f"\n[i] Archivos DICOM encontrados: {cantidad_archivos}")
if cantidad_archivos <= 5:
    for archivo in archivos_dicom:
        print(f"    - {archivo}")
else:
    for archivo in archivos_dicom[:3]:
        print(f"    - {archivo}")
    print(f"    ... y {cantidad_archivos - 3} archivos más")

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
# SECCIÓN 4: PROCESAR TODOS LOS ARCHIVOS DICOM
# ═══════════════════════════════════════════════════════════════════════════
"""
PASO 3: CONECTAR Y ENVIAR CADA IMAGEN
──────────────────────────────────────
Iteramos sobre cada archivo DICOM encontrado y lo procesamos.
"""

print(f"\n[.] Conectando con PACS en {IP_SERVIDOR}:{PUERTO_SERVIDOR}...")
print(f"    (Si se cuelga aquí, el servidor PACS no está disponible)")

exitosos = 0
fallidos = 0

for idx, archivo in enumerate(archivos_dicom, 1):
    print(f"\n[{idx}/{cantidad_archivos}]", end=" ")
    
    if procesar_archivo_dicom(archivo, ae, IP_SERVIDOR, PUERTO_SERVIDOR, AET_SERVIDOR):
        exitosos += 1
    else:
        fallidos += 1

# ═══════════════════════════════════════════════════════════════════════════
# SECCIÓN 5: RESUMEN FINAL
# ═══════════════════════════════════════════════════════════════════════════

print(f"\n\n" + "=" * 80)
print("--- RESUMEN DE TRANSMISIÓN ---")
print("=" * 80)
print(f"Total procesados: {cantidad_archivos}")
print(f"[✓] Exitosos:    {exitosos}")
print(f"[✗] Fallidos:    {fallidos}")

if fallidos == 0:
    print(f"\n[✓✓✓] ¡TODAS LAS IMÁGENES FUERON ENVIADAS EXITOSAMENTE! ✓✓✓")
    print(f"    → Las imágenes están disponibles en: http://127.0.0.1:8042")
else:
    print(f"\n[!] Algunas imágenes no pudieron ser procesadas.")
    print(f"    → Verifica que el servidor PACS esté disponible")
    print(f"    → Intenta nuevamente: python ambulancia.py {ARCHIVO_A_ENVIAR}")

print("\n" + "=" * 80)
