"""
Agente Asesores - Sistema de Análisis de Conversaciones
Frontend Streamlit
"""
import streamlit as st
import pandas as pd
from pathlib import Path

# Configuración de página
st.set_page_config(
    page_title="Agente Asesores",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E88E5;
        margin-bottom: 1rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #424242;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeeba;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar de navegación
st.sidebar.markdown("## 📊 Agente Asesores")
st.sidebar.markdown("---")

# Menú de navegación
menu_options = {
    "🏠 Inicio": "inicio",
    "📋 Análisis de Asesores": "analisis_asesores",
    "🎯 Análisis de Intenciones": "analisis_intenciones",
    "⚖️ Comparador de Respuestas": "comparador",
    "📈 Reportes": "reportes"
}

selected_page = st.sidebar.radio(
    "Navegación",
    list(menu_options.keys()),
    label_visibility="collapsed"
)

page = menu_options[selected_page]

# Configuración de API
st.sidebar.markdown("---")
st.sidebar.markdown("### ⚙️ Configuración")

api_key = st.sidebar.text_input(
    "API Key (Gemini)",
    type="password",
    value=st.session_state.get("api_key", ""),
    help="Ingresa tu API Key de Google Gemini"
)

if api_key:
    st.session_state["api_key"] = api_key
    st.sidebar.success("✓ API Key configurada")

# ============================================================
# PÁGINA: INICIO
# ============================================================
if page == "inicio":
    st.markdown('<p class="main-header">📊 Agente Asesores</p>', unsafe_allow_html=True)
    st.markdown("### Sistema de Análisis de Conversaciones de Servicio al Cliente")

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 📋 Análisis de Asesores")
        st.markdown("""
        - Evalúa la calidad de las respuestas de asesores
        - Scoring del 1 al 5 por conversación
        - Identifica fortalezas y debilidades
        - Extrae intenciones del cliente
        """)

        st.markdown("#### 🎯 Análisis de Intenciones")
        st.markdown("""
        - Analiza patrones de intención del cliente
        - Identifica mejores prácticas de asesores top
        - Genera scripts de venta por caso de uso
        - Construye base de conocimiento
        """)

    with col2:
        st.markdown("#### ⚖️ Comparador de Respuestas")
        st.markdown("""
        - Compara respuestas de asesores vs IA
        - Sample automático de 100 conversaciones
        - Usa scripts y KB personalizados
        - Métricas comparativas detalladas
        """)

        st.markdown("#### 📈 Reportes")
        st.markdown("""
        - Gráficos interactivos de métricas
        - Distribución de scores
        - Análisis por asesor y grupo
        - Exportación de resultados
        """)

    st.markdown("---")
    st.info("👈 Selecciona una sección en el menú lateral para comenzar")

# ============================================================
# PÁGINA: ANÁLISIS DE ASESORES
# ============================================================
elif page == "analisis_asesores":
    st.markdown('<p class="main-header">📋 Análisis de Asesores</p>', unsafe_allow_html=True)
    st.markdown("Evalúa la calidad de las respuestas de los asesores en las conversaciones.")

    st.markdown("---")

    # Upload de archivo
    uploaded_file = st.file_uploader(
        "📁 Cargar archivo CSV/Excel con conversaciones",
        type=["csv", "xlsx"],
        help="El archivo debe contener las columnas: conversation_id, historial_de_mensajes_en_bot, historial_de_mensajes_en_asesor"
    )

    if uploaded_file:
        # Leer archivo
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)

            st.success(f"✓ Archivo cargado: {len(df)} registros")

            # Mostrar preview
            with st.expander("👀 Vista previa de datos", expanded=False):
                st.dataframe(df.head(10), use_container_width=True)

            # Validar columnas requeridas
            required_cols = ["conversation_id", "historial_de_mensajes_en_asesor"]
            missing_cols = [col for col in required_cols if col not in df.columns]

            if missing_cols:
                st.error(f"❌ Faltan columnas requeridas: {', '.join(missing_cols)}")
            else:
                # Filtrar solo conversaciones con asesor
                df_with_advisor = df[df["historial_de_mensajes_en_asesor"].notna() &
                                     (df["historial_de_mensajes_en_asesor"] != "")]

                st.info(f"📊 {len(df_with_advisor)} conversaciones con historial de asesor")

                # Opciones de análisis
                col1, col2 = st.columns(2)

                with col1:
                    sample_size = st.number_input(
                        "Tamaño de muestra (0 = todas)",
                        min_value=0,
                        max_value=len(df_with_advisor),
                        value=min(100, len(df_with_advisor)),
                        step=10
                    )

                with col2:
                    start_from = st.number_input(
                        "Iniciar desde registro #",
                        min_value=0,
                        max_value=len(df_with_advisor)-1,
                        value=0
                    )

                # Columnas a preservar del archivo original
                st.markdown("#### Columnas a incluir del archivo original")

                # Columnas recomendadas para preservar
                recommended_cols = [
                    "conversation_id",
                    "historial_de_mensajes_en_bot",
                    "historial_de_mensajes_en_asesor",
                    "tipificacion",
                    "company_name",
                    "group_name",
                    "user_name",
                    "fecha_primer_mensaje",
                    "tipo_origen"
                ]

                # Filtrar solo las que existen en el archivo
                available_cols = [col for col in recommended_cols if col in df.columns]
                other_cols = [col for col in df.columns if col not in recommended_cols]

                # Selector de columnas
                selected_cols = st.multiselect(
                    "Selecciona columnas a conservar",
                    options=df.columns.tolist(),
                    default=available_cols,
                    help="Estas columnas se incluirán junto con el análisis"
                )

                # Botón de análisis
                if st.button("🚀 Iniciar Análisis", type="primary", use_container_width=True):
                    if not st.session_state.get("api_key"):
                        st.error("❌ Configura tu API Key en el panel lateral")
                    else:
                        # Importar módulo de análisis
                        from modules.advisor_analyzer import AdvisorAnalyzer

                        analyzer = AdvisorAnalyzer(st.session_state["api_key"])

                        # Preparar datos
                        sample_df = df_with_advisor.iloc[start_from:].copy()
                        if sample_size > 0:
                            sample_df = sample_df.head(sample_size)

                        # Progress bar
                        progress_bar = st.progress(0)
                        status_text = st.empty()

                        results = []
                        total = len(sample_df)

                        for idx, (row_idx, row) in enumerate(sample_df.iterrows()):
                            status_text.text(f"Procesando {idx+1}/{total}...")
                            progress_bar.progress((idx + 1) / total)

                            # Analizar conversación
                            analysis = analyzer.analyze_conversation(row.to_dict())

                            # Combinar columnas originales con análisis
                            result = {}

                            # Primero las columnas seleccionadas del original
                            for col in selected_cols:
                                result[col] = row.get(col, "")

                            # Luego las columnas del análisis
                            for key, value in analysis.items():
                                result[key] = value

                            results.append(result)

                        # Crear DataFrame combinado
                        results_df = pd.DataFrame(results)

                        # Guardar resultados en session state
                        st.session_state["analysis_results"] = results
                        st.session_state["analysis_df"] = results_df
                        st.session_state["original_df"] = sample_df

                        status_text.text("✅ Análisis completado!")

                        # Mostrar resumen
                        results_df = pd.DataFrame(results)

                        st.markdown("### 📊 Resumen de Resultados")

                        col1, col2, col3, col4 = st.columns(4)

                        with col1:
                            avg_score = results_df["agent_score_numeric"].mean()
                            st.metric("Promedio Score", f"{avg_score:.2f}/5")

                        with col2:
                            top_advisors = len(results_df[results_df["agent_score_numeric"] >= 4])
                            st.metric("Score ≥ 4", f"{top_advisors} ({top_advisors/len(results_df)*100:.1f}%)")

                        with col3:
                            efficient = results_df["first_response_efficient"].sum()
                            st.metric("Primera Resp. Eficiente", f"{efficient} ({efficient/len(results_df)*100:.1f}%)")

                        with col4:
                            st.metric("Total Analizados", len(results_df))

                        # Mostrar resultados
                        st.markdown("### 📋 Resultados Detallados")
                        st.dataframe(results_df, use_container_width=True)

                        # Botón de descarga
                        csv = results_df.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            "📥 Descargar Resultados (CSV)",
                            csv,
                            "analisis_asesores.csv",
                            "text/csv",
                            use_container_width=True
                        )

        except Exception as e:
            st.error(f"❌ Error al procesar archivo: {str(e)}")

