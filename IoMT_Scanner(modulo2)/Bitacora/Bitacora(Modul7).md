# 🔌 Bitácora de Ciberseguridad IoMT: Protocolos de Integración (Módulo 7)

## Objetivo Estratégico
Ingeniería inversa y emulación del protocolo de transporte hospitalario (MLLP) para comprender la exposición de datos sensibles en tránsito. Construir un motor de integración desde cero usando Python sockets.

**Herramientas:** Python (`socket`, `hl7`), MLLP Protocol, TCP/IP, Wireshark (análisis de tráfico)

---

## 📝 Archivos Modificados en este Módulo

| Archivo | Tipo | Cambios Realizados |
|---------|------|-------------------|
| `recepcionista.py` | **Mejorado Drásticamente** | Ahora envía mensajes HL7 vía TCP/IP usando protocolo MLLP |
| `hospital_server.py` | **NUEVO** | Servidor TCP que escucha, parsea y responde mensajes HL7 |
| `Bitacora(Modulo7).md` | **NUEVO** | Documentación completa del módulo (este archivo) |

---

## 1. 🧭 El Pivote Táctico: Adaptabilidad (DevSecOps Mindset)

### El Reto Inicial

**Intento Original:** Desplegar Mirth Connect (Motor de Integración Clínico Comercial)

| Software | Problema Encontrado |
|----------|-------------------|
| **Mirth Connect** | Aplicación Java pesada (100+ MB) |
| **Java Runtime** | Bloqueos de API, versiones incompatibles |
| **Configuración** | Interfaz gráfica compleja, requiere experiencia |

### La Solución: Construir Nuestro Propio Motor

**Mentalidad DevSecOps:**
> "Si no puedo usar una herramienta externa, construyo la mía"

**Acción Tomada:**
- ❌ Reemplazar "Caja Negra" (Software de terceros)
- ✅ Construir solución propia en Python
- ✅ Trabajar a nivel de **Socket (Capa 4 del Modelo OSI)**
- ✅ Control total sobre cada byte de la red

### Valor de esta Aproximación

| Aspecto | Beneficio |
|---------|-----------|
| **Visibilidad** | Vemos CADA byte que viaja por la red |
| **Control** | Podemos modificar el protocolo a voluntad |
| **Aprendizaje** | Entendemos el protocolo de transporte médico |
| **Seguridad** | Identificamos vulnerabilidades a nivel de protocolo |
| **Portabilidad** | 100 líneas de Python vs 100MB de Java |

---

## 2. 🔐 Análisis del Protocolo MLLP: La Vulnerabilidad

### ¿Qué es MLLP?

**MLLP** = *Minimal Lower Layer Protocol* (Protocolo de Capa Inferior Mínima)

Es el **protocolo de transporte** que envuelve mensajes HL7 para enviarlos por la red TCP/IP.

### Estructura del Paquete MLLP

```
┌─────┬──────────────────────────┬─────┬─────┐
│ SB  │    MENSAJE HL7           │ EB  │ CR  │
└─────┴──────────────────────────┴─────┴─────┘
  ↑              ↑                   ↑     ↑
  │              │                   │     │
Start Block   Datos médicos      End Block │
(0x0B)        (Texto plano)       (0x1C)  Carriage Return
                                          (0x0D)
```

### Tabla de Caracteres de Control MLLP

| Carácter | Nombre | Valor Hexadecimal | Valor ASCII | Función |
|----------|--------|-------------------|-------------|---------|
| **SB** | Start Block (Vertical Tab) | `0x0B` | 11 | Marca el inicio del mensaje |
| **EB** | End Block (File Separator) | `0x1C` | 28 | Marca el fin del mensaje |
| **CR** | Carriage Return | `0x0D` | 13 | Fin de transmisión (ENTER) |

### 🔍 Explicación Profunda: ¿Por Qué Estos Valores Específicos?

#### ¿Qué es un "Byte de Control"?

En computación, hay caracteres especiales que **no se ven** pero tienen significado. Son como señales de tráfico en la red:

```
Caracteres normales:  A B C D E 1 2 3 = ş | ^ ~
                      ↑ Se ven en pantalla

Caracteres de control: SB EB CR
                      ↑ No se ven, pero cambian el comportamiento
```

#### Valores Específicos: ¿De Dónde Vienen?

Estos valores son **estándares de telecomunicaciones** establecidos hace 50+ años por la ASCII Table:

| Valor | Nombre Técnico | Uso Histórico | Uso en MLLP |
|-------|---|---|---|
| `0x0B` (11) | Vertical Tab (VT) | Antigas máquinas de escribir | **Señal de "EMPEZA A LEER"** |
| `0x1C` (28) | File Separator (FS) | Separador de archivos en cinta magnética | **Señal de "DEJA DE LEER"** |
| `0x0D` (13) | Carriage Return (CR) | Retorno del carro en máquina de escribir | **Fin de línea / PUNTO FINAL** |

#### Las 4 Formas de Representar el Mismo Byte

```python
# Todas estas líneas representan EXACTAMENTE lo mismo:

# Forma 1: Hexadecimal (más común en documentación técnica)
SB = b'\x0b'
#     ↑ ↑
#     │ Hexadecimal 0B (11 en decimal)
#     bytes (binary)

# Forma 2: Decimal (cómo el CPU lo interpreta)
SB = chr(11).encode('utf-8')
#     ↑
#     11 = 0x0B en decimal

# Forma 3: ASCII directo (si el teclado permitiera)
SB = b'\v'  # \v es escape sequence para vertical tab
#     ↑
#     Solo funciona para caracteres especiales conocidos

# Forma 4: Raw binary (raro, pero válido)
SB = bytes([0x0B])
#     ↑      ↑
#     bytes  [lista con número 11]

# VERIFICACIÓN: Son idénticas
assert chr(11).encode('utf-8') == b'\x0b'
assert bytes([11]) == b'\x0b'
assert b'\x0b' == b'\x0b'
```

