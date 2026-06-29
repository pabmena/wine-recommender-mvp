import numpy as np
from config.taste_mapping import ATTRIBUTE_COLUMNS

MIN_QUESTIONS = 5
MAX_QUESTIONS = 10
CONFIDENCE_THRESHOLD = 0.72

def check_contradictions(answers):
    """
    Evalúa inconsistencias graves en las respuestas que reducen la confianza metodológica.
    """
    contradictions = 0
    cafe = answers.get('cafe_pref')
    choco = answers.get('chocolate_pref')
    asado = answers.get('asado_pref')
    citricos = answers.get('citricos_pref')
    manzana = answers.get('manzana_pref')
    especias = answers.get('especias_pref')
    ref_acidez = answers.get('ref_acidez')
    
    # 1. Contradicción café/chocolate suave y dulce pero prefiere ahumado intenso
    if (cafe == 'A' or choco == 'A') and asado == 'C':
        contradictions += 1
        
    # 2. Contradicción evita cítricos pero prefiere manzana verde súper ácida
    if citricos == 'A' and manzana == 'C':
        contradictions += 1
        
    # 3. Contradicción evita cítricos pero prefiere acidez muy marcada en vinos
    if citricos == 'A' and ref_acidez == 'C':
        contradictions += 1
        
    # 4. Contradicción prefiere sabores suaves/dulces de chocolate blanco pero comidas muy especiadas/pimienta fuerte
    if choco == 'A' and especias == 'C':
        contradictions += 1
        
    return contradictions

def calculate_confidence(answers, user_profile, recommendations):
    """
    Calcula un score de confianza calibrado entre 0.0 y 1.0.
    1. Especificidad de respuestas: penaliza a la mitad las respuestas cotidianas neutrales.
    2. Fuerza del perfil: desviación media de los atributos modificados.
    3. Margen de recomendación: diferenciación en match rate del top 8.
    4. Cobertura de atributos clave.
    Bonus especial: +0.20 para nivel avanzado técnico y +0.10 por completar fase inicial.
    Penaliza perfiles inconsistentes o contradictorios.
    """
    if not answers:
        return 0.0

    total_non_calib_answers = sum(1 for q in answers if q != 'conocimiento')
    if total_non_calib_answers <= 0:
        return 0.0
    
    is_advanced = answers.get('conocimiento') == 'avanzado'
    if is_advanced:
        answer_specificity = 0.95
    else:
        neutral_count = sum(1 for q, val in answers.items() if val == 'B' and q in ['cafe_pref', 'chocolate_pref', 'citricos_pref'])
        answer_specificity = (total_non_calib_answers - 0.4 * neutral_count) / total_non_calib_answers

    # 2. Fuerza del perfil (desviación de 0.5)
    user_vals = user_profile.iloc[0].values
    deviations = np.abs(user_vals - 0.5)
    modified_deviations = deviations[deviations > 0.0]
    
    if len(modified_deviations) > 0:
        profile_strength = min(1.0, np.mean(modified_deviations) * 2.5)
    else:
        profile_strength = 0.0

    # 3. Margen de recomendación (separación de puntuaciones de match)
    if len(recommendations) >= 8:
        score_1 = recommendations[0]['match_rate'] / 100.0
        score_8 = recommendations[-1]['match_rate'] / 100.0
        margin = score_1 - score_8
        recommendation_margin = min(1.0, margin * 4.0)
    else:
        recommendation_margin = 0.0

    # 4. Cobertura de atributos clave (11 atributos principales)
    key_attrs = [
        'frutas_rojas', 'frutas_negras', 'frutas_cítricas', 'frutas_tropicales', 
        'frutas_hueso', 'especias', 'madera_y_otros', 'acidez', 'taninos', 'cuerpo', 'dulzor'
    ]
    altered_key_attrs = sum(1 for attr in key_attrs if user_profile.iloc[0][attr] != 0.5)
    attribute_coverage = altered_key_attrs / len(key_attrs)

    # Fórmula ponderada recalibrada:
    confidence_score = (
        0.35 * answer_specificity +
        0.35 * profile_strength +
        0.15 * recommendation_margin +
        0.15 * attribute_coverage
    )

    # Bonificaciones por calidad metodológica
    if is_advanced:
        confidence_score += 0.20
    if total_non_calib_answers >= 5:
        confidence_score += 0.10

    # Penalización especial para perfiles neutros/vagos (Perfil E de principiantes)
    if not is_advanced and total_non_calib_answers == 5 and neutral_count >= 3:
        confidence_score = min(0.45, confidence_score)

    # Penalización por contradicción
    contradictions = check_contradictions(answers)
    if contradictions > 0:
        confidence_score -= 0.25 * contradictions
        # Forzar a zona Inicial/Exploratoria si hay contradicciones
        confidence_score = min(0.48, confidence_score)

    return min(1.0, max(0.0, confidence_score))

