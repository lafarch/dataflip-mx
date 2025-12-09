# %% [markdown]
# # 🎯 DataFlip MX - Análisis Integrado y Scorecard Final
# 
# **Objetivo:** Combinar datos de Mercado Libre, Google Trends y Reddit para generar el ranking definitivo de nichos

# %%
# === IMPORTAR LIBRERÍAS ===
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import glob
import os

print("✅ Librerías importadas correctamente")

# %%
# === CARGAR DATOS DE ANÁLISIS ANTERIORES ===
print("\n" + "="*60)
print("📂 CARGANDO DATOS DE ANÁLISIS PREVIOS")
print("="*60 + "\n")

def load_latest_file(pattern: str) -> pd.DataFrame:
    """Carga el archivo más reciente que coincida con el patrón"""
    files = glob.glob(pattern)
    if not files:
        print(f"⚠️  No se encontraron archivos para: {pattern}")
        return pd.DataFrame()
    
    latest_file = max(files, key=os.path.getctime)
    print(f"✅ Cargando: {latest_file}")
    return pd.read_csv(latest_file, encoding='utf-8-sig')

# Cargar datos
df_meli_scorecard = load_latest_file('data/analytics/meli_scorecard_*.csv')
df_trends_scores = load_latest_file('data/analytics/trends_scores_*.csv')

# Si no hay datos guardados, crear DataFrames de ejemplo
if df_meli_scorecard.empty:
    print("\n⚠️  Creando datos de ejemplo para Mercado Libre...")
    df_meli_scorecard = pd.DataFrame({
        'nicho': ['calculadora financiera HP 12C', 'game boy advance', 'teclado mecanico'],
        'SCORE_TOTAL': [7.5, 6.8, 8.2],
        'score_volumen': [6.0, 7.5, 8.0],
        'score_competencia': [8.0, 6.0, 7.5],
        'score_margen': [8.5, 7.0, 9.0],
        'score_logistica': [7.0, 6.5, 8.5],
        'precio_promedio': [850, 1200, 1500]
    })

if df_trends_scores.empty:
    print("⚠️  Creando datos de ejemplo para Google Trends...")
    df_trends_scores = pd.DataFrame({
        'keyword': ['calculadora financiera', 'game boy', 'teclado mecanico'],
        'score_final': [6.8, 7.2, 8.5],
        'interes_promedio': [45, 52, 68],
        'tendencia': [0.05, -0.02, 0.15]
    })

print("\n📊 Datos cargados:")
print(f"   - Mercado Libre: {len(df_meli_scorecard)} nichos")
print(f"   - Google Trends: {len(df_trends_scores)} keywords")

# %%
# === NORMALIZAR Y COMBINAR DATOS ===
print("\n" + "="*60)
print("🔗 INTEGRANDO DATOS DE MÚLTIPLES FUENTES")
print("="*60 + "\n")

# Normalizar nombres de nichos/keywords para matching
def normalize_name(name: str) -> str:
    """Normaliza nombres para poder hacer matching entre datasets"""
    name = name.lower().strip()
    # Remover palabras comunes
    replacements = {
        'hp 12c': '',
        'advance': '',
        'mecanico': '',
        'mecánico': ''
    }
    for old, new in replacements.items():
        name = name.replace(old, new)
    return name.strip()

# Agregar columna normalizada
if 'nicho' in df_meli_scorecard.columns:
    df_meli_scorecard['nicho_norm'] = df_meli_scorecard['nicho'].apply(normalize_name)
if 'keyword' in df_trends_scores.columns:
    df_trends_scores['keyword_norm'] = df_trends_scores['keyword'].apply(normalize_name)

# Hacer merge (unir datasets)
df_integrated = pd.merge(
    df_meli_scorecard,
    df_trends_scores,
    left_on='nicho_norm',
    right_on='keyword_norm',
    how='outer',
    suffixes=('_meli', '_trends')
)

