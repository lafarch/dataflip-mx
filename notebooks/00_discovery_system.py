# %% [markdown]
# # 🔍 DataFlip MX - Descubrimiento de Nichos Rentables
# 
# **Objetivo:** Explorar sistemáticamente categorías de Mercado Libre para descubrir nichos con:
# - Alta demanda (ventas comprobadas)
# - Baja competencia (pocos listings)
# - Márgenes atractivos (rango de precios amplio)

# %%
# === IMPORTAR LIBRERÍAS ===
import requests
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time
from typing import List, Dict
import warnings
warnings.filterwarnings('ignore')

print("✅ Librerías importadas correctamente")

# %%
# === CONFIGURACIÓN CON HEADERS MEJORADOS ===
BASE_URL = "https://api.mercadolibre.com"
SITE_ID = "MLM"  # México
REQUEST_DELAY = 2  # Aumentado para evitar rate limiting

# Headers que simulan un navegador real
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json',
    'Accept-Language': 'es-MX,es;q=0.9,en;q=0.8',
    'Referer': 'https://www.mercadolibre.com.mx/',
    'Origin': 'https://www.mercadolibre.com.mx'
}

# Parámetros de búsqueda
MIN_SOLD_QUANTITY = 50  # Mínimo de ventas para considerar el producto
MAX_LISTINGS = 30       # Máximo de listings (baja competencia)
MIN_PRICE = 200         # Precio mínimo (evitar productos muy baratos)
MAX_PRICE = 5000        # Precio máximo (enfoque en ticket medio)

print("🎯 Parámetros de búsqueda configurados")

# %%
# === FUNCIONES DE EXPLORACIÓN MEJORADAS ===

def make_request(url: str, params: dict = None, max_retries: int = 3) -> dict:
    """
    Hace un request con reintentos y manejo de errores mejorado
    """
    for attempt in range(max_retries):
        try:
            response = requests.get(
                url, 
                params=params, 
                headers=HEADERS,
                timeout=15
            )
            
            # Si recibimos 403, intentar sin algunos headers
            if response.status_code == 403 and attempt < max_retries - 1:
                print(f"⚠️  403 recibido, reintentando sin Origin/Referer...")
                time.sleep(REQUEST_DELAY * 2)
                
                # Intentar con headers más simples
                simple_headers = {
                    'User-Agent': HEADERS['User-Agent'],
                    'Accept': 'application/json'
                }
                response = requests.get(url, params=params, headers=simple_headers, timeout=15)
            
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                print(f"❌ Error 403 (Forbidden) - Intento {attempt + 1}/{max_retries}")
                if attempt < max_retries - 1:
                    wait_time = REQUEST_DELAY * (attempt + 2)
                    print(f"   Esperando {wait_time}s antes de reintentar...")
                    time.sleep(wait_time)
                else:
                    print("\n💡 SOLUCIÓN: La API de MercadoLibre está bloqueando el acceso.")
                    print("   Opciones:")
                    print("   1. Usar un VPN")
                    print("   2. Esperar unos minutos y reintentar")
                    print("   3. Usar el approach alternativo con búsquedas directas (ver más abajo)")
                    return {}
            else:
                print(f"❌ Error HTTP {e.response.status_code}: {e}")
                return {}
        
        except Exception as e:
            print(f"❌ Error: {e}")
            if attempt < max_retries - 1:
                time.sleep(REQUEST_DELAY)
            else:
                return {}
    
    return {}

def get_all_categories(site_id: str = SITE_ID) -> pd.DataFrame:
    """
    Obtiene todas las categorías y subcategorías de Mercado Libre
    """
    url = f"{BASE_URL}/sites/{site_id}/categories"
    
    data = make_request(url)
    
    if data:
        df = pd.DataFrame(data)
        print(f"✅ {len(df)} categorías principales encontradas")
        return df
    else:
        print("⚠️  No se pudieron obtener categorías. Usando approach alternativo...")
        return pd.DataFrame()

