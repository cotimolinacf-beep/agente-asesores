"""
Módulo de Generación de Base de Conocimiento
Extrae y consolida información de las conversaciones
"""
import google.generativeai as genai
import pandas as pd
import time


def generate_knowledge_base(df: pd.DataFrame, api_key: str) -> str:
    """
    Genera una base de conocimiento desde las conversaciones.

    Args:
        df: DataFrame con los análisis
        api_key: API Key de Gemini

    Returns:
        Base de conocimiento generada
    """
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash')

    # Recopilar información de diferentes columnas
    key_topics = []
    if "key_topics" in df.columns:
        for topics in df["key_topics"].dropna():
            if topics and str(topics).strip():
                key_topics.extend([t.strip() for t in str(topics).split(",")])

    intentions = []
    if "client_intention" in df.columns:
        intentions = df["client_intention"].dropna().unique().tolist()

    use_cases = []
    if "use_case" in df.columns:
        use_cases = df["use_case"].dropna().unique().tolist()

    # Contar frecuencias de topics
    topic_freq = {}
    for topic in key_topics:
        if topic:
            topic_freq[topic] = topic_freq.get(topic, 0) + 1

    top_topics = sorted(topic_freq.items(), key=lambda x: -x[1])[:20]

    prompt = f"""Basándote en el análisis de conversaciones de servicio al cliente, genera una BASE DE CONOCIMIENTO estructurada.

TEMAS MÁS FRECUENTES EN LAS CONVERSACIONES:
{chr(10).join([f"- {t[0]} ({t[1]} menciones)" for t in top_topics]) if top_topics else "No disponibles"}

INTENCIONES DE CLIENTES DETECTADAS:
{chr(10).join([f"- {i}" for i in intentions[:15]]) if intentions else "No disponibles"}

CASOS DE USO IDENTIFICADOS:
{chr(10).join([f"- {u}" for u in use_cases]) if use_cases else "No disponibles"}

GENERA UNA BASE DE CONOCIMIENTO que incluya:

1. INFORMACIÓN DE PRODUCTOS
   - Modelos disponibles
   - Rangos de precio
   - Características principales

2. PROCESOS DE FINANCIAMIENTO
   - Requisitos para asalariados
   - Requisitos para independientes
   - Porcentajes de abono inicial
   - Documentos necesarios

3. PROMOCIONES Y BENEFICIOS
   - Promociones activas
   - Beneficios incluidos

4. INFORMACIÓN DE SERVICIO
   - Sucursales disponibles
   - Horarios de atención
   - Servicios adicionales

5. PREGUNTAS FRECUENTES (FAQ)
   - Preguntas comunes de clientes
   - Respuestas estándar

6. OBJECIONES COMUNES
   - Objeciones típicas
   - Respuestas recomendadas

Formato: texto estructurado con secciones claras, información concreta y verificable.
"""

    try:
        response = model.generate_content(prompt)
        time.sleep(1)
        return response.text.strip()
    except Exception as e:
        return f"Error generando KB: {str(e)}"


def extract_product_info(df: pd.DataFrame, api_key: str) -> dict:
    """
    Extrae información específica de productos.

    Args:
        df: DataFrame con los análisis
        api_key: API Key de Gemini

    Returns:
        Diccionario con información de productos
    """
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash')

    # Recopilar topics relacionados con productos
    product_keywords = ['precio', 'modelo', 'característica', 'motor', 'color', 'versión']

    key_topics = []
    if "key_topics" in df.columns:
        for topics in df["key_topics"].dropna():
            if topics:
                for topic in str(topics).split(","):
                    topic = topic.strip().lower()
                    if any(kw in topic for kw in product_keywords):
                        key_topics.append(topic)

    prompt = f"""Extrae información de productos mencionados en estas conversaciones:

TEMAS DETECTADOS:
{chr(10).join(set(key_topics[:30])) if key_topics else "No disponibles"}

Devuelve un resumen estructurado de:
1. Modelos mencionados
2. Rangos de precio detectados
3. Características mencionadas
4. Promociones detectadas

Formato: texto organizado por categorías.
"""

    try:
        response = model.generate_content(prompt)
        time.sleep(1)
        return {
            "raw_info": response.text.strip(),
            "topics_found": len(set(key_topics))
        }
    except Exception as e:
        return {
            "raw_info": f"Error: {str(e)}",
            "topics_found": 0
        }
