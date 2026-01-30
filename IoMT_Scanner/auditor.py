import pydicom
import sys

print("--- AUDITORÍA DE PRIVACIDAD ---")

try:
    # Intentamos leer el archivo que TU creaste
    dataset = pydicom.dcmread("paciente_anonimo.dcm")
    
    print(f"Archivo analizado: paciente_anonimo.dcm")
    print("-" * 40)
    
    # Verificamos los campos críticos
    nombre = dataset.PatientName
    id_paciente = dataset.PatientID
    comentarios = dataset.ImageComments
    
    print(f"Nombre encontrado: {nombre}")
    print(f"ID encontrado:     {id_paciente}")
    print(f"Comentarios:       {comentarios}")
    print("-" * 40)
    
    # Veredicto Automático
    if str(nombre) == "ANONIMO_001" and str(id_paciente) == "123456":
        print("✅ VEREDICTO: PASA (El archivo es seguro y anónimo).")
    else:
        print("❌ VEREDICTO: FALLA (Todavía hay datos sensibles).")

except FileNotFoundError:
    print("Error: No encuentro el archivo 'paciente_anonimo.dcm'.")
    print("¿Seguro que corriste el script 'medico.py' antes?")