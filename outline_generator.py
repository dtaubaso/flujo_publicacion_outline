# outline_generator.py
# Generación de outlines usando OpenAI y métodos heurísticos

import json
import re
from typing import List, Dict, Any
import pandas as pd
import numpy as np
from analytics import ngrams_top
from config import OPENAI_SYSTEM_PROMPT

try:
    from openai import OpenAI
except Exception:
    OpenAI = None


def generate_top_stories_markdown(top_stories: List[dict]) -> str:
    """Genera markdown de top stories encontradas en SERP"""
    if not top_stories:
        return ""
    
    lines = []
    lines.append("## 📰 Top Stories (Noticias Destacadas)")
    lines.append("")
    lines.append("**Encontradas en SERP - Oportunidad de contenido noticioso/trending:**")
    lines.append("")
    
    for i, story in enumerate(top_stories[:7], 1):
        title = story.get("title", "Sin título")
        source = story.get("source", "Sin fuente")
        url = story.get("url", "")
        date = story.get("date", "")
        
        if title:
            lines.append(f"### {i}. {title}")
            if source:
                lines.append(f"**Fuente**: {source}")
            if date:
                lines.append(f"**Fecha**: {date}")
            if url:
                lines.append(f"**URL**: {url}")
            lines.append("")
    
    lines.append("**💡 Estrategia**: Si hay top stories, considerar:")
    lines.append("- Ángulo de actualidad/trending en el contenido")
    lines.append("- Referencias a noticias recientes")
    lines.append("- Actualización más frecuente del contenido")
    lines.append("- Aprovechar el momentum de búsquedas relacionadas")
    lines.append("")
    
    return "\n".join(lines)


def generate_video_suggestions_markdown(videos: List[dict]) -> str:
    """Genera markdown de sugerencias de video"""
    if not videos:
        return ""
    
    lines = []
    lines.append("## 📹 Sugerencias de Video (encontradas en SERP)")
    lines.append("")
    
    for i, video in enumerate(videos[:5], 1):
        title = video.get("title", "Sin título")
        url = video.get("url", "")
        if url:
            lines.append(f"### {i}. {title}")
            lines.append(f"**URL**: {url}")
            if "youtube.com" in url:
                lines.append("**Tipo**: YouTube video")
            else:
                lines.append("**Tipo**: Video externo")
            lines.append("")
    
    lines.append("**💡 Recomendación**: Analizar estos videos para identificar oportunidades de crear contenido similar o superior.")
    lines.append("")
    
    return "\n".join(lines)


def generate_outline_with_openai(keyword: str, *, df: pd.DataFrame, paa: list, 
                               related: list, ai_overview: list, videos: list, top_stories: list = None,
                               intent_label: str, intent_scores: dict, model: str, 
                               api_key: str, temperature: float = None) -> str:
    """Genera outline usando OpenAI"""
    if not (OpenAI and api_key):
        raise RuntimeError("OpenAI SDK not available or API key missing")
    
    client = OpenAI(api_key=api_key)

    # Construir payload compacto para el modelo
    payload = {
        "keyword": keyword,
        "intent": {"label": intent_label, "scores": intent_scores},
        "serp_signals": {
            "paa": paa[:20],
            "related": (related or [])[:20],
            "ai_overview_present": bool(ai_overview),
            "videos": videos[:5],
            "top_stories": (top_stories or [])[:5],
        },
        "scraped_summary": {
            "median_length_words": int(df["len_words"].replace(0, np.nan).median(skipna=True) or 0),
            "has_tables": int(df["has_tables"].sum()),
            "has_lists": int(df["has_lists"].sum()),
            "titles": [t for t in df["title"].dropna().tolist() if t][:20],
            "h2": [h for arr in df["h2"].dropna().tolist() for h in (arr or [])][:40],
            "h3": [h for arr in df["h3"].dropna().tolist() for h in (arr or [])][:40],
        }
    }

    # Construir parámetros para la llamada a OpenAI
    api_params = {
        "model": model,
        "input": [
            {"role": "system", "content": OPENAI_SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps(payload, ensure_ascii=False)}
        ],
    }
    
    # Solo agregar temperature si el modelo lo soporta
    if temperature is not None:
        api_params["temperature"] = temperature

    resp = client.responses.create(**api_params)

    # Extraer contenido del texto (soporta nueva estructura SDK)
    try:
        content = resp.output_text
    except Exception:
        # Fallback para SDKs más antiguos
        content = resp.choices[0].message.content if getattr(resp, "choices", None) else str(resp)
    
    return content


