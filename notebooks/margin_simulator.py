# %% [markdown]
# # DataFlip MX - Simulador de Márgenes y Rentabilidad
# 
# **Objetivo:** Calcular la rentabilidad real de cada nicho considerando TODOS los costos operativos
# 
# **Componentes:**
# - Costos directos e indirectos
# - Simulación de escenarios (conservador, realista, optimista)
# - Punto de equilibrio (break-even)
# - Análisis de sensibilidad

# %%
# === IMPORTAR LIBRERÍAS ===
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

print("Librerías importadas correctamente")

# %%
# === DEFINICIÓN DE COSTOS MERCADO LIBRE MÉXICO ===

# Fuente: https://www.mercadolibre.com.mx/ayuda/costos-vender-producto_2443
COSTOS_ML = {
    'comision_venta': 0.16,      # 16% promedio (varía por categoría: 13-16%)
    'comision_mercadopago': 0.0399,  # 3.99% + IVA
    'iva_mercadopago': 0.16,     # IVA del 16% sobre comisión MP
    'envio_promedio': 100,        # MXN - costo promedio de envío si el vendedor lo absorbe
    'embalaje': 25,               # MXN - caja, burbuja, cinta
}

# Costos de tiempo y operación
COSTOS_OPERACION = {
    'tiempo_sourcing_hrs': 2.5,   # Horas para encontrar y comprar producto
    'tiempo_listing_hrs': 1.0,    # Fotografía, descripción, publicación
    'tiempo_empaque_hrs': 0.5,    # Empacar y enviar
    'costo_hora': 150,            # MXN - valor de tu tiempo (referencia: salario freelance junior)
    'transporte_sourcing': 80,    # MXN - transporte a tianguis/vendedor
}

print("\nESTRUCTURA DE COSTOS DEFINIDA")
print("\nComisiones Mercado Libre:")
print(f"  - Venta: {COSTOS_ML['comision_venta']*100}%")
print(f"  - MercadoPago: {COSTOS_ML['comision_mercadopago']*100}% + IVA")
print(f"\nCostos operativos:")
print(f"  - Tiempo total por producto: {COSTOS_OPERACION['tiempo_sourcing_hrs'] + COSTOS_OPERACION['tiempo_listing_hrs'] + COSTOS_OPERACION['tiempo_empaque_hrs']} hrs")
print(f"  - Valor hora: ${COSTOS_OPERACION['costo_hora']} MXN")

# %%
# === FUNCIÓN: CALCULAR RENTABILIDAD ===

def calcular_rentabilidad(precio_compra, precio_venta, incluir_tiempo=True, 
                          envio_gratis=False, categoria='estandar'):
    """
    Calcula la rentabilidad neta de un producto
    
    Args:
        precio_compra: Precio al que compras el producto
        precio_venta: Precio al que lo vendes
        incluir_tiempo: Si se debe contabilizar el costo del tiempo
        envio_gratis: Si ofreces envío gratis (tú absorbes el costo)
        categoria: 'estandar' (16%), 'tecnologia' (13%), 'coleccionables' (15%)
    
    Returns:
        Diccionario con todos los costos y ganancias
    """
    
    # Ajustar comisión según categoría
    comisiones_categoria = {
        'estandar': 0.16,
        'tecnologia': 0.13,
        'coleccionables': 0.15
    }
    comision_venta = comisiones_categoria.get(categoria, 0.16)
    
    # Calcular comisiones
    comision_ml = precio_venta * comision_venta
    comision_mp_base = precio_venta * COSTOS_ML['comision_mercadopago']
    iva_mp = comision_mp_base * COSTOS_ML['iva_mercadopago']
    comision_mp_total = comision_mp_base + iva_mp
    
    # Costos de envío y embalaje
    costo_envio = COSTOS_ML['envio_promedio'] if envio_gratis else 0
    costo_embalaje = COSTOS_ML['embalaje']
    
    # Costos de operación
    tiempo_total = (COSTOS_OPERACION['tiempo_sourcing_hrs'] + 
                   COSTOS_OPERACION['tiempo_listing_hrs'] + 
                   COSTOS_OPERACION['tiempo_empaque_hrs'])
    
    costo_tiempo = tiempo_total * COSTOS_OPERACION['costo_hora'] if incluir_tiempo else 0
    costo_transporte = COSTOS_OPERACION['transporte_sourcing']
    
    # Cálculos finales
    costo_total = (precio_compra + comision_ml + comision_mp_total + 
                   costo_envio + costo_embalaje + costo_tiempo + costo_transporte)
    
    ganancia_bruta = precio_venta - precio_compra
    ganancia_neta = precio_venta - costo_total
    
    roi_bruto = (ganancia_bruta / precio_compra * 100) if precio_compra > 0 else 0
    roi_neto = (ganancia_neta / precio_compra * 100) if precio_compra > 0 else 0
    
    margen_neto = (ganancia_neta / precio_venta * 100) if precio_venta > 0 else 0
    
    return {
        'precio_compra': precio_compra,
        'precio_venta': precio_venta,
        'comision_ml': comision_ml,
        'comision_mp': comision_mp_total,
        'costo_envio': costo_envio,
        'costo_embalaje': costo_embalaje,
        'costo_tiempo': costo_tiempo,
        'costo_transporte': costo_transporte,
        'costo_total': costo_total,
        'ganancia_bruta': ganancia_bruta,
        'ganancia_neta': ganancia_neta,
        'roi_bruto': roi_bruto,
        'roi_neto': roi_neto,
        'margen_neto': margen_neto,
        'viable': ganancia_neta > 0 and roi_neto >= 30  # Umbral mínimo 30% ROI
    }

