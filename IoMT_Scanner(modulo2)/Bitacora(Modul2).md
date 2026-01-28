# 📋 Bitácora IoMT Scanner - Módulo 2
## Proyecto de Ciberseguridad en Dispositivos Médicos IoT

---

## 1. 🏥 El Quirófano Digital: Entornos Virtuales (venv)

Antes de escribir una sola línea de código, aprendiste la regla de oro del desarrollo en Linux: **No contaminar el sistema operativo**.

### El Problema
Instalar librerías con `sudo pip install` puede romper herramientas de Fedora (como `dnf` o `firewalld`) si las versiones entran en conflicto.

### La Solución
Crear un **Entorno Virtual** (una caja de arena aislada).

### Comandos Clave

```bash
# 1. Crear el entorno llamado "venv"
python3 -m venv venv

# 2. Activar el entorno (Entrar en la Matrix)
source venv/bin/activate

# 3. Instalar librerías SOLO dentro del entorno

pip install python-nmap
```

> **Lección:** Todo proyecto de seguridad debe tener su propio entorno para ser portable y seguro.

---

## 2. 🎯 Script 1: El Radar (`radar.py`)

**Concepto:** Escaneo de Red Automatizado  
**Misión:** Replicar el comando `nmap -sn` pero controlado por software para procesar los datos.

### 🧠 Lógica del Código

- **Importar Nmap:** Usamos `python-nmap` como un "control remoto" para el motor de Nmap instalado en el sistema.
- **Definir Objetivo:** `192.168.1.0/24` (Tu red local).
- **Argumentos de Escaneo:** `-sn` (Ping Scan). Solo queremos saber quién está vivo, no escanear puertos (aún).
- **Extracción de Datos:** Iteramos sobre la lista de hosts para sacar IP, MAC y Fabricante.

### ⚠️ El Reto de los Privilegios (Root)

Descubriste que para leer la **MAC Address** (que es la huella digital física del dispositivo), Nmap necesita acceso directo al hardware de red.

| Situación | Comando | Resultado |
|-----------|---------|-----------|
| ❌ Error Común | `python radar.py` | Falla, no ve las MACs |
| ⚠️ Error Peligroso | `sudo python radar.py` | Usa el Python del sistema, no tiene las librerías |
| ✅ Solución | `sudo ./venv/bin/python radar.py` | Invoca el Python del entorno virtual con permisos de superusuario |

```bash
sudo ./venv/bin/python radar.py
```

---

## 3. 🛡️ Script 2: El Vigilante (`vigilante.py`)

**Concepto:** Sistema de Detección de Intrusos (IDS) Básico / Control de Acceso a la Red (NAC)  
**Misión:** Detectar anomalías temporales (dispositivos nuevos que no deberían estar ahí).

### 🧠 Arquitectura del Software

Este script introduce el concepto de **Persistencia de Datos** y **Línea Base (Baseline)**.

#### Base de Datos (Memoria)
Usamos un archivo `whitelist.json` para que el script "recuerde" qué dispositivos son amigos.

#### Modo Entrenamiento (Baseline)
- Si el archivo JSON no existe → Asume que la red es segura ahora mismo.
- Guarda todos los dispositivos actuales en el archivo.

#### Modo Patrulla (Detection)
- Escanea la red de nuevo.
- Compara cada MAC encontrada con la lista del JSON.
- **Lógica:** Si `MAC_DETECTADA` no está en `WHITELIST` → ¡ALERTA!

### 🚨 Caso de Estudio: El Falso Positivo

Durante tu prueba, el sistema lanzó una alerta de **3 Intrusos**.

**Causa:** Tu dispositivo Xiaomi (.65) y otros celulares estaban "dormidos" o desconectados durante el entrenamiento, pero aparecieron en el segundo escaneo.

> **Lección IoMT:** En un hospital, los dispositivos médicos se mueven y se apagan. Un sistema de seguridad rígido genera muchas falsas alarmas. El mantenimiento de la "Lista Blanca" es una tarea crítica.

---

## 4. 🔐 Conceptos Clave de Ciberseguridad Aprendidos

| Concepto | Explicación | Aplicación en Alemania |
|----------|-------------|------------------------|
| **Shadow IT** | Dispositivos conectados sin permiso (tu cámara TP-Link, los celulares). | Tu script permite detectar qué enfermero conectó su celular personal a la red de monitores cardíacos. |
| **MAC Address** | La cédula de identidad del hardware. | Usamos la MAC y no la IP para identificar intrusos, porque la IP cambia (DHCP), pero la MAC suele ser fija. |
| **MAC Randomization** | Dispositivos que cambian su MAC para privacidad. | Vimos celulares que aparecen como "Unknown" o cambian de identidad, complicando el rastreo. |
| **Privilege Escalation** | Ejecución con `sudo`. | Entendiste que para "ver" a bajo nivel (Capa 2 del modelo OSI), necesitas permisos de root. |

---

*Última actualización: Enero 2026*