import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
import spacy
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

# Configuración de estilo
sns.set(style="whitegrid")

# Rutas de los archivos
current_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(current_dir, 'data')  # Ruta correcta a la carpeta 'data'

# Archivos de Reddit y sus fuentes correspondientes
reddit_files = [
    os.path.join(data_dir, 'reddit_wine_data_sentiment.csv'),          # Fuente: reddit_international
    os.path.join(data_dir, 'reddit_argentina_wine_data_sentiment.csv') # Fuente: reddit_argentina
]
reddit_sources = [
    'reddit_international',
    'reddit_argentina'
]

# Archivo del Sommelier
sommelier_file = os.path.join(data_dir, 'wine_reviews_argentina_sentiment.csv')  # Fuente: sommelier_argentina

# Directorio para guardar las imágenes
img_dir = os.path.join(current_dir, 'img')  # Asegúrate de que 'img' esté al mismo nivel que 'data'
os.makedirs(img_dir, exist_ok=True)

# Cargar el modelo de spaCy para español
try:
    nlp = spacy.load("es_core_news_sm")
except OSError:
    print("El modelo 'es_core_news_sm' de spaCy no está instalado. Ejecuta 'python -m spacy download es_core_news_sm' para instalarlo.")
    exit(1)

# Función para extraer palabras clave relacionadas con vinos
def extract_wine_keywords(text):
    """
    Extrae palabras clave relacionadas con el vino utilizando spaCy.
    """
    doc = nlp(text.lower())
    keywords = set()
    for token in doc:
        if token.pos_ in ['NOUN', 'PROPN']:
            keywords.add(token.lemma_)
    return keywords

# Función para clasificar el estilo de vino
def classify_wine_style(keywords):
    """
    Clasifica el estilo de vino basado en palabras clave.
    """
    styles = {
        'tinto': {'tinto', 'cabernet', 'merlot', 'malbec', 'pinot', 'syrah', 'chianti'},
        'blanco': {'blanco', 'sauvignon', 'chardonnay', 'riesling', 'verdejo', 'gavi'},
        'rosado': {'rosado', 'pinot grigio', 'provence'},
        'espumoso': {'espumoso', 'champagne', 'cava', 'prosecco'},
        'dulce': {'dulce', 'moscatel', 'dulzón'},
        'fortificado': {'fortificado', 'porto', 'sherry'}
    }
    
    for style, keywords_set in styles.items():
        if keywords_set.intersection(keywords):
            return style.capitalize()
    return None

# Función para generar títulos
def generate_title(row, vectorizer, sommelier_tfidf_matrix, sommelier_titles):
    """
    Genera un título representativo basado en el full_text.
    Si no se identifican palabras clave, utiliza similitud con el dataset del sommelier.
    """
    keywords = extract_wine_keywords(row['full_text'])
    style = classify_wine_style(keywords)
    
    if style:
        # Generar título basado en el estilo
        if style.lower() in ['tinto', 'blanco', 'rosado', 'espumoso', 'dulce', 'fortificado']:
            return f"Recomendación de Vino {style}"
        else:
            return "Recomendación de Vino"
    else:
        # Fallback: utilizar similitud con el sommelier dataset
        if sommelier_tfidf_matrix is not None and not sommelier_tfidf_matrix.shape[0] == 0:
            user_vector = vectorizer.transform([row['full_text']])
            similarity = cosine_similarity(user_vector, sommelier_tfidf_matrix).flatten()
            if similarity.size > 0:
                similar_idx = similarity.argmax()
                similar_title = sommelier_titles[similar_idx]
                return f"Recomendación Similar a: {similar_title}"
        return "Recomendación de Vino"

# Función para generar títulos genéricos para Reddit
def generate_generic_title(text, max_words=10):
    """
    Genera un título genérico extrayendo las primeras 'max_words' palabras del texto.
    """
    if pd.isna(text):
        return "Título Genérico"
    words = text.split()
    if len(words) <= max_words:
        return ' '.join(words)
    else:
        return ' '.join(words[:max_words]) + '...'

# ------------------------------------------------
# 1. Cargar y Combinar los Datasets de Reddit
# ------------------------------------------------

