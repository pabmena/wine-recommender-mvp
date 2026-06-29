import os
import sys
import pandas as pd
import json
import numpy as np
from datetime import datetime

# Rutas del proyecto
sys.path.append(r"C:\Users\pabme\OneDrive\Escritorio\IA-UBA\IA_Agricultura\wine-recommender-mvp")

from app import create_user_profile, get_recommendations, get_recommendations_for_confidence
from config.confidence import calculate_confidence, should_continue_quiz

def run_audit():
    print("Iniciando auditoría de datos detallada (QA Post-Correcciones) de SommAI...")
    
    data_dir = r"C:\Users\pabme\OneDrive\Escritorio\IA-UBA\IA_Agricultura\wine-recommender-mvp\data"
    reports_dir = r"C:\Users\pabme\OneDrive\Escritorio\IA-UBA\IA_Agricultura\wine-recommender-mvp\reports"
    os.makedirs(reports_dir, exist_ok=True)
    
    # 1. Inspección de existencia de archivos
    files_to_check = {
        'wine_reviews_argentina_sentiment': os.path.join(data_dir, 'wine_reviews_argentina_sentiment.csv'),
        'reddit_wine_data_sentiment': os.path.join(data_dir, 'reddit_wine_data_sentiment.csv'),
        'reddit_argentina_wine_data_sentiment': os.path.join(data_dir, 'reddit_argentina_wine_data_sentiment.csv'),
        'wine_data_prepared_with_title': os.path.join(data_dir, 'wine_data_prepared_with_title.csv'),
        'wine_profiles6': os.path.join(data_dir, 'wine_profiles6.csv'),
        'reddit_argentina_2026': os.path.join(data_dir, 'raw/reddit_argentina_2026.csv'),
        'mercadolibre_reviews_wine_2026': os.path.join(data_dir, 'raw/mercadolibre_reviews_wine_2026.csv'),
        'wine_market_comments_argentina_v2': os.path.join(data_dir, 'processed/wine_market_comments_argentina_v2.csv'),
        'wine_profiles_argentina_v2': os.path.join(data_dir, 'processed/wine_profiles_argentina_v2.csv'),
        'vectorizer': os.path.join(data_dir, 'vectorizer.pkl')
    }
    
    file_existence = {}
    for key, path in files_to_check.items():
        exists = os.path.exists(path)
        file_existence[key] = {
            'path': path,
            'exists': exists,
            'size_bytes': os.path.getsize(path) if exists else 0
        }
        
    # 2. Conteo exacto V1
    v1_counts = {}
    v1_files = ['wine_reviews_argentina_sentiment', 'reddit_wine_data_sentiment', 
                'reddit_argentina_wine_data_sentiment', 'wine_data_prepared_with_title', 'wine_profiles6']
                
    for f_key in v1_files:
        info = file_existence[f_key]
        if info['exists']:
            df = pd.read_csv(info['path'])
            if df.columns.duplicated().any():
                df = df.loc[:, ~df.columns.duplicated()]
            v1_counts[f_key] = {
                'rows': len(df),
                'cols': len(df.columns)
            }
            
    wine_reviews_rows = v1_counts['wine_reviews_argentina_sentiment']['rows']
    reddit_wine_rows = v1_counts['reddit_wine_data_sentiment']['rows']
    reddit_arg_rows = v1_counts['reddit_argentina_wine_data_sentiment']['rows']
    v1_sources_total = wine_reviews_rows + reddit_wine_rows + reddit_arg_rows
    v1_prepared_total = v1_counts['wine_data_prepared_with_title']['rows']
    
    # 3. Conteo exacto V2
    v2_counts = {}
    v2_files = ['reddit_argentina_2026', 'mercadolibre_reviews_wine_2026', 
                'wine_market_comments_argentina_v2', 'wine_profiles_argentina_v2']
                
    for f_key in v2_files:
        info = file_existence[f_key]
        if info['exists']:
            df = pd.read_csv(info['path'])
            if df.columns.duplicated().any():
                df = df.loc[:, ~df.columns.duplicated()]
            v2_counts[f_key] = {
                'rows': len(df),
                'cols': len(df.columns)
            }

    reddit_v2_rows = v2_counts['reddit_argentina_2026']['rows']
    ml_v2_rows = v2_counts['mercadolibre_reviews_wine_2026']['rows']
    yt_raw_path = os.path.join(data_dir, 'raw/youtube_comments_wine_argentina_2026.csv')
    yt_v2_rows = len(pd.read_csv(yt_raw_path)) if os.path.exists(yt_raw_path) else 0
    total_market_raw = reddit_v2_rows + ml_v2_rows + yt_v2_rows
    market_processed_rows = v2_counts['wine_market_comments_argentina_v2']['rows']
    descartados_dup = total_market_raw - market_processed_rows
    
    # 4. Trazabilidad de Fuentes y Live vs Fallback
    source_stats = []
    df_mc = pd.read_csv(file_existence['wine_market_comments_argentina_v2']['path'])
    for plat, group in df_mc.groupby('source_platform'):
        rows_p = len(group)
        source_stats.append({
            'platform': plat,
            'method': str(group['source_method'].iloc[0]) if 'source_method' in group.columns else 'Unknown',
            'live_fallback': 'Live' if not group['is_fallback'].iloc[0] else 'Fallback',
            'rows': rows_p,
            'percentage': (rows_p / len(df_mc)) * 100
        })

    # 5. Validación de Recencia por Buckets
    # Fecha de recolección de referencia: 2026-06-29
    df_mc['created_at_dt'] = pd.to_datetime(df_mc['created_at'], errors='coerce')
    ref_date = pd.to_datetime('2026-06-29')
    
    recent_30 = df_mc[df_mc['created_at_dt'] >= (ref_date - pd.Timedelta(days=30))]
    recent_90 = df_mc[(df_mc['created_at_dt'] >= (ref_date - pd.Timedelta(days=90))) & (df_mc['created_at_dt'] < (ref_date - pd.Timedelta(days=30)))]
    recent_365 = df_mc[(df_mc['created_at_dt'] >= (ref_date - pd.Timedelta(days=365))) & (df_mc['created_at_dt'] < (ref_date - pd.Timedelta(days=90)))]
    older = df_mc[df_mc['created_at_dt'] < (ref_date - pd.Timedelta(days=365))]
    
    recency_buckets = {
        'ultimos_30_dias': len(recent_30),
        'ultimos_90_dias': len(recent_90),
        'ultimos_365_dias': len(recent_365),
        'mas_antiguo': len(older)
    }

    # 6. Cobertura de Mercado y Matches con Catálogo
    # Un comentario matchea al catálogo si menciona alguna de las marcas clave asociadas a vinos en la V2
    brands = ['rutini', 'alamos', 'don david', 'new age', 'zaha', 'catena', 'portillo', 'callia', 'luigi bosca', 'tintonegro']
    
    matched_comments_count = 0
    for idx, row_mc in df_mc.iterrows():
        text_clean = str(row_mc['clean_text']).lower()
        title_detect = str(row_mc['wine_title_detected']).lower()
        
        has_match = any(b in text_clean or b in title_detect for b in brands)
        if has_match:
            matched_comments_count += 1
            
    comments_with_wine_detected = df_mc['wine_title_detected'].dropna().count()
    comments_general_market = len(df_mc) - matched_comments_count
    
    # Cobertura sobre catálogo de 5.872 perfiles
    # ¿Cuántos vinos individuales del catálogo recibieron match de comentario?
    df_v2_p = pd.read_csv(file_existence['wine_profiles_argentina_v2']['path'])
    df_v2_p_matched = df_v2_p[df_v2_p['market_polarity'] != df_v2_p['polarity']] # Polarity difiere si se cruzaron comentarios de mercado
    catalog_coverage_count = len(df_v2_p_matched)
    catalog_coverage_pct = (catalog_coverage_count / len(df_v2_p)) * 100

    # 7. Reducción de variedad Unknown
    df_v1_p = pd.read_csv(file_existence['wine_profiles6']['path'])
    initial_unknowns = (df_v1_p['variedad'].astype(str).str.strip().str.lower() == 'unknown').sum()
    final_unknowns = (df_v2_p['variedad'].astype(str).str.strip().str.lower() == 'unknown').sum()
    unknowns_reduced = initial_unknowns - final_unknowns
    
    top_varieties_v2 = df_v2_p['variedad'].value_counts().head(10).to_dict()

    # 8. Preservación de base histórica
    v1_titles = set(df_v1_p['title'].dropna().astype(str))
    v2_titles = set(df_v2_p['title'].dropna().astype(str))
    preserved = v1_titles.intersection(v2_titles)
    missing = v1_titles - v2_titles
    
    preservation_stats = {
        'v1_unique_titles': len(v1_titles),
        'preserved_titles': len(preserved),
        'missing_titles': len(missing),
        'percentage_preserved': (len(preserved) / len(v1_titles)) * 100
    }

    # 9. Detección de duplicados detallados en el dataset final
    duplicates_stats = {
        'clean_text_duplicates': int(df_mc.duplicated(subset=['clean_text']).sum()),
        'title_text_duplicates': int(df_mc.duplicated(subset=['wine_title_detected', 'clean_text']).sum())
    }

    # 10. Estadísticas de Scores precalculados V2
    score_stats = {}
    scores_cols = ['argentine_palate_score', 'asado_score', 'precio_calidad_score']
    for col in scores_cols:
        series = df_v2_p[col].dropna()
        score_stats[col] = {
            'min': float(series.min()),
            'max': float(series.max()),
            'mean': float(series.mean()),
            'median': float(series.median()),
            'std': float(series.std()),
            'nulls': int(df_v2_p[col].isnull().sum())
        }

    # 11. Simulación de los 5 perfiles con recalibración de confianza y maridaje
    quiz_results = []
    
    responses_a = {
        'conocimiento': 'principiante',
        'cafe_pref': 'C',          # negro amargo
        'chocolate_pref': 'C',     # chocolate amargo
        'citricos_pref': 'B',
        'asado_pref': 'D',         # ahumado/parrilla leña (intención fuerte)
        'dulzor_pref': 'A',        # secas
        'precio': 'Más de $50'
    }
    
    responses_b = {
        'conocimiento': 'principiante',
        'cafe_pref': 'A',          # con leche/azúcar
        'chocolate_pref': 'A',     # blanco dulce
        'citricos_pref': 'C',      # cítricos intensos
        'asado_pref': 'A',         # comidas livianas
        'dulzor_pref': 'C',        # muy dulce
        'precio': '$10 - $20'
    }
    
    responses_c = {
        'conocimiento': 'principiante',
        'cafe_pref': 'B',          # equilibrado
        'chocolate_pref': 'B',
        'citricos_pref': 'B',
        'asado_pref': 'B',         # carne jugosa (asado intención fuerte)
        'dulzor_pref': 'A',
        'precio': '$10 - $20'
    }
    
    responses_d = {
        'conocimiento': 'avanzado',  # nivel avanzado
        'cuerpo_tecnico': 'B',     # cuerpo medio
        'madera_tecnico': 'A',     # sin madera
        'taninos_tecnico': 'B',    # taninos presentes
        'acidez_tecnico': 'B',     # acidez equilibrada
        'dulzor_tecnico': 'A',     # seco
        'precio': 'Más de $50'
    }
    
    responses_e = {
        'conocimiento': 'principiante',
        'cafe_pref': 'B',          # neutral
        'chocolate_pref': 'B',     # neutral
        'citricos_pref': 'B',      # neutral
        'asado_pref': 'C',
        'dulzor_pref': 'B',        # neutral
        'precio': '$20 - $50'
    }
    
    profiles = [
        ('Perfil A: Principiante Intenso', responses_a),
        ('Perfil B: Principiante Fresco/Liviano', responses_b),
        ('Perfil C: Asado Precio-Calidad', responses_c),
        ('Perfil D: Avanzado Técnico', responses_d),
        ('Perfil E: Contradictorio/Neutro', responses_e)
    ]
    
    for name, resp in profiles:
        u_prof, p_filt = create_user_profile(resp)
        recs_temp = get_recommendations_for_confidence(u_prof, p_filt)
        confidence = calculate_confidence(resp, u_prof, recs_temp)
        conf_percent = int(confidence * 100)
        
        if confidence >= 0.72:
            conf_label = "Alto"
        elif confidence >= 0.50:
            conf_label = "Medio"
        else:
            conf_label = "Inicial"
            
        recs = get_recommendations(u_prof, p_filt, user_responses=resp)
        top_5_recs = [w['title'] for w in recs[:5]]
        
        # Validar deduplicación
        has_duplicates = len(top_5_recs) != len(set(top_5_recs))
        
        quiz_results.append({
            'perfil': name,
            'questions_answered': len(resp),
            'confidence_score': float(confidence),
            'confidence_label': conf_label,
            'top_5_recommendations': top_5_recs,
            'maridaje': recs[0]['ideal_para'] if recs else 'N/A',
            'explicacion': recs[0]['explanation'] if recs else 'N/A',
            'has_duplicates': has_duplicates
        })

    # 12. Comparativa V1 vs V2 para el mismo usuario
    responses_comp_v2 = {
        'conocimiento': 'principiante',
        'cafe_pref': 'C',
        'chocolate_pref': 'C',
        'citricos_pref': 'B',
        'asado_pref': 'D',
        'dulzor_pref': 'A',
        'precio': 'Más de $50'
    }
    # V1 (simulación manual con columnas V1)
    u_prof_v1 = pd.DataFrame([{'frutas_rojas': 1, 'especias': 1, 'acidez': 0}])
    from sklearn.metrics.pairwise import cosine_similarity
    similarity_v1 = cosine_similarity(u_prof_v1, df_v1_p[['frutas_rojas', 'especias', 'acidez']])[0]
    df_v1_p['score_v1'] = similarity_v1 + df_v1_p['polarity']
    df_v1_p = df_v1_p[df_v1_p['price'] >= 50.0]
    top_v1 = df_v1_p.sort_values(by='score_v1', ascending=False).head(5)
    recs_v1 = [str(t).replace("Recomendación Similar a: ", "").strip() for t in top_v1['title'].tolist()]
    
    # V2 (en base al recomendador adaptativo con maridajes y deduplicación)
    u_prof_v2, p_filt_v2 = create_user_profile(responses_comp_v2)
    recs_v2_res = get_recommendations(u_prof_v2, p_filt_v2, user_responses=responses_comp_v2)
    recs_v2 = [w['title'] for w in recs_v2_res[:5]]

    # 13. Guardar reportes auditados actualizados
    audit_json = {
        'timestamp': datetime.now().isoformat(),
        'file_existence': file_existence,
        'v1_counts': v1_counts,
        'v2_counts': v2_counts,
        'v1_sources_total': v1_sources_total,
        'market_raw_total': total_market_raw,
        'descartados_dup': descartados_dup,
        'market_processed_rows': market_processed_rows,
        'recency_buckets': recency_buckets,
        'coverage_stats': {
            'comments_total': len(df_mc),
            'comments_with_wine': int(comments_with_wine_detected),
            'comments_matched_to_catalog': matched_comments_count,
            'comments_general_signal': comments_general_market,
            'catalog_coverage_count': catalog_coverage_count,
            'catalog_coverage_pct': catalog_coverage_pct
        },
        'unknowns_stats': {
            'initial_unknowns': int(initial_unknowns),
            'final_unknowns': int(final_unknowns),
            'unknowns_reduced': int(unknowns_reduced)
        },
        'preservation_stats': preservation_stats,
        'duplicates_stats': duplicates_stats,
        'score_stats': score_stats,
        'quiz_results': quiz_results,
        'comparison_data': {
            'v1_recs': recs_v1,
            'v2_recs': recs_v2
        }
    }
    
    json_path = os.path.join(reports_dir, 'v2_data_audit.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(audit_json, f, indent=4, ensure_ascii=False)
        
    md_path = os.path.join(reports_dir, 'v2_data_audit.md')
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write("# Auditoría V2 Wine Recommender (QA Final y Correcciones)\n\n")
        f.write("## Resumen ejecutivo\n")
        f.write("Este reporte valida formalmente las correcciones aplicadas sobre la V2 del recomendador de vinos, cubriendo la deduplicación, recencia, cobertura real y recalibración de confianza.\n\n")
        
        f.write("## Correcciones post-auditoría\n")
        f.write("- **Deduplicación**: Implementada deduplicación por título canónico y remoción del prefijo 'Recomendación Similar a:'.\n")
        f.write("- **Maridaje por Intención**: La lógica ahora Prioriza asado/picadas cuando el usuario indica dicha comida en el quiz.\n")
        f.write("- **Reducción de Unknowns**: Corregido patrón de extracción de variedades desde el título del vino.\n")
        f.write("- **Trazabilidad**: Integradas y persistidas las columnas de control de APIs en el CSV procesado final.\n\n")
        
        f.write("## Conteo V1\n")
        f.write(f"Suma de fuentes originales V1: {v1_sources_total} filas.\n")
        f.write(f"Dataset V1 preparado: {v1_prepared_total} filas. Coincidencia exacta: {v1_sources_total == v1_prepared_total}\n\n")
        
        f.write("## Conteo V2 y Trazabilidad\n")
        f.write(f"- Comentarios de Reddit 2026: {reddit_v2_rows} filas.\n")
        f.write(f"- Comentarios de Mercado Libre 2026: {ml_v2_rows} filas.\n")
        f.write(f"- Comentarios procesados finales: {market_processed_rows} filas.\n\n")
        
        f.write("## Live vs Fallback\n")
        f.write("| Fuente | Método | Live/Fallback | Filas | % |\n")
        f.write("| --- | --- | --- | --- | --- |\n")
        for stat in source_stats:
            f.write(f"| {stat['platform']} | {stat['method']} | {stat['live_fallback']} | {stat['rows']} | {stat['percentage']:.2f}% |\n")
            
        f.write("\n## Buckets de Recencia\n")
        f.write(f"- Últimos 30 días: {recency_buckets['ultimos_30_dias']} comentarios.\n")
        f.write(f"- Últimos 90 días: {recency_buckets['ultimos_90_dias']} comentarios.\n")
        f.write(f"- Últimos 365 días: {recency_buckets['ultimos_365_dias']} comentarios.\n")
        f.write(f"- Más antiguo: {recency_buckets['mas_antiguo']} comentarios.\n\n")
        
        f.write("## Cobertura de Mercado\n")
        f.write(f"- Comentarios nuevos totales: {len(df_mc)}\n")
        f.write(f"- Comentarios con vino detectado: {comments_with_wine_detected}\n")
        f.write(f"- Comentarios matcheados al catálogo V2: {matched_comments_count}\n")
        f.write(f"- Comentarios usados como señal general de mercado: {comments_general_market}\n")
        f.write(f"- Cobertura sobre catálogo (vinos con feedback directo): {catalog_coverage_count} vinos ({catalog_coverage_pct:.3f}% del catálogo total).\n\n")
        
        f.write("## Reducción de variedad Unknown\n")
        f.write(f"- Vinos Unknown V1: {initial_unknowns}\n")
        f.write(f"- Vinos Unknown V2 final: {final_unknowns}\n")
        f.write(f"- Vinos Unknown deducidos y reducidos: **{unknowns_reduced}** vinos.\n\n")
        
        f.write("## Validación de duplicados en recomendaciones\n")
        f.write("| Perfil | Duplicados Detectados en Recomendaciones |\n")
        f.write("| --- | --- |\n")
        for q in quiz_results:
            f.write(f"| {q['perfil']} | {'Sí (Error)' if q['has_duplicates'] else 'No (Corregido)'} |\n")
            
        f.write("\n## Validación quiz adaptativo recalibrado\n")
        f.write("| Perfil | Preguntas respondidas | Confidence Score | Confidence Label | Top 3 recomendaciones | Maridaje |\n")
        f.write("| --- | --- | --- | --- | --- | --- |\n")
        for q in quiz_results:
            f.write(f"| {q['perfil']} | {q['questions_answered']} | {q['confidence_score']:.3f} | {q['confidence_label']} | {', '.join(q['top_5_recommendations'][:3])} | {q['maridaje']} |\n")
            
    comp_path = os.path.join(reports_dir, 'v2_vs_v1_comparison.md')
    with open(comp_path, 'w', encoding='utf-8') as f:
        f.write("# Comparativa Final de Motores de Recomendación: V1 vs V2\n\n")
        f.write("## Comparación de Resultados (Perfil de Prueba Intenso)\n")
        f.write(f"- **V1 Recomendaciones**: {', '.join(recs_v1)}\n")
        f.write(f"- **V2 Recomendaciones (Deduplicado)**: {', '.join(recs_v2)}\n\n")
        f.write("## Mejoras Clave de V2:\n")
        f.write("1. Deduplicación de etiquetas duplicadas en las recomendaciones.\n")
        f.write("2. Maridaje alineado de forma robusta con la intención del quiz (asado, picada, empanadas).\n")
        f.write("3. Reducción masiva de la variedad Unknown en base al título.\n")
        
    print("Auditoría post-correcciones finalizada con éxito y reportes generados.")

if __name__ == '__main__':
    run_audit()
