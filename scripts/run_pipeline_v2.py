import sys
import os

# Agregar la raíz del proyecto al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from collect_reddit_argentina_v2 import collect_reddit_data
from collect_youtube_comments_v2 import collect_youtube_comments
from collect_mercadolibre_reviews_v2 import collect_mercadolibre_reviews
from normalize_market_comments import normalize_comments
from build_wine_profiles_argentina_v2 import build_profiles_v2

def run_full_pipeline():
    print("=================== INICIANDO PIPELINE DE DATOS V2 (SommAI) ===================")
    
    # 1. Ingesta / Colección (Fuentes Crudas)
    collect_reddit_data()
    collect_youtube_comments()
    collect_mercadolibre_reviews()
    
    print("\n--- Etapa 1: Ingesta finalizada. ---")
    
    # 2. Normalización de Comentarios
    normalize_comments()
    
    print("\n--- Etapa 2: Normalización finalizada. ---")
    
    # 3. Fusión de Perfiles y Cómputo de Scores Locales
    build_profiles_v2()
    
    print("\n=================== PIPELINE V2 COMPLETADO EXITOSAMENTE ===================")

if __name__ == '__main__':
    run_full_pipeline()
