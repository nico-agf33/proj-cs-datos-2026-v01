import requests
import re
import json
import logging
from datetime import datetime
from ..normalize import as_number, cc_to_liters, format_consumption_carone

logger = logging.getLogger(__name__)

_BASE = "https://carone.com.ar"
# User-Agent de un navegador real actualizado
_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.9",
    "Referer": "https://carone.com.ar/",
    "x-v6-country": "ar"
}

def get_available_brands() -> list[str]:
    """
    Busca marcas de usados. Si falla, devuelve lista vacía para que el 
    orquestador use la búsqueda global.
    """
    url = f"{_BASE}/comprar/usados"
    try:
        resp = requests.get(url, headers=_HEADERS, timeout=20)
        resp.raise_for_status()
        
        # Regex ultra-permissiva para capturar el valor de 'label' cerca de 'BrandFilter'
        # Busca: "label":"MARCA" ... "BrandFilter" en cualquier orden
        brand_pattern = r'\\"label\\":\\"(.*?)\\",\\"count\\":\d+,\\"__typename\\":\\"BrandFilter\\"'
        found = re.findall(brand_pattern, resp.text)
        
        if not found:
            # Intento 2: Buscar marca_data
            found = re.findall(r'\\"carone_marca_data\\":\{\\"__typename\\":\\"AttributeOptionOutput\\",\\"label\\":\\"(.*?)\\"\}', resp.text)

        return list(dict.fromkeys([b for b in found if b.strip()]))
    except Exception as e:
        logger.error(f"[carone] Error en descubrimiento: {e}")
        return []

def search(marca: str = None, modelo: str = None, limit: int = 50) -> list[dict]:
    """
    Si marca es None, busca en el listado general de usados.
    """
    results = []
    page = 1
    
    # Si no hay marca, usamos el path base de usados
    marca_path = f"/{marca.lower().replace(' ', '-')}" if marca else ""
    base_url = f"{_BASE}/comprar/usados{marca_path}"
    
    while len(results) < limit:
        url = f"{base_url}?p={page}"
        try:
            logger.info(f"[carone] Consultando: {url}")
            resp = requests.get(url, headers=_HEADERS, timeout=15)
            resp.raise_for_status()
            
            # Buscamos bloques de producto con typename SimpleProduct
            items_data = re.findall(r'(\{\\"__typename\\":\\"SimpleProduct\\",.*?\\"sku\\":\\".*?\\"})', resp.text)
            
            if not items_data:
                logger.warning(f"[carone] No se detectaron productos en p{page}. Fin de la fuente.")
                break

            for item_json in items_data:
                if len(results) >= limit: break
                try:
                    clean_json = item_json.replace('\\"', '"')
                    data = json.loads(clean_json)
                    
                    url_key = data.get('url_key')
                    if not url_key: continue

                    price_info = data.get("price_range", {}).get("maximum_price", {}).get("final_price", {})
                    
                    listing = {
                        "source": "carone",
                        "source_listing_id": str(data.get("sku") or data.get("id")),
                        "make": data.get("carone_marca_data", {}).get("label", "Desconocido"),
                        "model": data.get("carone_modelo_data", {}).get("label", "Desconocido"),
                        "version": data.get("carone_version_description", ""),
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
            
            if len(items_data) < 5: break
            page += 1
        except Exception as e:
            logger.error(f"[carone] Error en página {page}: {e}")
            break
            
    return results