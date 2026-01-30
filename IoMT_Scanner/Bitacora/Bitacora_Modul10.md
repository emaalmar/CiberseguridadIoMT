# 📡 Bitácora de Ciberseguridad: IoMT & Telemetría (Módulo 10)

## Objetivo Estratégico
Implementación y análisis de riesgos del protocolo MQTT en un entorno de monitoreo de pacientes en tiempo real (Wearables médicos). Comprender la arquitectura pub/sub, identificar vulnerabilidades inherentes y proponer mitigaciones para cumplir GDPR/HIPAA en sistemas IoMT.

**Protocolos:** MQTT 3.1.1, JSON, TCP/IP  
**Herramientas:** Paho MQTT, Mosquitto Broker, Wireshark  
**Riesgos:** Autenticación débil, confidencialidad nula, DoS

---

## 📝 Archivos Creados/Modificados en este Módulo

| Archivo | Tipo | Función |
|---------|------|---------|
| `pulsera.py` | **NUEVO** | Publicador MQTT (Wearable simulado) |
| `enfermeria.py` | **NUEVO** | Suscriptor MQTT (Central de monitoreo) |
| `mosquitto.conf` | **NUEVO** | Configuración del broker (sin seguridad) |
| `mosquitto_secure.conf` | **NUEVO** | Configuración del broker (con TLS) |
| `Bitacora(Modul10).md` | **NUEVO** | Documentación (este archivo) |

---

## 1. 🎓 Fundamentos Teóricos: ¿Qué es MQTT?

### Definición

**MQTT** = *Message Queuing Telemetry Transport* (Transporte de Telemetría con Colas de Mensajes)

Es un **protocolo de comunicación ligero** diseñado para:
- ✅ **Dispositivos con recursos limitados** (IoT, wearables)
- ✅ **Redes con ancho de banda limitado** (3G, satelital)
- ✅ **Dispositivos a batería** (overhead mínimo)
- ✅ **Mensajería pub/sub desacoplada** (no necesita conexión directa)

### Historia y Evolución

| Año | Versión | Nota |
|-----|---------|------|
| 2010 | MQTT 3.1 | Creado por Andy Stanford-Clark (IBM) |
| 2014 | MQTT 3.1.1 | Estándar OASIS (nosotros usamos esta) |
| 2019 | MQTT 5.0 | Mejoras de seguridad y confiabilidad |
| 2023 | MQTT 5.0.1 | Último estándar |

### Comparativa: MQTT vs Alternativas

| Protocolo | Peso | Latencia | Uso | Complejidad |
|-----------|------|----------|-----|-------------|
| **MQTT** | 2 bytes header | <100ms | IoT, Wearables | ⭐ Bajo |
| **HTTP/REST** | 50+ bytes header | 500ms+ | Web, APIs | ⭐⭐ Medio |
| **AMQP** | 8 bytes header | 50ms | Enterprise | ⭐⭐⭐ Alto |
| **CoAP** | 4 bytes header | <100ms | Embedded | ⭐ Bajo |

**¿Por qué MQTT en medicina?**
```
Hospital con 1,000 pulseras biométricas
Cada 1 segundo → 1,000 mensajes/segundo

HTTP/REST:
- 50 bytes overhead × 1,000 = 50 KB/segundo
- Latencia: 500ms (peligroso para alertas críticas)

MQTT:
- 2 bytes overhead × 1,000 = 2 KB/segundo
- Latencia: <100ms (ideal para alertas)
```

---

## 2. 🔄 Modelo Pub/Sub (Publisher-Subscriber)

### Concepto Fundamental

**Pub/Sub** = Desacoplamiento total entre productor y consumidor

```
MODELO TRADICIONAL (TCP Socket):
Cliente A ←→ Servidor ←→ Cliente B
(Conexión directa)

MODELO PUB/SUB (MQTT):
Publicador → Broker ← Suscriptor
            (Intermediario)

Ventajas del Broker:
✅ Publicador NO necesita conocer suscriptores
✅ Suscriptor NO necesita conocer publicador
✅ Escalabilidad horizontal
✅ Desconexiones no interrumpen el flujo
```

### Ejemplo Médico