def search_products(query: str, limit: int = 50, sort: str = 'relevance') -> List[Dict]:
    """
    Busca productos por término de búsqueda (approach alternativo)
    """
    url = f"{BASE_URL}/sites/{SITE_ID}/search"
    params = {
        'q': query,
        'limit': limit,
        'sort': sort
    }
    
    data = make_request(url, params)
    
    if data and 'results' in data:
        print(f"✅ {len(data['results'])} productos encontrados para '{query}'")
        return data['results']
    return []

def search_in_category(category_id: str, sort: str = 'sold_quantity_desc', limit: int = 50) -> List[Dict]:
    """
    Busca productos en una categoría específica
    """
    url = f"{BASE_URL}/sites/{SITE_ID}/search"
    params = {
        'category': category_id,
        'limit': limit,
        'sort': sort,
        'offset': 0
    }
    
    data = make_request(url, params)
    
    if data and 'results' in data:
        return data['results']
    return []

def parse_product(item: Dict) -> Dict:
    """
    Extrae información relevante de un producto
    """
    return {
        'id': item.get('id'),
        'titulo': item.get('title'),
        'precio': item.get('price'),
        'vendidos': item.get('sold_quantity', 0),
        'condicion': item.get('condition'),
        'envio_gratis': item.get('shipping', {}).get('free_shipping', False),
        'categoria_id': item.get('category_id'),
        'vendedor_id': item.get('seller', {}).get('id'),
        'link': item.get('permalink'),
    }

# %%
# === APPROACH ALTERNATIVO: BÚSQUEDA DIRECTA POR KEYWORDS ===
print("\n" + "="*60)
print("🎯 APPROACH ALTERNATIVO: BÚSQUEDA POR KEYWORDS")
print("="*60 + "\n")

# Lista de keywords seed para explorar nichos
SEED_KEYWORDS = [
    # Tecnología retro
    'calculadora financiera',
    'ipod classic',
    'game boy advance',
    'nintendo ds',
    'camara digital vintage',
    'walkman cassette',
    
    # Hobbies/Coleccionables
    'teclado mecanico',
    'cartas pokemon',
    'funko pop',
    'vinyl records',
    'lego sets',
    
    # Fitness/Salud
    'pesas rusas',
    'banda elastica ejercicio',
    'yoga mat premium',
    
    # Moda/Accesorios
    'reloj vintage',
    'lentes ray ban',
    'mochila outdoor',
]

print("📝 Keywords seed a explorar:")
for i, kw in enumerate(SEED_KEYWORDS, 1):
    print(f"   {i}. {kw}")

# %%
# === EXPLORACIÓN POR KEYWORDS ===
print("\n" + "="*60)
print("🔍 EXPLORANDO NICHOS...")
print("="*60 + "\n")

all_products = []
failed_searches = []

for keyword in SEED_KEYWORDS[:5]:  # Empezar con las primeras 5
    print(f"\n🔎 Buscando: '{keyword}'")
    
    # Buscar productos ordenados por más vendidos
    products = search_products(keyword, limit=50, sort='sold_quantity_desc')
    
    if products:
        # Parsear productos
        parsed = [parse_product(p) for p in products]
        
        # Agregar keyword para tracking
        for p in parsed:
            p['keyword_seed'] = keyword
        
        all_products.extend(parsed)
        
        print(f"   ✅ {len(parsed)} productos agregados")
        
        # Mostrar top 3 más vendidos
        df_temp = pd.DataFrame(parsed)
        top_3 = df_temp.nlargest(3, 'vendidos')
        print(f"   🔥 Top 3 más vendidos:")
        for idx, row in top_3.iterrows():
            print(f"      - {row['titulo'][:50]}... (${row['precio']:,.0f} | {row['vendidos']} vendidos)")
    else:
        failed_searches.append(keyword)
        print(f"   ❌ Sin resultados")
    
    # Rate limiting
    time.sleep(REQUEST_DELAY)

