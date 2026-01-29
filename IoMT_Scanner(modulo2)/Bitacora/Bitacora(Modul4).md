# 🏥 Bitácora de Entrenamiento: Infraestructura PACS & Redes (Módulo 4)

## Objetivo
Desplegar un servidor de imágenes médicas (PACS) y programar la transmisión de estudios vía red (Protocolo DICOM C-STORE).

**Herramientas:** Docker, Orthanc, Python (`pynetdicom`), Browser

---

## 1. 🏗️ Infraestructura: El Servidor PACS (Orthanc)

### ¿Qué es un PACS?

**PACS** = *Picture Archiving and Communication System* (Sistema de Archivo y Comunicación de Imágenes)

Es el **almacén digital centralizado** donde se guardan y distribuyen todas las imágenes médicas de un hospital (Rayos X, resonancias, tomografías, etc.). Sin PACS:
- Cada equipo médico tendría sus propias imágenes sueltas
- Los doctores no podrían acceder a todos los estudios del paciente
- Habría confusión total en la gestión de datos

### ¿Por qué Docker en lugar de instalar directamente?

En lugar de instalar software pesado en Fedora (lo que podría romper herramientas del sistema), usamos **Virtualización basada en Contenedores**.

**Docker** es como una "máquina virtual ligera":
- Aisla completamente el software dentro de un contenedor
- Es portable (funciona igual en cualquier máquina)
- Se puede activar/desactivar en segundos
- No afecta al sistema operativo

### Imagen PACS: Orthanc

**Orthanc** es un servidor PACS Open Source (de código abierto) que es:
- Gratuito
- Fácil de desplegar
- Perfectamente funcional para hospitales pequeños

**Imagen Docker:** `jodogne/orthanc-plugins`

### Comando de Despliegue

```bash
sudo docker run -p 4242:4242 -p 8042:8042 --name mi-pacs -d jodogne/orthanc-plugins
```

**Desglose del comando:**

| Parámetro | Significado |
|-----------|-------------|
| `docker run` | Crear e iniciar un nuevo contenedor |
| `-p 4242:4242` | Mapear puerto 4242 del contenedor al puerto 4242 de tu laptop |
| `-p 8042:8042` | Mapear puerto 8042 del contenedor al puerto 8042 de tu laptop |
| `--name mi-pacs` | Darle un nombre legible al contenedor |
| `-d` | Ejecutar en modo *detached* (fondo, sin bloquear terminal) |
| `jodogne/orthanc-plugins` | La imagen Docker a descargar y ejecutar |

### Puertos Críticos

| Puerto | Protocolo | Función |
|--------|-----------|---------|
| **4242** | DICOM | El "oído digital" del servidor. Aquí hablan las máquinas entre sí usando DICOM |
| **8042** | HTTP/Browser | Interfaz web para que los doctores vean las imágenes en el navegador |

> **Analogía:** El puerto 4242 es como una línea telefónica dedicada que solo entienden máquinas médicas. El puerto 8042 es la recepción del hospital donde entra cualquier persona con un navegador.

---

## 2. 🔌 Protocolo de Red: El Lenguaje DICOM

Las máquinas médicas **NO** usan FTP, Email, o protocolos genéricos. Tienen su propio idioma: **DICOM**.

### Concepto: AE Title (Application Entity Title)

**¿Qué es?** Es el "nombre de usuario" de cada máquina en la red DICOM.

| Ejemplo | Quién Es |
|---------|----------|
| `RESONANCIA_PISO3` | La máquina de resonancia magnética del piso 3 |
| `ORTHANC` | Tu servidor PACS |
| `MI_SCRIPT` | Tu script Python enviando datos |

**Regla Crítica:** Si los AE Titles no coinciden en la configuración del hospital, **la conexión se rechaza**. Es como intentar entrar a una oficina con credencial de otra persona.

### Concepto: Association (El Apretón de Manos)

Antes de enviar datos, las máquinas "negocian":

