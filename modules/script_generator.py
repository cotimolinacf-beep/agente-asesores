"""
Módulo de Generación de Scripts de Venta
Genera scripts consolidados a partir de las conversaciones analizadas
"""
import google.generativeai as genai
import pandas as pd
import time


def generate_sales_script(df: pd.DataFrame, api_key: str) -> str:
    """
    Genera un script de ventas consolidado desde las conversaciones.

    Args:
        df: DataFrame con los análisis (debe tener agent_score_numeric)
        api_key: API Key de Gemini

    Returns:
        Script de ventas generado
    """
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')

    # Filtrar mejores conversaciones (score >= 4)
    if "agent_score_numeric" in df.columns:
        top_df = df[df["agent_score_numeric"] >= 4]
    else:
        top_df = df.head(20)

    # Recopilar patrones
    patterns = []

    # Si tenemos la columna de score text
    if "agent_score_text" in top_df.columns:
        for _, row in top_df.head(10).iterrows():
            if pd.notna(row.get("agent_score_text")):
                patterns.append(str(row["agent_score_text"]))

    # Si tenemos intenciones
    intentions = []
    if "client_intention" in df.columns:
        intentions = df["client_intention"].dropna().unique().tolist()

    # Si tenemos casos de uso
    use_cases = []
    if "use_case" in df.columns:
        use_cases = df["use_case"].dropna().unique().tolist()

    prompt = f"""Basándote en el análisis de conversaciones de servicio al cliente, genera un SCRIPT DE VENTAS profesional.

PATRONES EXITOSOS DETECTADOS:
{chr(10).join(patterns[:5]) if patterns else "No disponibles"}

INTENCIONES DE CLIENTES DETECTADAS:
{', '.join(intentions[:10]) if intentions else "No disponibles"}

CASOS DE USO IDENTIFICADOS:
{', '.join(use_cases) if use_cases else "No disponibles"}

GENERA UN SCRIPT DE VENTAS que incluya:

1. SALUDO INICIAL
   - Frase de bienvenida profesional
   - Presentación del asesor

2. IDENTIFICACIÓN DE NECESIDAD
   - Preguntas clave para identificar intención
   - Cómo reconocer contexto previo (del bot)

3. OFRECIMIENTO DE OPCIONES
   - Compra contado
   - Financiamiento
   - Prueba de manejo

4. SOLICITUD DE DATOS (por tipo de cliente)
   - Asalariado: datos requeridos
   - Independiente: datos requeridos

5. INFORMACIÓN DE PRODUCTO
   - Cómo presentar características
   - Cómo mencionar precios
   - Cómo hablar de promociones

6. MANEJO DE OBJECIONES
   - Respuestas a dudas comunes
   - Cómo superar objeciones

7. CIERRE
   - Confirmación de siguiente paso
   - Despedida profesional

Formato: texto estructurado con secciones claras, frases textuales entre comillas.
"""

    try:
        response = model.generate_content(prompt)
        time.sleep(1)
        return response.text.strip()
    except Exception as e:
        return f"Error generando script: {str(e)}"


def generate_script_by_use_case(df: pd.DataFrame, api_key: str, use_case: str) -> str:
    """
    Genera un script específico para un caso de uso.

    Args:
        df: DataFrame con los análisis
        api_key: API Key de Gemini
        use_case: Caso de uso específico

    Returns:
        Script específico
    """
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')

    # Filtrar por caso de uso
    if "use_case" in df.columns:
        filtered_df = df[df["use_case"] == use_case]
    else:
        filtered_df = df

    # Recopilar info
    info = []
    if "agent_score_text" in filtered_df.columns:
        for _, row in filtered_df.head(5).iterrows():
            if pd.notna(row.get("agent_score_text")):
                info.append(str(row["agent_score_text"]))

    prompt = f"""Genera un SCRIPT DE VENTAS específico para: {use_case}

INFORMACIÓN DE CONVERSACIONES EXITOSAS:
{chr(10).join(info) if info else "No disponible"}

El script debe incluir:
1. Saludo contextualizado al caso de uso
2. Preguntas específicas para este tipo de cliente
3. Información relevante a proporcionar
4. Datos a solicitar
5. Cierre apropiado

Formato: texto estructurado con frases textuales entre comillas.
"""

    try:
        response = model.generate_content(prompt)
        time.sleep(1)
        return response.text.strip()
    except Exception as e:
        return f"Error: {str(e)}"
