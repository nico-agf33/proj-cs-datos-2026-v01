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
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "x-v6-country": "ar",
    "Referer": "https://carone.com.ar/"
}

def get_available_brands() -> list[str]:
    """Extrae marcas desde el bloque catalogFilters del código fuente."""
    url = f"{_BASE}/comprar?carOptions=usados"
    try:
        resp = requests.get(url, headers=_HEADERS, timeout=20)
        # Regex para capturar el listado de marcas en el JSON de filtros
        pattern = r'\\"brands\\":\{.*?\\"default\\":\[(.*?)\],\\"others\\":\[(.*?)\].*?\}'
        match = re.search(pattern, resp.text)
        
        brands = []
        if match:
            # Capturamos tanto las marcas 'default' como 'others' del snippet
            content = match.group(1) + match.group(2)
            brands = re.findall(r'\\"label\\":\\"(.*?)\\"', content)
        
        return list(dict.fromkeys([b for b in brands if b.strip()]))
    except Exception as e:
        logger.error(f"[carone] Error en marcas: {e}")
        return []

def search(marca: str = None, modelo: str = None, limit: int = 50) -> list[dict]:
    """Obtiene los usados de Carone y entra a cada ficha para asegurar consistencia técnica."""
    results = []
    page = 1
    
    # URL de búsqueda con el filtro de usados detectado en el source
    base_url = f"{_BASE}/comprar?carOptions=usados"
    if marca:
        base_url += f"&marca={marca.replace(' ', '%20')}"

    while len(results) < limit:
        url = f"{base_url}&p={page}"
        try:
            logger.info(f"[carone] Consultando catálogo: {url}")
            resp = requests.get(url, headers=_HEADERS, timeout=15)
            
            # Extraer todas las url_key de los autos en la grilla
            # Formato: "url_key":"peugeot-208-..."
            urls_keys = re.findall(r'\\"url_key\\":\\"(.*?)\\"', resp.text)
            unique_keys = list(dict.fromkeys(urls_keys))

            if not unique_keys:
                break

            for key in unique_keys:
                if len(results) >= limit: break
                
                detail_url = f"{_BASE}/comprar/usados/{key}"
                time.sleep(0.4) # Velocidad Carone es más alta que DeRuedas
                
                item = _scrape_detail(detail_url)
                if item:
                    results.append(item)
            
            if len(unique_keys) < 5: break
            page += 1
        except Exception as e:
            logger.error(f"[carone] Error en catálogo p{page}: {e}")
            break
            
    return results

def _scrape_detail(url: str) -> dict | None:
    """Entra a la ficha y extrae el JSON hidratado con los 6 datos técnicos."""
    try:
        resp = requests.get(url, headers=_HEADERS, timeout=10)
        # Buscamos el objeto 'product' que contiene los HP, Tracción y Motor
        pattern = r'\"product\":({.*?\"__typename\":\"SimpleProduct\"})'
        match = re.search(pattern, resp.text)
        
        if not match: return None
        
        data = json.loads(match.group(1).replace('\\"', '"'))
        
        # Mapeo de precios
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
            # --- LOS 6 DATOS TÉCNICOS (Extraídos del JSON interno) ---
            "engine": cc_to_liters(data.get("carone_cylinder_capacity")),
            "power_hp": as_number(data.get("carone_potency")),
            "transmission": data.get("carone_transmission_data", {}).get("label"),
            "traction": data.get("carone_traction_data", {}).get("label"),
            "fuel_type": data.get("carone_fuel_data", {}).get("label"),
            "consumption": format_consumption_carone(data.get("carone_consumption")),
            # ---------------------------------------------------------
            "location": data.get("carone_dealer_id", "Buenos Aires"),
            "url": url,
            "collected_at": datetime.now().isoformat()
        }
    except:
        return None