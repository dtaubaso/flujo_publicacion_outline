# scraper.py
# Funciones para extraer contenido de páginas web

import random
import requests, urllib
from curl_cffi import requests as curl_requests
from typing import Dict, Any
from bs4 import BeautifulSoup
import trafilatura
import json
from config import USER_AGENTS


def http_get(url: str, timeout: int = 30) -> str:
    """Realiza una petición HTTP GET con User-Agent aleatorio"""
    headers = {"User-Agent": random.choice(USER_AGENTS)}
    r = curl_requests.get(url, impersonate='chrome', timeout=timeout)
    if r.status_code != 200:
        raise ValueError(f"Error al realizar la petición: {r.status_code}") 
    return r.text

def extract_domain(url: str) -> str:
    """Extrae el dominio base de una URL"""
    try:
        parsed = urllib.parse.urlparse(url)
        domain = parsed.netloc.lower()
        # limpiar subdominios comunes
        if domain.startswith("www."):
            domain = domain[4:]
        return domain
    except:
        return ""


def extract_article(url: str) -> Dict[str, Any]:
    """Extrae contenido de una página web usando trafilatura y BeautifulSoup"""
    try:
        html = http_get(url)
        
        # Usar trafilatura para extraer el contenido principal
        downloaded = trafilatura.extract(html, include_links=False, favor_recall=True, 
                                       with_metadata=True, url=url)
        
        # Usar BeautifulSoup para extraer headings
        soup = BeautifulSoup(html, "lxml")
        h_tags = {f"h{i}": [h.get_text(strip=True) for h in soup.find_all(f"h{i}")] 
                 for i in range(1, 7)}
        
        # Extraer título meta
        meta_title = soup.title.get_text(strip=True) if soup.title else None
        
        text = None
        meta = {}
        
        if downloaded:
            # Re-ejecutar trafilatura para obtener JSON estructurado
            json_struct = trafilatura.extract(html, include_comments=False, 
                                            output="json", url=url)
            if json_struct:
                meta = json.loads(json_struct)
                text = meta.get("text")
                if not meta_title:
                    meta_title = meta.get("title")
        
        if not text:
            # fallback: usar texto visible de BeautifulSoup
            text = soup.get_text(" ", strip=True)
        
        # Detectar elementos estructurales
        has_tables = bool(soup.find_all("table"))
        has_lists = bool(soup.find_all(["ul", "ol"]))
        
        return {
            "url": url,
            "site": extract_domain(url), 
            "title": meta_title,
            "text": text,
            "h2": h_tags.get("h2", []),
            "h3": h_tags.get("h3", []),
            "has_tables": has_tables,
            "has_lists": has_lists,
            "len_words": len((text or "").split()),
        }
    
    except Exception as e:
        return {"url": url, "error": str(e)}