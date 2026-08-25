# RS-INT-01 — Proyecto Integrador de cátedra (HOLD)

## Harness Contract

```toon
id: RS-INT-01
kind: outcome
audience: dual
imports: [WIKI-00-GOBIERNO, WIKI-01-ALCANCE, WIKI-02-RESULTADOS]
exports: []
agent_must_read: [this file]
agent_may_edit: [estado, pregunta_lock]
agent_must_not_edit: [pregunta_texto]
verify: ["file exists", "doc_id present", "horizon HOLD or NEXT"]
stop_if: ["agent invents the research question", "private data"]
evidence: docs/pregunta-y-fuente.md
```

```toon
doc:
  doc_id: wiki-02-resultados-rs-int-01
  source_protocol: SDD-WIKI-SOURCE-v1
  harness_protocol: SDD-HARNESS-v1
  audience: dual
block:
  block_id: rs-int-01-promesa
  kind: outcome
  source_of_truth: this-toon
  id: RS-INT-01
  status: hold
  horizon: NEXT
  pregunta: SIN LOCK
  promise: el grupo entrega el ciclo completo de ciencia de datos de la materia
```

## Promesa de solución

El grupo recorre el ciclo de la materia: datos, exploración, modelo,
visualización y demo. **La pregunta sigue SIN LOCK.** El agente no la inventa.

## Usuario / actor

Grupo de 5 a 6 estudiantes. Docente valida pregunta y fuente.

## Problema que resuelve

La cátedra pide un proyecto de punta a punta (50 % de la nota). Sin pregunta
y fuente validadas, el resto de entregas no tiene ancla.

## Resultado observable

Cuando el grupo lockee la pregunta (una frase + unidad + URL de fuente) y el
docente la valide, este RS pasa de HOLD a vigente. Hasta entonces no hay
resultado observable de modelado ni de app.

## Criterio de éxito (cátedra)

```toon
block_id: rs-int-01-entregas
kind: schedule
definition: 2026-08-12
entrega_1: 2026-09-02
entrega_2: 2026-09-16
entrega_3: 2026-10-14
entrega_4: 2026-11-04
expo: 2026-11-18
recuperacion: 2026-11-25
```

Entregas 1–4 más exposición el 18/11/2026. Aprobación 60 %.

## No-resultados / límites

- El agente no escribe la pregunta.
- Este RS no autoriza implementación de modelo ni de app.
- CURRENT sigue siendo [[02_resultados/RS-DAT-01]].

## must_not_ship_if

- Pregunta inventada.
- Fuente que falle un eliminatorio (tidy, unidad, modelable, descarga automática).
- Datos privados.

## Trazabilidad esperada

- FL / RF / TP / UX: se crean **después** del lock de pregunta.
- Validación: formulario de cátedra.
- Handoff: exposición 18/11/2026.

## Estado

`hold` · horizonte `NEXT` · pregunta `SIN LOCK`
