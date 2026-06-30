# Mapeo de Gustos Cotidianos, Técnicos e Intenciones en Descorcha.IA

# Las 19 dimensiones del perfil sensorial de vinos
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

# 1. Preguntas Iniciales de Flujo B2B
QUESTIONS_INITIAL = {
    'intencion': {
        'id': 'intencion',
        'text': '¿Para quién es el vino que estás buscando?',
        'type': 'single_choice',
        'emoji': '🎁',
        'options': [
            {'label': 'Para mí', 'value': 'para_mi'},
            {'label': 'Para hacer un regalo', 'value': 'para_regalar'},
            {'label': 'Para compartir en una comida o reunión', 'value': 'comida'},
            {'label': 'Para un evento o regalo empresarial', 'value': 'evento'}
        ]
    },
    'conocimiento': {
        'id': 'conocimiento',
        'text': '¿Cómo describirías tu nivel de conocimiento sobre vinos?',
        'type': 'single_choice',
        'emoji': '🍷',
        'options': [
            {'label': 'Principiante (Prefiero sabores sencillos y cotidianos)', 'value': 'principiante'},
            {'label': 'Intermedio (Conozco algunas variedades y estilos comunes)', 'value': 'intermedio'},
            {'label': 'Avanzado (Disfruto detalles técnicos como barrica, acidez o taninos)', 'value': 'avanzado'}
        ]
    },
    'presupuesto': {
        'id': 'presupuesto',
        'text': '¿Qué presupuesto aproximado tenés por botella?',
        'type': 'single_choice',
        'emoji': '💵',
        'options': [
            {'label': 'Económico (Hasta $15.000)', 'value': 'bajo'},
            {'label': 'Medio ($15.000 a $35.000)', 'value': 'medio'},
            {'label': 'Premium (Más de $35.000)', 'value': 'alto'}
        ]
    }
}

# 2. Preguntas del Flujo Especial "Para Regalar"
QUESTIONS_REGALO = [
    {
        'id': 'regalo_conoce_gustos',
        'text': '¿Conocés los gustos de la persona que va a recibir el vino?',
        'type': 'single_choice',
        'emoji': '🤔',
        'options': [
            {'label': 'Sí, sé qué estilos prefiere', 'value': 'si'},
            {'label': 'No, prefiero ir a lo seguro y confiable', 'value': 'no'}
        ]
    },
    {
        'id': 'regalo_color_pref',
        'text': '¿Prefiere algún tipo de vino en particular?',
        'type': 'single_choice',
        'emoji': '🥂',
        'options': [
            {'label': 'Tinto', 'value': 'tinto'},
            {'label': 'Blanco', 'value': 'blanco'},
            {'label': 'Rosado o Espumante', 'value': 'rosado_espumante'},
            {'label': 'No sé, prefiero que decida la IA', 'value': 'no_se'}
        ]
    },
    {
        'id': 'regalo_conocimiento_destinatario',
        'text': '¿Cuál es el nivel de conocimiento del destinatario?',
        'type': 'single_choice',
        'emoji': '🎓',
        'options': [
            {'label': 'Principiante', 'value': 'principiante'},
            {'label': 'Intermedio', 'value': 'intermedio'},
            {'label': 'Avanzado', 'value': 'avanzado'},
            {'label': 'No estoy seguro', 'value': 'no_se'}
        ]
    },
    {
        'id': 'regalo_ocasion',
        'text': '¿Cuál es el motivo de este regalo?',
        'type': 'single_choice',
        'emoji': '🎂',
        'options': [
            {'label': 'Cumpleaños o Aniversario', 'value': 'cumple'},
            {'label': 'Agradecimiento o Cortesía', 'value': 'agradecimiento'},
            {'label': 'Regalo empresarial o institucional', 'value': 'empresa'},
            {'label': 'Celebración, cena o brindis informal', 'value': 'celebracion'}
        ]
    },
    {
        'id': 'regalo_estilo_etiqueta',
        'text': '¿Qué tipo de etiqueta estás buscando para el regalo?',
        'type': 'single_choice',
        'emoji': '🏷️',
        'options': [
            {'label': 'Una etiqueta clásica, segura y muy reconocida', 'value': 'clasico'},
            {'label': 'Algo original, boutique o con historia para contar', 'value': 'original'}
        ]
    },
    {
        'id': 'regalo_presupuesto',
        'text': '¿Qué presupuesto tenés pensado para el regalo?',
        'type': 'single_choice',
        'emoji': '💵',
        'options': [
            {'label': 'Económico (Hasta $15.000)', 'value': 'bajo'},
            {'label': 'Medio ($15.000 a $35.000)', 'value': 'medio'},
            {'label': 'Premium (Más de $35.000)', 'value': 'alto'}
        ]
    }
]

