# 🔬 Bitácora de Ciberseguridad: Network Forensics (Módulo 8)

## Objetivo Estratégico
Validar la confidencialidad (o falta de ella) en la transmisión de datos HL7 mediante interceptación de paquetes (**Packet Sniffing**). Demostrar que sin cifrado, cualquier actor en la red puede leer información médica sensible.

**Herramientas:** tcpdump, Wireshark, Packet Analysis, Network Forensics

---

## 📝 Archivos Analizados en este Módulo

| Archivo | Función | Estado |
|---------|---------|--------|
| `hospital_server.py` | Servidor HL7 MLLP (escucha puerto 6661) | En ejecución |
| `recepcionista.py` | Cliente HL7 MLLP (envía mensajes) | En ejecución |
| Captura de Wireshark | Análisis de tráfico | VULNERABILIDAD IDENTIFICADA |

---

## 1. 🎯 El Hallazgo: Vulnerabilidad Confirmada

### La Prueba Forense

#### Paso 1: Capturar Tráfico de Red

```bash
# Terminal 1: Capturar TODOS los paquetes en puerto 6661
sudo tcpdump -i lo -A port 6661
#       ↑    ↑   ↑ ↑
#       │    │   │ └─ Protocolo TCP/UDP en puerto 6661
#       │    │   └─ ASCII output (ver contenido en texto)
#       │    └─ Interface loopback (localhost)
#       └─ Requiere root para acceder a interfaces de red
```

**Salida esperada:**
```
listening on lo, link-type EN10MB (Ethernet), snapshot length 262144 bytes
15:35:16.931253 IP localhost.54736 > localhost.6661: Flags [S], seq 3440894431, win 65495
...
```

#### Paso 2: Ejecutar el Servidor

```bash
# Terminal 2: Iniciar servidor HL7
sudo ./venv/bin/python hospital_server.py
[.] Escuchando en el puerto 6661...
```

#### Paso 3: Enviar Mensajes

```bash
# Terminal 3: Enviar mensaje del paciente
sudo ./venv/bin/python recepcionista.py

[1] Mensaje Generado: MSG-20260129153516
[2] Conectando a Mirth Connect (localhost:6661)...
 -> Datos enviados.
[3] Respuesta del Servidor:
 MSH|^~\&|PYTHON_SRV|LINUX|RECEPCION|HOSPITAL|...
✅ Transmisión Exitosa.
```

#### Paso 4: Observar la Captura de tcpdump

```bash
# En Terminal 1 (tcpdump), verás:
...
15:35:16.999999 IP localhost.54736 > localhost.6661: Flags [P.], seq 1:120, ack 1, win 65495, length 119
E...Z.@.@..........................0.........
k.O.k.O........
.................
...
MSH|^~\&|SISTEMA_PY|FEDORA|MIRTH|SERVER|20260129153516||ADT^A01|MSG-20260129153516|P|2.3
PID|||123456||LEDESMA^EMANUEL||19991108|M
PV1||I|URGENCIAS^304^1||||001^DR. HOUSE
...
```

**⚠️ VULNERABILIDAD OBSERVADA:**
- ✅ El mensaje HL7 se VE CLARAMENTE en la captura
- ✅ Nombre del paciente: `LEDESMA^EMANUEL`
- ✅ ID del paciente: `123456`
- ✅ Ubicación: `URGENCIAS^304^1`
- ❌ **TODO en TEXTO PLANO, sin encriptación**

---

## 2. 🔍 ¿Qué es Network Forensics?

### Definición

**Network Forensics** = Análisis de tráfico de red para:
- ✅ Identificar ataques en progreso
- ✅ Recopilar evidencia de brechas de seguridad
- ✅ Validar cumplimiento normativo
- ✅ Detectar comportamiento anómalo
- ✅ Reconstruir comunicaciones completas

### En el Contexto Médico (Regulatorio)

| Normativa | Requisito | ¿Lo Cumplimos? |
|-----------|-----------|---|
| **GDPR (EU)** | "Medidas técnicas de seguridad" (Art. 32) | ❌ NO |
| **HIPAA (USA)** | "Encriptación de datos en tránsito" | ❌ NO |
| **MDR (EU)** | "Protección contra acceso no autorizado" | ❌ NO |
| **ISO 27001** | "Confidencialidad de información" | ❌ NO |

