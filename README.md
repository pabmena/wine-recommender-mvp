# -wine-recommender-mvp

Título del Proyecto
Desarrollo de una Plataforma de IA para Recomendación Personalizada de Vinos mediante Análisis de Sentimiento del Mercado

Descripción del Proyecto
Este proyecto integra técnicas de Inteligencia Artificial, Procesamiento de Lenguaje Natural (PLN) y Aprendizaje Automático para analizar datos no estructurados (reseñas de vinos y publicaciones en redes sociales) con el fin de:

Identificar las preferencias y sentimientos de los consumidores hacia distintos vinos.
Ofrecer recomendaciones personalizadas a los usuarios finales (consumidores) en función de sus gustos y el análisis de sentimiento del mercado.
Proveer insights a bodegas, distribuidores y minoristas para optimizar sus estrategias de producción y marketing.
La plataforma combina análisis de sentimiento, filtrado por atributos sensoriales y un motor de recomendación que tiene en cuenta las preferencias del usuario obtenidas a través de un quiz interactivo. Además, integra una interfaz web (Flask) que permite a los usuarios interactuar con el sistema.

Objetivos del Proyecto
Objetivo General:
Desarrollar una plataforma que, mediante IA y análisis de sentimiento del mercado, recomiende vinos personalizados a los consumidores, mejorando así la toma de decisiones de las bodegas y optimizando la experiencia de compra.

Objetivos Específicos:

Recolección y Procesamiento de Datos:
Obtener reseñas de vinos y datos de redes sociales, limpiarlos y prepararlos para el análisis.

Análisis de Sentimiento:
Desarrollar un modelo que clasifique las reseñas en positivas, negativas o neutrales, y calcule la polaridad (entre -1 y 1).

Motor de Recomendación:
Implementar un sistema de recomendación que, a partir de las preferencias del usuario (capturadas en un quiz) y las características sensoriales del vino (atributos extraídos del texto), sugiera los vinos más adecuados.

Interfaz de Usuario:
Crear una web app con Flask para que el consumidor responda un quiz, obtenga recomendaciones y que las bodegas puedan visualizar insights.

Validación y Optimización:
Realizar pruebas con datos reales, ajustar el modelo y la interfaz según feedback de usuarios y bodegas.

Datos y Técnicas Utilizadas
Datos:
Reseñas de vinos provenientes de archivos CSV preprocesados (wine_data_prepared_with_title.csv, wine_profiles6.csv).
Publicaciones en redes sociales (opcional, según disponibilidad).

Procesamiento de Lenguaje Natural (PLN):
Tokenización y lematización con NLTK (inglés).
Eliminación de stopwords.
Extracción de atributos sensoriales (frutas rojas, especias, acidez, etc.) a partir de palabras clave.

Análisis de Sentimiento:
Uso de TextBlob (en inglés) para calcular la polaridad de cada reseña.
Clasificación de sentimiento_label en Positivo/Negativo/Neutral en base a la polaridad calculada.

Aprendizaje Automático y Recomendación:
Uso de similitud coseno (cosine_similarity) para medir cercanía entre el perfil del usuario (sus preferencias) y las características sensoriales normalizadas de cada vino.
MinMaxScaler para normalizar atributos.
Filtrado por polaridad y precio para refinar las sugerencias.

Estructura del Proyecto

data/: Contiene los archivos CSV de datos preparados (wine_data_prepared_with_title.csv, wine_profiles6.csv, etc.).
key_attributes_wine.py: Script para procesar datos, asignar atributos sensoriales, calcular polaridad, normalizar datos y generar wine_profiles6.csv.

app.py: Aplicación Flask que:
Muestra el quiz.
Procesa las respuestas del usuario.
Calcula el perfil del usuario.
Genera las recomendaciones.
Renderiza las plantillas HTML (templates/) para mostrar los resultados.

templates/: Contiene las plantillas HTML (base.html, quiz.html, results.html, etc.).
static/: Contiene archivos CSS, JS y recursos estáticos.

Pasos para Ejecutar el Proyecto
1. Clonar el repositorio:
git clone https://github.com/pabmena/wine-recommender-mvp.git
cd wine-recommender-mvp

2. Crear y activar un entorno virtual:
Windows (CMD):
python -m venv venv
venv\Scripts\activate

Windows (Git Bash):
python -m venv venv
source venv/Scripts/activate

Unix/macOS:
python3 -m venv venv
source venv/bin/activate

3. Instalar dependencias:
pip install -r requirements.txt

4. Descargar recursos de NLTK:
python
>>> import nltk
>>> nltk.download('punkt')
>>> nltk.download('stopwords')
>>> nltk.download('wordnet')
>>> exit()

5. Procesar los datos: Ejecutar key_attributes_wine.py para generar wine_profiles6.csv:
python key_attributes_wine.py
Verificar que el archivo wine_profiles6.csv se haya generado correctamente en data/.

6. Ejecutar la aplicación Flask:
python app.py
Abre el navegador en: http://127.0.0.1:5000

7. Interacción con la Aplicación:
Completa el quiz en /quiz.
Envía las respuestas.
La aplicación mostrará las recomendaciones, con una descripción dinámica de las características y sugerencias personalizadas.

Contacto
Autor: Pablo Menardi
Email: pabmena@yahoo.com