# %%
# === ANÁLISIS DE NICHOS DEL SCORECARD ===

# Cargar el scorecard más reciente o usar datos de ejemplo
import glob
import os

scorecard_files = glob.glob('data/analytics/SCORECARD_FINAL_*.csv')

if scorecard_files:
    latest_scorecard = max(scorecard_files, key=os.path.getctime)
    df_scorecard = pd.read_csv(latest_scorecard, encoding='utf-8-sig')
    print(f"\nScorecard cargado: {latest_scorecard}")
else:
    # Datos de ejemplo si no existe el scorecard
    print("\nUsando datos de ejemplo (ejecuta notebooks 01-04 primero)")
    df_scorecard = pd.DataFrame({
        'nombre_nicho': [
            'Calculadora Financiera HP 12C',
            'Cámara Digital Vintage',
            'Teclado Mecánico',
            'Game Boy Advance',
            'iPod Classic'
        ],
        'SCORE_FINAL': [8.5, 7.8, 8.2, 6.9, 7.3],
        'precio_promedio': [850, 600, 1500, 1200, 800]
    })

print(f"\nNichos a analizar: {len(df_scorecard)}")

# %%
# === ESCENARIOS DE COMPRA/VENTA ===

def generar_escenarios(precio_mercado_promedio):
    """
    Genera tres escenarios de compra y venta basados en el precio de mercado
    
    Escenario Conservador: Compras caro, vendes barato
    Escenario Realista: Precio promedio
    Escenario Optimista: Compras barato, vendes bien
    """
    
    escenarios = {
        'conservador': {
            'precio_compra': precio_mercado_promedio * 0.75,  # 75% del precio de venta
            'precio_venta': precio_mercado_promedio * 0.90,   # 10% bajo mercado
            'descripcion': 'Compra cara, venta baja'
        },
        'realista': {
            'precio_compra': precio_mercado_promedio * 0.60,  # 60% del precio de venta
            'precio_venta': precio_mercado_promedio,          # Precio de mercado
            'descripcion': 'Compra promedio, venta mercado'
        },
        'optimista': {
            'precio_compra': precio_mercado_promedio * 0.45,  # 45% del precio de venta
            'precio_venta': precio_mercado_promedio * 1.10,   # 10% sobre mercado
            'descripcion': 'Compra barata, venta premium'
        }
    }
    
    return escenarios

# %%
# === ANÁLISIS COMPLETO POR NICHO ===

print("\n" + "="*80)
print("ANÁLISIS DE RENTABILIDAD POR NICHO")
print("="*80 + "\n")

resultados_completos = []

