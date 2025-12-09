# %% [markdown]
# # 🗣️ DataFlip MX - Reddit Sentiment Analysis
# 
# **Objetivo:** Detectar quejas, necesidades y oportunidades en comunidades nicho
# 
# **Docs:** https://praw.readthedocs.io/

# %%
# === IMPORTAR LIBRERÍAS ===
import praw
import pandas as pd
import numpy as np
from datetime import datetime
import time
import re
from collections import Counter
import plotly.express as px
import plotly.graph_objects as go
import warnings
warnings.filterwarnings('ignore')

print("✅ Librerías importadas correctamente")

# %%
# === CONFIGURACIÓN DE REDDIT API ===
# IMPORTANTE: Debes crear una app en https://www.reddit.com/prefs/apps

# Para este ejemplo, usamos credenciales de placeholder
# Reemplaza con tus credenciales reales en config/settings.py

try:
    from config.settings import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT
    
    reddit = praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent=REDDIT_USER_AGENT
    )
    
    # Verificar conexión
    print(f"✅ Conectado a Reddit como: {reddit.read_only}")
    
except Exception as e:
    print(f"⚠️  Error conectando a Reddit: {e}")
    print("   Configura tus credenciales en config/settings.py")
    reddit = None

# %%
# === SUBREDDITS RELEVANTES ===
# Comunidades donde buscaremos oportunidades

SUBREDDITS = [
    'MechanicalKeyboards',  # Teclados mecánicos
    'gamecollecting',       # Coleccionistas de videojuegos
    'retrogaming',          # Gaming retro
    'AnalogCommunity',      # Fotografía analógica
    'Flipping',             # Comunidad de resellers
    'ThriftStoreHauls',     # Hallazgos en segunda mano
    'mexico',               # México general
    'ITAM',                 # ITAM (si existe)
]

# Keywords a buscar
KEYWORDS = [
    'calculadora financiera',
    'hp 12c',
    'game boy',
    'ipod',
    'teclado mecanico',
    'camara vintage',
    'segunda mano',
    'donde comprar',
    'recomendaciones',
]

print(f"🎯 {len(SUBREDDITS)} subreddits a analizar")
print(f"🔍 {len(KEYWORDS)} keywords a buscar")

# %%
# === FUNCIONES DE SCRAPING ===

def search_subreddit(subreddit_name: str, query: str, limit: int = 100, time_filter: str = 'year'):
    """
    Busca posts en un subreddit específico
    
    Args:
        subreddit_name: Nombre del subreddit
        query: Término de búsqueda
        limit: Número máximo de posts
        time_filter: 'hour', 'day', 'week', 'month', 'year', 'all'
    
    Returns:
        Lista de diccionarios con datos de posts
    """
    if reddit is None:
        return []
    
    try:
        subreddit = reddit.subreddit(subreddit_name)
        posts = []
        
        for submission in subreddit.search(query, limit=limit, time_filter=time_filter):
            posts.append({
                'id': submission.id,
                'title': submission.title,
                'selftext': submission.selftext,
                'score': submission.score,
                'num_comments': submission.num_comments,
                'created_utc': datetime.fromtimestamp(submission.created_utc),
                'author': str(submission.author),
                'subreddit': subreddit_name,
                'url': submission.url,
                'permalink': f"https://reddit.com{submission.permalink}",
                'keyword': query
            })
        
        return posts
    
    except Exception as e:
        print(f"❌ Error en r/{subreddit_name} con '{query}': {e}")
        return []

def get_top_posts(subreddit_name: str, limit: int = 50, time_filter: str = 'month'):
    """
    Obtiene los posts más populares de un subreddit
    """
    if reddit is None:
        return []
    
    try:
        subreddit = reddit.subreddit(subreddit_name)
        posts = []
        
        for submission in subreddit.top(limit=limit, time_filter=time_filter):
            posts.append({
                'id': submission.id,
                'title': submission.title,
                'selftext': submission.selftext[:500],  # Primeros 500 chars
                'score': submission.score,
                'num_comments': submission.num_comments,
                'created_utc': datetime.fromtimestamp(submission.created_utc),
                'author': str(submission.author),
                'subreddit': subreddit_name,
                'permalink': f"https://reddit.com{submission.permalink}"
            })
        
        return posts
    
    except Exception as e:
        print(f"❌ Error en r/{subreddit_name}: {e}")
        return []