```
Máquina A: "¡Hola! Soy MI_SCRIPT"
PACS:      "Hola, bienvenido. ¿Qué tipos de imágenes tienes?"
Máquina A: "Tengo imágenes CT (Tomografías)"
PACS:      "Perfecto, aceptaré tus imágenes CT"
[Se establece la conexión]
```

### Concepto: C-STORE (El Comando de Almacenamiento)

**C-STORE** es el comando específico DICOM que significa: **"Guardar esta imagen en mi servidor"**

Es uno de varios comandos DICOM:
- **C-STORE:** Enviar una imagen
- **C-FIND:** Buscar imágenes
- **C-RETRIEVE:** Descargar imágenes
- **C-MOVE:** Mover imágenes entre servidores

---

## 3. 🚑 Script C: La Ambulancia (`ambulancia.py`)

**Misión:** Simular una modalidad médica (ejemplo: Tomógrafo) enviando un estudio al servidor PACS.

### 🧠 Arquitectura del Código

#### Paso 1: Carga
Lee el archivo `.dcm` anonimizado que creaste en el Módulo 3.

```python
ds = pydicom.dcmread(ARCHIVO_A_ENVIAR)
```

#### Paso 2: Definir el Contexto
Le comunicas al servidor qué tipo de datos vas a enviar (CT, Radiografía, Resonancia, etc.).

```python
ae.add_requested_context(CTImageStorage)  # "Voy a enviar imágenes de Tomografía"
```

#### Paso 3: Asociación (Handshake)
Establece la conexión y negocia con el servidor PACS.

```python
assoc = ae.associate('127.0.0.1', 4242, ae_title='ORTHANC')
```

**Parámetros:**
- `'127.0.0.1'` = Localhost (tu propia máquina)
- `4242` = Puerto DICOM del PACS
- `ae_title='ORTHANC'` = Nombre de la máquina a conectar

#### Paso 4: Transmisión (C-STORE)
Envía el dataset (imagen + metadatos) al servidor.

```python
status = assoc.send_c_store(ds)
```

#### Paso 5: Verificación
Comprueba que el servidor aceptó la imagen.

```python
if status.Status == 0x0000:
    print("✅ Éxito")
else:
    print("❌ Error")
```

**Código de Estado 0x0000:** Significa "Aceptado correctamente" en DICOM.

---

## 4. 🌐 Mapa de tu Hospital Digital (Estado Actual)

Tienes un **ecosistema completo** corriendo en tu laptop:

```
┌─────────────────────────────────────────────┐
│ TU LAPTOP: Hospital Digital Simulado        │
├─────────────────────────────────────────────┤
│ CAPA FÍSICA: Hardware (CPU, RAM, Disco)     │
├─────────────────────────────────────────────┤
│ CAPA SO: Fedora Linux (Firewall activo)     │
├─────────────────────────────────────────────┤
│ CAPA VIRTUALIZACIÓN: Docker (Contenedor)    │
│ └─ Orthanc PACS (Puerto 4242 + 8042)       │
├─────────────────────────────────────────────┤
│ CAPA LÓGICA: Scripts Python                 │
│ ├─ radar.py (Escaneo de red)               │
│ ├─ vigilante.py (Detección de intrusos)    │
│ ├─ medico.py (Anonimización DICOM)         │
│ ├─ auditor.py (Control de calidad)         │
│ └─ ambulancia.py (Transmisión DICOM)       │
└─────────────────────────────────────────────┘
```

### Flujo de Datos Completo

1. **Obtención de Imagen:** Una máquina médica captura una radiografía
2. **Anonimización:** `medico.py` elimina datos personales
3. **Verificación:** `auditor.py` confirma que está segura
4. **Transmisión:** `ambulancia.py` envía la imagen vía DICOM
5. **Almacenamiento:** Orthanc PACS recibe y guarda la imagen
6. **Acceso:** Los doctores entran en la web (puerto 8042) y ven la imagen

---

*Última actualización: Enero 2026*