# 03. Arquitectura

## Harness Contract

```toon
id: WIKI-03-ARQUITECTURA
kind: architecture
audience: dual
imports: [WIKI-01-ALCANCE, RS-DAT-01]
exports: [FL-DAT-01, RF-DAT-01]
agent_must_read: [this file, src/ingest/collect.py]
agent_may_edit: [module_map]
agent_must_not_edit: [RS-INT-01]
verify: ["file exists", "doc_id present", "python layout matches src/"]
stop_if: ["prisma", "next.js", "external kernel"]
evidence: src/ingest/
```

```toon
doc:
  doc_id: wiki-03-arquitectura
  source_protocol: SDD-WIKI-SOURCE-v1
  harness_protocol: SDD-HARNESS-v1
  audience: dual
block:
  block_id: arch-python-layout
  kind: architecture
  source_of_truth: this-toon
  runtime: python
  entry: python -m src.ingest.collect
```

## Decisión

Stack **Python** para ingestión. No hay Prisma, Next.js ni kernel externo.
`data/raw/` está en `.gitignore`. Notebooks, modelos y app quedan para RS-INT-01.

## Módulos CURRENT

```toon
block_id: arch-modules
kind: module-map
src_ingest:
  schema.py: Listing 1 aviso = 1 fila
  normalize.py: precios AR, strip_contact, filter_by_geo
  provinces.py: INDEC bna_id, bna_label (+Hogares) y remax_code
  collectors/inmoup.py: POST API
  collectors/bna.py: GET API
  collectors/remax.py: GET API
  collect.py: CLI orquestador
  download.py: stub URL genérica
data:
  raw: gitignored
  interim: gitignored
  processed: gitignored
  samples: muestras pequeñas
later: [notebooks/, src/models/, src/viz/, app/]
```

## Límites

Un collector que falle no corta la corrida. Contactos se recortan. Sin secretos
en el repo.