# %%
# === ANÁLISIS: BÚSQUEDA POR KEYWORDS ===
if reddit:
    print("\n" + "="*60)
    print("🔍 BUSCANDO KEYWORDS EN SUBREDDITS")
    print("="*60 + "\n")
    
    all_posts = []
    
    # Buscar solo en subreddits más relevantes para no saturar
    priority_subreddits = ['Flipping', 'ThriftStoreHauls', 'mexico']
    priority_keywords = ['game boy', 'calculadora', 'vintage']
    
    for subreddit in priority_subreddits:
        for keyword in priority_keywords:
            print(f"🔍 r/{subreddit} + '{keyword}'")
            posts = search_subreddit(subreddit, keyword, limit=25)
            
            if posts:
                all_posts.extend(posts)
                print(f"   ✅ {len(posts)} posts encontrados")
            else:
                print(f"   ⚠️  Sin resultados")
            
            time.sleep(2)  # Rate limiting
    
    if all_posts:
        df_posts = pd.DataFrame(all_posts)
        print(f"\n✅ Total: {len(df_posts)} posts recopilados")
    else:
        print("\n⚠️  No se encontraron posts")
        df_posts = pd.DataFrame()
else:
    print("\n⚠️  Saltando análisis (Reddit API no configurada)")
    df_posts = pd.DataFrame()

# %%
# === ANÁLISIS DE SENTIMIENTO BÁSICO ===
if not df_posts.empty:
    print("\n" + "="*60)
    print("🎭 ANÁLISIS DE SENTIMIENTO (BÁSICO)")
    print("="*60 + "\n")
    
    # Palabras clave de necesidad/oportunidad
    oportunity_keywords = [
        'no encuentro', 'donde comprar', 'alguien sabe', 'recomendaciones',
        'busco', 'necesito', 'ayuda', 'dónde', 'mejor', 'barato',
        'vale la pena', 'worth it', 'looking for', 'recommend', 'help'
    ]
    
    def detect_opportunity(text):
        """Detecta si un post expresa una necesidad/oportunidad"""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in oportunity_keywords)
    
    # Combinar título y texto
    df_posts['full_text'] = df_posts['title'] + ' ' + df_posts['selftext'].fillna('')
    df_posts['is_opportunity'] = df_posts['full_text'].apply(detect_opportunity)
    
    # Filtrar oportunidades
    df_opportunities = df_posts[df_posts['is_opportunity'] == True].copy()
    
    print(f"💡 {len(df_opportunities)} posts identificados como OPORTUNIDADES")
    print(f"   ({len(df_opportunities)/len(df_posts)*100:.1f}% del total)\n")
    
    # Mostrar top oportunidades
    if not df_opportunities.empty:
        top_opps = df_opportunities.nlargest(10, 'score')[['title', 'score', 'num_comments', 'subreddit', 'permalink']]
        print("🔥 Top 10 Oportunidades (por score):\n")
        for idx, row in top_opps.iterrows():
            print(f"📌 {row['title'][:80]}...")
            print(f"   ⬆️  {row['score']} | 💬 {row['num_comments']} | r/{row['subreddit']}")
            print(f"   🔗 {row['permalink']}\n")

# %%
# === ANÁLISIS DE FRECUENCIA DE PALABRAS ===
if not df_posts.empty:
    print("\n" + "="*60)
    print("📊 PALABRAS MÁS FRECUENTES")
    print("="*60 + "\n")
    
    def clean_text(text):
        """Limpia y tokeniza texto"""
        # Lowercase y eliminar caracteres especiales
        text = re.sub(r'[^a-zA-Z0-9\s]', '', text.lower())
        # Dividir en palabras
        words = text.split()
        # Filtrar stopwords básicas
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
                     'of', 'is', 'it', 'that', 'this', 'with', 'as', 'be', 'are', 'i', 'my',
                     'de', 'la', 'el', 'en', 'y', 'que', 'por', 'para', 'con', 'un', 'una'}
        words = [w for w in words if len(w) > 3 and w not in stopwords]
        return words
    
    # Procesar todo el texto
    all_words = []
    for text in df_posts['full_text']:
        all_words.extend(clean_text(str(text)))
    
    # Contar frecuencias
    word_freq = Counter(all_words)
    top_words = pd.DataFrame(word_freq.most_common(30), columns=['palabra', 'frecuencia'])
    
    print(top_words.head(20))
    
    # Visualizar
    fig = px.bar(
        top_words.head(20),
        x='frecuencia',
        y='palabra',
        orientation='h',
        title='📊 Top 20 Palabras Más Mencionadas',
        labels={'frecuencia': 'Frecuencia', 'palabra': 'Palabra'},
        height=600,
        color='frecuencia',
        color_continuous_scale='Teal'
    )
    
    fig.update_layout(
        yaxis={'categoryorder':'total ascending'},
        template='plotly_white'
    )
    
    fig.show()

