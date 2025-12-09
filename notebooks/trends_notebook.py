# %% [markdown]
# # 📈 DataFlip MX - Google Trends Analysis
# 
# **Objetivo:** Validar demanda real de nichos usando datos de búsqueda de Google
# 
# **Docs:** https://github.com/GeneralMills/pytrends

# %%
# === IMPORTAR LIBRERÍAS ===
from pytrends.request import TrendReq
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import warnings
warnings.filterwarnings('ignore')

print("✅ Librerías importadas correctamente")

# %%
# === CONFIGURACIÓN ===
# Inicializar pytrends (sin necesidad de API key)
pytrends = TrendReq(hl='es-MX', tz=360)

# Nichos a analizar (usar los mismos que en Mercado Libre)
KEYWORDS = [
    "calculadora financiera",
    "camara digital vintage",
    "teclado mecanico",
    "game boy",
    "ipod classic",
]

# Configuración de análisis
GEO = 'MX'  # México
TIMEFRAME = 'today 12-m'  # Últimos 12 meses
CATEGORY = 0  # Todas las categorías

print(f"🎯 Analizaremos {len(KEYWORDS)} keywords")
print(f"📍 Geografía: México")
print(f"📅 Período: {TIMEFRAME}")

# %%
# === FUNCIÓN: OBTENER INTERÉS POR TIEMPO ===
def get_interest_over_time(keywords: list, timeframe: str = TIMEFRAME, geo: str = GEO):
    """
    Obtiene el interés de búsqueda a lo largo del tiempo
    
    Args:
        keywords: Lista de palabras clave (máx 5 por request)
        timeframe: Período de análisis
        geo: Código de país
    
    Returns:
        DataFrame con datos de tendencias
    """
    try:
        pytrends.build_payload(keywords, cat=CATEGORY, timeframe=timeframe, geo=geo)
        df = pytrends.interest_over_time()
        
        if not df.empty and 'isPartial' in df.columns:
            df = df.drop('isPartial', axis=1)
        
        return df
    except Exception as e:
        print(f"❌ Error obteniendo datos: {e}")
        return pd.DataFrame()

# %%
# === ANÁLISIS: INTERÉS A LO LARGO DEL TIEMPO ===
print("\n" + "="*60)
print("📊 OBTENIENDO DATOS DE GOOGLE TRENDS")
print("="*60 + "\n")

# Como Google Trends solo permite 5 keywords por request, dividimos si hay más
batches = [KEYWORDS[i:i+5] for i in range(0, len(KEYWORDS), 5)]
all_trends = []

for i, batch in enumerate(batches, 1):
    print(f"🔍 Batch {i}/{len(batches)}: {', '.join(batch)}")
    df_batch = get_interest_over_time(batch)
    
    if not df_batch.empty:
        all_trends.append(df_batch)
        print(f"   ✅ {len(df_batch)} registros obtenidos")
    
    # Respetar rate limits
    if i < len(batches):
        time.sleep(2)

# Combinar resultados
if all_trends:
    df_trends = pd.concat(all_trends, axis=1)
    df_trends = df_trends.loc[:, ~df_trends.columns.duplicated()]  # Eliminar duplicados
    print(f"\n✅ Dataset completo: {df_trends.shape}")
else:
    print("\n❌ No se obtuvieron datos")
    df_trends = pd.DataFrame()

