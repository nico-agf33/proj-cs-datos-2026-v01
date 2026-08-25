# 01. Alcance funcional

## Harness Contract

```toon
id: WIKI-01-ALCANCE
kind: scope
audience: dual
imports: [WIKI-00-GOBIERNO]
exports: [scope]
agent_must_read: [this file]
agent_may_edit: [horizon, capabilities]
agent_must_not_edit: [outcomes RS-*, architecture, flows, requirements]
verify: ["file exists", "doc_id present", "block_id present"]
stop_if: ["missing governance", "invented research question", "private data"]
evidence: .docs/wiki/INDEX.md
```

## Objetivo del producto

Repositorio para el **Proyecto Integrador de Ciencia de Datos 2026** (UTN FRM,
Ingeniería en Sistemas de Información). El grupo es de 5 a 6 integrantes.
El objetivo general es recorrer el ciclo completo de ciencia de datos sobre un
problema que elige el grupo con datos que consigue el grupo: conseguir los datos,
explorarlos, modelarlos, visualizarlos y comunicar lo encontrado.

## Propuesta de valor

1. **Reproducible**: cualquier clon del repo puede obtener los datos desde APIs
   públicas sin intervención humana.
2. **Tidy**: 1 aviso = 1 fila, 1 variable = 1 columna (Criterio 1 eliminatorio).
3. **Sin datos privados**: no se persisten contactos, teléfonos, emails, DNI.
   Ningún dato de Casita, Gabriel, Jaz u otros se copia a este repo.
4. **Público y académico**: los datos provienen de portales inmobiliarios
   accesibles a cualquiera; la pregunta es decidida por los compañeros.

## Mapa de capacidades

```toon
id: CAP-MAP
kind: capability-map
audience: dual
imports: [WIKI-01-ALCANCE]
exports: [ingest, normalize, filter, collect]
agent_must_read: [this file]
agent_may_edit: [scope_items]
agent_must_not_edit: [RS-*]
verify: ["capability present", "block_id present"]
stop_if: ["invented question", "private data"]
evidence: .docs/wiki/01_alcance_funcional.md
```

| Capacidad | Estado | Descripción |
|-----------|--------|-------------|
| ingest | ACTIVA | Obtener datos de APIs públicas (InmoUp, BNA, RE/MAX) |
| normalize | ACTIVA | Convertir a schema Listing unificado |
| filter_geo | ACTIVA | Filtrar por provincia / zona post-descarga |
| collect_cli | ACTIVA | CLI que orquesta ingest → normalize → filtro → escritura |
| EDA | PENDIENTE | Análisis exploratorio, hipótesis, hallazgos |
| model | PENDIENTE | Modelo predictivo o clúster según pregunta del grupo |
| viz | PENDIENTE | Visualizaciones y app (Entrega 4) |
| expo | PENDIENTE | Exposición final 18/11/2026 |

## Actores

| Actor | Responsabilidad |
|-------|----------------|
| Estudiante (integrante del grupo) | Elige la pregunta, valida la fuente, entrega el integrador |
| Docente (cátedra) | Valida pregunta y fuente; evalúa entregas |
| Agente (Claude / Codex / Pi) | Lee wiki, ejecuta el flujo AE local (context → build → verify) |

## Áreas funcionales

### En alcance CURRENT

- Obtención de precios de alquiler y compra de avisos inmobiliarios
- APIs públicas: InmoUp, BNA Más Hogares, RE/MAX
- 1 aviso = 1 fila, tidy, sin datos privados
- Filtrado por provincia y zona
- Salida: JSONL + CSV + meta.json en `data/raw/`

### En alcance HOLD

- Definición de la pregunta del integrador (deciden los compañeros)
- Análisis exploratorio (Entrega 2)
- Modelado predictivo (Entrega 3)
- Visualización y app (Entrega 4)
- Exposición final (18/11/2026)

### Fuera de alcance

- Base de datos de Casita (datos privados, contactos)
- Secretos, tokens, credenciales de Casita
- Preguntas predictivas inventadas por el agente
- Deploy a producción
- Scraping con captcha / login humano

## Cronograma de cátedra

| Entrega | Fecha | Qué se presenta |
|---------|-------|-----------------|
| Definición | 12/08/2026 | Grupo, pregunta y fuente de datos |
| Entrega 1 — Ingeniería de datos | 02/09/2026 | Pipeline automatizado del dataset |
| Entrega 2 — Análisis exploratorio | 16/09/2026 | Exploración, hipótesis, hallazgos |
| Entrega 3 — Modelado | 14/10/2026 | Modelo predictivo / clúster, métricas |
| Entrega 4 — Visualización e integración | 04/11/2026 | Visualizaciones y app funcionando |
| Exposición final | 18/11/2026 | Presentación completa y demo en vivo |
| Recuperación | 25/11/2026 | Instancia para grupos que la necesiten |

## Nota sobre la pregunta

La **pregunta del integrador sigue SIN LOCK**. Los compañeros la definen y la
validan con el docente a través del formulario de la cátedra. El agente no
inventa preguntas ni bloquea el trabajo esperando una pregunta: el horizonte
CURRENT se centra en la capa de ingest de datos (RS-DAT-01).