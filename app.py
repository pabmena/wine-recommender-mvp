from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import pickle
import os
import numpy as np

# Importar configuraciones de mapeo y confianza
from config.taste_mapping import (
    QUESTION_CALIBRATION, QUESTIONS_BY_LEVEL, QUESTIONS_REFINEMENT,
    TASTE_MAPPING, ATTRIBUTE_COLUMNS
)
from config.confidence import should_continue_quiz, choose_next_question, calculate_confidence

app = Flask(__name__)
app.secret_key = 'somm_ai_secret_key_2026'

# Rutas de los archivos
current_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(current_dir, 'data')

# Ruta al dataset de perfiles de vino V2 (actualizado y procesado)
profiles_file_v2 = os.path.join(data_dir, 'processed/wine_profiles_argentina_v2.csv')
profiles_file_v1 = os.path.join(data_dir, 'wine_profiles6.csv')

# Ruta al vectorizador (TF-IDF)
vectorizer_file = os.path.join(data_dir, 'vectorizer.pkl')

# Cargar el dataset de perfiles de vino
try:
    if os.path.exists(profiles_file_v2):
        wine_profiles = pd.read_csv(profiles_file_v2)
        print("Dataset de perfiles de vino V2 (Argentina) cargado correctamente.")
    else:
        wine_profiles = pd.read_csv(profiles_file_v1)
        print("Dataset de perfiles de vino V1 (wine_profiles6) cargado correctamente.")
except FileNotFoundError:
    print("Error: No se encontró ningún dataset de perfiles de vino.")
    wine_profiles = pd.DataFrame()

# Limpiar columnas duplicadas si existieran
if not wine_profiles.empty and wine_profiles.columns.duplicated().any():
    duplicated_cols = wine_profiles.columns[wine_profiles.columns.duplicated()].tolist()
    print(f"Advertencia: Columnas duplicadas encontradas: {duplicated_cols}")
    wine_profiles = wine_profiles.loc[:, ~wine_profiles.columns.duplicated()]
    print("Columnas duplicadas eliminadas.")

# Asegurar que las columnas variedad y source tengan valores por defecto si no existen
if not wine_profiles.empty:
    if 'variedad' not in wine_profiles.columns:
        wine_profiles['variedad'] = 'Variedad Desconocida'
    if 'source' not in wine_profiles.columns:
        wine_profiles['source'] = 'unknown'

# Cargar o entrenar el vectorizador de texto
try:
    with open(vectorizer_file, 'rb') as f:
        vectorizer = pickle.load(f)
    print("Vectorizador cargado correctamente.")
except FileNotFoundError:
    print(f"Error: '{vectorizer_file}' no se encontró. Se reentrenará en el dataset.")
    vectorizer = TfidfVectorizer(stop_words='english')
    if not wine_profiles.empty:
        sommelier_text = wine_profiles[wine_profiles['source'] == 'sommelier_argentina']['full_text'].fillna('')
        if sommelier_text.empty:
            sommelier_text = wine_profiles['full_text'].fillna('')
        vectorizer.fit(sommelier_text)
        print("Vectorizador entrenado exitosamente.")
        with open(vectorizer_file, 'wb') as f:
            pickle.dump(vectorizer, f)
        print("Vectorizador guardado en 'vectorizer.pkl'.")

# Rutas de la aplicación

