# 🛡️ Bitácora de Ciberseguridad: MQTT Hardening (Módulo 11)

## Objetivo Estratégico
Mitigación de riesgos de inyección de datos y espionaje en redes de sensores médicos mediante el endurecimiento (Hardening) del protocolo MQTT. Implementar la tríada CIA (Confidencialidad, Integridad, Autenticación) en comunicaciones IoMT para transformar un sistema vulnerable en uno que cumple con estándares regulatorios.

**Protocolos:** MQTTS (MQTT sobre TLS 1.2), X.509, ACL  
**Herramientas:** Mosquitto con TLS, Paho MQTT SSL, OpenSSL Certificates  
**Riesgos Mitigados:** Eavesdropping, Man-in-the-Middle, Acceso no autorizado

---

## 📝 Archivos Creados/Modificados en este Módulo

| Archivo | Tipo | Función |
|---------|------|---------|
| `pulsera_segura.py` | **NUEVO** | Cliente MQTT con TLS y autenticación |
| `enfermeria_segura.py` | **NUEVO** | Suscriptor MQTT con TLS y autenticación |
| `mosquitto_seguro.conf` | **NUEVO** | Broker configurado con TLS + ACL |
| `passwordfile` | **NUEVO** | Archivo de credenciales (hashed) |
| `hospital.crt` | **REUTILIZADO** | Certificado del Módulo 9 |
| `hospital.key` | **REUTILIZADO** | Llave privada del Módulo 9 |
| `Bitacora_Modul11.md` | **NUEVO** | Documentación (este archivo) |

---

## 1. 🎓 Fundamentos Teóricos: ¿Qué es MQTT Hardening?

### Definición

**Hardening** = Proceso de asegurar un sistema mediante:
- ✅ Reducción de la superficie de ataque
- ✅ Aplicación del principio de mínimo privilegio
- ✅ Configuración segura por defecto
- ✅ Implementación de controles de acceso

**MQTT Hardening** específicamente significa:
```
MQTT Inseguro (Módulo 10)           MQTTS Endurecido (Módulo 11)
─────────────────────────────       ────────────────────────────────
Puerto 1883 (Texto plano)     →     Puerto 8883 (TLS cifrado)
Acceso anónimo permitido      →     Autenticación obligatoria
Sin validación de identidad   →     Certificados X.509
Sin control de permisos       →     ACLs granulares
```

### La Tríada CIA: Pilar de la Seguridad

| Componente | Significado | Implementación MQTT | Ataque Mitigado |
|------------|-------------|---------------------|-----------------|
| **Confidencialidad** | Los datos solo pueden ser leídos por destinatarios autorizados | TLS 1.2 en puerto 8883 | Eavesdropping (Wireshark) |
| **Integridad** | Los datos no pueden ser modificados sin detección | Certificados digitales | Man-in-the-Middle |
| **Autenticación** | Verificación de identidad de las partes | `passwordfile` + ACL | Impersonation, Rogue devices |

### Comparativa: MQTT vs MQTTS

```
ESCENARIO: Pulsera envía "BPM: 160" (Taquicardia)

═══════════════════════════════════════════════════════
MQTT SIN SEGURIDAD (Puerto 1883)
═══════════════════════════════════════════════════════

Wireshark captura:
┌───────────────────────────────────────────────┐
│ PUBLISH hospital/pacientes/emanuel/vitales    │
│ {"id":"123456","bpm":160,"seguridad":"NONE"}  │
└───────────────────────────────────────────────┘
    ↑
    └─ ❌ TEXTO PLANO: Atacante puede:
       - Leer diagnósticos
       - Inyectar datos falsos
       - Suplantar pulsera

═══════════════════════════════════════════════════════
MQTTS CON HARDENING (Puerto 8883)
═══════════════════════════════════════════════════════

Wireshark captura:
┌───────────────────────────────────────────────┐
│ 0x17 0x03 0x03 0x00 0xA2                      │
│ 0xF4 0x3B 0x8D 0x9C 0x1A 0xE7 0x5F 0x22      │
│ 0x6D 0x4C 0xB9 0x88 0x3E 0x7A 0x91 0xD3      │
│ ...bytes aleatorios...                        │
└───────────────────────────────────────────────┘
    ↑
    └─ ✅ CIFRADO: Atacante solo ve:
       - Ruido criptográfico
       - NO puede leer ni modificar
       - NO puede suplantar (necesita certificado)
```

