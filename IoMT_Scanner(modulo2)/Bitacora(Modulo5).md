# 📨 Bitácora de Entrenamiento: Interoperabilidad HL7 (Módulo 5)

## Objetivo
Comprender la estructura de mensajería hospitalaria (no-imagen) y generar eventos de admisión de pacientes mediante código.

**Herramientas:** Python (`hl7`), Estándar HL7 v2.x

---

## 1. 🧠 Fundamentos Teóricos: El Sistema Nervioso del Hospital

### ¿Qué es HL7?

**HL7** = *Health Level Seven* (Nivel 7 de Salud - capa de aplicación del modelo OSI)

Es el **estándar de mensajería** que permite la comunicación entre sistemas hospitalarios diferentes:

| Sistema Origen | → HL7 → | Sistema Destino |
|----------------|---------|-----------------|
| Admisión (HIS) | Mensaje ADT | Laboratorio (LIS) |
| Laboratorio (LIS) | Resultados ORU | Historia Clínica (EMR) |
| Farmacia | Orden OMP | Sistema de Facturación |
| Radiología (RIS) | Orden ORM | PACS |

### Diferencia: DICOM vs HL7

| Aspecto | DICOM | HL7 |
|---------|-------|-----|
| **Tipo de Datos** | Imágenes médicas (pesadas) | Texto administrativo/clínico (ligero) |
| **Velocidad** | Lenta (MB-GB) | Rápida (KB) |
| **Uso** | Radiología, Cardiología | Admisión, Lab, Farmacia, Facturación |
| **Analogía** | Envío de paquetes FedEx | Mensajes de texto SMS |

> **Mientras DICOM mueve imágenes pesadas, HL7 mueve texto crítico.**

---

## 2. 📐 Estructura del Mensaje HL7 v2.x

### El Sistema de Delimitadores

HL7 v2 usa **texto plano delimitado** (no XML, no JSON). Los separadores tienen jerarquía:

