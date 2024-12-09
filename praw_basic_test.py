import praw
import os
import csv
from datetime import datetime
from praw.models import MoreComments

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

# Lista de subreddits relacionados con vinos
subreddits = ['wine', 'winemaking', 'wine_tasting', 'vineyards', 'WineNoobs']

# Número total de publicaciones a extraer
total_posts = 1000

# Crear o abrir un archivo CSV para guardar los datos
output_file = 'reddit_wine_data.csv'

with open(output_file, mode='w', encoding='utf-8', newline='') as file:
    writer = csv.writer(file)
    # Escribir cabeceras
    writer.writerow(['subreddit', 'title', 'content', 'author', 'score', 'num_comments', 'created_utc', 'url'])

    posts_extracted = 0

    for subreddit_name in subreddits:
        subreddit = reddit.subreddit(subreddit_name)
        print(f"\nExtrayendo publicaciones de r/{subreddit_name}...\n")

        # Extraer publicaciones nuevas hasta alcanzar el total deseado
        for submission in subreddit.new(limit=None):
            if posts_extracted >= total_posts:
                break

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

        if posts_extracted >= total_posts:
            break

print(f"\n\nExtracción completada. Total de publicaciones extraídas: {posts_extracted}")
print(f"Datos guardados en '{output_file}'")
