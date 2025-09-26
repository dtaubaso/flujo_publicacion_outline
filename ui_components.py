# ui_components.py
# Componentes de interfaz de usuario de Streamlit

import os, time, base64, re
import streamlit as st
from config import DEFAULT_CONFIG, OPENAI_NO_TEMPERATURE_MODELS, COUNTRY_ISO_TO_NAME


def setup_sidebar():
    """Configura la barra lateral con controles de la aplicación"""
    with st.sidebar:
        st.title("Profile builder")
        st.caption(
            "Generate an SEO‑aware content outline from a keyword or topic cluster, using Google SERP signals."
        )

        # Credenciales de DataForSEO
        st.subheader("DataForSEO credentials")
        dfs_login = st.text_input("Login (email)", value=os.getenv("DATAFORSEO_LOGIN", ""))
        dfs_password = st.text_input("Password", type="password", 
                                   value=os.getenv("DATAFORSEO_PASSWORD", ""))
        st.caption("Credentials are used only to call DataForSEO Live SERP endpoints during this session.")

        # OpenAI (opcional)
        st.subheader("OpenAI (optional)")
        openai_key = st.text_input("OPENAI_API_KEY", value=os.getenv("OPENAI_API_KEY", ""), 
                                 type="password")
        openai_model = st.text_input("Model", value=os.getenv("OPENAI_MODEL", DEFAULT_CONFIG["openai_model"]))
        
        # Verificar si el modelo soporta temperature
        model_supports_temperature = not any(no_temp_model in openai_model.lower() 
                                           for no_temp_model in OPENAI_NO_TEMPERATURE_MODELS)
        
        if model_supports_temperature:
            openai_temperature = st.slider("Temperature", 0.0, 1.2, DEFAULT_CONFIG["openai_temperature"], 0.1)
        else:
            st.info(f"ℹ️ El modelo {openai_model} no soporta el parámetro 'temperature'")
            openai_temperature = None
            
        use_openai = st.toggle("Use OpenAI to generate the outline", 
                             value=True)

        # Parámetros de búsqueda
        st.subheader("Parámetros de búsqueda")
        
        # Configuración de mercado
        st.markdown("**Ubicación y idioma:**")
        country_iso_code = st.text_input("Código de país (ISO)", value=DEFAULT_CONFIG["country_iso_code"], help="Ej: AR para Argentina, US para Estados Unidos")
        lang_iso_code = st.text_input("Código de idioma (ISO)", value=DEFAULT_CONFIG["lang_iso_code"], help="Ej: es para español, en para inglés")
        
        # Configuración técnica
        device = st.selectbox("Dispositivo", ["desktop", "mobile"], index=0)
        top_n = st.slider("Top resultados a analizar", 3, 20, DEFAULT_CONFIG["top_n"])

        # Opciones avanzadas
        with st.expander("Configuración avanzada"):
            language_code = st.text_input("language_code (DataForSEO)", value=DEFAULT_CONFIG["language_code"], help="Ej: es-AR para español de Argentina")
            safe = st.selectbox("Búsqueda segura", ["off", "moderate", "strict"], index=0)
            pause = st.number_input("Pausa entre peticiones (segundos)", 
                                  min_value=0.0, value=DEFAULT_CONFIG["pause"], step=0.1)
            
            st.markdown("**Para compatibilidad con APIs legacy:**")
            gl = st.text_input("gl (Google API - código de país)", value=country_iso_code)
            hl = st.text_input("hl (Google API - código de idioma)", value=lang_iso_code)

    # Obtener el nombre completo del país para DataForSEO
    location_name = COUNTRY_ISO_TO_NAME.get(country_iso_code, "Argentina")
    
    return {
        "dfs_login": dfs_login,
        "dfs_password": dfs_password,
        "openai_key": openai_key,
        "openai_model": openai_model,
        "openai_temperature": openai_temperature,
        "use_openai": use_openai,
        "country_iso_code": country_iso_code,
        "lang_iso_code": lang_iso_code,
        "language_code": language_code,
        "location_name": location_name,  # Nombre completo para DataForSEO
        "device": device,
        "top_n": top_n,
        "safe": safe,
        "gl": gl,
        "hl": hl,
        "pause": pause,
    }


def setup_main_input():
    """Configura la entrada principal de keywords"""
    st.header("Palabra clave → SERP → Outline")
    keywords_raw = st.text_area(
        "Lista de palabras clave o temas (una por línea)",
        placeholder="url o palabras clave (ej.: 'mejores celulares 2025' o varias palabras para un segmento)",
        height=120,
    )

    if keywords_raw:
        keywords = [k.strip() for k in keywords_raw.splitlines() if k.strip()]
    else:
        keywords = []

    run_btn = st.button("Ejecutar análisis", type="primary")
    
    return keywords, run_btn


def display_results_summary(organic, paa, videos, ai_overview):
    """Muestra resumen de resultados SERP"""
    st.write({
        "organic": len(organic), 
        "paa": len(paa), 
        "videos": len(videos), 
        "ai_overview": bool(ai_overview)
    })


def display_content_anatomy(df):
    """Muestra anatomía del contenido"""
    st.markdown("### Anatomía del contenido")
    anatomy = {
        "median_length_words": int(df["len_words"].replace(0, None).median() or 0),
        "has_tables": int(df["has_tables"].sum()),
        "has_lists": int(df["has_lists"].sum()),
    }
    st.write(anatomy)


def display_video_suggestions(videos):
    """Muestra sugerencias de video"""
    if videos:
        st.markdown("#### Candidatos de YouTube / video")
        for v in videos[:5]:
            url = v.get("url", "")
            if "youtube.com" in (url or ""):
                st.video(url)
            else:
                st.write(f"- {v.get('title')}: {url}")


def create_download_links(outline_md, df, keyword):
    """Crea botones de descarga"""
    
    clean_kw = re.sub(r'[^a-zA-Z0-9]+','_', keyword)
    # csv link
    csv = df.to_csv(index=False, encoding='utf-8')
    b64_csv = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64_csv}" download="outline_{clean_kw}_{int(time.time())}.csv">Descargar como CSV</a>'
    st.markdown(href, unsafe_allow_html=True)

    # markdown link
    b64_md = base64.b64encode(outline_md.encode()).decode()
    href_md = f'<a href="data:file/markdown;base64,{b64_md}" download="outline_{clean_kw}_{int(time.time())}.md">Descargar como Markdown</a>'
    st.markdown(href_md, unsafe_allow_html=True)
