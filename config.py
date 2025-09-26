# config.py
# Configuración y constantes de la aplicación

import os

# User Agents para web scraping
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
]

# URLs de APIs de DataForSEO
DATAFORSEO_SERP_URL = "https://api.dataforseo.com/v3/serp/google/organic/live/advanced"
DATAFORSEO_RELATED_URL = "https://api.dataforseo.com/v3/dataforseo_labs/google/related_keywords/live"
DATAFORSEO_AUTOCOMPLETE_URL = "https://api.dataforseo.com/v3/keywords_data/google_autocomplete/live"

# Configuración por defecto
DEFAULT_CONFIG = {
    "market": "Argentina",
    "lang": "es",
    "device": "desktop",
    "top_n": 5,
    "safe": "off",
    "gl": "ar",
    "pause": 0.8,
    "openai_model": "gpt-4.1",
    "openai_temperature": 0.4,
}

# Configuración de OpenAI
OPENAI_SYSTEM_PROMPT = """Eres un editor SEO especializado en contenido informativo y evergreen. 
Basándote en las señales de SERP de Google (PAA, búsquedas relacionadas, AI overview, videos) y lo que cubren los competidores, 
produce un outline de contenido superior en Markdown limpio. Incluye: 
1) Análisis de intención SERP y tipo (informacional, transaccional, navegacional, investigación comercial, local).
2) Tipos de contenido (multimedia) a incluir.
3) Longitud recomendada (justifica brevemente).
4) Anatomía del contenido (tablas, listas, comparaciones, FAQs).
5) Outline con H2/H3/H4.
6) Gaps de contenido vs top resultados.
7) N-gramas que aparecen frecuentemente en títulos (top 10).
8) Preguntas a responder (de PAA).
9) Búsquedas relacionadas y Autocomplete a cubrir como subtemas.
10) Si hay presencia de YouTube/video, sugiere dónde encaja.
Sé conciso y concreto. Evita relleno. Responde SIEMPRE en español."""