def load_and_combine_reddit(files, sources):
    """
    Carga y combina múltiples archivos de Reddit en un único DataFrame.
    Asigna la columna 'source' según la lista de fuentes proporcionada.
    """
    dfs = []
    for file, source in zip(files, sources):
        try:
            df = pd.read_csv(file)
            df['source'] = source  # Asignar la fuente correspondiente
            print(f"Dataset de Reddit '{os.path.basename(file)}' Cargado:")
            print(df.info())
            dfs.append(df)
        except FileNotFoundError:
            print(f"Error: El archivo '{file}' no se encontró.")
    if dfs:
        combined_reddit = pd.concat(dfs, ignore_index=True)
        print(f"\nDatasets de Reddit combinados. Total de entradas: {combined_reddit.shape[0]}")
        return combined_reddit
    else:
        print("No se encontraron archivos de Reddit para combinar.")
        return pd.DataFrame()

df_reddit = load_and_combine_reddit(reddit_files, reddit_sources)

# Procesamiento de Reddit
if not df_reddit.empty:
    # a. Eliminar la columna 'region_2' si existe
    if 'region_2' in df_reddit.columns:
        df_reddit.drop(columns=['region_2'], inplace=True)
        print("Columna 'region_2' eliminada del dataset de Reddit.")
    
    # b. Imputar valores faltantes en 'author' con 'Unknown'
    if 'author' in df_reddit.columns:
        df_reddit['author'] = df_reddit['author'].fillna('Unknown')
        print("Valores faltantes en 'author' imputados con 'Unknown' en Reddit.")
    
    # c. Crear 'full_text' adecuadamente
    df_reddit['full_text'] = ''
    if 'title' in df_reddit.columns and 'content' in df_reddit.columns:
        reddit_mask = df_reddit['source'].str.contains('reddit', case=False, na=False)
        df_reddit.loc[reddit_mask, 'full_text'] = df_reddit.loc[reddit_mask, 'title'].fillna('') + ' ' + df_reddit.loc[reddit_mask, 'content'].fillna('')
        print("Campo 'full_text' actualizado para las fuentes de Reddit.")
    else:
        print("Advertencia: Las columnas 'title' o 'content' no existen en el dataset de Reddit.")
    
    # d. Manejo de valores faltantes en 'variety' y 'province'
    if 'variety' in df_reddit.columns:
        df_reddit['variety'] = df_reddit['variety'].fillna('Unknown')
    else:
        df_reddit['variety'] = 'Unknown'
        print("Advertencia: La columna 'variety' no existe en el dataset de Reddit. Se ha creado con valor 'Unknown'.")
        
    if 'province' in df_reddit.columns:
        df_reddit['province'] = df_reddit['province'].fillna('Unknown')
    else:
        df_reddit['province'] = 'Unknown'
        print("Advertencia: La columna 'province' no existe en el dataset de Reddit. Se ha creado con valor 'Unknown'.")
    print("Valores faltantes en 'variety' y 'province' imputados con 'Unknown' en Reddit.")
    
    # e. Generar 'wine_id' si no existe
    if 'wine_id' not in df_reddit.columns:
        df_reddit['wine_id'] = range(1, len(df_reddit) + 1)
        print("Columna 'wine_id' creada exitosamente en el dataset de Reddit.")
    
    # **Nueva Sección: Agregar 'points' y 'price' a Reddit con valores NaN**
    for col in ['points', 'price']:
        if col not in df_reddit.columns:
            df_reddit[col] = pd.NA
            print(f"Columna '{col}' creada con valores NaN en el dataset de Reddit.")
    
    # f. Generar títulos inteligentes para Reddit
    # Cargar dataset del sommelier para referencia
    if os.path.exists(sommelier_file):
        df_sommelier = pd.read_csv(sommelier_file)
        print("\nDataset del Sommelier Cargado:")
        print(df_sommelier.info())
        
        sommelier_titles = df_sommelier['title'].tolist()
        # Verificar existencia de 'full_text' en df_sommelier
        if 'full_text' not in df_sommelier.columns:
            # Intentar crear 'full_text' a partir de 'description' o 'content' si existen
            if 'description' in df_sommelier.columns:
                df_sommelier['full_text'] = df_sommelier['description'].fillna('')
                print("Campo 'full_text' creado a partir de 'description' en el sommelier.")
            elif 'content' in df_sommelier.columns and 'title' in df_sommelier.columns:
                df_sommelier['full_text'] = df_sommelier['title'].fillna('') + ' ' + df_sommelier['content'].fillna('')
                print("Campo 'full_text' creado a partir de 'title' y 'content' en el sommelier.")
            else:
                df_sommelier['full_text'] = ''
                print("Advertencia: No se encontró 'description', 'content' ni 'title' en el sommelier. 'full_text' asignado como cadena vacía.")
        
        # Vectorización para similitud usando un único vectorizador
        vectorizer = TfidfVectorizer(stop_words='english')
        sommelier_tfidf_matrix = vectorizer.fit_transform(df_sommelier['full_text'].fillna(''))
        print("Vectorización del dataset del sommelier completada.")
    else:
        df_sommelier = pd.DataFrame()
        sommelier_titles = []
        sommelier_tfidf_matrix = None
        print("Archivo del sommelier no encontrado.")
    
    # Transformar las reseñas de Reddit usando el mismo vectorizador
    if sommelier_tfidf_matrix is not None:
        reddit_tfidf_matrix = vectorizer.transform(df_reddit['full_text'].fillna(''))
        print("Vectorización de las reseñas de Reddit completada con el mismo vectorizador.")
    else:
        reddit_tfidf_matrix = None
        print("No se pudo vectorizar las reseñas de Reddit debido a la falta del dataset del sommelier.")
    
    # Generar títulos mejorados
    if sommelier_tfidf_matrix is not None:
        df_reddit['title'] = df_reddit.apply(
            lambda row: generate_title(row, vectorizer, sommelier_tfidf_matrix, sommelier_titles), 
            axis=1
        )
        print("Títulos inteligentes generados para las reseñas de Reddit.")
    else:
        # Fallback: generar títulos genéricos
        df_reddit['title'] = df_reddit['full_text'].apply(lambda x: generate_generic_title(x))
        print("Títulos genéricos generados para las reseñas de Reddit debido a la falta del dataset del sommelier.")
    
    # g. Seleccionar columnas relevantes
    relevant_columns = ['variety', 'province', 'points', 'price', 'sentiment_label', 'full_text', 'source', 'title']
    missing_reddit_columns = [col for col in relevant_columns if col not in df_reddit.columns]
    if missing_reddit_columns:
        print(f"Advertencia: Las siguientes columnas faltan en el dataset de Reddit y serán omitidas: {missing_reddit_columns}")
        relevant_columns = [col for col in relevant_columns if col in df_reddit.columns]
    
    df_reddit_model = df_reddit[relevant_columns].copy()
    
    # ------------------------------------------------
    # 2. Cargar y Procesar el Dataset del Sommelier
    # ------------------------------------------------

