Bitácora de Ciberseguridad: Network Forensics (Módulo 8)
Objetivo Estratégico: Validar la confidencialidad (o falta de ella) en la transmisión de datos HL7 mediante interceptación de paquetes (Packet Sniffing).

1. El Hallazgo (Vulnerabilidad Confirmada)
Acción: Se utilizó tcpdump y Wireshark para capturar tráfico en el puerto 6661 de la interfaz Loopback.

Evidencia: Mediante la función "Follow TCP Stream", se reconstruyó la conversación completa entre el Recepcionista y el Servidor.

Resultado: Los datos PII (Personally Identifiable Information) como Patient Name e ID viajaron en texto plano (Cleartext).

Riesgo: Crítico. Violación directa de la DSGVO (Alemania) y HIPAA (EE. UU.). Cualquier actor en la ruta de red (Man-in-the-Middle) tiene acceso total a los datos médicos.

🚦 El Cruce de Caminos
Emanuel, has completado la fase de "Ataque y Diagnóstico".

Construiste la red.

Atacaste el PACS (API Dump).

Interceptaste el tráfico HL7 (Sniffing).

❯ sudo tcpdump -i lo -A port 6661
[sudo] Passwort für ema: 
dropped privs to tcpdump
tcpdump: verbose output suppressed, use -v[v]... for full protocol decode
listening on lo, link-type EN10MB (Ethernet), snapshot length 262144 bytes
15:35:16.931253 IP localhost.54736 > localhost.6661: Flags [S], seq 3440894431, win 65495, options [mss 65495,sackOK,TS val 1807568894 ecr 0,nop,wscale 10], length 0
E..<Z.@.@............................0.........
k.O........

15:35:16.931280 IP localhost.6661 > localhost.54736: Flags [S.], seq 937805281, ack 3440894432, win 65483, options [mss 65495,sackOK,TS val 1807568894 ecr 1807568894,nop,wscale 10], length 0
E..<..@.@.<.............7............0.........
k.O.k.O....



 sudo ./venv/bin/python hospital_server.py
[sudo] Passwort für ema: 
--- MOTOR DE INTEGRACIÓN PYTHON (HL7 LISTENER - V2 FINAL) ---
[.] Escuchando en el puerto 6661...


❯ sudo ./venv/bin/python recepcionista.py
[sudo] Passwort für ema: 
--- SISTEMA DE ADMISIÓN HOSPITALARIA (HL7 v2 + MLLP) ---
[1] Mensaje Generado: MSG-20260129153516
[2] Conectando a Mirth Connect (localhost:6661)...
 -> Datos enviados.
[3] Respuesta del Servidor:
 
 MSH|^~\&|PYTHON_SRV|LINUX|RECEPCION|HOSPITAL|MSA|AA|MSG-20260129153516260129153516|P|2.3
❯ sudo ./venv/bin/python recepcionista.py
--- SISTEMA DE ADMISIÓN HOSPITALARIA (HL7 v2 + MLLP) ---
[1] Mensaje Generado: MSG-20260129153754
[2] Conectando a Mirth Connect (localhost:6661)...
 -> Datos enviados.
[3] Respuesta del Servidor:
 
 MSH|^~\&|PYTHON_SRV|LINUX|RECEPCION|HOSPITAL|20260129153754||ACK|ACK20MSA|AA|MSG-20260129153754
✅ Transmisión Exitosa.
