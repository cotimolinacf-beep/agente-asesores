"""
Módulo de Análisis de Asesores
Evalúa la calidad de las respuestas de los asesores usando Gemini API
"""
import google.generativeai as genai
import json
import re
import time
import pandas as pd


ANALYSIS_PROMPT = """Eres un evaluador de calidad de atención en conversaciones de WhatsApp entre un asesor comercial y un cliente. El cliente ya pasó por un bot; ahora está hablando con el asesor (USER).

CONTEXTO OPCIONAL DEL BOT (si está disponible):
{historial_bot}

CONVERSACIÓN ASESOR–CLIENTE (obligatorio):
{historial_asesor}

METADATOS: Empresa: {company_name}. Grupo: {group_name}. Asesor: {user_name}.

INSTRUCCIONES:
1. Evalúa solo los mensajes del asesor (USER) en la conversación asesor–cliente.
2. Primera respuesta: ¿El asesor reconoce el tema o la intención que ya traía el cliente desde el bot? ¿Saluda y ofrece algo útil (información, siguiente paso) cuando el contexto lo permite, o solo hace una pregunta genérica?
3. Segunda respuesta y siguientes: ¿Responde a lo que el cliente acaba de decir? ¿Evita preguntas redundantes que el bot ya había resuelto? ¿Cada mensaje acerca a una solución (dato, cita, oferta)?
4. Eficiencia: ¿Podría haber resuelto la necesidad con menos mensajes? ¿Hay promesas sin cumplir en el mismo hilo (ej. "se lo comparto" sin enviar el dato)?
5. Claridad y tono: ¿Lenguaje claro y profesional? ¿Trato cordial y empático?

TAMBIÉN EXTRAE:
- La intención principal del cliente (qué busca/necesita)
- El caso de uso detectado (FINANCIAMIENTO, COTIZACION, PRUEBA_MANEJO, VENTA_VEHICULO, SERVICIO, OTRO)

FORMATO DE SALIDA (JSON):
{{
  "agent_score_numeric": <número del 1 al 5, donde 1 = muy deficiente, 5 = excelente>,
  "agent_score_text": "<resumen en 2-4 líneas: fortalezas y debilidades del asesor en esta conversación, con foco en primera respuesta, eficiencia y claridad>",
  "first_response_efficient": <true si la primera respuesta reconoce contexto o aporta valor; false si es genérica o redundante>,
  "efficiency_notes": "<en una línea: si pudo ser más eficiente, cómo>",
  "client_intention": "<intención principal del cliente>",
  "use_case": "<FINANCIAMIENTO | COTIZACION | PRUEBA_MANEJO | VENTA_VEHICULO | SERVICIO | OTRO>",
  "key_topics": "<temas clave mencionados, separados por coma>"
}}

Responde ÚNICAMENTE con el JSON, sin texto adicional.
"""


class AdvisorAnalyzer:
    """Analizador de calidad de respuestas de asesores."""

    def __init__(self, api_key: str, model: str = "gemini-2.0-flash"):
        """
        Inicializa el analizador.

        Args:
            api_key: API Key de Google Gemini
            model: Modelo a usar (default: gemini-2.0-flash para mejor velocidad)
        """
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)
        self.delay = 0.5  # Delay entre llamadas API

    def _safe_str(self, val, max_len: int = 3000) -> str:
        """Convierte valor a string de forma segura."""
        if pd.isna(val) or val is None:
            return ""
        s = str(val)
        return s[:max_len] if len(s) > max_len else s

    def _extract_json(self, text: str) -> dict:
        """Extrae JSON de la respuesta."""
        json_match = re.search(r'\{[\s\S]*\}', text)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass

        return {
            "agent_score_numeric": 0,
            "agent_score_text": "Error al parsear respuesta",
            "first_response_efficient": False,
            "efficiency_notes": "Error",
            "client_intention": "No determinado",
            "use_case": "OTRO",
            "key_topics": ""
        }

    def analyze_conversation(self, conversation_data: dict) -> dict:
        """
        Analiza una conversación y evalúa al asesor.

        Args:
            conversation_data: Diccionario con datos de la conversación

        Returns:
            Diccionario con el análisis
        """
        # Preparar prompt
        prompt = ANALYSIS_PROMPT.format(
            historial_bot=self._safe_str(
                conversation_data.get("historial_de_mensajes_en_bot", ""),
                2000
            ) or "No disponible",
            historial_asesor=self._safe_str(
                conversation_data.get("historial_de_mensajes_en_asesor", ""),
                3000
            ),
            company_name=self._safe_str(
                conversation_data.get("company_name", "N/A"),
                100
            ),
            group_name=self._safe_str(
                conversation_data.get("group_name", "N/A"),
                100
            ),
            user_name=self._safe_str(
                conversation_data.get("user_name", "N/A"),
                100
            )
        )

        try:
            response = self.model.generate_content(prompt)
            time.sleep(self.delay)  # Rate limiting

            result = self._extract_json(response.text)
            result["analysis_success"] = True
            result["error"] = None

            return result

        except Exception as e:
            return {
                "agent_score_numeric": 0,
                "agent_score_text": f"Error: {str(e)}",
                "first_response_efficient": False,
                "efficiency_notes": f"Error: {str(e)}",
                "client_intention": "Error",
                "use_case": "OTRO",
                "key_topics": "",
                "analysis_success": False,
                "error": str(e)
            }

    def analyze_batch(
        self,
        conversations: list,
        progress_callback=None
    ) -> list:
        """
        Analiza un lote de conversaciones.

        Args:
            conversations: Lista de diccionarios con datos
            progress_callback: Función para reportar progreso

        Returns:
            Lista de análisis
        """
        results = []

        for i, conv in enumerate(conversations):
            result = self.analyze_conversation(conv)
            result["conversation_id"] = conv.get("conversation_id", f"row_{i}")
            results.append(result)

            if progress_callback:
                progress_callback(i + 1, len(conversations))

        return results
