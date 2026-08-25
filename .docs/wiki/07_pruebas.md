# 07. Pruebas

## Harness Contract

```toon
id: WIKI-07-PRUEBAS
kind: test-index
audience: llm-first
imports: [RF-DAT-01, WIKI-06-MODELO-DATOS]
exports: [TP-DAT-01]
agent_must_read: [this file]
agent_may_edit: [index]
agent_must_not_edit: [RS-INT-01]
verify: ["file exists", "TP-DAT-01 entry present"]
stop_if: ["TP references non-existent RF"]
evidence: .docs/wiki/07_pruebas/TP-DAT-01.md
```

```toon
doc:
  doc_id: wiki-07-pruebas-index
  source_protocol: SDD-WIKI-SOURCE-v1
  harness_protocol: SDD-HARNESS-v1
  audience: llm-first
```

## Índice de planes de prueba

> Tabla de referencia humana. La fuente de verdad de cada TP está en su archivo individual.

| ID | Archivo | RF cubiertos | Estado |
|----|---------|--------------|--------|
| TP-DAT-01 | [[07_pruebas/TP-DAT-01]] | RF-DAT-01 | ready |

```toon
block:
  block_id: pruebas-index
  kind: index
  source_of_truth: this-toon
  plans:
    - id: TP-DAT-01
      path: .docs/wiki/07_pruebas/TP-DAT-01.md
      covers: [RF-DAT-01]
      status: ready
      oracle: "python -m src.ingest.collect --help"
```
