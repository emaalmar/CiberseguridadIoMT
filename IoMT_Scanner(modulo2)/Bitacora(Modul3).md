# 🏥 Bitácora de Entrenamiento: Ingeniería de Datos Médicos (Módulo 3)

## Objetivo
Comprender la estructura de archivos médicos (DICOM), los riesgos de privacidad (GDPR) y aplicar técnicas de anonimización mediante programación.

**Herramientas:** Python 3, Librería `pydicom`, Entornos Virtuales

---

## 1. 📚 Fundamentos Teóricos: ¿Qué es DICOM?

Aprendiste que en un hospital, las imágenes no son simples fotos (`.jpg`). El estándar mundial es **DICOM** (Digital Imaging and Communications in Medicine).

### La Estructura: Un archivo `.dcm` es un contenedor híbrido

| Componente | Descripción |
|------------|-------------|
| **Header (Cabecera)** | Contiene metadatos de texto (Nombre, ID, Fecha, Dosis de radiación, Médico tratante) |
| **Pixel Data (Cuerpo)** | La imagen médica en sí (Rayos X, resonancia, etc.) |

### El Riesgo

Si envías una radiografía por correo, estás enviando también los datos personales del paciente incrustados. Esto viola las leyes de privacidad (como la **GDPR en Alemania**).


---

## 2. 🛠️ Gestión de Entornos (Troubleshooting)

### El Incidente
A mitad del ejercicio, cambiaste el nombre de la carpeta del proyecto de `IoMT_Scanner` a `IoMT_Scanner(modulo2)`.

### El Error
```
bad interpreter: .../venv/bin/python3: datei oder Verzeichnis nicht gefunden
```

### La Causa
Los entornos virtuales (`venv`) en Linux guardan la **ruta absoluta** (dirección completa) donde fueron creados. Si mueves o renombras la carpeta padre, el entorno se rompe porque sigue buscando la dirección vieja.

### La Solución

```bash
# 1. Borrar la carpeta rota
rm -rf venv

# 2. Crear uno nuevo
python3 -m venv venv

# 3. Reinstalar librerías
./venv/bin/pip install pydicom
```


---

## 3. 🏨 Script A: El Cirujano de Datos (`medico.py`)

**Misión:** Simular un software de privacidad que recibe datos crudos y los "limpia".

### Lógica del Código

#### 1. Ingestión
Carga un archivo DICOM real usando `pydicom.dcmread()`.

#### 2. Lectura de Tags
Accedemos a etiquetas específicas usando sus nombres estándar:

```python
dataset.PatientName    # Nombre
dataset.PatientID      # Cédula/ID
```

#### 3. Anonimización (La Operación)
Sobrescribimos los valores en memoria:

```python
dataset.PatientName = "ANONIMO_001"
dataset.PatientID = "123456"
```

#### 4. Exportación
Guardamos el resultado en un archivo nuevo (`paciente_anonimo.dcm`), dejando el original intacto (No destructivo).


---

## 4. 🔍 Script B: El Auditor de Calidad (`auditor.py`)

**Misión:** Verificar automáticamente que el proceso anterior funcionó (Quality Assurance).

### Lógica del Código

#### 1. Verificación Cruzada
Abre el archivo generado (`paciente_anonimo.dcm`).

#### 2. Comparación Lógica

```python
if dataset.PatientName == "ANONIMO_001":
    print("✅ PASA")
else:
    print("❌ FALLA")
```

#### 3. Resultado
Obtuviste el ✅ **CHECK VERDE**, confirmando que el archivo es seguro para ser compartido sin revelar la identidad del paciente.


---

## 5. 📋 Resumen de Comandos de Ejecución

Como estamos trabajando en un entorno virtual pero a veces necesitamos permisos de sistema, la sintaxis exacta que usamos fue:

```bash
# Para instalar librerías en el entorno virtual
./venv/bin/pip install pydicom

# Para ejecutar scripts usando el Python del entorno virtual
sudo ./venv/bin/python medico.py
sudo ./venv/bin/python auditor.py
```

> **Nota:** Usamos `sudo` cuando necesitamos permisos de sistema, pero invocamos explícitamente el Python del entorno virtual (`./venv/bin/python`) para asegurar que tiene acceso a las librerías instaladas.

---

*Última actualización: Enero 2026*