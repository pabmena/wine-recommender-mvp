from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import pickle
import os
import numpy as np
import uuid

# Importar dependencias comerciales y analíticas
from config.clients import get_client_config, CLIENTS
from config.analytics import track_event, get_client_dashboard_metrics

# Importar configuraciones de mapeo y confianza
from config.taste_mapping import (
    QUESTIONS_INITIAL, QUESTIONS_REGALO, QUESTIONS_SENSORIALES, QUESTIONS_REFINEMENT,
    ATTRIBUTE_COLUMNS
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

def load_client_catalog(client_id):
    """
    Carga el catálogo CSV de un cliente y mapea sensorialmente cada vino
    con el dataset maestro wine_profiles para heredar atributos de cata.
    """
    catalog_path = os.path.join(data_dir, f'clients/{client_id}/catalog.csv')
    if not os.path.exists(catalog_path):
        print(f"Advertencia: No se encontró catálogo para el cliente '{client_id}'.")
        return pd.DataFrame()
        
    try:
        client_df = pd.read_csv(catalog_path)
        # Filtrar por stock > 0 y active = True
        client_df['active'] = client_df['active'].astype(str).str.lower().str.strip()
        client_df = client_df[client_df['active'] == 'true']
        client_df = client_df[client_df['stock'].astype(float) > 0]
        
        if client_df.empty:
            return pd.DataFrame()
            
        # Preparar mapeo rápido con el catálogo maestro por título normalizado
        maestro_by_title = {}
        for idx, row in wine_profiles.iterrows():
            title_norm = str(row.get('title', '')).lower().strip()
            maestro_by_title[title_norm] = row
            
        # Perfiles promedio por variedad para fallbacks
        maestro_by_variety = {}
        if not wine_profiles.empty:
            grouped = wine_profiles.groupby('variedad')
            for var_name, group in grouped:
                maestro_by_variety[var_name.lower().strip()] = group[ATTRIBUTE_COLUMNS + ['argentine_palate_score', 'polarity']].mean(numeric_only=True)
                
        mapped_rows = []
        for idx, row in client_df.iterrows():
            title_norm = str(row.get('title', '')).lower().strip()
            variety_norm = str(row.get('variety', '')).lower().strip()
            
            # Buscar coincidencia exacta
            maestro_row = maestro_by_title.get(title_norm)
            
            if maestro_row is not None:
                record = row.to_dict()
                for attr in ATTRIBUTE_COLUMNS + ['argentine_palate_score', 'polarity', 'full_text']:
                    record[attr] = maestro_row.get(attr, 0.5)
                record['wine_id'] = maestro_row.get('wine_id', f"CLIENT-{row.get('sku')}")
                mapped_rows.append(record)
            else:
                # Fallback a perfil de variedad promedio
                record = row.to_dict()
                fallback_profile = maestro_by_variety.get(variety_norm)
                if fallback_profile is None:
                    # Intentar coincidencia parcial
                    found = False
                    for var_k, var_v in maestro_by_variety.items():
                        if var_k in variety_norm or variety_norm in var_k:
                            fallback_profile = var_v
                            found = True
                            break
                    if not found:
                        fallback_profile = {attr: 0.5 for attr in ATTRIBUTE_COLUMNS + ['argentine_palate_score', 'polarity']}
                        
                for attr in ATTRIBUTE_COLUMNS + ['argentine_palate_score', 'polarity']:
                    record[attr] = fallback_profile.get(attr, 0.5)
                record['full_text'] = row.get('description', '')
                record['wine_id'] = f"CLIENT-{row.get('sku')}"
                mapped_rows.append(record)
                
        mapped_df = pd.DataFrame(mapped_rows)
        mapped_df['variedad'] = mapped_df['variety']
        return mapped_df
    except Exception as e:
        print(f"Error al cargar catálogo del cliente '{client_id}': {e}")
        return pd.DataFrame()

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
    # Inicializar la sesión si es la primera vez en el quiz o si se requiere limpiar
    if 'answers' not in session or request.args.get('reset') == '1':
        session['answers'] = {}
        session['current_step'] = 0
        session['knowledge_level'] = None
        session['intencion'] = None
        session['presupuesto'] = None
        session['regalo_flow_step'] = 0
        session['refinement_questions'] = []
        session['confidence_score'] = 0.5
        session['completed_tracked'] = False
        session['session_id'] = str(uuid.uuid4())

    client_id = session.get('client_id')
    client_config = get_client_config(client_id) if client_id else None

    if request.method == 'POST':
        question_id = request.form.get('question_id')
        response_val = request.form.get('response_val')

        # Guardar en respuestas de sesión
        answers = session.get('answers', {})
        answers[question_id] = response_val
        session['answers'] = answers

        # Procesar según el ID de la pregunta
        if question_id == 'intencion':
            session['intencion'] = response_val
            track_event(client_id, 'quiz_intent_selected', session.get('session_id'), {'intent': response_val})
            return redirect(url_for('quiz'))

        elif question_id == 'conocimiento':
            session['knowledge_level'] = response_val
            track_event(client_id, 'quiz_level_selected', session.get('session_id'), {'level': response_val})
            return redirect(url_for('quiz'))

        elif question_id == 'presupuesto':
            session['presupuesto'] = response_val
            return redirect(url_for('quiz'))

        elif question_id.startswith('regalo_'):
            track_event(client_id, 'quiz_answered', session.get('session_id'), {'question_id': question_id, 'response_val': response_val})
            session['regalo_flow_step'] = session.get('regalo_flow_step', 0) + 1
            if session['regalo_flow_step'] >= len(QUESTIONS_REGALO):
                session['responses'] = session['answers']
                return redirect(url_for('results'))
            return redirect(url_for('quiz'))

        else:
            # Pregunta sensorial o de refinamiento
            track_event(client_id, 'quiz_answered', session.get('session_id'), {'question_id': question_id, 'response_val': response_val})
            
            # Si estamos en preguntas sensoriales base de nivel
            knowledge_level = session.get('knowledge_level', 'principiante')
            sensorial_questions = QUESTIONS_SENSORIALES.get(knowledge_level, QUESTIONS_SENSORIALES['principiante'])
            current_step = session.get('current_step', 0)

            if current_step < len(sensorial_questions):
                session['current_step'] = current_step + 1
                current_step = session['current_step']

            # Si ya contestamos las sensoriales del nivel base
            if current_step >= len(sensorial_questions):
                user_profile, price_filter = create_user_profile(session['answers'])
                recommendations = get_recommendations_for_confidence(user_profile, price_filter)
                
                # Evaluar confianza y refinamiento
                continue_quiz, confidence = should_continue_quiz(session['answers'], user_profile, recommendations)
                session['confidence_score'] = float(confidence)

                # Capar a un máximo absoluto de 10 respuestas totales (incluyendo calibración)
                if not continue_quiz or len(session['answers']) >= 10:
                    session['responses'] = session['answers']
                    return redirect(url_for('results'))
                else:
                    next_q_id = choose_next_question(session['answers'], user_profile)
                    if not next_q_id or next_q_id in session['answers']:
                        session['responses'] = session['answers']
                        return redirect(url_for('results'))

                    ref_list = session.get('refinement_questions', [])
                    ref_list.append(next_q_id)
                    session['refinement_questions'] = ref_list
            
            return redirect(url_for('quiz'))

    # --- Método GET ---
    answers = session.get('answers', {})
    intencion = session.get('intencion')
    knowledge_level = session.get('knowledge_level')
    presupuesto = session.get('presupuesto')
    regalo_flow_step = session.get('regalo_flow_step', 0)

    # 1. Pregunta inicial de Intención
    if intencion is None:
        return render_template('quiz.html',
                               question=QUESTIONS_INITIAL['intencion'],
                               step_num=1,
                               total_steps=3,
                               confidence_text="Definiendo la intención de compra...",
                               client=client_config)

    # 2. Si la intención es regalo -> Flujo de Regalo Secuencial
    if intencion == 'para_regalar':
        if regalo_flow_step < len(QUESTIONS_REGALO):
            question_to_ask = QUESTIONS_REGALO[regalo_flow_step]
            return render_template('quiz.html',
                                   question=question_to_ask,
                                   step_num=regalo_flow_step + 1,
                                   total_steps=len(QUESTIONS_REGALO),
                                   confidence_text=f"Analizando perfil del regalo ({regalo_flow_step + 1}/{len(QUESTIONS_REGALO)})...",
                                   client=client_config)
        else:
            session['responses'] = session['answers']
            return redirect(url_for('results'))

    # 3. Flujo Personal / Comida / Evento
    # 3a. Pregunta de Nivel
    if knowledge_level is None:
        return render_template('quiz.html',
                               question=QUESTIONS_INITIAL['conocimiento'],
                               step_num=2,
                               total_steps=3,
                               confidence_text="Identificando tu nivel de conocimiento...",
                               client=client_config)

    # 3b. Pregunta de Presupuesto
    if presupuesto is None:
        return render_template('quiz.html',
                               question=QUESTIONS_INITIAL['presupuesto'],
                               step_num=3,
                               total_steps=3,
                               confidence_text="Estableciendo rango de presupuesto...",
                               client=client_config)

    # 3c. Preguntas Sensoriales de Base del Nivel
    sensorial_questions = QUESTIONS_SENSORIALES.get(knowledge_level, QUESTIONS_SENSORIALES['principiante'])
    current_step = session.get('current_step', 0)
    total_base_steps = len(sensorial_questions)

    if current_step < total_base_steps:
        question_to_ask = sensorial_questions[current_step]
        # Progreso: pasos iniciales (3) + paso sensorial actual (current_step + 1)
        return render_template('quiz.html',
                               question=question_to_ask,
                               step_num=3 + current_step + 1,
                               total_steps=3 + total_base_steps,
                               confidence_text="Analizando gustos de base...",
                               client=client_config)

    # 3d. Preguntas de Refinamiento (si la confianza era baja)
    ref_list = session.get('refinement_questions', [])
    if ref_list:
        next_q_id = ref_list[-1]
        
        # Buscar la pregunta correspondiente en QUESTIONS_REFINEMENT
        question_to_ask = None
        if next_q_id in QUESTIONS_REFINEMENT:
            question_to_ask = QUESTIONS_REFINEMENT[next_q_id]
        else:
            for ref_key, ref_q in QUESTIONS_REFINEMENT.items():
                if ref_q['id'] == next_q_id or ref_key == next_q_id:
                    question_to_ask = ref_q
                    break
        
        if question_to_ask:
            q_answered = len(answers)
            conf_score = session.get('confidence_score', 0.5)
            display_conf_percent = int(min(conf_score, 0.95) * 100)
            
            return render_template('quiz.html',
                                   question=question_to_ask,
                                   step_num=q_answered + 1,
                                   total_steps="Refinamiento",
                                   confidence_text=f"Afinando recomendación (Entendimiento: {display_conf_percent}%)",
                                   client=client_config)

    # Si se completó todo sin refinamientos extra pendientes, ir a resultados
    session['responses'] = session['answers']
    return redirect(url_for('results'))

@app.route('/quiz/back')
def quiz_back():
    answers = session.get('answers', {})
    if not answers:
        return redirect(url_for('quiz'))

    # Obtener y remover la última respuesta guardada
    last_q_id = list(answers.keys())[-1]
    answers.pop(last_q_id, None)
    session['answers'] = answers

    # Sincronizar variables de control en base a lo que se eliminó
    if last_q_id == 'intencion':
        session['intencion'] = None
    elif last_q_id == 'conocimiento':
        session['knowledge_level'] = None
    elif last_q_id == 'presupuesto':
        session['presupuesto'] = None
    elif last_q_id.startswith('regalo_'):
        session['regalo_flow_step'] = max(0, session.get('regalo_flow_step', 0) - 1)
    else:
        if last_q_id.startswith('ref_') or last_q_id.startswith('refinement_'):
            ref_list = session.get('refinement_questions', [])
            if ref_list:
                ref_list.pop()
                session['refinement_questions'] = ref_list
        else:
            session['current_step'] = max(0, session.get('current_step', 0) - 1)

    return redirect(url_for('quiz'))

@app.route('/results')
def results():
    responses = session.get('responses', {})
    if not responses:
        return redirect(url_for('quiz'))

    user_profile, price_filter = create_user_profile(responses)
    recommendations = get_recommendations(user_profile, price_filter, user_responses=responses)
    
    from config.confidence import get_display_confidence
    
    # Calcular la confianza final
    raw_confidence = calculate_confidence(responses, user_profile, recommendations)
    display_confidence, confidence_label, confidence_text = get_display_confidence(raw_confidence)
    display_conf_percent = int(display_confidence * 100)

    # Inyectar variables comerciales y registrar eventos de tracking si hay client_id
    client_id = session.get('client_id')
    session_id = session.get('session_id')
    client_config = get_client_config(client_id) if client_id else None

    # Registrar el completado
    if client_id and session_id and not session.get('completed_tracked'):
        top_wines = [w['title'] for w in recommendations[:5]]
        price_range = responses.get('presupuesto', 'medio')
        track_event(client_id, 'quiz_completed', session_id, payload={
            'top_recommendations': top_wines,
            'price_range': price_range
        })
        track_event(client_id, 'recommendation_viewed', session_id)
        session['completed_tracked'] = True

    # --- AGRUPAMIENTO POR COLOR / ESTILO EN TABS (Punto 8) ---
    mejor_match = recommendations[:3] # Top 3
    
    tintos = []
    blancos = []
    espumantes = []
    rosados = []
    precio_calidad = []
    regalo = []
    asado = []

    for wine in recommendations:
        variedad_l = wine.get('variedad', '').lower()
        title_l = wine.get('title', '').lower()
        
        is_sparkling = any(s in variedad_l or s in title_l for s in ['sparkling', 'espumante', 'brut', 'champagne', 'extra brut', 'prosecco'])
        is_rose = 'rosé' in variedad_l or 'rose' in variedad_l or 'rosado' in title_l or 'rose' in title_l
        is_white = any(w in variedad_l for w in ['chardonnay', 'sauvignon', 'torrontes', 'torrontés', 'pinot grigio', 'chenin', 'semillon', 'semillón', 'viognier']) or 'blanco' in title_l
        
        if is_sparkling:
            espumantes.append(wine)
        elif is_rose:
            rosados.append(wine)
        elif is_white:
            blancos.append(wine)
        else:
            tintos.append(wine)

        # Regalo
        if wine.get('gift_safe'):
            regalo.append(wine)

        # Asado
        if wine.get('asado_score', 0.0) >= 0.55:
            asado.append(wine)

    # Ordenar por precio-calidad (mejor score precio_calidad_score primero)
    precio_calidad = sorted(recommendations, key=lambda w: w.get('precio_calidad_score', 0.0), reverse=True)

    es_regalo_intencion = (responses.get('intencion') == 'para_regalar')
    es_asado_comida = (responses.get('intencion') == 'comida')

    return render_template('results.html', 
                           recommendations=recommendations,
                           mejor_match=mejor_match,
                           tintos=tintos,
                           blancos=blancos,
                           espumantes=espumantes,
                           rosados=rosados,
                           precio_calidad=precio_calidad,
                           regalo=regalo,
                           asado=asado,
                           es_regalo_intencion=es_regalo_intencion,
                           es_asado_comida=es_asado_comida,
                           confidence_percent=display_conf_percent,
                           confidence_label=confidence_label,
                           confidence_text=confidence_text,
                           client=client_config)

@app.route('/track/tab_view/<client_slug>/<tab_name>', methods=['POST'])
def track_tab_view(client_slug, tab_name):
    session_id = session.get('session_id')
    track_event(client_slug, 'result_tab_viewed', session_id, payload={'tab': tab_name})
    return {"status": "success", "event_tracked": "result_tab_viewed", "tab": tab_name}

@app.route('/track/assistant/<client_slug>/<question_key>', methods=['POST'])
def track_assistant_question(client_slug, question_key):
    session_id = session.get('session_id')
    track_event(client_slug, 'assistant_question_clicked', session_id, payload={'question': question_key})
    return {"status": "success", "event_tracked": "assistant_question_clicked", "question": question_key}

@app.route('/track/explanation/<client_slug>/<wine_sku>', methods=['POST'])
def track_wine_explanation(client_slug, wine_sku):
    session_id = session.get('session_id')
    track_event(client_slug, 'wine_explanation_opened', session_id, payload={'wine_sku': wine_sku})
    return {"status": "success", "event_tracked": "wine_explanation_opened", "wine_sku": wine_sku}

# Funciones auxiliares

def create_user_profile(responses):
    """
    Convierte las respuestas del quiz en un perfil de usuario de 19 atributos.
    """
    # Inicializar el perfil del usuario en 0.5 (neutral)
    user_profile_dict = {attr: 0.5 for attr in ATTRIBUTE_COLUMNS}

    # Aplicar los impactos de las preguntas sensoriales
    for question_id, response_val in responses.items():
        # Encontrar el impacto de la pregunta
        impact = None
        for lvl in ['principiante', 'intermedio', 'avanzado']:
            if lvl in QUESTIONS_SENSORIALES:
                for q in QUESTIONS_SENSORIALES[lvl]:
                    if q['id'] == question_id:
                        impact = q.get('attribute_impact')
                        break
            if impact:
                break
        
        # Encontrar en refinamientos
        if not impact and question_id in QUESTIONS_REFINEMENT:
            impact = QUESTIONS_REFINEMENT[question_id].get('attribute_impact')
        if not impact:
            for ref_key, ref_q in QUESTIONS_REFINEMENT.items():
                if ref_q['id'] == question_id or ref_key == question_id:
                    impact = ref_q.get('attribute_impact')
                    break

        if impact:
            # Ponderación basada en la respuesta emocional (gusta/neutro/no_gusta)
            multiplier = 0.0
            if response_val == 'gusta':
                multiplier = 1.0
            elif response_val == 'no_gusta':
                multiplier = -1.0
            
            if multiplier != 0.0:
                for attr, weight in impact.items():
                    if attr in user_profile_dict:
                        user_profile_dict[attr] += multiplier * weight
                        user_profile_dict[attr] = max(0.0, min(1.0, user_profile_dict[attr]))

    user_profile = pd.DataFrame([user_profile_dict])

    # Rango de precios adaptado al presupuesto seleccionado (bajo, medio, alto)
    client_id = session.get('client_id')
    presupuesto = responses.get('presupuesto', responses.get('regalo_presupuesto', 'medio'))
    
    if client_id:
        price_ranges = {
            'bajo': (0.0, 15000.0),
            'medio': (15000.0, 35000.0),
            'alto': (35000.0, np.inf)
        }
    else:
        price_ranges = {
            'bajo': (0.0, 15.0),
            'medio': (15.0, 35.0),
            'alto': (35.0, np.inf)
        }
    price_min, price_max = price_ranges.get(presupuesto, (15000.0, 35000.0) if client_id else (15.0, 35.0))

    return user_profile, (price_min, price_max)

def get_recommendations_for_confidence(user_profile, price_filter):
    """
    Versión ultraliviana de recomendaciones para calcular el margen de confianza en tiempo real.
    Soporta la consulta sobre el catálogo del cliente si está activo.
    """
    client_id = session.get('client_id')
    current_wines = wine_profiles
    if client_id:
        client_catalog = load_client_catalog(client_id)
        if not client_catalog.empty:
            current_wines = client_catalog
            
    if current_wines.empty:
        return []
    
    wine_attributes = current_wines[ATTRIBUTE_COLUMNS].fillna(0.0)
    similarity = cosine_similarity(user_profile, wine_attributes)[0]
    
    wines_eval = current_wines.copy()
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
        'dulzor': 'su perfil amable, frutado y fácil de tomar'
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

# Clasificación comercial de estilos por variedad
white_fresh_varieties = ['torrontés', 'torrontes', 'chardonnay', 'sauvignon blanc', 'sauvignon', 'pinot grigio', 'white blend', 'sparkling blend', 'espumante', 'rosé', 'rose', 'viognier']
light_red_varieties = ['pinot noir', 'criolla', 'país', 'pais']
structured_red_varieties = ['malbec', 'cabernet sauvignon', 'cabernet franc', 'cabernet', 'bonarda', 'syrah', 'red blend', 'bordeaux-style red blend', 'malbec-cabernet sauvignon', 'merlot', 'malbec-cabernet', 'malbec blend', 'tempranillo']

def infer_commercial_intent(quiz_answers, user_profile):
    """
    Infiere la intención de compra y estilo comercial del usuario
    según sus respuestas del quiz o perfil sensorial.
    """
    wants_white_fresh = False
    wants_red = False
    wants_asado = False
    wants_price_value = False
    wants_premium = False
    allows_exploration = False

    user_profile_series = user_profile.iloc[0] if isinstance(user_profile, pd.DataFrame) else user_profile

    if quiz_answers:
        knowledge = quiz_answers.get('conocimiento', 'principiante')
        
        if knowledge == 'principiante':
            cafe = quiz_answers.get('cafe_pref')
            choco = quiz_answers.get('chocolate_pref')
            asado = quiz_answers.get('asado_pref')
            
            # Quiere blanco/fresco
            if asado == 'A' or (cafe == 'A' and choco == 'A'):
                wants_white_fresh = True
            # Quiere tintos
            if asado in ['B', 'C']:
                wants_red = True
            # Quiere asado robusto
            if asado == 'C':
                wants_asado = True
                wants_red = True
        else:
            cuerpo = quiz_answers.get('cuerpo_tecnico')
            taninos = quiz_answers.get('taninos_tecnico')
            acidez = quiz_answers.get('acidez_tecnico')
            
            # Quiere blanco/fresco
            if cuerpo == 'A' and taninos == 'A' and acidez == 'C':
                wants_white_fresh = True
            # Quiere tintos
            if cuerpo in ['B', 'C'] or taninos in ['B', 'C']:
                wants_red = True
            # Quiere asado
            if cuerpo == 'C' and taninos == 'C':
                wants_asado = True
                wants_red = True
                
        # Rango de precio
        precio_r = quiz_answers.get('precio', 'Más de $50')
        if precio_r in ['Menos de $10', '$10 - $20']:
            wants_price_value = True
        if precio_r == 'Más de $50':
            wants_premium = True
    else:
        # Heurísticas puramente sensoriales
        acidez = user_profile_series.get('acidez', 0.5)
        cuerpo = user_profile_series.get('cuerpo', 0.5)
        taninos = user_profile_series.get('taninos', 0.5)
        
        if acidez > 0.52 and cuerpo < 0.48 and taninos < 0.48:
            wants_white_fresh = True
        elif cuerpo > 0.52 or taninos > 0.52:
            wants_red = True
            if cuerpo > 0.62 and taninos > 0.58:
                wants_asado = True

    # Si hay contradicciones o neutralidad absoluta, permitir exploración
    allows_exploration = (user_profile_series.get('cuerpo', 0.5) == 0.5)

    return {
        "wants_white_fresh": wants_white_fresh,
        "wants_red": wants_red,
        "wants_asado": wants_asado,
        "wants_price_value": wants_price_value,
        "wants_premium": wants_premium,
        "allows_exploration": allows_exploration
    }

def get_recommendations(user_profile, price_filter, user_responses=None):
    """
    Genera recomendaciones de vinos personalizadas utilizando el perfil adaptativo del usuario.
    Aplica restricciones de intención semántica comercial y diversidad en tres pasadas de relajación.
    """
    client_id = session.get('client_id')
    current_wines = wine_profiles
    if client_id:
        client_catalog = load_client_catalog(client_id)
        if not client_catalog.empty:
            current_wines = client_catalog
            
    if current_wines.empty:
        return []

    user_responses = user_responses or {}
    is_regalo = (user_responses.get('intencion') == 'para_regalar')
    no_sabe_gustos = is_regalo and (user_responses.get('regalo_conoce_gustos') == 'no')
    color_pref = user_responses.get('regalo_color_pref', 'no_se')

    # 1. Calcular similitud coseno sensorial en 19 dimensiones
    wine_attributes = current_wines[ATTRIBUTE_COLUMNS].fillna(0.0)
    similarity = cosine_similarity(user_profile, wine_attributes)[0]

    wines_evaluated = current_wines.copy()
    wines_evaluated['sensory_similarity'] = similarity

    # Normalizar la similitud sensorial
    max_sensory_similarity = wines_evaluated['sensory_similarity'].max()
    if max_sensory_similarity > 0:
        wines_evaluated['sensory_similarity'] = wines_evaluated['sensory_similarity'] / max_sensory_similarity

    # 2. Filtrar por polaridad negativa fuerte
    if 'polarity' not in wines_evaluated.columns:
        wines_evaluated['polarity'] = 0.0
    filtered_wines = wines_evaluated[wines_evaluated['polarity'] > -0.2].copy()

    if filtered_wines.empty:
        return []

    # 3. Asignar Scores Argentinos a todos los candidatos
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

    filtered_wines['sentiment_score'] = (filtered_wines['polarity'] + 1.0) / 2.0
    filtered_wines['price_fit_score'] = 1.0

    # Inferencia de intención comercial
    intent = infer_commercial_intent(user_responses, user_profile)

    # Si busca relación precio-calidad, elevar su ponderación
    w_sensory = 0.55
    w_sentiment = 0.20
    w_argentine = 0.15
    w_price = 0.10
    
    if intent["wants_price_value"]:
        w_sensory = 0.40
        w_sentiment = 0.15
        w_argentine = 0.15
        w_price = 0.30  # Priorizar el ajuste y rendimiento comercial

    # FÓRMULA FINAL PONDERADA:
    filtered_wines['final_score'] = (
        w_sensory * filtered_wines['sensory_similarity'] +
        w_sentiment * filtered_wines['sentiment_score'] +
        w_argentine * filtered_wines['argentine_palate_score'] +
        w_price * filtered_wines['price_fit_score']
    )

    # Ordenar todos los candidatos
    sorted_wines = filtered_wines.sort_values(by='final_score', ascending=False)

    recommendations = []
    seen_titles = set()
    variety_counts = {}
    winery_counts = {}
    user_profile_series = user_profile.iloc[0]

    # --- PASADA 1: Filtro de Precio Estricto e Intención Estricta ---
    price_min, price_max = price_filter
    for idx, row in sorted_wines.iterrows():
        if len(recommendations) >= 15:
            break

        # A. Filtro de precio estricto de la Pasada 1
        price = float(row.get('price', 0))
        if price < price_min or price > price_max:
            continue

        raw_title = row.get('title', 'Vino sin Título')
        clean_title = str(raw_title).replace("Recomendación Similar a: ", "").replace("Recomendación Similar a:", "").strip()
        
        if clean_title.lower() in seen_titles:
            continue
            
        variedad = row.get('variedad', 'Unknown')
        if pd.isna(variedad) or str(variedad).strip().lower() in ['unknown', 'variedad desconocida', 'unknown variety']:
            variedad = extract_variedad_from_title(clean_title)
            
        winery = extract_winery_from_title(clean_title)
        variedad_lower = variedad.lower()

        # B. Reglas de Regalo sin Saber Gustos (Evitar perfiles extremos)
        if no_sabe_gustos:
            acidez = float(row.get('acidez', 0.5))
            taninos = float(row.get('taninos', 0.5))
            dulzor = float(row.get('dulzor', 0.5))
            if acidez > 0.75:
                continue
            if taninos > 0.75:
                continue
            if dulzor > 0.75:
                continue

        # C. Filtrado Estricto de Color para Regalos
        if is_regalo and color_pref != 'no_se':
            is_white = any(w in variedad_lower for w in ['chardonnay', 'sauvignon', 'torrontes', 'torrontés', 'pinot grigio', 'chenin', 'semillon', 'semillón', 'viognier']) or 'blanco' in clean_title.lower()
            is_sparkling = any(s in variedad_lower or s in clean_title.lower() for s in ['sparkling', 'espumante', 'brut', 'champagne', 'extra brut', 'prosecco'])
            is_rose = 'rosé' in variedad_lower or 'rose' in variedad_lower or 'rosado' in clean_title.lower() or 'rose' in clean_title.lower()
            is_red = not is_white and not is_sparkling and not is_rose

            if color_pref == 'tinto' and not is_red:
                continue
            elif color_pref == 'blanco' and not is_white:
                continue
            elif color_pref == 'rosado_espumante' and not (is_rose or is_sparkling):
                continue

        # Diversidad
        if len(recommendations) < 5 and variedad_lower in ['unknown', 'variedad desconocida', 'unknown variety']:
            continue
        if len(recommendations) < 5 and variety_counts.get(variedad_lower, 0) >= 2:
            continue
        if len(recommendations) < 5 and winery_counts.get(winery.lower(), 0) >= 2:
            continue

        # Restricciones de estilo estrictas (Pasada 1)
        if len(recommendations) < 5 and not is_regalo:
            if intent["wants_white_fresh"]:
                is_fresh = any(f in variedad_lower for f in white_fresh_varieties) or any(l in variedad_lower for l in light_red_varieties)
                if not is_fresh:
                    continue
                if 'malbec' in variedad_lower:
                    malbecs_top5 = sum(1 for w in recommendations if 'malbec' in w['variedad'].lower())
                    if malbecs_top5 >= 1:
                        continue
            elif intent["wants_red"]:
                is_white = any(w_v in variedad_lower for w_v in white_fresh_varieties)
                if is_white:
                    continue
            if intent["wants_asado"]:
                is_structured = any(s_v in variedad_lower for s_v in structured_red_varieties)
                if not is_structured:
                    continue
                if 'malbec' in variedad_lower:
                    malbecs_top5 = sum(1 for w in recommendations if 'malbec' in w['variedad'].lower())
                    if malbecs_top5 >= 3:
                        continue
            else:
                if 'malbec' in variedad_lower:
                    malbecs_top5 = sum(1 for w in recommendations if 'malbec' in w['variedad'].lower())
                    if malbecs_top5 >= 2:
                        continue

        # Agregar
        seen_titles.add(clean_title.lower())
        variety_counts[variedad_lower] = variety_counts.get(variedad_lower, 0) + 1
        winery_counts[winery.lower()] = winery_counts.get(winery.lower(), 0) + 1

        wine_data = build_wine_data_record(row, clean_title, variedad, winery, user_profile_series, user_responses, intent_relaxed=False)
        # Identificar regalo versátil
        if no_sabe_gustos or (is_regalo and any(v in variedad_lower for v in ['malbec', 'cabernet', 'blend', 'chardonnay', 'brut'])):
            wine_data['gift_safe'] = True
        else:
            wine_data['gift_safe'] = False
        recommendations.append(wine_data)

    # --- PASADA 2: Relajación de Rango de Precio con Intención Estricta ---
    if len(recommendations) < 15:
        for idx, row in sorted_wines.iterrows():
            if len(recommendations) >= 15:
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

            # Reglas de regalo sin saber gustos
            if no_sabe_gustos:
                acidez = float(row.get('acidez', 0.5))
                taninos = float(row.get('taninos', 0.5))
                dulzor = float(row.get('dulzor', 0.5))
                if acidez > 0.75:
                    continue
                if taninos > 0.75:
                    continue
                if dulzor > 0.75:
                    continue

            # Filtrado Estricto de Color para Regalos
            if is_regalo and color_pref != 'no_se':
                is_white = any(w in variedad_lower for w in ['chardonnay', 'sauvignon', 'torrontes', 'torrontés', 'pinot grigio', 'chenin', 'semillon', 'semillón', 'viognier']) or 'blanco' in clean_title.lower()
                is_sparkling = any(s in variedad_lower or s in clean_title.lower() for s in ['sparkling', 'espumante', 'brut', 'champagne', 'extra brut', 'prosecco'])
                is_rose = 'rosé' in variedad_lower or 'rose' in variedad_lower or 'rosado' in clean_title.lower() or 'rose' in clean_title.lower()
                is_red = not is_white and not is_sparkling and not is_rose

                if color_pref == 'tinto' and not is_red:
                    continue
                elif color_pref == 'blanco' and not is_white:
                    continue
                elif color_pref == 'rosado_espumante' and not (is_rose or is_sparkling):
                    continue

            # Diversidad y Restricciones duras de intención en Top 5 (mantener estrictas de estilo)
            if len(recommendations) < 5 and not is_regalo:
                if variedad_lower in ['unknown', 'variedad desconocida', 'unknown variety']:
                    continue
                if variety_counts.get(variedad_lower, 0) >= 2:
                    continue
                if winery_counts.get(winery.lower(), 0) >= 2:
                    continue
                
                # Reglas estrictas de Estilo (incluso con precio relajado)
                if intent["wants_white_fresh"]:
                    is_fresh = any(f in variedad_lower for f in white_fresh_varieties) or any(l in variedad_lower for l in light_red_varieties)
                    if not is_fresh:
                        continue  # Nunca meter Cabernet en blancos
                elif intent["wants_red"] or intent["wants_asado"]:
                    is_white = any(w_v in variedad_lower for w_v in white_fresh_varieties)
                    if is_white:
                        continue  # Nunca meter Torrontés en tintos/asados

            # Registrar
            seen_titles.add(clean_title.lower())
            variety_counts[variedad_lower] = variety_counts.get(variedad_lower, 0) + 1
            winery_counts[winery.lower()] = winery_counts.get(winery.lower(), 0) + 1

            wine_data = build_wine_data_record(row, clean_title, variedad, winery, user_profile_series, user_responses, intent_relaxed=True)
            if no_sabe_gustos or (is_regalo and any(v in variedad_lower for v in ['malbec', 'cabernet', 'blend', 'chardonnay', 'brut'])):
                wine_data['gift_safe'] = True
            else:
                wine_data['gift_safe'] = False
            recommendations.append(wine_data)

    # --- PASADA 3: Relajación Total Absoluta (Último recurso de inventario) ---
    if len(recommendations) < 15:
        for idx, row in sorted_wines.iterrows():
            if len(recommendations) >= 15:
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

            # Reglas de regalo sin saber gustos
            if no_sabe_gustos:
                acidez = float(row.get('acidez', 0.5))
                taninos = float(row.get('taninos', 0.5))
                dulzor = float(row.get('dulzor', 0.5))
                if acidez > 0.75:
                    continue
                if taninos > 0.75:
                    continue
                if dulzor > 0.75:
                    continue

            # Filtrado Estricto de Color para Regalos
            if is_regalo and color_pref != 'no_se':
                is_white = any(w in variedad_lower for w in ['chardonnay', 'sauvignon', 'torrontes', 'torrontés', 'pinot grigio', 'chenin', 'semillon', 'semillón', 'viognier']) or 'blanco' in clean_title.lower()
                is_sparkling = any(s in variedad_lower or s in clean_title.lower() for s in ['sparkling', 'espumante', 'brut', 'champagne', 'extra brut', 'prosecco'])
                is_rose = 'rosé' in variedad_lower or 'rose' in variedad_lower or 'rosado' in clean_title.lower() or 'rose' in clean_title.lower()
                is_red = not is_white and not is_sparkling and not is_rose

                if color_pref == 'tinto' and not is_red:
                    continue
                elif color_pref == 'blanco' and not is_white:
                    continue
                elif color_pref == 'rosado_espumante' and not (is_rose or is_sparkling):
                    continue

            seen_titles.add(clean_title.lower())
            wine_data = build_wine_data_record(row, clean_title, variedad, winery, user_profile_series, user_responses, intent_relaxed=True)
            if no_sabe_gustos or (is_regalo and any(v in variedad_lower for v in ['malbec', 'cabernet', 'blend', 'chardonnay', 'brut'])):
                wine_data['gift_safe'] = True
            else:
                wine_data['gift_safe'] = False
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

def build_wine_data_record(row, clean_title, variedad, winery, user_profile_series, user_responses, intent_relaxed=False):
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

    wine_id_val = row.get('wine_id', 0)
    try:
        wine_id_val = int(wine_id_val)
    except ValueError:
        wine_id_val = str(wine_id_val)

    return {
        'wine_id': wine_id_val,
        'title': clean_title,
        'price': formatted_price,
        'variedad': variedad,
        'winery': winery,
        'sku': row.get('sku', ''),
        'vintage': row.get('vintage', ''),
        'region': row.get('region', ''),
        'stock': int(row.get('stock', 0)) if pd.notna(row.get('stock')) else 0,
        'image_url': row.get('image_url', ''),
        'product_url': row.get('product_url', ''),
        'description': row.get('description', ''),
        'tags': row.get('tags', ''),
        'intent_relaxed': bool(intent_relaxed),
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

# --- RUTAS MULTI-CLIENTE Y ANALÍTICAS ---

@app.route('/c/<client_slug>')
def client_landing(client_slug):
    client_config = get_client_config(client_slug)
    if not client_config:
        return "Cliente no encontrado", 404
        
    # Inicializar sesión limpia para este cliente
    session['client_id'] = client_slug
    session['session_id'] = str(uuid.uuid4())
    session.pop('answers', None)
    session.pop('current_step', None)
    session.pop('completed_tracked', None)
    
    # Registrar evento quiz_started
    track_event(client_slug, 'quiz_started', session['session_id'])
    
    return render_template('client_landing.html', client=client_config)

@app.route('/c/<client_slug>/quiz')
def client_quiz_start(client_slug):
    client_config = get_client_config(client_slug)
    if not client_config:
        return "Cliente no encontrado", 404
        
    session['client_id'] = client_slug
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
        track_event(client_slug, 'quiz_started', session['session_id'])
        
    # Reiniciar estados del quiz
    session.pop('answers', None)
    session.pop('current_step', None)
    session.pop('completed_tracked', None)
    return redirect(url_for('quiz'))

@app.route('/c/<client_slug>/results')
def client_results(client_slug):
    client_config = get_client_config(client_slug)
    if not client_config:
        return "Cliente no encontrado", 404
        
    session['client_id'] = client_slug
    return redirect(url_for('results'))

@app.route('/track/click/<client_slug>/<wine_sku>')
def track_wine_click(client_slug, wine_sku):
    client_config = get_client_config(client_slug)
    if not client_config:
        return "Cliente no encontrado", 404
        
    session_id = session.get('session_id')
    
    # Cargar catálogo del cliente para obtener la URL de producto
    catalog = load_client_catalog(client_slug)
    target_url = client_config['ecommerce_url']
    wine_title = "Vino Desconocido"
    
    if not catalog.empty:
        wine_row = catalog[catalog['sku'] == wine_sku]
        if not wine_row.empty:
            target_url = wine_row.iloc[0].get('product_url', target_url)
            wine_title = wine_row.iloc[0].get('title', wine_title)
            
    # Registrar evento
    track_event(client_slug, 'wine_clicked', session_id, payload={
        'wine_sku': wine_sku,
        'wine_title': wine_title
    })
    
    return redirect(target_url)

@app.route('/track/whatsapp/<client_slug>/<wine_sku>')
def track_whatsapp_click(client_slug, wine_sku):
    client_config = get_client_config(client_slug)
    if not client_config:
        return "Cliente no encontrado", 404
        
    session_id = session.get('session_id')
    whatsapp_num = client_config.get('whatsapp_number', '')
    
    catalog = load_client_catalog(client_slug)
    wine_title = "un vino del catálogo"
    if not catalog.empty:
        wine_row = catalog[catalog['sku'] == wine_sku]
        if not wine_row.empty:
            wine_title = wine_row.iloc[0].get('title', wine_title)
            
    # Registrar evento
    track_event(client_slug, 'whatsapp_clicked', session_id, payload={
        'wine_sku': wine_sku,
        'wine_title': wine_title
    })
    
    # Construir enlace de WhatsApp con mensaje predeterminado
    import urllib.parse
    message = f"Hola! Realicé el quiz de Descorcha.IA y me interesa comprar/consultar por el vino: {wine_title} (SKU: {wine_sku})."
    encoded_message = urllib.parse.quote(message)
    whatsapp_url = f"https://wa.me/{whatsapp_num}?text={encoded_message}"
    
    return redirect(whatsapp_url)

@app.route('/track/feedback/<client_slug>/<feedback_type>', methods=['POST'])
def track_feedback(client_slug, feedback_type):
    client_config = get_client_config(client_slug)
    if not client_config:
        return {"status": "error", "message": "Cliente no encontrado"}, 404
        
    session_id = session.get('session_id')
    event = 'feedback_like' if feedback_type == 'like' else 'feedback_dislike'
    
    track_event(client_slug, event, session_id)
    return {"status": "success", "event_tracked": event}

@app.route('/admin/<client_slug>/dashboard')
def client_dashboard(client_slug):
    client_config = get_client_config(client_slug)
    if not client_config:
        return "Cliente no encontrado", 404
        
    metrics = get_client_dashboard_metrics(client_slug)
    return render_template('client_dashboard.html', client=client_config, metrics=metrics)

@app.route('/commercial')
def commercial_landing():
    return render_template('commercial_landing.html')

if __name__ == '__main__':
    app.run(debug=True)