# ============================================================
# PÁGINA: ANÁLISIS DE INTENCIONES
# ============================================================
elif page == "analisis_intenciones":
    st.markdown('<p class="main-header">🎯 Análisis de Intenciones</p>', unsafe_allow_html=True)
    st.markdown("Analiza intenciones, genera scripts de venta y base de conocimiento.")

    st.markdown("---")

    # Tabs para diferentes funcionalidades
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Análisis de Intenciones",
        "⭐ Top Asesores",
        "📝 Scripts de Venta",
        "📚 Base de Conocimiento"
    ])

    # TAB 1: Análisis de Intenciones
    with tab1:
        st.markdown("### Distribución de Intenciones")

        uploaded_results = st.file_uploader(
            "📁 Cargar resultados del análisis (CSV)",
            type=["csv"],
            key="intentions_upload"
        )

        if uploaded_results:
            results_df = pd.read_csv(uploaded_results)
            st.session_state["intentions_df"] = results_df

            if "client_intention" in results_df.columns:
                intention_counts = results_df["client_intention"].value_counts()

                col1, col2 = st.columns([2, 1])

                with col1:
                    import plotly.express as px
                    fig = px.pie(
                        values=intention_counts.values,
                        names=intention_counts.index,
                        title="Distribución de Intenciones"
                    )
                    st.plotly_chart(fig, use_container_width=True)

                with col2:
                    st.dataframe(
                        intention_counts.reset_index().rename(
                            columns={"index": "Intención", "client_intention": "Cantidad"}
                        ),
                        use_container_width=True
                    )
            else:
                st.warning("El archivo no contiene la columna 'client_intention'")

    # TAB 2: Top Asesores
    with tab2:
        st.markdown("### Respuestas de Asesores con Score 5")

        if "intentions_df" in st.session_state:
            df = st.session_state["intentions_df"]

            if "agent_score_numeric" in df.columns:
                top_df = df[df["agent_score_numeric"] == 5]
                st.info(f"📊 {len(top_df)} conversaciones con score perfecto (5/5)")

                if len(top_df) > 0:
                    st.dataframe(top_df[["conversation_id", "agent_score_text", "client_intention"]],
                                use_container_width=True)
                else:
                    st.warning("No hay conversaciones con score 5")
            else:
                st.warning("Primero carga los resultados del análisis")
        else:
            st.info("👆 Carga los resultados del análisis en la pestaña anterior")

    # TAB 3: Scripts de Venta
    with tab3:
        st.markdown("### Generación de Scripts de Venta")

        # Cargar script base o personalizado
        script_option = st.radio(
            "Fuente del Script",
            ["Generar desde conversaciones", "Cargar script personalizado"]
        )

        if script_option == "Cargar script personalizado":
            script_text = st.text_area(
                "Script de Ventas",
                height=300,
                placeholder="Pega aquí tu script de ventas..."
            )
            if script_text:
                st.session_state["sales_script"] = script_text
                st.success("✓ Script guardado")
        else:
            if st.button("🔄 Generar Script desde Datos"):
                if "intentions_df" in st.session_state and st.session_state.get("api_key"):
                    from modules.script_generator import generate_sales_script

                    with st.spinner("Generando script..."):
                        script = generate_sales_script(
                            st.session_state["intentions_df"],
                            st.session_state["api_key"]
                        )
                        st.session_state["sales_script"] = script
                        st.text_area("Script Generado", script, height=400)
                else:
                    st.error("Carga los datos y configura la API Key")

    # TAB 4: Base de Conocimiento
    with tab4:
        st.markdown("### Base de Conocimiento")

        kb_option = st.radio(
            "Fuente del KB",
            ["Generar desde conversaciones", "Cargar KB personalizado"]
        )

        if kb_option == "Cargar KB personalizado":
            kb_text = st.text_area(
                "Base de Conocimiento",
                height=300,
                placeholder="Pega aquí tu base de conocimiento..."
            )
            if kb_text:
                st.session_state["knowledge_base"] = kb_text
                st.success("✓ KB guardado")
        else:
            if st.button("🔄 Generar KB desde Datos"):
                if "intentions_df" in st.session_state and st.session_state.get("api_key"):
                    from modules.kb_generator import generate_knowledge_base

                    with st.spinner("Generando KB..."):
                        kb = generate_knowledge_base(
                            st.session_state["intentions_df"],
                            st.session_state["api_key"]
                        )
                        st.session_state["knowledge_base"] = kb
                        st.text_area("KB Generado", kb, height=400)
                else:
                    st.error("Carga los datos y configura la API Key")

