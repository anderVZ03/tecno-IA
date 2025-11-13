import pandas as pd
import requests
import json # Necesario para procesar la respuesta JSON del modelo

# ---------------------------------------------------------------------
# 1. CONFIGURACIÓN DE LA API LOCAL (LM Studio)
# ---------------------------------------------------------------------
API_URL = "http://localhost:1234/v1/chat/completions"
# Asegúrate de que este ID coincida con el que viste en LM Studio
MODEL_ID = "llama-3.2-3b-instruct" 
headers = {"Content-Type": "application/json"}

# Este es el "cerebro" de la operación.
# Define las reglas y el formato de salida JSON.
SYSTEM_PROMPT = """
Eres un asistente de evaluación académica. Tu tarea es calificar el resumen de un estudiante basándote en un texto original y una rúbrica. Debes ser objetivo y estricto. La rúbrica es la siguiente:

1.  **Estructura (1-5 puntos):** ¿El resumen sigue una secuencia lógica? ¿Presenta las ideas principales ordenadamente?
2.  **Ortografía (1-5 puntos):** ¿Está libre de errores ortográficos y gramaticales?
3.  **Comprensión (1-5 puntos):** ¿El resumen demuestra que el autor entendió el texto original? ¿Captura la esencia?
4.  **Redacción (1-5 puntos):** ¿El texto es claro, conciso y fácil de leer?
5.  **Síntesis (1-5 puntos):** ¿El resumen se enfoca en lo esencial sin incluir opiniones personales o detalles irrelevantes?

Tu respuesta DEBE ser únicamente un objeto JSON válido, sin texto introductorio, despedidas ni comillas de bloque (```json). El formato JSON debe ser el siguiente:
{
  "calificacion_total": 0,
  "calificaciones_criterios": {
    "estructura": 0,
    "ortografia": 0,
    "comprension": 0,
    "redaccion": 0,
    "sintesis": 0
  },
  "retroalimentacion_general": "(Tu feedback general aquí)",
  "retroalimentacion_especifica": [
    {"criterio": "Estructura", "feedback": "(Tu feedback para este criterio)"},
    {"criterio": "Ortografía", "feedback": "(Tu feedback para este criterio)"},
    {"criterio": "Comprensión", "feedback": "(Tu feedback para este criterio)"},
    {"criterio": "Redacción", "feedback": "(Tu feedback para este criterio)"},
    {"criterio": "Síntesis", "feedback": "(Tu feedback para este criterio)"}
  ]
}
"""

def evaluar_resumen(texto_base, resumen):
    """
    Llama a la API local de LM Studio con el formato de chat de OpenAI.
    Espera recibir un string JSON y lo convierte en un diccionario de Python.
    """
    
    # 1. Definir el prompt del usuario (los datos)
    user_content = f"""
    Por favor, evalúa el siguiente resumen basándote en el texto original.

    --- TEXTO ORIGINAL ---
    {texto_base}

    --- RESUMEN DEL ESTUDIANTE ---
    {resumen}
    """

    # 2. Construir el payload para LM Studio (formato OpenAI)
    json_payload = {
        "model": MODEL_ID,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content}
        ],
        "temperature": 0.2, # Temperatura baja para que sea objetivo
        "stream": False
    }

    try:
        # 3. Realizar la petición POST
        response = requests.post(API_URL, headers=headers, json=json_payload)
        # Lanza un error si la petición HTTP falló (ej. 4xx, 5xx)
        response.raise_for_status() 

        # 4. Extraer la respuesta de la API
        api_respuesta_dict = response.json()
        
        # El contenido es un STRING que se ve como JSON
        json_string_respuesta = api_respuesta_dict['choices'][0]['message']['content']

        # 5. ¡Paso clave! Convertir ese STRING en un diccionario real de Python
        try:
            # Usamos json.loads() para "parsear" el string
            evaluacion_final_dict = json.loads(json_string_respuesta)
            return evaluacion_final_dict
        except json.JSONDecodeError as e:
            print(f"Error: La IA no devolvió un JSON válido.")
            print(f"Respuesta cruda recibida: {json_string_respuesta}")
            return {"error": "JSON malformado de la IA", "respuesta_cruda": json_string_respuesta}

    except requests.exceptions.RequestException as e:
        print(f"Error de conexión con LM Studio: {e}")
        print("Asegúrate de que LM Studio esté corriendo y el servidor esté iniciado.")
        return {"error": f"Error de conexión: {str(e)}"}
    except Exception as e:
        # Captura otros errores (ej. 'choices' no existe, etc.)
        print(f"Error inesperado al procesar la respuesta: {e}")
        return {"error": f"Error en API: {str(e)}"}