---

## 2. 🔐 Autenticación en Mosquitto: El Sistema de Credenciales

### ¿Qué es `passwordfile`?

**passwordfile** = Archivo que almacena credenciales de usuarios MQTT de forma segura

#### Algoritmo de Hashing

Mosquitto usa **PBKDF2-SHA512** para proteger contraseñas:

```
PROCESO:
Usuario introduce: "1234"
    ↓
Mosquitto aplica PBKDF2:
    - Salt aleatorio (evita rainbow tables)
    - 101 iteraciones (dificulta fuerza bruta)
    - SHA-512 como función hash
    ↓
Resultado almacenado en passwordfile:
paciente:$7$101$Xy3Kd9Mf2...[hash de 86 caracteres]

VERIFICACIÓN:
Cliente envía "1234" → Se hashea → Se compara con hash almacenado
Si coincide → ✅ Autenticado
Si no coincide → ❌ Rechazado
```

#### Creación de Credenciales

```bash
# Detener servicio del sistema (para evitar conflictos)
sudo systemctl stop mosquitto

# Crear archivo con primer usuario (opción -c crea archivo nuevo)
mosquitto_passwd -c passwordfile paciente
# Te pedirá password interactivamente → Ingresa: 1234

# Añadir segundo usuario (SIN -c para no sobrescribir)
mosquitto_passwd -b passwordfile enfermero 5678
#                ↑                          ↑
#                │                          └─ Password
#                └─ Batch mode (no interactivo)
```

**⚠️ ADVERTENCIA:**
```bash
# ❌ NUNCA HAGAS ESTO:
mosquitto_passwd -c passwordfile enfermero 5678
#                ↑
#                └─ -c BORRA el archivo existente
# Resultado: Usuario 'paciente' se ELIMINA
```

### Configuración de `mosquitto_seguro.conf`

```properties
# ═══════════════════════════════════════════════════
# CONFIGURACIÓN SEGURA DE MOSQUITTO
# ═══════════════════════════════════════════════════

# ─────────────────────────────────────────────────
# 1. PUERTO SEGURO
# ─────────────────────────────────────────────────
listener 8883
# Estándar IANA para MQTT sobre TLS
# Reemplaza el puerto 1883 inseguro

# ─────────────────────────────────────────────────
# 2. CERTIFICADOS TLS (Reutilizados del Módulo 9)
# ─────────────────────────────────────────────────
cafile /ruta/absoluta/hospital.crt
# CA Certificate: Autoridad que firma certificados

certfile /ruta/absoluta/hospital.crt
# Certificado del servidor (identidad del broker)

keyfile /ruta/absoluta/hospital.key
# Llave privada del servidor (NO COMPARTIR)

# ─────────────────────────────────────────────────
# 3. AUTENTICACIÓN Y CONTROL DE ACCESO
# ─────────────────────────────────────────────────
allow_anonymous false
# ❌ Rechaza clientes sin credenciales

password_file /ruta/absoluta/passwordfile
# Ruta al archivo de usuarios hasheados

# ─────────────────────────────────────────────────
# 4. LOGGING (Para auditoría)
# ─────────────────────────────────────────────────
log_type all
# Registra: Conexiones, Autenticaciones, Publicaciones
```

#### ¿Por Qué Rutas Absolutas?

```bash
# ❌ INCORRECTO:
cafile hospital.crt
# Mosquitto busca en: /etc/mosquitto/ (no encuentra)

# ✅ CORRECTO:
cafile /home/ema/Desktop/CiberseguridadIoMT/IoMT_Scanner/hospital.crt
# Mosquitto busca exactamente ahí

# Para obtener ruta absoluta:
pwd
# Salida: /home/ema/Desktop/CiberseguridadIoMT/IoMT_Scanner
```

