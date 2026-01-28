# ⏰ HOJA DE RUTA: TIMELINE SEMANAL DETALLADO
## Ciberseguridad + IoMT | Febrero 2026 - Diciembre 2026

---

## 📍 CONTEXTO CRÍTICO

**Ubicación**: Febrero - Abril 2026 en **México** (3 meses finales)  
**Transición**: Mayo 2026 → **Alemania** (Ausbildung + UVEG)  
**Desafío**: Aprender mientras trabajas en prácticas hospitalarias  
**Herramientas**: Fedora Linux KDE, Docker, Python 3.x

---

## 🇲🇽 FASE 1: LABORATORIO EN MÉXICO (13 SEMANAS)
### Febrero 1 - Abril 30, 2026

---

## SEMANA 1-2: SETUP Y FUNDAMENTOS (Feb 3-16)

### Semana 1: Setup Completo
**Objetivo**: Tener tu entorno 100% operativo

#### Lunes - Miércoles: Instalaciones Básicas
```bash
# Actualizar Fedora
sudo dnf update -y

# Instalar herramientas básicas
sudo dnf install -y \
  git \
  python3-pip \
  docker-ce \
  wireshark \
  mosquitto \
  mosquitto-clients \
  nmap \
  curl \
  wget

# Agregar usuario a grupo docker
sudo usermod -aG docker $USER
# Requiere logout/login
```

**Tareas**:
- [ ] Actualizar Fedora a última versión
- [ ] Instalar todas las herramientas en lista
- [ ] Crear carpeta `/home/$USER/iomt-lab/`
- [ ] Inicializar git repository local

#### Jueves - Viernes: Configuración Inicial
**Git Setup**
```bash
git config --global user.name "Emanuel"
git config --global user.email "tu@email.com"
cd ~/iomt-lab
git init
```

**Crear estructura de directorios**
```
~/iomt-lab/
├── 01_wireshark/
├── 02_mqtt/
├── 03_linux_hardening/
├── 04_dicom/
├── 05_hl7/
├── 06_python_scripts/
└── README.md
```

**Documentación**:
- [ ] Crear `README.md` con descripción del proyecto
- [ ] Documentar versiones instaladas

### Semana 2: Fundamentos de Redes
**Objetivo**: Entender modelo OSI y TCP/IP

#### Lunes - Martes: Teoría
**Lectura + Anotaciones**:
- [ ] Modelo OSI (7 capas) - 2 horas
- [ ] Protocolo TCP/IP - 2 horas
- [ ] Subnetting básico - 1.5 horas

**Recursos**:
- CompTIA Network+: Search on YouTube (free)
- Wikipedia: OSI Model

#### Miércoles - Viernes: Práctica
```bash
# Ver interfaz de red
ip addr show

# Ver tabla de enrutamiento
ip route

# Calcular subredes
# Ej: 192.168.1.0/24
# - Network: 192.168.1.0
# - Broadcast: 192.168.1.255
# - IPs disponibles: 192.168.1.1 - 192.168.1.254
```

**Tareas Prácticas**:
- [ ] Identificar tu IP privada y pública
- [ ] Ver gateway y DNS
- [ ] Calcular 5 subredes distintas manualmente
- [ ] Documentar en `01_networks/networking_notes.md`

---

## SEMANA 3-4: WIRESHARK Y CAPTURA DE TRÁFICO (Feb 17-Mar 1)

### Semana 3: Wireshark Básico
**Objetivo**: Capturar y analizar tráfico de red

#### Lunes - Martes: Instalación y Interfaz
```bash
# Instalar (ya hecho, pero verificar)
wireshark --version

# Iniciar con sudo
sudo wireshark
```

**Tareas**:
- [ ] Iniciar Wireshark
- [ ] Identificar todas las interfaces de red
- [ ] Seleccionar interfaz Wi-Fi
- [ ] Capturar 2 minutos de tráfico en reposo

#### Miércoles - Viernes: Análisis Básico
**Captura y Filtrado**:
```bash
# En terminal (línea de comandos)
sudo tcpdump -i wlp3s0 -c 100 -w trafic.pcap

# Luego abrir en Wireshark
wireshark trafic.pcap
```

**Filtros en Wireshark**:
```
# Ver solo DNS
dns

# Ver solo HTTP
http

# Ver solo tráfico con tu IP
ip.src == 192.168.1.100 or ip.dst == 192.168.1.100

# Ver MQTT (puerto 1883)
tcp.port == 1883
```

