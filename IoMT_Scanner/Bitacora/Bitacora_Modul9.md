# 🔐 Bitácora de Ciberseguridad: Criptografía Aplicada (Módulo 9)

## Objetivo Estratégico
Implementar cifrado robusto (TLS 1.2/1.3) sobre canales de comunicación médicos heredados para mitigar el riesgo de intercepción (Sniffing). Transformar un sistema vulnerable en uno que cumple con estándares regulatorios europeos (GDPR/DSGVO).

**Herramientas:** OpenSSL, Python `ssl`, TLS/SSL, PKI (Public Key Infrastructure), Certificados X.509

---

## 📝 Archivos Creados/Modificados en este Módulo

| Archivo | Tipo | Función |
|---------|------|---------|
| `hospital_tls.py` | **NUEVO** | Servidor HL7 con cifrado TLS (puerto 6662) |
| `recepcionista_tls.py` | **NUEVO** | Cliente HL7 con cifrado TLS |
| `hospital.key` | **NUEVO** | Llave privada RSA 2048 bits |
| `hospital.crt` | **NUEVO** | Certificado digital X.509 autofirmado |
| `Bitacora(Modul9).md` | **NUEVO** | Documentación (este archivo) |

---

## 1. 🎓 Fundamentos Teóricos: ¿Qué es TLS/SSL?

### Definición

**TLS** = *Transport Layer Security* (Seguridad de la Capa de Transporte)  
**SSL** = *Secure Sockets Layer* (Capa de Sockets Seguros) - Predecesor obsoleto de TLS

Es un **protocolo criptográfico** que proporciona:
- ✅ **Confidencialidad:** Los datos viajan cifrados (nadie puede leerlos)
- ✅ **Integridad:** Los datos no pueden ser modificados sin detección
- ✅ **Autenticación:** Verificación de identidad del servidor (y opcionalmente del cliente)

### Ubicación en el Modelo OSI

```
┌─────────────────────────────────────────────────────┐
│ CAPA 7: APLICACIÓN (HL7, HTTP, SMTP)               │
├─────────────────────────────────────────────────────┤
│ CAPA 6: PRESENTACIÓN                                │
├─────────────────────────────────────────────────────┤
│ CAPA 5: SESIÓN                                      │
│         ┌─────────────────────────────────┐         │
│         │ TLS/SSL (AQUÍ SE UBICA)         │ ← Cifrado
│         └─────────────────────────────────┘         │
├─────────────────────────────────────────────────────┤
│ CAPA 4: TRANSPORTE (TCP, UDP)                       │
├─────────────────────────────────────────────────────┤
│ CAPA 3: RED (IP)                                    │
└─────────────────────────────────────────────────────┘

TLS opera ENTRE la aplicación y TCP
→ La aplicación NO sabe que hay cifrado
→ TCP NO sabe que hay cifrado
→ TLS es TRANSPARENTE para ambos
```

### ¿Por Qué es Importante en IoMT?

| Escenario | Sin TLS | Con TLS |
|-----------|---------|---------|
| **WiFi del hospital** | Atacante ve nombres de pacientes | Atacante ve solo bytes aleatorios |
| **Red corporativa** | Administrador puede leer diagnósticos | Administrador solo ve tráfico encriptado |
| **Compliance GDPR** | ❌ Violación Art. 32 | ✅ Cumplimiento técnico |
| **Multas potenciales** | €20,000,000 o 4% revenue | ✅ Protección legal |

---

## 2. 🔑 Infraestructura de Clave Pública (PKI)

### Conceptos Fundamentales

#### ¿Qué es PKI?

**PKI** = *Public Key Infrastructure* (Infraestructura de Clave Pública)

Es el **ecosistema completo** que permite usar criptografía asimétrica de forma segura:

```
PKI = Certificados + Autoridades Certificadoras + Políticas + Tecnología
```

#### Componentes de PKI

| Componente | Rol | Analogía |
|------------|-----|----------|
| **CA (Autoridad Certificadora)** | Entidad confiable que firma certificados | Notario público |
| **Certificado Digital** | Documento que vincula identidad con llave pública | Cédula de identidad |
| **Llave Privada** | Secreto matemático del dueño | Llave de tu casa |
| **Llave Pública** | Número público que cualquiera puede usar | Dirección de tu casa |
| **CRL (Lista de Revocación)** | Lista de certificados cancelados | Lista negra |

