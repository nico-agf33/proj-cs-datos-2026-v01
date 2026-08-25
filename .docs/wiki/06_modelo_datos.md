# 06. Modelo de Datos

## Harness Contract

```toon
id: WIKI-06-MODELO-DATOS
kind: data-model
audience: llm-first
imports: [RS-DAT-01, RF-DAT-01, WIKI-03-ARQUITECTURA]
exports: [TP-DAT-01]
agent_must_read: [this file, src/ingest/schema.py]
agent_may_edit: [listing-entity]
agent_must_not_edit: [forbidden_in_rows, RS-INT-01]
verify:
  - "rg 'class Listing' src/ingest/schema.py"
  - "python -m src.ingest.collect --help"
stop_if:
  - "campo email, telefono, dni o whatsapp presente en filas de salida"
  - "entidad nueva sin ownership explícito"
evidence: src/ingest/schema.py
```

```toon
doc:
  doc_id: wiki-06-modelo-datos-listing
  source_protocol: SDD-WIKI-SOURCE-v1
  harness_protocol: SDD-HARNESS-v1
  audience: llm-first
```

## Contexto

El modelo de datos del CURRENT (`RS-DAT-01`) es un único tipo de aviso inmobiliario: la
entidad **Listing**. No hay base de datos persistente; el almacenamiento es archivo plano
(`data/raw/*.jsonl` / `*.csv`). Sin ORM, sin Prisma, sin migraciones.

Notebooks, modelos y app quedan para RS-INT-01 (HOLD); no se anticipan aquí.

## Entidad Listing

```toon
block:
  block_id: listing-entity
  kind: record
  source_of_truth: this-toon
  classification: canonical-entity
  ownership: src/ingest
  lifecycle: write-once en tiempo de colección; nunca se edita in-place
  tenancy: archivo local por corrida; sin multi-tenant
  storage: data/raw/*.jsonl y *.csv (gitignored)
  invariants:
    - un aviso = una fila (unicidad lógica por source + source_listing_id + collected_at)
    - forbidden_in_rows: [email, telefono, dni, whatsapp]
    - price, operation, province, source deben estar presentes cuando el portal los publica (RS-DAT-01)
  links:
    imports:
      - [[02_resultados/RS-DAT-01]]
      - [[05_RF/RF-DAT-01]]
      - [[03_arquitectura]]
    exports:
      - TP-DAT-01
  records:
    - id: Listing
      status: implemented
      fields:
        owner: src/ingest/schema.py
        verify: "rg 'class Listing' src/ingest/schema.py"
        evidence: src/ingest/schema.py
```

### Campos

> Los campos siguen el orden de declaración en `src/ingest/schema.py`.
> Las columnas son referenciales para lectura humana; la fuente de verdad normativa es el bloque `toon` de cada campo a continuación.

