import requests
import json
import logging
from datetime import datetime
from ..normalize import as_number, cc_to_liters, format_consumption_carone

logger = logging.getLogger(__name__)

_GRAPHQL_URL = "https://carone.com.ar/api/graphql"

# Headers exactos del cURL para evitar bloqueos
_HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0",
    "Content-Type": "application/json",
    "x-v6-country": "ar",
    "Origin": "https://carone.com.ar",
    "Referer": "https://carone.com.ar/comprar?carOptions=usados"
}

def get_available_brands() -> list[str]:
    """
    En el nuevo sistema por API, no necesitamos marcas para paginar, 
    pero la mantenemos por compatibilidad con el orquestador.
    """
    return [None] # Devolvemos una lista con None para que download.py haga una sola pasada global

def search(marca: str = None, modelo: str = None, limit: int = 50) -> list[dict]:
    """
    Consulta la API GraphQL de Carone de forma paginada.
    """
    results = []
    current_page = 1
    page_size = 20 # Aumentamos a 20 para ir más rápido
    
    # Preparamos los filtros de la API
    # carone_tags_arg: [2] significa USADOS
    filters = {
        "stock_status": {"eq": "IN_STOCK"},
        "carone_tags_arg": {"in": [2]}
    }
    if marca:
        filters["carone_marca_label"] = {"eq": marca}

    while len(results) < limit:
        # El payload JSON que descubrimos en el cURL
        payload = {
            "operationName": "GetProductsCard",
            "variables": {
                "q": "",
                "pageSize": page_size,
                "currentPage": current_page,
                "sort": {"created_at": "DESC"},
                "filter": filters
            },
            "query": """
            query GetProductsCard($q: String!, $pageSize: Int!, $currentPage: Int!, $filter: ProductAttributeFilterInput) {
              products(search: $q, pageSize: $pageSize, currentPage: $currentPage, filter: $filter) {
                total_count
                items {
                  sku
                  name
                  url_key
                  carone_year
                  carone_mileage
                  carone_potency
                  carone_cylinder_capacity
                  carone_consumption
                  carone_marca_data { label }
                  carone_modelo_data { label }
                  carone_transmission_data { label }
                  carone_traction_data { label }
                  carone_fuel_data { label }
                  price_range {
                    maximum_price {
                      final_price { currency value }
                    }
                  }
                }
              }
            }
            """
        }

        try:
            logger.info(f"[carone] Pidiendo página {current_page} (Total acumulado: {len(results)})")
            resp = requests.post(_GRAPHQL_URL, json=payload, headers=_HEADERS, timeout=20)
            resp.raise_for_status()
            data = resp.json()
            
            products_data = data.get("data", {}).get("products", {})
            items = products_data.get("items", [])
            total_available = products_data.get("total_count", 0)

            if not items:
                break

            for item in items:
                if len(results) >= limit: break
                
                price_info = item.get("price_range", {}).get("maximum_price", {}).get("final_price", {})
                
                # Mapeo directo y limpio del JSON de la API
                row = {
                    "source": "carone",
                    "source_listing_id": item.get("sku"),
                    "make": (item.get("carone_marca_data") or {}).get("label"),
                    "model": (item.get("carone_modelo_data") or {}).get("label"),
                    "version": item.get("name"),
                    "year": int(as_number(item.get("carone_year"))),
                    "mileage": int(as_number(item.get("carone_mileage"))),
                    "price": as_number(price_info.get("value")),
                    "currency": price_info.get("currency", "ARS"),
                    "engine": cc_to_liters(item.get("carone_cylinder_capacity")),
                    "power_hp": as_number(item.get("carone_potency")),
                    "transmission": (item.get("carone_transmission_data") or {}).get("label"),
                    "traction": (item.get("carone_traction_data") or {}).get("label"),
                    "fuel_type": (item.get("carone_fuel_data") or {}).get("label"),
                    "consumption": format_consumption_carone(item.get("carone_consumption")),
                    "location": "Buenos Aires",
                    "url": f"https://carone.com.ar/comprar/usados/{item.get('url_key')}",
                    "collected_at": datetime.now().isoformat()
                }
                results.append(row)

            # Si ya bajamos todos los que la API dice que existen, frenamos
            if len(results) >= total_available or len(items) < page_size:
                logger.info(f"[carone] Se alcanzó el total de stock disponible ({total_available}).")
                break

            current_page += 1
            
        except Exception as e:
            logger.error(f"[carone] Error en API GraphQL: {e}")
            break
            
    return results