### Criptografía Asimétrica: El Corazón de TLS

#### El Problema que Resuelve

```
ESCENARIO SIN CRIPTOGRAFÍA ASIMÉTRICA:
Cliente y Servidor nunca se conocieron antes
¿Cómo comparten una contraseña secreta por Internet?

RESPUESTA: ¡Imposible de forma segura!
Si envías la contraseña por Internet, un atacante puede interceptarla
```

#### La Solución: Dos Llaves Relacionadas Matemáticamente

```python
# Generación de par de llaves (simplificado)
llave_privada = generar_numero_primo_gigante()  # 2048 bits
llave_publica = funcion_matematica(llave_privada)  # Relacionadas

# Propiedad mágica:
# Lo que cifras con llave_publica solo se descifra con llave_privada
# Lo que firmas con llave_privada se verifica con llave_publica

# Ejemplo:
mensaje = "LEDESMA^EMANUEL"
mensaje_cifrado = cifrar(mensaje, llave_publica)  # Cualquiera puede hacer esto
mensaje_descifrado = descifrar(mensaje_cifrado, llave_privada)  # SOLO el dueño
```

#### Tabla de Operaciones

| Operación | Usa Llave | Propósito | Quién Puede |
|-----------|-----------|-----------|-------------|
| **Cifrar** | Pública | Confidencialidad | Cualquiera |
| **Descifrar** | Privada | Leer mensaje | Solo dueño |
| **Firmar** | Privada | Autenticación/Integridad | Solo dueño |
| **Verificar Firma** | Pública | Validar origen | Cualquiera |

### Certificado Digital X.509

#### ¿Qué Contiene?

```
CERTIFICADO DIGITAL (hospital.crt)
┌─────────────────────────────────────────────────┐
│ Versión: 3                                      │
│ Número de Serie: 1a:2b:3c:4d:...               │
├─────────────────────────────────────────────────┤
│ IDENTIDAD DEL PROPIETARIO                       │
│ - Common Name (CN): localhost                   │
│ - Organization (O): Hospital Berlin             │
│ - Country (C): DE                               │
├─────────────────────────────────────────────────┤
│ LLAVE PÚBLICA                                   │
│ - Algoritmo: RSA                                │
│ - Tamaño: 2048 bits                             │
│ - Valor: MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8A...    │
├─────────────────────────────────────────────────┤
│ VALIDEZ                                         │
│ - Válido desde: 2026-01-29 00:00:00 UTC        │
│ - Válido hasta: 2027-01-29 00:00:00 UTC        │
├─────────────────────────────────────────────────┤
│ FIRMA DIGITAL                                   │
│ - Algoritmo: SHA256-RSA                         │
│ - Firmado por: (Self-signed)                    │
│ - Valor de firma: 3a:4b:5c:...                  │
└─────────────────────────────────────────────────┘

Este archivo es PÚBLICO (se comparte libremente)
```

#### Tipos de Certificados

| Tipo | Firmado Por | Uso | Ejemplo |
|------|-------------|-----|---------|
| **Self-signed** | Uno mismo | Testing, desarrollo | Tu `hospital.crt` |
| **CA-signed** | Autoridad Certificadora | Producción | Let's Encrypt, DigiCert |
| **Root CA** | Nadie (auto-firmado) | CA raíz confiable | Mozilla Root Store |

---

## 3. 🛠️ La Cerrajería: Generación de Certificados

### El Comando OpenSSL (Desglosado)

```bash
openssl req -newkey rsa:2048 -nodes -keyout hospital.key -x509 -days 365 -out hospital.crt
```

#### Desglose Completo

| Componente | Significado | Explicación Profunda |
|------------|-------------|---------------------|
| `openssl` | Herramienta CLI | Suite criptográfica open-source (industria estándar) |
| `req` | Request | Comando para gestionar **Certificate Signing Requests** (CSR) |
| `-newkey rsa:2048` | **Nueva llave RSA** | Genera un par de llaves usando algoritmo RSA con módulo de 2048 bits |
| `-nodes` | **No DES** | "No encrypt the private key" - La llave NO tiene contraseña (peligroso en producción) |
| `-keyout hospital.key` | Archivo salida llave | Dónde guardar la **llave privada** (NUNCA compartir) |
| `-x509` | Formato X.509 | En lugar de generar un CSR, crear un **certificado autofirmado** directamente |
| `-days 365` | Validez | El certificado expira en 365 días (1 año) |
| `-out hospital.crt` | Archivo salida certificado | Dónde guardar el **certificado público** (se comparte con clientes) |