```toon
block:
  block_id: listing-fields
  kind: record
  source_of_truth: this-toon
  fields:
    source:
      python_type: str
      required: true
      level: schema
      description: nombre del portal colector
      allowed_values: [inmoup, bna, remax, "html_…"]
      evidence: src/ingest/schema.py#L22
    source_listing_id:
      python_type: str
      required: true
      level: schema
      description: ID original asignado por el portal
      evidence: src/ingest/schema.py#L23
    operation:
      python_type: "Literal['venta', 'alquiler']"
      required: true
      level: schema
      description: tipo de operación inmobiliaria
      evidence: src/ingest/schema.py#L24
    property_type:
      python_type: "Optional[str]"
      required: false
      description: tipo de propiedad
      allowed_values: [casa, depto, terreno, local, otro]
      evidence: src/ingest/schema.py#L25
    title:
      python_type: "Optional[str]"
      required: false
      description: título del aviso tal como lo publica el portal
      evidence: src/ingest/schema.py#L26
    province:
      python_type: "Optional[str]"
      required: false
      level: schema
      business_required: true
      description: provincia; business-required según RS-DAT-01 cuando el portal la publica
      evidence: src/ingest/schema.py#L27
    locality:
      python_type: "Optional[str]"
      required: false
      description: localidad o ciudad dentro de la provincia
      evidence: src/ingest/schema.py#L28
    zone:
      python_type: "Optional[str]"
      required: false
      description: barrio o zona interna; se usa para el filtro --zona del CLI
      evidence: src/ingest/schema.py#L29
    address_hint:
      python_type: "Optional[str]"
      required: false
      description: dirección corta publicada por el portal; nunca incluye contacto personal
      forbidden_content: [email, telefono, dni, whatsapp]
      evidence: src/ingest/schema.py#L30
    lat:
      python_type: "Optional[float]"
      required: false
      description: latitud geográfica del aviso
      evidence: src/ingest/schema.py#L31
    lon:
      python_type: "Optional[float]"
      required: false
      description: longitud geográfica del aviso
      evidence: src/ingest/schema.py#L32
    price:
      python_type: "Optional[float]"
      required: false
      level: schema
      business_required: true
      description: precio numérico limpio (sin símbolo ni puntuación); business-required según RS-DAT-01
      evidence: src/ingest/schema.py#L33
    currency:
      python_type: "Optional[Literal['ARS', 'USD']]"
      required: false
      description: moneda del precio; None si el portal no la publica
      allowed_values: [ARS, USD, null]
      evidence: src/ingest/schema.py#L34
    total_m2:
      python_type: "Optional[float]"
      required: false
      description: superficie total en metros cuadrados
      evidence: src/ingest/schema.py#L35
    covered_m2:
      python_type: "Optional[float]"
      required: false
      description: superficie cubierta en metros cuadrados
      evidence: src/ingest/schema.py#L36
    bedrooms:
      python_type: "Optional[int]"
      required: false
      description: cantidad de dormitorios
      evidence: src/ingest/schema.py#L37
    bathrooms:
      python_type: "Optional[int]"
      required: false
      description: cantidad de baños
      evidence: src/ingest/schema.py#L38
    garage:
      python_type: "Optional[int]"
      required: false
      description: cajones de cochera o cantidad de garages
      evidence: src/ingest/schema.py#L39
    url:
      python_type: "Optional[str]"
      required: false
      description: URL pública de la ficha del aviso en el portal
      evidence: src/ingest/schema.py#L40
    collected_at:
      python_type: str
      required: true
      level: schema
      description: timestamp ISO-8601 UTC de colección; se auto-asigna en __post_init__
      evidence: src/ingest/schema.py#L41
```

## Invariantes de privacidad

```toon
block:
  block_id: listing-privacy
  kind: contract
  source_of_truth: this-toon
  forbidden_in_rows: [email, telefono, dni, whatsapp]
  policy: strip_contact aplica en src/ingest/normalize.py antes de escribir filas
  stop_if: any forbidden field value detected in output rows
  evidence: src/ingest/normalize.py
```

Los campos `address_hint`, `title` y `url` pasan por `strip_contact` en `normalize.py` antes de
ser persistidos. Ningún colector escribe contacto personal en una fila de Listing.

## Decisiones cerradas

```toon
block:
  block_id: listing-decisions
  kind: mapping
  source_of_truth: this-toon
  decisions:
    no_database: sin persistencia relacional; archivo plano JSONL/CSV es suficiente para RS-DAT-01
    no_update: las filas son inmutables tras la colección; no hay UPDATE ni DELETE
    no_shared_schema: cada corrida produce sus propios archivos; no hay schema compartido entre corridas
    no_rs_int_01: notebooks, modelos y app son HOLD; no se anticipan en este modelo
    derived_vs_persisted: todos los campos son directamente extraídos del portal (no derivados); zone puede derivarse de lat/lon solo si el portal no la publica (futuro RS-INT-01)
```

## Impacto en documentos downstream

```toon
block:
  block_id: listing-downstream
  kind: mapping
  source_of_truth: this-toon
  downstream:
    TP-DAT-01: debe verificar que los campos business-required (price, operation, province, source) estén presentes en corridas con datos reales; forbids email/telefono/dni/whatsapp
    RF-DAT-01: ya refleja los flags del CLI y el invariante 1 aviso = 1 fila
    09_modelo_fisico: no aplica (sin base de datos)
    10_contratos_tecnicos: no aplica (sin API externa que exija contrato de respuesta)
```
