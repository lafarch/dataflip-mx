# %% [markdown]
# # 📊 DataFlip MX - Análisis de Mercado Libre
# 
# **Objetivo:** Analizar precios, volumen de ventas y oportunidades en nichos específicos
# 
# **API Docs:** https://developers.mercadolibre.com.mx/

# %%
# === IMPORTAR LIBRERÍAS ===
import requests
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time
import json
from typing import List, Dict
import warnings
warnings.filterwarnings('ignore')

print("✅ Librerías importadas correctamente")

# %%
# === CONFIGURACIÓN ===
# La API pública de Mercado Libre NO requiere autenticación para búsquedas básicas
BASE_URL = "https://api.mercadolibre.com"
SITE_ID = "MLM"  # MLM = México

# Delay entre requests (buena práctica)
REQUEST_DELAY = 1

# Nichos a analizar
NICHOS = [
    "calculadora financiera HP 12C",
    "camara digital vintage",
    "teclado mecanico",
    "game boy advance",
    "ipod classic",
]

print(f"🎯 Analizaremos {len(NICHOS)} nichos")

# %%
# === FUNCIONES AUXILIARES ===

def search_products(query: str, limit: int = 50, site_id: str = SITE_ID) -> Dict:
    """
    Busca productos en Mercado Libre
    
    Args:
        query: Término de búsqueda
        limit: Número máximo de resultados (max 50 por request)
        site_id: Código del país (MLM para México)
    
    Returns:
        Diccionario con resultados de la API
    """
    url = f"{BASE_URL}/sites/{site_id}/search"
    params = {
        'q': query,
        'limit': limit
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"❌ Error en búsqueda '{query}': {e}")
        return {}

def parse_product_data(item: Dict) -> Dict:
    """
    Extrae información relevante de un producto
    
    Args:
        item: Diccionario con datos del producto de la API
    
    Returns:
        Diccionario con datos parseados
    """
    return {
        'id': item.get('id'),
        'titulo': item.get('title'),
        'precio': item.get('price'),
        'moneda': item.get('currency_id'),
        'vendidos': item.get('sold_quantity', 0),
        'condicion': item.get('condition'),  # new / used
        'envio_gratis': item.get('shipping', {}).get('free_shipping', False),
        'link': item.get('permalink'),
        'thumbnail': item.get('thumbnail'),
        'vendedor_id': item.get('seller', {}).get('id'),
        'categoria_id': item.get('category_id'),
    }

def analyze_niche(query: str, limit: int = 50) -> pd.DataFrame:
    """
    Analiza un nicho completo
    
    Args:
        query: Término de búsqueda
        limit: Número de productos a analizar
    
    Returns:
        DataFrame con análisis del nicho
    """
    print(f"\n🔍 Buscando: '{query}'...")
    
    # Hacer request
    results = search_products(query, limit)
    
    if not results or 'results' not in results:
        print(f"   ❌ No se encontraron resultados")
        return pd.DataFrame()
    
    # Parsear productos
    products = [parse_product_data(item) for item in results['results']]
    df = pd.DataFrame(products)
    
    # Agregar metadata
    df['nicho'] = query
    df['fecha_analisis'] = datetime.now()
    
    print(f"   ✅ {len(df)} productos encontrados")
    
    # Respetar rate limits
    time.sleep(REQUEST_DELAY)
    
    return df

# %%
# === ANÁLISIS DE TODOS LOS NICHOS ===
print("\n" + "="*60)
print("📊 INICIANDO ANÁLISIS DE MERCADO")
print("="*60)

all_data = []

for nicho in NICHOS:
    df_nicho = analyze_niche(nicho, limit=50)
    if not df_nicho.empty:
        all_data.append(df_nicho)

# Combinar todos los datos
if all_data:
    df_master = pd.concat(all_data, ignore_index=True)
    print(f"\n✅ Total de productos analizados: {len(df_master)}")
else:
    print("\n❌ No se obtuvieron datos")
    df_master = pd.DataFrame()