#### ¿Qué es RSA 2048?

**RSA** = Rivest-Shamir-Adleman (nombres de los inventores)

```
2048 bits = 617 dígitos decimales

Ejemplo de número primo usado:
24485026704962652867716763858993237355831149026259
81476396745998042154993334032959076890483104390764
...
(309 dígitos más)

Factorizar este número con supercomputadoras actuales:
Tiempo estimado: 300+ AÑOS
```

| Tamaño Llave | Seguridad | Uso |
|--------------|-----------|-----|
| 1024 bits | ❌ Roto | Obsoleto desde 2015 |
| 2048 bits | ✅ Seguro hasta 2030 | Estándar actual |
| 4096 bits | ✅ Seguro hasta 2050+ | Bancos, gobiernos |

#### ¿Qué es `-nodes` (No DES)?

```bash
# CON contraseña (más seguro pero incómodo)
openssl req -newkey rsa:2048 -keyout hospital.key ...
# Te pedirá: "Enter PEM pass phrase:"
# Resultado: hospital.key está CIFRADO
# Cada vez que inicies el servidor, pedirá contraseña

# SIN contraseña (nuestra versión)
openssl req -newkey rsa:2048 -nodes -keyout hospital.key ...
# NO pide contraseña
# Resultado: hospital.key en TEXTO PLANO
# Servidor inicia automáticamente
# ⚠️ RIESGO: Si alguien roba el archivo, tiene acceso total
```

**Best Practice Producción:**
- Llave CON contraseña
- Almacenar contraseña en gestor secreto (HashiCorp Vault, AWS Secrets Manager)
- Servidor lee contraseña de forma segura al iniciar

#### ¿Qué es X.509?

**X.509** es un **estándar internacional (ITU-T)** que define:
- Estructura de certificados digitales
- Formato de campos (CN, O, OU, C, etc.)
- Algoritmos de firma permitidos (RSA, ECDSA)
- Cómo verificar cadenas de confianza

```
JERARQUÍA X.509:
Root CA (Auto-firmado)
  └─ Intermediate CA (Firmado por Root)
      └─ End-Entity Certificate (Firmado por Intermediate)
          └─ hospital.crt ← Nosotros estamos aquí (autofirmado)
```

#### Proceso Interactivo del Comando

```bash
❯ openssl req -newkey rsa:2048 -nodes -keyout hospital.key -x509 -days 365 -out hospital.crt

Generating a RSA private key
.......................+++++
.....+++++
writing new private key to 'hospital.key'
-----
You are about to be asked to enter information that will be incorporated
into your certificate request.
What you are about to enter is what is called a Distinguished Name or a DN.
-----
Country Name (2 letter code) [AU]: DE                    # Alemania
State or Province Name [Some-State]: Berlin              # Estado
Locality Name []: Berlin                                  # Ciudad
Organization Name []: Hospital Charite                    # Organización
Organizational Unit Name []: IT Security                  # Departamento
Common Name []: localhost                                 # CRÍTICO: Hostname
Email Address []: admin@hospital.de                       # Email

# RESULTADO:
# - hospital.key (Llave privada 2048 bits)
# - hospital.crt (Certificado X.509 con los datos ingresados)
```

**⚠️ Importancia del Common Name (CN):**
```python
# Si pones CN=localhost
# El cliente DEBE conectarse a "localhost"
conn = context.wrap_socket(sock, server_hostname="localhost")  # ✅ OK

# Si pones CN=hospital.example.com
# El cliente DEBE conectarse a "hospital.example.com"
conn = context.wrap_socket(sock, server_hostname="hospital.example.com")  # ✅ OK
conn = context.wrap_socket(sock, server_hostname="localhost")  # ❌ ERROR
# Resultado: ssl.CertificateError: hostname 'localhost' doesn't match 'hospital.example.com'
```

---

