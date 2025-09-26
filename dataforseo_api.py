# dataforseo_api.py
# Cliente para interactuar con las APIs de DataForSEO

import requests, json
import logging
from typing import List, Dict, Any
import streamlit as st
from dfs_client import RestClient

logger = logging.getLogger(__name__)


@st.cache_data(show_spinner=False)
def dfs_live_serp(query: str, *, login: str, password: str, location_name: str, 
                  language_code:str, device: str, safe: str) -> Dict[str, Any]:
    """Call DataForSEO Google Organic (live/advanced). Returns JSON.
    Docs: https://api.dataforseo.com/v3/serp/google/organic/live/advanced
    """
    logger.info(f"Consultando SERP para: '{query}', location: {location_name}, device: {device}")
    client = RestClient(login, password)
    
    payload = [{
        "keyword": query,
        "location_name": location_name,
        "language_code": language_code,
        "device": device,
        "safe": safe,
    }]
    
    try:
        response = client.post("/v3/serp/google/organic/live/advanced", payload)
        logger.info(f"Respuesta SERP recibida para '{query}': {type(response)}")
        return response
    except Exception as e:
        logger.error(f"Error consultando SERP para '{query}': {str(e)}")
        raise


@st.cache_data(show_spinner=False)
def get_autocomplete(query: str, *, contry_iso_code: str, lang_iso: str) -> List[str]:
    """Google Autocomplete endpoint
    Receives query, country ISO code (gl), language ISO code (hl)."""
    try:
        
        params = {"output": "chrome",
                  "q": query,
                  "gl": contry_iso_code,
                  "hl": lang_iso}
        base_url = "https://suggestqueries.google.com/complete/search"        
        response = requests.get(base_url, params=params, timeout=30)
        results = json.loads(response.text)
        return results[1]
    except Exception:
        return []


def parse_serp_features(js: Dict[str, Any]) -> Dict[str, Any]:
    """Extract top organic, PAA, video carousel, AI Overviews, related searches, and images if present."""
    organic, paa, videos, ai_overview, related_searches, images = [], [], [], [], [], []
    tasks = js.get("tasks", [])
    
    for t in tasks:
        for res in t.get("result", []) or []:
            items = res.get("items", []) or []
            for it in items:
                tpe = it.get("type")
                
                if tpe == "organic":
                    link = it.get("url")
                    title = it.get("title")
                    snippet = (it.get("description") or "").strip()
                    if link and title:
                        organic.append({"title": title, "url": link, "snippet": snippet})
                
                elif tpe == "people_also_ask":
                    for q in it.get("items", []) or []:
                        qtext = q.get("title") or q.get("question")
                        if qtext:
                            paa.append(qtext)
                
                elif tpe in ("video", "video_carousel"):
                    for v in (it.get("items") or [{"title": it.get("title"), "url": it.get("url")}]):
                        if v and v.get("url"):
                            videos.append({"title": v.get("title"), "url": v.get("url")})
                
                elif tpe in ("ai_overview", "generative_overview", "ai_overview_box"):
                    content = it.get("text") or it.get("description") or it.get("content")
                    if content:
                        ai_overview.append(content)
                
                elif tpe == "related_searches":
                    search_items = it.get("items", []) or []
                    for search_term in search_items:
                        if isinstance(search_term, str) and search_term.strip():
                            related_searches.append(search_term.strip())
                
                elif tpe == "images":
                    for img in it.get("items", []) or []:
                        if img and img.get("image_url"):
                            images.append({
                                "alt": img.get("alt", ""),
                                "url": img.get("url", ""),
                                "image_url": img.get("image_url")
                            })
    
    return {
        "organic": organic, 
        "paa": paa, 
        "videos": videos, 
        "ai_overview": ai_overview,
        "related_searches": related_searches,
        "images": images
    }