@app.route('/')
def index():
    # Reiniciar sesión del quiz al ir al inicio
    session.pop('answers', None)
    session.pop('current_step', None)
    session.pop('knowledge_level', None)
    session.pop('refinement_questions', None)
    session.pop('confidence_score', None)
    return render_template('index.html')

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    # Inicializar la sesión si es la primera vez en el quiz
    if 'answers' not in session:
        session['answers'] = {}
        session['current_step'] = 0
        session['knowledge_level'] = None
        session['refinement_questions'] = []

    if request.method == 'POST':
        # Recibir la respuesta de la pregunta actual
        question_id = request.form.get('question_id')
        response_val = request.form.get('response_val')
        
        # Guardar respuesta
        answers = session.get('answers', {})
        answers[question_id] = response_val
        session['answers'] = answers

        # 1. Si respondimos a la calibración
        if question_id == 'conocimiento':
            session['knowledge_level'] = response_val
            session['current_step'] = 0
            return redirect(url_for('quiz'))

        # 2. Si es una pregunta de los niveles base
        current_step = session.get('current_step', 0)
        knowledge_level = session.get('knowledge_level', 'principiante')
        
        # Obtener cantidad de preguntas del nivel actual
        level_questions = QUESTIONS_BY_LEVEL.get(knowledge_level, QUESTIONS_BY_LEVEL['principiante'])
        total_base_steps = len(level_questions)
        
        if current_step < total_base_steps:
            # Incrementar el paso
            session['current_step'] = current_step + 1
            current_step = session['current_step']

        # 3. Si ya completamos las preguntas del nivel base, evaluar corte o refinamiento
        if current_step >= total_base_steps:
            # Crear perfil de usuario temporal
            user_profile, price_filter = create_user_profile(session['answers'])
            
            # Obtener recomendaciones temporales para calcular el margen y cobertura
            recommendations = get_recommendations_for_confidence(user_profile, price_filter)
            
            # Decidir si se continúa
            continue_quiz, confidence = should_continue_quiz(session['answers'], user_profile, recommendations)
            session['confidence_score'] = float(confidence)

            if not continue_quiz:
                # Terminar quiz y redirigir
                session['responses'] = session['answers']
                return redirect(url_for('results'))
            else:
                # Determinar cuál es la siguiente pregunta de refinamiento a hacer
                next_q_id = choose_next_question(session['answers'], user_profile)
                # Incrementar paso virtual en la sesión
                session['current_step'] = len(session['answers']) # El paso pasa a ser el total de preguntas contestadas
                
                # Si el refinamiento ya fue respondido en un ciclo anterior (no debería ocurrir), salir
                if next_q_id in session['answers']:
                    session['responses'] = session['answers']
                    return redirect(url_for('results'))
                
                # Guardar en la cola de refinamientos
                ref_list = session.get('refinement_questions', [])
                ref_list.append(next_q_id)
                session['refinement_questions'] = ref_list
                
        return redirect(url_for('quiz'))

    # Método GET: Renderizar la pregunta actual
    knowledge_level = session.get('knowledge_level')
    current_step = session.get('current_step', 0)
    answers = session.get('answers', {})

    # Paso Inicial: Pregunta de Calibración
    if knowledge_level is None:
        return render_template('quiz.html', 
                               question=QUESTION_CALIBRATION, 
                               step_num=1, 
                               total_steps="?",
                               confidence_text="Calibrando tu perfil de conocimiento...")

    # Pasos 1 a total_base_steps: Preguntas del Nivel Seleccionado
    level_questions = QUESTIONS_BY_LEVEL.get(knowledge_level, QUESTIONS_BY_LEVEL['principiante'])
    total_base_steps = len(level_questions)
    
    if current_step < total_base_steps:
        question_to_ask = level_questions[current_step]
        
        # Progreso: Paso actual de total_base_steps
        return render_template('quiz.html', 
                               question=question_to_ask, 
                               step_num=current_step + 1, 
                               total_steps=total_base_steps,
                               confidence_text="Analizando gustos de base...")

    # Pasos >= 6: Preguntas de Refinamiento
    ref_list = session.get('refinement_questions', [])
    if ref_list:
        next_q_id = ref_list[-1]
        question_to_ask = QUESTIONS_REFINEMENT.get(next_q_id)
        
        # Mostrar el progreso de refinamiento capado a 95%
        q_answered = len(answers)
        conf_score = session.get('confidence_score', 0.0)
        display_conf = min(conf_score, 0.95)
        display_conf_percent = int(display_conf * 100)
        
        return render_template('quiz.html', 
                               question=question_to_ask, 
                               step_num=q_answered, 
                               total_steps="Refinamiento",
                               confidence_text=f"Afinando recomendación (Entendimiento actual: {display_conf_percent}%)")

    # Si se cae de los flujos, terminar y mostrar resultados
    session['responses'] = session['answers']
    return redirect(url_for('results'))