def load_and_process_sommelier(file):
    """
    Carga y procesa el dataset del sommelier.
    """
    try:
        df = pd.read_csv(file)
        print("\nDataset del Sommelier Cargado:")
        print(df.info())
    except FileNotFoundError:
        print(f"Error: El archivo '{file}' no se encontró.")
        return pd.DataFrame()
    
    if not df.empty:
        # a. Eliminar la columna 'region_2' si existe
        if 'region_2' in df.columns:
            df.drop(columns=['region_2'], inplace=True)
            print("Columna 'region_2' eliminada del dataset del sommelier.")
    
        # b. Imputar valores faltantes en 'taster_name' con 'Unknown'
        if 'taster_name' in df.columns:
            df['taster_name'] = df['taster_name'].fillna('Unknown')
            print("Valores faltantes en 'taster_name' imputados con 'Unknown' en el sommelier.")
    
        # c. Crear 'full_text' adecuadamente
        if 'description' in df.columns:
            df['full_text'] = df['description'].fillna('')
            print("Campo 'full_text' actualizado a partir de 'description' en el sommelier.")
        elif 'content' in df.columns and 'title' in df.columns:
            df['full_text'] = df['title'].fillna('') + ' ' + df['content'].fillna('')
            print("Campo 'full_text' actualizado a partir de 'title' y 'content' en el sommelier.")
        else:
            df['full_text'] = ''
            print("Advertencia: No se encontró 'description', 'content' ni 'title' en el sommelier. 'full_text' asignado como cadena vacía.")
    
        # d. Manejo de valores faltantes en 'variety' y 'province'
        if 'variety' in df.columns:
            df['variety'] = df['variety'].fillna('Unknown')
        if 'province' in df.columns:
            df['province'] = df['province'].fillna('Unknown')
        print("Valores faltantes en 'variety' y 'province' imputados con 'Unknown' en el sommelier.")
    
        # e. Generar 'wine_id' si no existe
        if 'wine_id' not in df.columns:
            df['wine_id'] = range(1, len(df) + 1)
            print("Columna 'wine_id' creada exitosamente en el dataset del sommelier.")
    
        # f. Añadir la columna 'source' con un valor constante
        df['source'] = 'sommelier_argentina'
        print("Columna 'source' añadida al dataset del sommelier.")
    
        # g. Seleccionar columnas relevantes (incluyendo 'source' ahora)
        sommelier_relevant = ['variety', 'province', 'points', 'price', 'sentiment_label', 'full_text', 'source', 'title']
        missing_sommelier_columns = [col for col in sommelier_relevant if col not in df.columns]
        if missing_sommelier_columns:
            print(f"Advertencia: Las siguientes columnas faltan en el dataset del sommelier y serán omitidas: {missing_sommelier_columns}")
            sommelier_relevant = [col for col in sommelier_relevant if col in df.columns]
    
        df_sommelier_model = df[sommelier_relevant].copy()
        return df_sommelier_model
    else:
        return pd.DataFrame()

