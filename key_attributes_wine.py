import pandas as pd
import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import string
import os
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity 
from textblob import TextBlob

# Descargar recursos de NLTK si no están disponibles
nltk.download('punkt')
nltk.download('wordnet')

# Obtener el directorio actual y definir data_dir correctamente
current_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(current_dir, 'data')  # Asegúrate de que 'data' es la carpeta correcta

# Ruta absoluta al archivo preparado
file_path = os.path.join(data_dir, 'wine_data_prepared_with_title.csv')

# Cargar el archivo preparado
try:
    df = pd.read_csv(file_path)
    print("Archivo cargado correctamente.")
    print(df.head())  # Muestra las primeras filas como confirmación
except FileNotFoundError:
    print(f"Archivo no encontrado en la ruta: {file_path}")
    exit(1)  # Salir del script si el archivo no se encuentra

# Verificar la existencia de 'price' y 'title'
for col in ['price', 'title']:
    if col not in df.columns:
        print(f"Advertencia: La columna '{col}' no existe en el DataFrame. Se asignará un valor por defecto.")
        df[col] = None  # O asignar un valor por defecto apropiado

# Definir el diccionario de atributos
attribute_dict = {
    'frutas_rojas': ['cereza', 'frambuesa', 'fresa', 'granada', 'sandía', 'cherry', 'raspberry', 'strawberry', 'pomegranate', 'watermelon'],
    'frutas_negras': ['plum', 'zarzamora', 'blackberry', 'blueberry', 'currant', 'fig', 'raisin', 'mora', 'arándano', 'grosella negra', 'higo', 'pasas'],
    'frutas_cítricas': ['limón', 'lima', 'naranja', 'pomelo', 'mandarina', 'lemon', 'lime', 'orange', 'grapefruit', 'tangerine'],
    'frutas_tropicales': ['piña', 'mango', 'maracuyá', 'papaya', 'guayaba', 'coco', 'ananá', 'passionfruit', 'pineapple', 'guava', 'coconut'],
    'frutas_hueso': ['melocotón', 'albaricoque', 'nectarina', 'durazno', 'peach', 'apricot', 'nectarine'],
    'frutas_secas': ['dátil', 'higo seco', 'pasas', 'almendra tostada', 'raisin', 'dried fig', 'toasted almond'],
    'especias': ['pimienta', 'pimienta negra', 'pimienta blanca', 'clavo', 'canela', 'nuez moscada', 'anís', 'cardamomo', 'jengibre', 'vainilla', 'pepper', 'clove', 'cinnamon', 'nutmeg', 'anise', 'cardamom', 'ginger', 'vanilla'],
    'notas_herbales_frescas': ['menta', 'albahaca', 'eucalipto', 'hinojo', 'cilantro', 'mint', 'basil', 'eucalyptus', 'fennel', 'coriander'],
    'notas_herbales_secas': ['tomillo', 'romero', 'orégano', 'laurel', 'thyme', 'rosemary', 'oregano', 'bay leaf'],
    'notas_florales': ['rosa', 'violeta', 'jazmín', 'lavanda', 'peonía', 'rose', 'violet', 'jasmine', 'lavender', 'peony'],
    'notas_terrosas': ['tierra húmeda', 'hongos', 'trufa', 'arcilla', 'musgo', 'wet earth', 'mushroom', 'truffle', 'clay', 'moss'],
    'madera_y_otros': ['vainilla', 'cedro', 'tostado', 'cuero', 'tabaco', 'chocolate', 'café', 'cacao', 'humo', 'caramelo', 'vanilla', 'cedar', 'toasted', 'leather', 'tobacco', 'chocolate', 'coffee', 'cocoa', 'smoke', 'caramel'],
    'dulzor': ['seco', 'semi-seco', 'dulce', 'dry', 'semi-dry', 'sweet'],
    'acidez': ['acidez', 'ácido', 'acidic', 'acidity', 'crisp', 'tangy'],
    'cuerpo': ['ligero', 'medio', 'robusto', 'full-bodied', 'medium-bodied', 'light-bodied'],
    'taninos': ['suaves', 'medios', 'altos', 'astringentes', 'redondeados', 'tannins', 'astringent', 'rounded'],
    'alcohol': ['bajo', 'medio', 'alto', 'low alcohol', 'medium alcohol', 'high alcohol'],
    'finalizacion': ['largo', 'persistente', 'corto', 'prolongado', 'long finish', 'persistent', 'short finish'],
    'umami_y_otros': ['umami', 'sabroso', 'salado', 'savory', 'salty']
}

# Información adicional sobre atributos
attribute_categories = {
    'frutas_rojas': 'Sabores y Aromas',
    'frutas_negras': 'Sabores y Aromas',
    'frutas_cítricas': 'Sabores y Aromas',
    'frutas_tropicales': 'Sabores y Aromas',
    'frutas_hueso': 'Sabores y Aromas',
    'frutas_secas': 'Sabores y Aromas',
    'especias': 'Sabores y Aromas',
    'notas_herbales_frescas': 'Sabores y Aromas',
    'notas_herbales_secas': 'Sabores y Aromas',
    'notas_florales': 'Sabores y Aromas',
    'notas_terrosas': 'Sabores y Aromas',
    'madera_y_otros': 'Sabores y Aromas',
    'dulzor': 'Características Gustativas',
    'acidez': 'Características Gustativas',
    'cuerpo': 'Características Gustativas',
    'taninos': 'Características Gustativas',
    'alcohol': 'Características Gustativas',
    'finalizacion': 'Características Gustativas',
    'umami_y_otros': 'Características Gustativas'
}

