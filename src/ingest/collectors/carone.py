import requests
import re
import json
import logging
from datetime import datetime
from ..normalize import as_number, cc_to_liters, format_consumption_carone

logger = logging.getLogger(__name__)

_BASE = "https://carone.com.ar"
_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "x-v6-country": "ar",
    "Referer": "https://carone.com.ar/"
}

def get_available_brands() -> list[str]:
    """
    Extrae las marcas disponibles del catálogo general.
    """
    # La página real de búsqueda es /comprar
    url = f"{_BASE}/comprar"
    try:
        resp = requests.get(url, headers=_HEADERS, timeout=20)
        resp.raise_for_status()
        
        # Regex para el bloque catalogFilters que pasaste
        brand_pattern = r'\\"label\\":\\"(.*?)\\",\\"count\\":\d+,\\"__typename\\":\\"BrandFilter\\"'
        found = re.findall(brand_pattern, resp.text)
        
        if not found:
            # Intento sin escapes (algunas respuestas cambian)
            found = re.findall(r'"label":"(.*?)","count":\d+,"__typename":"BrandFilter"', resp.text)

        return list(dict.fromkeys([b for b in found if b.strip()]))
    except Exception as e:
        logger.error(f"[carone] Error en descubrimiento: {e}")
        return []

def search(marca: str = None, modelo: str = None, limit: int = 50) -> list[dict]:
    """
    Busca en el catálogo de Carone filtrando por Usados (car_options=2).
    """
    results = []
    page = 1
    
    # La URL correcta para listar es /comprar
    # El filtro de Usados Garantizados es car_options=2
    base_url = f"{_BASE}/comprar?car_options=2"
    
    if marca:
        # Carone usa parámetros de búsqueda en la query para filtros específicos
        # o slugs en la URL. Probamos con el parámetro de marca detectado en el JSON.
        base_url += f"&marca={marca.replace(' ', '%20')}"

    while len(results) < limit:
        # Paginación con parámetro &p=
        url = f"{base_url}&p={page}"
        try:
            logger.info(f"[carone] Consultando: {url}")
            resp = requests.get(url, headers=_HEADERS, timeout=15)
            resp.raise_for_status()
            
            # Buscamos bloques de producto con typename SimpleProduct
            items_data = re.findall(r'(\{\\"__typename\\":\\"SimpleProduct\\",.*?\\"sku\\":\\".*?\\"})', resp.text)
            
            if not items_data:
                # Intento alternativo por si el string cambia
                items_data = re.findall(r'({"__typename":"SimpleProduct",.*?"sku":".*?"})', resp.text)

            if not items_data:
                logger.warning(f"[carone] No se detectaron productos en p{page}.")
                break

            logger.info(f"[carone] Procesando {len(items_data)} autos en página {page}...")

            for item_json in items_data:
                if len(results) >= limit: break
                try:
                    clean_json = item_json.replace('\\"', '"')
                    data = json.loads(clean_json)
                    
                    # Carone usa url_key para construir el link
                    url_key = data.get('url_key')
                    if not url_key: continue
                    
                    # Solo nos interesan los que tienen /usados/ en el link
                    # (Doble check de seguridad contra sugeridos 0km)
                    final_url = f"{_BASE}/comprar/usados/{url_key}"

                    price_info = data.get("price_range", {}).get("maximum_price", {}).get("final_price", {})
                    
                    listing = {
                        "source": "carone",
                        "source_listing_id": str(data.get("sku") or data.get("id")),
                        "make": data.get("carone_marca_data", {}).get("label", marca or "Desconocido"),
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
                        "url": final_url,
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