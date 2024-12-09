import praw
import os
import csv
from datetime import datetime

# Credenciales de la aplicación Reddit
CLIENT_ID = 'xVZtoTS2u7TI_aBf5zsMcQ'  # Tu Client ID
CLIENT_SECRET = '31vcyV2pR1XmnAJs7kDCjTVe5mOGxw'  # Tu Client Secret
USER_AGENT = 'Paul_Wine (by u/No_Comparison8318)'  # Formato del User Agent

# Crear una instancia básica de Reddit
reddit = praw.Reddit(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    user_agent=USER_AGENT,
)

# Lista de subreddits relevantes
subreddits = ['argentina', 'wine', 'vino', 'es']

# Lista de palabras clave en español e inglés
keywords = [
    'vino argentino', 'Malbec argentino', 'bodegas argentinas', 'vinos de Mendoza', 'vinos de Salta', 'vinos de San Juan',
    'regiones vitivinícolas de Argentina', 'Cabernet Sauvignon argentina', 'recomendación de vinos argentinos',
    'mejores vinos argentinos', 'Torrontés argentino', 'Bonarda de argentina', 'variedades de vinos argentinos',
    'vino de la Patagonia Argentina', 'Argentine wine', 'Malbec from Argentina', 'wineries in Argentina',
    'Mendoza wine recommendations', 'best Argentine wines', 'Salta Argentinian wine', 'San Juan Argentinian wine',
    'Argentinian wine regions', 'Torrontes wine', 'Bonarda wine', 'Argentinian wine varietals',
    'Cabernet Sauvignon from Argentina', 'Patagonia Argentinian wine'
]

# Crear o abrir un archivo CSV para guardar los datos
current_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(current_dir, '..', 'data')
os.makedirs(output_dir, exist_ok=True)
output_file = os.path.join(output_dir, 'reddit_argentina_wine_data.csv')

with open(output_file, mode='w', encoding='utf-8', newline='') as file:
    writer = csv.writer(file)
    # Escribir cabeceras
    writer.writerow(['subreddit', 'title', 'content', 'author', 'score', 'num_comments', 'created_utc', 'url'])

    posts_extracted = 0

    for subreddit_name in subreddits:
        try:
            subreddit = reddit.subreddit(subreddit_name)
            print(f"\nBuscando publicaciones en r/{subreddit_name}...\n")

            for keyword in keywords:
                try:
                    print(f"Buscando por palabra clave: '{keyword}'")
                    # Buscar publicaciones que contengan la palabra clave
                    for submission in subreddit.search(keyword, limit=50):  # Cambia el límite si es necesario
                        # Ignorar publicaciones sin texto en el contenido y solo enlaces
                        if submission.is_self:
                            writer.writerow([
                                subreddit_name,
                                submission.title,
                                submission.selftext.replace('\n', ' ').replace('\r', ' '),
                                str(submission.author),
                                submission.score,
                                submission.num_comments,
                                datetime.utcfromtimestamp(submission.created_utc).strftime('%Y-%m-%d %H:%M:%S'),
                                submission.url
                            ])
                            posts_extracted += 1

                            print(f"Publicaciones extraídas: {posts_extracted}", end='\r')

                except Exception as e:
                    print(f"Error al procesar la palabra clave '{keyword}' en r/{subreddit_name}: {e}")

        except Exception as e:
            print(f"Error al procesar r/{subreddit_name}: {e}")

print(f"\n\nExtracción completada. Total de publicaciones extraídas: {posts_extracted}")
print(f"Datos guardados en '{output_file}'")