# Crear DataFrame master
if all_products:
    df_discovery = pd.DataFrame(all_products)
    print(f"\n✅ Total recopilado: {len(df_discovery)} productos de {len(SEED_KEYWORDS[:5])} keywords")
else:
    print("\n❌ No se pudieron recopilar productos")
    df_discovery = pd.DataFrame()

# %%
# === ANÁLISIS DE OPORTUNIDADES ===
if not df_discovery.empty:
    print("\n" + "="*60)
    print("💡 ANÁLISIS DE OPORTUNIDADES")
    print("="*60 + "\n")
    
    # Filtrar productos con criterios de oportunidad
    df_opportunities = df_discovery[
        (df_discovery['vendidos'] >= MIN_SOLD_QUANTITY) &
        (df_discovery['precio'] >= MIN_PRICE) &
        (df_discovery['precio'] <= MAX_PRICE)
    ].copy()
    
    print(f"Productos que cumplen criterios: {len(df_opportunities)}/{len(df_discovery)}")
    
    if not df_opportunities.empty:
        # Agrupar por keyword seed
        opp_by_keyword = df_opportunities.groupby('keyword_seed').agg({
            'id': 'count',
            'precio': ['mean', 'min', 'max', 'std'],
            'vendidos': ['sum', 'mean', 'max']
        }).round(2)
        
        opp_by_keyword.columns = ['_'.join(col).strip() for col in opp_by_keyword.columns.values]
        opp_by_keyword = opp_by_keyword.rename(columns={
            'id_count': 'num_productos',
            'precio_mean': 'precio_promedio',
            'precio_std': 'precio_std',
            'vendidos_sum': 'total_vendidos',
            'vendidos_mean': 'vendidos_promedio'
        })
        
        # Calcular score de oportunidad
        opp_by_keyword['cv_precio'] = (
            opp_by_keyword['precio_std'] / opp_by_keyword['precio_promedio']
        ).round(2)
        
        # Score simple: ventas altas + variación de precio alta = oportunidad
        opp_by_keyword['opportunity_score'] = (
            (opp_by_keyword['total_vendidos'] / opp_by_keyword['total_vendidos'].max() * 5) +
            (opp_by_keyword['cv_precio'] / opp_by_keyword['cv_precio'].max() * 5)
        ).round(2)
        
        opp_by_keyword = opp_by_keyword.sort_values('opportunity_score', ascending=False)
        
        print("\n🏆 RANKING DE NICHOS (por opportunity score):\n")
        print(opp_by_keyword[['opportunity_score', 'num_productos', 'precio_promedio', 'total_vendidos', 'cv_precio']])

# %%
# === VISUALIZACIÓN: PRECIO VS VENTAS ===
if not df_opportunities.empty:
    fig = px.scatter(
        df_opportunities,
        x='precio',
        y='vendidos',
        color='keyword_seed',
        size='vendidos',
        hover_data=['titulo', 'precio', 'vendidos'],
        title='💰 Precio vs Volumen de Ventas por Nicho',
        labels={'precio': 'Precio (MXN)', 'vendidos': 'Unidades Vendidas'},
        height=600
    )
    
    fig.update_layout(
        template='plotly_white',
        xaxis_type='log',  # Escala logarítmica para mejor visualización
        yaxis_type='log'
    )
    
    fig.show()