**Análisis**:
- [ ] ¿Qué protocolos ves en tu red?
- [ ] ¿Hacia dónde apuntan las DNS queries?
- [ ] ¿Hay tráfico encriptado (HTTPS)?
- [ ] Documentar en `01_wireshark/analisis_semana1.md`

### Semana 4: Wireshark Avanzado
**Objetivo**: Análisis profundo de protocolos

#### Lunes - Miércoles: Disección de Paquetes
**Tareas**:
- [ ] Capturar 10 minutos de tráfico HTTP (navega un sitio)
- [ ] Analizar estructura de paquete TCP
  - Source/Destination IP
  - Source/Destination Port
  - Flags (SYN, ACK, FIN)
  - Payload

#### Jueves - Viernes: Búsqueda de Anomalías
```bash
# Capturar tráfico de aplicación específica
sudo tcpdump -i wlp3s0 -w app.pcap host 8.8.8.8

# Analizar en Wireshark
# Buscar comportamientos sospechosos:
# - Conexiones a puertos extraños
# - Múltiples retransmisiones
# - Timeouts
```

**Informe**:
- [ ] Crear `01_wireshark/semana4_informe.md`
- [ ] Incluir 3-5 capturas de pantalla
- [ ] Análisis de comportamiento normal vs anómalo

---

## SEMANA 5-6: MQTT SETUP (Mar 2-16)

### Semana 5: Mosquitto Broker
**Objetivo**: Levantar un servidor MQTT

#### Lunes - Martes: Instalación Local
```bash
# Instalar Mosquitto
sudo dnf install mosquitto mosquitto-clients

# Iniciar servicio
sudo systemctl start mosquitto
sudo systemctl enable mosquitto

# Verificar
sudo systemctl status mosquitto

# Ver puerto
netstat -tlnp | grep mosquitto
# Debe mostrar: :::1883
```

**Tareas**:
- [ ] Confirmar que Mosquitto corre en puerto 1883
- [ ] Ver logs: `sudo journalctl -u mosquitto`

#### Miércoles - Viernes: Cliente Básico
```bash
# Terminal 1: Suscribirse a un tema
mosquitto_sub -t "test/temperatura" -v

# Terminal 2: Publicar mensajes
mosquitto_pub -t "test/temperatura" -m "36.5"
mosquitto_pub -t "test/temperatura" -m "37.2"
mosquitto_pub -t "test/temperatura" -m "36.8"
```

**Tareas Prácticas**:
- [ ] Crear 5 temas MQTT diferentes
- [ ] Publicar/Suscribirse a cada uno
- [ ] Documentar estructura de temas en `02_mqtt/mqtt_topics.md`

**Ejemplo de Estructura de Temas**:
```
hospital/
├── sensores/
│   ├── temperatura/paciente_01
│   ├── ritmo_cardiaco/paciente_01
│   └── oximetro/paciente_02
├── dispositivos/
│   ├── bomba_infusion_01
│   └── monitor_signos_02
└── alertas/
    ├── critica
    └── advertencia
```

### Semana 6: Cliente MQTT en Python
**Objetivo**: Automatizar envío/recepción de datos

#### Lunes - Miércoles: Librería paho-mqtt

```bash
pip install paho-mqtt
```

**Script 1: Suscriptor Simple**
```python
# 02_mqtt/subscriber.py
import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, rc):
    print(f"[OK] Conectado con código: {rc}")
    client.subscribe("hospital/sensores/#")

def on_message(client, userdata, msg):
    print(f"[{msg.topic}] {msg.payload.decode()}")

client = mqtt.Client("subscriber_01")
client.on_connect = on_connect
client.on_message = on_message
client.connect("127.0.0.1", 1883, 60)
client.loop_forever()
```

**Tareas**:
- [ ] Crear script subscriber
- [ ] Ejecutar mientras publicas desde otra terminal
- [ ] Confirmar que recibe mensajes

#### Jueves - Viernes: Publicador Automático

