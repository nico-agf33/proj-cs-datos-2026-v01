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
}

def get_available_brands() -> list[str]:
    """
    Extrae las marcas desde el bloque catalogFilters que aparece en el código fuente.
    """
    url = f"{_BASE}/comprar"
    try:
        resp = requests.get(url, headers=_HEADERS, timeout=20)
        resp.raise_for_status()
        
        # Esta Regex busca específicamente el patrón que pasaste en el fragmento:
        # "label":"MARCA","count":N,"__typename":"BrandFilter"
        # Manejamos los escapes de comillas que usa Next.js
        brand_pattern = r'\\"label\\":\\"(.*?)\\",\\"count\\":\d+,\\"__typename\\":\\"BrandFilter\\"'
        
        found_brands = re.findall(brand_pattern, resp.text)
        
        if not found_brands:
            # Fallback por si las comillas no están escapadas en la respuesta
            brand_pattern_alt = r'"label":"(.*?)","count":\d+,"__typename":"BrandFilter"'
            found_brands = re.findall(brand_pattern_alt, resp.text)

        # Limpiamos y quitamos duplicados
        resultado = list(dict.fromkeys([b for b in found_brands if b.strip()]))
        
        if resultado:
            logger.info(f"[carone] Se detectaron {len(resultado)} marcas (incluyendo {resultado[:3]})")
        return resultado

    except Exception as e:
        logger.error(f"[carone] Error descubriendo marcas: {e}")
        return []

def search(marca: str = None, modelo: str = None, limit: int = 50) -> list[dict]:
    """
    Busca vehículos en Carone con soporte para paginación automática.
    """
    results = []
    page = 1
    
    # Normalización del nombre de marca para la URL
    # Ej: "Mercedes Benz" -> "mercedes-benz"
    marca_url = marca.lower().replace(" ", "-") if marca else ""
    path = f"/comprar/usados/{marca_url}" if marca_url else "/comprar/usados"
    
    while len(results) < limit:
        url = f"{_BASE}{path}?p={page}"
        
        try:
            resp = requests.get(url, headers=_HEADERS, timeout=15)
            # Extraemos los productos usando la misma lógica de bloques
            items_data = re.findall(r'\"product\":({.*?\"__typename\":\"SimpleProduct\"})', resp.text)
            
            if not items_data:
                break

            for item_json in items_data:
                if len(results) >= limit: break
                
                try:
                    # Limpiamos el JSON de escapes
                    clean_json = item_json.replace('\\"', '"')
                    data = json.loads(clean_json)
                    
                    price_info = data.get("price_range", {}).get("maximum_price", {}).get("final_price", {})
                    
                    listing = {
                        "source": "carone",
                        "source_listing_id": str(data.get("sku") or data.get("id")),
                        "make": data.get("carone_marca_data", {}).get("label", marca),
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
                except:
                    continue
            
            if len(items_data) < 5: break # No hay más páginas
            page += 1
            
        except Exception as e:
            logger.error(f"[carone] Error en página {page}: {e}")
            break
            
    return results