# %%
# === ANÁLISIS POR SUBREDDIT ===
if not df_posts.empty:
    print("\n" + "="*60)
    print("📈 ANÁLISIS POR SUBREDDIT")
    print("="*60 + "\n")
    
    subreddit_stats = df_posts.groupby('subreddit').agg({
        'id': 'count',
        'score': ['mean', 'max'],
        'num_comments': ['mean', 'max'],
        'is_opportunity': 'sum'
    }).round(2)
    
    subreddit_stats.columns = ['_'.join(col).strip() for col in subreddit_stats.columns.values]
    subreddit_stats = subreddit_stats.rename(columns={
        'id_count': 'total_posts',
        'score_mean': 'score_promedio',
        'score_max': 'score_max',
        'num_comments_mean': 'comentarios_promedio',
        'num_comments_max': 'comentarios_max',
        'is_opportunity_sum': 'oportunidades'
    })
    
    subreddit_stats = subreddit_stats.sort_values('oportunidades', ascending=False)
    
    print(subreddit_stats)
    
    # Visualizar
    fig = px.scatter(
        subreddit_stats.reset_index(),
        x='total_posts',
        y='oportunidades',
        size='score_promedio',
        color='comentarios_promedio',
        hover_name='subreddit',
        title='🎯 Subreddits: Posts vs Oportunidades',
        labels={
            'total_posts': 'Total de Posts',
            'oportunidades': 'Posts con Oportunidades',
            'score_promedio': 'Score Promedio',
            'comentarios_promedio': 'Comentarios Promedio'
        },
        height=500
    )
    
    fig.update_layout(template='plotly_white')
    fig.show()

# %%
# === TENDENCIAS TEMPORALES ===
if not df_posts.empty:
    print("\n" + "="*60)
    print("📅 ACTIVIDAD TEMPORAL")
    print("="*60 + "\n")
    
    # Agregar columna de mes
    df_posts['mes'] = df_posts['created_utc'].dt.to_period('M')
    
    # Contar posts por mes
    temporal = df_posts.groupby('mes').agg({
        'id': 'count',
        'is_opportunity': 'sum'
    }).rename(columns={'id': 'total_posts', 'is_opportunity': 'oportunidades'})
    
    temporal.index = temporal.index.to_timestamp()
    
    # Visualizar
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=temporal.index,
        y=temporal['total_posts'],
        name='Total Posts',
        line=dict(color='blue', width=2)
    ))
    
    fig.add_trace(go.Scatter(
        x=temporal.index,
        y=temporal['oportunidades'],
        name='Oportunidades',
        line=dict(color='red', width=2, dash='dash')
    ))
    
    fig.update_layout(
        title='📅 Actividad en Reddit a lo Largo del Tiempo',
        xaxis_title='Fecha',
        yaxis_title='Número de Posts',
        height=400,
        template='plotly_white',
        hovermode='x unified'
    )
    
    fig.show()

# %%
# === EXPORTAR DATOS ===
if not df_posts.empty:
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Exportar posts completos
    df_posts.to_csv(f'data/processed/reddit_posts_{timestamp}.csv', index=False, encoding='utf-8-sig')
    
    # Exportar solo oportunidades
    if not df_opportunities.empty:
        df_opportunities.to_csv(f'data/analytics/reddit_opportunities_{timestamp}.csv', index=False, encoding='utf-8-sig')
    
    # Exportar estadísticas de subreddits
    subreddit_stats.to_csv(f'data/analytics/reddit_subreddit_stats_{timestamp}.csv', encoding='utf-8-sig')
    
    print(f"\n✅ Datos exportados con timestamp: {timestamp}")

# %%
# === RECOMENDACIONES ===
if not df_posts.empty:
    print("\n" + "="*60)
    print("💡 INSIGHTS DE REDDIT")
    print("="*60 + "\n")
    
    print("🎯 PRINCIPALES HALLAZGOS:\n")
    
    # Subreddit más activo
    top_sub = subreddit_stats.index[0]
    print(f"1. Subreddit más prometedor: r/{top_sub}")
    print(f"   - {subreddit_stats.loc[top_sub, 'oportunidades']:.0f} oportunidades detectadas")
    print(f"   - Score promedio: {subreddit_stats.loc[top_sub, 'score_promedio']:.1f}")
    
    # Palabras clave emergentes
    print(f"\n2. Top 5 palabras clave emergentes:")
    for i, row in top_words.head(5).iterrows():
        print(f"   - {row['palabra']} ({row['frecuencia']} menciones)")
    
    print("\n3. Próximos pasos:")
    print("   - Monitorear r/Flipping y r/ThriftStoreHauls semanalmente")
    print("   - Crear alertas para keywords de alta demanda")
    print("   - Participar en comunidades para entender mejor las necesidades")
    
    print("\n📋 ACCIÓN RECOMENDADA:")
    print("   Cruza estos datos con Mercado Libre y Google Trends")
    print("   para identificar el nicho con mejor score combinado")
