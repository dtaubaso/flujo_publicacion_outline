# app.py
# Streamlit app: from a keyword (or list) → analyze SERP (DataForSEO) → scrape top results →
# synthesize intent, content anatomy, gaps → generate a superior content outline.
#
# ──────────────────────────────────────────────────────────────────────────────
# SETUP
# - Put your DataForSEO credentials in environment variables DATAFORSEO_LOGIN and DATAFORSEO_PASSWORD
#   or fill them in the sidebar (they'll only live for this session).
# - Install requirements from requirements.txt
# - Run: streamlit run app.py
#
# DISCLAIMER
# Respect target sites' terms and robots.txt. Use responsibly.

import time
import pandas as pd
import streamlit as st

# Imports de nuestros módulos
from dataforseo_api import dfs_live_serp, dfs_related_searches, dfs_autocomplete, parse_serp_features
from dfs_client import RestClient
from scraper import extract_article
from analytics import guess_intent, analyze_content_structure
from outline_generator import generate_outline_with_openai, build_outline
from ui_components import (
    setup_sidebar, 
    setup_main_input, 
    display_results_summary,
    display_content_anatomy,
    display_video_suggestions,
    create_download_buttons
)

# ──────────────────────────────────────────────────────────────────────────────
# UI CONFIG
st.set_page_config(page_title="Profile builder", page_icon="🧭", layout="wide")

# Configurar interfaz
config = setup_sidebar()
keywords, run_btn = setup_main_input()

# ──────────────────────────────────────────────────────────────────────────────
# MAIN EXECUTION

if run_btn:
    if not keywords:
        st.warning("Por favor ingresa al menos una palabra clave.")
        st.stop()
    if not config["dfs_login"] or not config["dfs_password"]:
        st.error("Las credenciales de DataForSEO son requeridas.")
        st.stop()

    tabs = st.tabs([f"{k}" for k in keywords])

    for tab, kw in zip(tabs, keywords):
        with tab:
            st.subheader(f"Keyword: {kw}")

            # Consultar SERP via DataForSEO
            with st.status("Consultando SERP de Google via DataForSEO…", expanded=False):
                js = dfs_live_serp(
                    kw, 
                    login=config["dfs_login"], 
                    password=config["dfs_password"],
                    location_name=config["loc_name"] or config["market"], 
                    gl=config["gl"] or "", 
                    hl=config["hl"] or config["lang"],
                    device=config["device"], 
                    safe=config["safe"]
                )
                features = parse_serp_features(js)
                organic = features["organic"][:config["top_n"]]
                paa = features["paa"]
                videos = features["videos"]
                ai_overview = features["ai_overview"]
                display_results_summary(organic, paa, videos, ai_overview)

            # Análisis de intent
            intent_label, intent_scores = guess_intent(organic, paa)
            st.markdown(f"**Intención (heurística)**: `{intent_label}`")
            st.json(intent_scores, expanded=False)

            # Scraping de resultados
            st.info(f"Extrayendo contenido de los top {len(organic)} resultados…")
            rows = []
            for i, item in enumerate(organic, 1):
                url = item.get("url")
                title = item.get("title")
                if not url:
                    continue
                time.sleep(config["pause"])
                data = extract_article(url)
                data["rank"] = i
                if not data.get("title"):
                    data["title"] = title
                rows.append(data)

            df = pd.DataFrame(rows)
            st.dataframe(df[["rank", "site", "title", "len_words", "has_tables", "has_lists", "url"]])

            # Anatomía del contenido
            display_content_anatomy(df)

            # Related searches y Autocomplete
            col1, col2 = st.columns(2)
            with col1:
                related = dfs_related_searches(
                    kw, 
                    login=config["dfs_login"], 
                    password=config["dfs_password"], 
                    location_name=config["loc_name"] or config["market"], 
                    gl=config["gl"], 
                    hl=config["hl"]
                )
                st.markdown("**Búsquedas relacionadas**")
                if related:
                    st.write(related[:15])
                else:
                    st.write("(ninguna)")
            
            with col2:
                auto = dfs_autocomplete(
                    kw, 
                    login=config["dfs_login"], 
                    password=config["dfs_password"], 
                    gl=config["gl"], 
                    hl=config["hl"]
                )
                st.markdown("**Autocompletado**")
                if auto:
                    st.write(auto[:15])
                else:
                    st.write("(ninguno)")

            # Generar outline
            outline_md = None
            if config["use_openai"] and config["openai_key"]:
                with st.spinner("Generando outline con OpenAI…"):
                    try:
                        outline_md = generate_outline_with_openai(
                            kw,
                            df=df,
                            paa=paa,
                            related=related or auto or [],
                            ai_overview=ai_overview,
                            videos=videos,
                            intent_label=intent_label,
                            intent_scores=intent_scores,
                            model=config["openai_model"],
                            api_key=config["openai_key"],
                            temperature=config["openai_temperature"],
                        )
                    except Exception as e:
                        st.warning(f"Outline con OpenAI falló ({e}). Usando outline heurístico.")
                        outline_md = None
            
            if not outline_md:
                outline_md = build_outline(
                    kw, 
                    scraped=df, 
                    paa=paa, 
                    related=related or auto, 
                    ai_overview=ai_overview
                )

            # Mostrar outline
            st.markdown("### Outline recomendado")
            st.markdown(outline_md)

            # Sugerencias de video
            display_video_suggestions(videos)

            # Botones de descarga
            create_download_buttons(outline_md, df, kw)