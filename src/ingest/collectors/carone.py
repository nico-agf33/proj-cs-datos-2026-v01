import requests
import re
import json
import logging
from datetime import datetime
from ..normalize import as_number, cc_to_liters, format_consumption_carone

logger = logging.getLogger(__name__)

_BASE = "https://carone.com.ar"
_HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
    "Referer": "https://carone.com.ar/comprar",
    "x-v6-country": "ar"
}

def get_available_brands() -> list[str]:
    """
    Extrae dinámicamente las marcas desde el State de Next.js en la página principal.
    """
    url = f"{_BASE}/comprar"
    try:
        resp = requests.get(url, headers=_HEADERS, timeout=20)
        # Buscamos el listado de opciones del filtro de marcas
        pattern = r'\"attribute_code\":\"carone_marca\",\"label\":\"Marca\",\"options\":\[(.*?)\]'
        match = re.search(pattern, resp.text)
        
        if match:
            options_raw = match.group(1)
            brands = re.findall(r'\"label\":\"(.*?)\"', options_raw)
            return [b for b in brands if b.strip()]
        
        # Fallback por si la estructura cambia levemente
        brands_fallback = re.findall(r'\"carone_marca_data\":\{\"__typename\":\"AttributeOptionOutput\",\"label\":\"(.*?)\"\}', resp.text)
        return list(dict.fromkeys(brands_fallback))
    except Exception as e:
        logger.error(f"[carone] Error descubriendo marcas: {e}")
        return []

def search(marca: str = None, modelo: str = None, limit: int = 50) -> list[dict]:
    """
    Busca vehículos en Carone con soporte para paginación automática.
    """
    results = []
    page = 1
    
    # Construcción de la ruta base
    path = "/comprar/usados"
    if marca:
        # Normalizar marca para la URL (ej: Mercedes Benz -> mercedes-benz)
        path += f"/{marca.lower().replace(' ', '-')}"
    
    while len(results) < limit:
        # Carone usa el parámetro ?p=N para paginar
        url = f"{_BASE}{path}?p={page}"
        
        try:
            logger.info(f"[carone] Consultando página {page} de {marca or 'Usados'}...")
            resp = requests.get(url, headers=_HEADERS, timeout=15)
            
            # Extraemos los bloques de productos (vienen hidratados en el HTML)
            items_data = re.findall(r'\"product\":({.*?\"__typename\":\"SimpleProduct\"})', resp.text)
            
            if not items_data:
                logger.info(f"[carone] No hay más resultados en la página {page}.")
                break

            for item_json in items_data:
                if len(results) >= limit:
                    break
                
                try:
                    # Limpiamos el JSON (Next.js escapa comillas con \")
                    clean_json = item_json.replace('\\"', '"')
                    data = json.loads(clean_json)
                    
                    price_info = data.get("price_range", {}).get("maximum_price", {}).get("final_price", {})
                    
                    listing = {
                        "source": "carone",
                        "source_listing_id": str(data.get("sku") or data.get("id")),
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
                        "url": f"{_BASE}/comprar/usados/{data.get('url_key')}",
                        "collected_at": datetime.now().isoformat()
                    }
                    results.append(listing)
                except Exception as e:
                    continue
            
            # Si trajimos menos de 10 productos (aprox), es probable que sea la última página
            if len(items_data) < 10:
                break
                
            page += 1
            
        except Exception as e:
            logger.error(f"[carone] Error en página {page}: {e}")
            break
            
    return results