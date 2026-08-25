# 02. Resultados y soluciones de usuario

## Harness Contract

```toon
id: WIKI-02-RESULTADOS
kind: outcomes
audience: dual
imports: [WIKI-00-GOBIERNO, WIKI-01-ALCANCE]
exports: [outcomes, RS-DAT-01, RS-INT-01]
agent_must_read: [this file]
agent_may_edit: [horizon, index]
agent_must_not_edit: [individual RS-* bodies]
verify: ["file exists", "doc_id present", "block_id present"]
stop_if: ["missing governance", "invented research question", "private data"]
evidence: .docs/wiki/INDEX.md
```

## Índice de RS-*

| ID | Promesa | Estado | Horizonte |
|----|---------|--------|-----------|
| [[RS-DAT-01]] | Dataset tidy de precios de alquiler y compra | vigente | CURRENT |
| [[RS-INT-01]] | Proyecto completo de cátedra | hold | NEXT |

## RS-DAT-01: Dataset de precios

Promesa vigente. Ver `[[02_resultados/RS-DAT-01]]` para el detalle completo:
problema, resultado observable, criterio de éxito, limites.

## RS-INT-01: Proyecto Integrador de cátedra

Proyecto pendiente de la pregunta. Ver `[[02_resultados/RS-INT-01]]`.

## Criterio de paso de horizonte

- **CURRENT**: RS-DAT-01 activo, trabajo en ingest de datos.
- **NEXT**: RS-INT-01 se mueve a vigente cuando el grupo valida la pregunta y
  fuente con el docente. Se mantiene como HOLD hasta entonces.
- **HOLD**: todo lo que no sea CURRENT ni NEXT (futuro lejano).