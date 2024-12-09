import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.feature_extraction.text import CountVectorizer

# Configuración de estilo
sns.set(style="whitegrid")

# Rutas de los archivos
current_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(current_dir, '..', 'data')

reddit_international_file = os.path.join(data_dir, 'reddit_wine_data_sentiment.csv')
reddit_argentina_file = os.path.join(data_dir, 'reddit_argentina_wine_data_sentiment.csv')
sommelier_argentina_file = os.path.join(data_dir, 'wine_reviews_argentina_sentiment.csv')

# Cargar los datasets
df_reddit_international = pd.read_csv(reddit_international_file)
df_reddit_argentina = pd.read_csv(reddit_argentina_file)
df_sommelier_argentina = pd.read_csv(sommelier_argentina_file)

# Agregar columna de fuente
df_reddit_international['source'] = 'reddit_international'
df_reddit_argentina['source'] = 'reddit_argentina'
df_sommelier_argentina['source'] = 'sommelier_argentina'

# Unir los datasets
df_combined = pd.concat([df_reddit_international, df_reddit_argentina, df_sommelier_argentina], ignore_index=True)

# Guardar el DataFrame combinado
combined_file = os.path.join(data_dir, 'combined_wine_data_sentiment.csv')
df_combined.to_csv(combined_file, index=False)

print(f"Datasets combinados guardados en: {combined_file}")

# Cargar el dataset combinado
df_combined = pd.read_csv(combined_file)

# Mostrar las primeras filas
print(df_combined.head())

# Resumen de información
print(df_combined.info())

# Descripción estadística
print(df_combined.describe())

# Distribución de sentimientos por fuente
plt.figure(figsize=(12, 8))
sns.countplot(data=df_combined, x='source', hue='sentiment_label')
plt.title('Distribución de Sentimientos por Fuente')
plt.xlabel('Fuente')
plt.ylabel('Cantidad de Reseñas')
plt.legend(title='Sentimiento')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Distribución general de sentimientos
plt.figure(figsize=(8, 6))
sns.countplot(data=df_combined, x='sentiment_label', palette='viridis')
plt.title('Distribución de Sentimientos Globales')
plt.xlabel('Sentimiento')
plt.ylabel('Cantidad de Reseñas')
plt.tight_layout()
plt.show()

# Distribución de polaridad
plt.figure(figsize=(10, 6))
sns.histplot(df_combined['polarity'], bins=30, kde=True, color='skyblue')
plt.title('Distribución de Polaridad de Sentimientos')
plt.xlabel('Polaridad')
plt.ylabel('Frecuencia')
plt.tight_layout()
plt.show()

# Comparación de polaridad por fuente
plt.figure(figsize=(12, 8))
sns.boxplot(data=df_combined, x='source', y='polarity', palette='Set3')
plt.title('Comparación de Polaridad por Fuente')
plt.xlabel('Fuente')
plt.ylabel('Polaridad')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Filtrar reseñas positivas y negativas
df_positive = df_combined[df_combined['sentiment_label'] == 'Positivo']
df_negative = df_combined[df_combined['sentiment_label'] == 'Negativo']

# Función para plot de top palabras
def plot_top_words(texts, title, num=20, language='english'):
    if language == 'spanish':
        stop_words = 'spanish'
    else:
        stop_words = 'english'
    
    vectorizer = CountVectorizer(max_features=100, stop_words=stop_words)
    X = vectorizer.fit_transform(texts)
    sum_words = X.sum(axis=0)
    words_freq = [(word, sum_words[0, idx]) for word, idx in vectorizer.vocabulary_.items()]
    words_freq = sorted(words_freq, key=lambda x: x[1], reverse=True)[:num]
    words, counts = zip(*words_freq)
    
    plt.figure(figsize=(12, 6))
    sns.barplot(x=list(counts), y=list(words), palette='magma')
    plt.title(title)
    plt.xlabel('Frecuencia')
    plt.ylabel('Palabra')
    plt.tight_layout()
    plt.show()

# Para reseñas positivas
plot_top_words(df_positive['full_text'], 'Top 20 Palabras en Reseñas Positivas', language='spanish')

# Para reseñas negativas
plot_top_words(df_negative['full_text'], 'Top 20 Palabras en Reseñas Negativas', language='spanish')

# Guardar el DataFrame combinado
df_combined.to_csv(combined_file, index=False)
print(f"DataFrame combinado y con sentimiento guardado en: {combined_file}")
