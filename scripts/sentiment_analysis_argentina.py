import pandas as pd
import re
from textblob import TextBlob
from langdetect import detect
import os

def limpiar_texto(texto):
    if pd.isnull(texto):
        return ''
    texto = texto.lower()
    texto = re.sub(r'http\S+', '', texto)  # Eliminar URLs
    texto = re.sub(r'@\w+', '', texto)     # Eliminar menciones
    texto = re.sub(r'#\w+', '', texto)     # Eliminar hashtags
    texto = re.sub(r'[^\w\s]', '', texto)  # Eliminar caracteres especiales
    texto = re.sub(r'\d+', '', texto)      # Eliminar números
    texto = re.sub(r'\s+', ' ', texto).strip()  # Eliminar espacios extra
    return texto

def obtener_sentimiento(texto):
    try:
        idioma = detect(texto)
    except:
        # Si no se puede detectar el idioma, asumimos neutral
        return 'Neutral', 0

    # Usar TextBlob para el análisis
    analysis = TextBlob(texto)
    polarity = analysis.sentiment.polarity

    if polarity > 0:
        return 'Positivo', polarity
    elif polarity < 0:
        return 'Negativo', polarity
    else:
        return 'Neutral', polarity

# Ruta al archivo de datos de Reddit Argentina
current_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(current_dir, '..', 'data')
os.makedirs(output_dir, exist_ok=True)
reddit_argentina_data_file = os.path.join(output_dir, 'reddit_argentina_wine_data.csv')

if os.path.exists(reddit_argentina_data_file):
    df_reddit_argentina = pd.read_csv(reddit_argentina_data_file)

    # Limpiar el contenido y el título
    df_reddit_argentina['clean_content'] = df_reddit_argentina['content'].apply(limpiar_texto)
    df_reddit_argentina['clean_title'] = df_reddit_argentina['title'].apply(limpiar_texto)

    # Concatenar título y contenido
    df_reddit_argentina['full_text'] = df_reddit_argentina['clean_title'] + ' ' + df_reddit_argentina['clean_content']

    # Aplicar el análisis de sentimiento con detección de idioma
    df_reddit_argentina[['sentiment_label', 'polarity']] = df_reddit_argentina['full_text'].apply(
        lambda x: pd.Series(obtener_sentimiento(x))
    )

    # Guardar los resultados
    output_file_reddit_argentina = os.path.join(output_dir, 'reddit_argentina_wine_data_sentiment.csv')
    df_reddit_argentina.to_csv(output_file_reddit_argentina, index=False)

    print("\nAnálisis de sentimiento completado para datos de Reddit Argentina.")
    print(f"Resultados guardados en '{output_file_reddit_argentina}'")
else:
    print(f"El archivo '{reddit_argentina_data_file}' no existe. Ejecuta el script de extracción de datos de Reddit Argentina primero.")
