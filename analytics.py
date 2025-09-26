# analytics.py
# Funciones de análisis de contenido e intent

import re
import numpy as np
from typing import List, Dict, Any, Tuple
from sklearn.feature_extraction.text import CountVectorizer


def guess_intent(serp_snippets: List[Dict[str, Any]], paa: List[str]) -> Tuple[str, Dict[str, float]]:
    """Heuristic intent classifier based on snippets, PAA patterns, and SERP mix."""
    text = " ".join([(x.get("title") or "") + " " + (x.get("snippet") or "") 
                    for x in serp_snippets]).lower()
    text += " " + " ".join(paa).lower()
    
    scores = {
        "informational": 0.0,
        "transactional": 0.0,
        "navigational": 0.0,
        "commercial_investigation": 0.0,
        "local": 0.0,
    }
    
    kw = lambda *xs: any(x in text for x in xs)
    
    # Patrones de intent en español
    if kw("cómo", "que es", "qué es", "guía", "explicación", "review", "reseña", "vs "):
        scores["informational"] += 1.5
    if kw("comprar", "precio", "$", "oferta", "tienda", "dónde comprar"):
        scores["transactional"] += 1.5
    if kw("sitio oficial", "oficial", "inicio", "login", "marcapágina"):
        scores["navigational"] += 1.0
    if kw("mejores", "top", "ranking", "comparativa", "comparación"):
        scores["commercial_investigation"] += 1.5
    if kw("cerca", "cercano", "cerca de mí", "mapa", "dirección", "teléfono"):
        scores["local"] += 1.0
    
    # Normalizar y seleccionar
    label = max(scores, key=scores.get)
    total = sum(scores.values()) or 1.0
    probs = {k: v/total for k, v in scores.items()}
    
    return label, probs


def ngrams_top(texts: List[str], n: Tuple[int, int] = (1, 2), topk: int = 20) -> List[Tuple[str, int]]:
    """Extrae los n-gramas más frecuentes de una lista de textos"""
    if not texts:
        return []
    
    vect = CountVectorizer(ngram_range=n, lowercase=True, stop_words=None, 
                          token_pattern=r"(?u)\b\w+\b")
    X = vect.fit_transform(texts)
    sums = np.array(X.sum(axis=0)).ravel()
    items = list(zip(vect.get_feature_names_out(), sums))
    items.sort(key=lambda x: x[1], reverse=True)
    return items[:topk]


def analyze_content_structure(df) -> Dict[str, Any]:
    """Analiza la estructura del contenido extraído"""
    return {
        "median_length_words": int(df["len_words"].replace(0, np.nan).median(skipna=True) or 0),
        "has_tables": int(df["has_tables"].sum()),
        "has_lists": int(df["has_lists"].sum()),
        "total_h2": sum(len(h2) for h2 in df["h2"].dropna() if h2),
        "total_h3": sum(len(h3) for h3 in df["h3"].dropna() if h3),
    }