```
ESCENARIO: 3 pulseras, 5 enfermeras, 2 doctores

SIN MQTT (Pesadilla):
Pulsera 1 → Enfermera 1 (conexión TCP)
Pulsera 1 → Enfermera 2 (segunda conexión TCP)
Pulsera 1 → Enfermera 3 (tercera conexión TCP)
Pulsera 1 → Doctor 1 (cuarta conexión TCP)
...
Total: 3 pulseras × 9 receptores = 27 conexiones TCP simultáneas
+ Código complejo de broadcast
+ Si se desconecta una enfermera, hay que reconectar

CON MQTT:
Pulsera 1 → Broker (1 conexión)
           ↓
        (Broker distribuye automáticamente)
           ↓
Enfermera 1, 2, 3, Doctor 1, 2 (todos reciben)
Total: 1 conexión
+ Código simple de publicación
+ Si se desconecta enfermera, pulsera sigue funcionando
```

### Tópicos MQTT

Un **tópico** es una cadena jerárquica que organiza mensajes:

```
hospital/pacientes/123456/vitales/bpm
│         │         │      │       │
│         │         │      │       └─ Métrica específica
│         │         │      └─ Categoría
│         │         └─ ID paciente
│         └─ Tipo de datos
└─ Organización
```

#### Comodines en Tópicos

| Comodín | Nombre | Uso | Ejemplo |
|---------|--------|-----|---------|
| `+` | Single-level | Coincide 1 nivel | `hospital/pacientes/+/vitales` → `hospital/pacientes/123/vitales` ✅, `hospital/pacientes/123/45/vitales` ❌ |
| `#` | Multi-level | Coincide múltiples niveles | `hospital/#` → TODO bajo hospital |
| Ninguno | Exacto | Coincide exactamente | `hospital/pacientes/123/vitales/bpm` → exacto |

**Riesgo de Seguridad:**
```python
# Atacante se suscribe a TODO
cliente.subscribe("hospital/#")
# Ahora recibe TODOS los datos de TODOS los pacientes del hospital
```

---

## 3. 📦 Protocolo MQTT: Estructura de Paquetes

### Componentes de un Mensaje MQTT

```
┌─────────────────────────────────────────┐
│ PAQUETE MQTT                            │
├─────────────────────────────────────────┤
│ FIXED HEADER (2+ bytes)                 │
│ ┌───────────────────────────────────┐   │
│ │ Byte 1: Tipo y flags              │   │
│ │ Byte 2+: Longitud del payload     │   │
│ └───────────────────────────────────┘   │
│                                         │
│ VARIABLE HEADER (tamaño variable)       │
│ ┌───────────────────────────────────┐   │
│ │ Nombre del tópico (longitud+datos)│   │
│ │ Packet ID (para QoS)              │   │
│ └───────────────────────────────────┘   │
│                                         │
│ PAYLOAD (tamaño variable)               │
│ ┌───────────────────────────────────┐   │
│ │ Los datos reales (JSON, bytes)    │   │
│ └───────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

### Ejemplo Real: Mensaje de Vitales

```
FIXED HEADER:
0x30 0x49
│    │
│    └─ 73 bytes de longitud restante
└─ Tipo: PUBLISH (0x3), QoS: 1, DUP: 0, RETAIN: 0

VARIABLE HEADER:
0x00 0x27 (39 bytes = longitud del tópico)
hospital/pacientes/123456/vitales/bpm
0x00 0x01 (Packet ID = 1)

