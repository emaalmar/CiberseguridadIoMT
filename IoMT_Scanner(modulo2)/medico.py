import pydicom
from pydicom.data import get_testdata_file
import os

print("--- SISTEMA DE GESTIÓN DE DATOS MÉDICOS (DICOM) ---")

# 1. CARGAR UN PACIENTE DE PRUEBA
# Usamos un archivo de Tomografía Computarizada (CT) real que viene con la librería
print("[1] Cargando archivo DICOM de prueba...")
path_archivo = get_testdata_file("CT_small.dcm")
dataset = pydicom.dcmread(path_archivo)

# 2. LEER LOS "SECRETOS" DEL ARCHIVO
# Los archivos DICOM guardan datos en "Tags" (Etiquetas).
print("\n[2] LEYENDO METADATOS (Información Sensible):")
print("-" * 50)

# Accedemos a los datos como si fuera un objeto de Python
# Tag (0010,0010) - PatientName
if 'PatientName' in dataset:
    print(f" -> Nombre del Paciente: {dataset.PatientName}")
else:
    print(" -> Nombre del Paciente: [NO DISPONIBLE]")

# Tag (0010,0020) - PatientID
if 'PatientID' in dataset:
    print(f" -> ID del Paciente:     {dataset.PatientID}")

# Tag (0008,0060) - Modality (CT, MR, XA, etc.)
if 'Modality' in dataset:
    print(f" -> Modalidad (Tipo):    {dataset.Modality}")

# Tag (0008,0070) - Manufacturer
if 'Manufacturer' in dataset:
    print(f" -> Fabricante Equipo:   {dataset.Manufacturer}")

print("-" * 50)
print("¡ALERTA! Si este archivo sale del hospital así, violamos la ley GDPR.")

# 3. ANONIMIZACIÓN (CENSURA)
# Vamos a modificar los datos en memoria para proteger la identidad
print("\n[3] APLICANDO PROTOCOLO DE PRIVACIDAD (Anonimización)...")

# Cambiamos el nombre real por un código
dataset.PatientName = "ANONIMO_001"
# Borramos el ID original y ponemos uno genérico
dataset.PatientID = "123456"
# A veces es necesario borrar comentarios médicos privados
dataset.ImageComments = "Datos Censurados por Ing. Emanuel"

print(" -> Datos personales eliminados exitosamente.")

# 4. GUARDAR EL NUEVO ARCHIVO
nombre_nuevo = "paciente_anonimo.dcm"
dataset.save_as(nombre_nuevo)

print(f"\n[4] Archivo seguro guardado como: {nombre_nuevo}")
print("Este archivo ya puede ser enviado a investigación de forma segura.")