# ---------------------------------------------------------------------
# 2. LEER EL EXCEL (Esta lógica de tu amigo era perfecta)
# ---------------------------------------------------------------------
try:
    textos_base = pd.read_excel("resúmenes.xlsx", sheet_name="Textos Base")
    resúmenes = pd.read_excel("resúmenes.xlsx", sheet_name="Resúmenes")
except FileNotFoundError:
    print("Error: No se encontró el archivo 'resúmenes.xlsx'.")
    print("Asegúrate de que el archivo esté en la misma carpeta que el script.")
    exit()
except Exception as e:
    print(f"Error al leer el Excel: {e}")
    exit()

# ---------------------------------------------------------------------
# 3. EVALUAR CADA RESUMEN
# ---------------------------------------------------------------------
resultados = []
print("Iniciando evaluación de resúmenes...")
for _, resumen_row in resúmenes.iterrows():
    
    # Validaciones (de la lógica de tu amigo)
    if pd.isna(resumen_row["ID"]):
        print(f"Advertencia: El resumen de {resumen_row['Autor']} no tiene un ID válido. Omitiendo.")
        continue

    id_texto = int(resumen_row["ID"])
    texto_base_filtrado = textos_base[textos_base["ID"] == id_texto]

    if texto_base_filtrado.empty:
        print(f"Error: No se encontró el texto base para el ID {id_texto} (Autor: {resumen_row['Autor']}). Omitiendo.")
        continue

    # Obtenemos los datos para la API
    texto_base = texto_base_filtrado["Texto Base"].values[0]
    resumen_actual = resumen_row["Resumen"]
    autor = resumen_row["Autor"]
    
    print(f"  > Evaluando a: {autor} (ID: {id_texto})...")
    
    # Llamamos a nuestra nueva función
    evaluacion_dict = evaluar_resumen(texto_base, resumen_actual)

    # Preparamos la fila para el DataFrame de resultados
    fila_resultado = {
        "Autor": autor,
        "Resumen": resumen_actual
    }

    # "Aplanamos" el JSON para que se vea bien en Excel
    if "error" in evaluacion_dict:
        # Si algo salió mal, guardamos el error
        fila_resultado["Error"] = evaluacion_dict.get("error")
        fila_resultado["Respuesta Cruda"] = evaluacion_dict.get("respuesta_cruda", "")
    else:
        # Si todo salió bien, poblamos las columnas
        fila_resultado["Calificación Total"] = evaluacion_dict.get("calificacion_total")
        fila_resultado["Retroalimentación General"] = evaluacion_dict.get("retroalimentacion_general")
        
        # Añadir cada criterio como una columna separada
        criterios_notas = evaluacion_dict.get("calificaciones_criterios", {})
        for criterio, nota in criterios_notas.items():
            fila_resultado[f"Nota {criterio.capitalize()}"] = nota
            
        # Unir la retroalimentación específica en una sola celda (opcional)
        retro_especifica_list = evaluacion_dict.get("retroalimentacion_especifica", [])
        retro_texto = "\n".join([f"- {item['criterio']}: {item['feedback']}" for item in retro_especifica_list])
        fila_resultado["Retroalimentación Específica"] = retro_texto

    resultados.append(fila_resultado)

# ---------------------------------------------------------------------
# 4. GUARDAR RESULTADOS EN UN NUEVO EXCEL
# ---------------------------------------------------------------------
df_resultados = pd.DataFrame(resultados)
try:
    df_resultados.to_excel("resultados_evaluacion.xlsx", index=False)
    print("\n¡Evaluación completada! Revisa el archivo 'resultados_evaluacion.xlsx'.")
except PermissionError:
    print("\nError: Permiso denegado.")
    print("Por favor, cierra el archivo 'resultados_evaluacion.xlsx' si lo tienes abierto e intenta de nuevo.")
except Exception as e:
    print(f"\nError al guardar el Excel: {e}")