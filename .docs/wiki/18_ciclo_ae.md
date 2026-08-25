# 18. Ciclo AE local (sin kernel externo)

## Harness Contract

```toon
id: WIKI-18-CICLO-AE
kind: policy-human
audience: dual
imports: [WIKI-00-GOBIERNO]
exports: []
agent_must_read: [this file, AGENTS.md]
agent_may_edit: [examples]
agent_must_not_edit: [RS-DAT-01]
verify: ["file exists", "points to AGENTS.md"]
stop_if: ["external kernel required"]
evidence: AGENTS.md
```

```toon
doc:
  doc_id: wiki-18-ciclo-ae
  source_protocol: SDD-WIKI-SOURCE-v1
  harness_protocol: SDD-HARNESS-v1
  audience: dual
block:
  block_id: ciclo-ae-lite
  kind: cycle
  steps: [contexto, construir, verificar, cerrar]
```

## Qué es

Ciclo de trabajo **dentro de este repo**. No hace falta kernel externo,
mi-lsp ni Linear. Las reglas operativas están en `AGENTS.md` y `CLAUDE.md`.

## Pasos

1. **Contexto** — leer `00`, `01`, el RS CURRENT (`RS-DAT-01`), arquitectura y FL/RF.
2. **Construir** — implementar sin correr test suites a mitad de camino.
3. **Verificar una vez** — `python -m src.ingest.collect --help` (o la corrida
   acotada que pida el RS).
4. **Cerrar wiki** — solo si el código cambió una promesa o un flujo.

## Horizonte

- CURRENT: [[02_resultados/RS-DAT-01]]
- NEXT/HOLD: [[02_resultados/RS-INT-01]] hasta que el grupo lockee la pregunta.

## No hacer

- Inventar la pregunta.
- Pedir un kernel de otro repo.
- Subir `.env`, DNI, teléfonos o chats privados.
