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
    """Extract all SERP features: organic, PAA, videos, AI overview, related searches, images, top stories, twitter, carousel, knowledge graph."""
    organic, paa, videos, ai_overview, related_searches, images = [], [], [], [], [], []
    top_stories, twitter, carousel, knowledge_graph = [], [], [], []
    
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
                
                elif tpe == "top_stories":
                    for story in it.get("items", []) or []:
                        if story and story.get("url"):
                            top_stories.append({
                                "title": story.get("title", ""),
                                "url": story.get("url"),
                                "source": story.get("source", ""),
                                "domain": story.get("domain", ""),
                                "date": story.get("date", ""),
                                "timestamp": story.get("timestamp", ""),
                                "badges": story.get("badges", [])
                            })
                
                elif tpe == "twitter":
                    for tweet in it.get("items", []) or []:
                        if tweet and tweet.get("url"):
                            twitter.append({
                                "tweet": tweet.get("tweet", ""),
                                "url": tweet.get("url"),
                                "date": tweet.get("date", ""),
                                "timestamp": tweet.get("timestamp", "")
                            })
                
                elif tpe == "carousel":
                    carousel_title = it.get("title", "")
                    carousel_items = []
                    for item in it.get("items", []) or []:
                        if item:
                            carousel_items.append({
                                "title": item.get("title", ""),
                                "subtitle": item.get("subtitle", ""),
                                "image_url": item.get("image_url", ""),
                                "url": item.get("url", "")
                            })
                    if carousel_items:
                        carousel.append({
                            "title": carousel_title,
                            "items": carousel_items
                        })
                
                elif tpe == "knowledge_graph":
                    kg_data = {
                        "title": it.get("title", ""),
                        "subtitle": it.get("subtitle", ""),
                        "description": it.get("description", ""),
                        "url": it.get("url", ""),
                        "image_url": it.get("image_url", "")
                    }
                    # Extraer información estructurada del knowledge graph
                    kg_items = it.get("items", []) or []
                    structured_data = []
                    for kg_item in kg_items:
                        if kg_item.get("type") == "knowledge_graph_row_item":
                            structured_data.append({
                                "title": kg_item.get("title", ""),
                                "text": kg_item.get("text", "")
                            })
                    if structured_data:
                        kg_data["structured_data"] = structured_data
                    knowledge_graph.append(kg_data)
    
    return {
        "organic": organic, 
        "paa": paa, 
        "videos": videos, 
        "ai_overview": ai_overview,
        "related_searches": related_searches,
        "images": images,
        "top_stories": top_stories,
        "twitter": twitter,
        "carousel": carousel,
        "knowledge_graph": knowledge_graph
    }