@app.route('/results')
def results():
    responses = session.get('responses', {})
    if not responses:
        return redirect(url_for('quiz'))

    user_profile, price_filter = create_user_profile(responses)
    recommendations = get_recommendations(user_profile, price_filter, user_responses=responses)
    
    from config.confidence import get_display_confidence
    
    # Calcular la confianza final (raw y display)
    raw_confidence = calculate_confidence(responses, user_profile, recommendations)
    display_confidence, confidence_label, confidence_text = get_display_confidence(raw_confidence)
    display_conf_percent = int(display_confidence * 100)

    return render_template('results.html', 
                           recommendations=recommendations, 
                           confidence_percent=display_conf_percent,
                           confidence_label=confidence_label,
                           confidence_text=confidence_text)

# Funciones auxiliares

def create_user_profile(responses):
    """
    Convierte las respuestas del quiz en un perfil de usuario de 19 atributos.
    """
    # Inicializar el perfil del usuario en 0.5 (neutral)
    user_profile_dict = {attr: 0.5 for attr in ATTRIBUTE_COLUMNS}

    # Aplicar los pesos de TASTE_MAPPING
    for question_id, response_val in responses.items():
        if question_id in TASTE_MAPPING and response_val in TASTE_MAPPING[question_id]:
            adjustments = TASTE_MAPPING[question_id][response_val]
            for attr, weight in adjustments.items():
                if attr in user_profile_dict:
                    user_profile_dict[attr] += weight
                    user_profile_dict[attr] = max(0.0, min(1.0, user_profile_dict[attr]))

    user_profile = pd.DataFrame([user_profile_dict])

    # Rango de precios
    precio = responses.get('precio', 'Más de $50')
    price_ranges = {
        'Menos de $10': (0.0, 10.0),
        '$10 - $20': (10.0, 20.0),
        '$20 - $50': (20.0, 50.0),
        'Más de $50': (50.0, np.inf)
    }
    price_min, price_max = price_ranges.get(precio, (50.0, np.inf))

    return user_profile, (price_min, price_max)

def get_recommendations_for_confidence(user_profile, price_filter):
    """
    Versión ultraliviana de recomendaciones para calcular el margen de confianza en tiempo real.
    """
    if wine_profiles.empty:
        return []
    
    wine_attributes = wine_profiles[ATTRIBUTE_COLUMNS].fillna(0.0)
    similarity = cosine_similarity(user_profile, wine_attributes)[0]
    
    wines_eval = wine_profiles.copy()
    wines_eval['sensory_similarity'] = similarity
    
    # Filtro de precio
    price_min, price_max = price_filter
    if 'price' in wines_eval.columns:
        wines_eval = wines_eval[pd.to_numeric(wines_eval['price'], errors='coerce').notnull()]
        wines_eval['price'] = wines_eval['price'].astype(float)
        wines_eval = wines_eval[
            (wines_eval['price'] >= price_min) & (wines_eval['price'] <= price_max)
        ]
        
    if wines_eval.empty:
        return []
        
    top_wines = wines_eval.sort_values(by='sensory_similarity', ascending=False).head(8)
    
    recs = []
    for idx, row in top_wines.iterrows():
        # Match rate estimado
        mr = int(round(row['sensory_similarity'] * 100))
        recs.append({'match_rate': mr})
    return recs

