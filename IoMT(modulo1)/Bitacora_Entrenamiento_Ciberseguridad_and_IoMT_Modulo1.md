Bitácora de Entrenamiento: Ciberseguridad & IoMT (Módulo 1)

Objetivo: Transición de estudiante de ingeniería a Auditor de Seguridad en Salud. Entorno: Fedora Linux (KDE Plasma).

1. Análisis de Tráfico (El Oído)
Herramienta: Wireshark Misión: Entender la diferencia entre tráfico seguro e inseguro en un hospital.

Concepto Clave:

HTTP: Tráfico en texto plano. En IoMT, permite ver contraseñas y datos de pacientes.

TLS/HTTPS: Tráfico cifrado (aparece como "Application Data" ilegible). Es el estándar obligatorio.

Protocolos "Ruidosos" Detectados:

SSDP / mDNS: Dispositivos anunciándose. Un riesgo de privacidad en redes públicas.

ARP: Protocolo ciego de red (vulnerable a Spoofing).

2. Hardening / Defensa de Host (El Escudo) 🛡️
Herramientas: ss, firewalld Misión: Blindar la estación de trabajo (Fedora) para operar en redes hostiles.

Diagnóstico
Comando: sudo ss -tuln

Hallazgo: Puertos abiertos críticos (1716 KDE Connect, 5353 mDNS) expuestos a toda la red (0.0.0.0).

Implementación del Firewall
Estrategia: Mover interfaces de la zona de confianza (FedoraWorkstation) a la zona restrictiva (public).

Comandos Ejecutados:

Bash
# Ver zonas activas
firewall-cmd --get-active-zones

# Mover interfaces (Cable y Wi-Fi) a zona pública
sudo firewall-cmd --zone=public --change-interface=eno1
sudo firewall-cmd --zone=public --change-interface=wlo1

# Cerrar servicios innecesarios en zona pública
sudo firewall-cmd --zone=public --remove-service=mdns
sudo firewall-cmd --zone=public --remove-service=ssh

# Hacer cambios permanentes (Sobrevivir al reinicio)
sudo firewall-cmd --runtime-to-permanent
Resultado: La PC rechaza todas las conexiones entrantes no solicitadas. "Invisible" en la red.

3. Reconocimiento de Red (El Sonar) 📡
Herramienta: Nmap Misión: Descubrir y auditar dispositivos "Shadow IT" (dispositivos no autorizados) en la red.

Fase A: Descubrimiento (Ping Scan)
Comando: sudo nmap -sn 192.168.1.0/24

Resultado: Lista de IPs activas. Detección de fabricantes mediante MAC Address.

Fase B: Identificación (Fingerprinting)
Comando: sudo nmap -sV -O <IP>

Objetivo: Identificar SO y servicios.

Hallazgo (Caso Real):

Cámara TP-Link detectada por su certificado SSL y puertos abiertos.

Puerto 554 (RTSP - Video).

Puerto 2020 (ONVIF/gSOAP).

Fase C: Evasión de Bloqueos
Comando: sudo nmap -Pn <IP>

Situación: Dispositivos (como celulares) que no responden al Ping.

Lección: MACs aleatorias (F2:xx...) en móviles modernos protegen la privacidad.

4. Auditoría de Vulnerabilidades (El Médico) 🩺
Herramienta: Nmap Scripting Engine (NSE) Misión: Verificar si un dispositivo tiene fallos de seguridad conocidos (CVEs).

Comando: sudo nmap --script vuln <IP>

Resultado (Caso Real): La cámara TP-Link no mostró vulnerabilidades críticas conocidas (como Devil's Ivy), indicando un firmware actualizado.
