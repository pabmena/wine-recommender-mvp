from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import pickle
import os
import numpy as np

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Cambia esto por una clave secreta segura

# Rutas de los archivos
current_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(current_dir, 'data')

# Ruta al dataset de perfiles de vino
profiles_file = os.path.join(data_dir, 'wine_profiles6.csv')  # Actualizado a 'wine_profiles6.csv'

# Ruta al vectorizador
vectorizer_file = os.path.join(data_dir, 'vectorizer.pkl')

# Cargar el dataset de perfiles de vino
try:
    wine_profiles = pd.read_csv(profiles_file)
    print("Dataset de perfiles de vino cargado correctamente.")
except FileNotFoundError:
    print(f"Error: '{profiles_file}' no se encontró en la carpeta 'data/'.")
    wine_profiles = pd.DataFrame()

# Verificar columnas duplicadas
if wine_profiles.columns.duplicated().any():
    duplicated_cols = wine_profiles.columns[wine_profiles.columns.duplicated()].tolist()
    print(f"Advertencia: Columnas duplicadas encontradas: {duplicated_cols}")
    # Eliminar columnas duplicadas manteniendo la primera ocurrencia
    wine_profiles = wine_profiles.loc[:, ~wine_profiles.columns.duplicated()]
    print("Columnas duplicadas eliminadas.")

# Asegurarnos de que 'variedad' existe en 'wine_profiles'
if 'variedad' not in wine_profiles.columns:
    wine_profiles['variedad'] = 'Variedad Desconocida'

# Asegurarnos de que 'source' existe en 'wine_profiles'
if 'source' not in wine_profiles.columns:
    wine_profiles['source'] = 'unknown'  # O cualquier valor predeterminado

# Cargar el vectorizador
try:
    with open(vectorizer_file, 'rb') as f:
        vectorizer = pickle.load(f)
    print("Vectorizador cargado correctamente.")
except FileNotFoundError:
    print(f"Error: '{vectorizer_file}' no se encontró en la carpeta 'data/'. Se reentrenará el vectorizador.")
    vectorizer = TfidfVectorizer(stop_words='english')
    # Entrenar el vectorizador en el dataset del sommelier
    if 'source' in wine_profiles.columns:
        sommelier_text = wine_profiles[wine_profiles['source'] == 'sommelier_argentina']['full_text'].fillna('')
    else:
        sommelier_text = wine_profiles['full_text'].fillna('')
    vectorizer.fit(sommelier_text)
    print("Vectorizador entrenado en el dataset del sommelier.")
    # Guardar el vectorizador para uso futuro
    with open(vectorizer_file, 'wb') as f:
        pickle.dump(vectorizer, f)
    print("Vectorizador reentrenado y guardado exitosamente en 'vectorizer.pkl'.")

# Verificar que 'full_text' existe
if 'full_text' not in wine_profiles.columns:
    print("Error: La columna 'full_text' no existe en 'wine_profiles6.csv'. Por favor, verifica tu archivo de datos.")
    tfidf_matrix = None
else:
    # Vectorizar el dataset
    wine_profiles['full_text'] = wine_profiles['full_text'].fillna('')
    tfidf_matrix = vectorizer.transform(wine_profiles['full_text'])