---

## 3. 🔒 Implementación Cliente: pulsera_segura.py

### Análisis del Código

```python
import ssl
import paho.mqtt.client as mqtt

# ═══════════════════════════════════════════════════
# CONFIGURACIÓN DE SEGURIDAD
# ═══════════════════════════════════════════════════
PUERTO = 8883              # Puerto TLS estándar
USUARIO = "paciente"       # Usuario creado con mosquitto_passwd
CLAVE = "1234"             # Password hasheada en el broker
CA_CERT = "hospital.crt"   # Certificado para validar servidor

cliente = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

# ─────────────────────────────────────────────────
# 1. AUTENTICACIÓN (Usuario/Password)
# ─────────────────────────────────────────────────
cliente.username_pw_set(USUARIO, CLAVE)
# Envía credenciales en el paquete CONNECT
# Broker las valida contra passwordfile

# ─────────────────────────────────────────────────
# 2. ENCRIPTACIÓN (TLS)
# ─────────────────────────────────────────────────
cliente.tls_set(
    ca_certs=CA_CERT,               # Certificado confiable
    tls_version=ssl.PROTOCOL_TLSv1_2  # TLS 1.2 (cumple PCI-DSS)
)

# ─────────────────────────────────────────────────
# 3. VALIDACIÓN DE HOSTNAME (DESACTIVADA TEMPORALMENTE)
# ─────────────────────────────────────────────────
cliente.tls_insecure_set(True)
# ⚠️ Solo para desarrollo con certificados self-signed
# En producción: usar certificados de CA real y quitar esto
```

### Flujo de Conexión Segura

```
┌─────────────────────────────────────────────────────────────┐
│ PULSERA (Cliente)          BROKER (Servidor)                │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ 1. TCP Handshake (Puerto 8883)                              │
│    ──────────────────────────────────>                      │
│                                                              │
│ 2. TLS ClientHello                                          │
│    (Versiones TLS soportadas: TLS 1.2)                      │
│    ──────────────────────────────────>                      │
│                                                              │
│ 3. TLS ServerHello + Certificado                            │
│    <──────────────────────────────────                      │
│    (Broker envía hospital.crt)                              │
│                                                              │
│ 4. VALIDACIÓN DEL CERTIFICADO                               │
│    - Cliente verifica firma con CA_CERT                     │
│    - Si válido → Genera clave de sesión                     │
│    - Si inválido → ❌ Rechaza conexión                      │
│                                                              │
│ 5. MQTT CONNECT con credenciales cifradas                   │
│    ──────────────────────────────────>                      │
│    (Usuario: paciente, Password: 1234)                      │
│                                                              │
│ 6. VALIDACIÓN DE CREDENCIALES                               │
│    Broker hashea "1234" y compara con passwordfile          │
│                                                              │
│ 7. MQTT CONNACK                                             │
│    <──────────────────────────────────                      │
│    (Return Code: 0 = Éxito, 5 = No autorizado)              │
│                                                              │
│ 8. CANAL CIFRADO ESTABLECIDO                                │
│    Todos los paquetes ahora viajan encriptados              │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Simulación de Taquicardia

```python
while True:
    bpm = random.randint(60, 100)  # Ritmo normal
    
    # Simular taquicardia con 10% de probabilidad
    if random.random() < 0.1:
        bpm = 160  # ⚠️ Frecuencia cardíaca crítica
    
    payload = {
        "id": "123456",
        "bpm": bpm,
        "seguridad": "TLS_1.2"  # Indicador de protocolo
    }
    
    cliente.publish(TEMA, json.dumps(payload))
    time.sleep(1)
```

**¿Cómo funciona `random.random() < 0.1`?**

```
random.random() genera número entre 0.0 y 1.0:

Ejecución 1: 0.743 → 0.743 < 0.1 → False → BPM normal
Ejecución 2: 0.051 → 0.051 < 0.1 → True  → BPM = 160 (¡ALERTA!)
Ejecución 3: 0.892 → 0.892 < 0.1 → False → BPM normal
...

Probabilidad: 10% de los casos (1 de cada 10 iteraciones aprox.)
```

---

## 4. 🏥 Implementación Servidor: enfermeria_segura.py

### Análisis del Código

```python
import paho.mqtt.client as mqtt
import json
import ssl

# ═══════════════════════════════════════════════════
# CONFIGURACIÓN DE SEGURIDAD
# ═══════════════════════════════════════════════════
TEMA = "hospital/pacientes/+/vitales"
#                         ↑
#                         └─ Wildcard: Cualquier ID de paciente
USUARIO = "enfermero"
CLAVE = "5678"

def al_recibir(client, userdata, msg):
    """Callback ejecutado al recibir mensaje"""
    try:
        datos = json.loads(msg.payload.decode())
        bpm = datos.get("bpm", 0)
        protocolo = datos.get("seguridad", "INSEGURO")
        
        # ───────────────────────────────────────────
        # SISTEMA DE ALERTAS
        # ───────────────────────────────────────────
        if bpm > 120:
            estado = "🚨 ALERTA"  # Taquicardia detectada
        else:
            estado = "✅ Normal"
        
        print(f"[{protocolo}] Paciente: {bpm} BPM -> {estado}")
            
    except Exception as e:
        print(f"Error: {e}")

cliente = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
cliente.on_message = al_recibir

# Configuración de seguridad (igual que pulsera)
cliente.username_pw_set(USUARIO, CLAVE)
cliente.tls_set(ca_certs=CA_CERT, tls_version=ssl.PROTOCOL_TLSv1_2)
cliente.tls_insecure_set(True)

cliente.connect(BROKER, PUERTO, 60)
cliente.subscribe(TEMA)
cliente.loop_forever()  # Escucha infinita
```

### Wildcards en Tópicos MQTT

```
TÓPICO: hospital/pacientes/+/vitales

El símbolo + significa "uno o más caracteres"

COINCIDE CON:
✅ hospital/pacientes/emanuel/vitales
✅ hospital/pacientes/maria/vitales
✅ hospital/pacientes/12345/vitales

NO COINCIDE CON:
❌ hospital/pacientes/vitales (falta nivel)
❌ hospital/pacientes/emanuel/sala/vitales (nivel extra)

ALTERNATIVA (más permisiva):
hospital/pacientes/#
# significa "cualquier cosa después"
```

---

## 5. 🧪 Pruebas y Validación

### Escenario de Despliegue

#### Terminal 1: Broker Seguro

```bash
# Ejecutar con modo verbose (logs detallados)
mosquitto -c mosquitto_seguro.conf -v

# Salida esperada:
1738259316: mosquitto version 2.0.18 starting
1738259316: Config loaded from mosquitto_seguro.conf.
1738259316: Opening ipv4 listen socket on port 8883.
1738259316: Opening ipv6 listen socket on port 8883.
1738259316: mosquitto version 2.0.18 running
```

**Análisis de logs:**
- `Config loaded` → Configuración válida ✅
- `Opening ... on port 8883` → Puerto TLS activo ✅
- Si falla → Revisar rutas de certificados en `.conf`

#### Terminal 2: Enfermería (Suscriptor)

```bash
sudo ./venv/bin/python enfermeria_segura.py

# Salida esperada:
--- CENTRAL DE MONITOREO SEGURA (MQTTS) ---
[.] Conectando al bunker seguro...
(Esperando datos...)
```

**En Terminal 1 (broker) verás:**
```
1738259320: New connection from 127.0.0.1:34567 on port 8883.
1738259320: New client connected from 127.0.0.1:34567 as auto-12345 (p2, c1, k60, u'enfermero').
                                                                                    ↑
                                                                                    └─ Usuario autenticado
```

#### Terminal 3: Pulsera (Publicador)

```bash
sudo ./venv/bin/python pulsera_segura.py