def build_outline(keyword: str, *, scraped: pd.DataFrame, paa: List[str], 
                 related: List[str], ai_overview: List[str], videos: List[dict] = None, 
                 top_stories: List[dict] = None) -> str:
    """Compose a Markdown outline: H2/H3, PAA, gaps, multimedia suggestions."""
    titles = [t for t in scraped["title"].dropna().tolist() if t]
    heads2 = [h for arr in scraped["h2"].dropna().tolist() for h in (arr or [])]
    heads3 = [h for arr in scraped["h3"].dropna().tolist() for h in (arr or [])]
    grams = ngrams_top(titles, (1,2), 20)

    avg_len = int(scraped["len_words"].replace(0, np.nan).median(skipna=True) or 0)
    has_tables = scraped["has_tables"].sum() > 0
    has_lists = scraped["has_lists"].sum() > 0

    lines = []
    lines.append(f"# Outline: {keyword}\n")
    
    # Meta información
    lines.append("## Meta")
    lines.append(f"- Longitud sugerida: ~{max(400, min(2200, int(avg_len*1.1)))} palabras (promedio en SERP ≈ {avg_len})")
    content_bits = []
    if has_lists: 
        content_bits.append("lista con bullets")
    if has_tables: 
        content_bits.append("tabla de comparación")
    if content_bits: 
        lines.append("- Incluir: " + ", ".join(content_bits))
    if ai_overview:
        lines.append("- **AI Overview presente**: Considere una caja de resumen y citas en la primera pantalla.")
    if top_stories:
        lines.append(f"- **Top Stories presente**: {len(top_stories)} noticias destacadas - Considerar ángulo de actualidad")

    # Información contextual de SERP
    if top_stories:
        lines.append("\n## Contexto de Actualidad")
        lines.append(f"**Se encontraron {len(top_stories)} noticias destacadas**, lo que indica:")
        lines.append("- Alta búsqueda por información reciente")
        lines.append("- Oportunidad de contenido con ángulo noticioso")
        lines.append("- Posible estacionalidad o evento trending")
        lines.append("")
        lines.append("**Top Stories más relevantes:**")
        for i, story in enumerate(top_stories[:3], 1):
            title = story.get('title', 'Sin título')
            source = story.get('source', 'Sin fuente')
            lines.append(f"{i}. \"{title}\" - {source}")
        lines.append("")
    lines.append(f"# Outline: {keyword}\n")
    
    # Meta información
    lines.append("## Meta")
    lines.append(f"- Longitud sugerida: ~{max(400, min(2200, int(avg_len*1.1)))} palabras (promedio en SERP ≈ {avg_len})")
    content_bits = []
    if has_lists: 
        content_bits.append("lista con bullets")
    if has_tables: 
        content_bits.append("tabla de comparación")
    if content_bits: 
        lines.append("- Incluir: " + ", ".join(content_bits))
    if ai_overview:
        lines.append("- **AI Overview presente**: Considere una caja de resumen y citas en la primera pantalla.")

    # Estructura H2/H3
    lines.append("\n## Estructura H2/H3 (borrador)")
    seen = set()
    
    def add_head(h):
        h = re.sub(r"\s+", " ", h).strip()
        if h and h.lower() not in seen:
            lines.append(f"- {h}")
            seen.add(h.lower())

    # Empezar con temas dominantes (n-gramas), luego headings de competidores
    for g, _ in grams[:8]:
        add_head(g.title())
    for h in heads2[:12]:
        add_head(h)

    # Agregar sección FAQs desde PAA
    if paa:
        lines.append("\n### Preguntas frecuentes (de PAA)")
        for q in paa[:10]:
            lines.append(f"- {q}")

    # Related searches como subtemas
    if related:
        lines.append("\n### Subtemas relacionados (Related searches)")
        for r in related[:10]:
            lines.append(f"- {r}")

    # Sugerencia multimedia
    lines.append("\n## Multimedia")
    
    # Sugerencias específicas de video encontradas en SERP
    if videos:
        lines.append("\n### Contenido de video sugerido (encontrado en SERP)")
        for i, video in enumerate(videos[:5], 1):
            title = video.get("title", "Sin título")
            url = video.get("url", "")
            if url:
                lines.append(f"{i}. **{title}**")
                lines.append(f"   - URL: {url}")
                if "youtube.com" in url:
                    lines.append(f"   - Tipo: YouTube video")
                else:
                    lines.append(f"   - Tipo: Video externo")
                lines.append("")
    
    # Sugerencias generales de multimedia
    lines.append("### Estrategia multimedia general")
    if videos:
        lines.append("- ✅ **Videos encontrados en SERP** - Considerar crear contenido similar o de mayor calidad")
    else:
        lines.append("- **Videos**: No se encontraron videos en SERP, oportunidad para contenido original")
    lines.append("- **Imágenes**: Incluir capturas, infografías o comparativas según el tipo de contenido")
    lines.append("- **Elementos interactivos**: Tablas, listas numeradas, bullets para mejor legibilidad")

    # Content gaps heurístico
    lines.append("\n## Content gaps (heurístico)")
    all_text = " \n".join((scraped["text"].dropna().tolist()))
    if "precio" not in all_text.lower():
        lines.append("- Falta abordar precios/variantes por modelo o proveedor")
    if "compar" not in all_text.lower():
        lines.append("- Falta una tabla comparativa clara")
    if len(related) and not any("pros" in h.lower() or "contras" in h.lower() 
                               for h in heads2 + heads3):
        lines.append("- Agregar sección de pros y contras resumida")

    return "\n".join(lines)