for idx, row in df_scorecard.iterrows():
    nicho = row['nombre_nicho']
    precio_mercado = row['precio_promedio']
    
    print(f"\n{'─'*80}")
    print(f"NICHO: {nicho}")
    print(f"Precio promedio mercado: ${precio_mercado:,.2f} MXN")
    print(f"{'─'*80}\n")
    
    escenarios = generar_escenarios(precio_mercado)
    
    for escenario_nombre, escenario_data in escenarios.items():
        print(f"\n  {escenario_nombre.upper()} - {escenario_data['descripcion']}")
        print(f"  {'-'*76}")
        
        resultado = calcular_rentabilidad(
            precio_compra=escenario_data['precio_compra'],
            precio_venta=escenario_data['precio_venta'],
            incluir_tiempo=True,
            envio_gratis=True,
            categoria='estandar'
        )
        
        # Agregar metadata
        resultado['nicho'] = nicho
        resultado['escenario'] = escenario_nombre
        resultado['score_final'] = row.get('SCORE_FINAL', 0)
        
        resultados_completos.append(resultado)
        
        # Mostrar resultados
        print(f"  Compra:          ${resultado['precio_compra']:>10,.2f}")
        print(f"  Venta:           ${resultado['precio_venta']:>10,.2f}")
        print(f"  ───────────────────────────────")
        print(f"  Comisión ML:     ${resultado['comision_ml']:>10,.2f}")
        print(f"  Comisión MP:     ${resultado['comision_mp']:>10,.2f}")
        print(f"  Envío:           ${resultado['costo_envio']:>10,.2f}")
        print(f"  Embalaje:        ${resultado['costo_embalaje']:>10,.2f}")
        print(f"  Tiempo:          ${resultado['costo_tiempo']:>10,.2f}")
        print(f"  Transporte:      ${resultado['costo_transporte']:>10,.2f}")
        print(f"  ───────────────────────────────")
        print(f"  COSTO TOTAL:     ${resultado['costo_total']:>10,.2f}")
        print(f"  ═══════════════════════════════")
        print(f"  Ganancia Neta:   ${resultado['ganancia_neta']:>10,.2f}")
        print(f"  ROI Neto:        {resultado['roi_neto']:>10.1f}%")
        print(f"  Margen:          {resultado['margen_neto']:>10.1f}%")
        
        if resultado['viable']:
            print(f"  VEREDICTO:       VIABLE")
        else:
            print(f"  VEREDICTO:       NO VIABLE (ROI < 30%)")

# Crear DataFrame con todos los resultados
df_resultados = pd.DataFrame(resultados_completos)

# %%
# === VISUALIZACIÓN: COMPARACIÓN DE ESCENARIOS ===

# Filtrar solo escenario realista para comparar nichos
df_realista = df_resultados[df_resultados['escenario'] == 'realista'].copy()

fig = go.Figure()

# Ganancia neta
fig.add_trace(go.Bar(
    name='Ganancia Neta',
    x=df_realista['nicho'],
    y=df_realista['ganancia_neta'],
    marker_color='#2E86AB',
    text=df_realista['ganancia_neta'].round(0),
    texttemplate='$%{text:,.0f}',
    textposition='outside'
))

# Línea de ROI
fig.add_trace(go.Scatter(
    name='ROI Neto (%)',
    x=df_realista['nicho'],
    y=df_realista['roi_neto'],
    mode='lines+markers',
    yaxis='y2',
    line=dict(color='#F18F01', width=3),
    marker=dict(size=10)
))

# Línea de umbral mínimo (30% ROI)
fig.add_trace(go.Scatter(
    name='Umbral Mínimo (30%)',
    x=df_realista['nicho'],
    y=[30] * len(df_realista),
    mode='lines',
    yaxis='y2',
    line=dict(color='red', width=2, dash='dash'),
    showlegend=True
))