# %%
# === VISUALIZACIÓN: TENDENCIAS TEMPORALES ===
if not df_trends.empty:
    fig = go.Figure()
    
    for keyword in df_trends.columns:
        fig.add_trace(go.Scatter(
            x=df_trends.index,
            y=df_trends[keyword],
            mode='lines',
            name=keyword,
            line=dict(width=2)
        ))
    
    fig.update_layout(
        title='📈 Interés de Búsqueda en Google (Últimos 12 meses)',
        xaxis_title='Fecha',
        yaxis_title='Interés Relativo (0-100)',
        height=500,
        template='plotly_white',
        hovermode='x unified',
        legend=dict(
            orientation="v",
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
    )
    
    fig.show()

# %%
# === ANÁLISIS ESTADÍSTICO ===
if not df_trends.empty:
    print("\n" + "="*60)
    print("📊 ESTADÍSTICAS DE TENDENCIAS")
    print("="*60 + "\n")
    
    stats = df_trends.describe().T
    
    # Agregar métricas adicionales
    stats['tendencia'] = df_trends.apply(lambda x: np.polyfit(range(len(x)), x, 1)[0])
    stats['volatilidad'] = df_trends.std() / df_trends.mean()
    stats['estacionalidad'] = df_trends.max() - df_trends.min()
    
    # Ordenar por interés promedio
    stats = stats.sort_values('mean', ascending=False)
    
    print(stats.round(2))
    
    # Interpretación
    print("\n💡 INTERPRETACIÓN:")
    print("   - mean: Interés promedio (más alto = más búsquedas)")
    print("   - tendencia: Pendiente (positivo = creciendo, negativo = decreciendo)")
    print("   - volatilidad: std/mean (alto = búsquedas inconsistentes)")
    print("   - estacionalidad: Rango max-min (alto = muy estacional)")

# %%
# === BÚSQUEDAS RELACIONADAS ===
print("\n" + "="*60)
print("🔗 BÚSQUEDAS RELACIONADAS (TOP QUERIES)")
print("="*60 + "\n")

related_queries_all = {}

for keyword in KEYWORDS:
    try:
        pytrends.build_payload([keyword], cat=CATEGORY, timeframe=TIMEFRAME, geo=GEO)
        related = pytrends.related_queries()
        
        if keyword in related and related[keyword]['top'] is not None:
            print(f"\n🔍 {keyword.upper()}")
            top_related = related[keyword]['top']
            print(top_related.head(10))
            
            related_queries_all[keyword] = top_related
        
        time.sleep(2)  # Rate limiting
        
    except Exception as e:
        print(f"   ⚠️  Error: {e}")

# %%
# === ANÁLISIS GEOGRÁFICO (MÉXICO) ===
print("\n" + "="*60)
print("🗺️ INTERÉS POR REGIÓN EN MÉXICO")
print("="*60 + "\n")

geo_data_all = {}

for keyword in KEYWORDS[:3]:  # Solo primeros 3 para no saturar
    try:
        pytrends.build_payload([keyword], cat=CATEGORY, timeframe=TIMEFRAME, geo=GEO)
        geo_data = pytrends.interest_by_region(resolution='REGION', inc_low_vol=True)
        
        if not geo_data.empty:
            top_regions = geo_data.sort_values(keyword, ascending=False).head(10)
            print(f"\n📍 {keyword.upper()} - Top 10 Estados:")
            print(top_regions)
            
            geo_data_all[keyword] = geo_data
        
        time.sleep(2)
        
    except Exception as e:
        print(f"   ⚠️  Error: {e}")

# %%
# === VISUALIZACIÓN: HEATMAP DE INTERÉS POR REGIÓN ===
if geo_data_all:
    # Tomar primer keyword
    first_keyword = list(geo_data_all.keys())[0]
    df_geo = geo_data_all[first_keyword].reset_index()
    df_geo.columns = ['Estado', 'Interes']
    
    fig = px.bar(
        df_geo.sort_values('Interes', ascending=True).tail(15),
        x='Interes',
        y='Estado',
        orientation='h',
        title=f'🗺️ Interés por Estado: {first_keyword}',
        labels={'Interes': 'Interés Relativo', 'Estado': ''},
        height=500,
        color='Interes',
        color_continuous_scale='Blues'
    )
    
    fig.update_layout(template='plotly_white')
    fig.show()

# %%
# === DETECCIÓN DE ESTACIONALIDAD ===
if not df_trends.empty:
    print("\n" + "="*60)
    print("📅 ANÁLISIS DE ESTACIONALIDAD")
    print("="*60 + "\n")
    
    # Agregar columna de mes
    df_trends_monthly = df_trends.copy()
    df_trends_monthly['mes'] = df_trends_monthly.index.month
    
    # Promediar por mes
    monthly_avg = df_trends_monthly.groupby('mes').mean()
    
    # Visualizar patrón mensual
    fig = go.Figure()
    
    for keyword in monthly_avg.columns:
        fig.add_trace(go.Scatter(
            x=monthly_avg.index,
            y=monthly_avg[keyword],
            mode='lines+markers',
            name=keyword,
            line=dict(width=2)
        ))
    
    fig.update_layout(
        title='📅 Patrón de Búsqueda por Mes',
        xaxis_title='Mes',
        yaxis_title='Interés Promedio',
        xaxis=dict(
            tickmode='array',
            tickvals=list(range(1, 13)),
            ticktext=['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 
                      'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
        ),
        height=500,
        template='plotly_white'
    )
    
    fig.show()
    
    # Identificar meses pico
    for keyword in monthly_avg.columns:
        peak_month = monthly_avg[keyword].idxmax()
        low_month = monthly_avg[keyword].idxmin()
        print(f"\n🔍 {keyword}")
        print(f"   📈 Pico: Mes {peak_month}")
        print(f"   📉 Bajo: Mes {low_month}")

# %%
# === SCORE DE VOLUMEN (PARA SCORECARD) ===
if not df_trends.empty:
    print("\n" + "="*60)
    print("⭐ SCORE DE VOLUMEN DE BÚSQUEDA")
    print("="*60 + "\n")
    
    volume_scores = pd.DataFrame({
        'keyword': df_trends.columns,
        'interes_promedio': df_trends.mean(),
        'tendencia': df_trends.apply(lambda x: np.polyfit(range(len(x)), x, 1)[0]),
        'volatilidad': df_trends.std() / df_trends.mean(),
    })
    
    # Normalizar a escala 1-10
    volume_scores['score_volumen'] = (
        (volume_scores['interes_promedio'] / volume_scores['interes_promedio'].max()) * 10
    ).round(2)
    
    # Penalizar por volatilidad alta
    volume_scores['score_consistencia'] = (
        10 - (volume_scores['volatilidad'] * 5)
    ).clip(1, 10).round(2)
    
    # Score final
    volume_scores['score_final'] = (
        volume_scores['score_volumen'] * 0.7 + 
        volume_scores['score_consistencia'] * 0.3
    ).round(2)
    
    volume_scores = volume_scores.sort_values('score_final', ascending=False)
    
    print(volume_scores)
    
    # Visualizar
    fig = px.bar(
        volume_scores,
        x='keyword',
        y='score_final',
        color='score_final',
        title='⭐ Score de Volumen de Búsqueda (Google Trends)',
        labels={'score_final': 'Score (1-10)', 'keyword': 'Keyword'},
        height=400,
        color_continuous_scale='Viridis'
    )
    
    fig.update_layout(template='plotly_white', xaxis_tickangle=-45)
    fig.show()

# %%
# === EXPORTAR DATOS ===
if not df_trends.empty:
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Exportar datos de tendencias
    df_trends.to_csv(f'data/processed/trends_timeseries_{timestamp}.csv', encoding='utf-8-sig')
    
    # Exportar estadísticas
    stats.to_csv(f'data/analytics/trends_stats_{timestamp}.csv', encoding='utf-8-sig')
    
    # Exportar scores
    volume_scores.to_csv(f'data/analytics/trends_scores_{timestamp}.csv', index=False, encoding='utf-8-sig')
    
    print(f"\n✅ Datos exportados con timestamp: {timestamp}")

# %%
# === RECOMENDACIONES FINALES ===
if not df_trends.empty:
    print("\n" + "="*60)
    print("🎯 INSIGHTS DE GOOGLE TRENDS")
    print("="*60 + "\n")
    
    top_keyword = volume_scores.iloc[0]['keyword']
    top_score = volume_scores.iloc[0]['score_final']
    
    print(f"🥇 KEYWORD #1: {top_keyword}")
    print(f"   Score: {top_score}/10")
    print(f"   Interés Promedio: {volume_scores.iloc[0]['interes_promedio']:.2f}")
    
    if volume_scores.iloc[0]['tendencia'] > 0:
        print(f"   📈 Tendencia: CRECIENDO (+{volume_scores.iloc[0]['tendencia']:.3f})")
    else:
        print(f"   📉 Tendencia: DECRECIENDO ({volume_scores.iloc[0]['tendencia']:.3f})")
    
    print("\n📋 Próximos pasos:")
    print("   1. Cruzar estos datos con Mercado Libre")
    print("   2. Buscar 'queries relacionadas' con baja competencia")
    print("   3. Validar en Reddit si hay demanda cualitativa")