def should_continue_quiz(answers, user_profile, recommendations):
    """
    Decide si el quiz interactivo adaptativo debe continuar preguntando al usuario
    o si la confianza es suficiente.
    """
    # Contar cuántas respuestas de preguntas reales tenemos (excluyendo la de calibración)
    real_questions_answered = sum(1 for q in answers if q != 'conocimiento')
    
    if real_questions_answered < 5:
        return True, 0.0

    confidence = calculate_confidence(answers, user_profile, recommendations)

    # Si supera el umbral de confianza, se detiene
    if confidence >= CONFIDENCE_THRESHOLD:
        return False, confidence

    # Si supera el límite de 9 preguntas reales de sabor (5 base + 4 refinamiento), se detiene
    if real_questions_answered >= 9:
        return False, confidence

    return True, confidence

def choose_next_question(answers, user_profile):
    """
    Identifica cuál es el atributo de sabor con mayor incertidumbre (más cercano a 0.5)
    entre los atributos clave y devuelve el ID de la pregunta de refinamiento correspondiente.
    """
    key_attrs = ['acidez', 'taninos', 'cuerpo', 'madera_y_otros', 'dulzor']
    
    # Atributos ya cubiertos por refinamientos previos para no repetir
    already_asked = [
        'acidez' if 'ref_acidez' in answers else None,
        'taninos' if 'ref_taninos' in answers else None,
        'cuerpo' if 'ref_cuerpo' in answers else None,
        'madera_y_otros' if 'ref_madera' in answers else None,
        'dulzor' if 'ref_dulzor' in answers else None
    ]
    already_asked = [x for x in already_asked if x is not None]

    profile_series = user_profile.iloc[0]
    uncertainty_list = []
    
    for attr in key_attrs:
        if attr not in already_asked:
            val = profile_series.get(attr, 0.5)
            # Incertidumbre es 1 - (distancia absoluta a 0.5 * 2).
            uncertainty = 1.0 - (abs(val - 0.5) * 2.0)
            uncertainty_list.append((attr, uncertainty))

    if uncertainty_list:
        uncertainty_list.sort(key=lambda x: x[1], reverse=True)
        weakest_attr = uncertainty_list[0][0]
        
        refinement_ids = {
            'acidez': 'ref_acidez',
            'taninos': 'ref_taninos',
            'cuerpo': 'ref_cuerpo',
            'madera_y_otros': 'ref_madera',
            'dulzor': 'ref_dulzor'
        }
        return refinement_ids.get(weakest_attr, 'ref_acidez')
    
    return 'ref_acidez'

def get_display_confidence(raw_confidence_score):
    """
    Devuelve la confianza capada a máximo 95% para exposición visual,
    su label comercial (Alto, Medio, Exploratorio) y el copy recomendado.
    """
    display_conf = min(raw_confidence_score, 0.95)
    
    if raw_confidence_score >= 0.72:
        confidence_label = "Alto"
        copy = "Conocimos muy bien tu perfil de sabor."
    elif raw_confidence_score >= 0.50:
        confidence_label = "Medio"
        copy = "Tenemos una buena aproximación a tu paladar."
    else:
        confidence_label = "Exploratorio"
        copy = "Estas recomendaciones son una primera aproximación. Podés afinarlas más adelante."
        
    return display_conf, confidence_label, copy
