# Mapeo de Gustos Cotidianos y Técnicos a Atributos de Vinos (19 Dimensiones)

ATTRIBUTE_COLUMNS = [
    'frutas_rojas',
    'frutas_negras',
    'frutas_cítricas',
    'frutas_tropicales',
    'frutas_hueso',
    'frutas_secas',
    'especias',
    'notas_herbales_frescas',
    'notas_herbales_secas',
    'notas_florales',
    'notas_terrosas',
    'madera_y_otros',
    'dulzor',
    'acidez',
    'cuerpo',
    'taninos',
    'alcohol',
    'finalizacion',
    'umami_y_otros'
]

# Pregunta 1: Filtro de Calibración Adaptativa
QUESTION_CALIBRATION = {
    'id': 'conocimiento',
    'text': '¿Cuánto sabes de vinos y qué lenguaje prefieres para el quiz?',
    'type': 'single_choice',
    'options': [
        {'label': 'Prefiero preguntas de comidas y gustos cotidianos (Modelo Tastry)', 'value': 'principiante'},
        {'label': 'Sé algo y prefiero preguntas técnicas sobre estilos de vino (Avanzado)', 'value': 'avanzado'}
    ]
}

# Preguntas base según el perfil de conocimiento seleccionado
QUESTIONS_BY_LEVEL = {
    'principiante': [
        {
            'id': 'cafe_pref',
            'text': 'Cuando tomas café o té negro, ¿cómo lo prefieres?',
            'type': 'single_choice',
            'options': [
                {'label': 'Suave, con bastante leche y azúcar', 'value': 'A'},
                {'label': 'Equilibrado, con un toque moderado de azúcar o leche', 'value': 'B'},
                {'label': 'Intenso, negro y completamente sin azúcar', 'value': 'C'},
                {'label': 'No tomo café ni té negro', 'value': 'D'}
            ]
        },
        {
            'id': 'chocolate_pref',
            'text': '¿Qué tipo de chocolate disfrutas más?',
            'type': 'single_choice',
            'options': [
                {'label': 'Chocolate blanco o muy dulce y cremoso', 'value': 'A'},
                {'label': 'Chocolate con leche tradicional', 'value': 'B'},
                {'label': 'Chocolate negro amargo (70% de cacao o más)', 'value': 'C'},
                {'label': 'No me gusta o no consumo chocolate', 'value': 'D'}
            ]
        },
        {
            'id': 'citricos_pref',
            'text': '¿Qué tanto disfrutas de los sabores cítricos intensos (como el limón exprimido, lima o pomelo)?',
            'type': 'single_choice',
            'options': [
                {'label': 'Poco o nada, los encuentro demasiado ácidos o ásperos', 'value': 'A'},
                {'label': 'Moderadamente, me resultan agradables y frescos', 'value': 'B'},
                {'label': 'Mucho, me encantan las sensaciones ácidas y vibrantes', 'value': 'C'}
            ]
        },
        {
            'id': 'asado_pref',
            'text': '¿Te gusta el olor y sabor a humo de leña, fogatas, barbacoa o asado?',
            'type': 'single_choice',
            'options': [
                {'label': 'Evito las cosas ahumadas o con notas quemadas', 'value': 'A'},
                {'label': 'Moderado, me resultan indiferentes o agradables con sutileza', 'value': 'B'},
                {'label': 'Mucho, me fascinan el aroma a leña y los sabores ahumados intensos', 'value': 'C'}
            ]
        },
        {
            'id': 'hongos_pref',
            'text': '¿Qué opinas de los hongos frescos, trufas, el olor a tierra mojada o bosque húmedo?',
            'type': 'single_choice',
            'options': [
                {'label': 'No me gustan los hongos ni los aromas terrosos', 'value': 'A'},
                {'label': 'Moderado, los consumo si están bien integrados', 'value': 'B'},
                {'label': 'Me fascinan los hongos, trufas y aromas a bosque y tierra mojada', 'value': 'C'}
            ]
        },
        {
            'id': 'manzana_pref',
            'text': 'Cuando comes manzanas, ¿cuál prefieres?',
            'type': 'single_choice',
            'options': [
                {'label': 'Manzana roja, dulce, suave y arenosa (Baja acidez)', 'value': 'A'},
                {'label': 'Me da igual o me gustan ambas por igual', 'value': 'B'},
                {'label': 'Manzana verde, ácida, crujiente y vibrante (Alta acidez)', 'value': 'C'}
            ]
        },
        {
            'id': 'especias_pref',
            'text': '¿Qué tal te llevas con la pimienta negra molida o las especias fuertes en las comidas?',
            'type': 'single_choice',
            'options': [
                {'label': 'Las evito por completo, prefiero comidas suaves', 'value': 'A'},
                {'label': 'Moderado, tolero un toque de pimienta o pimentón', 'value': 'B'},
                {'label': 'Me encantan la pimienta negra molida y las comidas bien especiadas', 'value': 'C'}
            ]
        }
    ],
    'avanzado': [
        {
            'id': 'cuerpo_tecnico',
            'text': '¿Qué nivel de cuerpo y volumen prefieres en boca en un vino?',
            'type': 'single_choice',
            'options': [
                {'label': 'Cuerpo ligero, fluido y fácil de tomar', 'value': 'A'},
                {'label': 'Cuerpo medio, equilibrado y con buena presencia', 'value': 'B'},
                {'label': 'Vinos con mucho cuerpo, robustos y estructurados', 'value': 'C'}
            ]
        },
        {
            'id': 'madera_tecnico',
            'text': '¿Cuál es tu preferencia respecto al paso por barricas de roble (madera)?',
            'type': 'single_choice',
            'options': [
                {'label': 'Vinos jóvenes y frutados sin madera', 'value': 'A'},
                {'label': 'Presencia sutil de madera, que acompañe a la fruta', 'value': 'B'},
                {'label': 'Crianza prolongada con notas de vainilla, cacao, coco o ahumados', 'value': 'C'}
            ]
        },
        {
            'id': 'taninos_tecnico',
            'text': '¿Cómo te gusta la sensación táctil y astringencia de los taninos?',
            'type': 'single_choice',
            'options': [
                {'label': 'Taninos muy suaves, redondos y pulidos', 'value': 'A'},
                {'label': 'Taninos presentes que den estructura sin ser agresivos', 'value': 'B'},
                {'label': 'Taninos firmes, potentes y bien estructurados', 'value': 'C'}
            ]
        },
        {
            'id': 'acidez_tecnico',
            'text': '¿Qué perfil de acidez buscas en un vino?',
            'type': 'single_choice',
            'options': [
                {'label': 'Acidez baja, que sea sedoso y amable', 'value': 'A'},
                {'label': 'Acidez media, fresca y equilibrada', 'value': 'B'},
                {'label': 'Acidez alta, muy fresca, crujiente y vibrante', 'value': 'C'}
            ]
        },
        {
            'id': 'dulzor_tecnico',
            'text': '¿Cuál es tu nivel de azúcar residual preferido en el vino?',
            'type': 'single_choice',
            'options': [
                {'label': 'Completamente seco (sin rastros dulces)', 'value': 'A'},
                {'label': 'Abocado o semi-seco (con una leve sensación amable)', 'value': 'B'},
                {'label': 'Dulce natural o de cosecha tardía', 'value': 'C'}
            ]
        }
    ]
}

