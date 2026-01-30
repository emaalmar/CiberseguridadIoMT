import nmap
import sys

# 1. Configuración del Objetivo
# Cambia esto si tu red no es 192.168.1.0/24
target_network = "192.168.1.0/24"

print(f"--- Iniciando Escaneo IoMT en {target_network} ---")
print("Espere un momento, esto puede tardar unos segundos...")

# 2. Inicializar el Escáner
nm = nmap.PortScanner()

try:
    # 3. Ejecutar el Escaneo (Equivalente a nmap -sn)
    # arguments='-sn' significa "Ping Scan" (solo ver quién está vivo)
    nm.scan(hosts=target_network, arguments='-sn')

except nmap.PortScannerError:
    print("Error: No se encontró nmap. ¿Lo instalaste con dnf?")
    sys.exit(0)
except:
    print("Error inesperado:", sys.exc_info()[0])
    sys.exit(0)

# 4. Procesar y Mostrar Resultados
# nm.all_hosts() devuelve una lista de todas las IPs encontradas
hosts_found = nm.all_hosts()

print(f"\nDispositivos detectados: {len(hosts_found)}")
print("-" * 40)
print(f"{'IP':<20} {'MAC Address':<20} {'Fabricante'}")
print("-" * 40)

for host in hosts_found:
    try:
        # Intentamos obtener la MAC y el Fabricante
        # Nota: Esto solo funciona si corres el script con SUDO
        if 'mac' in nm[host]['addresses']:
            mac = nm[host]['addresses']['mac']
            vendor = nm[host]['vendor'].get(mac, "Desconocido")
        else:
            mac = "Desconocido/Local"
            vendor = "-"

        print(f"{host:<20} {mac:<20} {vendor}")

    except Exception as e:
        print(f"{host:<20} Error al leer datos")

print("-" * 40)
print("Escaneo finalizado.")