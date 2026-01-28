import hl7
import datetime

print("--- SISTEMA DE ADMISIÓN HOSPITALARIA (HL7 v2) ---")

# 1. DATOS DEL PACIENTE (Simulados)
nombre = "EMANUEL"
apellido = "LEDESMA"
id_paciente = "123456"
fecha_nacimiento = "19991108" # Formato YYYYMMDD
sexo = "M"

# 2. CREAR EL MENSAJE HL7
# En HL7 v2, el mensaje es un string gigante.
# \r significa "Salto de línea" (Carriage Return), que es el separador de segmentos.

timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

# Segmento MSH (Header)
# MSH | Separadores | Emisor | Lugar | Receptor | Lugar | Fecha | ... | Tipo Mensaje | ID | ... | Versión
msh = f"MSH|^~\\&|SISTEMA_PY|FEDORA|HIS_CENTRAL|BERLIN|{timestamp}||ADT^A01|MSG-{timestamp}|P|2.3"

# Segmento PID (Patient ID)
# PID | ID | ... | ID Interno | ... | APELLIDO^NOMBRE | ... | FECHA_NAC | SEXO
pid = f"PID|||{id_paciente}||{apellido}^{nombre}||{fecha_nacimiento}|{sexo}"

# Segmento PV1 (Patient Visit)
# PV1 | ... | Ubicación (Punto de cuidado^Habitación^Cama) | ... | Doctor
pv1 = "PV1||I|URGENCIAS^304^1||||001^DR. HOUSE"

# Unimos todo
mensaje_raw = f"{msh}\r{pid}\r{pv1}"

print("\n[1] MENSAJE GENERADO (Lo que viaja por el cable):")
print("-" * 50)
print(mensaje_raw)
print("-" * 50)

# 3. PARSEAR (Leer como máquina)
# Ahora usamos la librería 'hl7' para convertir ese texto feo en un objeto inteligente
print("\n[2] INTERPRETANDO EL MENSAJE (Lo que ve el servidor):")
h = hl7.parse(mensaje_raw)

# Accedemos como si fuera una matriz: h[segmento][campo]
print(f" -> Tipo de Evento:    {h[0][9]}")   # MSH-9 (ADT^A01)
print(f" -> ID Mensaje:        {h[0][10]}")  # MSH-10
print(f" -> Nombre Paciente:   {h[1][5]}")   # PID-5 (Nombre completo)
print(f" -> Ubicación:         {h[2][3]}")   # PV1-3 (Urgencias)

print("\n✅ Paciente admitido digitalmente.")