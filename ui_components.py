# ui_components.py
# Componentes de interfaz de usuario de Streamlit

import os
import streamlit as st
from config import DEFAULT_CONFIG


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
        openai_temperature = st.slider("Temperature", 0.0, 1.2, DEFAULT_CONFIG["openai_temperature"], 0.1)
        use_openai = st.toggle("Use OpenAI to generate the outline", 
                             value=bool(os.getenv("OPENAI_API_KEY") or ""))

        # Parámetros de búsqueda
        st.subheader("Search parameters")
        market = st.text_input("Market / Location", value=DEFAULT_CONFIG["market"])
        lang = st.text_input("Interface language (hl)", value=DEFAULT_CONFIG["lang"])
        device = st.selectbox("Device", ["desktop", "mobile"], index=0)
        top_n = st.slider("Top results to analyze", 3, 20, DEFAULT_CONFIG["top_n"])

        # Opciones avanzadas
        with st.expander("Opciones avanzadas"):
            safe = st.selectbox("Safe search", ["off", "moderate", "strict"], index=0)
            gl = st.text_input("gl (código de país)", value=DEFAULT_CONFIG["gl"])
            hl = st.text_input("hl (código de idioma)", value=lang)
            loc_name = st.text_input("location_name exacto (DataForSEO)", value=market)
            pause = st.number_input("Pausa entre peticiones (segundos)", 
                                  min_value=0.0, value=DEFAULT_CONFIG["pause"], step=0.1)

    return {
        "dfs_login": dfs_login,
        "dfs_password": dfs_password,
        "openai_key": openai_key,
        "openai_model": openai_model,
        "openai_temperature": openai_temperature,
        "use_openai": use_openai,
        "market": market,
        "lang": lang,
        "device": device,
        "top_n": top_n,
        "safe": safe,
        "gl": gl,
        "hl": hl,
        "loc_name": loc_name,
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


def create_download_buttons(outline_md, df, keyword):
    """Crea botones de descarga"""
    import re
    
    clean_kw = re.sub(r'[^a-zA-Z0-9]+','_', keyword)
    
    st.download_button(
        "Descargar outline (Markdown)",
        data=outline_md,
        file_name=f"outline_{clean_kw}.md",
        mime="text/markdown",
    )
    
    st.download_button(
        "Descargar dataset extraído (CSV)",
        data=df.to_csv(index=False),
        file_name=f"scraped_{clean_kw}.csv",
        mime="text/csv",
    )