# Cargar y procesar el dataset del sommelier
df_sommelier_model = load_and_process_sommelier(sommelier_file)

# ------------------------------------------------
# 3. Concatenar Ambos Datasets (Reddit y Sommelier)
# ------------------------------------------------

if not df_reddit_model.empty and not df_sommelier_model.empty:
    df_combined_model = pd.concat([df_reddit_model, df_sommelier_model], ignore_index=True)
    print("\nDatasets de Reddit y Sommelier concatenados.")
    print(f"Total de entradas combinadas: {df_combined_model.shape[0]}")
elif not df_reddit_model.empty:
    df_combined_model = df_reddit_model.copy()
    print("\nSolo el dataset de Reddit está disponible. Se utiliza como dataset combinado.")
    print(f"Total de entradas combinadas: {df_combined_model.shape[0]}")
elif not df_sommelier_model.empty:
    df_combined_model = df_sommelier_model.copy()
    print("\nSolo el dataset del sommelier está disponible. Se utiliza como dataset combinado.")
    print(f"Total de entradas combinadas: {df_combined_model.shape[0]}")
else:
    df_combined_model = pd.DataFrame()
    print("\nNo hay datasets disponibles para combinar.")

# ------------------------------------------------
# 4. Exploración y Visualización en el Dataset Combinado
# ------------------------------------------------

if not df_combined_model.empty:
    # a. Visualización de 'points' por 'source'
    plt.figure(figsize=(10, 6))
    sns.boxplot(data=df_combined_model.dropna(subset=['points']), x='source', y='points')
    plt.title('Distribución de Puntuaciones por Fuente')
    plt.xlabel('Fuente')
    plt.ylabel('Puntuación (points)')
    plt.tight_layout()
    plt.savefig(os.path.join(img_dir, 'puntuaciones_por_fuente.png'))
    plt.close()
    print("Gráfico 'puntuaciones_por_fuente.png' guardado en 'img/'.")
    
    # b. Visualización de 'price' por 'source'
    plt.figure(figsize=(10, 6))
    sns.boxplot(data=df_combined_model.dropna(subset=['price']), x='source', y='price')
    plt.title('Distribución de Precios por Fuente')
    plt.xlabel('Fuente')
    plt.ylabel('Precio ($)')
    plt.tight_layout()
    plt.savefig(os.path.join(img_dir, 'precios_por_fuente.png'))
    plt.close()
    print("Gráfico 'precios_por_fuente.png' guardado en 'img/'.")
    
    # c. Relación entre 'price' y 'points'
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df_combined_model.dropna(subset=['price', 'points']), x='price', y='points', hue='source', alpha=0.7)
    plt.title('Relación entre Precio y Puntuación de Vinos')
    plt.xlabel('Precio ($)')
    plt.ylabel('Puntuación (points)')
    plt.legend(title='Fuente')
    plt.tight_layout()
    plt.savefig(os.path.join(img_dir, 'relacion_precio_puntuacion.png'))
    plt.close()
    print("Gráfico 'relacion_precio_puntuacion.png' guardado en 'img/'.")
    
    # d. Estadísticas descriptivas
    print("\nEstadísticas descriptivas de 'points' por fuente:")
    print(df_combined_model.groupby('source')['points'].describe())
    
    print("\nEstadísticas descriptivas de 'price' por fuente:")
    print(df_combined_model.groupby('source')['price'].describe())