PAYLOAD:
{"bpm": 145, "timestamp": 1706510400.123}
```

**Total: 73 bytes**  
**Si fuera HTTP: 200+ bytes**  
**Compresión: 63% más pequeño**

### Tipos de Paquetes MQTT

| Tipo | Dirección | Propósito |
|------|-----------|-----------|
| **CONNECT** | Client→Broker | Iniciar sesión |
| **CONNACK** | Broker→Client | Confirmación de conexión |
| **PUBLISH** | Bidireccional | Enviar/recibir mensaje |
| **PUBACK** | Broker→Client | ACK de entrega (QoS 1) |
| **SUBSCRIBE** | Client→Broker | Suscribirse a tópico |
| **SUBACK** | Broker→Client | Confirmación suscripción |
| **UNSUBSCRIBE** | Client→Broker | Desuscribirse |
| **DISCONNECT** | Client→Broker | Cerrar sesión |
| **PING** | Client→Broker | Keep-alive |

### Quality of Service (QoS)

**QoS** = Nivel de garantía de entrega

| QoS | Nombre | Garantía | Latencia | Overhead | Uso |
|-----|--------|----------|----------|----------|-----|
| **0** | At Most Once | Envía 1 vez, puede perderse | Mínima | Mínimo | Sensores no críticos |
| **1** | At Least Once | Reintenta hasta confirmar ACK | Media | Medio | Alertas médicas |
| **2** | Exactly Once | Garantía de exactitud | Máxima | Máximo | Transacciones críticas |

**Diferencia en Flujo:**

```
QoS 0 (Fire and Forget):
Publisher: [PUBLISH] → Broker
           Listo, no espero respuesta

QoS 1 (At Least Once):
Publisher: [PUBLISH] → Broker
           Espera... Espera...
           [PUBACK] ← Confirmado

QoS 2 (Exactly Once):
Publisher: [PUBLISH] → Broker
           [PUBREC] ← Recibido
           [PUBREL] → Liberar
           [PUBCOMP] ← Completado
```

---

## 4. 💻 Implementación del Publicador (Pulsera)

### Código: `pulsera.py`

#### Import: `paho.mqtt.client`

```python
import paho.mqtt.client as mqtt
```

**¿Qué es Paho?**
- **Paho MQTT Client** es la librería Python oficial de Eclipse Foundation
- Implementa MQTT 3.1.1 completamente
- Maneja automáticamente: reconexión, reintentos, colas
- Compatible con cualquier broker MQTT estándar

```bash
# Instalación
pip install paho-mqtt
```

#### Conceptos Clave: CallbackAPIVersion

```python
cliente = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
#                     ↑
#                     IMPORTANTE: Versión de API
```

**¿Qué es CallbackAPIVersion?**

Paho mantiene dos versiones de API por compatibilidad:

| Versión | Lanzada | Estado | Diferencia |
|---------|---------|--------|-----------|
| **VERSION1** | 2016 | ⚠️ Deprecada | Callbacks con parámetro `userdata` |
| **VERSION2** | 2023 | ✅ Actual | Callbacks más limpios sin `userdata` |

**Diferencia en Callbacks:**

```python
# VERSION1 (antiguo)
def on_connect(client, userdata, flags, rc):
    pass

# VERSION2 (nuevo - más limpio)
def on_connect(client, flags, rc, properties):
    pass
```

Usamos **VERSION2** porque es el estándar moderno.

#### Estructura del Publicador

##### 1. Configuración y Conexión

```python
BROKER = "localhost"
PUERTO = 1883
TEMA = "hospital/pacientes/emanuel/vitales"

cliente = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
cliente.connect(BROKER, PUERTO, 60)
#                              ↑
#                      Keep-alive: 60 segundos
#                      (Si no hay actividad, envía PING)
```

**¿Qué es keep-alive?**
```
Problema: Firewall intermedio puede cerrar conexión "inactiva"
Solución: Cada 60 segundos enviar PINGREQ
Respuesta: Broker envía PINGRESP
Resultado: Conexión mantenida aunque no haya datos
```

##### 2. Simulación de Signos Vitales

```python
bpm = random.randint(55, 110)
oxigeno = random.randint(90, 100)

# Evento crítico (10% de probabilidad)
if random.random() < 0.1:
    bpm = random.randint(150, 190)  # Taquicardia
