import os
import pandas as pd
import numpy as np

# Columnas de los 19 atributos
ATTRIBUTE_COLUMNS = [
    'frutas_rojas', 'frutas_negras', 'frutas_cítricas', 'frutas_tropicales', 
    'frutas_hueso', 'frutas_secas', 'especias', 'notas_herbales_frescas', 
    'notas_herbales_secas', 'notas_florales', 'notas_terrosas', 'madera_y_otros', 
    'dulzor', 'acidez', 'cuerpo', 'taninos', 'alcohol', 'finalizacion', 'umami_y_otros'
]

def associate_comments(wine_title, comments_df):
    """
    Busca comentarios en redes que mencionen de manera difusa palabras clave
    del título del vino para asociar opinión de mercado.
    """
    wine_title_lower = str(wine_title).lower()
    
    # Extraer marcas comunes para simplificar la asociación
    brands = ['rutini', 'alamos', 'don david', 'new age', 'zaha', 'catena', 'portillo', 'callia', 'luigi bosca', 'tintonegro']
    detected_brand = None
    for brand in brands:
        if brand in wine_title_lower:
            detected_brand = brand
            break
            
    if not detected_brand:
        return pd.DataFrame()
        
    # Filtrar comentarios de la plataforma que contengan la marca en el texto o en el título
    associated = comments_df[
        comments_df['clean_text'].str.contains(detected_brand) | 
        comments_df['wine_title_detected'].str.lower().str.contains(detected_brand)
    ]
    return associated

