import logging
import argparse
import pandas as pd
from pathlib import Path
from datetime import datetime
from .collectors import deruedas, carone

logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s [%(levelname)s]: %(message)s"
)
logger = logging.getLogger("pipeline")

def main():
    parser = argparse.ArgumentParser(description="Pipeline Masivo Dinámico.")
    parser.add_argument("--total", type=int, default=20000, help="Meta de registros")
    parser.add_argument("--source", type=str, default="deruedas", choices=["deruedas", "carone", "both"], help="Fuente a usar")
    parser.add_argument("--output-dir", default="data/raw")
    args = parser.parse_args()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    filename = out_dir / f"dataset_full_{args.source}_{timestamp}.csv"

    sources_to_process = []
    if args.source == "both":
        sources_to_process = [deruedas, carone]
    elif args.source == "deruedas":
        sources_to_process = [deruedas]
    else:
        sources_to_process = [carone]

    all_data = []

    for src in sources_to_process:
        if len(all_data) >= args.total: break
        
        src_name = src.__name__.split('.')[-1]
        logger.info(f"--- Iniciando captura desde {src_name.upper()} ---")
        
        # Descubrimiento dinámico de marcas
        marcas = src.get_available_brands()
        logger.info(f"Se detectaron {len(marcas)} marcas en {src_name}.")

        for marca in marcas:
            if len(all_data) >= args.total: break
            
            faltantes = args.total - len(all_data)
            logger.info(f"[PIPELINE] Fuente: {src_name} | Marca: {marca} | Total: {len(all_data)}/{args.total}")
            
            # Buscamos en la fuente (deruedas o carone)
            lote = src.search(marca=marca, limit=min(1200, faltantes))
            
            if lote:
                all_data.extend(lote)
                # Guardado incremental y deduplicación
                df_temp = pd.DataFrame(all_data).drop_duplicates(subset=['source_listing_id'])
                df_temp.to_csv(filename, index=False, encoding="utf-8")
                logger.info(f"[HITO] {len(df_temp)} registros únicos guardados.")

    logger.info(f"=== PROCESO FINALIZADO: {len(all_data)} registros obtenidos ===")

if __name__ == "__main__":
    main()