## 4. 🔐 Implementación del Servidor TLS

### Código: `hospital_tls.py`

#### Import Crítico: `ssl`

```python
import ssl  # <--- La librería mágica
```

**¿Qué es el módulo `ssl`?**
- Wrapper Python para OpenSSL
- Implementa TLS/SSL sobre sockets TCP
- Maneja handshake, cifrado, descifrado automáticamente

#### Conceptos Clave del Código

##### 1. Creación del Contexto SSL

```python
context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
#                                     ↑
#                             Este contexto es para SERVIDOR
```

**¿Qué es un "Contexto SSL"?**

Es un **objeto de configuración** que define:
- Versión de TLS a usar (TLS 1.2, 1.3)
- Cifrados permitidos (AES-256-GCM, ChaCha20-Poly1305)
- Validación de certificados
- Opciones de seguridad

```python
# Lo que create_default_context() hace internamente:
context.minimum_version = ssl.TLSVersion.TLSv1_2  # No permite SSL 3.0, TLS 1.0, TLS 1.1
context.options |= ssl.OP_NO_SSLv2                # Deshabilita SSLv2 (inseguro)
context.options |= ssl.OP_NO_SSLv3                # Deshabilita SSLv3 (POODLE attack)
context.options |= ssl.OP_NO_COMPRESSION          # Previene CRIME attack
context.set_ciphers('DEFAULT:!aNULL:!eNULL:!MD5:!3DES')  # Solo cifrados fuertes
```

**Propósitos de Contexto:**

| Propósito | Uso | Ejemplo |
|-----------|-----|---------|
| `ssl.Purpose.CLIENT_AUTH` | Servidor autenticándose ante clientes | `hospital_tls.py` |
| `ssl.Purpose.SERVER_AUTH` | Cliente verificando servidor | `recepcionista_tls.py` |

##### 2. Carga de Certificado y Llave

```python
context.load_cert_chain(certfile=CERT_FILE, keyfile=KEY_FILE)
#                       ↑                    ↑
#                   hospital.crt         hospital.key
#                   (Público)            (SECRETO)
```

**¿Qué hace `load_cert_chain()`?**

1. **Lee `hospital.crt`:** Extrae la llave pública y los metadatos
2. **Lee `hospital.key`:** Carga la llave privada en memoria
3. **Verifica concordancia:** Confirma que la llave pública en el certificado corresponde a la llave privada
4. **Prepara para handshake:** El servidor está listo para demostrar su identidad

**¿Por qué "chain" (cadena)?**

```python
# Caso simple (nosotros):
context.load_cert_chain(
    certfile="hospital.crt"  # 1 certificado autofirmado
)

# Caso producción (cadena completa):
context.load_cert_chain(
    certfile="hospital.crt",           # Certificado del servidor
    # Internamente hospital.crt contendría:
    # 1. Certificado end-entity (hospital)
    # 2. Certificado intermediate CA
    # 3. Certificado root CA (opcional)
)
```

##### 3. El "Wrap" Mágico (Envoltura SSL)

```python
# Socket TCP normal (inseguro)
bindsocket = socket.socket()
bindsocket.bind((HOST, PORT))
bindsocket.listen(5)

newsocket, fromaddr = bindsocket.accept()

# ¡AQUÍ OCURRE LA MAGIA!
conn = context.wrap_socket(newsocket, server_side=True)
#      ↑                   ↑           ↑
#      Contexto SSL    Socket TCP   "Soy servidor, no cliente"
```

**¿Qué hace `wrap_socket()`?**

```
ANTES:
newsocket → [Cliente habla TCP] → [Servidor recibe TCP]
            Datos en TEXTO PLANO

DESPUÉS:
conn → [Cliente cifra con TLS] → [Servidor descifra con TLS]
       Datos ENCRIPTADOS en tránsito
       
Proceso:
1. Cliente envía "Client Hello" (Cifrados soportados)
2. Servidor envía "Server Hello" (Cifrado elegido)
3. Servidor envía su certificado (hospital.crt)
4. Cliente verifica certificado
5. Cliente genera secreto temporal, lo cifra con llave pública del servidor
6. Servidor descifra secreto con su llave privada
7. Ambos derivan llave de sesión simétrica (AES-256)
8. ¡Conexión segura establecida!
```