# 3. Preguntas Sensoriales por Nivel (Tastry-like con 3 respuestas emocionales)
QUESTIONS_SENSORIALES = {
    'principiante': [
        {
            'id': 'cafe_intenso',
            'text': '¿Qué tanto te gusta el café solo, negro y sin azúcar (intenso)?',
            'emoji': '☕',
            'attribute_impact': {
                'taninos': 0.4,
                'cuerpo': 0.3,
                'dulzor': -0.3,
                'finalizacion': 0.2
            }
        },
        {
            'id': 'chocolate_amargo',
            'text': '¿Disfrutas del chocolate negro amargo (70% de cacao o más)?',
            'emoji': '🍫',
            'attribute_impact': {
                'taninos': 0.4,
                'cuerpo': 0.2,
                'dulzor': -0.2
            }
        },
        {
            'id': 'dulce_leche',
            'text': '¿Te encantan los postres muy dulces como el dulce de leche o caramelo?',
            'emoji': '🍮',
            'attribute_impact': {
                'dulzor': 0.5,
                'acidez': -0.3
            }
        },
        {
            'id': 'citricos_pomelo',
            'text': '¿Qué tanto disfrutas del pomelo rosado o la acidez del limón exprimido?',
            'emoji': '🍋',
            'attribute_impact': {
                'acidez': 0.4,
                'frutas_cítricas': 0.4
            }
        },
        {
            'id': 'asado_humo',
            'text': '¿Te fascina el aroma a leña, humo de fogata o asado a la parrilla?',
            'emoji': '🍖',
            'attribute_impact': {
                'madera_y_otros': 0.5,
                'notas_terrosas': 0.2,
                'cuerpo': 0.2
            }
        }
    ],
    
    'intermedio': [
        {
            'id': 'provoleta_leña',
            'text': '¿Te gusta la provoleta dorada a la chapa con hierbas frescas?',
            'emoji': '🧀',
            'attribute_impact': {
                'cuerpo': 0.3,
                'notas_herbales_frescas': 0.3,
                'umami_y_otros': 0.2
            }
        },
        {
            'id': 'pastas_tuco',
            'text': '¿Qué opinas de las pastas de domingo con tuco y pesto intenso?',
            'emoji': '🍝',
            'attribute_impact': {
                'acidez': 0.3,
                'notas_herbales_frescas': 0.3,
                'especias': 0.2
            }
        },
        {
            'id': 'picada_fiambres',
            'text': '¿Disfrutas de una picada con salamines, quesos duros y aceitunas?',
            'emoji': '🥖',
            'attribute_impact': {
                'taninos': 0.3,
                'cuerpo': 0.3,
                'alcohol': 0.2
            }
        },
        {
            'id': 'frutos_rojos_patagonia',
            'text': '¿Te encantan los frutos rojos de la Patagonia (moras, frambuesas)?',
            'emoji': '🍓',
            'attribute_impact': {
                'frutas_rojas': 0.5,
                'frutas_negras': 0.3
            }
        },
        {
            'id': 'yerba_mate_intensa',
            'text': '¿Te gusta tomar el mate amargo y bien cebado (yerba intensa)?',
            'emoji': '🧉',
            'attribute_impact': {
                'notas_herbales_secas': 0.4,
                'taninos': 0.3,
                'acidez': 0.2
            }
        }
    ],
    
    'avanzado': [
        {
            'id': 'cuerpo_robusto_tecnico',
            'text': '¿Preferís vinos con cuerpo robusto, pesado y estructurados en boca?',
            'emoji': '🏺',
            'attribute_impact': {
                'cuerpo': 0.5,
                'finalizacion': 0.3,
                'alcohol': 0.2
            }
        },
        {
            'id': 'madera_barrica_tecnico',
            'text': '¿Te gusta la crianza prolongada en barricas de roble (vainilla, cacao)?',
            'emoji': '🪵',
            'attribute_impact': {
                'madera_y_otros': 0.5,
                'notas_terrosas': 0.2
            }
        },
        {
            'id': 'taninos_firmes_tecnico',
            'text': '¿Disfrutás los taninos firmes, potentes y bien astringentes?',
            'emoji': '🍇',
            'attribute_impact': {
                'taninos': 0.5,
                'cuerpo': 0.2
            }
        },
        {
            'id': 'acidez_vibrante_tecnico',
            'text': '¿Buscás acidez crujiente, refrescante y bien alta en boca?',
            'emoji': '❄️',
            'attribute_impact': {
                'acidez': 0.5,
                'frutas_cítricas': 0.2
            }
        },
        {
            'id': 'dulzor_residual_tecnico',
            'text': '¿Preferís que el vino tenga cierta sensación dulce o azúcar residual?',
            'emoji': '🍯',
            'attribute_impact': {
                'dulzor': 0.5
            }
        },
        {
            'id': 'region_uco_tecnico',
            'text': '¿Preferís la tipicidad mineral y herbal del Valle de Uco a otras regiones?',
            'emoji': '🏔️',
            'attribute_impact': {
                'notas_terrosas': 0.3,
                'notas_herbales_frescas': 0.3,
                'acidez': 0.2
            }
        }
    ]
}

# 4. Preguntas de Refinamiento Extra (para baja confianza)
QUESTIONS_REFINEMENT = {
    'acidez': {
        'id': 'ref_acidez',
        'text': '¿Disfrutás la manzana verde ácida y bien crujiente?',
        'emoji': '🍏',
        'attribute_impact': {
            'acidez': 0.3
        }
    },
    'taninos': {
        'id': 'ref_taninos',
        'text': '¿Disfrutás el sabor de las bebidas amargas como el agua tónica?',
        'emoji': '🥤',
        'attribute_impact': {
            'taninos': 0.3
        }
    },
    'cuerpo': {
        'id': 'ref_cuerpo',
        'text': 'En bebidas, ¿preferís texturas con peso e intensidad en boca?',
        'emoji': '🥛',
        'attribute_impact': {
            'cuerpo': 0.3
        }
    },
    'madera_y_otros': {
        'id': 'ref_madera',
        'text': '¿Te agrada el aroma a coco tostado o tabaco en las cosas?',
        'emoji': '🥥',
        'attribute_impact': {
            'madera_y_otros': 0.3
        }
    },
    'dulzor': {
        'id': 'ref_dulzor',
        'text': '¿Disfrutás del sabor de la miel pura o el flan con caramelo?',
        'emoji': '🍯',
        'attribute_impact': {
            'dulzor': 0.3
        }
    }
}
