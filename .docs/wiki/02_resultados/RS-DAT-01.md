# RS-DAT-01 — Dataset tidy de precios de alquiler y compra

## Harness Contract

```toon
id: RS-DAT-01
kind: outcome
audience: dual
imports: [WIKI-00-GOBIERNO, WIKI-01-ALCANCE, WIKI-02-RESULTADOS]
exports: [FL-DAT-01, RF-DAT-01, WIKI-03-ARQUITECTURA]
agent_must_read: [this file, .docs/wiki/01_alcance_funcional.md]
agent_may_edit: [criterio_exito, evidencia]
agent_must_not_edit: [pregunta_integrador, datos_privados]
verify: ["file exists", "doc_id present", "block_id present", "horizon CURRENT"]
stop_if: ["private data", "invented research question", "manual captcha in documented run"]
evidence: data/raw/*_meta.json
```

```toon
doc:
  doc_id: wiki-02-resultados-rs-dat-01
  source_protocol: SDD-WIKI-SOURCE-v1
  harness_protocol: SDD-HARNESS-v1
  audience: dual
block:
  block_id: rs-dat-01-promesa
  kind: outcome
  source_of_truth: this-toon
  id: RS-DAT-01
  status: vigente
  horizon: CURRENT
  promise: dataset tidy de avisos de alquiler y venta en Argentina, filtrable por provincia y zona, sin intervencion humana y sin datos privados
```

## Promesa de solución

El grupo obtiene un **dataset público y tidy** de avisos inmobiliarios de
alquiler y de venta en Argentina. Cada fila es un aviso. Se puede filtrar por
provincia y, opcionalmente, por zona. La descarga corre sin intervención humana.

## Usuario / actor

Integrante del grupo (estudiante) y agente que ejecuta el CLI de ingestión.

## Problema que resuelve

Sin un dataset automático, la Entrega 1 no existe: no hay pipeline, no hay
filas para explorar ni modelar. Datos privados o captcha manual rompen el
criterio 4 de la cátedra.

## Resultado observable

```toon
block_id: rs-dat-01-observable
kind: acceptance
command: python -m src.ingest.collect --operacion alquiler --provincia Mendoza
writes:
  - data/raw/alquiler_mendoza_YYYYMMDD.jsonl
  - data/raw/alquiler_mendoza_YYYYMMDD.csv
  - data/raw/alquiler_mendoza_YYYYMMDD_meta.json
unit: 1 aviso = 1 fila
```

Correr `python -m src.ingest.collect --operacion alquiler --provincia Mendoza`
escribe JSONL, CSV (pandas o `csv` de la stdlib) y meta en `data/raw/`. Una
línea = un aviso.

## Criterio de éxito

```toon
block_id: rs-dat-01-exito
kind: success-criteria
required_fields: [price, operation, province, source]
forbidden_in_rows: [email, telefono, dni, whatsapp]
sources_current: [inmoup, bna, remax]
```

Cada fila tiene `price`, `operation`, `province` y `source` cuando el portal
los publica. No hay emails ni teléfonos persistidos.

## No-resultados / límites

- No hay modelo de precio en este RS.
- Zonaprop / Argenprop / Playwright no forman parte de este RS.
- No se copian datos de Casita ni de personas.
- La pregunta de cátedra no se lockea acá.

## must_not_ship_if

- Datos privados en `data/` o en el código.
- Pregunta de investigación inventada por el agente.
- Corrida documentada que exige captcha o login humano.

## Trazabilidad esperada

- FL: [[04_FL/FL-DAT-01]]
- RF: [[05_RF/RF-DAT-01]]
- Arquitectura: [[03_arquitectura]]
- TP: [[07_pruebas/TP-DAT-01]]
- UX: no aplica
- Validación: meta.json de una corrida (local, `data/raw/` gitignored)
- Handoff: Entrega 1 cátedra (02/09/2026)
- Cierre AE-lite: `.docs/ae/cierre-rs-dat-01.md`

## Evidencia

```toon
block_id: rs-dat-01-evidencia
kind: evidence
source_of_truth: this-toon
final_verify: "python -m src.ingest.collect --help"
live_meta_policy: gitignored
live_meta_local: data/raw/*_meta.json
live_meta_published: false
notes:
  - "FINAL_VERIFY del ciclo es el oracle estático --help"
  - "corridas vivas locales 2026-08-22 existen en data/raw/ pero no se versionan"
  - "BNA alquiler en 0 es esperado (portal de crédito hipotecario)"
```

## Estado

`vigente` · horizonte `CURRENT` · ciclo AE-lite cerrado en estático (ver `.docs/ae/cierre-rs-dat-01.md`)