# %%
# === ESTADÍSTICAS POR NICHO ===
if not df_master.empty:
    print("\n" + "="*60)
    print("📈 ESTADÍSTICAS POR NICHO")
    print("="*60 + "\n")
    
    stats = df_master.groupby('nicho').agg({
        'precio': ['mean', 'median', 'min', 'max', 'std'],
        'vendidos': ['sum', 'mean', 'max'],
        'id': 'count'
    }).round(2)
    
    stats.columns = ['_'.join(col).strip() for col in stats.columns.values]
    stats = stats.rename(columns={
        'precio_mean': 'precio_promedio',
        'precio_median': 'precio_mediana',
        'precio_min': 'precio_min',
        'precio_max': 'precio_max',
        'precio_std': 'precio_std',
        'vendidos_sum': 'total_vendidos',
        'vendidos_mean': 'vendidos_promedio',
        'vendidos_max': 'vendidos_max',
        'id_count': 'num_productos'
    })
    
    print(stats)

# %%
# === VISUALIZACIÓN: DISTRIBUCIÓN DE PRECIOS ===
if not df_master.empty:
    fig = px.box(
        df_master,
        x='nicho',
        y='precio',
        color='condicion',
        title='📊 Distribución de Precios por Nicho',
        labels={'precio': 'Precio (MXN)', 'nicho': 'Nicho'},
        height=500
    )
    
    fig.update_layout(
        xaxis_tickangle=-45,
        showlegend=True,
        template='plotly_white'
    )
    
    fig.show()

# %%
# === VISUALIZACIÓN: VOLUMEN DE VENTAS ===
if not df_master.empty:
    # Top 20 productos más vendidos
    top_sellers = df_master.nlargest(20, 'vendidos')[['titulo', 'vendidos', 'precio', 'nicho']]
    
    fig = px.bar(
        top_sellers,
        x='vendidos',
        y='titulo',
        color='nicho',
        title='🔥 Top 20 Productos Más Vendidos',
        labels={'vendidos': 'Cantidad Vendida', 'titulo': 'Producto'},
        orientation='h',
        height=600
    )
    
    fig.update_layout(
        yaxis={'categoryorder':'total ascending'},
        showlegend=True,
        template='plotly_white'
    )
    
    fig.show()

# %%
# === ANÁLISIS DE OPORTUNIDADES (GAP ANALYSIS) ===
if not df_master.empty:
    print("\n" + "="*60)
    print("💡 ANÁLISIS DE OPORTUNIDADES")
    print("="*60 + "\n")
    
    # Filtrar productos usados (mayor margen potencial)
    df_used = df_master[df_master['condicion'] == 'used'].copy()
    
    if not df_used.empty:
        # Calcular dispersión de precios (oportunidad = alta dispersión)
        opportunities = df_used.groupby('nicho').agg({
            'precio': ['mean', 'std', 'min', 'max', 'count'],
            'vendidos': 'sum'
        })
        
        opportunities.columns = ['_'.join(col).strip() for col in opportunities.columns.values]
        
        # Coeficiente de variación (std/mean) = dispersión relativa
        opportunities['cv_precio'] = (
            opportunities['precio_std'] / opportunities['precio_mean']
        ).round(2)
        
        # Rango de precio (max - min)
        opportunities['rango_precio'] = (
            opportunities['precio_max'] - opportunities['precio_min']
        ).round(2)
        
        # Ordenar por coeficiente de variación (mayor = más oportunidad)
        opportunities = opportunities.sort_values('cv_precio', ascending=False)
        
        print("🎯 Nichos con MAYOR dispersión de precios (más oportunidad):")
        print("\nCV alto = Puedes encontrar productos baratos y revenderlos caros")
        print(opportunities[['precio_mean', 'cv_precio', 'rango_precio', 'vendidos_sum']])
    else:
        print("⚠️  No se encontraron productos usados en la muestra")