##### 4. Inspección del Cifrado

```python
print(f"    Cifrado: {conn.cipher()}")
# Salida típica:
# ('ECDHE-RSA-AES256-GCM-SHA384', 'TLSv1.3', 256)
#  ↑                             ↑           ↑
#  Suite de cifrado            Versión    Bits de llave simétrica
```

**Desglose de la Suite de Cifrado:**

```
ECDHE-RSA-AES256-GCM-SHA384
  ↑     ↑   ↑      ↑   ↑
  │     │   │      │   └─ Hash: SHA-384 (para integridad)
  │     │   │      └─ Modo: GCM (Galois/Counter Mode - autenticado)
  │     │   └─ Cifrado simétrico: AES con llave de 256 bits
  │     └─ Firma: RSA (para autenticar servidor)
  └─ Key Exchange: Elliptic Curve Diffie-Hellman Ephemeral (Forward Secrecy)
```

| Componente | Algoritmo | Propósito | Seguridad |
|------------|-----------|-----------|-----------|
| **ECDHE** | Diffie-Hellman Curva Elíptica | Intercambio de llaves | ⭐⭐⭐⭐⭐ Forward Secrecy |
| **RSA** | RSA 2048 bits | Autenticación del servidor | ⭐⭐⭐⭐ |
| **AES-256** | AES 256 bits | Cifrado de datos | ⭐⭐⭐⭐⭐ Máxima seguridad |
| **GCM** | Galois/Counter Mode | Autenticación + cifrado | ⭐⭐⭐⭐⭐ |
| **SHA-384** | SHA-2 384 bits | Hash de integridad | ⭐⭐⭐⭐⭐ |

**Forward Secrecy (Secreto Perfecto hacia Adelante):**
```
Propiedad: Si un atacante roba hospital.key MAÑANA,
           NO puede descifrar el tráfico de HOY.

¿Cómo? ECDHE genera llaves de sesión EFÍMERAS (temporales)
       que se destruyen después de cada conexión.
```

##### 5. Manejo de Errores SSL

```python
except ssl.SSLError as e:
    print(f"⛔ Error de Seguridad (Handshake fallido): {e}")
```

**Errores Comunes:**

| Error | Causa | Solución |
|-------|-------|----------|
| `ssl.SSLError: [SSL: CERTIFICATE_VERIFY_FAILED]` | Cliente no confía en certificado | Agregar certificado a trust store |
| `ssl.SSLError: [SSL: WRONG_VERSION_NUMBER]` | Cliente no habla TLS | Verificar que cliente use `wrap_socket()` |
| `ssl.SSLError: [SSL: SSLV3_ALERT_HANDSHAKE_FAILURE]` | Incompatibilidad de cifrados | Ajustar cifrados permitidos |
| `ssl.SSLError: [SSL: KEY_VALUES_MISMATCH]` | Certificado y llave no coinciden | Regenerar par |

---

## 5. 🔐 Implementación del Cliente TLS

### Código: `recepcionista_tls.py`

#### Conceptos Clave

##### 1. Contexto para Cliente

```python
context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
#                                     ↑
#                             "Voy a verificar UN SERVIDOR"
```

**Diferencia con servidor:**
```python
# SERVIDOR (hospital_tls.py):
context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
# → "Voy a autenticar CLIENTES" (opcional)

# CLIENTE (recepcionista_tls.py):
context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
# → "Voy a verificar EL SERVIDOR"
```

##### 2. Verificación del Certificado del Servidor

```python
context.load_verify_locations(CERT_FILE)
#      ↑
#      "Confía en este certificado específico"
```

**¿Por qué es necesario?**

```
PROBLEMA:
hospital.crt es AUTOFIRMADO
→ No está firmado por CA reconocida (Let's Encrypt, DigiCert)
→ Python NO lo tiene en su trust store por defecto
→ Si intentas conectar, falla con CERTIFICATE_VERIFY_FAILED

SOLUCIÓN:
Le decimos explícitamente a Python:
"Confía en hospital.crt aunque sea autofirmado"
```

**En Producción (Certificado de CA):**
```python
# NO necesitas load_verify_locations() si usas CA reconocida
context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
# Python automáticamente confía en:
# - Let's Encrypt
# - DigiCert
# - GlobalSign
# - Etc. (root store del sistema operativo)
```