| Carácter | Nombre | Nivel | Ejemplo |
|----------|--------|-------|---------|
| `\|` | Pipe (Tubería) | **Campos** | `MSH\|^~\\&\|SISTEMA\|LUGAR` |
| `^` | Caret (Gorro) | **Componentes** | `LEDESMA^EMANUEL^ANTONIO` |
| `~` | Tilde | **Repeticiones** | `555-1234~555-5678` |
| `\` | Backslash | **Caracteres de escape** | `\T\` (tab), `\R\` (return) |
| `&` | Ampersand | **Subcomponentes** | Usado en codificación compleja |

### Anatomía de un Mensaje

```
MSH|^~\&|EMISOR|LUGAR_ORIGEN|RECEPTOR|LUGAR_DESTINO|20260127120000||ADT^A01|MSG123|P|2.3
PID|||123456||LEDESMA^EMANUEL||19991108|M
PV1||I|URGENCIAS^304^1||||001^DR. HOUSE
```

**Desglose:**
- **Línea 1:** Segmento MSH (Header)
- **Línea 2:** Segmento PID (Datos del Paciente)
- **Línea 3:** Segmento PV1 (Datos de la Visita)

---

## 3. 📋 Segmentos HL7 Comunes

### Tabla de Segmentos Críticos

| Segmento | Nombre Completo | Contenido |
|----------|-----------------|-----------|
| **MSH** | Message Header | Quién envía, a quién, cuándo, tipo de mensaje |
| **PID** | Patient Identification | Nombre, ID, fecha de nacimiento, sexo, dirección |
| **PV1** | Patient Visit | Ubicación, tipo de admisión, doctor asignado |
| **OBR** | Observation Request | Orden de laboratorio/estudio |
| **OBX** | Observation Result | Resultados de laboratorio |
| **AL1** | Allergy Information | Alergias del paciente |
| **DG1** | Diagnosis | Diagnósticos |

### Ejemplo: Segmento PID (Campo por Campo)

```
PID|||123456||LEDESMA^EMANUEL||19991108|M
```

| Posición | Campo | Valor | Significado |
|----------|-------|-------|-------------|
| PID-1 | Set ID | *(vacío)* | Número de secuencia |
| PID-2 | Patient ID (External) | *(vacío)* | ID externo (legacy) |
| PID-3 | Patient ID (Internal) | `123456` | ID único del hospital |
| PID-4 | Alternate Patient ID | *(vacío)* | ID alternativo |
| PID-5 | Patient Name | `LEDESMA^EMANUEL` | Apellido^Nombre |
| PID-6 | Mother's Maiden Name | *(vacío)* | Apellido materno |
| PID-7 | Date of Birth | `19991108` | 1999-11-08 (YYYYMMDD) |
| PID-8 | Sex | `M` | M=Masculino, F=Femenino |

---

## 4. 🚨 Eventos ADT (Admission, Discharge, Transfer)

### Tabla de Eventos Comunes

| Código | Evento | Descripción |
|--------|--------|-------------|
| **ADT^A01** | Admit Patient | Paciente ingresado al hospital |
| **ADT^A02** | Transfer Patient | Paciente trasladado de habitación/piso |
| **ADT^A03** | Discharge Patient | Paciente dado de alta |
| **ADT^A04** | Register Patient | Pre-registro (antes de admisión) |
| **ADT^A08** | Update Patient Info | Actualización de datos demográficos |
| **ADT^A11** | Cancel Admit | Cancelar admisión |

**Formato:** `ADT^A01`
- **ADT:** Categoría (Admission/Discharge/Transfer)
- **^:** Separador de componentes
- **A01:** Código específico del evento

---

## 5. 🏥 Script: El Recepcionista (`recepcionista.py`)

**Misión:** Simular un HIS (Hospital Information System) enviando una orden de ingreso.

### 🧠 Arquitectura del Código

#### Paso 1: Construcción del Mensaje (String Manipulation)

HL7 v2 es **manipulación de cadenas pura**. Concatenamos variables separadas por pipes (`|`):

```python
msh = f"MSH|^~\\&|SISTEMA_PY|FEDORA|HIS_CENTRAL|BERLIN|{timestamp}||ADT^A01|MSG-{timestamp}|P|2.3"
pid = f"PID|||{id_paciente}||{apellido}^{nombre}||{fecha_nacimiento}|{sexo}"
pv1 = "PV1||I|URGENCIAS^304^1||||001^DR. HOUSE"
```

#### Paso 2: Unir Segmentos con `\r`

El separador de segmentos en HL7 es **Carriage Return** (`\r`):

```python
mensaje_raw = f"{msh}\r{pid}\r{pv1}"
```

**Resultado (lo que viaja por la red):**
```
MSH|^~\&|SISTEMA_PY|FEDORA|...\rPID|||123456|...\rPV1||I|...
```

#### Paso 3: Parsing - Convertir String en Matriz

Aquí ocurre la **magia del parsing**:

```python
h = hl7.parse(mensaje_raw)
```

**¿Qué hace `hl7.parse()`?**

1. **Divide por `\r`** → Obtiene lista de segmentos:
   ```python
   [
     "MSH|^~\&|SISTEMA_PY|FEDORA|...",
     "PID|||123456||LEDESMA^EMANUEL|...",
     "PV1||I|URGENCIAS^304^1|..."
   ]
   ```

2. **Divide cada segmento por `|`** → Obtiene lista de campos:
   ```python
   h[0] = ["MSH", "^~\&", "SISTEMA_PY", "FEDORA", ...]
   h[1] = ["PID", "", "", "123456", "", "LEDESMA^EMANUEL", ...]
   h[2] = ["PV1", "", "I", "URGENCIAS^304^1", ...]
   ```

3. **Resultado:** Una **matriz bidimensional** `h[segmento][campo]`

### 🔍 Entendiendo la Matriz de Acceso

```python
print(f" -> Tipo de Evento:    {h[0][9]}")   # MSH-9 (ADT^A01)
print(f" -> ID Mensaje:        {h[0][10]}")  # MSH-10
print(f" -> Nombre Paciente:   {h[1][5]}")   # PID-5 (Nombre completo)
print(f" -> Ubicación:         {h[2][3]}")   # PV1-3 (Urgencias)
```

**Desglose de `h[0][9]`:**

| Parte | Significado | Valor |
|-------|-------------|-------|
| `h` | El mensaje parseado (objeto HL7) | Toda la estructura |
| `[0]` | **Índice del segmento** (0=primer segmento) | Segmento MSH |
| `[9]` | **Índice del campo** (9=noveno campo) | Campo MSH-9 (Message Type) |
| **Resultado** | Contenido del campo | `ADT^A01` |

**Visualización de la Matriz:**

```
mensaje_raw = "MSH|^~\&|SYS|LUGAR|...|ADT^A01|MSG123|...\rPID|||123456||LEDESMA^EMANUEL|..."