# %%
# === SCORE DE NICHO (FRAMEWORK) ===
if not df_master.empty:
    print("\n" + "="*60)
    print("⭐ SCORECARD DE NICHOS")
    print("="*60 + "\n")
    
    def calculate_niche_score(row, stats_df):
        """
        Calcula el score de un nicho basado en el framework
        
        Criterios:
        - Volumen (25%): Basado en productos vendidos
        - Competencia baja (20%): Basado en número de listings
        - Margen (25%): Basado en rango de precios
        - Facilidad logística (15%): Productos pequeños/digitales
        - Estacionalidad baja (15%): Asumimos consistencia (mejorar con datos históricos)
        """
        nicho = row.name
        
        # 1. Volumen de búsqueda (proxy: total vendido)
        total_vendidos = row['total_vendidos']
        score_volumen = min(10, (total_vendidos / 100)) if total_vendidos > 0 else 1
        
        # 2. Competencia (inverso del número de productos)
        num_productos = row['num_productos']
        score_competencia = max(1, 10 - (num_productos / 10))
        
        # 3. Margen (basado en rango de precios)
        rango = row['precio_max'] - row['precio_min']
        score_margen = min(10, (rango / row['precio_promedio']) * 2) if row['precio_promedio'] > 0 else 1
        
        # 4. Facilidad logística (estimado por precio medio - bajo = más fácil)
        precio_medio = row['precio_promedio']
        score_logistica = 10 if precio_medio < 1000 else (5 if precio_medio < 5000 else 2)
        
        # 5. Estacionalidad (default medio por falta de datos históricos)
        score_estacionalidad = 5
        
        # Calcular weighted score
        score_total = (
            score_volumen * 0.25 +
            score_competencia * 0.20 +
            score_margen * 0.25 +
            score_logistica * 0.15 +
            score_estacionalidad * 0.15
        )
        
        return pd.Series({
            'score_volumen': round(score_volumen, 2),
            'score_competencia': round(score_competencia, 2),
            'score_margen': round(score_margen, 2),
            'score_logistica': round(score_logistica, 2),
            'score_estacionalidad': round(score_estacionalidad, 2),
            'SCORE_TOTAL': round(score_total, 2)
        })
    
    # Calcular scores
    scorecard = stats.apply(calculate_niche_score, axis=1, stats_df=stats)
    scorecard = pd.concat([stats[['precio_promedio', 'num_productos', 'total_vendidos']], scorecard], axis=1)
    scorecard = scorecard.sort_values('SCORE_TOTAL', ascending=False)
    
    print(scorecard)
    
    # Visualizar
    fig = go.Figure()
    
    for col in ['score_volumen', 'score_competencia', 'score_margen', 'score_logistica']:
        fig.add_trace(go.Bar(
            name=col.replace('score_', '').title(),
            x=scorecard.index,
            y=scorecard[col]
        ))
    
    fig.update_layout(
        title='⭐ Scorecard de Nichos por Criterio',
        xaxis_title='Nicho',
        yaxis_title='Score (1-10)',
        barmode='group',
        height=500,
        template='plotly_white',
        xaxis_tickangle=-45
    )
    
    fig.show()

# %%
# === EXPORTAR DATOS ===
if not df_master.empty:
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Exportar dataset completo
    df_master.to_csv(f'data/processed/meli_analisis_{timestamp}.csv', index=False, encoding='utf-8-sig')
    
    # Exportar estadísticas
    stats.to_csv(f'data/analytics/meli_stats_{timestamp}.csv', encoding='utf-8-sig')
    
    # Exportar scorecard
    scorecard.to_csv(f'data/analytics/meli_scorecard_{timestamp}.csv', encoding='utf-8-sig')
    
    print(f"\n✅ Datos exportados a data/processed/ y data/analytics/")
    print(f"   Timestamp: {timestamp}")

# %%
# === RECOMENDACIONES FINALES ===
if not df_master.empty:
    print("\n" + "="*60)
    print("🎯 RECOMENDACIONES BASADAS EN DATOS")
    print("="*60 + "\n")
    
    top_niche = scorecard.index[0]
    top_score = scorecard.iloc[0]['SCORE_TOTAL']
    
    print(f"🥇 NICHO #1: {top_niche}")
    print(f"   Score Total: {top_score}/10")
    print(f"   Precio Promedio: ${scorecard.iloc[0]['precio_promedio']:,.2f} MXN")
    print(f"   Total Vendidos: {int(scorecard.iloc[0]['total_vendidos'])}")
    
    print("\n📋 Próximos pasos:")
    print("   1. Validar este nicho con Google Trends")
    print("   2. Analizar sentiment en Reddit")
    print("   3. Hacer scraping de Amazon MX para comparar precios")
    print("   4. Calcular simulación de márgenes de ganancia")
    
    print("\n💡 TIP: Filtra productos con 'cv_precio' alto para encontrar")
    print("   arbitraje (comprar barato, vender al precio medio)")
