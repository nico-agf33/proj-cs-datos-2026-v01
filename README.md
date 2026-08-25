# Ciencia de Datos 2026 

## Principios del Dataset

* **Tidy Data:** 1 vehículo publicado = 1 fila.
* **Datos en vivo:** la utilidad consulta las fuentes en tiempo real, reflejando variaciones de stock y precios de mercado.
* **Riqueza técnica:** extracción de atributos de ingeniería como potencia, tracción, motor y consumo para una valoración más precisa.

---

## Capacidades Actuales

### Ingestión Híbrida y Masiva

* **Carone (Alta Fidelidad):** consulta directa a su **API GraphQL**. Provee datos técnicos profesionales de fichas de fábrica y constituye la fuente primaria por su velocidad y precisión.
* **DeRuedas (Volumen de Mercado):** scraping de microdatos **Schema.org** y parsing de HTML. Es la fuente principal para capturar la realidad del mercado de vehículos usados y la dispersión de precios, especialmente en la región de Cuyo.

### Normalización Automática

El módulo `normalize.py` garantiza la consistencia entre las diferentes fuentes:

* **Precios:** detección automática de moneda (`USD` / `ARS`) mediante el análisis del texto renderizado.
* **Motorización:** conversión de cilindrada de `cc` a litros (ejemplo: `1600` → `1.6 lts`).
* **Consumo:** estandarización del formato a `lts / 100 km`.
* **Limpieza:** eliminación de acentos y caracteres especiales.
* **Kilometraje y potencia:** normalización a valores numéricos (`int` / `float`).

---

## Instalación y Setup

### Requisitos

* **Python 3.11+**
* Dependencias:

  * `pandas`
  * `requests`
  * `beautifulsoup4`
  * `lxml`

### Instalación

Compatible con **Linux, macOS y Windows**.

```bash
git clone https://github.com/nico-agf33/proj-cs-datos-2026.git
cd proj-cs-datos-2026

python3 -m venv .venv
source .venv/bin/activate

# En Windows:
# .venv\Scripts\activate

pip install -r requirements.txt
```

---

## Uso de la Utilidad

El proyecto ofrece dos interfaces de línea de comandos (CLI).

### 1. Ingesta Específica (`collect.py`)

Permite capturar modelos puntuales y validar los datos técnicos obtenidos.

| Flag        | Obligatorio | Descripción                                                          |
| ----------- | :---------: | -------------------------------------------------------------------- |
| `--marca`   |    **Sí**   | Marca del vehículo.                                                  |
| `--modelo`  |    **Sí**   | Modelo del vehículo.                                                 |
| `--limit`   |      No     | Máximo de registros por fuente. Default: `50`.                       |
| `--sources` |      No     | Fuentes a consultar: `deruedas`, `carone` o `both`. Default: `both`. |

#### Ejemplo

```bash
python3 -m src.ingest.collect \
    --marca BMW \
    --modelo "Serie 1" \
    --limit 10
```

---

### 2. Ingesta Masiva y Dinámica (`download.py`)

El proceso descubre marcas automáticamente y segmenta las búsquedas para evitar alcanzar los límites de los servidores de las fuentes consultadas.

#### Ejemplo

Descarga automatizada de registros únicos combinando ambas fuentes (limite 10000):

```bash
python3 -m src.ingest.download \
    --total 10000 \
    --source both
```

---

## Esquema de Datos — Features

El dataset exporta las siguientes columnas críticas para el modelo de tasación:

| Columna        | Descripción                                           |
| -------------- | ----------------------------------------------------- |
| `source`       | Portal de origen (`deruedas` / `carone`).             |
| `make`         | Marca normalizada.                                    |
| `model`        | Modelo normalizado.                                   |
| `year`         | Año de fabricación.                                   |
| `mileage`      | Kilometraje numérico.                                 |
| `price`        | Valor numérico original.                              |
| `currency`     | Moneda detectada (`USD` / `ARS`).                     |
| `engine`       | Cilindrada expresada en litros (ej.: `1.6 lts`).      |
| `power_hp`     | Potencia en caballos de fuerza.                       |
| `transmission` | Tipo de caja (`Manual` / `Automática`).               |
| `traction`     | Tipo de tracción (`Delantera`, `Trasera`, `4x4`).     |
| `fuel_type`    | Tipo de combustible (`Nafta`, `Diesel`, `Eléctrico`). |
| `consumption`  | Consumo promedio normalizado.                         |
| `location`     | Provincia o localidad del aviso.                      |
| `url`          | Enlace a la ficha pública original.                   |
| `collected_at` | Timestamp de la captura en formato ISO UTC.           |

---

## Salida de Datos

Los archivos generados se almacenan en:

```text
data/raw/
```

Esta carpeta se encuentra excluida de Git mediante `.gitignore`.

El pipeline genera tres tipos principales de archivos:

### CSV

Dataset estructurado y preparado para su utilización con **Pandas** y las etapas posteriores de análisis.

```text
{marca}_{modelo}_{YYYYMMDD}.csv
```

### JSONL

Respaldo de los objetos crudos obtenidos durante la ingesta.

```text
{marca}_{modelo}_{YYYYMMDD}.jsonl
```

### META.json

Archivo con estadísticas y metadatos de la ejecución, incluyendo:

* Cantidad total de filas.
* Cantidad de marcas procesadas.
* Cantidad de errores.
* Información general de la ejecución.

```text
{marca}_{modelo}_{YYYYMMDD}_meta.json
```