#### Visualización: Qué Ocurre en la Red

```
LÍNEA DE TRANSMISIÓN (lo que viaja por el cable):

┌──────┬──────────────────────────────────┬──────┬──────┐
│ 0x0B │ MSH|^~\&|SISTEMA|FEDORA|...      │ 0x1C │ 0x0D │
└──────┴──────────────────────────────────┴──────┴──────┘
   ↑                   ↑                      ↑      ↑
   SB              Datos HL7                 EB     CR
   11              (texto legible)           28     13
(visual Tab)                               (no visible)
[NO se ve]                                 [NO se ve]

VISTA EN HEX (lo que Wireshark muestra):
0B 4D 53 48 7C 5E 7E 5C 26 ... 1C 0D
↑  M  S  H  |  ^  ~  \  &      ↑  ↑
SB [----------HL7 CONTENT-----------] EB CR
```

#### Tabla: Diferentes Representaciones

```python
# ¿Cómo escribir SB en Python?

# ❌ INCORRECTO (Confundir tipos)
SB = 11              # Es un entero, NO es bytes
SB = "0x0b"          # Es texto, NO es bytes
SB = '\x0b'          # Es STRING, no BYTES (error en socket.send)

# ✅ CORRECTO (Las 5 formas válidas)
SB = b'\x0b'         # Directo en hexadecimal ← MÁS COMÚN
SB = bytes([11])     # Lista de decimales
SB = chr(11).encode('utf-8')  # Conversión desde char
SB = b'\v'           # Escape sequence (solo para VT)
SB = b''.join([bytes([0x0B])])  # Metodo desusado pero válido
```

#### Tabla de Equivalencias: SB = EB = CR

| Representación | SB | EB | CR | Tipo |
|---|---|---|---|---|
| **Hexadecimal** | `0x0B` | `0x1C` | `0x0D` | En código |
| **Decimal** | `11` | `28` | `13` | ASCII standard |
| **Bytes Python** | `b'\x0b'` | `b'\x1c'` | `b'\x0d'` | Lo que usamos |
| **Char Python** | `chr(11)` | `chr(28)` | `chr(13)` | Conversión |
| **Visual** | `[VT]` | `[FS]` | `[CR]` | No visible en pantalla |
| **Teclado** | `Ctrl+K` | `Ctrl+\` | `ENTER` | Cómo generarlo (legacy) |

---

### 🎯 Ejemplo Práctico: Construir un Paquete MLLP Paso a Paso

```python
# PASO 1: Definir los caracteres de control
SB = b'\x0b'     # Byte de inicio
EB = b'\x1c'     # Byte de fin
CR = b'\x0d'     # Carriage return

# PASO 2: Mensaje HL7 (texto normal)
mensaje_hl7 = "MSH|^~\\&|SISTEMA|FEDORA|MIRTH|SERVER|...\rPID|||123456||LEDESMA^EMANUEL|..."

# PASO 3: Convertir a bytes
mensaje_bytes = mensaje_hl7.encode('utf-8')

# PASO 4: EMPAQUETAR en MLLP
mensaje_mllp = SB + mensaje_bytes + EB + CR

# PASO 5: Ver qué es
print(type(mensaje_mllp))  # <class 'bytes'>
print(len(mensaje_mllp))   # Tamaño total

# PASO 6: Enviar por socket
socket.send(mensaje_mllp)
#           ↑ Requiere BYTES, no STRING
```

#### Visualización del Proceso

```
ENTRADA (STRING):
"MSH|^~\&|SISTEMA|FEDORA|..."
    ↓ .encode('utf-8')
BYTES:
b'MSH|^~\&|SISTEMA|FEDORA|...'
    ↓ Agregar wrapper
MLLP:
b'\x0b' + b'MSH|^~\&|...' + b'\x1c\x0d'
    ↓
TRANSMISIÓN POR SOCKET:
[0B 4D 53 48 7C ....... 1C 0D]
 ↑                      ↑  ↑
 SB                    EB CR
```

---

### 🔍 Explicación Profunda: Acceso a la Matriz HL7

Ahora que entiendes MLLP, es hora de entender cómo **leer los datos** del mensaje HL7.

#### El Problema: String vs Matriz Estructurada

```python
# ❌ PROBLEMA: Tienes un string crudo
mensaje_crudo = "MSH|^~\\&|SISTEMA|FEDORA|MIRTH|SERVER|20260129120000||ADT^A01|MSG-20260129120000|P|2.3\rPID|||123456||LEDESMA^EMANUEL||19991108|M\rPV1||I|URGENCIAS^304^1||||001^DR. HOUSE"

# ¿Cómo sacas el nombre del paciente?
# Opción 1: Contar pipes manualmente
campos = mensaje_crudo.split('|')
nombre = campos[5]  # ¿Pero cuál es el campo 5? ¿En qué segmento?

# Opción 2: Regex (complicado y frágil)
import re
nombre = re.search(r'PID.*?\|{4}(.*?)\|', mensaje_crudo).group(1)

