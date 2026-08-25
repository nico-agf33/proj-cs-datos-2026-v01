# FL-DAT-01 — Ingestión de avisos

## Harness Contract

```toon
id: FL-DAT-01
kind: flow
audience: dual
imports: [RS-DAT-01, WIKI-03-ARQUITECTURA]
exports: [RF-DAT-01]
agent_must_read: [this file, src/ingest/collect.py]
agent_may_edit: [steps]
agent_must_not_edit: [RS-INT-01]
verify: ["file exists", "steps match collect.py"]
stop_if: ["single source failure aborts whole run"]
evidence: src/ingest/collect.py
```

```toon
doc:
  doc_id: wiki-04-fl-dat-01
  source_protocol: SDD-WIKI-SOURCE-v1
  harness_protocol: SDD-HARNESS-v1
  audience: dual
block:
  block_id: fl-dat-01-steps
  kind: flow
  id: FL-DAT-01
  trigger: python -m src.ingest.collect
  on_source_error: continue
  steps:
    - cli_parse
    - resolve_province
    - search_each_source
    - normalize_rows
    - filter_zona
    - write_jsonl_csv_meta
```

## Pasos

1. CLI parsea `--operacion`, `--provincia`, `--zona`, `--limit`, `--sources`, `--output`.
2. `resolve_province` traduce la provincia a IDs de API (`bna_id`, `bna_label`, `remax_code`).
3. Cada fuente en `--sources` corre `search`. Si falla, se registra y se sigue.
4. Filas al schema Listing (sin contactos).
5. Si `--zona` no está vacío, `filter_by_geo`.
6. Escritura JSONL + CSV (pandas o stdlib) + `_meta.json` en `--output`.