```python
# 02_mqtt/publisher_sensor.py
import paho.mqtt.client as mqtt
import time
import json
import random
from datetime import datetime

BROKER = "127.0.0.1"
PORT = 1883
TOPIC_TEMP = "hospital/sensores/temperatura/paciente_01"

def on_connect(client, userdata, flags, rc):
    print(f"[Publicador] Conectado: {rc}")

client = mqtt.Client("sensor_temp_01")
client.on_connect = on_connect
client.connect(BROKER, PORT, 60)
client.loop_start()

# Enviar datos cada 5 segundos
try:
    contador = 0
    while True:
        temp = round(36.0 + random.uniform(-0.5, 0.5), 1)
        payload = json.dumps({
            "id": "paciente_01",
            "temperatura": temp,
            "timestamp": datetime.now().isoformat(),
            "unidad": "C"
        })
        client.publish(TOPIC_TEMP, payload)
        print(f"[{datetime.now()}] Temp: {temp}°C")
        contador += 1
        time.sleep(5)
        
        if contador >= 60:  # 5 min total
            break
except KeyboardInterrupt:
    client.disconnect()
```

**Tareas**:
- [ ] Crear script publicador
- [ ] Ejecutar 2 terminales: subscriber + publisher
- [ ] Capturar tráfico con Wireshark
  - [ ] Filtro: `tcp.port == 1883`
  - [ ] Analizar estructura de paquete MQTT
  - [ ] Documentar en `02_mqtt/wireshark_mqtt_analysis.md`

---

## SEMANA 7-8: LINUX HARDENING (Mar 17-30)

### Semana 7: Firewall y Control de Puertos
**Objetivo**: Asegurar tu sistema

#### Lunes - Martes: firewalld
```bash
# Ver estado
sudo systemctl status firewalld

# Ver configuración actual
sudo firewall-cmd --list-all

# Ver puertos abiertos
sudo ss -tlnp

# Aplicaciones corriendo
netstat -tlnp
```

**Tareas**:
- [ ] Documentar todos los puertos abiertos actuales
- [ ] En `03_linux_hardening/puertos_abiertos_inicial.txt`

#### Miércoles - Viernes: Configuración de Firewall

```bash
# Permitir solo SSH (puerto 22)
sudo firewall-cmd --permanent --remove-service=dhcpv6-client
sudo firewall-cmd --permanent --remove-service=cockpit
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-port=1883/tcp  # MQTT
sudo firewall-cmd --permanent --add-port=8080/tcp  # Web app

# Recargar reglas
sudo firewall-cmd --reload

# Verificar
sudo firewall-cmd --list-all
```

**Tareas de Seguridad**:
- [ ] Listar todos los servicios habilitados
- [ ] Deshabilitar los innecesarios
- [ ] Permitir solo puertos explícitamente necesarios
- [ ] Crear `03_linux_hardening/firewall_config.md` con todas las reglas

### Semana 8: Auditoría y Permisos
**Objetivo**: Monitorear acceso al sistema

#### Lunes - Miércoles: auditd
```bash
# Instalar
sudo dnf install audit audit-libs

# Iniciar servicio
sudo systemctl start auditd
sudo systemctl enable auditd

# Ver estado
sudo systemctl status auditd

# Ver logs recientes
sudo ausearch -ts recent | head -20
```

#### Jueves - Viernes: SELinux y Permisos

```bash
# Ver estado de SELinux
getenforce

# Ver contextos de archivos
ls -laZ /etc/mosquitto/

# Cambiar permisos críticos
sudo chmod 600 /etc/shadow
sudo chmod 600 /etc/gshadow
sudo chmod 644 /etc/passwd
sudo chmod 644 /etc/group

# Ver archivos con permisos débiles
sudo find /home -perm -002 -type f
```

**Documentación**:
- [ ] Crear `03_linux_hardening/seguridad_linea_base.md`
- [ ] Listar todos los cambios realizados
- [ ] Justificar por qué cada uno es necesario

---

## SEMANA 9-10: DICOM Y ANÁLISIS MÉDICO (Mar 31-Apr 13)

### Semana 9: pydicom
**Objetivo**: Leer archivos DICOM médicos

```bash
pip install pydicom pillow numpy matplotlib
```

#### Lunes - Martes: Lectura Básica