# Lista de preguntas del quiz (manteniendo las mismas preguntas)
questions = [
    {
        'id': 'experience_level',
        'text': '¿Cómo calificarías tu nivel de experiencia en vinos?',
        'options': ['Principiante', 'Intermedio', 'Avanzado'],
        'type': 'single_choice'
    },
    {
        'id': 'frutas_rojas',
        'text': '¿Qué tanto disfrutas de los sabores a frutas rojas como cerezas y frambuesas en el vino?',
        'type': 'likert'
    },
    {
        'id': 'especias',
        'text': '¿Qué opinas de las notas especiadas como la pimienta negra y la canela en el vino?',
        'type': 'likert'
    },
    {
        'id': 'acidez',
        'text': '¿Cómo te sientes acerca de la acidez en los vinos? (Esa sensación refrescante y crujiente)',
        'type': 'likert'
    },
    # Agrega más preguntas según sea necesario
    {
        'id': 'ocasion',
        'text': '¿Para qué ocasión estás buscando un vino?',
        'options': ['Cena informal', 'Celebración especial', 'Regalo', 'Maridaje específico', 'Disfrutar solo', 'Evento formal'],
        'type': 'single_choice'
    },
    {
        'id': 'maridaje',
        'text': '¿Planeas acompañar el vino con alguna comida en particular?',
        'options': ['Carnes rojas', 'Aves', 'Pescados y mariscos', 'Pastas', 'Quesos', 'Postres', 'Comida picante', 'No tengo un maridaje específico en mente'],
        'type': 'single_choice'
    },
    {
        'id': 'precio',
        'text': '¿Cuál es tu rango de precio preferido por botella?',
        'options': ['Menos de $10', '$10 - $20', '$20 - $50', 'Más de $50'],
        'type': 'single_choice'
    }
]

# Rutas de la aplicación

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if request.method == 'POST':
        # Obtener respuestas
        responses = request.form.to_dict()
        session['responses'] = responses
        return redirect(url_for('results'))
    else:
        return render_template('quiz.html', questions=questions)

@app.route('/results')
def results():
    responses = session.get('responses', {})
    if not responses:
        return redirect(url_for('quiz'))

    user_profile, price_filter = create_user_profile(responses)
    recommendations = get_recommendations(user_profile, price_filter)
    return render_template('results.html', recommendations=recommendations)

# Funciones auxiliares

def create_user_profile(responses):
    """
    Convierte las respuestas del quiz en un perfil de usuario.
    Retorna el vector de perfil y el filtro de precio seleccionado.
    """
    # Define una escala para las preguntas de tipo 'likert'
    likert_scale = {
        '1': -2,  # Me desagrada mucho
        '2': -1,  # Me desagrada
        '3': 0,   # Neutral
        '4': 1,   # Me gusta
        '5': 2    # Me encanta
    }

    # Atributos que corresponden a las preguntas de tipo 'likert'
    attribute_likert = ['frutas_rojas', 'especias', 'acidez']

    # Crear un diccionario para el perfil del usuario
    user_profile_dict = {}

    for attr in attribute_likert:
        value = responses.get(attr, '3')  # Default a 'Neutral' si no se responde
        user_profile_dict[attr] = likert_scale.get(value, 0)

    # Convertir el diccionario en un DataFrame
    user_profile = pd.DataFrame([user_profile_dict])

    # Obtener el filtro de precio seleccionado
    precio = responses.get('precio', 'Más de $50')  # Default a 'Más de $50' si no se responde

    # Definir rangos de precios
    price_ranges = {
        'Menos de $10': (0, 10),
        '$10 - $20': (10, 20),
        '$20 - $50': (20, 50),
        'Más de $50': (50, np.inf)
    }

    price_min, price_max = price_ranges.get(precio, (50, np.inf))

    return user_profile, (price_min, price_max)

