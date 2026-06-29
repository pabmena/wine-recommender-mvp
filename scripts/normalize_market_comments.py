import os
import pandas as pd
import string
from textblob import TextBlob

def preprocess_text(text):
    if pd.isna(text):
        return ""
    # Convertir a minúsculas y eliminar puntuación
    text = str(text).lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    return text

def calculate_polarity(text):
    if not text:
        return 0.0
    try:
        # Nota: Usamos TextBlob. Dado que es texto en español,
        # para un MVP calculamos la polaridad léxica. Traducir al inglés 
        # o usar un analizador básico de palabras positivas/negativas locales
        # es lo más estable sin instalar paquetes extra como pysentimiento.
        # Crearemos un analizador de polaridad híbrido básico para español:
        pos_words = ['bueno', 'excelente', 'rico', 'espectacular', 'ideal', 'perfecto', 'recomiendo', 'lindo', 'agradable', 'cumplidor', 'ganga', 'mejor']
        neg_words = ['malo', 'feo', 'horrible', 'caro', 'ácido', 'empalagoso', 'malo', 'falla', 'defecto', 'decepcionado']
        
        words = text.split()
        pos_count = sum(1 for w in words if w in pos_words)
        neg_count = sum(1 for w in words if w in neg_words)
        
        # Combinar con TextBlob como fallback
        blob_pol = TextBlob(text).sentiment.polarity
        
        # Calcular balance
        balance = pos_count - neg_count
        if balance > 0:
            local_pol = 0.2 + (balance * 0.1)
        elif balance < 0:
            local_pol = -0.2 + (balance * 0.1)
        else:
            local_pol = 0.0
            
        # Ponderar: 70% local, 30% TextBlob
        final_pol = 0.7 * local_pol + 0.3 * blob_pol
        return max(-1.0, min(1.0, final_pol))
    except Exception:
        return 0.0

def normalize_comments():
    print("Iniciando normalización de comentarios de mercado...")
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    raw_dir = os.path.join(current_dir, '../data/raw')
    processed_dir = os.path.join(current_dir, '../data/processed')
    os.makedirs(processed_dir, exist_ok=True)
    
    # Rutas
    reddit_path = os.path.join(raw_dir, 'reddit_argentina_2026.csv')
    youtube_path = os.path.join(raw_dir, 'youtube_comments_wine_argentina_2026.csv')
    ml_path = os.path.join(raw_dir, 'mercadolibre_reviews_wine_2026.csv')
    
    normalized_list = []
    
    # 1. Procesar Reddit
    if os.path.exists(reddit_path):
        df_red = pd.read_csv(reddit_path)
        for _, row in df_red.iterrows():
            text = f"{row['title']} {row['content']}"
            pol = calculate_polarity(text)
            normalized_list.append({
                'comment_id': row['comment_id'],
                'source': 'reddit',
                'source_platform': 'reddit_argentina',
                'text': text,
                'clean_text': preprocess_text(text),
                'wine_title_detected': row['title'],
                'polarity': pol,
                'sentiment_label': 'Positivo' if pol > 0.1 else ('Negativo' if pol < -0.1 else 'Neutral'),
                'created_at': row['created_utc'],
                'source_method': 'PRAW API',
                'is_fallback': False,
                'is_live_collected': True,
                'collected_at': '2026-06-29'
            })
            
    # 2. Procesar YouTube
    if os.path.exists(youtube_path):
        df_yt = pd.read_csv(youtube_path)
        for _, row in df_yt.iterrows():
            text = row['comment_text']
            pol = calculate_polarity(text)
            normalized_list.append({
                'comment_id': row['comment_id'],
                'source': 'youtube',
                'source_platform': 'youtube_comments',
                'text': text,
                'clean_text': preprocess_text(text),
                'wine_title_detected': row['video_title'],
                'polarity': pol,
                'sentiment_label': 'Positivo' if pol > 0.1 else ('Negativo' if pol < -0.1 else 'Neutral'),
                'created_at': row['created_at'],
                'source_method': 'YT API Fallback',
                'is_fallback': True,
                'is_live_collected': False,
                'collected_at': '2026-06-29'
            })
            
    # 3. Procesar Mercado Libre
    if os.path.exists(ml_path):
        df_ml = pd.read_csv(ml_path)
        for _, row in df_ml.iterrows():
            text = row['review_text']
            pol = calculate_polarity(text)
            normalized_list.append({
                'comment_id': row['review_id'],
                'source': 'mercadolibre',
                'source_platform': 'mercadolibre_reviews',
                'text': text,
                'clean_text': preprocess_text(text),
                'wine_title_detected': row['product_title'],
                'polarity': pol,
                'sentiment_label': 'Positivo' if pol > 0.1 else ('Negativo' if pol < -0.1 else 'Neutral'),
                'created_at': row['created_date'],
                'source_method': 'MLA API Fallback',
                'is_fallback': True,
                'is_live_collected': False,
                'collected_at': '2026-06-29'
            })
            
    if normalized_list:
        df_out = pd.DataFrame(normalized_list)
        output_file = os.path.join(processed_dir, 'wine_market_comments_argentina_v2.csv')
        df_out.to_csv(output_file, index=False)
        print(f"Dataset de comentarios normalizado guardado en: {output_file}")
    else:
        print("Error: No se encontraron archivos raw para normalizar.")

if __name__ == '__main__':
    normalize_comments()