↓ hl7.parse() ↓

h = [
  [0] → ["MSH", "^~\&", "SYS", "LUGAR", ... , "ADT^A01", "MSG123", ...],
        ↑                                    ↑           ↑
        h[0][0]                             h[0][9]     h[0][10]
  
  [1] → ["PID", "", "", "123456", "", "LEDESMA^EMANUEL", ...],
        ↑                               ↑
        h[1][0]                        h[1][5]
  
  [2] → ["PV1", "", "I", "URGENCIAS^304^1", ...],
        ↑                ↑
        h[2][0]         h[2][3]
]
```

**¿Por qué índice 0, 1, 2?**
- Python usa **indexación base-0** (empieza en 0)
- `h[0]` = Primer segmento (MSH)
- `h[1]` = Segundo segmento (PID)
- `h[2]` = Tercer segmento (PV1)

**¿Por qué campo 9, 10, 5?**
- Los campos también empiezan en 0
- `h[0][9]` = MSH campo 9 (en documentación HL7 se llama MSH-9)
- `h[1][5]` = PID campo 5 (PID-5 = Patient Name)

### 📊 Tabla de Correspondencia: Código → Estándar HL7

| Código Python | Nombre Estándar HL7 | Contenido |
|---------------|---------------------|-----------|
| `h[0][9]` | MSH-9 | Message Type (ADT^A01) |
| `h[0][10]` | MSH-10 | Message Control ID (MSG123) |
| `h[1][5]` | PID-5 | Patient Name (LEDESMA^EMANUEL) |
| `h[2][3]` | PV1-3 | Assigned Patient Location (URGENCIAS^304^1) |

---

## 6. 💡 Ventajas del Parsing

### Sin Parsing (Manual):
```python
# Contar pipes manualmente = Pesadilla
campos = mensaje_raw.split('|')
nombre = campos[5]  # ¿Cuál era el 5? 🤔
```

### Con Parsing (Librería `hl7`):
```python
# Acceso directo y legible
nombre = h[1][5]  # PID-5 (Documentado en estándar)
```

**Beneficios:**
- ✅ Código más legible
- ✅ Menos errores de conteo
- ✅ Manejo automático de delimitadores
- ✅ Validación de estructura

---

## 7. 🔄 Flujo Completo del Sistema

```
[1] RECEPCIONISTA INGRESA DATOS
    ↓
[2] SISTEMA GENERA MENSAJE HL7 (String)
    MSH|^~\&|...\rPID|...\rPV1|...
    ↓
[3] TRANSMISIÓN POR RED (TCP/IP)
    ↓
[4] SERVIDOR RECIBE Y PARSEA
    String → Matriz h[segmento][campo]
    ↓
[5] SISTEMA EXTRAE DATOS
    h[1][5] = Nombre del paciente
    ↓
[6] ACTUALIZA BASE DE DATOS
    INSERT INTO pacientes...
```

---

*Última actualización: Enero 2026*