# Llenar valores faltantes con valores por defecto
df_integrated['SCORE_TOTAL'] = df_integrated['SCORE_TOTAL'].fillna(5.0)
df_integrated['score_final'] = df_integrated['score_final'].fillna(5.0)

print(f"✅ Dataset integrado: {len(df_integrated)} nichos")
print(f"\n{df_integrated[['nicho', 'SCORE_TOTAL', 'score_final']].head()}")

# %%
# === SCORECARD FINAL (Framework Completo) ===
print("\n" + "="*60)
print("⭐ CALCULANDO SCORECARD FINAL")
print("="*60 + "\n")

def calculate_final_score(row):
    """
    Calcula el score final combinando todas las fuentes
    
    Pesos:
    - Mercado Libre (40%): Datos de competencia y márgenes reales
    - Google Trends (35%): Validación de demanda
    - Reddit (15%): Análisis cualitativo (si disponible)
    - Ajustes (10%): Factores adicionales
    """
    # Score base de Mercado Libre
    meli_score = row.get('SCORE_TOTAL', 5.0)
    
    # Score de Google Trends
    trends_score = row.get('score_final', 5.0)
    
    # Reddit score (si no existe, usar valor neutro)
    reddit_score = 5.0  # Placeholder - agregar cuando tengamos datos
    
    # Ajuste por tendencia (si está creciendo, bonus)
    trend_direction = row.get('tendencia', 0)
    trend_bonus = min(1.0, max(-1.0, trend_direction * 10))  # -1 a +1
    
    # Ajuste por precio (productos baratos = más fácil logística)
    price = row.get('precio_promedio', 1000)
    price_bonus = 1.0 if price < 1000 else (0.5 if price < 3000 else 0)
    
    # Cálculo weighted
    final_score = (
        meli_score * 0.40 +
        trends_score * 0.35 +
        reddit_score * 0.15 +
        (5 + trend_bonus + price_bonus) * 0.10
    )
    
    return round(final_score, 2)

# Aplicar cálculo
df_integrated['SCORE_FINAL'] = df_integrated.apply(calculate_final_score, axis=1)

# Crear nombre limpio para mostrar
df_integrated['nombre_nicho'] = df_integrated['nicho'].fillna(df_integrated['keyword'])

# Ordenar por score final
df_scorecard = df_integrated.sort_values('SCORE_FINAL', ascending=False)

print("🏆 TOP 10 NICHOS RANKEADOS:\n")
display_cols = ['nombre_nicho', 'SCORE_FINAL', 'SCORE_TOTAL', 'score_final', 'precio_promedio']
available_cols = [col for col in display_cols if col in df_scorecard.columns]
print(df_scorecard[available_cols].head(10).to_string(index=False))

# %%
# === VISUALIZACIÓN: SCORECARD COMPLETO ===
if not df_scorecard.empty:
    top_nichos = df_scorecard.head(10).copy()
    
    fig = go.Figure()
    
    # Score final (barra principal)
    fig.add_trace(go.Bar(
        name='Score Final',
        x=top_nichos['nombre_nicho'],
        y=top_nichos['SCORE_FINAL'],
        marker_color='#2E86AB',
        text=top_nichos['SCORE_FINAL'],
        textposition='outside'
    ))
    
    # Score de Mercado Libre (componente)
    fig.add_trace(go.Bar(
        name='Mercado Libre',
        x=top_nichos['nombre_nicho'],
        y=top_nichos['SCORE_TOTAL'],
        marker_color='#FFE66D',
        visible='legendonly'
    ))
    
    # Score de Google Trends (componente)
    fig.add_trace(go.Bar(
        name='Google Trends',
        x=top_nichos['nombre_nicho'],
        y=top_nichos['score_final'],
        marker_color='#06A77D',
        visible='legendonly'
    ))
    
    fig.update_layout(
        title='🏆 Scorecard Final de Nichos (Top 10)',
        xaxis_title='Nicho',
        yaxis_title='Score (1-10)',
        yaxis_range=[0, 10.5],
        height=600,
        template='plotly_white',
        xaxis_tickangle=-45,
        barmode='group',
        showlegend=True
    )
    
    fig.show()