**Veredicto Regulatorio:** Sistema **NO CONFORME** con normativas médicas europeas/estadounidenses.

---

## 3. 🕵️ Herramientas Utilizadas

### tcpdump: El Rastreador de Bajo Nivel

```bash
tcpdump -i lo -A port 6661
```

| Parámetro | Función | Ejemplo |
|-----------|---------|---------|
| `-i lo` | Interface a capturar | `lo` (loopback), `eth0` (ethernet), `wlan0` (WiFi) |
| `-A` | ASCII output | Ver contenido en texto legible |
| `-X` | Hex + ASCII | Ver en hexadecimal Y texto |
| `-nn` | No resolver DNS/puertos | Más rápido |
| `-w file.pcap` | Guardar a archivo | Para análisis posterior |
| `port 6661` | Filtro de puerto | Solo tráfico en ese puerto |

**Ventajas de tcpdump:**
- ✅ Ligero, usa pocos recursos
- ✅ Correo en línea de comandos
- ✅ Disponible en cualquier sistema Linux
- ✅ Perfecto para captures rápidas

**Desventajas:**
- ❌ Interfaz poco amigable
- ❌ Difícil analizar miles de paquetes
- ❌ No tiene UI gráfica

---

### Wireshark: El Analizador Gráfico

Aunque en este módulo usamos principalmente `tcpdump`, **Wireshark** es la herramienta profesional para análisis forense:

```bash
# Opción 1: Capturar en vivo
wireshark

# Opción 2: Abrir archivo previamente capturado
wireshark captura.pcap

# Opción 3: Capturar desde línea de comandos
tshark -i lo -A port 6661 | tee captura.pcap
```

#### Características Principales de Wireshark

| Característica | Uso | Ventaja |
|---|---|---|
| **Live Capture** | Capturar en tiempo real | Ver qué ocurre ahora |
| **Packet Inspector** | Ver detalles de cada paquete | Entender capa por capa |
| **Follow TCP Stream** | Reconstruir conversación TCP completa | Ver comunicación como si fuera chat |
| **Protocol Dissectors** | Decodificar protocolos (HTTP, DNS, HL7) | Parsear automáticamente |
| **Filters** | Buscar paquetes específicos | `tcp.port == 6661 && ip.src == 127.0.0.1` |
| **Color Coding** | Código de colores por protocolo | Identificar tipos de tráfico |
| **Export** | Guardar conversaciones | Evidencia forense |

#### Filtros Útiles en Wireshark

```
tcp.port == 6661           → Todo en puerto 6661
ip.src == 127.0.0.1        → Solo desde localhost
tcp.stream == 0            → Solo primera conexión TCP
contains "LEDESMA"         → Buscar string específico
frame.time.relative < 5    → Primeros 5 segundos
tcp.flags.syn == 1         → Solo handshake inicial
```

---

## 4. 📊 Análisis Profundo: Lo Que Se Vio

### Diagrama de Flujo de la Captura

```
[CLIENTE: recepcionista.py]
           ↓
   socket.connect(localhost:6661)
           ↓
   [TCP HANDSHAKE - 3 paquetes]
   SYN → SYN/ACK → ACK
           ↓
   socket.send(mensaje_mllp)
           ↓
   [PAQUETE CON DATOS - VISIBLE EN TEXTO PLANO]
   0B 4D 53 48 7C ... 1C 0D
   ↑  M  S  H  |     ↑  ↑
   SB [------ HL7 ------] EB CR
   
   → MENSAJE VISIBLE: MSH|^~\&|SISTEMA|...|LEDESMA^EMANUEL|...
           ↓
[SERVIDOR: hospital_server.py]
   socket.recv(1024)
           ↓
   socket.send(ack_mllp)
           ↓
   [PAQUETE CON ACK - TAMBIÉN EN TEXTO PLANO]
   MSA|AA|MSG-123456
           ↓
   socket.close()
```

### Los 4 Paquetes TCP Capturados

#### Paquete 1: SYN (Inicio de conexión)

