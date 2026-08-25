import re
import unicodedata

def remove_accents(text: str) -> str:
    if not text: return ""
    text = str(text).lower().strip()
    return "".join(
        c for c in unicodedata.normalize('NFD', text)
        if unicodedata.category(c) != 'Mn'
    )

def as_number(val) -> float:
    """Limpia '161.000 Km' o '20.500' -> 161000.0 / 20500.0"""
    if val is None: return 0.0
    if isinstance(val, (int, float)): return float(val)
    s = str(val).replace('.', '').strip()
    s = s.replace(',', '.')
    match = re.search(r'(\d+(\.\d+)?)', s)
    if match:
        try: return float(match.group(1))
        except: return 0.0
    return 0.0

def clean_price_and_currency(text: str) -> tuple[float, str]:
    """Detecta U$ o $ y devuelve (numero, moneda)"""
    if not text: return 0.0, "ARS"
    t = text.upper()
    currency = "USD" if ("U$" in t or "USD" in t) else "ARS"
    return as_number(t), currency

def _slug(text: str) -> str:
    return remove_accents(text).replace(" ", "-")

def cc_to_liters(val) -> str:
    """Convierte 1600 a '1.6 lts'"""
    num = as_number(val)
    if num <= 0: return None
    if num > 100: # Si es mayor a 100 asumimos que son CC
        return f"{round(num / 1000, 1)} lts"
    return f"{num} lts"

def format_consumption_carone(val) -> str:
    """Recibe 12 y devuelve '12 lts / 100km' (solo formato)"""
    num = as_number(val)
    if num <= 0: return None
    s_num = str(num).replace('.0', '').replace('.', ',')
    return f"{s_num} lts / 100km"