# ❌ AMBAS son malas, propensas a errores
```

#### ✅ LA SOLUCIÓN: Usar `hl7.parse()`

```python
import hl7

mensaje_crudo = "MSH|^~\\&|...\rPID|||123456||LEDESMA^EMANUEL|...\rPV1||I|URGENCIAS^304^1|..."

# parse() convierte el string en una MATRIZ ESTRUCTURADA
h = hl7.parse(mensaje_crudo)

# ¿Qué es h?
# No es un diccionario, no es una lista simple
# Es una LISTA DE LISTAS (matriz 2D)
# Donde cada fila es un SEGMENTO
# Y cada columna es un CAMPO

print(type(h))  # <class 'list'>
print(len(h))   # 3 (tenemos 3 segmentos: MSH, PID, PV1)
```

#### Estructura Completa de la Matriz h

```
Mensaje Crudo:
MSH|^~\&|SISTEMA|FEDORA|MIRTH|SERVER|20260129120000||ADT^A01|MSG-123|P|2.3
PID|||123456||LEDESMA^EMANUEL||19991108|M
PV1||I|URGENCIAS^304^1||||001^DR. HOUSE

↓ h = hl7.parse(mensaje)

h = [
  # SEGMENTO 0 (MSH - Message Header)
  [
    "MSH",        # h[0][0] - Identificador del segmento
    "^~\\&",      # h[0][1] - Delimitadores
    "SISTEMA",    # h[0][2] - Emisor
    "FEDORA",     # h[0][3] - Ubicación origen
    "MIRTH",      # h[0][4] - Receptor
    "SERVER",     # h[0][5] - Ubicación destino
    "20260129120000",  # h[0][6] - Timestamp
    "",           # h[0][7] - Security (vacío)
    "ADT^A01",    # h[0][8] - Message Type ← Tipo de evento
    "MSG-123",    # h[0][9] - Message Control ID ← ID único
    "P",          # h[0][10] - Processing ID
    "2.3"         # h[0][11] - HL7 Version
  ],
  
  # SEGMENTO 1 (PID - Patient ID)
  [
    "PID",           # h[1][0] - Identificador del segmento
    "",              # h[1][1] - (vacío)
    "",              # h[1][2] - (vacío)
    "123456",        # h[1][3] - Patient ID Interno
    "",              # h[1][4] - (vacío)
    "LEDESMA^EMANUEL", # h[1][5] - Nombre del Paciente ← ESTO ES LO QUE QUEREMOS
    "",              # h[1][6] - (vacío)
    "19991108",      # h[1][7] - Fecha nacimiento
    "M"              # h[1][8] - Sexo
  ],
  
  # SEGMENTO 2 (PV1 - Patient Visit)
  [
    "PV1",           # h[2][0] - Identificador del segmento
    "",              # h[2][1] - (vacío)
    "I",             # h[2][2] - (vacío)
    "URGENCIAS^304^1", # h[2][3] - Ubicación (Punto de cuidado^Habitación^Cama)
    "",              # h[2][4] - (vacío)
    "",              # h[2][5] - (vacío)
    "",              # h[2][6] - (vacío)
    "",              # h[2][7] - (vacío)
    "001^DR. HOUSE"  # h[2][8] - Doctor asignado
  ]
]
```

#### El Mapa Visual: Cómo Acceder a h[0][9]

```
                    SEGMENTO 0 (MSH)
                           │
          ┌────────────────┼────────────────┐
          │                │                │
[0][0]    [0][1]    [0][2]  [0][3]   ...   [0][9]
  │        │         │       │            │
"MSH"  "^~\&"   "SISTEMA" "FEDORA"     "MSG-123"
                                          ↑
                              ESTO ES LO QUE QUEREMOS
                              Message Control ID
                              Campo 9 del Segmento 0
```

#### Tabla: Índices Comunes y Sus Significados

```python
# Acceso: h[SEGMENTO][CAMPO]
#         h[   0-3    ][  0-15  ]

# EJEMPLOS COMUNES:

# MSH (Segmento 0)
h[0][0]   # "MSH" - Identificador
h[0][9]   # Tipo de evento (ADT^A01) ← h[0][8] en realidad
h[0][10]  # Message Control ID

# PID (Segmento 1)  
h[1][0]   # "PID" - Identificador
h[1][3]   # Patient ID (número de historia)
h[1][5]   # Nombre del paciente (APELLIDO^NOMBRE) ← IMPORTANTE

# PV1 (Segmento 2)
h[2][0]   # "PV1" - Identificador
h[2][3]   # Ubicación (PISO^HABITACION^CAMA)
h[2][7]   # Doctor asignado

# OBR (Observation Request - si existe)
h[3][0]   # "OBR" - Identificador
h[3][4]   # Código de test/orden
h[3][16]  # Médico ordenante
```

#### La Indexación Python (Base 0)

```
IMPORTANTE: Python empieza a contar desde 0, NO desde 1

Posición Visual:  1ª    2ª    3ª    4ª    5ª    6ª
Índice Python:    0     1     2     3     4     5

Ejemplos:
- "MSH" es el campo [0] (primer campo)
- "^~\&" es el campo [1] (segundo campo)
- "SISTEMA" es el campo [2] (tercer campo)
- El nombre está en el campo [5] (sexto campo)

RECUERDA: 
h[0][5] ≠ h[0][6]
h[0][5] = "SISTEMA" (campo 5, posición 6)
h[0][6] = "FEDORA" (campo 6, posición 7)
```

---

### 🎯 Ejemplo Práctico: Extraer Datos del Mensaje

```python
import hl7