fig.update_layout(
    title='Comparación de Rentabilidad por Nicho (Escenario Realista)',
    xaxis=dict(title='Nicho', tickangle=-45),
    yaxis=dict(title='Ganancia Neta (MXN)', side='left'),
    yaxis2=dict(title='ROI Neto (%)', side='right', overlaying='y', showgrid=False),
    template='plotly_white',
    height=600,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

fig.show()

# %%
# === ANÁLISIS DE SENSIBILIDAD: PRECIO DE COMPRA ===

print("\n" + "="*80)
print("ANÁLISIS DE SENSIBILIDAD")
print("="*80 + "\n")

# Tomar el mejor nicho según score
mejor_nicho = df_scorecard.iloc[0]
nicho_nombre = mejor_nicho['nombre_nicho']
precio_venta_fijo = mejor_nicho['precio_promedio']

print(f"Nicho analizado: {nicho_nombre}")
print(f"Precio de venta fijo: ${precio_venta_fijo:,.2f} MXN\n")

# Variar precio de compra de 30% a 80% del precio de venta
porcentajes_compra = np.arange(30, 85, 5)
sensibilidad = []

for pct in porcentajes_compra:
    precio_compra = precio_venta_fijo * (pct / 100)
    resultado = calcular_rentabilidad(
        precio_compra=precio_compra,
        precio_venta=precio_venta_fijo,
        incluir_tiempo=True,
        envio_gratis=True
    )
    
    sensibilidad.append({
        'porcentaje_compra': pct,
        'precio_compra': precio_compra,
        'ganancia_neta': resultado['ganancia_neta'],
        'roi_neto': resultado['roi_neto'],
        'viable': resultado['viable']
    })

df_sensibilidad = pd.DataFrame(sensibilidad)

# Visualizar
fig = make_subplots(
    rows=2, cols=1,
    subplot_titles=(
        'Ganancia Neta vs Precio de Compra',
        'ROI Neto vs Precio de Compra'
    ),
    vertical_spacing=0.12
)

# Ganancia Neta
fig.add_trace(
    go.Scatter(
        x=df_sensibilidad['porcentaje_compra'],
        y=df_sensibilidad['ganancia_neta'],
        mode='lines+markers',
        name='Ganancia Neta',
        line=dict(color='#2E86AB', width=3),
        marker=dict(size=8),
        fill='tozeroy',
        fillcolor='rgba(46, 134, 171, 0.2)'
    ),
    row=1, col=1
)

# ROI Neto
fig.add_trace(
    go.Scatter(
        x=df_sensibilidad['porcentaje_compra'],
        y=df_sensibilidad['roi_neto'],
        mode='lines+markers',
        name='ROI Neto',
        line=dict(color='#F18F01', width=3),
        marker=dict(size=8)
    ),
    row=2, col=1
)

# Línea de umbral en ROI
fig.add_trace(
    go.Scatter(
        x=df_sensibilidad['porcentaje_compra'],
        y=[30] * len(df_sensibilidad),
        mode='lines',
        name='Umbral 30%',
        line=dict(color='red', width=2, dash='dash')
    ),
    row=2, col=1
)

fig.update_xaxes(title_text="Precio de Compra (% del precio de venta)", row=2, col=1)
fig.update_yaxes(title_text="Ganancia Neta (MXN)", row=1, col=1)
fig.update_yaxes(title_text="ROI Neto (%)", row=2, col=1)

fig.update_layout(
    title=f'Análisis de Sensibilidad: {nicho_nombre}',
    height=800,
    template='plotly_white',
    showlegend=True
)

fig.show()

# Encontrar precio máximo de compra viable
precio_max_viable = df_sensibilidad[df_sensibilidad['viable']]['precio_compra'].max()
porcentaje_max = df_sensibilidad[df_sensibilidad['viable']]['porcentaje_compra'].max()

print(f"\nPRECIO MÁXIMO DE COMPRA VIABLE:")
print(f"  ${precio_max_viable:,.2f} MXN ({porcentaje_max}% del precio de venta)")
print(f"\nRECOMENDACIÓN: No pagar más de ${precio_max_viable:,.2f} por este producto")

# %%
# === PUNTO DE EQUILIBRIO (BREAK-EVEN) ===

print("\n" + "="*80)
print("ANÁLISIS DE PUNTO DE EQUILIBRIO")
print("="*80 + "\n")

inversion_inicial = 5000  # MXN - inversión inicial propuesta

# Calcular cuántas unidades necesitas vender para recuperar inversión
productos_breakeven = []

for idx, row in df_realista.iterrows():
    nicho = row['nicho']
    ganancia_por_unidad = row['ganancia_neta']
    precio_compra = row['precio_compra']
    
    if ganancia_por_unidad > 0:
        # Unidades necesarias para recuperar inversión inicial
        unidades_para_inversion = np.ceil(inversion_inicial / ganancia_por_unidad)
        
        # Capital necesario para comprar esas unidades
        capital_necesario = unidades_para_inversion * precio_compra
        
        # Días estimados (asumiendo venta cada 2 semanas por unidad)
        dias_estimados = unidades_para_inversion * 14
        
        productos_breakeven.append({
            'nicho': nicho,
            'ganancia_por_unidad': ganancia_por_unidad,
            'unidades_breakeven': unidades_para_inversion,
            'capital_necesario': capital_necesario,
            'dias_estimados': dias_estimados,
            'roi_por_unidad': row['roi_neto']
        })

df_breakeven = pd.DataFrame(productos_breakeven).sort_values('unidades_breakeven')

print(f"Inversión inicial objetivo: ${inversion_inicial:,.2f} MXN")
print(f"\nUnidades necesarias para break-even por nicho:\n")

for idx, row in df_breakeven.iterrows():
    print(f"{row['nicho']}:")
    print(f"  Ganancia por unidad: ${row['ganancia_por_unidad']:,.2f}")
    print(f"  Unidades necesarias: {int(row['unidades_breakeven'])}")
    print(f"  Capital requerido:   ${row['capital_necesario']:,.2f}")
    print(f"  Tiempo estimado:     {int(row['dias_estimados'])} días ({int(row['dias_estimados']/30)} meses)")
    print(f"  ROI por unidad:      {row['roi_por_unidad']:.1f}%")
    print()

# Visualizar
fig = go.Figure()

fig.add_trace(go.Bar(
    x=df_breakeven['nicho'],
    y=df_breakeven['unidades_breakeven'],
    marker_color='#06A77D',
    text=df_breakeven['unidades_breakeven'].astype(int),
    textposition='outside'
))

fig.update_layout(
    title=f'Unidades Necesarias para Break-Even (Inversión: ${inversion_inicial:,} MXN)',
    xaxis_title='Nicho',
    yaxis_title='Número de Unidades',
    template='plotly_white',
    height=500,
    xaxis_tickangle=-45
)

fig.show()

# %%
# === RECOMENDACIÓN FINAL ===

print("\n" + "="*80)
print("RECOMENDACIÓN DE INVERSIÓN")
print("="*80 + "\n")

# Ordenar nichos por score combinado (rentabilidad + factibilidad)
df_realista['score_combinado'] = (
    df_realista['score_final'] * 0.4 +  # Score del análisis de mercado
    (df_realista['roi_neto'] / 10) * 0.3 +  # ROI normalizado
    (df_realista['ganancia_neta'] / df_realista['ganancia_neta'].max() * 10) * 0.3  # Ganancia normalizada
)

df_recomendacion = df_realista.sort_values('score_combinado', ascending=False)

print("TOP 3 NICHOS RECOMENDADOS:\n")

for i, (idx, row) in enumerate(df_recomendacion.head(3).iterrows(), 1):
    print(f"{i}. {row['nicho']}")
    print(f"   Score combinado:    {row['score_combinado']:.2f}/10")
    print(f"   Ganancia por unidad: ${row['ganancia_neta']:,.2f}")
    print(f"   ROI neto:            {row['roi_neto']:.1f}%")
    print(f"   Inversión sugerida:  ${row['precio_compra'] * 5:,.2f} (5 unidades)")
    print(f"   Ganancia esperada:   ${row['ganancia_neta'] * 5:,.2f}")
    print()

# %%
# === EXPORTAR RESULTADOS ===

timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

# Exportar análisis completo
df_resultados.to_csv(
    f'data/analytics/simulacion_margenes_{timestamp}.csv',
    index=False,
    encoding='utf-8-sig'
)

# Exportar recomendaciones
df_recomendacion[['nicho', 'score_combinado', 'ganancia_neta', 'roi_neto', 'precio_compra', 'precio_venta']].to_csv(
    f'data/analytics/recomendaciones_inversion_{timestamp}.csv',
    index=False,
    encoding='utf-8-sig'
)

print(f"\nResultados exportados con timestamp: {timestamp}")
print("\nPróximo paso: Notebook 06 - Análisis de Factibilidad")