```
15:35:16.931253 IP localhost.54736 > localhost.6661: Flags [S]
                     ↑              ↑         ↑
                 Timestamp      Cliente    Servidor
                 
[S] = SYN Flag (cliente solicita conexión)
```

**Contenido:** Header TCP únicamente, sin datos de aplicación.

#### Paquete 2: SYN/ACK (Servidor acepta)

```
15:35:16.931280 IP localhost.6661 > localhost.54736: Flags [S.]
```

**Contenido:** Header TCP, servidor confirma que puede recibir datos.

#### Paquete 3: ACK (Cliente confirma)

```
(No mostrado, pero ocurre automáticamente)
IP localhost.54736 > localhost.6661: Flags [.]
```

**Contenido:** Header TCP, confirmación de que la conexión está lista.

#### **⚠️ Paquete 4: DATOS (AQUÍ ESTÁ LA VULNERABILIDAD)**

```bash
# Esto es lo que tcpdump mostró con -A (ASCII):
15:35:16.999999 IP localhost.54736 > localhost.6661: Flags [P.], length 119

....
.................
...
MSH|^~\&|SISTEMA_PY|FEDORA|MIRTH|SERVER|20260129153516||ADT^A01|MSG-20260129153516|P|2.3
PID|||123456||LEDESMA^EMANUEL||19991108|M
PV1||I|URGENCIAS^304^1||||001^DR. HOUSE

# DATOS SENSIBLES VISIBLES:
- Nombre: LEDESMA^EMANUEL
- ID: 123456
- Ubicación: URGENCIAS^304^1
- Doctor: DR. HOUSE
- Fecha nacimiento: 19991108
- Sexo: M
```

---

## 5. ⚠️ Análisis de la Vulnerabilidad

### ¿Qué Es lo Malo?

```
ATACANTE EN LA RED
       ↓
   [Conectado a WiFi del hospital]
       ↓
   [Ejecuta tcpdump en su laptop]
       ↓
   [Captura tráfico puerto 6661]
       ↓
   [VE MENSAJES HL7 EN TEXTO PLANO]
       ↓
   [Extrae nombres, IDs, diagnósticos, doctores]
       ↓
   ACCESO A PII (PERSONALLY IDENTIFIABLE INFORMATION)
       ↓
   VIOLACIÓN DE GDPR/HIPAA
       ↓
   MULTAS: 4% del revenue anual (GDPR)
```

### Tabla: Información Expuesta

| Dato | Sensibilidad | Visible en tcpdump | Riesgo |
|------|---|---|---|
| Nombre del paciente | 🔴 CRÍTICA | ✅ Sí | Robo de identidad |
| ID del paciente | 🔴 CRÍTICA | ✅ Sí | Acceso a historia clínica |
| Fecha nacimiento | 🔴 CRÍTICA | ✅ Sí | Fraude de seguros |
| Ubicación en hospital | 🟠 ALTA | ✅ Sí | Privacidad violada |
| Médico tratante | 🟠 ALTA | ✅ Sí | Información diagnóstica |
| Tipo de evento (ADT^A01) | 🟠 ALTA | ✅ Sí | Saber cuándo ingresa/egresa |
| Tipo de habitación | 🟡 MEDIA | ✅ Sí | Inferir tipo de enfermedad |
| Sexo | 🟡 MEDIA | ✅ Sí | Identificación demográfica |

### Escenarios de Ataque Reales

#### Escenario 1: Insider Malicioso
```
Hospital: St. Mariahilf (Berlín)
Actor: Empleado administrativo en facturación
Motivación: Dinero (vender datos a aseguradoras)
Método: Ejecuta tcpdump en su computadora de oficina
Resultado: Acceso a datos de 10,000 pacientes
Impacto: GDPR Violation, €20,000,000 multa
```

#### Escenario 2: Atacante Externo (Conexión a WiFi pública)
```
Hospital: Oferece WiFi gratuito para visitantes
Actor: Ciberdelincuente en sala de espera
Motivación: Vender datos a mafiosos de seguros
Método: ARP Spoofing → MITM → tcpdump
Resultado: Acceso a datos de 5,000 pacientes
Impacto: Extorsión, venta de datos, reputación dañada
```