```

**¿Por qué esta lógica?**
- Normal: 55-110 BPM (rango clínico fisiológico)
- Crítico: 150-190 BPM (taquicardia arrítmica)
- 10% de eventos = simula estrés/actividad del paciente

##### 3. Serialización JSON

```python
payload = {
    "id_paciente": "123456",
    "timestamp": time.time(),
    "bpm": bpm,
    "spo2": oxigeno,
    "bateria": 85
}
mensaje_json = json.dumps(payload)
```

**¿Por qué JSON?**

| Formato | Tamaño | Legibilidad | Interoperabilidad |
|---------|--------|-------------|-------------------|
| **JSON** | 127 bytes | ✅ Excelente | ✅ Universal |
| **XML** | 200+ bytes | ✅ Excelente | ✅ Universal |
| **Binario** | 20 bytes | ❌ Nula | ⚠️ Específico |
| **CSV** | 60 bytes | ✅ Buena | ⚠️ Ambiguo |

JSON es **estándar de facto** en IoT moderno:
- Parseado por cualquier lenguaje
- Compacto pero legible
- Herramientas de validación (JSON Schema)

##### 4. Publicación del Mensaje

```python
cliente.publish(TEMA, mensaje_json)
#                ↑     ↑
#             Tópico  Payload
```

**¿Qué hace `publish()`?**

```
Internamente:
1. Crea paquete MQTT PUBLISH
2. Lo encola en buffer local
3. Lo envía al Broker
4. Broker lo recibe
5. Broker lo distribuye a suscriptores
6. Suscriptores lo reciben
```

**Flujo completo (< 50 ms típicamente):**
```
Pulsera          Broker           Enfermería
  │                │                  │
  ├──PUBLISH──────→│                  │
  │                ├──PUBLISH────────→│
  │                │                  │
  │                │ (en paralelo)
  │                ├──PUBLISH────────→Doctor
```

---

## 5. 💻 Implementación del Suscriptor (Enfermería)

### Código: `enfermeria.py`

#### Callbacks: La Arquitectura Event-Driven

```python
def al_recibir_mensaje(client, userdata, msg):
    # Este código se ejecuta CUANDO llega un mensaje
    # No es código de polling (no preguntas "¿hay mensaje?")
    pass

cliente.on_message = al_recibir_mensaje
```

**¿Qué es un Callback?**

```
Callback = "Llámame cuando algo suceda"

SIN Callback (Polling - Ineficiente):
while True:
    mensaje = broker.get_mensaje()
    if mensaje:
        procesar(mensaje)
    time.sleep(1)  # Desperdicia CPU

CON Callback (Event-Driven - Eficiente):
def al_recibir_mensaje(msg):
    procesar(msg)

broker.on_message = al_recibir_mensaje
# Broker me llama automáticamente cuando hay mensaje
# CPU duerme hasta que algo ocurra
```

#### Decodificación del Payload

```python
contenido = msg.payload.decode()
#           ↑
#           msg.payload es bytes (no es texto)
#           decode() lo convierte a string

# Ejemplo:
msg.payload = b'{"bpm": 145}'  # Bytes
contenido = '{"bpm": 145}'      # String
```

**¿Por qué enviamos bytes?**
```python
# Razón 1: Eficiencia
'{"bpm": 145}' → 14 caracteres = 14 bytes (UTF-8)

# Razón 2: Flexibilidad (también podría ser)
b'\x91\x91' → Binario comprimido = 2 bytes

# MQTT no sabe ni le importa si es JSON, XML, binario
# Solo transporta bytes
```

#### Parseo JSON y Validación

```python
datos = json.loads(contenido)
#       ↑
#       Convierte string JSON a diccionario Python

bpm = datos.get("bpm", 0)  # Si "bpm" no existe, retorna 0
```

**¿Por qué usar `.get()`?**

```python
# ❌ PELIGROSO:
bpm = datos["bpm"]
# Si "bpm" no existe → KeyError → crash

# ✅ SEGURO:
bpm = datos.get("bpm", 0)
# Si "bpm" no existe → retorna 0 → continúa
```

En medicina, el código debe ser **robusto**:
```
Si una pulsera envía JSON malformado,
el sistema NO debe caer
Debe loguear el error y continuar monitoreando otros pacientes
```

#### Análisis de Riesgo (Lógica de Negocio)

```python
if bpm > 120:
    print(f"🚨 ALERTA CRÍTICA: Paciente {paciente} con TAQUICARDIA ({bpm} BPM)")
else:
    print(f"✅ Paciente {paciente}: Estable ({bpm} BPM)")