# PASO 1: Mensaje crudo
mensaje_raw = "MSH|^~\\&|SISTEMA|FEDORA|MIRTH|SERVER|20260129120000||ADT^A01|MSG-123456|P|2.3\rPID|||123456||LEDESMA^EMANUEL||19991108|M\rPV1||I|URGENCIAS^304^1||||001^DR. HOUSE"

# PASO 2: Parsear en matriz
h = hl7.parse(mensaje_raw)

# PASO 3: EXTRAER DATOS CRÍTICOS
print("=== INFORMACIÓN DEL MENSAJE ===")
print(f"Tipo de Evento:    {h[0][8]}")    # MSH-9 → ADT^A01
print(f"ID Mensaje:        {h[0][10]}")   # MSH-11 → MSG-123456
print(f"Nombre Paciente:   {h[1][5]}")    # PID-5 → LEDESMA^EMANUEL
print(f"ID Paciente:       {h[1][3]}")    # PID-3 → 123456
print(f"Fecha Nacimiento:  {h[1][7]}")    # PID-7 → 19991108
print(f"Sexo:              {h[1][8]}")    # PID-8 → M
print(f"Ubicación:         {h[2][3]}")    # PV1-3 → URGENCIAS^304^1
print(f"Doctor:            {h[2][8]}")    # PV1-8 → 001^DR. HOUSE

# PASO 4: PROCESAR DATOS (Ejemplo: Separar nombre y apellido)
nombre_completo = h[1][5]  # "LEDESMA^EMANUEL"
partes = nombre_completo.split('^')
apellido = partes[0]  # "LEDESMA"
nombre = partes[1]    # "EMANUEL"

print(f"\nApellido: {apellido}")
print(f"Nombre:   {nombre}")
```

#### Salida del Script:
```
=== INFORMACIÓN DEL MENSAJE ===
Tipo de Evento:    ADT^A01
ID Mensaje:        MSG-123456
Nombre Paciente:   LEDESMA^EMANUEL
ID Paciente:       123456
Fecha Nacimiento:  19991108
Sexo:              M
Ubicación:         URGENCIAS^304^1
Doctor:            001^DR. HOUSE

Apellido: LEDESMA
Nombre:   EMANUEL
```

---

### 📊 Tabla Resumen: De Crudo a Matriz

| Paso | Input | Proceso | Output | Tipo |
|------|-------|---------|--------|------|
| 1 | Mensaje HL7 | `hl7.parse()` | Matriz h[seg][campo] | list |
| 2 | h[0][10] | Acceso directo | "MSG-123456" | str |
| 3 | h[1][5] | Split por "^" | ["LEDESMA", "EMANUEL"] | list |
| 4 | Elemento [0] | Acceso a lista | "LEDESMA" | str |
| 5 | Elemento [1] | Acceso a lista | "EMANUEL" | str |

---

### ⚠️ Errores Comunes (Y cómo evitarlos)

```python
# ❌ ERROR 1: Confundir STRING con MATRIZ
h = "MSH|^~\&|..."  # String (incorrecto)
h[0][9]            # IndexError: string index out of range

# ✅ SOLUCIÓN: Usar hl7.parse()
h = hl7.parse(mensaje_raw)  # Matriz (correcto)

# ❌ ERROR 2: Off-by-one (confundir índices)
nombre = h[1][6]   # Probablemente vacío
nombre = h[1][5]   # ✅ Correcto

# ❌ ERROR 3: Olvidar que Python empieza en 0
# Documentación HL7: "PID-5 es el nombre"
# Python: h[1][5] (porque el primer campo es h[1][0])

# ❌ ERROR 4: No validar antes de acceder
id_med = h[0][10]  # Qué si el mensaje no tiene esto?
# ✅ SOLUCIÓN:
if len(h) > 0 and len(h[0]) > 10:
    id_med = h[0][10]
else:
    id_med = "DESCONOCIDO"

# ❌ ERROR 5: No decodificar bytes
datos_socket = b'MSH|...'
h = hl7.parse(datos_socket)  # Error: puede ser bytes

# ✅ SOLUCIÓN:
datos_texto = datos_socket.decode('utf-8')
h = hl7.parse(datos_texto)
```

### Ejemplo Real de Paquete MLLP

```python
# Mensaje HL7 original:
mensaje_hl7 = "MSH|^~\&|SISTEMA_PY|FEDORA|...\rPID|||123456||LEDESMA^EMANUEL|..."

# Empaquetado en MLLP:
SB = chr(11)   # Vertical Tab
EB = chr(28)   # File Separator  
CR = chr(13)   # Carriage Return

mensaje_mllp = SB + mensaje_hl7 + EB + CR

# Resultado en hexadecimal:
# 0B 4D 53 48 7C 5E 7E ... 1C 0D
# ↑  M  S  H  |  ^  ~      ↑  ↑
# SB                       EB CR
```

---

## 3. 🚨 Hallazgo Crítico de Seguridad

### ⚠️ MLLP NO TIENE CIFRADO NATIVO

**Descubrimiento:**
Durante la implementación del servidor, notamos que:

```
[Cliente] → Envía mensaje
     ↓
[Servidor] → Recibe mensaje
     ↓
