# 🤖 Evaluador Automático de Resúmenes con IA Local

Este proyecto utiliza un modelo de lenguaje local (Llama 3.2 3B) para calificar automáticamente resúmenes de estudiantes basándose en un texto original y una rúbrica predefinida.

El sistema funciona 100% local, sin necesidad de APIs pagadas ni de enviar datos a la nube, garantizando la privacidad.

## 🚀 Características

* **Procesamiento por Lote:** Lee un archivo `resúmenes.xlsx`, procesa múltiples resúmenes y genera un `resultados_evaluacion.xlsx` con las notas.
* **Aplicación Web Interactiva:** Incluye una interfaz web simple (hecha con Streamlit) para probar la evaluación de un resumen a la vez copiando y pegando texto.
* **Modelo Local:** Se integra con [LM Studio](https://lmstudio.ai/) para ejecutar modelos de IA localmente.

## 🛠️ Tecnologías Utilizadas

* Python 3.10+
* LM Studio (como servidor de modelo local)
* Modelo: `llama-3.2-3b-instruct`
* **Librerías Python:**
    * `pandas` y `openpyxl` (para manejar archivos Excel)
    * `streamlit` (para la interfaz web)
    * `requests` (para comunicarse con la API de LM Studio)

---

## ⚙️ Configuración del Entorno

Sigue estos pasos para poner en marcha el proyecto.

### 1. Configurar el Modelo en LM Studio

Antes de ejecutar el código, necesitas tener el modelo de IA sirviendo localmente.

1.  Descarga e instala [LM Studio](https://lmstudio.ai/).
2.  En la pestaña de búsqueda (lupa 🔎), busca y descarga el modelo: `llama-3.2-3b-instruct`.
3.  Ve a la pestaña del servidor local (icono `<->`).
4.  En la parte superior, selecciona el modelo `llama-3.2-3b-instruct` que descargaste.
5.  Haz clic en **"Start Server"**.

¡Listo! Ahora tienes una API de IA compatible con OpenAI ejecutándose en `http://localhost:1234`.

### 2. Configurar el Entorno de Python

1.  **Clonar o descargar el proyecto:**
    ```bash
    git clone [URL_DE_TU_REPO]
    cd [NOMBRE_DEL_PROYECTO]
    ```

2.  **Crear un entorno virtual:**
    ```bash
    # En Windows
    python -m venv venv

    # En macOS/Linux
    python3 -m venv venv
    ```

3.  **Activar el entorno virtual:**
    ```bash
    # En Windows
    .\venv\Scripts\activate

    # En macOS/Linux
    source venv/bin/activate
    ```
    *Verás `(venv)` al inicio de tu línea de comandos.*

4.  **Instalar las dependencias:**
    El archivo `requirements.txt` contiene todas las librerías necesarias.
    ```bash
    pip install -r requirements.txt
    ```

---

## 🏃‍♂️ Cómo Usar el Proyecto

Este proyecto tiene dos modos de uso. Asegúrate de tener **LM Studio corriendo y el entorno `venv` activado** para ambos.

### Versión 1: Script de Lote (Batch) con Excel

Esta versión es ideal para calificar a toda una clase.

1.  **Prepara tu archivo Excel:**
    * Crea un archivo llamado `resúmenes.xlsx`.
    * Debe tener dos hojas:
        * **`Textos Base`**: Con columnas `ID` y `Texto Base`.
        * **`Resúmenes`**: Con columnas `ID`, `Autor` y `Resumen`.
    * El `ID` en la hoja "Resúmenes" se usa para encontrar el "Texto Base" correspondiente.

2.  **Ejecuta el script:**
    ```bash
    python3 script.py
    ```

3.  **Revisa los resultados:**
    El script generará un nuevo archivo `resultados_evaluacion.xlsx` con las calificaciones y la retroalimentación de la IA.

### Versión 2: Aplicación Web (Streamlit)

Esta versión es perfecta para demostraciones o pruebas rápidas.

1.  **Ejecuta la aplicación Streamlit:**
    ```bash
    streamlit run app.py
    ```

2.  **Abre tu navegador:**
    Streamlit abrirá automáticamente tu navegador en una URL local (ej. `http://localhost:8501`).

3.  **Usa la App:**
    Pega el texto original y el resumen que quieres evaluar en las cajas de texto y haz clic en "Evaluar Resumen".

## ⚠️ Posibles Problemas

* **Error de Conexión (Connection Refused):** Asegúrate de que el servidor de LM Studio esté activo y corriendo en el puerto `1234` **antes** de ejecutar cualquier script de Python.
* **Errores de Formato o `JSONDecodeError`:** El modelo `llama-3.2-3b-instruct` es pequeño. A veces puede fallar al generar un formato perfecto (como JSON). La versión `app.py` utiliza un parser de texto simple (`::`) que es mucho más robusto. Si `script.py` falla, considera aplicar esa misma lógica de parser simple.