# Función de preprocesamiento
def preprocess_text(text):
    # Convertir a minúsculas
    text = str(text).lower()
    # Eliminar puntuación
    text = text.translate(str.maketrans('', '', string.punctuation))
    # Tokenizar
    tokens = word_tokenize(text)
    # Lematizar
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(token) for token in tokens]
    return tokens

# Aplicar la función al DataFrame
df['tokens'] = df['full_text'].apply(preprocess_text)

# Inicializar columnas para cada atributo
for attribute in attribute_dict.keys():
    df[attribute] = 0

# Función para asignar atributos
def assign_attributes(tokens):
    attributes_found = {}
    for attribute, keywords in attribute_dict.items():
        count = sum(tokens.count(keyword) for keyword in keywords)
        attributes_found[attribute] = count
    return pd.Series(attributes_found)

# Aplicar la función al DataFrame
df[list(attribute_dict.keys())] = df['tokens'].apply(assign_attributes)

# Normalizar los atributos
attribute_columns = list(attribute_dict.keys())
scaler = MinMaxScaler()
df[attribute_columns] = scaler.fit_transform(df[attribute_columns])

# Crear un identificador único si no existe la columna 'wine_id'
if 'wine_id' not in df.columns:
    df['wine_id'] = range(1, len(df) + 1)
    print("Columna 'wine_id' creada exitosamente.")

# Integrar la columna 'variedad' desde el archivo de origen
if 'variety' in df.columns:
    df['variedad'] = df['variety']
else:
    df['variedad'] = 'Variedad Desconocida'

# Para las reseñas de Reddit donde la variedad puede no estar presente, inferir la variedad
# basado en los atributos y comparándolos con las reseñas del sommelier
# Separar los datos del sommelier y de Reddit
# Asumimos que en el DataFrame existe una columna que nos permite diferenciar las fuentes, por ejemplo 'source'
if 'source' not in df.columns:
    df['source'] = 'Desconocido'  # O asignar el valor apropiado

# Filtrar los vinos del sommelier y de Reddit
sommelier_df = df[df['source'] == 'sommelier_argentina']
reddit_df = df[df['source'].isin(['reddit_argentina', 'reddit_international'])]

# Crear un DataFrame para mapear atributos a variedades utilizando los datos del sommelier
attribute_means_by_variety = sommelier_df.groupby('variedad')[attribute_columns].mean()

# Función para inferir la variedad basada en los atributos
def infer_variety(row):
    if pd.isna(row['variedad']) or row['variedad'] == 'Variedad Desconocida':
        # Calcular la similitud entre el vino y las variedades conocidas
        similarities = {}
        for variety, attrs in attribute_means_by_variety.iterrows():
            similarity = cosine_similarity([row[attribute_columns]], [attrs.values])[0][0]
            similarities[variety] = similarity
        # Seleccionar la variedad con mayor similitud
        if similarities:
            inferred_variety = max(similarities, key=similarities.get)
            return inferred_variety
        else:
            return 'Variedad Desconocida'
    else:
        return row['variedad']

# Aplicar la función para inferir la variedad en los vinos de Reddit
# Para evitar SettingWithCopyWarning, utilizamos .loc
reddit_df.loc[:, 'variedad'] = reddit_df.apply(infer_variety, axis=1)

# Combinar los DataFrames nuevamente
df = pd.concat([sommelier_df, reddit_df], ignore_index=True)

# **Calcular Sentimiento (`polarity`) usando TextBlob**
def calcular_polaridad(texto):
    """
    Calcula la polaridad de un texto utilizando TextBlob.
    Retorna un valor entre -1 (negativo) y 1 (positivo).
    """
    try:
        blob = TextBlob(texto)
        return blob.sentiment.polarity
    except Exception as e:
        print(f"Error al calcular polaridad con TextBlob: {e}")
        return 0.0

# Calcular `polarity` para todas las entradas
print("Calculando polaridad utilizando TextBlob...")
df['polarity'] = df['full_text'].apply(calcular_polaridad)
print("Cálculo de polaridad completado.")

# Verificar la columna 'polarity'
print("Ejemplo de valores de 'polarity':")
print(df[['wine_id', 'title', 'polarity']].head())

# Verificar y agregar 'sentiment_label' y 'polarity'
if 'sentiment_label' in df.columns:
    df['sentiment_label'] = df['sentiment_label']
else:
    df['sentiment_label'] = df['polarity'].apply(lambda x: 'Positivo' if x > 0 else ('Negativo' if x < 0 else 'Neutral'))
    print("Columna 'sentiment_label' no encontrada. Se ha asignado basado en 'polarity'.")

# **Crear df_profiles incluyendo las nuevas columnas**
# Verificar si 'price' y 'title' existen y están en df.columns
columns_to_include = ['wine_id', 'variedad', 'sentiment_label', 'polarity', 'full_text']
for col in ['price', 'title']:
    if col in df.columns:
        columns_to_include.append(col)
    else:
        print(f"Advertencia: La columna '{col}' no existe en el DataFrame. Se asignará un valor por defecto.")
        df[col] = None  # O asignar un valor por defecto
        columns_to_include.append(col)

columns_to_include += attribute_columns

df_profiles = df[columns_to_include]

# Guardar los perfiles de vino incluyendo 'variedad' y otros campos
output_file = os.path.join(data_dir, 'wine_profiles6.csv')  # Asegúrate de que 'data_dir' está definido correctamente
df_profiles.to_csv(output_file, index=False)
print(f"Perfiles de vino guardados exitosamente en: {output_file}")
