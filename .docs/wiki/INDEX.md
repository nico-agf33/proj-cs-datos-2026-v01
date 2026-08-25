# INDEX — Wiki del Proyecto Integrador

## Sobre esta carpeta

Este repositorio del **Proyecto Integrador de Ciencia de Datos 2026 (UTN FRM)**
utiliza una wiki como fuente única de verdad (SoT). El ciclo de trabajo es:

```
CONTEXTO → CONSTRUIR (libre) → VERIFICAR una vez → CERRAR wiki si hay drift
```

Cada archivo de wiki tiene un **Harness Contract** y **doc_id** / **block_id**
para que un agente pueda leerlo y ejecutarlo sin ambigüedades.

## Tabla de archivos

| # | Archivo | Propósito |
|---|---------|-----------|
| 00 | [[00_gobierno_documental]] | Gobierno, reglas de bloqueo y proyección |
| 01 | [[01_alcance_funcional]] | Objetivo, capacidades, actores, limites |
| 02 | [[02_resultados_soluciones_usuario]] | Índice de promesas de resultado (RS-*) |
| 02 | [[02_resultados/RS-DAT-01]] | Dataset de precios — horizonte CURRENT |
| 02 | [[02_resultados/RS-INT-01]] | Proyecto completo de cátedra — horizon NEXT |
| 03 | [[03_arquitectura]] | Estructura del código Python |
| 04 | [[04_FL]] Índice de flujos | Descripción de flujos |
| 04 | [[04_FL/FL-DAT-01]] | Flujo de ingestión de datos |
| 05 | [[05_RF]] Índice de requerimientos | Requerimientos funcionales y no funcionales |
| 05 | [[05_RF/RF-DAT-01]] | CLI de ingestión — flag, aceptancia |
| 06 | [[06_modelo_datos]] | Modelo de datos — entidad Listing (20 campos) |
| 07 | [[07_pruebas]] | Índice de planes de prueba |
| 07 | [[07_pruebas/TP-DAT-01]] | Plan de pruebas del CLI de ingestión |
| 18 | [[18_ciclo_ae]] | Explicación humana del ciclo AE local |
| ae  | [[.docs/ae/repo-policy.yaml]] | Política AE (machine-readable) |
| ae  | `.docs/ae/cierre-rs-dat-01.md` | Cierre AE-lite de RS-DAT-01 (estático) |

## Políticas AE

| Archivo | Rol |
|---------|-----|
| [[AGENTS.md]] | Política operativa para agentes (inglés) |
| [[CLAUDE.md]] | Espejo twin de AGENTS.md (inglés) |
| [[PATHS.md]] | Mapa de caminos canon del repo (inglés) |

## Cómo comenzar

1. Leer `00_gobierno_documental` para entender las reglas del repo.
2. Leer `01_alcance_funcional` para entender el contexto y las limitaciones.
3. Ver RS-DAT-01 (horizonte CURRENT).
4. Revisar `18_ciclo_ae` para entender cómo se trabaja.
5. Consultar `AGENTS.md` / `CLAUDE.md` para las reglas de ejecución.