##### 3. Opcional: Deshabilitar Verificación de Hostname

```python
# context.check_hostname = False  # ← Comentado por seguridad
```

**¿Cuándo usarlo?**

| Escenario | `check_hostname` | Seguridad |
|-----------|------------------|-----------|
| Producción (CN=hospital.com, conectas a hospital.com) | `True` | ✅ Máxima |
| Testing (CN=localhost, conectas a 127.0.0.1) | `False` | ⚠️ Solo dev |
| Testing (CN=localhost, conectas a localhost) | `True` | ✅ OK |

**Error típico:**
```python
# Certificado CN=localhost
# Pero conectas a IP:
context.wrap_socket(sock, server_hostname="127.0.0.1")
# Error: ssl.CertificateError: hostname '127.0.0.1' doesn't match 'localhost'

# Solución 1: Deshabilitar check
context.check_hostname = False

# Solución 2: Usar hostname correcto
context.wrap_socket(sock, server_hostname="localhost")  # ✅
```

##### 4. Wrap del Socket del Cliente

```python
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
conn_segura = context.wrap_socket(sock, server_hostname=IP_SERVIDOR)
#                                       ↑
#                        CRÍTICO: Debe coincidir con CN del certificado
conn_segura.connect((IP_SERVIDOR, PUERTO_SERVIDOR))
```

**Diferencia con servidor:**
```python
# SERVIDOR:
conn = context.wrap_socket(newsocket, server_side=True)
#                                     ↑ Parámetro diferente

# CLIENTE:
conn = context.wrap_socket(sock, server_hostname="localhost")
#                                 ↑ Parámetro diferente
```

##### 5. Inspección de Versión TLS

```python
print(f"    Versión: {conn_segura.version()}")
# Salida:
# TLSv1.3  ← Mejor
# TLSv1.2  ← Bueno
# TLSv1.1  ← Obsoleto (no debería ocurrir con create_default_context)
```

**Versiones de TLS:**

| Versión | Año | Estado | Seguridad |
|---------|-----|--------|-----------|
| SSL 3.0 | 1996 | ❌ Roto (POODLE) | Prohibido |
| TLS 1.0 | 1999 | ❌ Obsoleto | Prohibido por PCI DSS |
| TLS 1.1 | 2006 | ❌ Obsoleto | Prohibido por PCI DSS |
| TLS 1.2 | 2008 | ✅ Seguro | Aceptable |
| TLS 1.3 | 2018 | ✅ Moderno | Recomendado |

---

## 6. 🔬 Validación Forense: ¿Funcionó el Cifrado?

### Prueba con Wireshark

#### Configuración

```bash
# 1. Abrir Wireshark
wireshark

# 2. Seleccionar interface: Loopback (lo)

# 3. Filtro de captura:
tcp.port == 6662

# 4. Iniciar captura

# 5. En terminales separadas:
Terminal 1: sudo ./venv/bin/python hospital_tls.py
Terminal 2: sudo ./venv/bin/python recepcionista_tls.py
```

#### Resultado Esperado en Wireshark

```
PAQUETES VISIBLES:
┌─────────────────────────────────────────────────┐
│ No.  Protocol  Info                              │
├─────────────────────────────────────────────────┤
│ 1    TCP       [SYN]                            │
│ 2    TCP       [SYN, ACK]                       │
│ 3    TCP       [ACK]                            │
│ 4    TLSv1.3   Client Hello                     │ ← Handshake
│ 5    TLSv1.3   Server Hello                     │ ← Handshake
│ 6    TLSv1.3   Certificate, Server Key Exchange │ ← Certificado
│ 7    TLSv1.3   Client Key Exchange, Finished    │ ← Fin handshake
│ 8    TLSv1.3   Application Data                 │ ← DATOS CIFRADOS
│ 9    TLSv1.3   Application Data                 │ ← ACK CIFRADO
│ 10   TCP       [FIN, ACK]                       │
└─────────────────────────────────────────────────┘

Click derecho en paquete 8 → Follow → TLS Stream
```

**Vista del Stream (SIN cifrado - Módulo 7):**
```
MSH|^~\&|SISTEMA_PY|FEDORA|...|LEDESMA^EMANUEL|...
PID|||123456||LEDESMA^EMANUEL||19991108|M
```

