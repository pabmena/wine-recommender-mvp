import os
import csv
import praw
from datetime import datetime
from dotenv import load_dotenv

# Cargar variables de entorno del archivo .env
load_dotenv()

def collect_reddit_data():
    print("Iniciando recolección REAL de datos de Reddit...")
    
    client_id = os.getenv('REDDIT_CLIENT_ID')
    client_secret = os.getenv('REDDIT_CLIENT_SECRET')
    user_agent = os.getenv('REDDIT_USER_AGENT')
    
    if not client_id or not client_secret:
        print("Error: No se encontraron credenciales de Reddit en el archivo .env.")
        return
        
    try:
        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )
        
        # Palabras clave reales para buscar en Reddit en español
        keywords = ['vino argentino', 'malbec mendocino', 'cabernet franc argentina', 'vino asado', 'vino supermercado argentina', 'bodega mendoza']
        
        # Definir ruta de salida
        current_dir = os.path.dirname(os.path.abspath(__file__))
        raw_dir = os.path.join(current_dir, '../data/raw')
        os.makedirs(raw_dir, exist_ok=True)
        output_file = os.path.join(raw_dir, 'reddit_argentina_2026.csv')
        
        posts_extracted = 0
        max_posts = 100  # Límite controlado para evitar saturación de la API
        
        with open(output_file, mode='w', encoding='utf-8', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['comment_id', 'subreddit', 'title', 'content', 'author', 'score', 'created_utc', 'url'])
            
            # Buscar en r/argentina y r/buenosaires o búsqueda global en español
            for query in keywords:
                if posts_extracted >= max_posts:
                    break
                print(f"Buscando posts en Reddit con la consulta: '{query}'...")
                
                # Realizar la búsqueda en Reddit
                submissions = reddit.subreddit('all').search(query, sort='relevance', limit=20)
                
                for submission in submissions:
                    if posts_extracted >= max_posts:
                        break
                        
                    # Filtrar posts que contengan texto descriptivo
                    if submission.is_self and len(submission.selftext) > 20:
                        writer.writerow([
                            f"red_{submission.id}",
                            submission.subreddit.display_name,
                            submission.title,
                            submission.selftext.replace('\n', ' ').replace('\r', ' '),
                            str(submission.author),
                            submission.score,
                            datetime.utcfromtimestamp(submission.created_utc).strftime('%Y-%m-%d %H:%M:%S'),
                            submission.url
                        ])
                        posts_extracted += 1
                        print(f" -> Post real extraído: [ID: {submission.id}] [Score: {submission.score}]")
                        
                        # Extraer también algunos comentarios relevantes del post
                        submission.comments.replace_more(limit=0) # Evitar llamadas extras de paginación
                        for comment in submission.comments[:3]: # Tomar los 3 comentarios más votados
                            if len(comment.body) > 15:
                                writer.writerow([
                                    f"red_c_{comment.id}",
                                    submission.subreddit.display_name,
                                    f"Comentario en: {submission.title[:30]}",
                                    comment.body.replace('\n', ' ').replace('\r', ' '),
                                    str(comment.author),
                                    comment.score,
                                    datetime.utcfromtimestamp(comment.created_utc).strftime('%Y-%m-%d %H:%M:%S'),
                                    submission.url
                                ])
                                posts_extracted += 1
                                
        print(f"Extracción de Reddit finalizada. Se guardaron {posts_extracted} entradas reales en: {output_file}")
        
    except Exception as e:
        print(f"Error durante la conexión o extracción de Reddit: {e}")

if __name__ == '__main__':
    collect_reddit_data()
