# Proyecto Integrador — Ciencia de Datos 2026  
## Tasación de Vehículos

Este repositorio contiene la infraestructura de **Ingeniería de Datos** para el Proyecto Integrador de la cátedra de **Ciencia de Datos 2026 (UTN FRM)**.

El objetivo principal es la construcción de un **pipeline automatizado** que recolecta, estandariza y exporta datos técnicos y precios de vehículos (usados y 0 km) en Argentina, para alimentar un futuro sistema de **tasación automatizada**.

### Estructura del dataset

El dataset sigue el principio de **Tidy Data**:

> **1 vehículo = 1 fila**

Los registros contienen atributos técnicos y comerciales relevantes para el futuro modelo de tasación.

---

## 🚀 Capacidades actuales

### Ingestión híbrida

- **V6:** extracción de objetos JSON (Next.js) para obtener especificaciones técnicas de alta precisión:
  - Torque
  - Potencia (HP)
  - Consumo

- **DeRuedas:** scraping de microdatos **Schema.org** para capturar información del mercado de vehículos usados.

### Normalización

Limpieza y estandarización de variables críticas:

- Kilometraje → entero
- Potencia → `float`
- Unificación de monedas

### Exportación

Generación de archivos en:

- CSV
- JSONL
- Metadatos de la corrida

---

## 🛠️ Requisitos y setup

### Requisitos

- **Python 3.11+**
- `requests`
- `beautifulsoup4`
- `lxml`
- `pandas`

### Instalación — Linux / macOS

```bash
git clone https://github.com/nico-agf33/proj-cs-datos-2026.git
cd proj-cs-datos-2026

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
```

### Instalación — Windows

Abrir **PowerShell** y ejecutar:

```powershell
git clone https://github.com/nico-agf33/proj-cs-datos-2026.git
cd proj-cs-datos-2026

python -m venv .venv
.venv\Scripts\activate

pip install -r requirements.txt
```

---

## 📊 Uso del CLI — Ingesta

La obtención de datos se realiza mediante **flags de línea de comandos**. No se requiere interfaz gráfica.

| Flag | Obligatorio | Descripción |
|---|:---:|---|
| `--marca` | **Sí** | Marca del vehículo. Ej.: `Ford`, `Fiat`, `BMW` |
| `--modelo` | **Sí** | Modelo del vehículo. Ej.: `Cronos`, `Mustang` |
| `--limit` | No | Máximo de avisos a recolectar por fuente. Default: `50` |
| `--sources` | No | Fuentes a consultar: `deruedas`, `v6`. Default: ambas |
| `--output` | No | Directorio para archivos crudos. Default: `data/raw` |

### Ejemplos de ejecución

#### Recolectar datos para un Ford Fiesta

```bash
python3 -m src.ingest.collect \
    --marca Ford \
    --modelo "Fiesta Kinetic Design"
```

#### Recolectar 100 avisos de Fiat Cronos solamente desde DeRuedas

```bash
python3 -m src.ingest.collect \
    --marca Fiat \
    --modelo Cronos \
    --limit 100 \
    --sources deruedas
```

---

## 📋 Esquema de datos — Features

El dataset generado incluye las siguientes columnas fundamentales para el modelo de tasación:

| Columna | Descripción |
|---|---|
| `source` | Portal de origen (`deruedas` o `v6`) |
| `make` | Marca del vehículo |
| `model` | Modelo |
| `version` | Versión específica o trim |
| `year` | Año de fabricación |
| `mileage` | Kilometraje (numérico) |
| `price` | Precio de venta (limpio) |
| `currency` | Moneda (`ARS` o `USD`) |
| `power_hp` | Potencia en caballos de fuerza |
| `torque_nm` | Torque en Newton-metro |
| `transmission` | Tipo de caja (`Manual` / `Automática`) |
| `traction` | Tipo de tracción (`Delantera`, `Trasera`, `Integral`) |
| `fuel_type` | Tipo de combustible |
| `location` | Ubicación geográfica del aviso |
| `url` | Enlace a la ficha pública |
| `collected_at` | Timestamp de la descarga (ISO UTC) |

---

## 📁 Salida de datos

Los archivos se generan en:

```text
data/raw/
```

Esta carpeta está excluida de Git mediante `.gitignore`.

Para cada corrida se generan los siguientes archivos:

### Dataset CSV

```text
{marca}_{modelo}_{YYYYMMDD}.csv
```

Dataset listo para ser utilizado con **Pandas**.

### Datos crudos JSONL

```text
{marca}_{modelo}_{YYYYMMDD}.jsonl
```

Registro de objetos crudos obtenidos durante la ingesta.

### Metadatos

```text
{marca}_{modelo}_{YYYYMMDD}_meta.json
```

Contiene los metadatos de la corrida, incluyendo:

- Cantidad de filas
- Cantidad de errores
- Información de la ejecución

---

## 📅 Cronograma del proyecto

| Entrega | Fecha | Hito |
|---|---:|---|
| Definición | 12/08/2026 | Pregunta de investigación y grupo |
| **Entrega 1** | **02/09/2026** | **Ingeniería de Datos — Pipeline** |
| Entrega 2 | 16/09/2026 | Análisis Exploratorio — EDA |
| Entrega 3 | 14/10/2026 | Modelado Predictivo — Tasador |
| Entrega 4 | 04/11/2026 | Visualización e Integración Final |

---

## 👥 Equipo

**Equipo:** A definir

**Cátedra:** Ciencia de Datos 2026 — UTN FRM

---

## 📌 Estado del proyecto

Actualmente el proyecto se encuentra enfocado en la etapa de **Ingeniería de Datos**, con el objetivo de completar el pipeline de recolección, normalización y exportación para la **Entrega 1 — 02/09/2026**.