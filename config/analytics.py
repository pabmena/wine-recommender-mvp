import os
import sqlite3
import json
from datetime import datetime

DATABASE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'analytics.db')

def init_analytics_db():
    """
    Inicializa la base de datos SQLite de analíticas si no existe.
    """
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            client_id TEXT NOT NULL,
            event_type TEXT NOT NULL,
            session_id TEXT,
            payload TEXT
        )
    ''')
    conn.commit()
    conn.close()

def track_event(client_id, event_type, session_id, payload=None):
    """
    Registra un evento de tracking en la base de datos.
    """
    init_analytics_db()
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    timestamp = datetime.now().isoformat()
    payload_str = json.dumps(payload, ensure_ascii=False) if payload else None
    
    cursor.execute('''
        INSERT INTO events (timestamp, client_id, event_type, session_id, payload)
        VALUES (?, ?, ?, ?, ?)
    ''', (timestamp, client_id, event_type, session_id, payload_str))
    
    conn.commit()
    conn.close()

def get_client_dashboard_metrics(client_id):
    """
    Obtiene las métricas agregadas del dashboard para un cliente.
    """
    init_analytics_db()
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # 1. Total quizzes iniciados
    cursor.execute("SELECT COUNT(*) FROM events WHERE client_id = ? AND event_type = 'quiz_started'", (client_id,))
    started = cursor.fetchone()[0]
    
    # 2. Total quizzes completados
    cursor.execute("SELECT COUNT(*) FROM events WHERE client_id = ? AND event_type = 'quiz_completed'", (client_id,))
    completed = cursor.fetchone()[0]
    
    # 3. Tasa de finalización
    completion_rate = (completed / started * 100) if started > 0 else 0.0
    
    # 4. Clicks a WhatsApp
    cursor.execute("SELECT COUNT(*) FROM events WHERE client_id = ? AND event_type = 'whatsapp_clicked'", (client_id,))
    whatsapp_clicks = cursor.fetchone()[0]
    
    # 5. Vinos más recomendados (parsear payload en quiz_completed)
    cursor.execute("SELECT payload FROM events WHERE client_id = ? AND event_type = 'quiz_completed'", (client_id,))
    completed_events = cursor.fetchall()
    
    wine_recommendation_counts = {}
    price_ranges_counts = {}
    
    for row in completed_events:
        try:
            if row[0]:
                payload = json.loads(row[0])
                # Contar vinos
                top_wines = payload.get('top_recommendations', [])
                for title in top_wines:
                    wine_recommendation_counts[title] = wine_recommendation_counts.get(title, 0) + 1
                # Contar rangos de precio
                price_range = payload.get('price_range')
                if price_range:
                    price_ranges_counts[price_range] = price_ranges_counts.get(price_range, 0) + 1
        except Exception:
            continue
            
    sorted_recommended_wines = sorted(wine_recommendation_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    
    # 6. Vinos más clickeados
    cursor.execute("SELECT payload FROM events WHERE client_id = ? AND event_type = 'wine_clicked'", (client_id,))
    click_events = cursor.fetchall()
    wine_click_counts = {}
    for row in click_events:
        try:
            if row[0]:
                payload = json.loads(row[0])
                title = payload.get('wine_title')
                if title:
                    wine_click_counts[title] = wine_click_counts.get(title, 0) + 1
        except Exception:
            continue
            
    sorted_clicked_wines = sorted(wine_click_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    
    # 7. Feedback summary
    cursor.execute("SELECT COUNT(*) FROM events WHERE client_id = ? AND event_type = 'feedback_like'", (client_id,))
    likes = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM events WHERE client_id = ? AND event_type = 'feedback_dislike'", (client_id,))
    dislikes = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        'quizzes_started': started,
        'quizzes_completed': completed,
        'completion_rate': round(completion_rate, 2),
        'whatsapp_clicks': whatsapp_clicks,
        'top_recommended_wines': sorted_recommended_wines,
        'top_clicked_wines': sorted_clicked_wines,
        'price_ranges': price_ranges_counts,
        'likes': likes,
        'dislikes': dislikes
    }
