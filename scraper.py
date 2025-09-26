# scraper.py
# Funciones para extraer contenido de páginas web

import random
import requests, urllib
import logging
from curl_cffi import requests as curl_requests
from typing import Dict, Any
from bs4 import BeautifulSoup, Comment
import re
from config import USER_AGENTS

logger = logging.getLogger(__name__)


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
        if not url:
            return ""
        parsed = urllib.parse.urlparse(url)
        domain = parsed.netloc.lower()
        # limpiar subdominios comunes
        if domain.startswith("www."):
            domain = domain[4:]
        return domain
    except Exception:
        return url  # Si falla el parsing, devolver la URL original
    except:
        return ""


def extract_article(url: str) -> Dict[str, Any]:
    """Extrae contenido de una página web usando solo curl_cffi y BeautifulSoup"""
    logger.info(f"Iniciando extracción de: {url}")
    try:
        html = http_get(url)
        logger.info(f"HTML obtenido: {len(html)} caracteres")
        
        # Parsear HTML con BeautifulSoup
        soup = BeautifulSoup(html, "lxml")
        logger.info("HTML parseado con BeautifulSoup")
        
        # Extraer título
        meta_title = ""
        if soup.title:
            meta_title = soup.title.get_text(strip=True)
        elif soup.find("h1"):
            meta_title = soup.find("h1").get_text(strip=True)
        
        # Extraer headings estructurados
        h_tags = {}
        for i in range(1, 7):
            headings = soup.find_all(f"h{i}")
            h_tags[f"h{i}"] = [h.get_text(strip=True) for h in headings if h.get_text(strip=True)]
        
        # Remover elementos no deseados (scripts, styles, navigation, etc.)
        for element in soup(["script", "style", "nav", "header", "footer", "aside", 
                           "noscript", "iframe", "form", "button"]):
            element.decompose()
        
        # Remover comentarios HTML
        for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
            comment.extract()
        
        # Remover elementos con clases/ids comunes de navegación, ads, etc.
        unwanted_patterns = [
            'nav', 'navigation', 'menu', 'sidebar', 'footer', 'header',
            'ad', 'ads', 'advertisement', 'promo', 'banner',
            'social', 'share', 'related', 'comment', 'widget'
        ]
        
        for pattern in unwanted_patterns:
            for element in soup.find_all(attrs={"class": re.compile(pattern, re.I)}):
                element.decompose()
            for element in soup.find_all(attrs={"id": re.compile(pattern, re.I)}):
                element.decompose()
        
        # Buscar el contenido principal
        main_content = None
        
        # Intentar encontrar elementos de contenido principal
        content_selectors = [
            'article', 
            '[role="main"]',
            'main',
            '.content',
            '.post-content', 
            '.entry-content',
            '.article-content',
            '#content',
            '#main-content'
        ]
        
        for selector in content_selectors:
            main_content = soup.select_one(selector)
            if main_content:
                logger.info(f"Contenido encontrado con selector: {selector}")
                break
        
        # Si no se encontró contenido específico, usar todo el body
        if not main_content:
            main_content = soup.find('body')
            if not main_content:
                main_content = soup
        
        # Extraer texto del contenido principal
        text = ""
        if main_content:
            # Obtener todos los párrafos y elementos de texto
            text_elements = main_content.find_all(['p', 'div', 'span', 'li', 'td', 'th'])
            text_parts = []
            
            for element in text_elements:
                element_text = element.get_text(strip=True)
                if element_text and len(element_text) > 20:  # Filtrar textos muy cortos
                    text_parts.append(element_text)
            
            text = " ".join(text_parts)
            
            # Si no hay suficiente texto, usar todo el texto visible
            if len(text.split()) < 50:
                text = main_content.get_text(" ", strip=True)
        
        # Limpiar texto
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Detectar elementos estructurales
        has_tables = bool(soup.find_all("table"))
        has_lists = bool(soup.find_all(["ul", "ol"]))
        
        result = {
            "url": url,
            "site": extract_domain(url), 
            "title": meta_title,
            "text": text,
            "h2": h_tags.get("h2", []),
            "h3": h_tags.get("h3", []),
            "has_tables": has_tables,
            "has_lists": has_lists,
            "len_words": len(text.split()),
        }
        
        logger.info(f"Extracción exitosa: {result['len_words']} palabras, {len(result['h2'])} H2s, {len(result['h3'])} H3s")
        return result
    
    except Exception as e:
        logger.error(f"Error en extract_article para {url}: {str(e)}")
        return {
            "url": url,
            "site": extract_domain(url) if url else "",
            "title": "",
            "text": "",
            "h2": [],
            "h3": [],
            "has_tables": False,
            "has_lists": False,
            "len_words": 0,
            "error": str(e)
        }