def build_profiles_v2():
    print("Iniciando construcción de Perfiles de Vino Argentina V2...")
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, '../data')
    processed_dir = os.path.join(current_dir, '../data/processed')
    
    # 1. Cargar perfiles base
    profiles_v1_path = os.path.join(data_dir, 'wine_profiles6.csv')
    if not os.path.exists(profiles_v1_path):
        print(f"Error: No se encontró el dataset base {profiles_v1_path}")
        return
        
    df_profiles = pd.read_csv(profiles_v1_path)
    if df_profiles.columns.duplicated().any():
        df_profiles = df_profiles.loc[:, ~df_profiles.columns.duplicated()]
        
    # Reducir variedad Unknown deduciéndolas desde el título
    def deduce_variety_from_title(row):
        var_str = str(row.get('variedad', 'Unknown'))
        title_lower = str(row.get('title', '')).lower()
        if pd.isna(row.get('variedad')) or var_str.strip().lower() in ['unknown', 'unknown variety', 'variedad desconocida']:
            patterns = {
                'cabernet sauvignon': 'Cabernet Sauvignon',
                'cabernet franc': 'Cabernet Franc',
                'sauvignon blanc': 'Sauvignon Blanc',
                'pinot noir': 'Pinot Noir',
                'red blend': 'Red Blend',
                'bordeaux': 'Bordeaux-style Red Blend',
                'malbec': 'Malbec',
                'chardonnay': 'Chardonnay',
                'torrontes': 'Torrontés',
                'torrontés': 'Torrontés',
                'bonarda': 'Bonarda',
                'syrah': 'Syrah',
                'shiraz': 'Syrah',
                'merlot': 'Merlot',
                'semillon': 'Semillon',
                'semillón': 'Semillon',
                'tempranillo': 'Tempranillo',
                'viognier': 'Viognier',
                'blend': 'Red Blend'
            }
            for pattern, canonical in patterns.items():
                if pattern in title_lower:
                    return canonical
        return row.get('variedad', 'Unknown')
        
    initial_unknowns = (df_profiles['variedad'].astype(str).str.strip().str.lower() == 'unknown').sum()
    df_profiles['variedad'] = df_profiles.apply(deduce_variety_from_title, axis=1)
    final_unknowns = (df_profiles['variedad'].astype(str).str.strip().str.lower() == 'unknown').sum()
    print(f"Reducción de variedades Unknown: de {initial_unknowns} a {final_unknowns} (Deducidos: {initial_unknowns - final_unknowns} vinos).")

    # 2. Cargar comentarios unificados
    comments_path = os.path.join(processed_dir, 'wine_market_comments_argentina_v2.csv')
    if os.path.exists(comments_path):
        df_comments = pd.read_csv(comments_path)
        print(f"Cargados {len(df_comments)} comentarios de opinión de mercado.")
    else:
        df_comments = pd.DataFrame()
        print("Advertencia: No se encontró el archivo de comentarios de mercado. Se usará fallback heurístico.")

    # 3. Calcular scores para cada vino
    asado_scores = []
    precio_calidad_scores = []
    argentine_palate_scores = []
    market_polarities = []
    
    for _, row in df_profiles.iterrows():
        # Asignación de scores base por atributos del vino
        cuerpo = row.get('cuerpo', 0.0)
        taninos = row.get('taninos', 0.0)
        madera = row.get('madera_y_otros', 0.0)
        price = row.get('price', 15.0)
        
        # 1. Asado score base
        asado_score = 0.4 * cuerpo + 0.4 * taninos + 0.2 * madera
        
        # Buscar comentarios asociados para refinar scores
        associated_comments = pd.DataFrame()
        if not df_comments.empty:
            associated_comments = associate_comments(row['title'], df_comments)
            
        if not associated_comments.empty:
            # Si hay comentarios reales, tomamos la polaridad promedio local
            local_sentiment_polarity = associated_comments['polarity'].mean()
            # Ajustar asado score si en comentarios se menciona asado/parrilla/brasa/leña
            text_combined = " ".join(associated_comments['clean_text'].tolist())
            if any(w in text_combined for w in ['asado', 'parrilla', 'leña', 'vacio', 'entraña', 'costillar', 'carne']):
                asado_score = min(1.0, asado_score + 0.25)
        else:
            # Fallback a la polaridad de la reseña original del sommelier
            local_sentiment_polarity = row.get('polarity', 0.0)
            
        market_polarities.append(local_sentiment_polarity)
        
        # 2. Precio Calidad Score
        sentiment_score = (local_sentiment_polarity + 1.0) / 2.0
        if price < 15.0:
            precio_calidad_score = sentiment_score * 1.0
        elif price < 30.0:
            precio_calidad_score = sentiment_score * 0.85
        elif price < 60.0:
            precio_calidad_score = sentiment_score * 0.70
        else:
            precio_calidad_score = sentiment_score * 0.50
            
        # 3. Origen y Variedad Argentina
        source = str(row.get('source', '')).lower()
        variedad = str(row.get('variedad', '')).lower()
        típicas_argentinas = ['malbec', 'bonarda', 'torrontes', 'torrontés', 'cabernet franc', 'criolla']
        es_local = 'argentina' in source or any(t in variedad for t in típicas_argentinas)
        argentina_source_weight = 1.0 if es_local else 0.5
        
        # 4. Recency Score (Añadas más recientes > 2010 tienen 1.0)
        title = str(row.get('title', ''))
        recency_score = 0.9
        for year in range(2010, 2027):
            if str(year) in title:
                recency_score = 1.0
                break
                
        # 5. Argentine Palate Score consolidado
        local_sentiment_score = sentiment_score
        arg_palate_score = (
            0.30 * local_sentiment_score +
            0.25 * asado_score +
            0.20 * precio_calidad_score +
            0.15 * argentina_source_weight +
            0.10 * recency_score
        )
        
        asado_scores.append(asado_score)
        precio_calidad_scores.append(precio_calidad_score)
        argentine_palate_scores.append(arg_palate_score)

    # Añadir nuevas columnas
    df_profiles['asado_score'] = asado_scores
    df_profiles['precio_calidad_score'] = precio_calidad_scores
    df_profiles['argentine_palate_score'] = argentine_palate_scores
    df_profiles['market_polarity'] = market_polarities
    
    # Guardar archivo procesado consolidado V2
    output_file = os.path.join(processed_dir, 'wine_profiles_argentina_v2.csv')
    df_profiles.to_csv(output_file, index=False)
    print(f"Perfiles unificados V2 guardados exitosamente en: {output_file}")

if __name__ == '__main__':
    build_profiles_v2()
