# Criterios de una buena fuente de datos

Criterios oficiales del Proyecto Integrador Ciencia de Datos 2026 (UTN FRM).

## Bloque A — Criterios eliminarios

Si la fuente no cumple alguno de estos cuatro, el proyecto no llega a buen puerto.
Buscá otra fuente o ajustá tu pregunta.

### Criterio 1: Datos tidy

Cada fila es una observación. Cada columna es una variable. El nombre técnico es *tidy* — "ordenado".

**Formato no tidy (wide):**

| PERSONA | ENERO | FEBRERO | MARZO |
|---------|-------|---------|-------|
| Ana | 1500 | 1700 | 1600 |
| Bruno | 1300 | 1400 | 1450 |

_"Mes" es una variable, pero está escondida como nombre de columna._

**Formato tidy (long):**

| PERSONA | MES | VALOR |
|---------|-----|-------|
| Ana | Enero | 1500 |
| Ana | Febrero | 1700 |
| Ana | Marzo | 1600 |
| Bruno | Enero | 1300 |

_Cada fila es una observación (persona-mes). Cada columna, una variable._

### Criterio 2: Unidad de análisis alineada con la pregunta

La unidad que representa cada fila del dataset tiene que coincidir con la unidad sobre la
que querés sacar conclusiones. La granularidad se decide desde la pregunta, no desde el dataset.

**Alineadas:**
- Pregunta: ¿Qué distingue los perfiles físicos de cada posición en el fútbol?
- Unidad: jugador. Dataset: FIFA, un jugador por fila. _Match._

**Desalineadas:**
- Pregunta: ¿Qué distingue a las personas que emigran?
- Dataset: Banco Mundial, país-año por fila. La unidad país no captura decisiones individuales.

### Criterio 3: Algo modelable

En la Unidad 3 vas a construir un modelo. La fuente tiene que dar el material. Basta con que
se cumpla una de estas dos condiciones:

**Aprendizaje supervisado:** Hay una variable que querés predecir a partir de las otras.
Ej: predecir la posición del jugador desde sus atributos técnicos.

**Aprendizaje no supervisado:** Sospechás que hay grupos naturales escondidos en los datos.
Ej: agrupar jugadores en arquetipos — "delantero potente", "extremo veloz".

Un listado de museos con dirección, en cambio, no tiene qué predecir ni grupos que descubrir —
en U3 el proyecto se rompe.

### Criterio 4: Descargable de forma automatizada

En la Unidad 1 vas a construir un pipeline que baje los datos sin intervención humana.

- **Archivos por URL directa** — un CSV o JSON servido en un endpoint público.
  El caso más simple: `requests.get()` y listo.
- **APIs REST públicas** — con o sin API key, siempre que se pueda automatizar.
  Ej: Banco Mundial, GitHub, OpenWeather.
- **Páginas scrapeables** — HTML navegable con estructura estable. Aun con Cloudflare
  o JS pesado se puede, con Playwright. Es más trabajo, pero es válido.

**NO:** foto de una tabla en un PDF. Sitios con captcha manual. Bases privadas o pagas.
Apuntes propios.

## Bloque B — Criterios facilitadores

No rompen el proyecto, pero lo complican si no se cumplen.

### Criterio 5: Volumen suficiente

Con pocas filas los modelos no aprenden y las visualizaciones cuentan anécdotas.

| Rango | Eval |
|-------|------|
| < 1.000 | Insuficiente |
| 1.000 – 10.000 | Suficiente para arrancar |
| > 10.000 | Cómodo |

Si se queda corto: combinar con otra fuente relacionada por una clave común, o acotar
el alcance del modelo.

### Criterio 6: Varias columnas informativas

Al menos **5 columnas útiles**, con mezcla de tipos: numéricas, categóricas, fechas.

**Ejemplo bueno (FIFA):** 100+ atributos por jugador. Físicos (altura, peso), técnicos
(regate, pase, tiro), financieros (valor, salario), contextuales (club, liga, país).

**Contraejemplo:** habitantes por localidad — una única columna útil. No hay features
para modelar ni dimensiones para cruzar en visualizaciones.

**Salida si faltan columnas:** derivar nuevas variables desde las existentes (feature
engineering) o combinar con otra fuente por una clave común (ej: país, año, ID de jugador).

### Criterio 7: Documentación entendible

Tenés que saber qué significa cada columna, sus unidades, su origen, qué representa un
valor faltante.

**Ejemplo bueno (FIFA / sofifa):** Los atributos son estándar del videojuego y están
ampliamente documentados. Un "85 en *dribbling*" significa lo mismo en todos los jugadores.

**Contraejemplo:** CSV con columnas `col_1, col_2, col_3`. Sin diccionario ni nombres
claros. Vas a pasar más tiempo adivinando que analizando.

**Salida de emergencia:** Si no hay documentación, se puede reconstruir leyendo los
datos y consultando la fuente original. Cuesta tiempo, pero se puede — no descarta
la fuente por sí solo.

## Checklist antes de aceptar tu fuente

Si a alguna de las 4 primeras respondés "no" o "no sé", buscá otra fuente o ajustá tu pregunta.

| # | Pregunta |
|---|----------|
| 01 | ¿Cada fila representa una unidad concreta que podés nombrar en una frase? |
| 02 | ¿Esa unidad coincide con la unidad sobre la que querés sacar conclusiones? |
| 03 | ¿Hay algo que quieras predecir, o grupos que sospeches encontrar? |
| 04 | ¿La podés descargar sin intervención humana? (URL, API, scraping) |
| 05 | ¿Cuántas filas hay? (Objetivo: >1.000. Ideal: >10.000) |
| 06 | ¿Cuántas columnas útiles hay? (Objetivo: >5, con mezcla de tipos) |
| 07 | ¿Sabés qué significa cada columna? |

Los 4 primeros son eliminatorios (teal). Los 3 últimos son facilitadores solucionables
con trabajo extra (dorado).