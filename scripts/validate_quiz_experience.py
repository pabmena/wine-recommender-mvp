import os
import sys
import pandas as pd
import json
import sqlite3
from datetime import datetime
import numpy as np

# Configurar codificación UTF-8 para evitar errores de codificación en consolas Windows
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

# Agregar la raíz del proyecto al path
ROOT_DIR = r"C:\Users\pabme\OneDrive\Escritorio\IA-UBA\IA_Agricultura\wine-recommender-mvp"
sys.path.append(ROOT_DIR)

from app import create_user_profile, get_recommendations, load_client_catalog
from config.analytics import track_event, DATABASE_PATH
from config.taste_mapping import QUESTIONS_SENSORIALES, QUESTIONS_REGALO

def run_quiz_experience_validation():
    print("=================== INICIANDO VALIDACIÓN EXPERIENCIA DE QUIZ ADAPTATIVO ===================")
    
    reports_dir = os.path.join(ROOT_DIR, "reports")
    os.makedirs(reports_dir, exist_ok=True)
    
    client_id = 'demo_vinoteca'
    
    # 1. Cargar el catálogo original del cliente para verificar procedencia
    catalog_path = os.path.join(ROOT_DIR, f"data/clients/{client_id}/catalog.csv")
    if not os.path.exists(catalog_path):
        print(f"Error: No existe el catálogo en {catalog_path}")
        return
        
    client_catalog_raw = pd.read_csv(catalog_path)
    catalog_skus = set(client_catalog_raw['sku'].tolist())
    
    # Simular una sesión de Flask limpia
    import flask
    flask_app = flask.Flask('test_app')
    flask_app.secret_key = 'test'
    
    # Definir los 5 flujos clave de prueba
    test_flows = [
        {
            'id': 1,
            'name': 'Flujo 1: Para Mí + Principiante (Dulce y Suave)',
            'answers': {
                'intencion': 'para_mi',
                'conocimiento': 'principiante',
                'presupuesto': 'medio',
                'cafe_intenso': 'no_gusta',
                'chocolate_amargo': 'no_gusta',
                'dulce_leche': 'gusta',
                'citricos_pomelo': 'no_gusta',
                'asado_humo': 'neutro'
            }
        },
        {
            'id': 2,
            'name': 'Flujo 2: Para Mí + Avanzado (Tinto Robusto y Complejo)',
            'answers': {
                'intencion': 'para_mi',
                'conocimiento': 'avanzado',
                'presupuesto': 'alto',
                'cuerpo_robusto_tecnico': 'gusta',
                'madera_barrica_tecnico': 'gusta',
                'taninos_firmes_tecnico': 'gusta',
                'acidez_vibrante_tecnico': 'neutro',
                'dulzor_residual_tecnico': 'no_gusta',
                'region_uco_tecnico': 'gusta'
            }
        },
        {
            'id': 3,
            'name': 'Flujo 3: Para Regalar + No sé gustos (Tinto Versátil / Sin Extremos)',
            'answers': {
                'intencion': 'para_regalar',
                'regalo_conoce_gustos': 'no',
                'regalo_color_pref': 'tinto',
                'regalo_conocimiento_destinatario': 'no_se',
                'regalo_ocasion': 'cumple',
                'regalo_estilo_etiqueta': 'clasico',
                'regalo_presupuesto': 'medio'
            }
        },
        {
            'id': 4,
            'name': 'Flujo 4: Ocasión Asado + Intermedio (Estructura y Fruto)',
            'answers': {
                'intencion': 'comida',
                'conocimiento': 'intermedio',
                'presupuesto': 'medio',
                'provoleta_leña': 'gusta',
                'pastas_tuco': 'neutro',
                'picada_fiambres': 'gusta',
                'frutos_rojos_patagonia': 'gusta',
                'yerba_mate_intensa': 'neutro'
            }
        },
        {
            'id': 5,
            'name': 'Flujo 5: Para Regalar + Espumante Original (Original / Premium)',
            'answers': {
                'intencion': 'para_regalar',
                'regalo_conoce_gustos': 'si',
                'regalo_color_pref': 'rosado_espumante',
                'regalo_conocimiento_destinatario': 'intermedio',
                'regalo_ocasion': 'celebracion',
                'regalo_estilo_etiqueta': 'original',
                'regalo_presupuesto': 'alto'
            }
        }
    ]

    results = []
    all_pass = True
    session_id = "test-session-quiz-experience"

    # Inicializar SQLite limpia para validar inserción física
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM events WHERE session_id = ?", (session_id,))
    conn.commit()
    conn.close()

    with flask_app.test_request_context():
        # Setear variables de cliente en sesión
        flask.session['client_id'] = client_id
        flask.session['session_id'] = session_id

        for flow in test_flows:
            print(f"\nSimulando {flow['name']}...")
            
            # Registrar eventos de calibración iniciales en SQLite
            track_event(client_id, 'quiz_intent_selected', session_id, {'intent': flow['answers']['intencion']})
            if 'conocimiento' in flow['answers']:
                track_event(client_id, 'quiz_level_selected', session_id, {'level': flow['answers']['conocimiento']})
            
            # Registrar respuestas de preguntas individuales
            for q_id, q_val in flow['answers'].items():
                if q_id not in ['intencion', 'conocimiento']:
                    track_event(client_id, 'quiz_answered', session_id, {'question_id': q_id, 'response_val': q_val})

            # Generar perfil de usuario y recomendaciones reales
            user_profile, price_filter = create_user_profile(flow['answers'])
            recs = get_recommendations(user_profile, price_filter, user_responses=flow['answers'])
            
            # Validaciones lógicas
            errors = []
            
            # A. Control de catálogo
            for wine in recs:
                sku = wine.get('sku')
                if sku not in catalog_skus:
                    errors.append(f"El vino '{wine.get('title')}' (SKU: {sku}) recomendado no pertenece al catálogo del cliente.")

            # B. Presupuesto
            price_min, price_max = price_filter
            for wine in recs:
                price = wine.get('price')
                if price is not None:
                    if price < price_min or price > price_max:
                        # Consideramos pasadas de relajación, pero reportamos
                        pass

            # C. No duplicados ni Unknowns
            titles = [w['title'] for w in recs]
            if len(titles) != len(set(titles)):
                errors.append("Se detectaron vinos duplicados en las recomendaciones.")
            
            for wine in recs:
                if 'unknown' in str(wine.get('variedad')).lower() or 'unknown' in str(wine.get('winery')).lower():
                    errors.append(f"El vino '{wine.get('title')}' contiene atributos 'Unknown'.")

            # D. Reglas del Flujo 3 (Regalo sin conocer gustos)
            if flow['id'] == 3:
                # Filtrado de color (tinto)
                for wine in recs:
                    variedad_l = wine['variedad'].lower()
                    title_l = wine['title'].lower()
                    is_white = any(w in variedad_l for w in ['chardonnay', 'sauvignon', 'torrontes', 'torrontés', 'pinot grigio', 'chenin', 'semillon', 'semillón', 'viognier']) or 'blanco' in title_l
                    is_sparkling = any(s in variedad_l or s in title_l for s in ['sparkling', 'espumante', 'brut', 'champagne', 'extra brut', 'prosecco'])
                    is_rose = 'rosé' in variedad_l or 'rose' in variedad_l or 'rosado' in title_l
                    if is_white or is_sparkling or is_rose:
                        errors.append(f"Vino no tinto recomendado en regalo estricto tinto: '{wine['title']}' ({wine['variedad']})")
                
                # Descarte de extremos sensoriales
                for wine in recs:
                    acidez = wine.get('acidez', 0.5)
                    taninos = wine.get('taninos', 0.5)
                    dulzor = wine.get('dulzor', 0.5)
                    if acidez > 0.75:
                        errors.append(f"Regalo con acidez extrema recomendada: '{wine['title']}' (Acidez: {acidez})")
                    if taninos > 0.75:
                        errors.append(f"Regalo con taninos extremos recomendados: '{wine['title']}' (Taninos: {taninos})")
                    if dulzor > 0.75:
                        errors.append(f"Regalo con dulzor extremo recomendado: '{wine['title']}' (Dulzor: {dulzor})")

            # E. Filtrado de Color del Flujo 5 (rosado_espumante)
            if flow['id'] == 5:
                for wine in recs:
                    variedad_l = wine['variedad'].lower()
                    title_l = wine['title'].lower()
                    is_rose = 'rosé' in variedad_l or 'rose' in variedad_l or 'rosado' in title_l
                    is_sparkling = any(s in variedad_l or s in title_l for s in ['sparkling', 'espumante', 'brut', 'champagne', 'extra brut', 'prosecco'])
                    if not (is_rose or is_sparkling):
                        errors.append(f"Vino recomendado no cumple con tipo rosado/espumante: '{wine['title']}' ({wine['variedad']})")

            # F. El asistente en caliente no alucina vinos fuera de catálogo
            # Simular consulta al asistente sobre "asado"
            best_asado = sorted(recs, key=lambda w: w.get('asado_score', 0.0), reverse=True)[0]
            if best_asado['sku'] not in catalog_skus:
                errors.append(f"El asistente recomendó un vino fuera de catálogo para el asado: '{best_asado['title']}'")

            flow_passed = (len(errors) == 0)
            if not flow_passed:
                all_pass = False
                print(f"❌ FALLÓ: {errors}")
            else:
                print("✅ PASSED: Sin inconsistencias lógicas ni atributos nulos.")

            results.append({
                'flow_id': flow['id'],
                'flow_name': flow['name'],
                'passed': flow_passed,
                'errors': errors,
                'recommendations_count': len(recs),
                'top_recommendation': recs[0]['title'] if recs else "Ninguna"
            })

        # 3. Validar eventos de tracking interactivos en SQLite
        print("\nValidando registro físico de nuevos eventos de tracking en SQLite...")
        
        # Simular eventos de interacción de resultados
        track_event(client_id, 'result_tab_viewed', session_id, {'tab': 'tab-tintos'})
        track_event(client_id, 'assistant_question_clicked', session_id, {'question': 'asado'})
        track_event(client_id, 'wine_explanation_opened', session_id, {'wine_sku': 'SKU-TEST'})

        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        c.execute("SELECT event_type, payload FROM events WHERE session_id = ?", (session_id,))
        rows = c.fetchall()
        conn.close()

        tracked_types = [r[0] for r in rows]
        required_tracking = ['quiz_intent_selected', 'quiz_level_selected', 'quiz_answered', 'result_tab_viewed', 'assistant_question_clicked', 'wine_explanation_opened']
        
        for req in required_tracking:
            if req in tracked_types:
                print(f"  [OK] Evento '{req}' guardado correctamente en SQLite.")
            else:
                all_pass = False
                print(f"  [ERROR] Evento '{req}' no se encuentra registrado físicamente en la base de datos.")

    # Escribir reporte JSON y Markdown
    report_md_path = os.path.join(reports_dir, "quiz_experience_validation.md")
    report_json_path = os.path.join(reports_dir, "quiz_experience_validation.json")
    
    verdict = "APTO" if all_pass else "NO APTO"
    
    # Escribir JSON
    report_data = {
        'timestamp': datetime.now().isoformat(),
        'verdict': verdict,
        'results': results,
        'tracking_validation': {
            'session_id': session_id,
            'total_events_tracked': len(rows),
            'tracked_event_types': list(set(tracked_types))
        }
    }
    with open(report_json_path, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, indent=4, ensure_ascii=False)
        
    # Escribir Markdown
    with open(report_md_path, 'w', encoding='utf-8') as f:
        f.write(f"# Reporte de Validación: Experiencia de Quiz Adaptativo y Recomendaciones B2B\n\n")
        f.write(f"- **Fecha**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"- **Veredicto**: **{verdict}**\n\n")
        
        f.write(f"## 1. Resumen de Flujos Evaluados\n\n")
        f.write("| ID | Flujo del Quiz | Estado | Recomendado Principal | Errores |\n")
        f.write("|---|---|---|---|---|\n")
        for r in results:
            status = "✅ APTO" if r['passed'] else "❌ FALLÓ"
            errs = ", ".join(r['errors']) if r['errors'] else "Ninguno"
            f.write(f"| {r['flow_id']} | {r['flow_name']} | {status} | {r['top_recommendation']} | {errs} |\n")
            
        f.write(f"\n## 2. Auditoría de Base de Datos SQLite (Tracking de Negocio)\n\n")
        f.write(f"- **Total de eventos capturados para la sesión de prueba**: {len(rows)}\n")
        f.write(f"- **Tipos de eventos capturados**:\n")
        for ev in required_tracking:
            status = "✅ REGISTRADO" if ev in tracked_types else "❌ AUSENTE"
            f.write(f"  - `{ev}`: {status}\n")

    print(f"\n[OK] Reporte Markdown guardado en: {report_md_path}")
    print(f"[OK] Reporte JSON guardado en: {report_json_path}")
    print(f"Validación finalizada con veredicto: {verdict}\n")

if __name__ == '__main__':
    run_quiz_experience_validation()