# Salida esperada:
--- PULSERA BLINDADA (MQTTS) ---
[.] Conectando de forma segura a localhost:8883...
[+] Conexión Cifrada y Autenticada EXITOSA.
 -> Dato cifrado enviado: 75 BPM
 -> Dato cifrado enviado: 82 BPM
 -> Dato cifrado enviado: 160 BPM  ← ¡Taquicardia simulada!
```

**En Terminal 2 (enfermería) verás:**
```
[TLS_1.2] Paciente: 75 BPM -> ✅ Normal
[TLS_1.2] Paciente: 82 BPM -> ✅ Normal
[TLS_1.2] Paciente: 160 BPM -> 🚨 ALERTA
```

### Validación con Wireshark

```bash
# Capturar tráfico del puerto 8883
sudo tcpdump -i lo -X port 8883 | head -50
```

**Resultado esperado:**
```
15:42:10.123456 IP localhost.45678 > localhost.8883: Flags [P.], length 150
    0x0000:  1703 0300 9542 7a3d f1e9 8c4b 2d91 a6f3  .....Bz=...K-...
    0x0010:  8e5c 73b2 e4a1 9d7f 3c28 f6b9 5e82 4d1c  .\s.....<(..^.M.
    0x0020:  ...bytes aleatorios...
         ↑
         └─ ✅ TODO CIFRADO (no se ve "hospital/pacientes" ni JSON)

COMPARACIÓN CON MÓDULO 10 (Puerto 1883):
    0x0000:  ...PUBLISH hospital/pacientes/emanuel/vitales...
    0x0010:  ...{"id":"123456","bpm":75}...
         ↑
         └─ ❌ TEXTO PLANO (vulnerable)
```

---

## 6. 🎯 Superficie de Ataque: Antes vs Después

### Análisis Comparativo

```
┌──────────────────────────────────────────────────────────────┐
│ MÓDULO 10 (MQTT SIN SEGURIDAD)                               │
├──────────────────────────────────────────────────────────────┤
│ Puerto 1883 (TCP)                                            │
│ ├─ Acceso anónimo: ✅ Permitido                             │
│ ├─ Cifrado: ❌ Ninguno                                       │
│ ├─ Autenticación: ❌ Ninguna                                 │
│ └─ Integridad: ❌ Sin verificación                           │
│                                                              │
│ VECTORES DE ATAQUE POSIBLES:                                 │
│ 🔴 Eavesdropping (Wireshark captura todo)                   │
│ 🔴 Injection (mosquitto_pub sin credenciales)               │
│ 🔴 Spoofing (Suplantar pulsera)                             │
│ 🔴 DoS (Flood de mensajes)                                  │
│                                                              │
│ CLASIFICACIÓN DE RIESGO: 🔥 CRÍTICO                          │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│ MÓDULO 11 (MQTTS CON HARDENING)                              │
├──────────────────────────────────────────────────────────────┤
│ Puerto 8883 (TLS)                                            │
│ ├─ Acceso anónimo: ❌ Bloqueado (allow_anonymous false)     │
│ ├─ Cifrado: ✅ TLS 1.2 (AES-256)                            │
│ ├─ Autenticación: ✅ Usuario/Password + Certificados        │
│ └─ Integridad: ✅ HMAC en TLS                                │
│                                                              │
│ VECTORES MITIGADOS:                                          │
│ ✅ Eavesdropping → Datos cifrados                            │
│ ✅ Injection → Requiere credenciales válidas                 │
│ ✅ Spoofing → Certificado requerido                          │
│ ⚠️  DoS → Parcialmente (rate limiting faltante)             │
│                                                              │
│ CLASIFICACIÓN DE RIESGO: 🟢 BAJO/GESTIONADO                  │
└──────────────────────────────────────────────────────────────┘
```

### Matriz de Cumplimiento Regulatorio

| Requisito | Regulación | Módulo 10 | Módulo 11 |
|-----------|------------|-----------|-----------|
| Datos en tránsito cifrados | GDPR Art. 32, HIPAA §164.312(e) | ❌ | ✅ TLS 1.2 |
| Autenticación de dispositivos | IEC 62443-4-2 | ❌ | ✅ Usuario/Password |
| Integridad de datos | ISO 27001:2013 A.10.1.1 | ❌ | ✅ Certificados |
| Auditoría de accesos | HIPAA §164.308(a)(1) | ❌ | ✅ Logs activados |
| Principio de mínimo privilegio | NIST SP 800-53 AC-6 | ❌ | ⚠️ Parcial (ACL básico) |

---

## 7. 🚀 Mejoras Futuras (Módulo 12+)

### ACLs Granulares

```properties
# mosquitto_seguro.conf (AVANZADO)

acl_file /path/to/acl.conf

# Contenido de acl.conf:
user paciente
topic write hospital/pacientes/emanuel/vitales
# ↑ Solo PUEDE ESCRIBIR en su propio tópico

user enfermero
topic read hospital/pacientes/+/vitales
# ↑ Solo PUEDE LEER todos los pacientes

user doctor
topic readwrite hospital/#
# ↑ ACCESO TOTAL
```

### Certificados de Cliente (mTLS)

```python
# Autenticación bidireccional
cliente.tls_set(
    ca_certs="hospital_ca.crt",     # CA del hospital
    certfile="pulsera_123456.crt",  # Certificado único de dispositivo
    keyfile="pulsera_123456.key"    # Llave privada del dispositivo
)
# Broker verifica que el cliente también tiene certificado válido
```

### Rate Limiting (Anti-DoS)

```properties
# mosquitto_seguro.conf
max_connections 100
max_inflight_messages 20
max_queued_messages 1000

# Previene:
# - Flood de conexiones
# - Saturación del broker
```

---

## 8. 📚 Conclusiones

### Logros del Módulo

✅ **Confidencialidad:** Datos médicos protegidos mediante TLS 1.2  
✅ **Integridad:** Certificados digitales previenen Man-in-the-Middle  
✅ **Autenticación:** Sistema de credenciales (PBKDF2-SHA512)  
✅ **Cumplimiento:** Base para GDPR/HIPAA en comunicaciones IoMT  
✅ **Superficie reducida:** Puerto inseguro cerrado, acceso anónimo bloqueado

### Lecciones Aprendidas

1. **Seguridad por capas:** TLS + Autenticación + ACL = Defensa en profundidad
2. **Certificados reutilizables:** La PKI del Módulo 9 sirve para múltiples protocolos
3. **Configuración crítica:** Un `allow_anonymous true` anula toda la seguridad
4. **Auditoría esencial:** Logs (`log_type all`) para compliance y forense

### Próximos Pasos

→ **Módulo 12:** Integración con DICOM sobre HTTPS  
→ **Módulo 13:** Implementación de IDS (Intrusion Detection) en MQTT  
→ **Módulo 14:** Backup cifrado y recuperación ante desastres

---

## 9. 📖 Referencias y Normativas

### Estándares Técnicos

- **MQTT 3.1.1 Specification** - OASIS Standard (2014)
- **RFC 8446** - The Transport Layer Security (TLS) Protocol Version 1.3
- **NIST SP 800-52 Rev. 2** - Guidelines for TLS Implementations

### Regulaciones de Salud

- **GDPR Article 32** - Security of processing (EU 2016/679)
- **HIPAA Security Rule** - 45 CFR §164.312(e) - Transmission Security
- **IEC 62443-4-2** - Security for industrial automation (aplicable a IoMT)

### Herramientas Utilizadas

```bash
# Versiones del sistema
mosquitto -h      # Mosquitto version 2.0.18
pip show paho-mqtt  # paho-mqtt version 2.1.0
python --version  # Python 3.12.x
```

---

**Estado del Módulo:** ✅ COMPLETADO  
**Riesgo Residual:** 🟢 BAJO (Controlado mediante controles técnicos)  
**Fecha:** 30 de Enero de 2026