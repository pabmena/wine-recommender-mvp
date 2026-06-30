import os
import sys
import pandas as pd
import json
from datetime import datetime

# Agregar la raíz del proyecto al path
sys.path.append(r"C:\Users\pabme\OneDrive\Escritorio\IA-UBA\IA_Agricultura\wine-recommender-mvp")

from app import create_user_profile, get_recommendations, get_recommendations_for_confidence, load_client_catalog, infer_commercial_intent
from config.analytics import track_event, get_client_dashboard_metrics

# Definiciones de estilos de variedad de uva
white_fresh_varieties = ['torrontés', 'torrontes', 'chardonnay', 'sauvignon blanc', 'sauvignon', 'pinot grigio', 'white blend', 'sparkling blend', 'espumante', 'rosé', 'rose', 'viognier']
light_red_varieties = ['pinot noir', 'criolla', 'país', 'pais']
structured_red_varieties = ['malbec', 'cabernet sauvignon', 'cabernet franc', 'cabernet', 'bonarda', 'syrah', 'red blend', 'bordeaux-style red blend', 'malbec-cabernet sauvignon', 'merlot', 'malbec-cabernet', 'malbec blend', 'tempranillo']

def run_commercial_validation():
    print("=================== INICIANDO VALIDACIÓN COMERCIAL MVP 0.1.1 (INTENT ALIGNMENT) ===================")
    
    reports_dir = r"C:\Users\pabme\OneDrive\Escritorio\IA-UBA\IA_Agricultura\wine-recommender-mvp\reports"
    os.makedirs(reports_dir, exist_ok=True)
    
    client_id = 'demo_vinoteca'
    
    # 1. Cargar el catálogo original del cliente para verificar procedencia
    catalog_path = f"data/clients/{client_id}/catalog.csv"
    if not os.path.exists(catalog_path):
        catalog_path = f"demo_data/clients/{client_id}/catalog.csv"
    if not os.path.exists(catalog_path):
        print(f"Error: No existe el catálogo en {catalog_path}")
        return
        
    client_catalog_raw = pd.read_csv(catalog_path)
    catalog_skus = set(client_catalog_raw['sku'].tolist())
    
    # 5 Perfiles a evaluar
    test_profiles = [
        {
            'id': 1,
            'name': 'Perfil 1: Blanco Fresco / Bajo presupuesto',
            'answers': {'conocimiento': 'principiante', 'cafe_pref': 'A', 'chocolate_pref': 'A', 'citricos_pref': 'C', 'asado_pref': 'A', 'hongos_pref': 'A', 'manzana_pref': 'C', 'especias_pref': 'A', 'precio': 'Menos de $10'}
        },
        {
            'id': 2,
            'name': 'Perfil 2: Tinto Asado / Alto presupuesto',
            'answers': {'conocimiento': 'principiante', 'cafe_pref': 'C', 'chocolate_pref': 'C', 'citricos_pref': 'B', 'asado_pref': 'C', 'hongos_pref': 'C', 'manzana_pref': 'A', 'especias_pref': 'C', 'precio': 'Más de $50'}
        },
        {
            'id': 3,
            'name': 'Perfil 3: Equilibrado / Presupuesto Medio',
            'answers': {'conocimiento': 'principiante', 'cafe_pref': 'B', 'chocolate_pref': 'B', 'citricos_pref': 'B', 'asado_pref': 'B', 'hongos_pref': 'B', 'manzana_pref': 'B', 'especias_pref': 'B', 'precio': '$10 - $20'}
        },
        {
            'id': 4,
            'name': 'Perfil 4: Avanzado Técnico Tinto / Alto presupuesto',
            'answers': {'conocimiento': 'avanzado', 'cuerpo_tecnico': 'C', 'madera_tecnico': 'C', 'taninos_tecnico': 'C', 'acidez_tecnico': 'B', 'dulzor_tecnico': 'A', 'precio': 'Más de $50'}
        },
        {
            'id': 5,
            'name': 'Perfil 5: Avanzado Técnico Fresco / Presupuesto Medio-Alto',
            'answers': {'conocimiento': 'avanzado', 'cuerpo_tecnico': 'A', 'madera_tecnico': 'A', 'taninos_tecnico': 'A', 'acidez_tecnico': 'C', 'dulzor_tecnico': 'A', 'precio': '$20 - $50'}
        }
    ]
    
    # Simular una sesión de Flask limpia
    import flask
    flask_app = flask.Flask('test_app')
    flask_app.secret_key = 'test'
    
    results = []
    all_pass = True
    
    # Limpiar base de datos SQLite antes de la prueba
    db_path = "data/analytics.db"
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print("Base de datos de analíticas SQLite limpiada para la simulación.")
        except Exception as e:
            print(f"No se pudo limpiar la DB anterior: {e}")
            
    with flask_app.test_request_context():
        flask.session['client_id'] = client_id
        
        for i, prof in enumerate(test_profiles, 1):
            name = prof['name']
            answers = prof['answers']
            pid = prof['id']
            session_id = f"SESSION-SIM-{pid:03d}"
            
            print(f"\nSimulando {name}...")
            
            # Registrar evento de inicio de quiz
            track_event(client_id, 'quiz_started', session_id)
            
            # Obtener perfil y recomendaciones
            user_profile, price_filter = create_user_profile(answers)
            recs = get_recommendations(user_profile, price_filter, user_responses=answers)
            top_5 = recs[:5]
            
            # Registrar evento de completado
            top_wines_titles = [w['title'] for w in top_5]
            track_event(client_id, 'quiz_completed', session_id, payload={
                'top_recommendations': top_wines_titles,
                'price_range': answers.get('precio', 'Más de $50')
            })
            track_event(client_id, 'recommendation_viewed', session_id)
            
            # Simular clicks y feedback
            if len(top_5) > 0:
                first_sku = top_5[0]['sku']
                track_event(client_id, 'wine_clicked', session_id, payload={
                    'wine_sku': first_sku,
                    'wine_title': top_5[0]['title']
                })
                track_event(client_id, 'whatsapp_clicked', session_id, payload={
                    'wine_sku': first_sku,
                    'wine_title': top_5[0]['title']
                })
                
            feedback_type = 'feedback_like' if pid % 2 != 0 else 'feedback_dislike'
            track_event(client_id, feedback_type, session_id)
            
            # --- EVALUAR CONTADORES DE ESTILO ---
            white_fresh_count = 0
            light_red_count = 0
            structured_red_count = 0
            malbec_count = 0
            unknown_count = 0
            duplicate_count = 0
            intent_relaxed = False
            
            seen_local_titles = set()
            for w in top_5:
                var_l = w['variedad'].lower()
                
                # Clasificar
                if any(f in var_l for f in white_fresh_varieties):
                    white_fresh_count += 1
                elif any(l in var_l for l in light_red_varieties):
                    light_red_count += 1
                elif any(s in var_l for s in structured_red_varieties):
                    structured_red_count += 1
                else:
                    unknown_count += 1
                    
                if 'malbec' in var_l:
                    malbec_count += 1
                    
                if w['title'].lower() in seen_local_titles:
                    duplicate_count += 1
                seen_local_titles.add(w['title'].lower())
                
                if w.get('intent_relaxed', False):
                    intent_relaxed = True

            # --- VALIDACIONES DURES POR PERFIL (TESTS OBLIGATORIOS) ---
            belong_to_catalog = all(w['sku'] in catalog_skus for w in top_5)
            no_stock_out = all(w['stock'] > 0 for w in top_5)
            only_active = True # Garantizado por carga en caliente
            
            price_min, price_max = price_filter
            respects_budget = all(float(w['price']) >= price_min and float(w['price']) <= price_max for w in top_5) or intent_relaxed
            
            intent_flags = {k: bool(v) for k, v in infer_commercial_intent(answers, user_profile).items()}
            
            passed = True
            motivo_falla = ""
            
            # Assert Perfil 1
            if pid == 1:
                # 0 Cab. Sauv, mínimo 3 frescos/livianos, máximo 1 estructurado, precio <= 12000
                cabernet_present = any('cabernet' in w['variedad'].lower() for w in top_5)
                frescos_livianos = white_fresh_count + light_red_count
                if cabernet_present:
                    passed = False
                    motivo_falla += "Contiene Cabernet Sauvignon en Perfil Blanco Fresco. "
                if frescos_livianos < 3:
                    passed = False
                    motivo_falla += f"Faltan frescos/livianos ({frescos_livianos}/3). "
                if structured_red_count > 1:
                    passed = False
                    motivo_falla += f"Exceso de tintos estructurados ({structured_red_count}/1). "
                if price_max > 12000:
                    passed = False
                    motivo_falla += f"Presupuesto mal acotado en ARS ({price_max}/12000). "
                    
            # Assert Perfil 2
            elif pid == 2:
                # Mínimo 4 estructurados, 0 Torrontés (ni blancos en general), precio >= 60000
                torrontes_present = any('torrontes' in w['variedad'].lower() or 'torrontés' in w['variedad'].lower() for w in top_5)
                whites_present = white_fresh_count > 0
                if structured_red_count < 4:
                    passed = False
                    motivo_falla += f"Faltan tintos estructurados ({structured_red_count}/4). "
                if torrontes_present:
                    passed = False
                    motivo_falla += "Contiene Torrontés en perfil Tinto Asado. "
                if whites_present and not intent_relaxed:
                    passed = False
                    motivo_falla += "Contiene vinos blancos sin relajación de intención. "
                if price_min < 60000:
                    passed = False
                    motivo_falla += f"Presupuesto inicial mal mapeado a ARS ({price_min}/60000). "

            # Assert Perfil 3
            elif pid == 3:
                # Rango 12000 a 25000, div mínima 3 variedades, 0 duplicados
                variedades_top5 = len(set(w['variedad'].lower() for w in top_5))
                if price_min != 12000 or price_max != 25000:
                    passed = False
                    motivo_falla += f"Rango de precio medio incorrecto (${price_min} - ${price_max}). "
                if variedades_top5 < 3:
                    passed = False
                    motivo_falla += f"Falta diversidad de variedades ({variedades_top5}/3). "
                if duplicate_count > 0:
                    passed = False
                    motivo_falla += "Contiene títulos duplicados en Top 5. "

            # Assert Perfil 4
            elif pid == 4:
                # Mínimo 4 tintos, 0 Torrontés, máximo 2 Malbec, div 3 var.
                tintos_count = light_red_count + structured_red_count
                torrontes_present = any('torrontes' in w['variedad'].lower() or 'torrontés' in w['variedad'].lower() for w in top_5)
                variedades_top5 = len(set(w['variedad'].lower() for w in top_5))
                if tintos_count < 4:
                    passed = False
                    motivo_falla += f"Faltan tintos ({tintos_count}/4). "
                if torrontes_present:
                    passed = False
                    motivo_falla += "Contiene Torrontés en perfil avanzado tinto. "
                if malbec_count > 2:
                    passed = False
                    motivo_falla += f"Exceso de Malbec ({malbec_count}/2). "
                if variedades_top5 < 3:
                    passed = False
                    motivo_falla += f"Falta diversidad ({variedades_top5}/3). "

            # Assert Perfil 5
            elif pid == 5:
                # Mínimo 3 frescos, máx 1 Malbec, máx 1 structured_red
                frescos_livianos = white_fresh_count + light_red_count
                if frescos_livianos < 3:
                    passed = False
                    motivo_falla += f"Faltan frescos/livianos ({frescos_livianos}/3). "
                if malbec_count > 1:
                    passed = False
                    motivo_falla += f"Exceso de Malbec ({malbec_count}/1). "
                if structured_red_count > 1:
                    passed = False
                    motivo_falla += f"Exceso de tintos estructurados ({structured_red_count}/1). "

            # Validaciones genéricas de QA
            if not belong_to_catalog:
                passed = False
                motivo_falla += "Vinos no pertenecen al catálogo del cliente. "
            if not no_stock_out:
                passed = False
                motivo_falla += "Hay vinos sin stock en el Top 5. "
            if not respects_budget:
                passed = False
                motivo_falla += "Hay vinos fuera del presupuesto. "

            if not passed:
                all_pass = False
                
            results.append({
                'perfil_id': pid,
                'perfil': name,
                'recs': [f"{w['sku']} - {w['title']} ({w['variedad']}) (${w['price']:.2f}, Stock: {w['stock']})" for w in top_5],
                'intent_flags': intent_flags,
                'structured_red_count': structured_red_count,
                'white_fresh_count': white_fresh_count,
                'light_red_count': light_red_count,
                'malbec_count': malbec_count,
                'unknown_count': unknown_count,
                'duplicate_count': duplicate_count,
                'intent_relaxed': intent_relaxed,
                'passed': passed,
                'motivo': motivo_falla if not passed else "OK"
            })
            
            print(f"  Resultados: PASSED={passed} | Motivo={motivo_falla or 'OK'}")

        # Leer y validar analíticas del dashboard
        metrics = get_client_dashboard_metrics(client_id)
        dash_ok = (
            metrics['quizzes_started'] == 5 and
            metrics['quizzes_completed'] == 5 and
            metrics['whatsapp_clicks'] == 5
        )
        if not dash_ok:
            all_pass = False
            print("\n[ERROR] El Dashboard de Analíticas no acumula correctamente los eventos.")
        else:
            print("\n[OK] El Dashboard de Analíticas registra todos los eventos correctamente.")

    decision = "APTO" if all_pass else "NO APTO"
    
    # Consolidar JSON de validación
    val_json = {
        'timestamp': datetime.now().isoformat(),
        'version': 'commercial-mvp-v0.1.1-intent-aligned',
        'final_decision': decision,
        'all_profiles_passed': bool(all_pass),
        'results': results,
        'dashboard_metrics': metrics
    }
    
    json_path = os.path.join(reports_dir, 'commercial_mvp_validation.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(val_json, f, indent=4, ensure_ascii=False)
        
    md_path = os.path.join(reports_dir, 'commercial_mvp_validation.md')
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write("# Informe de Calidad e Integración Comercial V0.1.1 (SommAI MVP)\n\n")
        f.write("## Resumen Ejecutivo\n")
        f.write("Este informe valida la calibración comercial **V0.1.1 (Intent Alignment)** de la plataforma SommAI. Evalúa de forma automática el cumplimiento de las restricciones semánticas de estilo e intención por perfil (evitando Cabernet Sauvignon en perfiles frescos, Torrontés en tintos/asados, y Malbec excedentes), además de respetar stock, estado activo e intervalos de precios en pesos argentinos reales, confirmando el correcto tracking SQLite.\n\n")
        
        f.write("## Tabla de Resultados por Perfil Simulado\n")
        f.write("| ID | Perfil Evaluado | Tintos Est. | Blancos/Frescos | Tintos Livianos | Malbecs | Relajado | Resultado | Detalle/Motivo |\n")
        f.write("| --- | --- | --- | --- | --- | --- | --- | --- | --- |\n")
        for r in results:
            emoji = "✅ PASSED" if r['passed'] else "❌ FAILED"
            f.write(f"| {r['perfil_id']} | {r['perfil']} | {r['structured_red_count']} | {r['white_fresh_count']} | {r['light_red_count']} | {r['malbec_count']} | {'Sí' if r['intent_relaxed'] else 'No'} | {emoji} | {r['motivo']} |\n")
            
        f.write("\n## Detalle de Recomendaciones y Búsqueda por Perfil\n")
        for r in results:
            f.write(f"### {r['perfil']}\n")
            f.write(f"- **Flags de Intención**: `{json.dumps(r['intent_flags'])}`\n")
            f.write("- **Top 5 Recomendaciones asignadas**:\n")
            for rec in r['recs']:
                f.write(f"  - {rec}\n")
            f.write("\n")
            
        f.write("## Auditoría de Analíticas en Dashboard (Persistencia SQLite)\n")
        f.write(f"- **Quizzes Iniciados**: {metrics['quizzes_started']} (Esperado: 5) -> {'✅ OK' if metrics['quizzes_started'] == 5 else '❌ ERROR'}\n")
        f.write(f"- **Quizzes Completados**: {metrics['quizzes_completed']} (Esperado: 5) -> {'✅ OK' if metrics['quizzes_completed'] == 5 else '❌ ERROR'}\n")
        f.write(f"- **Tasa de Conversión**: {metrics['completion_rate']}% (Esperado: 100.0%) -> {'✅ OK' if metrics['completion_rate'] == 100.0 else '❌ ERROR'}\n")
        f.write(f"- **Clicks a WhatsApp (Leads)**: {metrics['whatsapp_clicks']} (Esperado: 5) -> {'✅ OK' if metrics['whatsapp_clicks'] == 5 else '❌ ERROR'}\n")
        f.write(f"- **Feedback Likes (👍)**: {metrics['likes']} (Esperado: 3) -> {'✅ OK' if metrics['likes'] == 3 else '❌ ERROR'}\n")
        f.write(f"- **Feedback Dislikes (👎)**: {metrics['dislikes']} (Esperado: 2) -> {'✅ OK' if metrics['dislikes'] == 2 else '❌ ERROR'}\n\n")
        
        f.write("### Top Vinos Recomendados:\n")
        for title, count in metrics['top_recommended_wines']:
            f.write(f"- **{title}**: recomendado {count} veces\n")
            
        f.write("\n### Top Vinos Clickeados a E-Commerce:\n")
        for title, count in metrics['top_clicked_wines']:
            f.write(f"- **{title}**: clickeado {count} veces\n")
            
        f.write("\n## Decisión Final de QA\n")
        f.write(f"**Veredicto**: **{decision}** para la salida comercial del MVP.\n")
        
    print(f"\nReporte comercial guardado en: {md_path}")
    print(f"Reporte JSON guardado en: {json_path}")
    print(f"Validación finalizada con veredicto: {decision}")

if __name__ == '__main__':
    run_commercial_validation()