# %%
# === ANÁLISIS DIMENSIONAL ===
if not df_scorecard.empty and 'SCORE_TOTAL' in df_scorecard.columns and 'score_final' in df_scorecard.columns:
    print("\n" + "="*60)
    print("📊 ANÁLISIS DIMENSIONAL (Mercado Libre vs Google Trends)")
    print("="*60 + "\n")
    
    fig = px.scatter(
        df_scorecard.head(15),
        x='SCORE_TOTAL',
        y='score_final',
        size='SCORE_FINAL',
        color='SCORE_FINAL',
        hover_name='nombre_nicho',
        hover_data=['precio_promedio'],
        text='nombre_nicho',
        title='📈 Mercado Libre vs Google Trends',
        labels={
            'SCORE_TOTAL': 'Score Mercado Libre (Competencia + Margen)',
            'score_final': 'Score Google Trends (Demanda)',
            'SCORE_FINAL': 'Score Final'
        },
        color_continuous_scale='Viridis',
        height=600
    )
    
    # Línea diagonal (equilibrio perfecto)
    fig.add_trace(go.Scatter(
        x=[0, 10],
        y=[0, 10],
        mode='lines',
        line=dict(dash='dash', color='gray'),
        name='Equilibrio',
        showlegend=True
    ))
    
    fig.update_traces(textposition='top center')
    fig.update_layout(template='plotly_white')
    
    fig.show()
    
    print("💡 INTERPRETACIÓN:")
    print("   - Arriba de la línea: Alta demanda, baja competencia (IDEAL)")
    print("   - Abajo de la línea: Buena oferta, pero poca demanda (RIESGOSO)")
    print("   - Cerca de la línea: Equilibrio entre oferta y demanda")

# %%
# === RECOMENDACIONES POR PERFIL ===
print("\n" + "="*60)
print("🎯 RECOMENDACIONES PERSONALIZADAS")
print("="*60 + "\n")

if not df_scorecard.empty:
    # Nicho #1
    top_niche = df_scorecard.iloc[0]
    
    print(f"🥇 NICHO GANADOR: {top_niche['nombre_nicho']}")
    print(f"   Score Final: {top_niche['SCORE_FINAL']:.2f}/10")
    print(f"   Score Mercado Libre: {top_niche.get('SCORE_TOTAL', 'N/A'):.2f}")
    print(f"   Score Google Trends: {top_niche.get('score_final', 'N/A'):.2f}")
    
    if 'precio_promedio' in top_niche and pd.notna(top_niche['precio_promedio']):
        print(f"   Precio Promedio: ${top_niche['precio_promedio']:,.2f} MXN")
    
    print("\n📋 ESTRATEGIA RECOMENDADA:\n")
    
    # Estrategia basada en score
    score = top_niche['SCORE_FINAL']
    
    if score >= 8.0:
        print("✅ EXCELENTE OPORTUNIDAD")
        print("   1. Iniciar con este nicho AHORA")
        print("   2. Comprar inventario pequeño para validar (5-10 unidades)")
        print("   3. Publicar en Mercado Libre con fotos profesionales")
        print("   4. Medir conversion rate en primeras 2 semanas")
        
    elif score >= 6.5:
        print("⚠️  BUENA OPORTUNIDAD CON VALIDACIÓN")
        print("   1. Validar primero con 2-3 unidades")
        print("   2. Analizar competencia directa en detalle")
        print("   3. Buscar proveedores de confianza")
        print("   4. Escalar solo si ROI > 40%")
        
    else:
        print("🤔 OPORTUNIDAD MODERADA")
        print("   1. Considerar nichos alternativos primero")
        print("   2. Buscar sub-nichos menos competidos")
        print("   3. Validar con presupuesto mínimo")
    
    # Timeline
    print("\n📅 TIMELINE SUGERIDO (Fase 1: Nov-Dic 2024):")
    print("   Semana 1: Sourcing (tianguis, Marketplace)")
    print("   Semana 2-3: Listing y primeras ventas")
    print("   Semana 4-6: Iteración y escala")
    print("   Semana 7-8: Liquidación antes de viaje")
    
    print("\n🌍 FASE 2 (Desde Holanda - Feb 2025+):")
    print("   - Migrar a Print on Demand (Printful + Shopify)")
    print("   - Usar este nicho como inspiración para diseños")
    print("   - Marketing digital desde Europa")