def generate_explanation(user_profile_series, wine_row):
    """
    Genera una explicación dinámica personalizada en español detallando
    la afinidad de paladar y el maridaje ideal argentino.
    """
    explanations = []
    
    # Atributos de sabor y aroma
    key_attrs = [
        'frutas_rojas', 'frutas_negras', 'frutas_cítricas', 'frutas_tropicales', 
        'frutas_hueso', 'especias', 'madera_y_otros', 'acidez', 'taninos', 'cuerpo', 'dulzor'
    ]
    
    # Buscar atributos donde el usuario tiene preferencia positiva (> 0.55) y el vino tiene presencia (> 0.35)
    matches = []
    for attr in key_attrs:
        user_val = user_profile_series.get(attr, 0.5)
        wine_val = wine_row.get(attr, 0.0)
        if user_val > 0.55 and wine_val > 0.35:
            matches.append((attr, wine_val * user_val))

    # Ordenar las coincidencias por relevancia
    matches.sort(key=lambda x: x[1], reverse=True)
    
    attr_descriptions = {
        'frutas_rojas': 'sus notas de frutas rojas (cerezas, frambuesas)',
        'frutas_negras': 'su marcado aroma a frutas negras maduras (ciruelas, moras)',
        'frutas_cítricas': 'sus toques cítricos refrescantes',
        'frutas_tropicales': 'sus expresivos aromas tropicales',
        'frutas_hueso': 'sus notas a frutas de hueso como durazno o damasco',
        'especias': 'su carácter especiado con notas de pimienta o canela',
        'madera_y_otros': 'su crianza en roble que aporta notas de vainilla y tabaco',
        'acidez': 'su acidez vibrante y refrescante',
        'taninos': 'sus taninos firmes y bien estructurados',
        'cuerpo': 'su gran cuerpo y volumen en boca',
        'dulzor': 'su perfil dulce y amable en el paladar'
    }
    
    top_matches = [attr_descriptions[m[0]] for m in matches if m[0] in attr_descriptions][:2]
    
    # Preferencia por suavidad
    suavidad_exps = []
    if user_profile_series.get('taninos', 0.5) < 0.45 and wine_row.get('taninos', 0.0) < 0.25:
        suavidad_exps.append("su textura suave y sedosa en boca")
    if user_profile_series.get('acidez', 0.5) < 0.45 and wine_row.get('acidez', 0.0) < 0.25:
        suavidad_exps.append("una acidez sumamente baja y dócil")
        
    if top_matches:
        frase_gustos = f"Coincide con tu preferencia por {' y '.join(top_matches)}"
        if suavidad_exps:
            frase_gustos += f", acompañado de {' y '.join(suavidad_exps)}"
        explanations.append(frase_gustos + ".")
    elif suavidad_exps:
        explanations.append(f"Ideal para ti por {' y '.join(suavidad_exps)}.")
    else:
        explanations.append("Recomendado por su excelente equilibrio sensorial adaptado a tu paladar.")
        
    # Incorporar el análisis de sentimiento del mercado
    polarity = wine_row.get('polarity', 0.0)
    if polarity > 0.3:
        explanations.append("El mercado local lo valora con reseñas sumamente positivas en contextos de parrilla y juntadas.")
    elif polarity > 0.1:
        explanations.append("Tiene una reputación favorable y opiniones positivas de los consumidores.")
        
    return " ".join(explanations)

def calculate_argentine_scores(wine_row):
    """
    Calcula dinámicamente el asado_score, precio_calidad_score y el argentine_palate_score
    para el vino en base a sus atributos sensoriales, polaridad y precio real.
    """
    # 1. Asado Score: requiere cuerpo, taninos y madera. Típico de tintos robustos.
    cuerpo = wine_row.get('cuerpo', 0.0)
    taninos = wine_row.get('taninos', 0.0)
    madera = wine_row.get('madera_y_otros', 0.0)
    asado_score = 0.4 * cuerpo + 0.4 * taninos + 0.2 * madera
    
    # 2. Precio Calidad Score:
    # Sentimiento en rango [0, 1]
    polarity = wine_row.get('polarity', 0.0)
    sentiment_score = (polarity + 1.0) / 2.0
    price = wine_row.get('price', 15.0)
    
    # Vinos excelentes y económicos tienen el mayor score
    if price < 15.0:
        precio_calidad_score = sentiment_score * 1.0
    elif price < 30.0:
        precio_calidad_score = sentiment_score * 0.85
    elif price < 60.0:
        precio_calidad_score = sentiment_score * 0.70
    else:
        precio_calidad_score = sentiment_score * 0.50

    # 3. Local Sentiment Score
    local_sentiment_score = sentiment_score

    # 4. Origen y Variedad Argentina
    # sommelier_argentina o variedades típicas (Malbec, Bonarda, Torrontés, Cabernet Franc, Criolla)
    source = str(wine_row.get('source', '')).lower()
    variedad = str(wine_row.get('variedad', '')).lower()
    
    típicas_argentinas = ['malbec', 'bonarda', 'torrontes', 'torrontés', 'cabernet franc', 'criolla']
    es_local = 'argentina' in source or any(t in variedad for t in típicas_argentinas)
    
    argentina_source_weight = 1.0 if es_local else 0.5

    # 5. Recency Score (Añadas más recientes > 2010 tienen 1.0)
    # Por defecto 0.9 si no se puede inferir del título
    title = str(wine_row.get('title', ''))
    recency_score = 0.9
    for year in range(2010, 2027):
        if str(year) in title:
            recency_score = 1.0
            break

    # Argentine Palate Score ponderado
    # Formula: 30% local sentiment, 25% asado, 20% precio-calidad, 15% origen, 10% añada
    argentine_palate_score = (
        0.30 * local_sentiment_score +
        0.25 * asado_score +
        0.20 * precio_calidad_score +
        0.15 * argentina_source_weight +
        0.10 * recency_score
    )

    return asado_score, precio_calidad_score, argentine_palate_score