# ============================================================
# PÁGINA: COMPARADOR DE RESPUESTAS
# ============================================================
elif page == "comparador":
    st.markdown('<p class="main-header">⚖️ Comparador de Respuestas</p>', unsafe_allow_html=True)
    st.markdown("Compara respuestas de asesores vs respuestas generadas por IA.")

    st.markdown("---")

    # Verificar prerrequisitos
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 📝 Script de Ventas")
        if st.session_state.get("sales_script"):
            st.success("✓ Script cargado")
            with st.expander("Ver Script"):
                st.text(st.session_state["sales_script"][:500] + "...")
        else:
            st.warning("⚠️ Carga un script en 'Análisis de Intenciones'")

    with col2:
        st.markdown("#### 📚 Base de Conocimiento")
        if st.session_state.get("knowledge_base"):
            st.success("✓ KB cargado")
            with st.expander("Ver KB"):
                st.text(st.session_state["knowledge_base"][:500] + "...")
        else:
            st.warning("⚠️ Carga un KB en 'Análisis de Intenciones'")

    st.markdown("---")

    # Upload de archivo para comparación
    uploaded_compare = st.file_uploader(
        "📁 Cargar archivo para comparación (CSV/Excel)",
        type=["csv", "xlsx"],
        key="compare_upload"
    )

    if uploaded_compare:
        try:
            if uploaded_compare.name.endswith('.csv'):
                compare_df = pd.read_csv(uploaded_compare)
            else:
                compare_df = pd.read_excel(uploaded_compare)

            # Filtrar conversaciones con asesor
            compare_df = compare_df[
                compare_df["historial_de_mensajes_en_asesor"].notna() &
                (compare_df["historial_de_mensajes_en_asesor"] != "")
            ]

            st.success(f"✓ {len(compare_df)} conversaciones disponibles para comparar")

            sample_size = st.slider(
                "Tamaño de muestra",
                min_value=10,
                max_value=min(100, len(compare_df)),
                value=min(50, len(compare_df))
            )

            if st.button("🚀 Iniciar Comparación", type="primary", use_container_width=True):
                if not st.session_state.get("api_key"):
                    st.error("❌ Configura tu API Key")
                elif not st.session_state.get("sales_script"):
                    st.error("❌ Carga un Script de Ventas primero")
                else:
                    from modules.response_comparator import ResponseComparator

                    comparator = ResponseComparator(
                        api_key=st.session_state["api_key"],
                        sales_script=st.session_state.get("sales_script", ""),
                        knowledge_base=st.session_state.get("knowledge_base", "")
                    )

                    sample_df = compare_df.sample(n=sample_size)

                    progress_bar = st.progress(0)
                    status_text = st.empty()

                    results = []
                    total = len(sample_df)

                    for idx, (_, row) in enumerate(sample_df.iterrows()):
                        status_text.text(f"Comparando {idx+1}/{total}...")
                        progress_bar.progress((idx + 1) / total)

                        result = comparator.compare(row.to_dict())
                        results.append(result)

                    status_text.text("✅ Comparación completada!")

                    results_df = pd.DataFrame(results)
                    st.session_state["comparison_results"] = results_df

                    # Mostrar resumen
                    st.markdown("### 📊 Resumen de Comparación")

                    col1, col2, col3, col4 = st.columns(4)

                    with col1:
                        avg_advisor = results_df["advisor_score"].mean()
                        st.metric("Promedio Asesor", f"{avg_advisor:.2f}/5")

                    with col2:
                        avg_ai = results_df["ai_score"].mean()
                        st.metric("Promedio IA", f"{avg_ai:.2f}/5")

                    with col3:
                        ai_wins = (results_df["winner"] == "ia").sum()
                        st.metric("Victorias IA", f"{ai_wins} ({ai_wins/len(results_df)*100:.1f}%)")

                    with col4:
                        advisor_wins = (results_df["winner"] == "asesor").sum()
                        st.metric("Victorias Asesor", f"{advisor_wins} ({advisor_wins/len(results_df)*100:.1f}%)")

                    st.dataframe(results_df, use_container_width=True)

                    # Descargar
                    csv = results_df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        "📥 Descargar Comparación (CSV)",
                        csv,
                        "comparacion_respuestas.csv",
                        "text/csv",
                        use_container_width=True
                    )

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