```python
# 04_dicom/read_dicom.py
from pydicom import dcmread
import os

# Leer archivo DICOM
dcm_file = "../paciente_anonimo.dcm"
dcm = dcmread(dcm_file)

# Información del paciente
print("=== INFORMACIÓN DEL PACIENTE ===")
print(f"Nombre: {dcm.PatientName}")
print(f"ID Paciente: {dcm.PatientID}")
print(f"Edad: {dcm.PatientAge}")
print(f"Sexo: {dcm.PatientSex}")

# Información médica
print("\n=== INFORMACIÓN MÉDICA ===")
print(f"Modalidad: {dcm.Modality}")  # CT, MR, XA, etc.
print(f"Descripción: {dcm.SeriesDescription}")
print(f"Fecha: {dcm.StudyDate}")
print(f"Fabricante: {dcm.Manufacturer}")
```

**Tareas**:
- [ ] Leer archivo `paciente_anonimo.dcm`
- [ ] Extraer 15 campos diferentes
- [ ] Documentar qué significa cada uno

#### Miércoles - Viernes: Análisis de Imagen

```python
# 04_dicom/visualize_dicom.py
from pydicom import dcmread
import matplotlib.pyplot as plt
import numpy as np

dcm = dcmread("../paciente_anonimo.dcm")

# Extraer datos de imagen
img = dcm.pixel_array

# Información de imagen
print(f"Dimensiones: {img.shape}")
print(f"Bits almacenados: {dcm.BitsAllocated}")
print(f"Ventana (Window Center): {dcm.WindowCenter}")
print(f"Ventana (Window Width): {dcm.WindowWidth}")

# Mostrar imagen
plt.figure(figsize=(10, 8))
plt.imshow(img, cmap='gray')
plt.title(f"DICOM: {dcm.SeriesDescription}")
plt.colorbar()
plt.savefig("04_dicom/imagen_dicom.png")
plt.close()

print("[OK] Imagen guardada")
```

**Tareas**:
- [ ] Visualizar imagen DICOM
- [ ] Guardar como PNG
- [ ] Extraer metadatos completos en JSON

```python
# 04_dicom/export_json.py
import json
from pydicom import dcmread
from pydicom.dataset import Dataset

dcm = dcmread("../paciente_anonimo.dcm")

# Convertir a diccionario
data_dict = {}
for elem in dcm:
    data_dict[elem.tag] = {
        "keyword": elem.keyword,
        "value": str(elem.value)
    }

# Guardar como JSON
with open("04_dicom/metadatos.json", "w") as f:
    json.dump(data_dict, f, indent=2)

print("[OK] Metadatos guardados")
```

### Semana 10: Seguridad DICOM
**Objetivo**: Entender privacidad en imágenes médicas

#### Lunes - Miércoles: Anonimización

```python
# 04_dicom/anonymize.py
from pydicom import dcmread
import secrets

dcm = dcmread("../paciente_anonimo.dcm")

# Campos sensibles a limpiar
campos_sensibles = [
    'PatientName',
    'PatientID',
    'PatientBirthDate',
    'PatientAddress',
    'InstitutionName',
    'ReferringPhysicianName'
]

# Anonimizar
for campo in campos_sensibles:
    if hasattr(dcm, campo):
        setattr(dcm, campo, f"ANONIMIZADO_{secrets.token_hex(4)}")

# Guardar copia anonimizada
dcm.save_as("04_dicom/paciente_anonimo_clean.dcm")
print("[OK] Archivo anonimizado creado")
```

#### Jueves - Viernes: Análisis de Seguridad

**Tareas**:
- [ ] Identificar qué información identifica a un paciente
- [ ] Crear checklist de DSGVO para DICOM
- [ ] Documentar en `04_dicom/seguridad_dicom_dsgvo.md`

---

## SEMANA 11-12: HL7 Y DATOS CLÍNICOS (Apr 14-27)

### Semana 11: HL7 Básico

```bash
pip install hl7
```

#### Lunes - Martes: Parsing de Mensajes

```python
# 05_hl7/parse_hl7.py
import hl7

# Mensaje HL7 real (simplificado)
hl7_msg = r'''MSH|^~\&|ORIGEN_APP|ORIGEN_FAC|DESTINO_APP|DESTINO_FAC|20260415120000||ADT^A01|MSG0001|P|2.5
PID|||12345^^^MRN||Pérez^Juan||19800101|M|||C.Falsa 123^^Madrid^28001^ES
OBX|1|TX|DIAGNOSIS||Hipertensión esencial
OBX|2|NM|TEMPERATURA||36.8
OBX|3|NM|PRESION_ARTERIAL||120/80'''

# Parsear
mensaje = hl7.parse(hl7_msg)

print("=== SEGMENTO MSH ===")
msh = mensaje.segment('MSH')
print(f"Aplicación origen: {msh[3]}")
print(f"Timestamp: {msh[7]}")

print("\n=== SEGMENTO PID ===")
pid = mensaje.segment('PID')
print(f"Nombre paciente: {pid[5]}")
print(f"Fecha nacimiento: {pid[7]}")
print(f"Sexo: {pid[8]}")
```

