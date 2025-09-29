# create_article.py
from typing import Callable, Optional, Dict, Any
import streamlit as st
from ui_components import create_article_download_button  # asegúrate de tener este helper

# ──────────────────────────────────────────────────────────────────────────────
# Estado base (se llama una vez al iniciar la app, desde app.py)

def bootstrap_state():
    ss = st.session_state
    ss.setdefault("results", {})   # {kw: {"df":..., "outline_md":..., "features": {...}, "config": {...}, "related_or_auto": [...]}}
    ss.setdefault("articles", {})  # {kw: {"type": "ia"|"basico", "content": "..."}}
    ss.setdefault("ui", {})        # estados de radios/botones por kw


# ──────────────────────────────────────────────────────────────────────────────
# Guardado del análisis (se llama después de generar outline, una por KW)

def save_analysis_result(
    kw: str,
    *,
    df,
    outline_md: str,
    features: Dict[str, Any],
    config: Dict[str, Any],
    related_or_auto: Optional[list] = None,
):
    st.session_state["results"][kw] = {
        "df": df,
        "outline_md": outline_md,
        "features": features,
        "config": config,
        "related_or_auto": (related_or_auto or []),
    }


# ──────────────────────────────────────────────────────────────────────────────
# UI de Generación (lee lo guardado, genera bajo demanda y persiste el artículo)

def render_article_section(
    kw: str,
    *,
    generate_article_with_openai: Optional[Callable[..., str]] = None,
    generate_article_heuristic: Optional[Callable[..., str]] = None,
):
    # Guardas defensivas livianas (por si alguien reusa el módulo sin bootstrap)
    st.session_state.setdefault("results", {})
    st.session_state.setdefault("articles", {})
    st.session_state.setdefault("ui", {})

    st.markdown("---")
    st.subheader("🚀 Generar Artículo Completo")
    st.markdown("Puedes generar un artículo completo basado en el outline creado:")

    with st.expander("ℹ️ ¿Qué opción elegir?"):
        st.markdown(
            """
**Artículo con IA (OpenAI)**
- ✅ Alta calidad y coherencia
- ✅ Usa todo el contexto SERP (PAA, videos, Top Stories, etc.)
- ✅ Contenido original y bien estructurado
- ⚠️ Requiere OPENAI_API_KEY
- ⏳ Puede demorar

**Artículo Básico (Heurístico)**
- ✅ Rápido y sin costo
- ✅ Sigue la estructura del outline
- ⚠️ Más genérico; requiere edición
"""
        )

    # Radio con key única por keyword
    radio_key = f"article_option_{kw}"
    st.session_state["ui"].setdefault(radio_key, "No generar artículo")
    options = ["No generar artículo", "✨ Artículo con IA (OpenAI)", "📝 Artículo Básico (Heurístico)"]

    article_option = st.radio(
        "Selecciona el tipo de artículo a generar:",
        options,
        index=options.index(st.session_state["ui"][radio_key]),
        key=radio_key,
        help="El artículo se guardará y quedará visible aunque la app haga rerun.",
    )

    # Botón explícito para disparar generación
    generar = st.button("Generar ahora", key=f"btn_generar_{kw}")

    # Render del artículo previamente guardado (si existe), SIEMPRE
    _render_persisted_article(kw)

    if not generar:
        return

    # Recuperar paquete de análisis
    pack = st.session_state["results"].get(kw)
    if not pack:
        st.error("No hay resultados previos para esta keyword. Ejecuta el análisis primero.")
        return

    df_saved = pack["df"]
    outline_saved = pack["outline_md"]
    feats = pack["features"] or {}
    cfg = pack["config"] or {}
    related_or_auto = pack.get("related_or_auto", [])

    if article_option == "✨ Artículo con IA (OpenAI)":
        if not generate_article_with_openai:
            st.error("No se proveyó la función generate_article_with_openai.")
            return
        if not cfg.get("use_openai") or not cfg.get("openai_key"):
            st.warning("⚠️ Configura OpenAI en la barra lateral para usar esta opción.")
            return

        with st.spinner("Generando artículo con IA... ⏳"):
            try:
                article_content = generate_article_with_openai(
                    kw,
                    outline=outline_saved,
                    df=df_saved,
                    paa=feats.get("paa"),
                    related=related_or_auto,
                    ai_overview=feats.get("ai_overview"),
                    videos=feats.get("videos"),
                    top_stories=feats.get("top_stories"),
                    related_searches=feats.get("related_searches"),
                    images=feats.get("images"),
                    twitter=feats.get("twitter"),
                    carousel=feats.get("carousel"),
                    knowledge_graph=feats.get("knowledge_graph"),
                    intent_label=feats.get("intent_label"),
                    intent_scores=feats.get("intent_scores"),
                    model=cfg.get("openai_model"),
                    api_key=cfg.get("openai_key"),
                    temperature=cfg.get("openai_temperature"),
                )
                st.session_state["articles"][kw] = {"type": "ia", "content": article_content}
                st.success("✅ ¡Artículo generado exitosamente con IA!")
            except Exception as e:
                st.error(f"❌ Error generando artículo con IA: {e}")
                return

    elif article_option == "📝 Artículo Básico (Heurístico)":
        if not generate_article_heuristic:
            st.error("No se proveyó la función generate_article_heuristic.")
            return
        with st.spinner("Generando artículo básico... ⏳"):
            try:
                article_content = generate_article_heuristic(
                    kw,
                    outline=outline_saved,
                    df=df_saved,
                    paa=feats.get("paa"),
                    related=related_or_auto,
                )
                st.session_state["articles"][kw] = {"type": "basico", "content": article_content}
                st.success("✅ ¡Artículo básico generado exitosamente!")
            except Exception as e:
                st.error(f"❌ Error generando artículo básico: {e}")
                return

    # Render actualizado
    _render_persisted_article(kw)


def _render_persisted_article(kw: str):
    art_store = st.session_state["articles"].get(kw)
    if not art_store or not art_store.get("content"):
        return
    tipo = "IA" if art_store["type"] == "ia" else "Heurístico"
    st.markdown(f"### 📄 Artículo Completo (Generado: {tipo})")
    st.markdown(art_store["content"])
    tipo_id = "ia" if art_store["type"] == "ia" else "basico"
    create_article_download_button(art_store["content"], kw, tipo_id)