¿Se intercambiaron llaves criptográficas? NO
¿Se negoció un certificado SSL? NO
¿Los datos están cifrados? NO
```

### Comparativa: MLLP vs Protocolos Seguros

| Protocolo | Cifrado | Autenticación | Integridad | Uso Médico |
|-----------|---------|---------------|------------|------------|
| **MLLP** | ❌ Ninguno | ❌ Ninguna | ❌ Ninguna | HL7 legacy (años 90) |
| **TLS/SSL** | ✅ AES-256 | ✅ Certificados | ✅ HMAC | HTTPS moderno |
| **MLLP+TLS** | ✅ AES-256 | ✅ Certificados | ✅ HMAC | Hospitales modernos |
| **VPN IPSec** | ✅ AES-256 | ✅ Pre-shared keys | ✅ HMAC | Redes corporativas |

### ⚠️ Veredicto de Seguridad

> **MLLP estándar transmite datos médicos (Nombres, IDs, Diagnósticos) en TEXTO PLANO (Cleartext).**

**Impacto:**
- Cualquier persona conectada a la red Wi-Fi del hospital podría interceptar los mensajes
- No hay autenticación (cualquier máquina puede enviar mensajes)
- No hay integridad (los mensajes pueden ser modificados en tránsito)

### Escenario de Ataque Real

```
[Atacante con laptop en la cafetería del hospital]
     ↓
[Conectado al Wi-Fi "Hospital_Guest"]
     ↓
[Ejecuta: sudo tcpdump -i wlan0 port 6661]
     ↓
[Captura paquetes MLLP en texto plano]
     ↓
RESULTADO: Lee nombres, diagnósticos, médicos tratantes
```

---

## 4. 🛠️ Implementación del Cliente: `recepcionista.py` (Versión Mejorada)

### Modificaciones Clave

#### Antes (Módulo 5):
```python
# Solo imprimía el mensaje HL7 en la terminal
print(mensaje_hl7)
```

#### Ahora (Módulo 7):
```python
# Envía el mensaje por la RED a un servidor real
s.send(mensaje_mllp.encode('utf-8'))
```

### Imports Críticos del Cliente

```python
import hl7          # Parseador de mensajes HL7
import datetime     # Timestamps para Control IDs
import socket       # Comunicación TCP/IP (Capa 4 OSI)
```

### Tabla de Imports: ¿Para Qué Sirven?

| Import | Propósito | Sin Esto... |
|--------|-----------|-------------|
| `hl7` | Parsear/generar mensajes HL7 | Tendríamos que manipular strings manualmente |
| `datetime` | Crear timestamps únicos | Los mensajes no tendrían IDs únicos |
| `socket` | Comunicación de red TCP/IP | No podríamos enviar datos por la red |

### Flujo del Cliente (Paso a Paso)

```python
# PASO 1: CREAR MENSAJE HL7
timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
msh = f"MSH|^~\&|SISTEMA_PY|FEDORA|MIRTH|SERVER|{timestamp}||ADT^A01|..."
mensaje_hl7 = f"{msh}\r{pid}\r{pv1}"

# PASO 2: EMPAQUETAR EN MLLP
SB = chr(11)   # Start Block
EB = chr(28) + chr(13)  # End Block + Carriage Return
mensaje_mllp = SB + mensaje_hl7 + EB

# PASO 3: CREAR CONEXIÓN TCP
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#                 ↑               ↑
#                 IPv4            TCP (no UDP)

# PASO 4: CONECTAR AL SERVIDOR
s.connect(('localhost', 6661))
#          ↑             ↑
#          IP destino    Puerto destino

# PASO 5: ENVIAR DATOS
s.send(mensaje_mllp.encode('utf-8'))
#                           ↑
#                    String → bytes

# PASO 6: RECIBIR RESPUESTA (ACK)
respuesta = s.recv(1024)  # Buffer de 1024 bytes
print(respuesta.decode('utf-8'))

# PASO 7: CERRAR CONEXIÓN
s.close()
```

### Diagrama de Flujo: Cliente HL7

```
[1] GENERAR MENSAJE HL7
    ↓
[2] EMPAQUETAR EN MLLP (SB + mensaje + EB + CR)
    ↓
[3] CREAR SOCKET TCP
    ↓
[4] CONECTAR A SERVIDOR (IP:PUERTO)
    ↓
[5] ENVIAR BYTES POR LA RED
    ↓
[6] ESPERAR ACK (Acknowledgment)
    ↓
[7] CERRAR CONEXIÓN
```

---

## 5. 🖥️ Implementación del Servidor: `hospital_server.py`

### Imports Críticos del Servidor

```python
import socket       # Escuchar conexiones TCP
import hl7          # Parsear mensajes HL7 recibidos
import datetime     # Timestamps para ACKs
```

### Arquitectura del Servidor (Componentes)

```
┌───────────────────────────────────────────────────┐
│         HOSPITAL_SERVER.PY (LISTENER)             │
├───────────────────────────────────────────────────┤
│ [1] SOCKET LISTENER                               │
│     └─ Escucha en puerto 6661 (TCP)              │
├───────────────────────────────────────────────────┤
│ [2] DESEMPAQUETADOR MLLP                         │
│     └─ Remueve SB, EB, CR del paquete            │
├───────────────────────────────────────────────────┤
│ [3] PARSEADOR HL7                                │
│     └─ Convierte string → matriz h[seg][campo]   │
├───────────────────────────────────────────────────┤
│ [4] EXTRACTOR DE DATOS                           │
│     └─ Lee nombre, evento, control ID            │
├───────────────────────────────────────────────────┤
│ [5] GENERADOR DE ACK                             │
│     └─ Crea respuesta MSA|AA|{control_id}        │
├───────────────────────────────────────────────────┤
│ [6] EMPAQUETADOR MLLP                            │
│     └─ Envuelve ACK con SB + EB + CR             │
├───────────────────────────────────────────────────┤
│ [7] TRANSMISOR TCP                               │
│     └─ Envía ACK de vuelta al cliente            │
└───────────────────────────────────────────────────┘
```

### Flujo del Servidor (Detallado)

```python
# PASO 1: CONFIGURAR SERVIDOR
HOST = '0.0.0.0'  # Escuchar en TODAS las interfaces de red
PORT = 6661       # Puerto estándar HL7 MLLP
SB = b'\x0b'      # Start Block (en bytes)
EB = b'\x1c'      # End Block (en bytes)
CR = b'\x0d'      # Carriage Return (en bytes)

