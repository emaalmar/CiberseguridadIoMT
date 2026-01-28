# 🔓 STACK OPEN SOURCE: Ciberseguridad + IoMT
## Alternativas libres y gratuitas para tu laboratorio

---

## 📌 Por qué Open Source?

En Alemania, muchas instituciones hospitalarias **confían en soluciones open source**:
- ✅ **DSGVO compliant**: Sin telemetría oculta
- ✅ **Auditable**: Puedes ver el código
- ✅ **Económico**: Sin licencias costosas
- ✅ **Comunitario**: Soporte global

Dominando estas herramientas, **tendrás ventaja competitiva** en empleadores alemanes.

---

## 🛠️ 1. CAPTURA Y ANÁLISIS DE TRÁFICO

### 🥇 Wireshark (Open Source)
**Descarga**: https://www.wireshark.org/

```bash
# En Fedora
sudo dnf install wireshark
```

| Característica | Detalles |
|---|---|
| **Licencia** | GPL v2 |
| **Plataforma** | Linux, Windows, macOS |
| **Capacidades** | Captura en vivo, análisis profundo, filtros avanzados |
| **Para IoMT** | Ver tráfico MQTT, HL7, DICOM |

### 🥈 tcpdump (Ultra-Ligero)
```bash
sudo dnf install tcpdump
# Captura desde línea de comandos
sudo tcpdump -i eth0 -w captura.pcap
```

---

## 📡 2. MQTT: BROKER Y CLIENTE

### 🥇 Mosquitto (Open Source)
**Web**: https://mosquitto.org/

```bash
# Instalación en Fedora
sudo dnf install mosquitto mosquitto-clients

# Iniciar el broker
mosquitto -c /etc/mosquitto/mosquitto.conf

# En otra terminal: suscribirse a un tema
mosquitto_sub -t "hospital/sensores/#"

# Enviar datos (tercera terminal)
mosquitto_pub -t "hospital/sensores/temperatura" -m "36.5"
```

| Característica | Detalles |
|---|---|
| **Licencia** | EPL 2.0 (Open Source) |
| **Memoria** | ~2-3 MB (ideal para IoT) |
| **Seguridad** | TLS/SSL, autenticación username/password |
| **Clustering** | Soporta múltiples brokers en red |

