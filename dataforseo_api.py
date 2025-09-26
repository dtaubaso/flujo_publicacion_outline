# dataforseo_api.py
# Cliente para interactuar con las APIs de DataForSEO

import requests
from typing import List, Dict, Any
import streamlit as st
from config import DATAFORSEO_SERP_URL, DATAFORSEO_RELATED_URL, DATAFORSEO_AUTOCOMPLETE_URL
from dfs_client import RestClient


@st.cache_data(show_spinner=False)
def dfs_live_serp(query: str, *, login: str, password: str, location_name: str, 
                  gl: str, hl: str, device: str, safe: str) -> Dict[str, Any]:
    """Call DataForSEO Google Organic (live/advanced). Returns JSON.
    Docs: https://api.dataforseo.com/v3/serp/google/organic/live/advanced
    """
    client = RestClient(login, password)
    
    payload = [{
        "keyword": query,
        "location_name": location_name,
        "gl": gl,
        "hl": hl,
        "device": device,
        "safe": safe,
    }]
    
    response = client.post("/v3/serp/google/organic/live/advanced", payload)
    return response


@st.cache_data(show_spinner=False)
def dfs_related_searches(query: str, *, login: str, password: str, location_name: str, 
                        gl: str, hl: str) -> List[str]:
    """DataForSEO related searches (if available via the same endpoint's extra results). 
    Fallback: Google Autocomplete endpoint."""
    try:
        client = RestClient(login, password)
        
        payload = [{
            "keyword": query,
            "location_name": location_name,
            "gl": gl,
            "hl": hl,
        }]
        
        response = client.post("/v3/dataforseo_labs/google/related_searches/live", payload)
        out = []
        for task in response.get("tasks", []):
            for rs in task.get("result", []) or []:
                for item in rs.get("items", []) or []:
                    kw = item.get("keyword")
                    if kw:
                        out.append(kw)
        return sorted(set(out))
    except Exception:
        return []


@st.cache_data(show_spinner=False)
def dfs_autocomplete(query: str, *, login: str, password: str, gl: str, hl: str) -> List[str]:
    """DataForSEO Google Autocomplete endpoint"""
    try:
        client = RestClient(login, password)
        
        payload = [{"keyword": query, "gl": gl, "hl": hl}]
        
        response = client.post("/v3/keywords_data/google_autocomplete/live", payload)
        suggests = []
        for task in response.get("tasks", []):
            for res in task.get("result", []) or []:
                for it in res.get("items", []) or []:
                    v = it.get("suggestion")
                    if v:
                        suggests.append(v)
        return sorted(set(suggests))
    except Exception:
        return []


def parse_serp_features(js: Dict[str, Any]) -> Dict[str, Any]:
    """Extract top organic, PAA, video carousel, AI Overviews if present."""
    organic, paa, videos, ai_overview = [], [], [], []
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
                    # Different accounts/versions may label this differently over time
                    content = it.get("text") or it.get("description") or it.get("content")
                    if content:
                        ai_overview.append(content)
    
    return {"organic": organic, "paa": paa, "videos": videos, "ai_overview": ai_overview}