# Preguntas de Refinamiento Extra (para baja confianza)
QUESTIONS_REFINEMENT = {
    'acidez': {
        'id': 'ref_acidez',
        'text': 'Cuando consumes frutas frescas, ¿prefieres una manzana verde ácida y crocante o una roja dulce y arenosa?',
        'type': 'single_choice',
        'options': [
            {'label': 'Definitivamente la roja, dulce y suave (Prefiero baja acidez)', 'value': 'A'},
            {'label': 'Me es indiferente', 'value': 'B'},
            {'label': 'La verde, bien ácida y refrescante (Prefiero alta acidez)', 'value': 'C'}
        ]
    },
    'taninos': {
        'id': 'ref_taninos',
        'text': '¿Disfrutas del sabor amargo y seco del mate amargo, el té negro fuerte o el agua tónica?',
        'type': 'single_choice',
        'options': [
            {'label': 'No, los evito por completo (Prefiero vinos sin astringencia)', 'value': 'A'},
            {'label': 'Me gustan con moderación', 'value': 'B'},
            {'label': 'Sí, me encantan esos sabores amargos y secos (Prefiero taninos firmes)', 'value': 'C'}
        ]
    },
    'cuerpo': {
        'id': 'ref_cuerpo',
        'text': 'En tus bebidas en general, ¿prefieres texturas ligeras como un agua frutal o densas y con peso en boca?',
        'type': 'single_choice',
        'options': [
            {'label': 'Ligeras, refrescantes y rápidas de beber (Vino ligero)', 'value': 'A'},
            {'label': 'Neutras', 'value': 'B'},
            {'label': 'Con buena textura, densas y persistentes (Vino con cuerpo)', 'value': 'C'}
        ]
    },
    'madera_y_otros': {
        'id': 'ref_madera',
        'text': '¿Te atraen los aromas de coco tostado, fogata de leña, vainilla dulce o el olor a cuero?',
        'type': 'single_choice',
        'options': [
            {'label': 'Prefiero aromas puramente limpios y afrutados (Vinos jóvenes)', 'value': 'A'},
            {'label': 'Me resultan agradables en baja cantidad', 'value': 'B'},
            {'label': 'Me fascinan, me parecen aromas complejos y profundos (Vinos con madera)', 'value': 'C'}
        ]
    },
    'dulzor': {
        'id': 'ref_dulzor',
        'text': '¿Qué tan fanático eres de los postres muy dulces como el dulce de leche o flan con caramelo?',
        'type': 'single_choice',
        'options': [
            {'label': 'No me gustan las cosas muy empalagosas (Vinos muy secos)', 'value': 'A'},
            {'label': 'Me gustan con moderación o equilibrados', 'value': 'B'},
            {'label': 'Me encantan las cosas bien dulces (Vinos dulces)', 'value': 'C'}
        ]
    }
}

