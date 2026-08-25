# TP-DAT-01 — Plan de Pruebas: CLI de ingestión

## Harness Contract

```toon
id: TP-DAT-01
kind: TP
audience: llm-first
imports: [RF-DAT-01, RS-DAT-01, WIKI-06-MODELO-DATOS]
exports: []
agent_must_read: [this file, src/ingest/collect.py, src/ingest/schema.py]
agent_may_edit: [casos]
agent_must_not_edit: [RS-INT-01, forbidden_in_rows]
verify:
  - "python -m src.ingest.collect --help"
stop_if:
  - "caso TP requiere descarga real sin autorización del operador"
  - "caso TP persiste datos privados (email, telefono, dni, whatsapp)"
evidence: src/ingest/collect.py
```

```toon
doc:
  doc_id: wiki-07-pruebas-tp-dat-01
  source_protocol: SDD-WIKI-SOURCE-v1
  harness_protocol: SDD-HARNESS-v1
  audience: llm-first
```

## Alcance

Cubre **RF-DAT-01** (CLI de ingestión) y los criterios de éxito de **RS-DAT-01**.
Oracle base: `python -m src.ingest.collect --help` (sin descarga real).
Las pruebas de descarga real son **opcionales** y solo se ejecutan si el operador las autoriza explícitamente.

## Casos de prueba

```toon
block:
  block_id: tp-dat-01-casos
  kind: validation
  source_of_truth: this-toon
  links:
    imports:
      - [[05_RF/RF-DAT-01]]
      - [[02_resultados/RS-DAT-01]]
      - [[06_modelo_datos]]
  records:
    - id: TP-DAT-01-HELP
      status: ready
      description: "El CLI expone --help con todos los flags documentados en RF-DAT-01"
      type: static
      command: "python -m src.ingest.collect --help"
      expect:
        - "--operacion aparece en la salida"
        - "--provincia aparece en la salida"
        - "--zona aparece en la salida"
        - "--limit aparece en la salida"
        - "--sources aparece en la salida"
        - "--output aparece en la salida"
      no_network: true
      evidence: src/ingest/collect.py

    - id: TP-DAT-01-OP-REQUIRED
      status: ready
      description: "Falla con error si --operacion está ausente"
      type: static
      command: "python -m src.ingest.collect --provincia Mendoza"
      expect:
        - "salida con código de error distinto de 0 o mensaje de argumento requerido"
      no_network: true
      evidence: src/ingest/collect.py

    - id: TP-DAT-01-PROV-REQUIRED
      status: ready
      description: "Falla con error si --provincia está ausente"
      type: static
      command: "python -m src.ingest.collect --operacion alquiler"
      expect:
        - "salida con código de error distinto de 0 o mensaje de argumento requerido"
      no_network: true
      evidence: src/ingest/collect.py

    - id: TP-DAT-01-OP-INVALID
      status: ready
      description: "Rechaza un valor de --operacion que no sea venta ni alquiler"
      type: static
      command: "python -m src.ingest.collect --operacion renta --provincia Mendoza"
      expect:
        - "salida con código de error distinto de 0 o mensaje de valor inválido"
      no_network: true
      evidence: src/ingest/collect.py

    - id: TP-DAT-01-LISTING-SCHEMA
      status: ready
      description: "La clase Listing tiene exactamente los 20 campos definidos en schema.py"
      type: static
      command: "rg 'class Listing' src/ingest/schema.py"
      expect:
        - "source, source_listing_id, operation, property_type, title, province, locality, zone, address_hint, lat, lon, price, currency, total_m2, covered_m2, bedrooms, bathrooms, garage, url, collected_at"
      no_network: true
      evidence: src/ingest/schema.py

    - id: TP-DAT-01-PRIVACY
      status: ready
      description: "Ningún campo de Listing acepta o persiste email, telefono, dni, whatsapp"
      type: static
      command: "rg 'email|telefono|dni|whatsapp' src/ingest/schema.py"
      expect:
        - "sin coincidencias en campos del dataclass Listing"
      no_network: true
      evidence: src/ingest/schema.py

    - id: TP-DAT-01-SOURCE-ISOLATION
      status: optional
      description: "Un source que falla no aborta la corrida de los demás sources"
      type: live
      requires_operator_auth: true
      command: "python -m src.ingest.collect --operacion alquiler --provincia Mendoza --sources fuente_invalida,inmoup --limit 2"
      expect:
        - "la corrida termina sin excepción no capturada"
        - "el error del source inválido aparece registrado en meta.json"
        - "los resultados de inmoup se escriben normalmente"
      no_network: false
      evidence: src/ingest/collect.py

    - id: TP-DAT-01-OUTPUT-FILES
      status: optional
      description: "Una corrida válida escribe JSONL, CSV y _meta.json en data/raw/"
      type: live
      requires_operator_auth: true
      command: "python -m src.ingest.collect --operacion alquiler --provincia Mendoza --limit 2"
      expect:
        - "data/raw/alquiler_mendoza_YYYYMMDD.jsonl existe y tiene al menos una línea"
        - "data/raw/alquiler_mendoza_YYYYMMDD_meta.json existe"
        - "ninguna fila contiene email, telefono, dni ni whatsapp"
        - "cada fila tiene source, operation, province distintos de null"
      no_network: false
      evidence: src/ingest/collect.py
```

## Matriz de trazabilidad

> Tabla de referencia humana. La fuente de verdad normativa está en el bloque `toon` de casos.

| TP ID | RF cubierto | Tipo | Red requerida |
|-------|-------------|------|---------------|
| TP-DAT-01-HELP | RF-DAT-01 | static | No |
| TP-DAT-01-OP-REQUIRED | RF-DAT-01 | static | No |
| TP-DAT-01-PROV-REQUIRED | RF-DAT-01 | static | No |
| TP-DAT-01-OP-INVALID | RF-DAT-01 | static | No |
| TP-DAT-01-LISTING-SCHEMA | RF-DAT-01 / 06 | static | No |
| TP-DAT-01-PRIVACY | RS-DAT-01 / 06 | static | No |
| TP-DAT-01-SOURCE-ISOLATION | RF-DAT-01 | live (opcional) | Sí |
| TP-DAT-01-OUTPUT-FILES | RS-DAT-01 / RF-DAT-01 | live (opcional) | Sí |

```toon
block:
  block_id: tp-dat-01-traceability
  kind: mapping
  source_of_truth: this-toon
  coverage:
    RF-DAT-01:
      static_cases: [TP-DAT-01-HELP, TP-DAT-01-OP-REQUIRED, TP-DAT-01-PROV-REQUIRED, TP-DAT-01-OP-INVALID]
      live_cases_optional: [TP-DAT-01-SOURCE-ISOLATION, TP-DAT-01-OUTPUT-FILES]
    RS-DAT-01:
      static_cases: [TP-DAT-01-LISTING-SCHEMA, TP-DAT-01-PRIVACY]
      live_cases_optional: [TP-DAT-01-OUTPUT-FILES]
    wiki-06-modelo-datos:
      static_cases: [TP-DAT-01-LISTING-SCHEMA, TP-DAT-01-PRIVACY]
```
