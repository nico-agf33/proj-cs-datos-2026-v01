# PATHS.md — canonical paths

English map of this repo. Wiki prose stays in Spanish.

## Product / course

- Course notes: `docs/`
- Wiki (source of truth): `.docs/wiki/`
- Wiki index: `.docs/wiki/INDEX.md`
- Governance: `.docs/wiki/00_gobierno_documental.md`
- Scope: `.docs/wiki/01_alcance_funcional.md`
- Outcomes index: `.docs/wiki/02_resultados_soluciones_usuario.md`
- CURRENT outcome: `.docs/wiki/02_resultados/RS-DAT-01.md`
- HOLD outcome: `.docs/wiki/02_resultados/RS-INT-01.md`
- Architecture: `.docs/wiki/03_arquitectura.md`
- Flows: `.docs/wiki/04_FL.md`, `.docs/wiki/04_FL/FL-DAT-01.md`
- Requirements: `.docs/wiki/05_RF.md`, `.docs/wiki/05_RF/RF-DAT-01.md`
- AE cycle (human, Spanish): `.docs/wiki/18_ciclo_ae.md`
- Repo policy: `.docs/ae/repo-policy.yaml`

## Code

- Ingest CLI: `src/ingest/collect.py`
- Collectors: `src/ingest/collectors/`
- Schema: `src/ingest/schema.py`
- Raw data (gitignored): `data/raw/`

## Agent policy

- `AGENTS.md`
- `CLAUDE.md`
- this file

## Do not edit as product

- `.env`, `.env.*`
- `.git/`
- `__pycache__/`
- `.pi-subagents/`
