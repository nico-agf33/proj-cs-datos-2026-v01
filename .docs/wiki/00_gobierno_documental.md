# 00. Gobierno documental

## Harness Contract

```toon
id: WIKI-00-GOBIERNO
kind: governance
audience: dual
imports: []
exports: [governance, scope, outcomes, architecture, flows, requirements]
agent_must_read: [this file]
agent_may_edit: [blocking_rules, projection]
agent_must_not_edit: [outcomes RS-*, architecture, flows, requirements]
verify: ["file exists", "doc_id present", "yaml source valid", "blocking_rules defined"]
stop_if: ["missing governance yaml", "invented research question", "private personal data"]
evidence: .docs/wiki/INDEX.md
```

## Propósito

`00_gobierno_documental.md` es la autoridad humana sobre la gobernanza de este repositorio.
Si este documento no está perfectamente claro, el trabajo spec-driven se detiene.

La wiki (esta carpeta) es la **única fuente de verdad** para este proyecto.
`AGENTS.md` y `CLAUDE.md` son políticas operativas derivadas de la wiki.
No se usa ningún kernel externo.

## Governance Source

```yaml
version: 1
profile: ordered_wiki
overlays:
  - spec_core
numbering_recommended: true
hierarchy:
  - id: governance
    label: Gobierno documental
    layer: "00"
    family: functional
    pack_stage: governance
    paths: [.docs/wiki/00_gobierno_documental.md]
  - id: scope
    label: Alcance
    layer: "01"
    family: functional
    pack_stage: context
    paths: [.docs/wiki/01_alcance_funcional.md]
  - id: outcomes
    label: Resultados
    layer: "02"
    family: functional
    pack_stage: context
    paths: [.docs/wiki/02_resultados_soluciones_usuario.md]
  - id: architecture
    label: Arquitectura
    layer: "03"
    family: technical
    pack_stage: design
    paths: [.docs/wiki/03_arquitectura.md]
  - id: flows
    label: Flujos
    layer: "04"
    family: functional
    pack_stage: design
    paths: [.docs/wiki/04_FL.md]
  - id: requirements
    label: Requerimientos
    layer: "05"
    family: functional
    pack_stage: design
    paths: [.docs/wiki/05_RF.md]
context_chain: [governance, scope, outcomes, architecture, flows, requirements]
closure_chain: [outcomes, requirements, flows]
audit_chain: [governance, outcomes]
blocking_rules:
  - missing_human_governance_doc
  - missing_governance_yaml
  - missing_rs_for_user_visible_work
  - invented_research_question
  - private_data_exposure
projection:
  output: .docs/wiki/_mi-lsp/read-model.toml
  format: toml
  auto_sync: false
  versioned: true
  required_to_work: false
```

## Autoridad canónica

- `00_gobierno_documental.md` es la autoridad humana.
- `read-model.toml` es la proyección ejecutable (opcional, no bloquea el trabajo).
- `AGENTS.md` y `CLAUDE.md` son políticas operativas derivadas (twins).
- `.docs/ae/repo-policy.yaml` es la fuente de verdad AE (machine-readable).

## Reglas de bloqueo

- Todo trabajo nuevo comienza validando que este documento exista y sea consistente.
- Si hay conflicto entre wiki y políticas AE, la wiki manda (es la SoT).
- Si la gobernanza es ambigua, invalida, incompleta o stale, el repo entra en blocked mode.
- En blocked mode solo se permite diagnóstico y reparación (crear/repair wiki).
- Nunca se inventa una pregunta de investigación ni se usa dato privado.

## Autoría

Este documento fue creado para el Proyecto Integrador de Ciencia de Datos 2026 (UTN FRM).
El grupo de 5-6 estudiantes es el dueño de las decisiones. No interviene ningún kernel
externo (ae-kernel, worker-runtime, Linear, Casita).