def get_recommendations(user_profile, price_filter, user_responses=None):
    """
    Genera recomendaciones de vinos personalizadas utilizando el perfil adaptativo del usuario,
    el cálculo del Argentine Palate Score, y una fórmula final ponderada.
    Implementa deduplicación de títulos en caliente y maridajes orientados a la intención de comida.
    """
    if wine_profiles.empty:
        return []

    # 1. Calcular similitud coseno sensorial en 19 dimensiones
    wine_attributes = wine_profiles[ATTRIBUTE_COLUMNS].fillna(0.0)
    similarity = cosine_similarity(user_profile, wine_attributes)[0]

    wines_evaluated = wine_profiles.copy()
    wines_evaluated['sensory_similarity'] = similarity

    # Normalizar la similitud sensorial
    max_sensory_similarity = wines_evaluated['sensory_similarity'].max()
    if max_sensory_similarity > 0:
        wines_evaluated['sensory_similarity'] = wines_evaluated['sensory_similarity'] / max_sensory_similarity

    # 2. Filtrar por polaridad negativa fuerte
    if 'polarity' not in wines_evaluated.columns:
        wines_evaluated['polarity'] = 0.0
    filtered_wines = wines_evaluated[wines_evaluated['polarity'] > -0.2].copy()

    # 3. Filtrar por rango de precio
    price_min, price_max = price_filter
    if 'price' in filtered_wines.columns:
        filtered_wines = filtered_wines[pd.to_numeric(filtered_wines['price'], errors='coerce').notnull()]
        filtered_wines['price'] = filtered_wines['price'].astype(float)
        filtered_wines = filtered_wines[
            (filtered_wines['price'] >= price_min) & (filtered_wines['price'] <= price_max)
        ]
    else:
        return []

    if filtered_wines.empty:
        return []

    # 4. Asignar Scores Argentinos
    # Si existen columnas precalculadas (V2), las usamos para optimizar; si no (fallback V1), calculamos en caliente.
    if 'argentine_palate_score' not in filtered_wines.columns or 'asado_score' not in filtered_wines.columns:
        asado_scores = []
        precio_calidad_scores = []
        argentine_palate_scores = []

        for idx, row in filtered_wines.iterrows():
            asado, pc, arg_palate = calculate_argentine_scores(row)
            asado_scores.append(asado)
            precio_calidad_scores.append(pc)
            argentine_palate_scores.append(arg_palate)

        filtered_wines['asado_score'] = asado_scores
        filtered_wines['precio_calidad_score'] = precio_calidad_scores
        filtered_wines['argentine_palate_score'] = argentine_palate_scores

    # Score de sentimiento simple [0, 1]
    filtered_wines['sentiment_score'] = (filtered_wines['polarity'] + 1.0) / 2.0
    filtered_wines['price_fit_score'] = 1.0

    # FÓRMULA FINAL PONDERADA V2:
    filtered_wines['final_score'] = (
        0.55 * filtered_wines['sensory_similarity'] +
        0.20 * filtered_wines['sentiment_score'] +
        0.15 * filtered_wines['argentine_palate_score'] +
        0.10 * filtered_wines['price_fit_score']
    )

    # 5. Ordenar por score final descendente
    sorted_wines = filtered_wines.sort_values(by='final_score', ascending=False)

    # 6. Preparar listado final deduplicado con reglas de diversidad de V2.0.2
    recommendations = []
    seen_titles = set()
    variety_counts = {}
    winery_counts = {}
    user_profile_series = user_profile.iloc[0]

    # Detectar perfil fresco/liviano (principiante y avanzado)
    fresh_light_profile = False
    if user_responses:
        asado_pref = user_responses.get('asado_pref')
        cafe_pref = user_responses.get('cafe_pref')
        choco_pref = user_responses.get('chocolate_pref')
        cuerpo_tecnico = user_responses.get('cuerpo_tecnico')
        taninos_tecnico = user_responses.get('taninos_tecnico')
        acidez_tecnico = user_responses.get('acidez_tecnico')
        
        # Principiante fresco/liviano
        if asado_pref == 'A' or (cafe_pref == 'A' and choco_pref == 'A'):
            fresh_light_profile = True
        # Avanzado fresco/liviano
        elif cuerpo_tecnico == 'A' and taninos_tecnico == 'A' and acidez_tecnico == 'C':
            fresh_light_profile = True

    # También por perfil sensorial si tiene acidez alta y cuerpo/taninos bajos
    if user_profile_series.get('acidez', 0.5) > 0.50 and user_profile_series.get('cuerpo', 0.5) < 0.50 and user_profile_series.get('taninos', 0.5) < 0.50:
        fresh_light_profile = True

    # Determinar si es perfil intensivo/asado
    is_intense_profile = False
    if user_responses:
        asado_pref = user_responses.get('asado_pref', 'B')
        if asado_pref == 'D':
            is_intense_profile = True
    elif user_profile_series.get('cuerpo', 0.5) > 0.65:
        is_intense_profile = True

    fresh_varieties = ['torrontés', 'torrontes', 'chardonnay', 'sauvignon blanc', 'pinot noir', 'rosé', 'rose', 'white blend', 'sparkling blend', 'pinot grigio', 'viognier']
    tinto_estructurado_varieties = ['malbec', 'cabernet sauvignon', 'syrah', 'bordeaux-style red blend', 'tempranillo', 'merlot', 'red blend']

    # Pasada 1: Aplicar reglas estrictas de diversidad de V2.0.2
    for idx, row in sorted_wines.iterrows():
        if len(recommendations) >= 8:
            break

        raw_title = row.get('title', 'Vino sin Título')
        clean_title = str(raw_title).replace("Recomendación Similar a: ", "").replace("Recomendación Similar a:", "").strip()
        
        if clean_title.lower() in seen_titles:
            continue
            
        variedad = row.get('variedad', 'Unknown')
        if pd.isna(variedad) or str(variedad).strip().lower() in ['unknown', 'variedad desconocida', 'unknown variety']:
            variedad = extract_variedad_from_title(clean_title)
            
        winery = extract_winery_from_title(clean_title)
        variedad_lower = variedad.lower()

        # A. Excluir variedad Unknown en Top 5
        if len(recommendations) < 5 and variedad_lower in ['unknown', 'variedad desconocida', 'unknown variety']:
            continue
            
        # B. Máximo 2 vinos de la misma variedad en Top 5
        var_count = variety_counts.get(variedad_lower, 0)
        if len(recommendations) < 5 and var_count >= 2:
            continue

        # C. Máximo 2 vinos de la misma bodega en Top 5
        winery_count = winery_counts.get(winery.lower(), 0)
        if len(recommendations) < 5 and winery_count >= 2:
            continue

        # D. Reglas específicas para Perfil Fresco/Liviano
        if len(recommendations) < 5 and fresh_light_profile:
            # 1. Máximo 1 Malbec
            is_malbec = 'malbec' in variedad_lower
            if is_malbec:
                malbec_in_top5 = sum(1 for w in recommendations if 'malbec' in w['variedad'].lower())
                if malbec_in_top5 >= 1:
                    continue
            
            # 2. Máximo 2 tintos estructurados
            is_tinto_est = any(t in variedad_lower for t in tinto_estructurado_varieties) and (row.get('cuerpo', 0.0) > 0.40 or row.get('taninos', 0.0) > 0.40)
            if is_tinto_est:
                tintos_in_top5 = sum(1 for w in recommendations if any(t in w['variedad'].lower() for t in tinto_estructurado_varieties) and (w['cuerpo'] > 0.40 or w['taninos'] > 0.40))
                if tintos_in_top5 >= 2:
                    continue
                    
            # 3. Forzar a tener variedad fresca si no es tinto
            is_fresh = any(f in variedad_lower for f in fresh_varieties)
            if not is_fresh:
                non_fresh_in_top5 = sum(1 for w in recommendations if not any(f in w['variedad'].lower() for f in fresh_varieties))
                if non_fresh_in_top5 >= 2:
                    continue

        # E. Excluir exceso de Malbec si no es perfil asado por defecto
        elif len(recommendations) < 5 and not is_intense_profile:
            is_malbec = 'malbec' in variedad_lower
            if is_malbec:
                malbec_in_top5 = sum(1 for w in recommendations if 'malbec' in w['variedad'].lower())
                if malbec_in_top5 >= 2:
                    continue

        seen_titles.add(clean_title.lower())
        variety_counts[variedad_lower] = variety_counts.get(variedad_lower, 0) + 1
        winery_counts[winery.lower()] = winery_counts.get(winery.lower(), 0) + 1

        wine_data = build_wine_data_record(row, clean_title, variedad, winery, user_profile_series, user_responses)
        recommendations.append(wine_data)

    # Pasada 2 (Fallback): si faltan recomendaciones, completar relajando restricciones
    if len(recommendations) < 8:
        for idx, row in sorted_wines.iterrows():
            if len(recommendations) >= 8:
                break

            raw_title = row.get('title', 'Vino sin Título')
            clean_title = str(raw_title).replace("Recomendación Similar a: ", "").replace("Recomendación Similar a:", "").strip()
            
            if clean_title.lower() in seen_titles:
                continue

            variedad = row.get('variedad', 'Unknown')
            if pd.isna(variedad) or str(variedad).strip().lower() in ['unknown', 'variedad desconocida', 'unknown variety']:
                variedad = extract_variedad_from_title(clean_title)
                
            winery = extract_winery_from_title(clean_title)

            seen_titles.add(clean_title.lower())
            wine_data = build_wine_data_record(row, clean_title, variedad, winery, user_profile_series, user_responses)
            recommendations.append(wine_data)

    return recommendations

