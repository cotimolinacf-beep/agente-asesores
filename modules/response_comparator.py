"""
Módulo Comparador de Respuestas
Compara respuestas de asesores vs respuestas generadas por IA
"""
import google.generativeai as genai
import json
import re
import time
import pandas as pd


class ResponseComparator:
    """Comparador de respuestas Asesor vs IA."""

    def __init__(
        self,
        api_key: str,
        sales_script: str = "",
        knowledge_base: str = "",
        model: str = "gemini-2.0-flash"
    ):
        """
        Inicializa el comparador.

        Args:
            api_key: API Key de Gemini
            sales_script: Script de ventas a usar
            knowledge_base: Base de conocimiento
            model: Modelo a usar
        """
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)
        self.sales_script = sales_script
        self.knowledge_base = knowledge_base

    def _safe_str(self, val, max_len: int = 2000) -> str:
        """Convierte valor a string de forma segura."""
        if pd.isna(val) or val is None:
            return ""
        s = str(val)
        return s[:max_len] if len(s) > max_len else s

    def _extract_first_advisor_response(self, historial_asesor: str) -> str:
        """Extrae la primera respuesta del asesor."""
        if not historial_asesor or pd.isna(historial_asesor):
            return ""

        historial = str(historial_asesor)
        lines = historial.split('\n')

        first_response_parts = []
        found_user_message = False

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Detectar mensajes del asesor (USER)
            if 'USER:' in line or line.startswith('[USER]'):
                found_user_message = True
                if 'USER:' in line:
                    content = line.split('USER:', 1)[1].strip()
                else:
                    content = line.split('[USER]', 1)[1].strip()

                if content:
                    first_response_parts.append(content)

            # Si encontramos mensaje del cliente después del asesor, paramos
            elif found_user_message and ('CLIENT:' in line or '[CLIENT]' in line):
                break

        result = '\n'.join(first_response_parts)
        return result[:1500] if result else historial[:500]

    def _detect_client_interest(self, historial_bot: str) -> dict:
        """Detecta el interés del cliente desde el bot."""
        if not historial_bot or pd.isna(historial_bot):
            return {'financiamiento': False, 'test_drive': False, 'resumen': 'Sin info'}

        texto = str(historial_bot).lower()

        result = {
            'financiamiento': any(kw in texto for kw in ['financiamiento', 'financiar', 'crédito', 'cuotas']),
            'test_drive': any(kw in texto for kw in ['prueba de manejo', 'test drive', 'cita', 'visitar']),
            'contado': any(kw in texto for kw in ['contado', 'efectivo']),
            'modelo': None
        }

        # Detectar modelo
        modelos = ['x50', 'dashing', 't1', 't2', 's06']
        for modelo in modelos:
            if modelo in texto:
                result['modelo'] = modelo.upper()
                break

        intereses = []
        if result['financiamiento']:
            intereses.append('FINANCIAMIENTO')
        if result['test_drive']:
            intereses.append('TEST DRIVE')
        if result['contado']:
            intereses.append('CONTADO')
        if result['modelo']:
            intereses.append(f"Modelo: {result['modelo']}")

        result['resumen'] = ', '.join(intereses) if intereses else 'Sin interés específico'

        return result

    def _generate_ai_response(self, historial_bot: str, intereses: dict) -> str:
        """Genera una respuesta de IA basada en el contexto."""
        prompt = f"""Eres un asesor de ventas experto de un concesionario automotriz.

CONTEXTO DE LA CONVERSACIÓN CON EL BOT:
{self._safe_str(historial_bot, 2000) or "Sin historial previo"}

INTERESES DETECTADOS DEL CLIENTE:
{intereses['resumen']}

SCRIPT DE VENTAS:
{self.sales_script[:2000] if self.sales_script else "No disponible"}

BASE DE CONOCIMIENTO:
{self.knowledge_base[:2000] if self.knowledge_base else "No disponible"}

INSTRUCCIONES:
1. Genera la PRIMERA RESPUESTA que el asesor debería dar al cliente
2. NO repitas opciones si el cliente ya eligió una (financiamiento, test drive, etc.)
3. La respuesta debe:
   - Reconocer el contexto que el cliente trajo desde el bot
   - Saludar brevemente y ofrecer algo útil
   - Avanzar hacia el siguiente paso lógico
   - Ser concisa (2-4 oraciones)

Responde SOLO con el texto de la respuesta.
"""

        try:
            response = self.model.generate_content(prompt)
            time.sleep(0.5)
            return response.text.strip()
        except Exception as e:
            return f"Error: {str(e)}"

    def _evaluate_responses(
        self,
        advisor_response: str,
        ai_response: str,
        historial_bot: str,
        intereses: dict
    ) -> dict:
        """Evalúa ambas respuestas."""
        prompt = f"""Eres un evaluador de calidad de servicio al cliente.

CONTEXTO (conversación con bot):
{self._safe_str(historial_bot, 1000)}

INTERESES DEL CLIENTE:
{intereses['resumen']}

RESPUESTA #1 (ASESOR):
{advisor_response}

RESPUESTA #2 (IA):
{ai_response}

CRITERIOS:
1. RECONOCIMIENTO DEL CONTEXTO (25%): ¿Reconoce lo que el cliente ya expresó?
2. VALOR AGREGADO (25%): ¿Ofrece información útil o solo pregunta?
3. AVANCE (25%): ¿Acerca a una solución?
4. CLARIDAD Y TONO (25%): ¿Profesional y empático?

ESCALA: 1 = muy deficiente, 5 = excelente

Responde SOLO con JSON:
{{
    "advisor_score": <1-5>,
    "ai_score": <1-5>,
    "advisor_justification": "<breve justificación>",
    "ai_justification": "<breve justificación>",
    "winner": "asesor" o "ia" o "empate",
    "decisive_criterion": "<criterio que decidió>"
}}
"""

        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            time.sleep(0.5)

            json_match = re.search(r'\{[\s\S]*\}', text)
            if json_match:
                return json.loads(json_match.group())
            else:
                return {
                    "advisor_score": 3,
                    "ai_score": 3,
                    "advisor_justification": "No evaluado",
                    "ai_justification": "No evaluado",
                    "winner": "empate",
                    "decisive_criterion": "N/A"
                }
        except Exception as e:
            return {
                "advisor_score": 0,
                "ai_score": 0,
                "advisor_justification": f"Error: {str(e)}",
                "ai_justification": f"Error: {str(e)}",
                "winner": "error",
                "decisive_criterion": "Error"
            }

    def compare(self, conversation_data: dict) -> dict:
        """
        Compara la respuesta del asesor con una generada por IA.

        Args:
            conversation_data: Datos de la conversación

        Returns:
            Diccionario con la comparación
        """
        historial_bot = self._safe_str(
            conversation_data.get("historial_de_mensajes_en_bot", "")
        )
        historial_asesor = self._safe_str(
            conversation_data.get("historial_de_mensajes_en_asesor", "")
        )

        # Extraer primera respuesta del asesor
        advisor_response = self._extract_first_advisor_response(historial_asesor)

        # Detectar intereses
        intereses = self._detect_client_interest(historial_bot)

        # Generar respuesta de IA
        ai_response = self._generate_ai_response(historial_bot, intereses)

        # Evaluar ambas
        evaluation = self._evaluate_responses(
            advisor_response,
            ai_response,
            historial_bot,
            intereses
        )

        return {
            "conversation_id": conversation_data.get("conversation_id", ""),
            "client_interests": intereses['resumen'],
            "advisor_response": advisor_response[:500],
            "ai_response": ai_response[:500],
            "advisor_score": evaluation.get("advisor_score", 0),
            "ai_score": evaluation.get("ai_score", 0),
            "advisor_justification": evaluation.get("advisor_justification", ""),
            "ai_justification": evaluation.get("ai_justification", ""),
            "winner": evaluation.get("winner", ""),
            "decisive_criterion": evaluation.get("decisive_criterion", "")
        }