**Vista del Stream (CON TLS - Módulo 9):**
```
17 03 03 00 89 d4 f2 8a 9c 3e 7b a1 4f 92 cd e8
4a 6c 9f 2d 8b 47 5e 3a f9 0c 2b 8d 4e 7f a2 6c
... (bytes aleatorios)
... IMPOSIBLE leer "LEDESMA" o "123456"
```

### Comparativa Visual

```
┌─────────────────────────────────────────────────┐
│ MÓDULO 7 (Sin TLS) - puerto 6661               │
├─────────────────────────────────────────────────┤
│ Follow TCP Stream:                              │
│ MSH|^~\&|SISTEMA|FEDORA|...                     │
│ PID|||123456||LEDESMA^EMANUEL||19991108|M      │
│                                                 │
│ ✅ VULNERABLE: Todo visible en texto plano      │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│ MÓDULO 9 (Con TLS) - puerto 6662               │
├─────────────────────────────────────────────────┤
│ Follow TLS Stream:                              │
│ d4 f2 8a 9c 3e 7b a1 4f 92 cd e8 4a 6c 9f 2d  │
│ 8b 47 5e 3a f9 0c 2b 8d 4e 7f a2 6c b3 5d 1e  │
│                                                 │
│ ✅ SEGURO: Datos completamente ininteligibles   │
└─────────────────────────────────────────────────┘
```

---

## 7. 📊 Cumplimiento Normativo: Antes vs Después

### Tabla de Cumplimiento GDPR/DSGVO

| Artículo | Requisito | Módulo 7 (Sin TLS) | Módulo 9 (Con TLS) |
|----------|-----------|--------------------|--------------------|
| **Art. 32.1(a)** | "Pseudonimización y cifrado de datos personales" | ❌ NO | ✅ SÍ |
| **Art. 32.1(b)** | "Confidencialidad, integridad, disponibilidad" | ❌ Falla confidencialidad | ✅ Cumple |
| **Art. 32.2** | "Medidas técnicas apropiadas al riesgo" | ❌ Inadecuado | ✅ Apropiado |
| **Art. 33** | "Notificación de brechas de seguridad" | ⚠️ Brecha continua | ✅ Riesgo mitigado |
| **Art. 83.4** | "Multas hasta €10M o 2% revenue" | ⚠️ Riesgo alto | ✅ Protección |

### Tabla de Cumplimiento HIPAA

| Regla | Requisito | Sin TLS | Con TLS |
|-------|-----------|---------|---------|
| **Security Rule § 164.312(a)(2)(iv)** | "Encryption and decryption" | ❌ | ✅ |
| **Security Rule § 164.312(e)(1)** | "Transmission security" | ❌ | ✅ |
| **Breach Notification Rule** | "Notificar si PHI expuesto" | ⚠️ | ✅ Safe Harbor |

**Safe Harbor:**
```
Si datos médicos están CIFRADOS y la llave NO es robada,
→ NO se considera "brecha notificable"
→ NO necesitas notificar a los 50,000 pacientes afectados
→ Ahorras millones en costos de notificación
```

---

## 8. 🎓 Conceptos Avanzados Aprendidos

### Tabla de Conocimientos Técnicos

| Concepto | Comprensión | Evidencia |
|----------|-------------|-----------|
| **TLS/SSL** | ⭐⭐⭐⭐⭐ | Implementaste servidor y cliente |
| **PKI** | ⭐⭐⭐⭐ | Generaste certificados y llaves |
| **Criptografía Asimétrica** | ⭐⭐⭐⭐ | Entiendes llave pública/privada |
| **X.509** | ⭐⭐⭐ | Sabes qué contiene un certificado |
| **OpenSSL** | ⭐⭐⭐⭐ | Usaste CLI para generar certificados |
| **Python ssl module** | ⭐⭐⭐⭐⭐ | Código funcional con wrap_socket |
| **Handshake TLS** | ⭐⭐⭐ | Entiendes el proceso de negociación |
| **Forward Secrecy** | ⭐⭐⭐ | Sabes qué es ECDHE |

### Lo Más Importante que Aprendiste

