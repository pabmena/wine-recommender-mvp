import pandas as pd

# Rutas a los archivos
reddit_sentiment_file = 'C:/Users/pabme/OneDrive/Escritorio/IA-UBA/IA_Agricultura/wine-recommender-mvp/data/reddit_wine_data_sentiment.csv'
argentina_sentiment_file = 'C:/Users/pabme/OneDrive/Escritorio/IA-UBA/IA_Agricultura/wine-recommender-mvp/data/wine_reviews_argentina_sentiment.csv'

# Cargar los datos procesados
df_reddit = pd.read_csv(reddit_sentiment_file)
df_argentina = pd.read_csv(argentina_sentiment_file)

# Mostrar las primeras filas
print("Datos de Reddit:")
print(df_reddit.head())  # Muestra las primeras 5 filas

print("\nDatos de Argentina:")
print(df_argentina.head())  # Muestra las primeras 5 filas