# %%
# === ANÁLISIS PROFUNDO: MEJOR NICHO ===
if not df_opportunities.empty and not opp_by_keyword.empty:
    print("\n" + "="*60)
    print("🎯 ANÁLISIS PROFUNDO DEL MEJOR NICHO")
    print("="*60 + "\n")
    
    best_niche = opp_by_keyword.index[0]
    
    print(f"🥇 NICHO GANADOR: {best_niche.upper()}\n")
    
    # Filtrar productos de ese nicho
    df_best = df_opportunities[df_opportunities['keyword_seed'] == best_niche].copy()
    
    print(f"📊 Estadísticas:")
    print(f"   - Productos analizados: {len(df_best)}")
    print(f"   - Precio promedio: ${df_best['precio'].mean():,.2f} MXN")
    print(f"   - Precio mínimo: ${df_best['precio'].min():,.2f} MXN")
    print(f"   - Precio máximo: ${df_best['precio'].max():,.2f} MXN")
    print(f"   - Total vendidos: {df_best['vendidos'].sum():,} unidades")
    print(f"   - Promedio vendidos: {df_best['vendidos'].mean():.0f} unidades/producto")
    
    # Top 10 productos más vendidos de ese nicho
    print(f"\n🔥 TOP 10 PRODUCTOS MÁS VENDIDOS:\n")
    top_10 = df_best.nlargest(10, 'vendidos')
    for i, (idx, row) in enumerate(top_10.iterrows(), 1):
        print(f"{i}. {row['titulo'][:70]}...")
        print(f"   💰 ${row['precio']:,.2f} | 📦 {row['vendidos']} vendidos")
        print(f"   🔗 {row['link']}\n")

# %%
# === RECOMENDACIONES FINALES ===
if not df_opportunities.empty:
    print("\n" + "="*60)
    print("✅ RECOMENDACIONES")
    print("="*60 + "\n")
    
    print("📋 PRÓXIMOS PASOS:\n")
    print(f"1. Profundizar análisis del nicho: {best_niche}")
    print(f"   - Ejecutar notebook 01_mercadolibre_api.ipynb con este nicho específico")
    print(f"   - Validar demanda con Google Trends")
    print(f"   - Buscar menciones en Reddit\n")
    
    print("2. Sourcing:")
    print("   - Buscar proveedores en tianguis/segunda mano")
    print("   - Calcular precio de compra objetivo (40-60% del precio de venta)")
    print(f"   - Objetivo: comprar a ~${df_best['precio'].mean() * 0.5:,.2f} MXN\n")
    
    print("3. Validación:")
    print("   - Comprar 2-3 unidades para prueba")
    print("   - Listar en Mercado Libre")
    print("   - Medir conversion rate en 2 semanas\n")
    
    print("💡 TIP: Si este nicho no funciona, probar con los siguientes")
    print("    del ranking de opportunity_score")

# %%
# === EXPORTAR DATOS ===
if not df_discovery.empty:
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Exportar productos descubiertos
    df_discovery.to_csv(
        f'data/processed/discovery_productos_{timestamp}.csv',
        index=False,
        encoding='utf-8-sig'
    )
    
    # Exportar ranking de oportunidades
    if not opp_by_keyword.empty:
        opp_by_keyword.to_csv(
            f'data/analytics/discovery_ranking_{timestamp}.csv',
            encoding='utf-8-sig'
        )
    
    print(f"\n💾 Datos exportados con timestamp: {timestamp}")
    print("   - data/processed/discovery_productos_[timestamp].csv")
    print("   - data/analytics/discovery_ranking_[timestamp].csv")

# %%
# === TROUBLESHOOTING GUIDE ===
print("\n" + "="*60)
print("🔧 TROUBLESHOOTING")
print("="*60 + "\n")

print("Si sigues teniendo problemas con la API de MercadoLibre:\n")
print("1. Error 403 Forbidden:")
print("   - Tu IP puede estar temporalmente bloqueada")
print("   - Solución: Espera 30-60 minutos antes de reintentar")
print("   - O usa un VPN para cambiar tu IP\n")

print("2. Rate Limiting:")
print("   - Aumenta REQUEST_DELAY a 3-5 segundos")
print("   - Reduce el número de keywords seed a explorar\n")

print("3. Alternative approach:")
print("   - Si la API no funciona, usa el notebook 01 directamente")
print("   - Ese notebook usa búsquedas simples que rara vez fallan")
print("   - Solo necesitas definir tus NICHOS manualmente\n")

if failed_searches:
    print(f"⚠️  Búsquedas que fallaron: {', '.join(failed_searches)}")