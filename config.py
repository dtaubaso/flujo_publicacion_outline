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
Basándote en las señales completas de SERP de Google (PAA, búsquedas relacionadas, AI overview, videos, top stories, tweets, carousels, knowledge graph) y lo que cubren los competidores, 
produce un outline de contenido superior en Markdown limpio. 

Analiza TODOS los elementos SERP disponibles:
- **Top Stories**: Si hay noticias destacadas, considera ángulo de actualidad/trending
- **Videos**: Si hay YouTube/videos, sugiere contenido multimedia específico  
- **Twitter**: Si hay tweets oficiales, incluye perspectiva de redes sociales
- **Carousel**: Si hay carruseles (libros, productos), analiza el tipo de contenido
- **Knowledge Graph**: Si hay panel de información, considera datos estructurados
- **PAA & Related**: Para subtemas y preguntas frecuentes
- **AI Overview**: Para entender el formato de respuesta preferido

Incluye obligatoriamente: 
1) **Análisis de intención SERP** y tipo (informacional, transaccional, navegacional, investigación comercial, local).
2) **Contexto de actualidad**: Si hay top stories, especifica estrategia de contenido noticioso/trending.
3) **Tipos de contenido multimedia** a incluir (basado en videos, carousels encontrados).
4) **Longitud recomendada** (justifica basándote en competidores).
5) **Anatomía del contenido** (tablas, listas, comparaciones, FAQs, elementos estructurados).
6) **Outline con H2/H3 reales** (formato SEO real, no ideas generales).
7) **Content gaps** vs top resultados actuales.
8) **N-gramas frecuentes** en títulos de competidores (top 10).
9) **Preguntas a responder** (extraídas de PAA).
10) **Subtemas relacionados** (búsquedas relacionadas + autocomplete).
11) **Estrategia multimedia específica** (YouTube, videos externos, carruseles).
12) **Elementos de actualidad** si hay top stories (noticias, eventos, trending).

Sé conciso y concreto. Evita relleno. Responde SIEMPRE en español. Genera un outline accionable y específico, no conceptos generales. No des preguntas de seguimiento, es una respuesta cerrada."""