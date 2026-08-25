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
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "x-v6-country": "ar",
    "Referer": "https://carone.com.ar/comprar"
}

def get_available_brands() -> list[str]:
    """
    Extrae las marcas desde el catálogo general de Carone.
    """
    url = f"{_BASE}/comprar?carOptions=usados"
    try:
        resp = requests.get(url, headers=_HEADERS, timeout=20)
        resp.raise_for_status()
        
        # Buscamos el bloque de marcas en los filtros (BrandFilter)
        # Probamos con y sin escapes de comillas
        brand_pattern = r'\\"label\\":\\"(.*?)\\",\\"count\\":\d+,\\"__typename\\":\\"BrandFilter\\"'
        found = re.findall(brand_pattern, resp.text)
        
        if not found:
            found = re.findall(r'"label":"(.*?)","count":\d+,"__typename":"BrandFilter"', resp.text)

        return list(dict.fromkeys([b for b in found if b.strip()]))
    except Exception as e:
        logger.error(f"[carone] Error en descubrimiento: {e}")
        return []

def search(marca: str = None, modelo: str = None, limit: int = 50) -> list[dict]:
    """
    Busca usados en Carone usando extracción de JSON-LD y marcadores técnicos.
    """
    results = []
    page = 1
    
    # URL de búsqueda correcta según el view-source
    base_url = f"{_BASE}/comprar?carOptions=usados"
    if marca:
        base_url += f"&marca={marca.replace(' ', '%20')}"

    while len(results) < limit:
        url = f"{base_url}&p={page}"
        try:
            logger.info(f"[carone] Consultando: {url}")
            resp = requests.get(url, headers=_HEADERS, timeout=15)
            resp.raise_for_status()
            html = resp.text

            # --- ESTRATEGIA 1: Capturar JSON-LD (Schema.org) ---
            # Estos bloques contienen: Nombre, Precio, Marca, Modelo, Año y KM.
            # Vienen en etiquetas <script type="application/ld+json">
            json_ld_blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.DOTALL)
            
            extracted_count = 0
            for block in json_ld_blocks:
                try:
                    data = json.loads(block)
                    # Solo procesamos si el tipo es 'Car' (ignora Organization y Breadcrumb)
                    if data.get("@type") != "Car":
                        continue
                    
                    sku = data.get("url", "").split("-")[-1] # El ID suele estar al final de la URL
                    
                    # --- ESTRATEGIA 2: Buscar Specs Técnicas en el "ruido" de Next.js ---
                    # Buscamos patrones específicos cerca de este SKU en el HTML
                    potency = re.search(fr'\\"{sku}\\".*?\\"carone_potency\\":\\"(.*?)\\"', html)
                    engine_cc = re.search(fr'\\"{sku}\\".*?\\"carone_cylinder_capacity\\":(\d+)', html)
                    trans = re.search(fr'\\"{sku}\\".*?\\"carone_transmission_data\\":\{{.*?\\"label\\":\\"(.*?)\\"\}}', html)
                    traction = re.search(fr'\\"{sku}\\".*?\\"carone_traction_data\\":\{{.*?\\"label\\":\\"(.*?)\\"\}}', html)
                    fuel = re.search(fr'\\"{sku}\\".*?\\"carone_fuel_data\\":\{{.*?\\"label\\":\\"(.*?)\\"\}}', html)
                    
                    offer = data.get("offers", {})
                    
                    item = {
                        "source": "carone",
                        "source_listing_id": sku,
                        "make": data.get("brand", {}).get("name", marca),
                        "model": data.get("model"),
                        "version": data.get("name"),
                        "year": int(as_number(data.get("vehicleModelDate", 0))),
                        "mileage": int(as_number(data.get("mileageFromOdometer", {}).get("value", 0))),
                        "price": float(as_number(offer.get("price", 0))),
                        "currency": offer.get("priceCurrency", "ARS"),
                        # Datos técnicos (Regex directo al HTML de Next.js)
                        "engine": cc_to_liters(engine_cc.group(1)) if engine_cc else None,
                        "power_hp": as_number(potency.group(1)) if potency else None,
                        "transmission": trans.group(1) if trans else None,
                        "traction": traction.group(1) if traction else None,
                        "fuel_type": fuel.group(1) if fuel else None,
                        "consumption": None, # Difícil de sacar del listado
                        "location": "Buenos Aires (CarOne)",
                        "url": data.get("url"),
                        "collected_at": datetime.now().isoformat()
                    }
                    
                    # Evitar duplicados
                    if not any(r['source_listing_id'] == item['source_listing_id'] for r in results):
                        results.append(item)
                        extracted_count += 1
                        
                except Exception:
                    continue

            if extracted_count == 0:
                break # No encontramos más autos en esta página
            
            logger.info(f"[carone] Se capturaron {extracted_count} autos de la página {page}.")
            page += 1
            
        except Exception as e:
            logger.error(f"[carone] Error en p{page}: {e}")
            break
            
    return results