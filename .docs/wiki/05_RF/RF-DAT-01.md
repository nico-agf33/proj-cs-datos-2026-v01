# RF-DAT-01 — CLI de ingestión

## Harness Contract

```toon
id: RF-DAT-01
kind: requirement
audience: dual
imports: [FL-DAT-01, RS-DAT-01]
exports: []
agent_must_read: [this file, src/ingest/collect.py]
agent_may_edit: [flags]
agent_must_not_edit: [RS-INT-01]
verify: ["python -m src.ingest.collect --help"]
stop_if: ["required flag missing", "unknown operation value"]
evidence: src/ingest/collect.py
```

```toon
doc:
  doc_id: wiki-05-rf-dat-01
  source_protocol: SDD-WIKI-SOURCE-v1
  harness_protocol: SDD-HARNESS-v1
  audience: dual
block:
  block_id: rf-dat-01-flags
  kind: requirement
  id: RF-DAT-01
  entry: python -m src.ingest.collect
  flags:
    operacion: {required: true, values: [venta, alquiler]}
    provincia: {required: true, type: string}
    zona: {required: false, default: ""}
    limit: {required: false, default: 200, type: int}
    sources: {required: false, default: "inmoup,bna,remax"}
    output: {required: false, default: data/raw}
```

## Aceptancia

- `--operacion` solo `venta` o `alquiler`.
- `--provincia` obligatorio.
- `--zona` opcional; vacío = sin filtro post-descarga.
- `--limit` máximo por collector.
- `--sources` lista separada por comas.
- `--output` directorio de crudos.
- Un source con error no aborta el resto.