else:
    print("\nNo hay datos combinados para generar visualizaciones.")

# ------------------------------------------------
# 5. Preparación para el Motor de Recomendación
# ------------------------------------------------

if not df_combined_model.empty:
    # Selección de Características Relevantes incluyendo 'title'
    relevant_columns = ['variety', 'province', 'points', 'price', 'sentiment_label', 'full_text', 'source', 'title']
    
    # Verifica que todas las columnas existen
    missing_relevant = [col for col in relevant_columns if col not in df_combined_model.columns]
    if missing_relevant:
        print(f"Advertencia: Las siguientes columnas faltan en el DataFrame y serán omitidas: {missing_relevant}")
        relevant_columns = [col for col in relevant_columns if col in df_combined_model.columns]
    
    df_model = df_combined_model[relevant_columns].copy()
    
    # Guardar el Dataset Preparado para el Modelo
    prepared_file = os.path.join(data_dir, 'wine_data_prepared_with_title.csv')
    df_model.to_csv(prepared_file, index=False)
    
    if os.path.exists(prepared_file):
        print(f"\nDataset preparado guardado exitosamente en: {prepared_file}")
    else:
        print("\nError al guardar el dataset preparado.")

# ------------------------------------------------
# 6. Asignar Precios a las Reseñas de Reddit
# ------------------------------------------------

def assign_price_to_reddit(prepared_file, data_dir):
    """
    Asigna el precio de las reseñas del sommelier a las reseñas de Reddit basándose en títulos similares.
    """
    # Cargar el dataset preparado
    df_prepared = pd.read_csv(prepared_file)
    
    # Separar Reddit y Sommelier
    df_reddit = df_prepared[df_prepared['source'].str.contains('reddit', case=False, na=False)].copy()
    df_sommelier = df_prepared[df_prepared['source'] == 'sommelier_argentina'].copy()
    
    print("\nResumen de Reseñas de Reddit antes de asignar precios:")
    print(df_reddit[['title', 'price']].head())
    
    # Identificar reseñas de Reddit con títulos similares
    # Suponiendo que los títulos similares siguen el formato "Recomendación Similar a: {similar_title}"
    similar_title_prefix = "Recomendación Similar a: "
    df_reddit['similar_title'] = df_reddit['title'].apply(
        lambda x: x.replace(similar_title_prefix, '') if isinstance(x, str) and x.startswith(similar_title_prefix) else None
    )
    
    # Realizar el merge para obtener el precio del sommelier
    df_reddit = df_reddit.merge(
        df_sommelier[['title', 'price']],
        left_on='similar_title',
        right_on='title',
        how='left',
        suffixes=('', '_sommelier')
    )
    
    # Asignar el precio del sommelier a Reddit
    df_reddit['price'] = df_reddit['price_sommelier']
    
    # Eliminar columnas innecesarias
    df_reddit.drop(['similar_title', 'title_sommelier'], axis=1, inplace=True)
    
    # Reemplazar las entradas originales en el dataset preparado
    df_prepared.update(df_reddit)
    
    # Guardar el dataset actualizado
    df_prepared.to_csv(prepared_file, index=False)
    print("\nPrecio asignado a las reseñas de Reddit y dataset combinado actualizado.")
    
    # Mostrar un resumen después de la asignación
    print("\nResumen de Reseñas de Reddit después de asignar precios:")
    print(df_reddit[['title', 'price']].head())

# Llamar a la función después de guardar el dataset preparado
assign_price_to_reddit(prepared_file, data_dir)