#### Escenario 3: Autoridades Maliciosas
```
País: Alemania (supongamos régimen totalitario hipotético)
Actor: Agencia de seguridad estatal
Motivación: Vigilancia política de disidentes
Método: Acceso a infraestructura de red hospitalaria
Resultado: Vigilancia médica de objetivos políticos
Impacto: Violación de derechos fundamentales
```

---

## 6. 🛡️ Mitigaciones: Cómo Arreglarlo

### Solución 1: MLLP + TLS (Recomendada para Producción)

```python
import ssl
import socket

# SERVIDOR CON TLS
context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
context.load_cert_chain(
    certfile="/etc/certs/hospital.crt",
    keyfile="/etc/certs/hospital.key"
)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('0.0.0.0', 6661))
s.listen()

with context.wrap_socket(s, server_side=True) as ssocket:
    conn, addr = ssocket.accept()
    # Ahora todos los datos están CIFRADOS con AES-256
    datos_encriptados = conn.recv(1024)
    # Descifre automático por SSL
```

**Ventajas:**
- ✅ Datos cifrados con AES-256
- ✅ Autenticación de servidor (certificado)
- ✅ Integridad (verificación HMAC)
- ✅ Compatible con estándar MLLP-TLS (puerto 2575)

**Desventajas:**
- ❌ Requiere certificados (autofirmados o de CA)
- ❌ Overhead de CPU (encriptación)

### Solución 2: VPN (Aislar la Red)

```bash
# Todos los servidores en una VPN privada
# Los clientes deben conectarse VPN primero
# Tráfico encriptado a nivel de red

wireguard config:
[Interface]
PrivateKey = ...
Address = 10.0.0.1/24

[Peer]
PublicKey = ...  # Hospital_Receptor
AllowedIPs = 10.0.0.2/32
Endpoint = ...
```

**Ventajas:**
- ✅ Encriptación de todo el tráfico
- ✅ Autenticación de pares (peers)
- ✅ Aislamiento de red completo

**Desventajas:**
- ❌ Mayor complejidad de infraestructura
- ❌ Requiere configuración en múltiples máquinas

### Solución 3: Firewall + Restricción de Red

```bash
# Solo permitir tráfico desde IPs conocidas
sudo firewall-cmd --add-rich-rule='rule family="ipv4" source address="192.168.1.10" port protocol="tcp" port="6661" accept'

# Bloquear todo lo demás
sudo firewall-cmd --add-rich-rule='rule family="ipv4" port protocol="tcp" port="6661" reject'
```

**Ventajas:**
- ✅ Rápido de implementar
- ✅ Bajo overhead

**Desventajas:**
- ❌ No cifra datos (solo restringe acceso)
- ❌ Inútil contra ataques internos

### Solución 4: Cifrado en Reposo (Datos en BD)

```python
from cryptography.fernet import Fernet

# Cifrar datos antes de guardar en BD
cifrador = Fernet(clave_secreta)
nombre_cifrado = cifrador.encrypt(b"LEDESMA^EMANUEL")

# Guardar en BD
db.insert("pacientes", {
    "id": 123456,
    "nombre": nombre_cifrado,  # Cifrado
    "fecha_nac": 19991108
})

# Al leer
nombre_descifrado = cifrador.decrypt(nombre_cifrado)
```

**Ventajas:**
- ✅ Protege datos si la BD es comprometida
- ✅ Cumplimiento GDPR

**Desventajas:**
- ❌ No protege datos en tránsito
- ❌ Impacto en búsquedas (no indexable mientras cifrado)

---

## 7. 📋 Tabla Resumen: Mitigaciones vs Riesgos

| Medida | Encriptación | Costo | Complejidad | Compliance |
|--------|---|---|---|---|
| **Sin protección** | ❌ | $0 | 1/10 | ❌ FALLA |
| **Firewall** | ❌ | $500 | 3/10 | ⚠️ PARCIAL |
| **MLLP+TLS** | ✅ | $1000 | 5/10 | ✅ APRUEBA |
| **VPN** | ✅ | $2000 | 7/10 | ✅ APRUEBA |
| **Cifrado en reposo** | ✅ | $1500 | 6/10 | ✅ APRUEBA |
| **Todas (Defense in Depth)** | ✅✅✅ | $4500 | 9/10 | ✅✅ GOLD |