# PASO 2: CREAR SOCKET Y ENLAZARLO AL PUERTO
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#            ↑                   ↑
#            Socket Level      Reusar dirección (evita "Address already in use")

s.bind((HOST, PORT))  # Enlazar al puerto 6661
s.listen()            # Empezar a escuchar conexiones

# PASO 3: ACEPTAR CONEXIONES (BUCLE INFINITO)
while True:
    conn, addr = s.accept()  # Bloquea hasta que alguien se conecte
    #    ↑     ↑
    #    │     └─ Dirección del cliente (IP, Puerto)
    #    └─ Conexión establecida
    
    # PASO 4: RECIBIR DATOS
    datos_crudos = conn.recv(4096)  # Leer hasta 4KB
    
    # PASO 5: DESEMPAQUETAR MLLP
    mensaje_limpio = datos_crudos[1:-2]  # Quitar SB (1) y EB+CR (-2)
    #                            ↑    ↑
    #                       Slice  Slice
    
    mensaje_texto = mensaje_limpio.decode('utf-8')
    
    # PASO 6: PARSEAR HL7
    h = hl7.parse(mensaje_texto)
    
    # PASO 7: EXTRAER DATOS
    tipo_mensaje = h[0][9]   # MSH-9 (ADT^A01)
    id_control = h[0][10]    # MSH-10 (MSG-20260129...)
    nombre_paciente = h[1][5] # PID-5 (LEDESMA^EMANUEL)
    
    # PASO 8: GENERAR ACK (ACKNOWLEDGMENT)
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    ack_hl7 = f"MSH|^~\&|PYTHON_SRV|LINUX|...|{timestamp}||ACK|...\r"
    ack_hl7 += f"MSA|AA|{id_control}"  # AA = Application Accept
    #            ↑  ↑
    #            │  └─ Echo del ID original
    #            └─ Código de aceptación
    
    # PASO 9: EMPAQUETAR ACK EN MLLP
    ack_mllp = SB + ack_hl7.encode('utf-8') + EB + CR
    
    # PASO 10: ENVIAR ACK AL CLIENTE
    conn.sendall(ack_mllp)
    
    # PASO 11: CERRAR CONEXIÓN
    conn.close()
```

### Técnica Crítica: Slicing vs Replace

#### ❌ Método INCORRECTO (replace):
```python
# Problema: Si el mensaje contiene 0x0B o 0x1C internamente, se rompe
mensaje_limpio = datos_crudos.replace(SB, b'').replace(EB, b'').replace(CR, b'')
```

**Riesgo:**
- Si el nombre del paciente es "Dr. O'Brien" y contiene bytes similares
- El `replace()` eliminaría caracteres internos del mensaje
- **Resultado:** Corrupción de datos médicos críticos

#### ✅ Método CORRECTO (slicing):
```python
# Solo remueve el PRIMER byte (SB) y los ÚLTIMOS 2 bytes (EB+CR)
mensaje_limpio = datos_crudos[1:-2]
#                            ↑   ↑
#                    Desde posición 1 (salta SB)
#                    Hasta 2 antes del final (salta EB+CR)
```

**Ventajas:**
- No toca el contenido interno del mensaje
- Siempre funciona, independiente del contenido
- Evita buffer overflow y corrupción

---

## 6. 🔄 Protocolo de Comunicación Completo

### Diagrama de Secuencia

```
CLIENTE (recepcionista.py)          SERVIDOR (hospital_server.py)
         │                                    │
         │  [1] Crear mensaje HL7             │
         │  MSH|...|ADT^A01|MSG123|...       │
         │  PID|||123456||LEDESMA^EMANUEL|... │
         │                                    │
         │  [2] Empaquetar MLLP               │
         │  SB + mensaje + EB + CR            │
         │                                    │
         │  [3] TCP Connect (puerto 6661)     │
         ├────────────────────────────────────>│
         │                                    │ [4] Accept connection
         │                                    │
         │  [5] SEND (mensaje_mllp)           │
         ├────────────────────────────────────>│
         │                                    │ [6] RECV (4096 bytes)
         │                                    │
         │                                    │ [7] Desempaquetar MLLP
         │                                    │     mensaje[1:-2]
         │                                    │
         │                                    │ [8] Parsear HL7
         │                                    │     h = hl7.parse()
         │                                    │
         │                                    │ [9] Extraer datos
         │                                    │     nombre = h[1][5]
         │                                    │
         │                                    │ [10] Generar ACK
         │                                    │      MSA|AA|MSG123
         │                                    │
         │  [11] RECV ACK                     │ [12] SEND ACK
         │<────────────────────────────────────┤
         │  MSA|AA|MSG123                     │
         │                                    │
         │  [13] Close connection             │
         ├────────────────────────────────────>│
         │                                    │
