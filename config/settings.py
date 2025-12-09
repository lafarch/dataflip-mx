# DataFlip MX - Configuración
# IMPORTANTE: No subas este archivo a Git si contiene API keys reales

import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# === MERCADO LIBRE API ===
# Documentación: https://developers.mercadolibre.com.mx/
MELI_CLIENT_ID = os.getenv('MELI_CLIENT_ID', '')
MELI_CLIENT_SECRET = os.getenv('MELI_CLIENT_SECRET', '')

# === REDDIT API ===
# Crear app en: https://www.reddit.com/prefs/apps
REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID', '')
REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET', '')
REDDIT_USER_AGENT = 'DataFlipMX/1.0'

# === PARÁMETROS DE ANÁLISIS ===
NICHES_TO_ANALYZE = [
    'calculadora financiera',
    'camara digital vintage',
    'teclado mecanico',
    'libros ciencia datos',
    'nintendo game boy',
    'ipod classic',
    'chamarra carhartt',
    'the north face',
]

# === CONFIGURACIÓN DE SCRAPING ===
REQUEST_DELAY = 2  # Segundos entre requests (respetar servidores)
MAX_RETRIES = 3
TIMEOUT = 10

# === PATHS ===
DATA_RAW = 'data/raw'
DATA_PROCESSED = 'data/processed'
DATA_ANALYTICS = 'data/analytics'
LOGS = 'logs'