#### Miércoles - Viernes: Generación de Mensajes

```python
# 05_hl7/generate_hl7.py
import hl7
from datetime import datetime

# Crear componentes
msh = ['MSH', '^~\&', 'HOSPITAL', 'UNIDAD_UCI', 
       'SISTEMA_REMOTO', 'CENTRAL', 
       datetime.now().strftime('%Y%m%d%H%M%S'), 
       '', 'ADT^A01', 'MSG0002', 'P', '2.5']

pid = ['PID', '', '', '67890^^^MRN', '', 'García^María', 
       '', '19750615', 'F', '', 'C.Real 456^^Barcelona^08002^ES']

obx1 = ['OBX', '1', 'TX', 'DIAGNOSTICO', '', 'Diabetes Tipo 2']
obx2 = ['OBX', '2', 'NM', 'GLUCOSA', '', '145']

# Crear mensaje
msg = hl7.Message('\r', [
    hl7.Segment('|', msh),
    hl7.Segment('|', pid),
    hl7.Segment('|', obx1),
    hl7.Segment('|', obx2)
])

# Ver como string
mensaje_str = str(msg)
print(mensaje_str)

# Guardar a archivo
with open("05_hl7/mensaje_generado.hl7", "w") as f:
    f.write(mensaje_str)
```

### Semana 12: Integración y Proyecto Final
**Objetivo**: Proyecto integrador con todos los elementos

#### Lunes - Miércoles: Diseño de Proyecto

```
PROYECTO: "Sistema de Monitoreo Remoto Seguro"

Componentes:
1. Sensor (Python + MQTT)
2. Broker (Mosquitto)
3. Receptor (Python)
4. Análisis de datos (HL7)
5. Captura de tráfico (Wireshark)
6. Seguridad (firewall, encriptación)
```

#### Jueves - Viernes: Implementación

```python
# 06_proyecto_final/sensor_completo.py
import paho.mqtt.client as mqtt
import json
from datetime import datetime
import random
import hl7

# Configuración MQTT
BROKER = "127.0.0.1"
PORT = 1883
TOPIC = "hospital/monitoreo/paciente_001"

class MonitorMedico:
    def __init__(self):
        self.client = mqtt.Client("monitor_001")
        self.client.on_connect = self.on_connect
        
    def on_connect(self, client, userdata, flags, rc):
        print(f"[OK] Monitor conectado: {rc}")
        
    def generar_datos(self):
        """Genera datos médicos realistas"""
        return {
            "temperatura": round(36.0 + random.uniform(-1, 1), 1),
            "ritmo_cardiaco": random.randint(60, 100),
            "presion_sistolica": random.randint(110, 140),
            "presion_diastolica": random.randint(70, 90),
            "oxigenacion": random.randint(95, 99),
            "timestamp": datetime.now().isoformat()
        }
    
    def generar_mensaje_hl7(self):
        """Crea un segmento HL7 con los datos"""
        datos = self.generar_datos()
        # ... código para crear HL7 ...
        return hl7_message
    
    def enviar(self):
        self.client.connect(BROKER, PORT, 60)
        self.client.loop_start()
        
        try:
            while True:
                datos = self.generar_datos()
                payload = json.dumps(datos)
                self.client.publish(TOPIC, payload)
                print(f"[ENVIADO] {datos}")
                time.sleep(10)
        except KeyboardInterrupt:
            self.client.disconnect()

if __name__ == "__main__":
    monitor = MonitorMedico()
    monitor.enviar()
```

**Tareas del Proyecto**:
- [ ] Sensor MQTT funcionando
- [ ] Broker recibiendo datos
- [ ] Análisis en Wireshark completado
- [ ] Documentación completa en `06_proyecto_final/README.md`
- [ ] Presentación de resultados (incluir:)
  - Diagramas de arquitectura
  - Capturas de pantalla
  - Análisis de seguridad
  - Recomendaciones para producción