```

### Códigos de ACK (Acknowledgment)

| Código | Nombre | Significado | Acción del Cliente |
|--------|--------|-------------|--------------------|
| **AA** | Application Accept | ✅ Mensaje recibido y procesado correctamente | Continuar |
| **AE** | Application Error | ❌ Mensaje recibido pero hubo error de aplicación | Revisar datos |
| **AR** | Application Reject | 🚫 Mensaje rechazado por reglas de negocio | No reintentar |
| **CA** | Commit Accept | ✅ Datos guardados en base de datos | Confirmar |
| **CE** | Commit Error | ❌ Error al guardar en BD | Reintentar |
| **CR** | Commit Reject | 🚫 Datos rechazados por BD | Revisar integridad |

---

## 7. 🔬 Conceptos Técnicos que Debes Dominar

### Capa 4 del Modelo OSI: Transporte (TCP)

```
┌─────────────────────────────────────────┐
│ CAPA 7: APLICACIÓN (HL7)                │ ← Mensajes médicos
├─────────────────────────────────────────┤
│ CAPA 6: PRESENTACIÓN (UTF-8, ASCII)     │ ← Codificación
├─────────────────────────────────────────┤
│ CAPA 5: SESIÓN (MLLP)                   │ ← Protocolo de transporte médico
├─────────────────────────────────────────┤
│ CAPA 4: TRANSPORTE (TCP)                │ ← SOCKET (Tu código trabaja aquí)
├─────────────────────────────────────────┤
│ CAPA 3: RED (IP)                        │ ← 127.0.0.1, 192.168.1.x
├─────────────────────────────────────────┤
│ CAPA 2: ENLACE (Ethernet)               │ ← MAC Address
├─────────────────────────────────────────┤
│ CAPA 1: FÍSICA (Cables, Wi-Fi)          │ ← Señales eléctricas
└─────────────────────────────────────────┘
```

### TCP vs UDP (¿Por qué TCP?)

| Característica | TCP | UDP | Elección para HL7 |
|---|---|---|---|
| **Conexión** | Orientado a conexión | Sin conexión | ✅ TCP (necesitamos handshake) |
| **Garantía de entrega** | Sí (retransmite paquetes perdidos) | No | ✅ TCP (datos médicos críticos) |
| **Orden de paquetes** | Garantizado | No garantizado | ✅ TCP (orden importa) |
| **Velocidad** | Más lento | Más rápido | TCP (prioridad: confiabilidad) |
| **Uso típico** | HTTP, FTP, HL7 | DNS, Streaming | HL7 = TCP siempre |

### Bytes vs Strings (Codificación)

```python
# STRING (Python str)
mensaje_str = "MSH|^~\&|SISTEMA|..."
tipo = type(mensaje_str)  # <class 'str'>

# BYTES (Python bytes)
mensaje_bytes = mensaje_str.encode('utf-8')
tipo = type(mensaje_bytes)  # <class 'bytes'>

# CONVERSIÓN
string → bytes: .encode('utf-8')
bytes → string: .decode('utf-8')

# ¿POR QUÉ IMPORTANTE?
# socket.send() requiere BYTES
# hl7.parse() requiere STRING
```

### Tabla de Conversiones Críticas

| Operación | Input | Output | Función |
|-----------|-------|--------|---------|
| String → Bytes | `"MSH\|..."` | `b'MSH\|...'` | `.encode('utf-8')` |
| Bytes → String | `b'MSH\|...'` | `"MSH\|..."` | `.decode('utf-8')` |
| Char → Byte | `chr(11)` | `b'\x0b'` | `chr().encode()` |
| Hex → Byte | `0x0B` | `b'\x0b'` | `bytes([0x0B])` |

---

## 8. 🗺️ Estado Actual del Laboratorio: Ecosistema Completo

### Mapa de tu Red IoMT

```
┌────────────────────────────────────────────────────────────────────┐
│              TU LABORATORIO IoMT - MÓDULO 7                        │
├────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────┐                    ┌──────────────────┐      │
│  │ CLIENTE HL7     │                    │ SERVIDOR HL7     │      │
│  │ recepcionista.py│──── TCP 6661 ────>│ hospital_server.py│     │
│  │                 │   (MLLP)           │                  │      │
│  │ - Genera ADT^A01│                    │ - Parsea mensaje │      │
│  │ - Empaqueta MLLP│<──── ACK ─────────│ - Envía ACK      │      │
│  └─────────────────┘                    └──────────────────┘      │
│          │                                        │                │
│          │                                        │                │
│          v                                        v                │
│  ┌─────────────────┐                    ┌──────────────────┐      │
│  │ RED VIRTUAL     │                    │ LOGS / AUDITORÍA │      │
│  │ localhost       │                    │ (stdout)         │      │
│  │ 127.0.0.1       │                    └──────────────────┘      │
│  └─────────────────┘                                              │
│                                                                     │
│  ┌────────────────────────────────────────────────────────┐       │
│  │ PACS ORTHANC (Módulo 4-6)                              │       │
│  │ - Puerto 4242 (DICOM)                                  │       │
│  │ - Puerto 8042 (HTTP REST API)                          │       │
│  │ - Almacena imágenes médicas                            │       │
│  └────────────────────────────────────────────────────────┘       │
│                                                                     │
│  ┌────────────────────────────────────────────────────────┐       │
│  │ SCANNER DE RED (Módulo 1-2)                            │       │
│  │ - radar.py (Descubrimiento)                            │       │
│  │ - vigilante.py (Detección de intrusos)                 │       │
│  └────────────────────────────────────────────────────────┘       │
└────────────────────────────────────────────────────────────────────┘
```

### Vectores de Ataque Posibles

| # | Vector | Herramienta | Impacto |
|---|--------|-------------|---------|
| 1 | **Sniffing de red** | Wireshark, tcpdump | Leer mensajes HL7 en texto plano |
| 2 | **Man-in-the-Middle** | ARP Spoofing | Modificar mensajes en tránsito |
| 3 | **Inyección HL7** | Script Python malicioso | Crear pacientes falsos |
| 4 | **DoS (Denial of Service)** | Flood de mensajes | Saturar el servidor |
| 5 | **Port Scanning** | nmap | Descubrir servicios HL7 |

---

## 9. 🛡️ Lecciones de Seguridad Aprendidas

### Vulnerabilidades Identificadas

| Vulnerabilidad | Causa Raíz | Mitigación |
|---|---|---|
| **Sin cifrado** | MLLP estándar no cifra | Usar MLLP+TLS (puerto 2575) |
| **Sin autenticación** | Protocolo legacy | Implementar certificados cliente |
| **Sin validación** | Confiar en remitente | Validar origen por IP/firewall |
| **Sin auditoría** | Solo print() en consola | Log a archivo + SIEM |
| **Bind a 0.0.0.0** | Expuesto a toda la red | Bind solo a 127.0.0.1 en dev |

### Controles de Seguridad Recomendados

```python
# ❌ INSEGURO (Actual)
HOST = '0.0.0.0'  # Cualquiera puede conectarse