```

**¿Qué es una taquicardia?**

| Clasificación | BPM | Estado | Acción |
|---------------|-----|--------|--------|
| Bradicardia | < 60 | Peligroso (ritmo lento) | ⚠️ Alertar |
| Normal | 60-100 | Salud | ✅ Monitores |
| Taquicardia leve | 100-120 | Esfuerzo/Estrés | 🔔 Notificar |
| Taquicardia | 120-150 | Arritmia | 🚨 ALERTA CRÍTICA |
| Crisis | > 150 | Paro inminente | 🆘 Llamar ambulancia |

Nuestro código solo alerta en **120+** (simplificado).

#### Manejo de Excepciones

```python
except json.JSONDecodeError:
    print("⚠️ Error: El mensaje recibido no es un JSON válido.")
except Exception as e:
    print(f"❌ Error procesando datos: {e}")
```

**¿Por qué dos tipos de excepciones?**

```
JSONDecodeError = Esperábamos JSON pero llegó basura
                  Ejemplo: "bpm": 145}  (falta {)
                  Acción: Loguearlo, ignorar

Exception = Algo inesperado
            Ejemplo: División por cero, file I/O error
            Acción: Loguearlo, ignorar, continuar
```

#### Loop Principal: `loop_forever()`

```python
try:
    cliente.loop_forever()
except KeyboardInterrupt:
    print("\nDesconectando central...")
```

**¿Qué es `loop_forever()`?**

```python
# Internamente hace algo como:
while True:
    # 1. Verifica conexión (keep-alive, reconexión)
    self._check_connection()
    
    # 2. Recibe paquetes MQTT del broker
    paquetes = self._socket_receive()
    
    # 3. Para cada paquete PUBLISH, dispara callback
    for paquete in paquetes:
        if paquete.tipo == PUBLISH:
            self.on_message(paquete)
    
    # 4. Duerme brevemente para no gastar CPU
    time.sleep(0.001)
```

Es un **event loop** bloqueante (no retorna hasta que se desconecte).

---

## 6. 🔴 Vulnerabilidades: El Puerto 1883 Sin Seguridad

### Vector 1: Autenticación Ausente

```python
cliente.connect(BROKER, PUERTO, 60)
# No hay usuario ni contraseña
# Cualquiera puede conectarse
```

**Escenario de Ataque:**

```python
# El atacante escribe en su máquina:
import paho.mqtt.client as mqtt

cliente = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
cliente.connect("192.168.1.100", 1883, 60)  # IP del hospital

# Ahora está adentro del broker sin credenciales
cliente.publish("hospital/pacientes/#", "MALWARE")
```

**Impacto:**
- ❌ Inyecta datos falsos
- ❌ Modifica señales vitales
- ❌ Publica alertas falsas
- ❌ Causa pánico en enfermería

### Vector 2: Cifrado Ausente (Texto Plano)

```bash
# Atacante captura tráfico:
sudo tcpdump -i eth0 -A port 1883 | grep -i paciente
```

**Resultado:**
```
{"id_paciente": "123456", "bpm": 145, "spo2": 98}
{"id_paciente": "123457", "bpm": 62, "spo2": 95}
{"id_paciente": "123458", "bpm": 89, "spo2": 97}

Atacante aprende:
✅ Cuántos pacientes hay
✅ IDs de pacientes
✅ Sus signos vitales en tiempo real
✅ Patrones de salud (si es diabético, hipertenso, etc.)
```

**Violación GDPR:**
```
Art. 4(1): Datos personales = Cualquier info que identifique a persona
Art. 5(1)(f): Integridad y confidencialidad
Art. 32: Cifrado obligatorio

Todo esto está siendo violado en tiempo real.
```

### Vector 3: Comodín de Suscripción (#)

```python
# Atacante en su máquina:
cliente.subscribe("hospital/#")

# Recibe TODO:
hospital/pacientes/123456/vitales/bpm
hospital/pacientes/123456/vitales/spo2
hospital/pacientes/123456/medicamentos/lista
hospital/pacientes/123456/alergias/ibuprofen
hospital/doctores/5678/credenciales/usuario
hospital/doctores/5678/credenciales/password
```

**Riesgo:** Escalada a credenciales, información sensible de doctores, etc.

### Vector 4: Falta de Control de Acceso

```python
# Sin ACL (Access Control List):
# Cualquiera puede publicar en CUALQUIER tópico

cliente.publish("hospital/pacientes/123456/vitales/bpm", 999)
# ✅ Se ejecuta sin problemas
# El doctor ve BPM = 999 (imposible fisiológicamente)
# Pánico, decisión médica errónea
```

### Vector 5: DoS (Denegación de Servicio)

```python
# Atacante flood:
while True:
    for i in range(10000):
        cliente.publish("hospital/pacientes/123456/vitales/bpm", random.randint(0, 200))
```

**Impacto:**
- Broker saturado
- Alertas reales perdidas
- Paciente crítico no detectado
- Muerte

---

## 7. 📊 Tabla de Vulnerabilidades Críticas

| ID | Vulnerabilidad | Severidad | CVSS | Impacto | Riesgo |
|-----|----------------|-----------|------|---------|--------|
| **V1** | Sin autenticación | CRÍTICA | 9.8 | Acceso total al broker | Altísimo |
| **V2** | Sin cifrado (1883) | CRÍTICA | 9.8 | Intercepción de PHI | Altísimo |
| **V3** | Comodín sin restricción | ALTA | 8.6 | Lectura de datos sensibles | Altísimo |
| **V4** | Sin ACL | ALTA | 8.2 | Publicación en tópicos críticos | Altísimo |
| **V5** | DoS resource | MEDIA | 6.5 | Interrupción servicio | Alto |
| **V6** | QoS 0 default | MEDIA | 6.0 | Pérdida de mensajes críticos | Medio |

---

## 8. 🎯 Escenarios de Ataque Clínico Real

### Escenario 1: Inyección de Paro Cardíaco

```
MOMENTO: 14:30, Hospital de Berlin
PACIENTE: Maria (habitación 405)
PULSERA: Monitoreada correctamente

ATAQUE:
14:31:00 → Hacker en cafetería se conecta a WiFi del hospital
14:31:15 → Conecta a broker MQTT 192.168.1.50:1883
14:31:20 → Publica:
          hospital/pacientes/405/vitales/bpm = 0
          hospital/pacientes/405/vitales/spo2 = 0

RESULTADO:
14:31:25 → Central enfermería ve: PARO CARDÍACO
14:31:26 → Alarma sonora estruendosa
14:31:27 → Enfermeros corren a habitación 405
14:31:28 → Encuentran a Maria consciente, incómoda por el pánico
14:31:30 → Falsa alarma
14:32:00 → Segundo ataque: otro paro falso en habitación 406
14:32:30 → Tercer ataque: otro paro falso en habitación 407

IMPACTO:
- Enfermeros desmoralizados (síndrome del "niño que gritaba lobo")
- Ignoran alerta REAL de paro cardíaco en habitación 410
- Paciente muere por negligencia involuntaria
```

### Escenario 2: Modificación de Rango de Normalidad

```
MOMENTO: Cuidado Intensivo

ATAQUE:
Hacker publica en "hospital/config/bpm_normal_max" = 200
(En lugar del verdadero 100)

RESULTADO:
Pacientes con taquicardia a 130 BPM NO generan alertas
Mueren de arritmias no detectadas
```

### Escenario 3: Corrupción de Medicación

```
ATAQUE:
Publica en "hospital/farmacia/dosis/maria_405" = 100 (en lugar de 10)
Publica en "hospital/medicamentos/lista/maria_405" = "Insulina"

RESULTADO:
Sistema automatizado dispensa 100 unidades en lugar de 10
Paciente diabético muere por hipoglucemia
```

---

## 9. 🛡️ Mitigaciones: Asegurar MQTT

### Mitigación 1: Autenticación + Contraseña

```bash
# mosquitto_secure.conf
allow_anonymous false
password_file /etc/mosquitto/pwfile
```

```bash
# Crear usuarios
mosquitto_passwd -c /etc/mosquitto/pwfile enfermera1
# Ingresa contraseña

mosquitto_passwd /etc/mosquitto/pwfile doctor1
mosquitto_passwd /etc/mosquitto/pwfile pulsera_maria
```

**Código Python:**

```python
cliente = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
cliente.username_pw_set("pulsera_maria", "contraseña123")  # ← CRÍTICO
cliente.connect(BROKER, PUERTO, 60)
```

**Seguridad:**
- ✅ Broker rechaza conexiones sin credenciales
- ✅ Se pueden auditar intentos fallidos
- ❌ Contraseña en texto plano en memoria (riesgo moderado)

### Mitigación 2: TLS/SSL (Cifrado)

```bash
# mosquitto_secure.conf
listener 8883  # Puerto TLS estándar
cafile /etc/mosquitto/ca.crt
certfile /etc/mosquitto/server.crt
keyfile /etc/mosquitto/server.key
```

**Código Python:**

```python
import ssl

cliente = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
cliente.username_pw_set("pulsera_maria", "contraseña123")

# ← CIFRADO TLS
cliente.tls_set(
    ca_certs="/path/to/ca.crt",
    certfile="/path/to/client.crt",
    keyfile="/path/to/client.key",
    cert_reqs=ssl.CERT_REQUIRED,
    tls_version=ssl.PROTOCOL_TLSv1_2,
    ciphers=None
)
cliente.tls_insecure = False  # Verificar certificados

cliente.connect(BROKER, 8883, 60)  # Puerto 8883 (TLS)
```

**Seguridad:**
- ✅ Datos cifrados (imposible ver JSON con Wireshark)
- ✅ Verificación de identidad del broker
- ✅ Forward Secrecy (si roban llave privada, no descifran datos pasados)
- ❌ Overhead ~15% CPU

### Mitigación 3: ACL (Access Control List)

```bash
# mosquitto_acl.conf
# Usuario pulsera_maria solo puede publicar en su tópico
user pulsera_maria
topic write hospital/pacientes/123456/vitales/#

# Usuario enfermera puede leer vitales de sus pacientes
user enfermera1
topic read hospital/pacientes/123456/vitales/#
topic read hospital/pacientes/123457/vitales/#

# Usuario doctor puede leer todos
user doctor1
topic read hospital/#

# Nadie más puede ver configuración
user admin
topic readwrite hospital/#
```

**Seguridad:**
- ✅ Pulsera NO puede leer datos de otros pacientes
- ✅ Enfermera NO puede modificar configuración
- ✅ Atacante con credenciales robadas tiene acceso limitado
- ✅ Principio de Menor Privilegio (PoLP)

### Mitigación 4: QoS = 2 (Exactitud)

```python
# En publicador:
cliente.publish("hospital/pacientes/123456/vitales/bpm", payload, qos=2)
#                                                                 ↑
#                                                        Exactly Once
```

**Seguridad:**
- ✅ No se pierden mensajes críticos
- ✅ No se duplican
- ❌ Latencia aumenta 50-100%

### Mitigación 5: Validación en Suscriptor

```python
def al_recibir_mensaje(client, userdata, msg):
    try:
        datos = json.loads(msg.payload.decode())
        
        # Validación 1: Estructura
        if not all(k in datos for k in ["bpm", "spo2", "id_paciente"]):
            raise ValueError("Campos faltantes")
        
        # Validación 2: Rangos
        if not (40 <= datos["bpm"] <= 200):
            raise ValueError(f"BPM imposible: {datos['bpm']}")
        
        if not (50 <= datos["spo2"] <= 100):
            raise ValueError(f"SpO2 imposible: {datos['spo2']}")
        
        # Si llegamos aquí, es válido
        procesar_datos(datos)
        
    except (json.JSONDecodeError, ValueError) as e:
        log_error(f"Mensaje rechazado: {e}")
        # NO procesar datos inválidos
```

**Seguridad:**
- ✅ Rechaza datos imposibles fisiológicamente
- ✅ Previene inyección lógica
- ✅ Log para auditoría

---

## 10. 📊 Tabla Comparativa: Antes vs Después

| Aspecto | Módulo 10 (Puerto 1883) | Con Mitigaciones |
|--------|--------------------------|-----------------|
| **Autenticación** | ❌ Ninguna | ✅ Usuario/contraseña |
| **Cifrado** | ❌ Texto plano | ✅ TLS 1.2+ (puerto 8883) |
| **Control Acceso** | ❌ Ninguno (todos acceden todo) | ✅ ACL granular |
| **QoS** | 0 (Fire & Forget) | 2 (Exactly Once) |
| **Validación** | ❌ Mínima | ✅ Exhaustiva |
| **Compliance GDPR** | ❌ Violación Art. 32 | ✅ Cumple |
| **Compliance HIPAA** | ❌ Violación Security Rule | ✅ Cumple |
| **Riesgo Integridad** | CRÍTICO | Bajo |
| **Riesgo Disponibilidad** | CRÍTICO (DoS) | Medio (rate limiting) |

---

## 11. 🔍 Validación Forense

### Captura con Wireshark: Antes

```bash
sudo tcpdump -i lo -A port 1883 | head -30
```

**Salida:**
```
14:30:45.123456 IP localhost.57234 > localhost.1883: Flags [P.], seq 1
E...."@.@....................
{"id_paciente":"123456","bpm":145,"spo2":98}

✅ VE EL CONTENIDO COMPLETO (JSON legible)
```

### Captura con Wireshark: Después (TLS)

```bash
sudo tcpdump -i lo -A port 8883 | head -30
```

**Salida:**
```
14:31:12.789012 IP localhost.57235 > localhost.8883: Flags [P.], seq 1
E...."@.@....................
..£'..z..H....Ü©ÅGÛüôì.....æu»c.,.w0.....
".©......*.}..¿Û$o..2m..Q.Ò

❌ SOLO VE BYTES ALEATORIOS (ilegible)
```

---

## 12. 📚 Conceptos Avanzados Aprendidos

| Concepto | Comprensión | Evidencia |
|----------|-------------|-----------|
| **Pub/Sub** | ⭐⭐⭐⭐⭐ | Implementaste broker con múltiples clientes |
| **MQTT** | ⭐⭐⭐⭐ | Entiendes estructura de paquetes |
| **Callbacks** | ⭐⭐⭐⭐ | Código event-driven funcional |
| **JSON** | ⭐⭐⭐⭐ | Serialización/deserialización segura |
| **QoS** | ⭐⭐⭐ | Entiendes garantías de entrega |
| **Tópicos y Comodines** | ⭐⭐⭐⭐ | Jerarquía y patrones de suscripción |
| **Seguridad MQTT** | ⭐⭐⭐⭐ | Autenticación, TLS, ACL |

---

## 13. 🎓 Resumen Ejecutivo: IoMT Vulnerable a Seguro

### Lo que Lograste

✅ **Implementaste sistema pub/sub real** (Paho MQTT)  
✅ **Comprendiste arquitectura IoMT médica** (Edge devices → Broker → Central)  
✅ **Identificaste 6 vulnerabilidades críticas** (Autenticación, Cifrado, ACL, DoS, Integridad, Validación)  
✅ **Diseñaste 5 mitigaciones** (Autenticación, TLS, ACL, QoS, Validación)  
✅ **Validaste con Wireshark** (Texto plano vs Cifrado)  

### Transformación

```
ANTES (Puerto 1883 inseguro):
- Datos médicos legibles en red
- Cualquiera puede conectarse
- Posible inyectar paro cardíaco falso
- GDPR/HIPAA violado

DESPUÉS (Puerto 8883 + TLS + ACL):
- Datos cifrados imposibles de leer
- Solo usuarios autenticados
- Ataques bloqueados por validación
- GDPR/HIPAA cumplido
```

### Impacto Clínico

```
Sin seguridad:
❌ Paciente muere por alerta falsa ignorada
❌ Medicación incorrecta por datos modificados
❌ Pérdida de confianza en sistemas médicos

Con seguridad:
✅ Alertas confiables
✅ Datos auténticos
✅ Cumplimiento regulatorio
✅ Privacidad del paciente protegida
```

### Próximos Pasos (Producción)

1. **Implementar MQTT sobre TLS** (port 8883)
2. **Configurar autenticación** (usuarios, contraseñas con hash)
3. **Definir ACL granular** (por rol: enfermera, doctor, dispositivo)
4. **Monitoreo y logging** (detectar intentos de acceso no autorizado)
5. **Encriptación en reposo** (base de datos)
6. **Auditoría GDPR** (demostrar conformidad)

---

*Última actualización: Enero 2026*  
*Módulo 10: IoMT & Telemetría - De Vulnerable a Seguro con MQTT+TLS*