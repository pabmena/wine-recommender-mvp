import pandas as pd
import re
from textblob import TextBlob
import os

def limpiar_texto(texto):
    if pd.isnull(texto):
        return ''
    texto = texto.lower()
    texto = re.sub(r'http\S+', '', texto)  # Remove URLs
    texto = re.sub(r'@\w+', '', texto)     # Remove mentions
    texto = re.sub(r'#\w+', '', texto)     # Remove hashtags
    texto = re.sub(r'[^\w\s]', '', texto)  # Remove punctuation
    texto = re.sub(r'\d+', '', texto)      # Remove numbers
    texto = re.sub(r'\s+', ' ', texto).strip()  # Remove extra spaces
    return texto

def obtener_sentimiento(texto):
    analysis = TextBlob(texto)
    polarity = analysis.sentiment.polarity
    if polarity > 0:
        return 'Positivo', polarity
    elif polarity < 0:
        return 'Negativo', polarity
    else:
        return 'Neutral', polarity

# Get the current directory of the script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Create the 'data' folder if it doesn't exist
output_dir = os.path.join(current_dir, '..', 'data')
os.makedirs(output_dir, exist_ok=True)

# ------------------------------
# Sentiment Analysis for Reddit Data
# ------------------------------

# Path to the Reddit data file
reddit_data_file = os.path.join(current_dir, '..', 'data', 'reddit_wine_data.csv')

# Check if the Reddit data file exists
if os.path.exists(reddit_data_file):
    # Load the Reddit data
    df_reddit = pd.read_csv(reddit_data_file)

    # Clean the content and title
    df_reddit['clean_content'] = df_reddit['content'].apply(limpiar_texto)
    df_reddit['clean_title'] = df_reddit['title'].apply(limpiar_texto)

    # Apply sentiment analysis
    df_reddit[['sentiment_label', 'polarity']] = df_reddit['clean_content'].apply(
        lambda x: pd.Series(obtener_sentimiento(x))
    )

    # Save the results
    output_file_reddit = os.path.join(output_dir, 'reddit_wine_data_sentiment.csv')
    df_reddit.to_csv(output_file_reddit, index=False)

    print("Análisis de sentimiento completado para datos de Reddit.")
    print(f"Resultados guardados en '{output_file_reddit}'")
else:
    print(f"El archivo '{reddit_data_file}' no existe. Asegúrate de ejecutar el script de extracción de datos de Reddit primero.")

# ------------------------------
# Sentiment Analysis for Argentina Wine Reviews
# ------------------------------

# Path to the Argentina wine reviews data file
argentina_data_file = os.path.join(current_dir, '..', 'data', 'wine_reviews_argentina.csv')

# Check if the Argentina data file exists
if os.path.exists(argentina_data_file):
    # Load the Argentina wine reviews data
    df_argentina = pd.read_csv(argentina_data_file)

    # Assuming the reviews are in a column named 'description'
    if 'description' in df_argentina.columns:
        # Clean the descriptions
        df_argentina['clean_description'] = df_argentina['description'].apply(limpiar_texto)

        # Apply sentiment analysis
        df_argentina[['sentiment_label', 'polarity']] = df_argentina['clean_description'].apply(
            lambda x: pd.Series(obtener_sentimiento(x))
        )

        # Save the results
        output_file_argentina = os.path.join(output_dir, 'wine_reviews_argentina_sentiment.csv')
        df_argentina.to_csv(output_file_argentina, index=False)

        print("\nAnálisis de sentimiento completado para reseñas de vinos de Argentina.")
        print(f"Resultados guardados en '{output_file_argentina}'")
    else:
        print("La columna 'description' no existe en el archivo de datos de Argentina.")
else:
    print(f"El archivo '{argentina_data_file}' no existe. Asegúrate de que el archivo esté en la carpeta 'data'.")

