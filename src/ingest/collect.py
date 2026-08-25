#!/usr/bin/env python3
"""CLI de ingestión para Dataset de Vehículos (DeRuedas + Carone)."""

import argparse
import csv
import json
import logging
import sys
from pathlib import Path
from datetime import datetime, timezone
from .collectors import deruedas, carone
from .normalize import _slug

# Configuración de logging
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s [%(levelname)s]: %(message)s"
)
logger = logging.getLogger("collect")

def main():
    parser = argparse.ArgumentParser(description="Colector de datos de Autos para Ciencia de Datos.")
    parser.add_argument("--marca", required=True, help="Marca del vehículo (ej: Ford)")
    parser.add_argument("--modelo", required=True, help="Modelo del vehículo (ej: Fiesta)")
    parser.add_argument("--limit", type=int, default=50, help="Límite de avisos por fuente (default: 50)")
    parser.add_argument("--output", default="data/raw", help="Directorio de salida (default: data/raw)")
    parser.add_argument("--sources", default="deruedas,carone", help="Fuentes a consultar separadas por coma")
    
    args = parser.parse_args()
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    sources_to_run = [s.strip().lower() for s in args.sources.split(",")]
    all_items = []
    
    logger.info(f"Iniciando descarga para: {args.marca} {args.modelo} (Límite: {args.limit} por fuente)")

    # 1. Ejecutar DeRuedas
    if "deruedas" in sources_to_run:
        try:
            logger.info("[collect] Consultando DeRuedas...")
            dr_items = deruedas.search(args.marca, args.modelo, args.limit)
            all_items.extend(dr_items)
            logger.info(f"[collect] DeRuedas aportó {len(dr_items)} avisos.")
        except Exception as e:
            logger.error(f"[collect] Error en DeRuedas: {e}")

    # 2. Ejecutar Carone
    if "carone" in sources_to_run:
        try:
            logger.info("[collect] Consultando Carone...")
            ca_items = carone.search(args.marca, args.modelo, args.limit)
            all_items.extend(ca_items)
            logger.info(f"[collect] Carone aportó {len(ca_items)} avisos.")
        except Exception as e:
            logger.error(f"[collect] Error en Carone: {e}")

    if not all_items:
        logger.warning("No se obtuvieron resultados de ninguna fuente.")
        return

    # 3. Guardado de archivos
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d")
    marca_slug = _slug(args.marca)
    modelo_slug = _slug(args.modelo)
    base_filename = f"{marca_slug}_{modelo_slug}_{timestamp}"

    # --- Exportar CSV ---
    csv_path = output_dir / f"{base_filename}.csv"
    # Usamos las llaves del primer elemento para las columnas
    fieldnames = all_items[0].keys()
    
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_items)
    
    # --- Exportar JSONL (Opcional, para redundancia) ---
    jsonl_path = output_dir / f"{base_filename}.jsonl"
    with open(jsonl_path, "w", encoding="utf-8") as f:
        for item in all_items:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    # --- Exportar Meta ---
    meta_path = output_dir / f"{base_filename}_meta.json"
    meta_data = {
        "marca": args.marca,
        "modelo": args.modelo,
        "total_filas": len(all_items),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "sources": sources_to_run
    }
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta_data, f, indent=2)

    logger.info(f"Dataset generado exitosamente: {csv_path} ({len(all_items)} filas totales)")

if __name__ == "__main__":
    main()