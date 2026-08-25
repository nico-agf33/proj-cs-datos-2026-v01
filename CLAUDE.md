# CLAUDE.md — proyecto-integrador-frmutn

> **Authority**: local wiki, especially `.docs/wiki/02_resultados/RS-DAT-01.md`, plus this file.
> **Language**: English for this file. Wiki and course docs are Spanish.
> Self-contained AE-lite. No external kernel.

## North Star Cycle

Wiki is the only source of truth.

1. **Context** — read `.docs/wiki/00_gobierno_documental.md`, `01_alcance_funcional.md`, CURRENT RS, architecture, FL/RF. Use `rg` / Read. mi-lsp is optional and never required.
2. **Build** — gate-free. Implement the whole goal. Do not run test suites mid-build.
3. **IMPLEMENTATION_COMPLETE** — parent only, when the file inventory for the goal is done.
4. **Verify once** — one FINAL_VERIFY. Default oracle: `python -m src.ingest.collect --help`.
5. **Wiki close** — edit wiki only if promises, flows, or flags drifted.

## Chief of Staff

The principal session routes. It does not silently become a long implementer.

- Principal: intent, priority, bounded leaves, join, decide.
- Leaves: read/edit inside allowed paths; report paths only; no test suites; no push; no inventing RS-INT-01.
- Join ≠ FINAL_VERIFY. One writer per cwd.
- FAST default: 1–few reversible files may be done inline.
- Tracker mode: none. Git + wiki own the workflow. No Linear.

## CURRENT vs HOLD

- CURRENT: `RS-DAT-01` (public tidy listings, rent + sale, province/zone).
- HOLD / NEXT: `RS-INT-01`. Research question is **SIN LOCK**. Do not invent it.

## Repo rules

- Python under `src/`. Ingest CLI: `python -m src.ingest.collect`.
- Wiki: `.docs/wiki/`. Course notes: `docs/`.
- Never commit `.env` or `.env.*`.
- Never persist DNI, phones, emails, full chats, or private Casita data.
- One listing = one row. A failed source must not abort the other sources.

## FINAL_VERIFY

```text
python -m src.ingest.collect --help
```

Live downloads are optional and only when the operator asks.

## Completion

Handoff does not authorize commit, push, merge, or delete. Operator publishes.

---

**Version**: CLAUDE.md (AE-lite, self-contained)
**Status**: Twin of AGENTS.md
**Source**: local wiki + this file (not generated from an external kernel)