# Diccionario de pesos para actualizar el perfil base (inicializado en 0.5)
TASTE_MAPPING = {
    # Nivel Principiante (Modelo Tastry)
    'cafe_pref': {
        'A': {'taninos': -0.3, 'cuerpo': -0.2, 'dulzor': 0.2, 'finalizacion': -0.1},
        'B': {},
        'C': {'taninos': 0.4, 'cuerpo': 0.3, 'dulzor': -0.3, 'finalizacion': 0.3},
        'D': {'taninos': -0.4, 'cuerpo': -0.2, 'dulzor': 0.1}
    },
    'chocolate_pref': {
        'A': {'dulzor': 0.4, 'taninos': -0.3, 'cuerpo': -0.2},
        'B': {'dulzor': 0.1, 'taninos': -0.1},
        'C': {'dulzor': -0.3, 'taninos': 0.4, 'cuerpo': 0.3, 'finalizacion': 0.2},
        'D': {}
    },
    'citricos_pref': {
        'A': {'acidez': -0.4, 'frutas_cítricas': -0.3},
        'B': {},
        'C': {'acidez': 0.4, 'frutas_cítricas': 0.4}
    },
    'asado_pref': {
        'A': {'madera_y_otros': -0.4, 'notas_terrosas': -0.2},
        'B': {},
        'C': {'madera_y_otros': 0.5, 'notas_terrosas': 0.2, 'taninos': 0.2, 'cuerpo': 0.3}
    },
    'hongos_pref': {
        'A': {'notas_terrosas': -0.4, 'umami_y_otros': -0.3},
        'B': {},
        'C': {'notas_terrosas': 0.5, 'umami_y_otros': 0.4, 'cuerpo': 0.2}
    },
    'manzana_pref': {
        'A': {'acidez': -0.4, 'dulzor': 0.2},
        'B': {},
        'C': {'acidez': 0.4, 'dulzor': -0.2}
    },
    'especias_pref': {
        'A': {'especias': -0.4, 'alcohol': -0.2},
        'B': {},
        'C': {'especias': 0.5, 'alcohol': 0.3, 'taninos': 0.2}
    },
    
    # Nivel Avanzado/Técnico
    'cuerpo_tecnico': {
        'A': {'cuerpo': -0.4, 'finalizacion': -0.2, 'alcohol': -0.2},
        'B': {'cuerpo': 0.0},
        'C': {'cuerpo': 0.4, 'finalizacion': 0.3, 'alcohol': 0.2}
    },
    'madera_tecnico': {
        'A': {'madera_y_otros': -0.4, 'notas_terrosas': -0.2, 'notas_florales': 0.2},
        'B': {'madera_y_otros': 0.1},
        'C': {'madera_y_otros': 0.5, 'notas_terrosas': 0.3}
    },
    'taninos_tecnico': {
        'A': {'taninos': -0.4, 'cuerpo': -0.1},
        'B': {'taninos': 0.1},
        'C': {'taninos': 0.4, 'cuerpo': 0.2}
    },
    'acidez_tecnico': {
        'A': {'acidez': -0.4},
        'B': {'acidez': 0.0},
        'C': {'acidez': 0.4}
    },
    'dulzor_tecnico': {
        'A': {'dulzor': -0.4},
        'B': {'dulzor': 0.1},
        'C': {'dulzor': 0.5}
    },
    
    # Refinamientos
    'ref_acidez': {
        'A': {'acidez': -0.3, 'frutas_cítricas': -0.2},
        'B': {},
        'C': {'acidez': 0.3, 'frutas_cítricas': 0.2}
    },
    'ref_taninos': {
        'A': {'taninos': -0.3},
        'B': {},
        'C': {'taninos': 0.3}
    },
    'ref_cuerpo': {
        'A': {'cuerpo': -0.3, 'finalizacion': -0.1},
        'B': {},
        'C': {'cuerpo': 0.3, 'finalizacion': 0.2}
    },
    'ref_madera': {
        'A': {'madera_y_otros': -0.3, 'notas_terrosas': -0.1},
        'B': {},
        'C': {'madera_y_otros': 0.3, 'notas_terrosas': 0.2}
    },
    'ref_dulzor': {
        'A': {'dulzor': -0.3},
        'B': {},
        'C': {'dulzor': 0.3}
    }
}