def extract_winery_from_title(title):
    """
    Deduce el nombre de la bodega a partir de las primeras palabras del título.
    """
    words = str(title).split()
    if len(words) >= 2:
        if words[0].lower() in ['bodega', 'bodegas', 'viña', 'viñas', 'finca', 'fincas']:
            return " ".join(words[:3])
        return " ".join(words[:2])
    return words[0] if words else 'Bodega Desconocida'

def build_wine_data_record(row, clean_title, variedad, winery, user_profile_series, user_responses):
    """
    Construye de forma estructurada el registro de datos para cada recomendación.
    """
    raw_price = row.get('price', None)
    formatted_price = round(float(raw_price), 2) if pd.notna(raw_price) else None

    asado_val = row['asado_score']
    madera_val = row.get('madera_y_otros', 0.0)
    cuerpo_val = row.get('cuerpo', 0.0)
    acidez_val = row.get('acidez', 0.0)
    dulzor_val = row.get('dulzor', 0.0)
    
    variedad_lower = variedad.lower()
    maridajes = []
    ocasiones = []
    
    # Prioridad 1: Intención explícita de comida y asado del quiz
    has_asado_intent = False
    if user_responses:
        asado_pref = user_responses.get('asado_pref', 'B')
        if asado_pref in ['B', 'C', 'D']:
            has_asado_intent = True
            
    if has_asado_intent:
        asado_pref = user_responses.get('asado_pref', 'B')
        if asado_pref == 'D':
            maridajes.append("Asado de tira a la leña / Vacío ahumado")
            maridajes.append("Choripán con chimichurri / Provoleta dorada")
            ocasiones.append("Parrillada con amigos / Domingo familiar")
        elif asado_pref == 'B':
            maridajes.append("Ojo de bife jugoso / Bife de chorizo")
            maridajes.append("Empanadas criollas de carne cortada a cuchillo")
            ocasiones.append("Almuerzo de domingo / Cena con amigos")
        else:
            maridajes.append("Picada completa (quesos, fiambres, aceitunas)")
            maridajes.append("Provoleta dorada a la parrilla")
            ocasiones.append("Reunión informal / Juntada al aire libre")
            
    # Prioridad 2: Maridajes basados en variedad de uva y perfil organoléptico
    elif "torrontes" in variedad_lower or "torrontés" in variedad_lower:
        maridajes.append("Empanadas salteñas picantes")
        maridajes.append("Humita en chala / Tamales")
        ocasiones.append("Juntada informal con empanadas")
    elif "bonarda" in variedad_lower:
        maridajes.append("Picada de fiambres y quesos argentinos")
        maridajes.append("Guiso de lentejas o asado cotidiano")
        ocasiones.append("Reunión distendida / Asado con amigos")
    elif "pinot noir" in variedad_lower:
        maridajes.append("Milanesa de ternera o pollo")
        maridajes.append("Pastas rellenas con salsas suaves")
        ocasiones.append("Cena tranquila / Conversación informal")
    elif "criolla" in variedad_lower:
        maridajes.append("Empanadas de queso y choclo")
        maridajes.append("Picada ligera / Tortilla de papas")
        ocasiones.append("Consumo cotidiano fresco de verano")
    elif "chardonnay" in variedad_lower or "sauvignon" in variedad_lower or "semillon" in variedad_lower or "semillón" in variedad_lower:
        maridajes.append("Pescado de río a la parrilla (pacú, dorado)")
        maridajes.append("Picada con quesos suaves y aceitunas")
        ocasiones.append("Tarde de verano / Almuerzo fresco")
    elif "sparkling" in variedad_lower or "espumante" in variedad_lower:
        maridajes.append("Flan con dulce de leche / Postres dulces")
        maridajes.append("Cena de celebración / Recepciones")
        ocasiones.append("Brindis / Celebración especial")
    elif "cabernet franc" in variedad_lower:
        maridajes.append("Entraña o vacío a la parilla con chimichurri")
        maridajes.append("Pastas de domingo con estofado")
        ocasiones.append("Cena especial / Parrillada gourmet")
    else:
        if asado_val > 0.40:
            maridajes.append("Asado de tira / Vacío a la parrilla")
            maridajes.append("Choripán / Provoleta dorada")
            ocasiones.append("Parrillada familiar de domingo")
        elif cuerpo_val > 0.4 and madera_val > 0.3:
            maridajes.append("Empanadas de carne cortada a cuchillo")
            maridajes.append("Milanesa a la napolitana con papas fritas")
            ocasiones.append("Cena de amigos en bodegón")
        elif acidez_val > 0.35:
            maridajes.append("Picada tradicional y quesos")
            maridajes.append("Pizza de molde argentina (muzzarella/fugazzeta)")
            ocasiones.append("Reunión de fin de semana")
        elif dulzor_val > 0.35:
            maridajes.append("Queso y dulce (Vigilante) / Alfajores")
            ocasiones.append("Cierre de cena / Sobremesa dulce")
        else:
            maridajes.append("Pastas de domingo con tuco y pesto")
            ocasiones.append("Cena familiar / Consumo cotidiano")

    explanation = generate_explanation(user_profile_series, row)
    match_rate = int(round(row['final_score'] * 100))
    match_rate = min(100, max(0, match_rate))
    
    arg_palate_val = row['argentine_palate_score']
    if arg_palate_val >= 0.52:
        afinidad_arg = "Alta"
    elif arg_palate_val >= 0.42:
        afinidad_arg = "Media"
    else:
        afinidad_arg = "Baja"

    return {
        'wine_id': int(row.get('wine_id', 0)),
        'title': clean_title,
        'price': formatted_price,
        'variedad': variedad,
        'winery': winery,
        'sentiment_label': row.get('sentiment_label', 'Neutral'),
        'polarity': float(row.get('polarity', 0.0)),
        'match_rate': match_rate,
        'afinidad_argentine': afinidad_arg,
        'ideal_para': ", ".join(maridajes),
        'ocasion': ", ".join(ocasiones),
        'explanation': explanation,
        'source': row.get('source', 'unknown'),
        'frutas_rojas': float(row.get('frutas_rojas', 0.0)),
        'frutas_negras': float(row.get('frutas_negras', 0.0)),
        'especias': float(row.get('especias', 0.0)),
        'acidez': float(row.get('acidez', 0.0)),
        'madera_y_otros': float(row.get('madera_y_otros', 0.0)),
        'cuerpo': float(row.get('cuerpo', 0.0)),
        'taninos': float(row.get('taninos', 0.0)),
        'dulzor': float(row.get('dulzor', 0.0))
    }

def extract_variedad_from_title(title):
    if not title or pd.isna(title):
        return 'Variedad Desconocida'
    title_str = str(title)
    if '(' in title_str and ')' in title_str:
        try:
            dentro_parentesis = title_str.split('(')[-1].split(')')[0]
            return dentro_parentesis.split()[-1]
        except IndexError:
            pass
    return title_str.split()[-1]

if __name__ == '__main__':
    app.run(debug=True)
