# # Opción para generar artículo completo
#                 st.markdown("---")
#                 st.subheader("🚀 Generar Artículo Completo")
#                 st.markdown("Puedes generar un artículo completo basado en el outline creado:")
                
#                 # Explicación de las opciones
#                 with st.expander("ℹ️ ¿Qué opción elegir?"):
#                     st.markdown("""
#                     **Artículo con IA (OpenAI):**
#                     - ✅ Alta calidad y coherencia
#                     - ✅ Uso de todo el contexto SERP (PAA, videos, top stories, etc.)
#                     - ✅ Contenido original y bien estructurado
#                     - ⚠️ Requiere configuración de OpenAI
#                     - ⏳ Toma varios minutos
                    
#                     **Artículo Básico (Heurístico):**
#                     - ✅ Rápido y gratuito
#                     - ✅ Estructura básica siguiendo el outline
#                     - ⚠️ Contenido más genérico
#                     - ⚠️ Requiere edición manual posterior
#                     """)
                
#                 # Selector de tipo de artículo (sin botones)
#                 article_option = st.radio(
#                     "Selecciona el tipo de artículo a generar:",
#                     ["No generar artículo", "✨ Artículo con IA (OpenAI)", "📝 Artículo Básico (Heurístico)"],
#                     index=0,
#                     help="El artículo se generará automáticamente al seleccionar una opción"
#                 )
                
#                 # Generar artículo según la selección (sin botones)
#                 if article_option == "✨ Artículo con IA (OpenAI)":
#                     if config["use_openai"] and config["openai_key"]:
#                         logger.info("Generando artículo completo con OpenAI...")
#                         with st.spinner("Generando artículo completo con IA... Esto puede tomar varios minutos ⏳"):
#                             try:
#                                 article_content = generate_article_with_openai(
#                                     kw,
#                                     outline=outline_md,
#                                     df=df,
#                                     paa=paa,
#                                     related=related or auto or [],
#                                     ai_overview=ai_overview,
#                                     videos=videos,
#                                     top_stories=top_stories,
#                                     related_searches=related_searches,
#                                     images=images,
#                                     twitter=twitter,
#                                     carousel=carousel,
#                                     knowledge_graph=knowledge_graph,
#                                     intent_label=intent_label,
#                                     intent_scores=intent_scores,
#                                     model=config["openai_model"],
#                                     api_key=config["openai_key"],
#                                     temperature=config["openai_temperature"],
#                                 )
                                
#                                 logger.info(f"Artículo generado con IA: {len(article_content)} caracteres")
                                
#                                 # Mostrar el artículo generado
#                                 st.success("✅ ¡Artículo generado exitosamente con IA!")
#                                 st.markdown("### 📄 Artículo Completo (Generado con IA)")
#                                 st.markdown(article_content)
                                
#                                 # Botón de descarga para el artículo
#                                 create_article_download_button(article_content, kw, "ia")
                                
#                             except Exception as e:
#                                 logger.error(f"Error generando artículo con IA: {str(e)}")
#                                 st.error(f"❌ Error generando artículo con IA: {str(e)}")
#                     else:
#                         st.warning("⚠️ Para generar artículos con IA necesitas configurar OpenAI en la barra lateral")
                
#                 elif article_option == "📝 Artículo Básico (Heurístico)":
#                     logger.info("Generando artículo básico con método heurístico...")
#                     with st.spinner("Generando artículo básico... ⏳"):
#                         try:
#                             article_content = generate_article_heuristic(
#                                 kw,
#                                 outline=outline_md,
#                                 df=df,
#                                 paa=paa,
#                                 related=related or auto or []
#                             )
                            
#                             logger.info(f"Artículo generado heurísticamente: {len(article_content)} caracteres")
                            
#                             # Mostrar el artículo generado
#                             st.success("✅ ¡Artículo básico generado exitosamente!")
#                             st.markdown("### 📄 Artículo Básico (Generado Heurísticamente)")
#                             st.markdown(article_content)
                            
#                             # Botón de descarga para el artículo
#                             create_article_download_button(article_content, kw, "basico")
                            
#                         except Exception as e:
#                             logger.error(f"Error generando artículo básico: {str(e)}")
#                             st.error(f"❌ Error generando artículo básico: {str(e)}")
                
#                 logger.info(f"=== PROCESAMIENTO COMPLETADO PARA: {kw} ===")