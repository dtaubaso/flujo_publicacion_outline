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
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)
logger = logging.getLogger(__name__)

# Imports de nuestros módulos
from dataforseo_api import dfs_live_serp, get_autocomplete, parse_serp_features
from dfs_client import RestClient
from scraper import extract_article
from analytics import guess_intent, analyze_content_structure
from outline_generator import generate_outline_with_openai, build_outline, generate_video_suggestions_markdown
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

def main():
    """Función principal de la aplicación Streamlit"""
    logger.info("=== INICIANDO APLICACIÓN ===")
    st.set_page_config(page_title="Generador de outline SEO", page_icon="🧭", layout="wide")

    # Configurar interfaz
    logger.info("Configurando interfaz de usuario...")
    config = setup_sidebar()
    logger.info(f"Config obtenida: {list(config.keys())}")
    
    keywords, run_btn = setup_main_input()
    logger.info(f"Keywords ingresadas: {keywords}")
    logger.info(f"Botón presionado: {run_btn}")

    # ──────────────────────────────────────────────────────────────────────────────
    # MAIN EXECUTION

    if run_btn:
        logger.info("=== INICIANDO ANÁLISIS ===")
        if not keywords:
            logger.warning("No se ingresaron keywords")
            st.warning("Por favor ingresa al menos una palabra clave.")
            st.stop()
        if not config["dfs_login"] or not config["dfs_password"]:
            logger.error("Credenciales de DataForSEO faltantes")
            st.error("Las credenciales de DataForSEO son requeridas.")
            st.stop()

        logger.info(f"Procesando {len(keywords)} keywords: {keywords}")
        tabs = st.tabs([f"{k}" for k in keywords])

        for tab, kw in zip(tabs, keywords):
            with tab:
                logger.info(f"--- PROCESANDO KEYWORD: {kw} ---")
                st.subheader(f"Keyword: {kw}")

                # Consultar SERP via DataForSEO
                logger.info(f"Consultando SERP para: {kw}")
                with st.status("Consultando SERP de Google via DataForSEO…", expanded=False):
                    try:
                        js = dfs_live_serp(
                            kw, 
                            login=config["dfs_login"], 
                            password=config["dfs_password"],
                            location_name=config["location_name"], 
                            language_code=config["language_code"],
                            device=config["device"], 
                            safe=config["safe"]
                        )
                        logger.info(f"Respuesta SERP recibida: {type(js)}, keys: {js.keys() if isinstance(js, dict) else 'No dict'}")
                        
                        features = parse_serp_features(js)
                        logger.info(f"Features parseadas: organic={len(features['organic'])}, paa={len(features['paa'])}, videos={len(features['videos'])}, ai_overview={len(features['ai_overview'])}, related_searches={len(features['related_searches'])}")
                        
                        organic = features["organic"][:config["top_n"]]
                        paa = features["paa"]
                        videos = features["videos"]
                        ai_overview = features["ai_overview"]
                        related_searches = features["related_searches"]
                        logger.info(f"Usando top {len(organic)} resultados orgánicos")
                        logger.info(f"Related searches extraídas del SERP: {len(related_searches)}")
                        
                        display_results_summary(organic, paa, videos, ai_overview)
                    except Exception as e:
                        logger.error(f"Error consultando SERP: {str(e)}")
                        st.error(f"Error consultando SERP: {str(e)}")
                        continue

                # Análisis de intent
                logger.info("Analizando intención de búsqueda...")
                intent_label, intent_scores = guess_intent(organic, paa)
                logger.info(f"Intent detectado: {intent_label}, scores: {intent_scores}")
                st.markdown(f"**Intención (heurística)**: `{intent_label}`")
                st.json(intent_scores, expanded=False)

                # Scraping de resultados
                logger.info(f"Iniciando scraping de {len(organic)} resultados...")
                st.info(f"Extrayendo contenido de los top {len(organic)} resultados…")
                rows = []
                for i, item in enumerate(organic, 1):
                    url = item.get("url")
                    title = item.get("title")
                    logger.info(f"Scraping {i}/{len(organic)}: {url}")
                    if not url:
                        logger.warning(f"URL vacía en resultado {i}")
                        continue
                    time.sleep(config["pause"])
                    try:
                        data = extract_article(url)
                        logger.info(f"Scraping exitoso: {url} -> {data.get('len_words', 0)} palabras")
                    except Exception as e:
                        logger.error(f"Error scraping {url}: {str(e)}")
                        data = {
                            "url": url, "site": url, "title": title or "", "text": "", 
                            "h2": [], "h3": [], "has_tables": False, "has_lists": False, 
                            "len_words": 0, "error": str(e)
                        }
                    data["rank"] = i
                    if not data.get("title"):
                        data["title"] = title
                    rows.append(data)
                    logger.info(f"Datos agregados para {url}: {list(data.keys())}")

                logger.info(f"Creando DataFrame con {len(rows)} filas...")
                df = pd.DataFrame(rows)
                logger.info(f"DataFrame creado. Shape: {df.shape}, Columnas: {list(df.columns)}")
                
                # Debug: mostrar columnas disponibles si hay error
                st.write("**Columnas disponibles en el DataFrame:**", list(df.columns))
                st.write("**Primeras filas:**")
                st.write(df.head())
                logger.info(f"Mostrando DataFrame en UI: shape={df.shape}")
                
                # Verificar que las columnas existen antes de mostrar
                expected_cols = ["rank", "site", "title", "len_words", "has_tables", "has_lists", "url"]
                available_cols = [col for col in expected_cols if col in df.columns]
                logger.info(f"Columnas esperadas: {expected_cols}")
                logger.info(f"Columnas disponibles: {available_cols}")
                
                if available_cols:
                    logger.info(f"Mostrando columnas disponibles: {available_cols}")
                    st.dataframe(df[available_cols])
                else:
                    logger.error("Error: No se pudieron extraer las columnas esperadas del contenido web")
                    st.error("Error: No se pudieron extraer las columnas esperadas del contenido web")
                    st.write("Datos extraídos:", df)

                # Anatomía del contenido
                logger.info("Mostrando anatomía del contenido...")
                display_content_anatomy(df)

                # Related searches y Autocomplete
                logger.info("Mostrando búsquedas relacionadas y autocompletado...")
                col1, col2 = st.columns(2)
                with col1:
                    # Las related searches ya están extraídas del SERP
                    related = related_searches
                    logger.info(f"Related searches del SERP: {len(related)} resultados")
                        
                    st.markdown("**Búsquedas relacionadas**")
                    if related:
                        st.write(related[:15])
                    else:
                        st.write("(ninguna)")
                
                with col2:
                    try:
                        auto = get_autocomplete(
                            kw, 
                            contry_iso_code=config["country_iso_code"], 
                            lang_iso=config["lang_iso_code"]
                        )
                        logger.info(f"Autocomplete obtenido: {len(auto)} resultados")
                    except Exception as e:
                        logger.error(f"Error obteniendo autocomplete: {str(e)}")
                        auto = []
                    st.markdown("**Autocompletado**")
                    if auto:
                        st.write(auto[:15])
                    else:
                        st.write("(ninguno)")

                # Generar outline
                logger.info("Iniciando generación de outline...")
                outline_md = None
                if config["use_openai"] and config["openai_key"]:
                    logger.info("Usando OpenAI para generar outline...")
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
                            logger.info(f"Outline generado con OpenAI: {len(outline_md)} caracteres")
                        except Exception as e:
                            logger.error(f"Error generando outline con OpenAI: {str(e)}")
                            st.warning(f"Outline con OpenAI falló ({e}). Usando outline heurístico.")
                            outline_md = None
                
                if not outline_md:
                    logger.info("Usando método heurístico para generar outline...")
                    outline_md = build_outline(
                        kw, 
                        scraped=df, 
                        paa=paa, 
                        related=related or auto, 
                        ai_overview=ai_overview,
                        videos=videos
                    )
                    logger.info(f"Outline generado con método heurístico: {len(outline_md)} caracteres")

                # Agregar sugerencias de video al markdown para exportación
                video_suggestions_md = generate_video_suggestions_markdown(videos)
                full_outline_md = outline_md
                if video_suggestions_md:
                    full_outline_md += "\n\n" + video_suggestions_md
                
                # Mostrar outline
                logger.info("Mostrando outline final...")
                st.markdown("### Outline recomendado")
                st.markdown(outline_md)

                # Sugerencias de video
                logger.info(f"Mostrando sugerencias de video: {len(videos)} videos")
                display_video_suggestions(videos)

                # Botones de descarga (con sugerencias de video incluidas)
                logger.info("Creando botones de descarga...")
                create_download_buttons(full_outline_md, df, kw)
                
                logger.info(f"=== PROCESAMIENTO COMPLETADO PARA: {kw} ===")

    logger.info("=== APLICACIÓN FINALIZADA ===")


if __name__ == "__main__":
    main()