# %%
# === MATRIZ DE DECISIÓN ===
if not df_scorecard.empty:
    print("\n" + "="*60)
    print("🎲 MATRIZ DE DECISIÓN")
    print("="*60 + "\n")
    
    # Crear categorías
    def categorize_niche(row):
        """Categoriza el nicho según sus características"""
        score = row['SCORE_FINAL']
        meli_score = row.get('SCORE_TOTAL', 5)
        trends_score = row.get('score_final', 5)
        
        if score >= 8 and trends_score >= 7.5:
            return '🔥 QUICK WIN'
        elif score >= 7 and meli_score >= 7.5:
            return '💰 CASH COW'
        elif trends_score >= 8 and meli_score < 6:
            return '🌱 EMERGING'
        elif score >= 6:
            return '⚖️ BALANCED'
        else:
            return '❌ AVOID'
    
    df_scorecard['categoria'] = df_scorecard.apply(categorize_niche, axis=1)
    
    # Contar por categoría
    category_counts = df_scorecard['categoria'].value_counts()
    
    print("Distribución de Nichos por Categoría:\n")
    for cat, count in category_counts.items():
        print(f"{cat}: {count} nichos")
    
    print("\n📖 LEYENDA:")
    print("   🔥 QUICK WIN: Alta demanda + baja competencia → Atacar YA")
    print("   💰 CASH COW: Mercado establecido + buenos márgenes → Seguro")
    print("   🌱 EMERGING: Tendencia creciente → Riesgoso pero potencial alto")
    print("   ⚖️ BALANCED: Equilibrado → Validar antes de escalar")
    print("   ❌ AVOID: Bajo score → Mejor buscar alternativas")

# %%
# === EXPORTAR SCORECARD FINAL ===
if not df_scorecard.empty:
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Crear reporte final
    output_cols = [
        'nombre_nicho', 'SCORE_FINAL', 'SCORE_TOTAL', 'score_final',
        'precio_promedio', 'interes_promedio', 'tendencia', 'categoria'
    ]
    available_output_cols = [col for col in output_cols if col in df_scorecard.columns]
    
    df_report = df_scorecard[available_output_cols].copy()
    
    # Exportar
    filename = f'data/analytics/SCORECARD_FINAL_{timestamp}.csv'
    df_report.to_csv(filename, index=False, encoding='utf-8-sig')
    
    # Exportar también en Excel con formato
    filename_excel = f'data/analytics/SCORECARD_FINAL_{timestamp}.xlsx'
    df_report.to_excel(filename_excel, index=False, sheet_name='Scorecard')
    
    print("\n" + "="*60)
    print("✅ ANÁLISIS COMPLETADO")
    print("="*60)
    print(f"\n💾 Reportes generados:")
    print(f"   - {filename}")
    print(f"   - {filename_excel}")
    
    print("\n🎉 ¡Listo para ejecutar!")
    print("\n📋 SIGUIENTE PASO:")
    print("   Notebook 05: Simulador de Márgenes de Ganancia")
    print("   (Calcular ROI esperado del nicho ganador)")
