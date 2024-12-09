import praw
import os
from dotenv import load_dotenv
import logging

# Habilitar registros de depuración
logging.basicConfig(level=logging.DEBUG)

# Cargar variables de entorno
load_dotenv()

CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
USER_AGENT = os.getenv('REDDIT_USER_AGENT')

# Crear instancia de Reddit
reddit = praw.Reddit(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    user_agent=USER_AGENT,
)

# Verificar la conexión
try:
    print(f"Autenticado como: {reddit.user.me()}")
except Exception as e:
    print("Error en la autenticación:", e)
    exit()

# Intentar extraer publicaciones
try:
    subreddit = reddit.subreddit('wine')
    print("\nPublicaciones recientes en r/wine:\n")
    for submission in subreddit.new(limit=10):
        print(f"Título: {submission.title}")
        print(f"Contenido: {submission.selftext[:100]}...")
        print(f"Autor: {submission.author}")
        print("-" * 40)
except Exception as e:
    print("Error al extraer publicaciones:", e)

