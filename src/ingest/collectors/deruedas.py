import requests
from bs4 import BeautifulSoup
import re
import time
import logging
from ..normalize import as_number, remove_accents, clean_price_and_currency

logger = logging.getLogger(__name__)

_BASE = "https://www.deruedas.com.ar"
_HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def get_available_brands() -> list[str]:
    """
    Extrae la lista completa de marcas desde el panel 'divModelosFancy'.
    """
    url = f"{_BASE}/bus.asp?segmento=0"
    try:
        resp = requests.get(url, headers=_HEADERS, timeout=20)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        marcas = []
        # Buscamos los inputs tipo checkbox dentro del div de marcas
        inputs = soup.select("#divModelosFancy input.fancyCheck")
        
        for i in inputs:
            val = i.get("value")
            if val and val.strip():
                marcas.append(val.strip())
        
        # Fallback por si el div anterior no está
        if not marcas:
            enlaces = soup.find_all("a", {"marcaVal": True})
            for a in enlaces:
                val = a.get("marcaVal")
                if val: marcas.append(val.strip())

        resultado = list(dict.fromkeys(marcas))
        return resultado

    except Exception as e:
        logger.error(f"Error en descubrimiento de marcas: {e}")
        return []

def search(marca: str = None, modelo: str = None, limit: int = 50) -> list[dict]:
    """
    Realiza la búsqueda segmentada o global y recorre la paginación.
    """
    results = []
    page = 1
    
    # Construcción de parámetros
    params = "segmento=0"
    if marca:
        params += f"&marca={marca.replace(' ', '%20')}"
    if modelo:
        modelo_enc = f"{marca}:{modelo}".replace(" ", "%20")
        params += f"&modelo={modelo_enc}"

    while len(results) < limit:
        search_url = f"{_BASE}/busCraw.asp?{params}&weNeed=divBusqueda&pag={page}"
        
        try:
            resp = requests.get(search_url, headers=_HEADERS, timeout=20)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            links = []
            for a in soup.find_all('a', href=True):
                if 'vendo/' in a['href']:
                    full_url = a['href'] if a['href'].startswith("http") else _BASE + a['href']
                    links.append(full_url)
            
            unique_links = list(dict.fromkeys(links))
            if not unique_links:
                break 

            logger.info(f"[deruedas] Marca {marca or 'Global'} | Página {page}: Procesando {len(unique_links)} avisos...")

            for url in unique_links:
                if len(results) >= limit:
                    break
                time.sleep(0.33) # Velocidad optimizada
                item = _scrape_detail(url)
                if item:
                    results.append(item)
            
            page += 1
            
        except Exception as e:
            logger.error(f"[deruedas] Error en página {page}: {e}")
            break 
            
    return results

def _scrape_detail(url: str) -> dict | None:
    """
    Extrae la información técnica de la ficha individual, 
    incluyendo modelo exacto desde JS y precio original.
    """
    try:
        resp = requests.get(url, headers=_HEADERS, timeout=15)
        resp.encoding = 'utf-8'
        html_content = resp.text
        soup = BeautifulSoup(html_content, 'html.parser')

        # 1. MODELO Y MARCA EXACTOS (Desde el bloque JavaScript 'var datos')
        model_exact = None
        make_exact = None
        scripts = soup.find_all("script")
        for script in scripts:
            if script.string and "modelo:" in script.string:
                model_match = re.search(r"modelo:\s*'([^']+)'", script.string)
                make_match = re.search(r"marca:\s*'([^']+)'", script.string)
                if model_match: model_exact = model_match.group(1)
                if make_match: make_exact = make_match.group(1)
                break 

        # 2. PRECIO Y MONEDA (Desde la tabla "Datos del Vehículo")
        price_val, price_curr = 0.0, "ARS"
        for td in soup.find_all("td"):
            if "Precio:" in td.get_text():
                b_tag = td.find("b")
                if b_tag:
                    price_val, price_curr = clean_price_and_currency(b_tag.get_text(strip=True))
                    break

        # 3. ATRIBUTOS TÉCNICOS (Boxes destacados)
        mapping = {
            "motor": "engine", "potencia": "power_hp",
            "transmision": "transmission", "traccion": "traction",
            "combustible": "fuel_type", "consumo prom.": "consumption"
        }
        specs = {}
        for box in soup.select(".box-destacado"):
            content = box.get_text(separator="|", strip=True).split("|")
            if len(content) >= 2:
                label = remove_accents(content[0])
                value = content[-1]
                if label in mapping:
                    col = mapping[label]
                    specs[col] = as_number(value) if col == "power_hp" else value

        # 4. DATOS BÁSICOS (Meta tags / Schema.org)
        def get_meta(prop):
            tag = soup.find("meta", itemprop=prop)
            return tag["content"] if tag else None

        return {
            "source": "deruedas",
            "source_listing_id": url.split("cod=")[-1],
            "make": make_exact or get_meta("brand"),
            "model": model_exact or get_meta("model"),
            "version": soup.select_one(".titulo.resaltar span").get_text(strip=True) if soup.select_one(".titulo.resaltar span") else "",
            "year": int(as_number(get_meta("modelDate"))),
            "mileage": int(as_number(get_meta("mileageFromOdometer"))),
            "price": price_val,
            "currency": price_curr,
            "engine": specs.get("engine"),
            "power_hp": specs.get("power_hp"),
            "transmission": specs.get("transmission"),
            "traction": specs.get("traction"),
            "fuel_type": specs.get("fuel_type") or get_meta("fuelType"),
            "consumption": specs.get("consumption"),
            "location": get_meta("address"),
            "url": url
        }
    except Exception:
        return None