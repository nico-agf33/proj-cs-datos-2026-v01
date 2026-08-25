import logging
import argparse
import pandas as pd
import json
from pathlib import Path
from datetime import datetime, timezone
from .collectors import deruedas, carone

# Configuración de logging profesional
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s [%(levelname)s]: %(message)s"
)
logger = logging.getLogger("pipeline")

def main():
    parser = argparse.ArgumentParser(description="Pipeline de Ingestión Masiva para Tasador de Vehículos.")
    parser.add_argument("--total", type=int, default=10000, help="Meta total de registros únicos")
    parser.add_argument("--source", type=str, default="both", choices=["deruedas", "carone", "both"], help="Fuente a usar")
    parser.add_argument("--output-dir", default="data/raw")
    args = parser.parse_args()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    filename_base = f"dataset_full_{args.source}_{timestamp}"
    csv_path = out_dir / f"{filename_base}.csv"
    jsonl_path = out_dir / f"{filename_base}.jsonl"

    # Determinar qué colectores ejecutar
    sources_to_process = []
    if args.source == "both":
        sources_to_process = [deruedas, carone]
    elif args.source == "deruedas":
        sources_to_process = [deruedas]
    else:
        sources_to_process = [carone]

    all_data = []
    seen_ids = set()

    for src in sources_to_process:
        if len(all_data) >= args.total:
            break
        
        src_name = src.__name__.split('.')[-1].upper()
        logger.info(f"--- INICIANDO CAPTURA DESDE {src_name} ---")
        
        # 1. Intentar descubrimiento dinámico de marcas
        marcas = src.get_available_brands()
        
        if not marcas:
            logger.warning(f"[{src_name}] No se detectaron marcas individuales. Usando BÚSQUEDA GLOBAL.")
            # Al poner [None], el bucle de abajo se ejecutará una vez con marca=None
            marcas = [None]
        else:
            logger.info(f"[{src_name}] Se detectaron {len(marcas)} marcas disponibles.")

        # 2. Bucle de recolección
        for marca in marcas:
            if len(all_data) >= args.total:
                break
            
            faltantes = args.total - len(all_data)
            msg_marca = marca if marca else "GLOBAL"
            logger.info(f"[PIPELINE] Fuente: {src_name} | Segmento: {msg_marca} | Progreso: {len(all_data)}/{args.total}")
            
            # Llamada al collector (ambos aceptan marca=None para feed global)
            lote = src.search(marca=marca, limit=min(1500, faltantes))
            
            if lote:
                for item in lote:
                    # Deduplicación en tiempo real por ID original
                    if item['source_listing_id'] not in seen_ids:
                        all_data.append(item)
                        seen_ids.add(item['source_listing_id'])
                
                # 3. Guardado Incremental (Resiliencia ante cortes)
                if all_data:
                    df_temp = pd.DataFrame(all_data)
                    df_temp.to_csv(csv_path, index=False, encoding="utf-8")
                    
                    # Exportar también a JSONL como backup de crudos
                    with open(jsonl_path, "w", encoding="utf-8") as f:
                        for row in all_data:
                            f.write(json.dumps(row, ensure_ascii=False) + "\n")
                            
                    logger.info(f"[HITO] {len(all_data)} registros únicos guardados en disco.")
            else:
                logger.debug(f"[{src_name}] Sin resultados para {msg_marca}")

    # 4. Resumen final y metadatos
    logger.info(f"\n=== PROCESO FINALIZADO ===")
    logger.info(f"Total registros únicos obtenidos: {len(all_data)}")
    
    meta_path = out_dir / f"{filename_base}_meta.json"
    meta_info = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_registros": len(all_data),
        "fuentes_solicitadas": args.source,
        "limite_seteado": args.total
    }
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta_info, f, indent=4)

if __name__ == "__main__":
    main()