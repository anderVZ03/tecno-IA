import streamlit as st
import requests
import json
import pandas as pd

# ---------------------------------------------------------------------
# 1. LA LÓGICA DE IA (CON PROMPT SIMPLIFICADO)
# ---------------------------------------------------------------------

# Configuración de la API local
API_URL = "http://localhost:1234/v1/chat/completions"
MODEL_ID = "llama-3.2-3b-instruct"
headers = {"Content-Type": "application/json"}

# --- ¡CAMBIO IMPORTANTE AQUÍ! ---
# Simplificamos el JSON a un formato "plano" (sin anidar).
# Esto es MUCHO más fácil de generar para un modelo 3B.
SYSTEM_PROMPT = """
Eres un asistente de evaluación académica. Tu tarea es calificar el resumen de un estudiante basándote en un texto original y una rúbrica. Debes ser objetivo y estricto. La rúbrica es la siguiente:

1.  **Estructura (1-5 puntos):** ¿El resumen sigue una secuencia lógica?
2.  **Ortografía (1-5 puntos):** ¿Está libre de errores ortográficos y gramaticales?
3.  **Comprensión (1-5 puntos):** ¿El resumen demuestra que el autor entendió el texto original?
4.  **Redacción (1-5 puntos):** ¿El texto es claro, conciso y fácil de leer?
5.  **Síntesis (1-5 puntos):** ¿El resumen se enfoca en lo esencial?

Tu respuesta DEBE ser únicamente un objeto JSON válido, sin olvidarte de comillas, cierre de llaves del JSON por favor, no lo olvides y uso de comas para separar elementos, sin texto introductorio, con este formato "plano":
{
  "nota_estructura": 0,
  "nota_ortografia": 0,
  "nota_comprension": 0,
  "nota_redaccion": 0,
  "nota_sintesis": 0,
  "calificacion_total": 0,
  "retroalimentacion_general": "Tu feedback general aquí"
}
"""

def evaluar_resumen(texto_base, resumen):
    """
    Llama a la API local de LM Studio.
    Esta versión es ROBUSTA: limpia la respuesta para extraer solo el JSON.
    """
    
    user_content = f"""
    Por favor, evalúa el siguiente resumen basándote en el texto original.
    --- TEXTO ORIGINAL ---
    {texto_base}
    --- RESUMEN DEL ESTUDIANTE ---
    {resumen}
    """

    json_payload = {
        "model": MODEL_ID,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content}
        ],
        "temperature": 0.2,
        "stream": False
    }

    try:
        response = requests.post(API_URL, headers=headers, json=json_payload, timeout=300)
        response.raise_for_status() 

        api_respuesta_dict = response.json()
        json_string_respuesta = api_respuesta_dict['choices'][0]['message']['content']

        # El código de "limpieza" sigue siendo útil por si el modelo
        # añade texto basura al final (ej. ```json ... ```)

        start_index = json_string_respuesta.find('{')
        end_index = json_string_respuesta.rfind('}')

        if start_index != -1 and end_index != -1 and end_index > start_index:
            json_limpio = json_string_respuesta[start_index : end_index + 1]

            try:
                evaluacion_final_dict = json.loads(json_limpio)
                return evaluacion_final_dict
            except json.JSONDecodeError as e:
                # Si esto falla, es porque el JSON está malformado por dentro
                st.error(f"Error al parsear el JSON extraído: {e}")
                st.subheader("Respuesta Cruda (Original):")
                st.text(json_string_respuesta)
                st.subheader("Intento de JSON (Limpio):")
                st.text(json_limpio)
                return {"error": "JSON malformado (revisa la consola de LM Studio)", "respuesta_cruda": json_string_respuesta}
        else:
            st.error("Error: No se encontró un objeto JSON ({...}) en la respuesta de la IA.")
            st.subheader("Respuesta Cruda (Original):")
            st.text(json_string_respuesta)
            return {"error": "No se encontró un JSON en la respuesta de la IA", "respuesta_cruda": json_string_respuesta}

    except requests.exceptions.RequestException as e:
        return {"error": f"Error de conexión con LM Studio: {str(e)}"}
    except Exception as e:
        return {"error": f"Error en API: {str(e)}"}

# ---------------------------------------------------------------------
# 2. LA INTERFAZ WEB (Actualizada al formato plano)
# ---------------------------------------------------------------------

st.title("🤖 Evaluador Automático de Resúmenes")
st.write("Esta app usa un modelo Llama local (vía LM Studio) para calificar resúmenes.")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Texto Original")
    texto_base_input = st.text_area("Pega el texto original aquí:", height=300, key="base")

with col2:
    st.subheader("Resumen del Estudiante")
    resumen_input = st.text_area("Pega el resumen a evaluar aquí:", height=300, key="resumen")

if st.button("Evaluar Resumen"):
    if texto_base_input.strip() and resumen_input.strip():
        with st.spinner("El modelo está pensando... Esto puede tardar unos segundos..."):
            resultado = evaluar_resumen(texto_base_input, resumen_input)
        
        st.subheader("Resultados de la Evaluación")
        
        if "error" in resultado:
            # El error ya se muestra dentro de la función `evaluar_resumen`
            pass
        else:
            st.success("¡Evaluación completada!")
            
            # --- ¡CAMBIO IMPORTANTE AQUÍ! ---
            # Leemos las claves planas del JSON
            
            st.metric(label="Calificación Total", value=f"{resultado.get('calificacion_total', 0)} / 25")
            
            st.subheader("Retroalimentación General")
            st.write(resultado.get('retroalimentacion_general', "N/A"))
            
            st.subheader("Calificaciones por Criterio")
            
            # Creamos la tabla a partir de las claves planas
            criterios_data = [
                ("Estructura", resultado.get('nota_estructura', 0)),
                ("Ortografía", resultado.get('nota_ortografia', 0)),
                ("Comprensión", resultado.get('nota_comprension', 0)),
                ("Redacción", resultado.get('nota_redaccion', 0)),
                ("Síntesis", resultado.get('nota_sintesis', 0))
            ]
            df_criterios = pd.DataFrame(criterios_data, columns=['Criterio', 'Nota'])
            st.table(df_criterios)
            
            # --- FIN DEL CAMBIO ---
            
            with st.expander("Ver respuesta JSON cruda del modelo"):
                st.json(resultado)
                
    else:
        st.warning("Por favor, completa ambos campos de texto.")