---

## 8. 🔐 Cómo Capturar Mensajes HL7 (Para Auditoría)

### Método 1: tcpdump con Guardado

```bash
# Capturar y guardar a archivo
sudo tcpdump -i lo -w captura_hl7.pcap port 6661

# Leer el archivo
tcpdump -r captura_hl7.pcap -A

# Analizar de forma bonita
tcpdump -r captura_hl7.pcap -X -l | grep -A 20 "MSH|"
```

### Método 2: Wireshark (Interfaz Gráfica)

```bash
# Instalar
sudo apt install wireshark

# Ejecutar
wireshark

# En la interfaz:
1. Seleccionar interface "Loopback" (lo)
2. Filtro: port 6661
3. Click en "Start Capturing"
4. Ejecutar recepcionista.py
5. Ver paquetes en tiempo real
6. Click derecho → "Follow TCP Stream" → VER TODO EL TRÁFICO
```

#### Vista de Wireshark

```
┌─────────────────────────────────────────────────────────┐
│ Interfaces: lo ◉ eth0 ○ wlan0 ○                         │
├─────────────────────────────────────────────────────────┤
│ Filter: port 6661                    [Start] [Stop]     │
├─────────────────────────────────────────────────────────┤
│ No.  Time      Source      Dest      Protocol Info      │
├─────────────────────────────────────────────────────────┤
│ 1    0.000     127.0.0.1:54736→6661  TCP [SYN]         │
│ 2    0.001     127.0.0.1:6661→54736  TCP [SYN,ACK]     │
│ 3    0.002     127.0.0.1:54736→6661  TCP [ACK]         │
│ 4    0.003     127.0.0.1:54736→6661  MLLP DATA 119 B   │
│                                       ▲ ← AQUÍ HACEN    │
│ 5    0.004     127.0.0.1:6661→54736  MLLP ACK 85 B    │
└─────────────────────────────────────────────────────────┘

Click en paquete 4:
┌─────────────────────────────────────────────────────────┐
│ Frame 4: 119 bytes on wire (952 bits)                   │
│ Ethernet II, Src: 00:00:00:00:00:00, Dst: ...          │
│ Internet Protocol Version 4, Src: 127.0.0.1, Dst:      │
│ Transmission Control Protocol, Src Port: 54736          │
│ [DATA SECTION]                                          │
│ 0b4d5348 7c5e7e5c 26... MSH|^~\&|SISTEMA|FEDORA|...   │
│ (cada paquete mostrado en HEX y ASCII)                  │
│                                                         │
│ CONTENIDO:                                              │
│ MSH|^~\&|SISTEMA_PY|FEDORA|MIRTH|SERVER|...            │
│ PID|||123456||LEDESMA^EMANUEL||19991108|M             │
│ PV1||I|URGENCIAS^304^1||||001^DR. HOUSE                │
└─────────────────────────────────────────────────────────┘
```

---

## 9. 📈 Lecciones Aprendidas

### Conocimientos Técnicos

| Concepto | Comprensión | Aplicación |
|----------|---|---|
| **Packet Sniffing** | ⭐⭐⭐⭐⭐ | Puedes capturar y analizar tráfico de red |
| **tcpdump** | ⭐⭐⭐⭐ | Herramienta de línea de comandos para captures |
| **Wireshark** | ⭐⭐⭐ | Interfaz gráfica para análisis forense |
| **TCP Handshake** | ⭐⭐⭐⭐ | Entiendes cómo comienza una conexión |
| **Cleartext vs Encrypted** | ⭐⭐⭐⭐⭐ | Impacto crítico en seguridad |
| **Network Forensics** | ⭐⭐⭐⭐ | Puedes identificar brechas de seguridad |

### Competencias de Ciberseguridad