#### 1. **El cifrado NO es opcional en medicina**
```
GDPR Art. 32: "Medidas técnicas apropiadas"
→ TLS/SSL es OBLIGATORIO para transmitir PHI/PII
```

#### 2. **Certificados autofirmados solo para testing**
```
Producción → Usar CA reconocida (Let's Encrypt es gratis)
Testing → Autofirmado está bien
```

#### 3. **TLS es transparente para la aplicación**
```python
# Sin TLS:
socket.send(datos)
socket.recv(1024)

# Con TLS:
conn_segura.send(datos)  # Automáticamente cifrado
conn_segura.recv(1024)   # Automáticamente descifrado
```

#### 4. **Wireshark puede ver el handshake, pero NO los datos**
```
Visible:
- Client Hello (cifrados soportados)
- Server Hello (cifrado elegido)
- Certificate (hospital.crt en claro)
- Finished

NO visible:
- Datos de aplicación (HL7)
- Contenido de mensajes
- Información del paciente
```

---

## 9. 🛡️ Comparativa Final: Módulos 7 vs 9

### Diagrama de Arquitectura

```
MÓDULO 7: SISTEMA VULNERABLE
┌──────────────┐                    ┌──────────────┐
│  Cliente     │────TCP(cleartext)──>│  Servidor    │
│ recep...py   │  Puerto 6661        │ hospital.py  │
└──────────────┘                    └──────────────┘
       │                                    │
       └──────────[Wireshark]───────────────┘
                      ↓
            ✅ VE TODO EN TEXTO PLANO


MÓDULO 9: SISTEMA SEGURO
┌──────────────┐                    ┌──────────────┐
│  Cliente TLS │──TLS(encrypted)───>│ Servidor TLS │
│ recep_tls.py │  Puerto 6662        │hosp_tls.py   │
└──────────────┘                    └──────────────┘
       │                                    │
       └──────────[Wireshark]───────────────┘
                      ↓
            ❌ SOLO VE BYTES ALEATORIOS
```

### Tabla Técnica Comparativa

| Aspecto | Módulo 7 | Módulo 9 |
|---------|----------|----------|
| **Puerto** | 6661 | 6662 |
| **Protocolo** | TCP puro | TCP + TLS 1.3 |
| **Cifrado** | Ninguno | AES-256-GCM |
| **Autenticación** | Ninguna | Certificado X.509 |
| **Intercepción** | ✅ Posible | ❌ Imposible |
| **Compliance GDPR** | ❌ | ✅ |
| **Compliance HIPAA** | ❌ | ✅ |
| **Multa potencial** | €20M | €0 |
| **Overhead CPU** | 0% | ~5-10% |
| **Latencia adicional** | 0 ms | ~10-20 ms (handshake inicial) |

---

## 10. 📚 Resumen Ejecutivo

### Lo Que Lograste

✅ **Generaste infraestructura PKI propia** (CA autofirmada)  
✅ **Implementaste TLS en Python** (servidor y cliente)  
✅ **Validaste cifrado con Wireshark** (forense de red)  
✅ **Cumpliste GDPR Art. 32** (cifrado de datos médicos)  
✅ **Entendiste criptografía moderna** (RSA, AES, ECDHE)  

### Transformación Técnica

```
ANTES (Módulo 7):
- Datos médicos en texto plano
- Violación GDPR/HIPAA
- Multas de €20,000,000 posibles
- Wireshark ve LEDESMA^EMANUEL

DESPUÉS (Módulo 9):
- Datos cifrados con AES-256
- Cumplimiento normativo
- Safe harbor de brechas
- Wireshark ve bytes aleatorios
```

### Próximos Pasos (Producción)

1. **Certificado de CA reconocida**
   ```bash
   # Let's Encrypt (gratis)
   certbot certonly --standalone -d hospital.example.com
   ```

2. **Llave privada con contraseña**
   ```bash
   openssl genrsa -aes256 -out hospital.key 2048
   ```

3. **Renovación automática**
   ```bash
   # Certificados expiran (365 días)
   # Configurar cron job para renovación
   ```

4. **Monitoreo de expiración**
   ```python
   # Alertar 30 días antes de expiración
   ```

---

*Última actualización: Enero 2026*  
*Módulo 9: Criptografía Aplicada - De Vulnerable a Conforme con GDPR*