---

## 🇩🇪 FASE 2: ALEMANIA (Mayo - Diciembre 2026)

---

## MAYO-JUNIO: Transición y Enfoque Académico

### Primeras 4 Semanas en Alemania
**Enfoque**: Integración laboral + mantenimiento de conocimientos

#### Agenda Realista
```
Lunes-Viernes: 8:00-15:00 → Ausbildung (Prácticas hospitalarias)
Miércoles-Viernes: 17:00-19:00 → Estudio personal (1-2 horas/día)
Sábados: Estudio independiente (2-3 horas)
Domingos: Descanso/Revisión
```

**Enfoque**:
- [ ] Observar equipamiento médico (sin manipular)
- [ ] Documentar arquitectura de red hospitalaria
- [ ] Estudiar DSGVO en contexto médico alemán
- [ ] Escribir proyecto UVEG sobre seguridad médica

---

## JULIO-SEPTIEMBRE: Consolidación

### Fases Académicas
1. **Julio**: Cursos UVEG
2. **Agosto**: Investigación de campo + experiencia
3. **Septiembre**: Capstone project proposal

**Objetivo**: Completar proyecto final de Ingeniería integrando ciberseguridad IoMT

---

## OCTUBRE-DICIEMBRE: Finalización

### Último Trimestre
- [ ] Proyecto final de UVEG completado
- [ ] Certificación en Linux (opcional)
- [ ] Documentación de experiencias en Alemania
- [ ] Preparación para primer trabajo (CV + Portfolio)

---

## 📊 TRACKING DE PROGRESO

### Métricas por Mes

**FEBRERO**:
- [ ] 100% setup completo
- [ ] Wireshark básico funcional
- [ ] MQTT broker corriendo

**MARZO**:
- [ ] Cliente MQTT Python avanzado
- [ ] Linux hardening completado
- [ ] Análisis DICOM iniciado

**ABRIL**:
- [ ] HL7 parsing completado
- [ ] Proyecto final planteado
- [ ] Documentación al 80%

**MAYO-JUNIO**:
- [ ] Transición a Alemania sin pérdida de momentum
- [ ] Proyecto académico iniciado
- [ ] Primeras observaciones en hospital documentadas

**JULIO-AGOSTO**:
- [ ] Proyecto UVEG 50% completado
- [ ] Experiencia práctica consolidada
- [ ] Network hospitalario comprendido

**SEPTIEMBRE-DICIEMBRE**:
- [ ] Proyecto UVEG finalizado
- [ ] Portfolio actualizado
- [ ] Primer trabajo identificado

---

## 🎖️ HITOS CLAVE

### Semana 4 (Feb 17)
✅ Wireshark funcional, captura de tráfico documentada

### Semana 8 (Mar 17)
✅ MQTT broker corriendo, cliente Python completado

### Semana 12 (Apr 13)
✅ DICOM y HL7 analizados e integrados

### Semana 16 (May 11)
✅ Proyecto integrador completado con documentación

### Mes 5 (Junio)
✅ Integración a vida alemana + proyecto académico iniciado

### Mes 8 (Septiembre)
✅ Proyecto UVEG completado

### Mes 12 (Diciembre 2026)
✅ **OBJETIVO FINAL**: Ser especialista empleable en IoMT + Ciberseguridad

---

## 📚 RECURSOS RECOMENDADOS

| Semana | Recurso | Tipo | Tiempo |
|--------|---------|------|--------|
| 1-2 | CompTIA Network+ (YouTube) | Video | 6 horas |
| 3-4 | Wireshark Official Docs | Lectura | 3 horas |
| 5-6 | MQTT.org Spec | Lectura | 2 horas |
| 7-8 | CIS Benchmarks Linux | Lectura | 4 horas |
| 9-10 | pydicom Documentation | Código | 5 horas |
| 11-12 | HL7 Standard (simplified) | Lectura | 3 horas |

---

## 🚀 PRÓXIMOS PASOS

**Esta semana (27 Jan - 2 Feb)**:
- [ ] Crear estructura de carpetas
- [ ] Instalar todas las herramientas
- [ ] Verificar que todo funciona
- [ ] Iniciar apuntes de redes

¡Tienes 13 semanas. Puedes hacerlo. No es una maratón, es una carrera de resistencia. 💪
