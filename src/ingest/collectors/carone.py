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
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "x-v6-country": "ar",
    "Referer": "https://carone.com.ar/"
}

def get_available_brands() -> list[str]:
    """
    Extrae marcas desde el bloque catalogFilters detectado en el HTML.
    """
    url = f"{_BASE}/comprar?carOptions=usados"
    try:
        resp = requests.get(url, headers=_HEADERS, timeout=20)
        resp.raise_for_status()
        
        # Regex para capturar marcas del JSON de Apollo (BrandFilter)
        # Buscamos: "label":"Chevrolet","count":75
        brand_pattern = r'\\"label\\":\\"(.*?)\\",\\"count\\":\d+,\\"__typename\\":\\"BrandFilter\\"'
        found = re.findall(brand_pattern, resp.text)
        
        if not found:
            # Fallback para formato sin escapes
            found = re.findall(r'"label":"(.*?)","count":\d+,"__typename":"BrandFilter"', resp.text)

        return list(dict.fromkeys([b for b in found if b.strip()]))
    except Exception as e:
        logger.error(f"[carone] Error en descubrimiento: {e}")
        return []

def search(marca: str = None, modelo: str = None, limit: int = 50) -> list[dict]:
    """
    Recorre el catálogo de usados usando la URL y filtros correctos.
    """
    results = []
    page = 1
    
    # URL Base observada en el código fuente
    base_url = f"{_BASE}/comprar?carOptions=usados"
    
    if marca:
        # El sitio usa el nombre de la marca directamente
        base_url += f"&marca={marca.replace(' ', '%20')}"

    while len(results) < limit:
        # Paginación observada: &p=N
        url = f"{base_url}&p={page}"
        try:
            logger.info(f"[carone] Consultando: {url}")
            resp = requests.get(url, headers=_HEADERS, timeout=15)
            resp.raise_for_status()
            
            # --- CAMBIO DE REGEX ---
            # El fragmento muestra que los datos están en objetos con typename 'ProductCardFragment' 
            # o dentro de la lista de 'items' de la query 'GetProductsCard'.
            # Buscamos el patrón del objeto de producto individual:
            items_data = re.findall(r'(\{\\"id\\":\\"\d+\\",\\"sku\\":\\".*?\\",\\"name\\":\\".*?\\",.*?\\"__typename\\":\\"SimpleProduct\\".*?\})', resp.text)
            
            if not items_data:
                # Intento 2: Búsqueda por SKU
                items_data = re.findall(r'(\{\\"sku\\":\\".*?\\",\\"name\\":\\".*?\\",.*?\\"carone_year\\":\d+.*?\})', resp.text)

            if not items_data:
                break

            logger.info(f"[carone] Detectados {len(items_data)} autos en página {page}")

            for item_json in items_data:
                if len(results) >= limit: break
                try:
                    # Limpiar JSON de escapes de Next.js
                    clean_json = item_json.replace('\\"', '"')
                    data = json.loads(clean_json)
                    
                    sku = data.get("sku")
                    if not sku: continue
                    
                    # Evitar duplicados
                    if any(r['source_listing_id'] == str(sku) for r in results):
                        continue

                    price_info = data.get("price_range", {}).get("maximum_price", {}).get("final_price", {})
                    
                    listing = {
                        "source": "carone",
                        "source_listing_id": str(sku),
                        "make": data.get("carone_marca_data", {}).get("label") or marca,
                        "model": data.get("carone_modelo_data", {}).get("label"),
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
                        "url": f"{_BASE}/comprar/usados/{data.get('url_key')}",
                        "collected_at": datetime.now().isoformat()
                    }
                    results.append(listing)
                except:
                    continue
            
            # Carone tiene páginas de 9 o 20 productos. Si vienen pocos, es el final.
            if len(items_data) < 5: break
            page += 1
            
        except Exception as e:
            logger.error(f"[carone] Error en página {page}: {e}")
            break
            
    return results