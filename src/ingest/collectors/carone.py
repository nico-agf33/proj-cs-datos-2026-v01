import requests
import re
import json
import logging
from datetime import datetime
from ..normalize import as_number, cc_to_liters, format_consumption_carone

logger = logging.getLogger(__name__)

_BASE = "https://carone.com.ar"
_HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "x-v6-country": "ar"
}

def get_available_brands() -> list[str]:
    """
    Extrae marcas que tengan stock de USADOS únicamente.
    """
    # Apuntamos directamente a la subcategoría de usados
    url = f"{_BASE}/comprar/usados"
    try:
        resp = requests.get(url, headers=_HEADERS, timeout=20)
        # Buscamos el filtro de marcas en el JSON de usados
        brand_pattern = r'\\"label\\":\\"(.*?)\\",\\"count\\":\d+,\\"__typename\\":\\"BrandFilter\\"'
        found_brands = re.findall(brand_pattern, resp.text)
        
        if not found_brands:
            brand_pattern_alt = r'"label":"(.*?)","count":\d+,"__typename":"BrandFilter"'
            found_brands = re.findall(brand_pattern_alt, resp.text)

        return list(dict.fromkeys([b for b in found_brands if b.strip()]))
    except Exception as e:
        logger.error(f"[carone] Error descubriendo marcas de usados: {e}")
        return []

def search(marca: str = None, modelo: str = None, limit: int = 50) -> list[dict]:
    """
    Captura masivamente solo la categoría USADOS.
    """
    results = []
    page = 1
    
    # Construcción de la URL específica para USADOS
    base_path = "/comprar/usados"
    if marca:
        # Carone usa marcas en minúscula con guiones en la URL
        marca_norm = marca.lower().replace(" ", "-")
        base_path += f"/{marca_norm}"
    
    while len(results) < limit:
        url = f"{_BASE}{base_path}?p={page}"
        try:
            logger.info(f"[carone] Scrapeando USADOS: {url}")
            resp = requests.get(url, headers=_HEADERS, timeout=15)
            
            # Buscamos los bloques de producto
            items_data = re.findall(r'(\{\\"__typename\\":\\"SimpleProduct\\",.*?\\"sku\\":\\".*?\\"})', resp.text)
            
            if not items_data:
                break

            for item_json in items_data:
                if len(results) >= limit: break
                try:
                    clean_json = item_json.replace('\\"', '"')
                    data = json.loads(clean_json)
                    
                    # DOBLE VALIDACIÓN: Verificar que la URL del auto contenga /usados/
                    # Esto evita que se filtren "Sugeridos" 0km que a veces aparecen al final
                    url_key = data.get('url_key', '')
                    if not url_key: continue
                    
                    price_info = data.get("price_range", {}).get("maximum_price", {}).get("final_price", {})
                    
                    listing = {
                        "source": "carone",
                        "source_listing_id": str(data.get("sku") or data.get("id")),
                        "make": data.get("carone_marca_data", {}).get("label") or marca,
                        "model": data.get("carone_modelo_data", {}).get("label"),
                        "version": data.get("carone_version_description"),
                        "year": int(as_number(data.get("carone_year", 0))),
                        "mileage": int(as_number(data.get("carone_mileage", 0))),
                        "price": as_number(price_info.get("value", 0)),
                        "currency": price_info.get("currency", "ARS"),
                        "engine": cc_to_liters(data.get("carone_cylinder_capacity")),
                        "power_hp": as_number(data.get("carone_potency")),
                        "transmission": data.get("carone_transmission_data", {}).get("label"),
                        "traction": data.get("carone_traction_data", {}).get("label"),
                        "fuel_type": data.get("carone_fuel_data", {}).get("label"),
                        "consumption": format_consumption_carone(data.get("carone_consumption")),
                        "location": data.get("carone_dealer_id", "Buenos Aires"),
                        "url": f"{_BASE}/comprar/usados/{url_key}",
                        "collected_at": datetime.now().isoformat()
                    }
                    results.append(listing)
                except:
                    continue
            
            if len(items_data) < 10: break
            page += 1
            
        except Exception as e:
            logger.error(f"[carone] Error en página {page}: {e}")
            break
            
    return results