# Cierre AE-lite — RS-DAT-01

Paquete único de cierre (`only_publish` / `single_closure_packet`).
FAST same-repo, tracker none, sin kernel externo. No se acuñan IDs `D-*`.
No se crea `24_negocio`. No se inventa `RS-INT-01`.

```toon
doc:
  doc_id: ae-cierre-rs-dat-01
  audience: dual
block:
  block_id: cierre-rs-dat-01
  kind: closure
  rs: RS-DAT-01
  horizon: CURRENT
  completion_profile: full_cycle_to_origin_main
  implementation_complete: true
  goal_phase: FINAL_VERIFY
  verify_packet:
    mode: collapsed_fast
    oracle: "python -m src.ingest.collect --help"
  learning_pass: skipped_fast
  anti_hold:
    hold_emitted: false
    forbidden_holds_avoided:
      - ask_user_to_merge
      - remember_wiki_close
      - remember_trazabilidad
  branch_disposition: integrate-main
  remotes:
    origin: git@github.com:fgpaz/proyecto-integrador-frmutn-.git
    equipo_untouched: true
```

## IMPLEMENTATION_COMPLETE

Inventario del goal CURRENT (`RS-DAT-01`):

| Path | Rol |
|------|-----|
| `src/ingest/collect.py` | CLI; CSV con pandas o stdlib |
| `src/ingest/schema.py` | Entidad Listing (20 campos) |
| `src/ingest/provinces.py` | `bna_id`, `bna_label`, `remax_code` |
| `src/ingest/collectors/remax.py` | `_extract_items` (wrapper anidado) |
| `src/ingest/collectors/bna.py` | label de +Hogares vía `bna_label` |
| `tests/test_remax_collector.py` | Regresión del wrapper Remax |
| `.docs/wiki/06_modelo_datos.md` | Modelo Listing |
| `.docs/wiki/07_pruebas.md` | Índice TP |
| `.docs/wiki/07_pruebas/TP-DAT-01.md` | Plan de pruebas |
| `.docs/wiki/04_FL/FL-DAT-01.md` | Flujo (CSV siempre) |
| `.docs/wiki/03_arquitectura.md` | Módulos + `bna_label` |
| `.docs/wiki/02_resultados/RS-DAT-01.md` | Promesa + evidencia de cierre |

## packet_vs_diff

```toon
block_id: packet-vs-diff
kind: evidence
verdict: PASS
compare: working-tree vs wiki CURRENT
covered:
  - Remax _extract_items + tests (ya en origin/main a379767)
  - wiki 06 / 07 / TP-DAT-01 (ya en origin/main)
  - leftover: provinces bna_label + remax_code CABA/BA/Córdoba
  - leftover: BNA usa bna_label
  - leftover: CSV sin pandas
  - leftover: README cobertura Remax
  - wiki-close: CSV ya no es "si hay pandas"; FL y arquitectura alineados
not_in_diff:
  - RS-INT-01 (HOLD, sin lock)
  - data/raw (gitignored)
stale: false
```

Historias `main` y `fix/remax-wrapped-listings-and-wiki-dat-01` son
**no relacionadas**. No se mergea la feature: contaminaría `origin/main`
con el historial de `equipo/master`. El trabajo útil ya está en `main`
(mismos blobs) y el leftover se integra por commit en `main`.

## Conformidad FAST (sin ps-trazabilidad STANDARD)

`18_ciclo_ae` no exige `crear-conformidad-solucion` ni IDs `D-*`.
Este bloque es la traza colapsada RS → FL → RF → TP → código.

| Ancla | Estado |
|-------|--------|
| Promesa RS-DAT-01 (dataset tidy alquiler+venta, provincia/zona, sin PII) | Conformante en contrato y CLI |
| FL-DAT-01 pasos = `collect.py` | Conformante tras wiki-close CSV |
| RF-DAT-01 flags = `--help` | A verificar en FINAL_VERIFY |
| TP-DAT-01 casos estáticos | Oracle `--help` + schema/privacy |
| TP-DAT-01 live | Opcional; meta local no versionada |
| Listing 20 campos / `forbidden_in_rows` | Conformante (`schema.py`) |
| Sources inmoup, bna, remax | Conformante; Remax sin `remax_code` salta |
| Un source fallido no aborta | Contrato en CLI; live opcional |

## FINAL_VERIFY

Única ola. Oracle:

```text
python -m src.ingest.collect --help
```

**Resultado (esta sesión):** `PASS` · exit `0` · flags
`--operacion`, `--provincia`, `--zona`, `--limit`, `--sources`, `--output`
presentes. Regresión Remax: `tests/test_remax_collector.py` · 7 passed
(no es FINAL_VERIFY; gate de `finishing-a-development-branch`).

No se relanza descarga viva en este cierre. Ya hay `data/raw/*_20260822_meta.json`
locales (gitignored). No se publican.

## HOLD / no cerrado

| Ítem | Por qué |
|------|---------|
| `RS-INT-01` | Horizonte NEXT. Pregunta **SIN LOCK**. El agente no la inventa. |
| TP-DAT-01-SOURCE-ISOLATION | Live; exige autorización de operador. |
| TP-DAT-01-OUTPUT-FILES | Live; meta local existe pero no se versiona. |
| Push a `equipo` | Operador sin write; remoto prohibido en este ciclo. |
| Guard `Invoke-PrePushGuard.ps1` | No existe en este repo AE-lite; N/A. |

`hold_emitted: false` para el ciclo CURRENT estático. Los HOLD de arriba
son horizonte / evidencia viva no contratada / remoto ajeno, no HOLDs
mecánicos prohibidos por `ae-close`.

## Routing

`handoff_ready` → `finishing-a-development-branch` con
`branch_disposition: integrate-main`.

- Base: `main` (default de `origin`).
- Push: `git push origin main`. Nunca `equipo`. Nunca force.
- Cleanup: no mergear ni borrar ramas de `equipo`. La feature local/origin
  queda **superseded** (historial ajeno); se puede borrar en `origin` del
  fork si el push a `main` confirma wiki 06/07 + Remax + este cierre.