# ============================================================
# PÁGINA: REPORTES
# ============================================================
elif page == "reportes":
    st.markdown('<p class="main-header">📈 Reportes</p>', unsafe_allow_html=True)
    st.markdown("Visualiza métricas y genera reportes de los análisis.")

    st.markdown("---")

    # Tabs de reportes
    tab1, tab2, tab3 = st.tabs([
        "📊 Análisis de Asesores",
        "⚖️ Comparación",
        "📥 Exportar"
    ])

    with tab1:
        st.markdown("### Métricas de Análisis de Asesores")

        if "analysis_df" in st.session_state:
            df = st.session_state["analysis_df"]

            import plotly.express as px
            import plotly.graph_objects as go

            col1, col2 = st.columns(2)

            with col1:
                # Distribución de scores
                fig = px.histogram(
                    df, x="agent_score_numeric",
                    title="Distribución de Scores",
                    labels={"agent_score_numeric": "Score"},
                    nbins=5
                )
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                # Primera respuesta eficiente
                efficient_counts = df["first_response_efficient"].value_counts()
                fig = px.pie(
                    values=efficient_counts.values,
                    names=["Eficiente" if x else "No Eficiente" for x in efficient_counts.index],
                    title="Primera Respuesta Eficiente"
                )
                st.plotly_chart(fig, use_container_width=True)

            # Intenciones si existen
            if "client_intention" in df.columns:
                fig = px.bar(
                    df["client_intention"].value_counts().reset_index(),
                    x="index", y="client_intention",
                    title="Intenciones del Cliente",
                    labels={"index": "Intención", "client_intention": "Cantidad"}
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("👆 Primero realiza un análisis de asesores")

    with tab2:
        st.markdown("### Métricas de Comparación")

        if "comparison_results" in st.session_state:
            df = st.session_state["comparison_results"]

            import plotly.express as px

            col1, col2 = st.columns(2)

            with col1:
                # Comparación de promedios
                fig = px.bar(
                    x=["Asesor", "IA"],
                    y=[df["advisor_score"].mean(), df["ai_score"].mean()],
                    title="Promedio de Scores",
                    labels={"x": "Tipo", "y": "Score Promedio"}
                )
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                # Distribución de ganadores
                winner_counts = df["winner"].value_counts()
                fig = px.pie(
                    values=winner_counts.values,
                    names=winner_counts.index,
                    title="Distribución de Ganadores"
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("👆 Primero realiza una comparación")

    with tab3:
        st.markdown("### Exportar Reportes")

        export_options = st.multiselect(
            "Selecciona qué exportar",
            ["Análisis de Asesores", "Comparación de Respuestas", "Reporte Completo"]
        )

        if st.button("📥 Generar Exportación", type="primary"):
            if "Análisis de Asesores" in export_options and "analysis_df" in st.session_state:
                csv = st.session_state["analysis_df"].to_csv(index=False).encode('utf-8')
                st.download_button(
                    "Descargar Análisis de Asesores",
                    csv,
                    "analisis_asesores_export.csv",
                    "text/csv"
                )

            if "Comparación de Respuestas" in export_options and "comparison_results" in st.session_state:
                csv = st.session_state["comparison_results"].to_csv(index=False).encode('utf-8')
                st.download_button(
                    "Descargar Comparación",
                    csv,
                    "comparacion_export.csv",
                    "text/csv"
                )

            if not export_options:
                st.warning("Selecciona al menos una opción")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("### 💡 Ayuda")
st.sidebar.markdown("""
1. Configura tu API Key
2. Carga tu archivo CSV/Excel
3. Ejecuta el análisis
4. Visualiza reportes
""")
st.sidebar.markdown("---")
st.sidebar.caption("Agente Asesores v1.0")