| Competencia | Nivel | Evidencia |
|---|---|---|
| **Detección de Vulnerabilidades** | ⭐⭐⭐⭐⭐ | Identificaste tráfico en cleartext |
| **Análisis Forense** | ⭐⭐⭐⭐ | Reconstruiste conversación TCP |
| **Auditoría de Seguridad** | ⭐⭐⭐⭐ | Evaluaste cumplimiento GDPR/HIPAA |
| **Mitigación de Riesgos** | ⭐⭐⭐ | Propuesiste soluciones (TLS, VPN, Firewall) |

### Lo Más Importante

> **"La encriptación no es un lujo, es una obligación legal"**

Si transmites datos médicos sin cifrar, estás violando GDPR/HIPAA. Punto.

---

## 10. 🎯 Ejercicios Prácticos

### Nivel 1: Captura Básica

```bash
# 1. Capturar tráfico durante 30 segundos
timeout 30 sudo tcpdump -i lo -A port 6661 > captura.txt

# 2. Enviar mensajes
python recepcionista.py  # En otra terminal

# 3. Buscar "LEDESMA" en la captura
grep "LEDESMA" captura.txt

# 4. ¿Cuántos datos sensibles encontraste?
```

### Nivel 2: Análisis con Wireshark

```bash
# 1. Guardar captura en archivo
sudo tcpdump -i lo -w captura.pcap port 6661

# 2. Enviar mensajes
python recepcionista.py

# 3. Abrir en Wireshark
wireshark captura.pcap

# 4. Click derecho en paquete → "Follow TCP Stream"
# 5. ¿Qué datos ves? ¿Qué tan fácil es leerlos?
```

### Nivel 3: Implementar TLS

```python
# 1. Generar certificados autofirmados
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes

# 2. Modificar hospital_server.py para usar SSL
# (Ver sección 6, Solución 1)

# 3. Capturar tráfico con Wireshark
# 4. Intentar leer el contenido
# 5. ¿Ves datos en cleartext? ¿Cuál es la diferencia?
```

---

## 11. 🔒 Resumen Ejecutivo

### Lo Que Pasó

✅ Se configuró cliente y servidor HL7 MLLP  
✅ Se capturó tráfico con tcpdump  
✅ Se analizaron paquetes con ASCII output  
✅ Se identificaron datos sensibles en cleartext  

### Lo Que Significa

❌ **Sin cifrado, los datos médicos son accesibles a cualquiera en la red**  
❌ **Violación directa de GDPR/HIPAA**  
❌ **Riesgo de multas, demandas, cierre hospitalario**  

### Lo Que Hay Que Hacer

🛡️ **Implementar MLLP+TLS (Obligatorio)**  
🛡️ **Agregar Firewall (Recomendado)**  
🛡️ **Aislar en VPN (Recomendado)**  
🛡️ **Auditar regularmente con tcpdump/Wireshark**  

### Cumplimiento Normativo

| Normativa | Requisito | Actual | Necesario |
|-----------|-----------|--------|-----------|
| GDPR | Encriptación en tránsito | ❌ | ✅ TLS |
| HIPAA | Protección de PHI | ❌ | ✅ TLS + VPN |
| MDR | Seguridad de datos | ❌ | ✅ TLS + Firewall |
| ISO 27001 | Confidencialidad | ❌ | ✅ Múltiples capas |

---

## 12. 📚 Referencia Rápida

### Comandos tcpdump

```bash
# Captura simple
sudo tcpdump -i lo port 6661

# Con ASCII
sudo tcpdump -i lo -A port 6661

# Con Hex + ASCII
sudo tcpdump -i lo -X port 6661

# Guardar a archivo
sudo tcpdump -i lo -w archivo.pcap port 6661

# Leer archivo
tcpdump -r archivo.pcap -A

# Verbose
sudo tcpdump -i lo -v -A port 6661

# Número de paquetes
sudo tcpdump -i lo -c 50 port 6661
```

### Comandos Wireshark

```bash
# Instalar
sudo apt install wireshark

# Ejecutar
wireshark

# Capturar desde CLI (tshark)
tshark -i lo -A port 6661

# Guardar y analizar
tshark -i lo -w captura.pcap port 6661
wireshark captura.pcap
```

---

*Última actualización: Enero 2026*  
*Módulo 8: Network Forensics - Demostración de Vulnerabilidad en Tránsito*
