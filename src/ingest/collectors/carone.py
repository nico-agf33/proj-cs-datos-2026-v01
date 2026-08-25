import requests
import re
import json
import logging
import time
from datetime import datetime
from ..normalize import as_number, cc_to_liters, format_consumption_carone

logger = logging.getLogger(__name__)

_BASE = "https://carone.com.ar"
_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "x-v6-country": "ar",
    "Referer": "https://carone.com.ar/comprar?carOptions=usados"
}

def get_available_brands() -> list[str]:
    """Extrae marcas del objeto catalogFilters en el HTML."""
    url = f"{_BASE}/comprar?carOptions=usados"
    try:
        resp = requests.get(url, headers=_HEADERS, timeout=20)
        # Buscamos el patrón: "label":"MARCA","count":... "__typename":"BrandFilter"
        pattern = r'\\"label\\":\\"(.*?)\\",\\"count\\":\d+,\\"__typename\\":\\"BrandFilter\\"'
        brands = re.findall(pattern, resp.text)
        return list(dict.fromkeys([b for b in brands if b.strip()]))
    except Exception as e:
        logger.error(f"[carone] Error en marcas: {e}")
        return []

def search(marca: str = None, modelo: str = None, limit: int = 50) -> list[dict]:
    results = []
    page = 1
    seen_ids = set() # Para evitar loops infinitos
    
    # URL base corregida según el snippet
    base_url = f"{_BASE}/comprar?carOptions=usados"
    if marca:
        base_url += f"&marca={marca.replace(' ', '%20')}"

    while len(results) < limit:
        url = f"{base_url}&p={page}"
        try:
            logger.info(f"[carone] Consultando: {url}")
            resp = requests.get(url, headers=_HEADERS, timeout=15)
            resp.raise_for_status()
            
            # --- REGEX CORREGIDA: Detecta ID numérico o string ---
            # Buscamos url_key que es lo que necesitamos para ir al detalle
            keys_found = re.findall(r'\\"url_key\\":\\"(.*?)\\"', resp.text)
            unique_keys = list(dict.fromkeys(keys_found))

            if not unique_keys:
                break

            new_in_page = 0
            for key in unique_keys:
                if len(results) >= limit: break
                
                # Si ya procesamos esta URL en esta ejecución, es que p=N no está funcionando
                if key in seen_ids:
                    continue
                
                seen_ids.add(key)
                new_in_page += 1
                
                # Ir al detalle (donde están los 6 datos técnicos)
                detail_url = f"{_BASE}/comprar/usados/{key}"
                time.sleep(0.3)
                item = _scrape_detail(detail_url)
                if item:
                    results.append(item)

            if new_in_page == 0:
                logger.info(f"[carone] No hay más autos nuevos en p{page}. Fin.")
                break
                
            page += 1
            if page > 100: break # Freno de emergencia
            
        except Exception as e:
            logger.error(f"[carone] Error en p{page}: {e}")
            break
            
    return results

def _scrape_detail(url: str) -> dict | None:
    try:
        resp = requests.get(url, headers=_HEADERS, timeout=10)
        # Capturamos el objeto product completo del detalle
        pattern = r'\"product\":({.*?\"__typename\":\"SimpleProduct\"})'
        match = re.search(pattern, resp.text)
        if not match: return None
        
        data = json.loads(match.group(1).replace('\\"', '"'))
        price_info = data.get("price_range", {}).get("maximum_price", {}).get("final_price", {})
        
        return {
            "source": "carone",
            "source_listing_id": str(data.get("sku")),
            "make": data.get("carone_marca_data", {}).get("label"),
            "model": data.get("carone_modelo_data", {}).get("label"),
            "version": data.get("carone_version_description"),
            "year": int(as_number(data.get("carone_year"))),
            "mileage": int(as_number(data.get("carone_mileage"))),
            "price": as_number(price_info.get("value")),
            "currency": price_info.get("currency", "ARS"),
            "engine": cc_to_liters(data.get("carone_cylinder_capacity")),
            "power_hp": as_number(data.get("carone_potency")),
            "transmission": data.get("carone_transmission_data", {}).get("label"),
            "traction": data.get("carone_traction_data", {}).get("label"),
            "fuel_type": data.get("carone_fuel_data", {}).get("label"),
            "consumption": format_consumption_carone(data.get("carone_consumption")),
            "location": data.get("carone_dealer_id", "Buenos Aires"),
            "url": url,
            "collected_at": datetime.now().isoformat()
        }
    except:
        return None