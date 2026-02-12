# Agente Asesores

Sistema de análisis de conversaciones de servicio al cliente con interfaz Streamlit.

## Características

### 1. Análisis de Asesores
- Evalúa la calidad de las respuestas de asesores (scoring 1-5)
- Identifica fortalezas y debilidades
- Extrae intención del cliente
- Detecta casos de uso

### 2. Análisis de Intenciones
- Visualiza distribución de intenciones
- Identifica mejores prácticas de asesores top (score 5)
- Genera scripts de venta por caso de uso
- Construye base de conocimiento

### 3. Comparador de Respuestas
- Compara respuestas de asesores vs IA
- Sample automático de conversaciones
- Usa scripts y KB personalizados
- Métricas comparativas detalladas

### 4. Reportes
- Gráficos interactivos
- Distribución de scores
- Análisis por asesor y grupo
- Exportación de resultados

## Instalación

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

## Uso

```bash
# Ejecutar la aplicación
streamlit run app.py
```

## Configuración

1. Obtén una API Key de Google Gemini
2. Ingresa la API Key en el panel lateral de la aplicación

## Estructura del Proyecto

```
agente_asesores/
├── app.py                 # Aplicación principal Streamlit
├── requirements.txt       # Dependencias
├── .env.example          # Ejemplo de variables de entorno
├── README.md             # Este archivo
└── modules/
    ├── __init__.py
    ├── advisor_analyzer.py    # Análisis de asesores
    ├── response_comparator.py # Comparador de respuestas
    ├── script_generator.py    # Generador de scripts
    └── kb_generator.py        # Generador de KB
```

## Formato de Archivo de Entrada

El archivo CSV/Excel debe contener las siguientes columnas:
- `conversation_id`: Identificador único
- `historial_de_mensajes_en_bot`: Conversación con el bot (opcional)
- `historial_de_mensajes_en_asesor`: Conversación con el asesor (requerido)
- `company_name`: Nombre de la empresa (opcional)
- `group_name`: Grupo/marca (opcional)
- `user_name`: Nombre del asesor (opcional)

## Criterios de Evaluación

1. **Primera respuesta**: ¿Reconoce el contexto del cliente?
2. **Eficiencia**: ¿Evita preguntas redundantes?
3. **Valor**: ¿Cada mensaje acerca a una solución?
4. **Claridad**: ¿Lenguaje profesional y empático?
