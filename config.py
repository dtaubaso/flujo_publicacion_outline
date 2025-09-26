# config.py
# Configuración y constantes de la aplicación

import os

# User Agents para web scraping
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
]

# Mapeo de códigos ISO de país a nombres completos para DataForSEO
COUNTRY_ISO_TO_NAME = {
    "AR": "Argentina",
    "US": "United States", 
    "ES": "Spain",
    "MX": "Mexico",
    "CO": "Colombia",
    "CL": "Chile",
    "PE": "Peru",
    "VE": "Venezuela",
    "EC": "Ecuador",
    "BO": "Bolivia",
    "UY": "Uruguay",
    "PY": "Paraguay",
    "BR": "Brazil",
    "GB": "United Kingdom",
    "DE": "Germany",
    "FR": "France",
    "IT": "Italy",
    "CA": "Canada",
    "AU": "Australia"
}



# Configuración por defecto
DEFAULT_CONFIG = {
    "language_code": "es",  # Código de idioma para DataForSEO
    "country_iso_code": "AR",  # Código ISO para Google Autocomplete
    "lang_iso_code": "es-419",  # Código ISO de idioma para Google Autocomplete
    "device": "desktop",
    "top_n": 5,
    "safe": "off",
    "pause": 0.8,
    "openai_model": "gpt-5-nano",
    "openai_temperature": 0.4,
}

# Modelos de OpenAI que NO soportan temperature
OPENAI_NO_TEMPERATURE_MODELS = [
    "o1", "o1-preview", "o1-mini",
    "o5", "o5-preview", "o5-mini",
    "gpt-5", "gpt-5-nano", "gpt-5-preview"
]

# Configuración de OpenAI
OPENAI_SYSTEM_PROMPT = """Eres un editor SEO especializado en contenido informativo y evergreen. 
Basándote en las señales de SERP de Google (PAA, búsquedas relacionadas, AI overview, videos) y lo que cubren los competidores, 
produce un outline de contenido superior en Markdown limpio. Incluye: 
1) Análisis de intención SERP y tipo (informacional, transaccional, navegacional, investigación comercial, local).
2) Tipos de contenido (multimedia) a incluir.
3) Longitud recomendada (justifica brevemente).
4) Anatomía del contenido (tablas, listas, comparaciones, FAQs).
5) Outline con subtítulos H2 (con formato de subtítulo real SEO, no una "idea").
6) Gaps de contenido vs top resultados.
7) N-gramas que aparecen frecuentemente en títulos (top 10).
8) Preguntas a responder (de PAA).
9) Búsquedas relacionadas y Autocomplete a cubrir como subtemas.
10) Si hay presencia de YouTube/video, sugiere dónde encaja.
Sé conciso y concreto. Evita relleno. Responde SIEMPRE en español. No des preguntas de seguimiento, es una respuesta cerrada"""