# ✅ SEGURO (Producción)
HOST = '127.0.0.1'  # Solo localhost
# O mejor aún:
WHITELIST_IPS = ['192.168.1.10', '192.168.1.11']

def validar_origen(addr):
    if addr[0] not in WHITELIST_IPS:
        print(f"[!] ALERTA: Conexión rechazada desde {addr[0]}")
        return False
    return True
```

### Implementación de MLLP Seguro (TLS)

```python
import ssl

# Crear contexto SSL
context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
context.load_cert_chain(certfile="server.crt", keyfile="server.key")

# Envolver socket con TLS
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    
    with context.wrap_socket(s, server_side=True) as secure_socket:
        conn, addr = secure_socket.accept()
        # Ahora los datos viajan cifrados
```

---

## 10. 📚 Resumen de lo que Aprendiste

### Conocimientos Técnicos Adquiridos

| Concepto | Descripción | Aplicación |
|----------|-------------|------------|
| **Python Sockets** | Programación de red a bajo nivel | Crear servidores y clientes TCP |
| **MLLP Protocol** | Protocolo de transporte HL7 | Entender cómo viajan mensajes médicos |
| **TCP/IP** | Capa de transporte (OSI Layer 4) | Comunicación confiable entre máquinas |
| **Bytes vs Strings** | Codificación de datos | Conversión para sockets y parsing |
| **Slicing Python** | Técnica de extracción de datos | Limpiar wrappers sin corromper datos |
| **ACK/NACK** | Protocolos de confirmación | Implementar comunicación robusta |

### Habilidades de Ciberseguridad

| Habilidad | Nivel | Evidencia |
|-----------|-------|-----------|
| **Ingeniería Inversa** | ⭐⭐⭐⭐ | Replicaste MLLP sin documentación oficial |
| **Análisis de Protocolos** | ⭐⭐⭐⭐ | Identificaste falta de cifrado |
| **Desarrollo de Exploits** | ⭐⭐⭐ | Podrías crear un sniffer HL7 |
| **Auditoría de Seguridad** | ⭐⭐⭐⭐ | Evaluaste toda la cadena de comunicación |
| **DevSecOps** | ⭐⭐⭐⭐⭐ | Construiste tu propio motor de integración |

---

## 11. 🎯 Ejercicios de Refuerzo

### Nivel 1: Básico
1. Modifica `recepcionista.py` para enviar mensajes ADT^A03 (Discharge Patient)
2. Agrega logging a archivo en `hospital_server.py`
3. Implementa validación de IP en el servidor

### Nivel 2: Intermedio
4. Crea un sniffer usando Wireshark para capturar mensajes HL7
5. Implementa rate limiting (máximo 10 mensajes/minuto)
6. Agrega soporte para múltiples clientes simultáneos (threading)

### Nivel 3: Avanzado
7. Implementa MLLP+TLS con certificados autofirmados
8. Crea un proxy HL7 que log todos los mensajes (Man-in-the-Middle educativo)
9. Desarrolla un fuzzer que envíe mensajes malformados para testing

---

## 12. 📖 Referencia Rápida de Comandos

### Ejecutar el Ecosistema

```bash
# Terminal 1: Iniciar el servidor
python hospital_server.py

# Terminal 2: Enviar mensaje
python recepcionista.py

# Terminal 3: Monitorear tráfico (opcional)
sudo tcpdump -i lo port 6661 -X
```

### Debugging

```bash
# Ver qué está escuchando en el puerto 6661
sudo netstat -tlnp | grep 6661

# Probar conectividad
telnet localhost 6661

# Enviar mensaje HL7 manual
echo -e '\x0bMSH|^~\&|TEST|...\x1c\x0d' | nc localhost 6661
```

---

*Última actualización: Enero 2026*  
*Módulo 7: Protocolos de Integración - Motor HL7 MLLP desde Cero*