### 🥈 Alternatives
- **HiveMQ Community Edition**: Versión gratuita con límites (https://www.hivemq.com/mqtt-broker/)
- **EMQX**: IoT platform open source (https://www.emqx.io/)

---

## 🔒 3. LINUX HARDENING

### 📋 Herramientas Esenciales (Todas Incluidas en Fedora)

#### firewalld (Firewall)
```bash
# Estado
sudo systemctl status firewalld

# Listar reglas actuales
sudo firewall-cmd --list-all

# Añadir una regla (SSH)
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --reload

# Ver puertos abiertos
sudo ss -tlnp
```

#### auditd (Auditoría)
```bash
sudo dnf install audit audit-libs

# Iniciar servicio
sudo systemctl start auditd
sudo systemctl enable auditd

# Ver logs de auditoría
sudo ausearch -ts recent
```

#### SELinux (Control de Acceso)
```bash
# Ver estado
getenforce

# Ver políticas
semanage fcontext -l | grep -i medical
```

### 🥇 CIS Benchmarks (Guía Libre)
**Web**: https://www.cisecurity.org/

Descarga el benchmark para Linux. Úsalo como checklist:
- Configuración de sistema
- Permisos de ficheros
- Servicios a desactivar

---

## 🏥 4. PROTOCOLOS MÉDICOS: ANÁLISIS Y GENERACIÓN

### DICOM (Imágenes Médicas)

#### pydicom (Python - Open Source)
```bash
pip install pydicom
```

```python
from pydicom import dcmread

# Leer archivo DICOM
dcm = dcmread('paciente_anonimo.dcm')
print(dcm.patient_name)
print(dcm.modality)  # ej: "CT", "MR"
```

**Documentación**: https://pydicom.github.io/

### HL7 / FHIR (Intercambio de Datos)

#### python-hl7 (Open Source)
```bash
pip install hl7
```

```python
import hl7

# Parsear mensaje HL7
msg = hl7.parse(r'MSH|^~\&|SENDING_APP|SENDING_FAC|RECEIVING_APP|RECEIVING_FAC|20231215120000||ADT^A01|MSG0001|P|2.5')
print(msg.segment('MSH'))
```

#### FHIR.js (JavaScript/Node.js)
```bash
npm install fhirpath
```

---

## 🐳 5. DOCKER & CONTENEDORES (Open Source)

### Docker Engine (Comunidad)
```bash
sudo dnf install docker-ce

# Iniciar servicio
sudo systemctl start docker
sudo usermod -aG docker $USER  # Sin sudo

# Verificar
docker --version
```

### Ejemplo: Levanta un Mosquitto en Docker
```bash
docker run -it --name mqtt-broker -p 1883:1883 \
  eclipse-mosquitto:latest
```

### Alternativa: Podman (Redhat - Más Seguro)
```bash
sudo dnf install podman

podman run -d --name mqtt \
  -p 1883:1883 \
  docker.io/library/eclipse-mosquitto
```

---

## 🐍 6. PYTHON: LIBRERÍAS ESPECÍFICAS PARA IoMT

```bash
pip install paho-mqtt       # Cliente MQTT
pip install pydicom         # Lectura DICOM
pip install hl7             # Parsing HL7
pip install cryptography    # Encriptación
pip install scapy           # Análisis de paquetes (alternativa tcpdump)
pip install requests        # HTTP/HTTPS
pip install flask           # Servidor web ligero
```

### Ejemplo Completo: Sensor MQTT Seguro
```python
import paho.mqtt.client as mqtt
import json
import random
from datetime import datetime

# Configuración
BROKER = "localhost"
PORT = 1883
TOPIC = "hospital/sensores/temperatura"

def on_connect(client, userdata, flags, rc):
    print(f"[OK] Conectado al broker. Código: {rc}")
    client.subscribe("hospital/comandos/#")

def on_message(client, userdata, msg):
    print(f"[MSG] {msg.topic}: {msg.payload.decode()}")

def on_disconnect(client, userdata, rc):
    print(f"[DESCONECTADO] Código: {rc}")

# Cliente
client = mqtt.Client(client_id="sensor_temperatura_01")
client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect

# Conectar (sin contraseña por ahora)
client.connect(BROKER, PORT, keepalive=60)

# Enviar datos cada 5 segundos
client.loop_start()
try:
    while True:
        temp = round(36.0 + random.random(), 1)
        payload = json.dumps({
            "sensor": "temp_001",
            "temperatura": temp,
            "timestamp": datetime.now().isoformat(),
            "unidad": "C"
        })
        client.publish(TOPIC, payload)
        print(f"[ENVIADO] Temperatura: {temp}°C")
        time.sleep(5)
except KeyboardInterrupt:
    client.disconnect()
```

---

## 🔐 7. SEGURIDAD: HERRAMIENTAS ESSENCIALES

### Nmap (Escaneo de Puertos - Open Source)
```bash
sudo dnf install nmap

# Escanear tu propia máquina
nmap localhost

# Escanear subred (con cuidado)
nmap -p 1883 192.168.1.0/24  # Buscar brokers MQTT
```

### OpenSSL (Certificados y Encriptación)
```bash
# Generar certificado auto-firmado (para MQTT)
openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 365 -nodes
```

### fail2ban (Protección contra Ataques)
```bash
sudo dnf install fail2ban

# Monitorea intentos fallidos de login
sudo systemctl start fail2ban
```

---

## 📦 8. STACK MÍNIMO RECOMENDADO

```yaml
Sistema Base: Fedora Linux (Ya tienes)

Captura de Tráfico:
  - Wireshark (GUI)
  - tcpdump (CLI)

Brokers IoT:
  - Mosquitto (MQTT)
  - EMQX (Alternativa más robusta)

Análisis Médico:
  - pydicom (Python)
  - python-hl7 (Python)

Contenedores:
  - Docker o Podman

Lenguajes:
  - Python 3.x (análisis)
  - Bash/Zsh (scripts)

Seguridad:
  - firewalld
  - auditd
  - SELinux
  - Nmap
  - OpenSSL
```

---

## 📚 9. RECURSOS DE APRENDIZAJE (TODOS GRATUITOS)

| Recurso | Link | Tema |
|---------|------|------|
| **Wireshark Official** | https://www.wireshark.org/download/ | Captura de tráfico |
| **MQTT.org** | https://mqtt.org/ | Protocolos IoT |
| **Mosquitto Docs** | https://mosquitto.org/man/mqtt-7/ | Broker MQTT |
| **pydicom Docs** | https://pydicom.github.io/ | DICOM en Python |
| **FHIR Docs** | https://www.hl7.org/fhir/ | Estándar HL7 FHIR |
| **Linux Foundation** | https://www.linuxfoundation.org/ | Certificaciones Linux |
| **CIS Benchmarks** | https://www.cisecurity.org/ | Hardening de Linux |
| **OWASP** | https://owasp.org/ | Seguridad Web/Apps |

---

## 🎯 10. PLAN DE ACCIÓN (FEBRERO - ABRIL 2026)

### Semana 1-2: Instalación y Primeros Pasos
- [ ] Instala Wireshark, Mosquitto, Docker
- [ ] Captura tráfico de tu propia red
- [ ] Levanta un broker MQTT local

### Semana 3-4: Python + MQTT
- [ ] Crea scripts en Python con paho-mqtt
- [ ] Simula un sensor médico
- [ ] Envía y recibe mensajes MQTT

### Semana 5-6: DICOM y HL7
- [ ] Lee archivos DICOM con pydicom
- [ ] Parsea mensajes HL7
- [ ] Analiza datos médicos reales (anonimizados)

### Semana 7-8: Seguridad y Hardening
- [ ] Configura firewall avanzado
- [ ] Activa auditoría en Linux
- [ ] Implementa MQTT con TLS/SSL
- [ ] Escanea tu red con Nmap

### Semana 9-12: Proyecto Integrador
- [ ] Crea un "monitoreo remoto seguro" con:
  - Sensor MQTT (Python)
  - Broker Mosquitto (Docker)
  - Cliente que recibe datos (Python)
  - Análisis de tráfico con Wireshark
  - Certificados TLS/SSL

---

## ⭐ El Diferenciador

A diferencia de otros ingenieros, **tú podrás decir en una entrevista**:
> "Monitoré tráfico MQTT en una red médica real, configuré firewalls compatibles con DSGVO, y validé datos HL7 usando herramientas open source. Todo sin comprar una sola licencia."

Eso es oro puro en Alemania. 🏆