def get_recommendations(user_profile, price_filter):
    """
    Genera recomendaciones basadas en el perfil del usuario y el rango de precio.
    """
    if wine_profiles.empty or tfidf_matrix is None:
        return []

    # Calcular la similitud entre el perfil del usuario y los atributos relevantes
    similarity = cosine_similarity(user_profile, wine_profiles[['frutas_rojas', 'especias', 'acidez']])[0]

    # Añadir la similitud al DataFrame
    wine_profiles_with_similarity = wine_profiles.copy()
    wine_profiles_with_similarity['similarity'] = similarity

    # Incorporar el análisis de sentimiento
    # Ajustar la similitud según la polaridad
    if 'polarity' not in wine_profiles_with_similarity.columns:
        print("Error: La columna 'polarity' no existe en 'wine_profiles6.csv'.")
        return []
    wine_profiles_with_similarity['adjusted_similarity'] = wine_profiles_with_similarity['similarity'] + wine_profiles_with_similarity['polarity']

    # **Normalizar la similitud ajustada entre 0 y 1**
    max_adjusted_similarity = wine_profiles_with_similarity['adjusted_similarity'].max()
    if max_adjusted_similarity > 0:
        wine_profiles_with_similarity['adjusted_similarity'] /= max_adjusted_similarity

    # Filtrar vinos con sentimientos negativos fuertes
    threshold = -0.2  # Ajusta este valor según tus datos
    filtered_wines = wine_profiles_with_similarity[wine_profiles_with_similarity['polarity'] > threshold]

    print("\nValores de 'polarity' después del ajuste:")
    print(filtered_wines[['wine_id', 'title', 'polarity', 'similarity', 'adjusted_similarity']].head())

    # Aplicar el filtro de precio
    price_min, price_max = price_filter
    if 'price' in filtered_wines.columns:
        # Asegurarse de que 'price' es numérico
        filtered_wines = filtered_wines[pd.to_numeric(filtered_wines['price'], errors='coerce').notnull()]
        filtered_wines['price'] = filtered_wines['price'].astype(float)
        filtered_wines = filtered_wines[
            (filtered_wines['price'] >= price_min) & (filtered_wines['price'] <= price_max)
        ]
    else:
        print("Error: La columna 'price' no existe en el DataFrame filtrado.")
        return []

    # Ordenar por similitud ajustada
    top_wines = filtered_wines.sort_values(by='adjusted_similarity', ascending=False).head(8)

    # Seleccionar columnas relevantes, incluyendo 'title', 'price', 'polarity'
    required_columns = ['wine_id', 'variedad', 'title', 'price', 'sentiment_label', 'polarity', 'similarity', 'adjusted_similarity', 'source']
    available_columns = [col for col in required_columns if col in top_wines.columns]
    recommendations = top_wines[available_columns].copy()

    # Evitar duplicación de 'similarity' renombrando 'adjusted_similarity' y eliminando la original 'similarity'
    if 'similarity' in recommendations.columns and 'adjusted_similarity' in recommendations.columns:
        # Eliminar la columna original 'similarity'
        recommendations = recommendations.drop('similarity', axis=1)
        # Renombrar 'adjusted_similarity' a 'similarity'
        recommendations = recommendations.rename(columns={'adjusted_similarity': 'similarity'})

    # Rellenar 'variedad' desde 'title' si está como 'Variedad Desconocida' o 'Unknown'
    recommendations['variedad'] = recommendations.apply(
        lambda row: extract_variedad_from_title(row['title']) if pd.isna(row['variedad']) or row['variedad'] == 'Variedad Desconocida' or row['variedad'] == 'Unknown' else row['variedad'],
        axis=1
    )

    # Convertir a diccionario
    recommendations = recommendations.to_dict('records')

    # Formatear los precios si es necesario
    for wine in recommendations:
        if 'price' in wine and pd.notna(wine['price']):
            wine['price'] = round(wine['price'], 2)
        else:
            wine['price'] = None  # O asignar un valor por defecto

    # Verificar valores de 'polarity' y 'variedad'
    print("\nRecomendaciones Generadas:")
    for wine in recommendations:
        print(wine)

    # Verificar que 'polarity' está presente
    for wine in recommendations:
        if 'polarity' not in wine:
            print(f"Advertencia: El vino con ID {wine.get('wine_id')} no tiene 'polarity'.")
        else:
            print(f"Vino ID {wine['wine_id']} - Polaridad: {wine['polarity']}")

    return recommendations

def extract_variedad_from_title(title):
    """
    Extrae la variedad de uva del título del vino.
    Asume que la variedad está al final del título entre paréntesis o después del último espacio.
    """
    # Intentar extraer variedad entre paréntesis
    if '(' in title and ')' in title:
        try:
            # Extraer texto dentro de paréntesis
            dentro_parentesis = title.split('(')[-2].split(')')[0]
            # Suponiendo que la variedad es la última palabra antes del paréntesis
            variedad = dentro_parentesis.split()[-1]
            return variedad
        except IndexError:
            pass

    # Si no hay paréntesis, extraer la última palabra
    return title.split()[-1]

if __name__ == '__main__':
    app.run(debug=True)







