# %% [markdown]
# # DataFlip MX - Análisis de Factibilidad
# 
# **Objetivo:** Validar si el proyecto es viable considerando restricciones temporales, académicas y de recursos
# 
# **Componentes:**
# - Análisis de timeline realista
# - Comparación con alternativas
# - Matriz de riesgo
# - Decisión GO/NO-GO

# %%
# === IMPORTAR LIBRERÍAS ===
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

print("Librerías importadas correctamente")

# %%
# === PARÁMETROS DE CONTEXTO PERSONAL ===

CONTEXTO = {
    # Timeline
    'fecha_inicio': datetime(2024, 11, 15),
    'fecha_examenes': datetime(2024, 12, 9),
    'fecha_viaje': datetime(2026, 2, 1),
    
    # Disponibilidad de tiempo
    'horas_semanales_normal': 15,      # Durante semestre
    'horas_semanales_examenes': 5,     # Durante exámenes finales
    'horas_semanales_vacaciones': 30,  # Enero
    
    # Académico
    'semestre_actual': 5,
    'promedio_actual': 9.0,  # Asumiendo buen promedio
    'creditos_semestre': 42,
    
    # Económico
    'capital_disponible': 5000,  # MXN inicial
    'capital_maximo': 15000,     # MXN máximo dispuesto a invertir
    'meta_ganancia': 20000,      # MXN objetivo para viaje
}

# Calcular semanas disponibles
semanas_totales = ((CONTEXTO['fecha_viaje'] - CONTEXTO['fecha_inicio']).days) / 7
semanas_hasta_examenes = ((CONTEXTO['fecha_examenes'] - CONTEXTO['fecha_inicio']).days) / 7
semanas_examenes = 2
semanas_vacaciones = 4
semanas_enero = 4

print("\n" + "="*80)
print("CONTEXTO DEL PROYECTO")
print("="*80 + "\n")

print(f"Timeline:")
print(f"  Inicio:           {CONTEXTO['fecha_inicio'].strftime('%d/%m/%Y')}")
print(f"  Exámenes finales: {CONTEXTO['fecha_examenes'].strftime('%d/%m/%Y')}")
print(f"  Viaje a Amsterdam: {CONTEXTO['fecha_viaje'].strftime('%d/%m/%Y')}")
print(f"  Semanas totales:  {semanas_totales:.0f} semanas")
print(f"\nDisponibilidad de tiempo:")
print(f"  Normal:           {CONTEXTO['horas_semanales_normal']} hrs/semana")
print(f"  Exámenes:         {CONTEXTO['horas_semanales_examenes']} hrs/semana")
print(f"  Vacaciones:       {CONTEXTO['horas_semanales_vacaciones']} hrs/semana")
print(f"\nRecursos:")
print(f"  Capital inicial:  ${CONTEXTO['capital_disponible']:,} MXN")
print(f"  Meta ganancia:    ${CONTEXTO['meta_ganancia']:,} MXN")

# %%
# === ANÁLISIS DE TIEMPO DISPONIBLE ===

# Desglose semanal
periodos = []

# Noviembre (hasta exámenes)
for semana in range(int(semanas_hasta_examenes)):
    periodos.append({
        'semana': semana + 1,
        'periodo': 'Noviembre (Semestre)',
        'horas_disponibles': CONTEXTO['horas_semanales_normal'],
        'dedicacion': 'Media'
    })

# Exámenes finales
for semana in range(int(semanas_examenes)):
    periodos.append({
        'semana': len(periodos) + 1,
        'periodo': 'Exámenes Finales',
        'horas_disponibles': CONTEXTO['horas_semanales_examenes'],
        'dedicacion': 'Baja'
    })

# Vacaciones diciembre-enero
for semana in range(int(semanas_vacaciones + semanas_enero)):
    periodos.append({
        'semana': len(periodos) + 1,
        'periodo': 'Vacaciones/Enero',
        'horas_disponibles': CONTEXTO['horas_semanales_vacaciones'],
        'dedicacion': 'Alta'
    })

df_tiempo = pd.DataFrame(periodos)

# Calcular acumulados
df_tiempo['horas_acumuladas'] = df_tiempo['horas_disponibles'].cumsum()

# Visualizar
fig = go.Figure()

fig.add_trace(go.Bar(
    x=df_tiempo['semana'],
    y=df_tiempo['horas_disponibles'],
    name='Horas Semanales',
    marker_color=df_tiempo['horas_disponibles'],
    marker=dict(
        colorscale='Viridis',
        showscale=True,
        colorbar=dict(title="Horas")
    ),
    text=df_tiempo['periodo'],
    hovertemplate='Semana %{x}<br>Horas: %{y}<br>Periodo: %{text}<extra></extra>'
))

fig.add_trace(go.Scatter(
    x=df_tiempo['semana'],
    y=df_tiempo['horas_acumuladas'],
    name='Horas Acumuladas',
    mode='lines+markers',
    line=dict(color='red', width=3),
    yaxis='y2'
))

fig.update_layout(
    title='Disponibilidad de Tiempo Semanal',
    xaxis_title='Semana',
    yaxis_title='Horas Semanales',
    yaxis2=dict(
        title='Horas Acumuladas',
        overlaying='y',
        side='right'
    ),
    template='plotly_white',
    height=500
)

fig.show()

total_horas = df_tiempo['horas_disponibles'].sum()
print(f"\nTotal de horas disponibles: {total_horas:.0f} horas")
print(f"Promedio semanal: {total_horas / len(df_tiempo):.1f} horas/semana")

# %%
# === ANÁLISIS DE CAPACIDAD OPERATIVA ===

# Tiempo requerido por producto (de costos operación)
TIEMPO_POR_PRODUCTO = {
    'sourcing': 2.5,      # Encontrar y comprar
    'listing': 1.0,       # Fotografiar y publicar
    'gestion': 0.5,       # Atender mensajes, negociar
    'empaque_envio': 0.5, # Empacar y enviar
}

tiempo_total_por_producto = sum(TIEMPO_POR_PRODUCTO.values())

print("\n" + "="*80)
print("CAPACIDAD OPERATIVA")
print("="*80 + "\n")

print(f"Tiempo por producto: {tiempo_total_por_producto} horas")
print(f"\nDesglose:")
for actividad, horas in TIEMPO_POR_PRODUCTO.items():
    print(f"  {actividad.capitalize()}: {horas} hrs")

# Calcular capacidad por periodo
df_tiempo['productos_posibles'] = (df_tiempo['horas_disponibles'] / tiempo_total_por_producto).astype(int)
df_tiempo['productos_acumulados'] = df_tiempo['productos_posibles'].cumsum()

print(f"\nCapacidad máxima teórica:")
print(f"  Productos por semana (promedio): {df_tiempo['productos_posibles'].mean():.1f}")
print(f"  Productos totales (15 semanas): {df_tiempo['productos_posibles'].sum()}")

# Ajustar por realismo (eficiencia del 70%)
eficiencia = 0.70
df_tiempo['productos_realistas'] = (df_tiempo['productos_posibles'] * eficiencia).astype(int)
df_tiempo['productos_realistas_acum'] = df_tiempo['productos_realistas'].cumsum()

print(f"\nCapacidad realista (70% eficiencia):")
print(f"  Productos totales: {df_tiempo['productos_realistas'].sum()}")

# %%
# === SIMULACIÓN DE ESCENARIOS ===

# Cargar datos de rentabilidad del notebook anterior
import glob
import os

margin_files = glob.glob('data/analytics/recomendaciones_inversion_*.csv')

if margin_files:
    latest_margin = max(margin_files, key=os.path.getctime)
    df_nichos = pd.read_csv(latest_margin, encoding='utf-8-sig')
    print(f"\nDatos de rentabilidad cargados: {latest_margin}")
else:
    print("\nUsando datos de ejemplo (ejecuta notebook 05 primero)")
    df_nichos = pd.DataFrame({
        'nicho': ['Calculadora HP 12C', 'Teclado Mecánico', 'Cámara Vintage'],
        'ganancia_neta': [227, 350, 180],
        'roi_neto': [37.8, 45.5, 30.0],
        'precio_compra': [600, 800, 600]
    })

# Tomar el mejor nicho
mejor_nicho = df_nichos.iloc[0]

print(f"\nNicho seleccionado: {mejor_nicho['nicho']}")
print(f"Ganancia por unidad: ${mejor_nicho['ganancia_neta']:.2f}")
print(f"ROI: {mejor_nicho['roi_neto']:.1f}%")

# %%
# === ESCENARIOS DE GANANCIA ===

def simular_escenario(nombre, productos_por_semana, ganancia_por_unidad, 
                      capital_inicial, precio_compra, semanas_operacion):
    """
    Simula un escenario completo de ventas
    """
    
    resultados = []
    capital_actual = capital_inicial
    productos_inventario = 0
    productos_vendidos_total = 0
    ganancia_acumulada = 0
    
    for semana in range(1, int(semanas_operacion) + 1):
        # Determinar disponibilidad según periodo
        if semana <= semanas_hasta_examenes:
            factor_disponibilidad = 1.0
        elif semana <= (semanas_hasta_examenes + semanas_examenes):
            factor_disponibilidad = 0.3  # Muy poco tiempo en exámenes
        else:
            factor_disponibilidad = 1.5  # Más tiempo en vacaciones
        
        # Productos que se pueden procesar esta semana
        productos_semana = int(productos_por_semana * factor_disponibilidad)
        
        # Comprar nuevos productos si hay capital
        productos_a_comprar = min(
            productos_semana,
            int(capital_actual / precio_compra)
        )
        
        if productos_a_comprar > 0:
            costo_compra = productos_a_comprar * precio_compra
            capital_actual -= costo_compra
            productos_inventario += productos_a_comprar
        
        # Vender productos (asumiendo 70% de conversión semanal del inventario)
        productos_vendidos_semana = int(productos_inventario * 0.7)
        
        if productos_vendidos_semana > 0:
            ganancia_semana = productos_vendidos_semana * ganancia_por_unidad
            capital_actual += ganancia_semana + (productos_vendidos_semana * precio_compra)
            productos_inventario -= productos_vendidos_semana
            productos_vendidos_total += productos_vendidos_semana
            ganancia_acumulada += ganancia_semana
        
        resultados.append({
            'semana': semana,
            'productos_comprados': productos_a_comprar,
            'productos_vendidos': productos_vendidos_semana,
            'inventario': productos_inventario,
            'capital': capital_actual,
            'ganancia_acumulada': ganancia_acumulada,
            'productos_vendidos_total': productos_vendidos_total
        })
    
    return pd.DataFrame(resultados)

# Definir tres escenarios
escenarios = {
    'Conservador': {
        'productos_por_semana': 2,
        'descripcion': '2 productos/semana, venta lenta'
    },
    'Realista': {
        'productos_por_semana': 3,
        'descripcion': '3 productos/semana, venta moderada'
    },
    'Optimista': {
        'productos_por_semana': 4,
        'descripcion': '4 productos/semana, venta rápida'
    }
}

print("\n" + "="*80)
print("SIMULACIÓN DE ESCENARIOS")
print("="*80 + "\n")

resultados_escenarios = {}

for nombre, config in escenarios.items():
    print(f"\n{nombre}: {config['descripcion']}")
    
    df_sim = simular_escenario(
        nombre=nombre,
        productos_por_semana=config['productos_por_semana'],
        ganancia_por_unidad=mejor_nicho['ganancia_neta'],
        capital_inicial=CONTEXTO['capital_disponible'],
        precio_compra=mejor_nicho['precio_compra'],
        semanas_operacion=len(df_tiempo)
    )
    
    resultados_escenarios[nombre] = df_sim
    
    # Mostrar resultados finales
    final = df_sim.iloc[-1]
    print(f"  Productos vendidos: {int(final['productos_vendidos_total'])}")
    print(f"  Ganancia total: ${final['ganancia_acumulada']:,.2f}")
    print(f"  Capital final: ${final['capital']:,.2f}")
    print(f"  Inventario restante: {int(final['inventario'])} unidades")
    
    # Evaluar si alcanza meta
    if final['ganancia_acumulada'] >= CONTEXTO['meta_ganancia']:
        print(f"  RESULTADO: META ALCANZADA")
    else:
        deficit = CONTEXTO['meta_ganancia'] - final['ganancia_acumulada']
        print(f"  RESULTADO: DÉFICIT de ${deficit:,.2f}")

# %%
# === VISUALIZACIÓN DE ESCENARIOS ===

fig = go.Figure()

colores = {'Conservador': '#E63946', 'Realista': '#F1A208', 'Optimista': '#06A77D'}

for nombre, df_sim in resultados_escenarios.items():
    fig.add_trace(go.Scatter(
        x=df_sim['semana'],
        y=df_sim['ganancia_acumulada'],
        mode='lines+markers',
        name=nombre,
        line=dict(width=3, color=colores[nombre]),
        marker=dict(size=6)
    ))

# Línea de meta
fig.add_trace(go.Scatter(
    x=[1, len(df_tiempo)],
    y=[CONTEXTO['meta_ganancia'], CONTEXTO['meta_ganancia']],
    mode='lines',
    name='Meta',
    line=dict(color='black', width=2, dash='dash')
))

fig.update_layout(
    title='Ganancia Acumulada por Escenario',
    xaxis_title='Semana',
    yaxis_title='Ganancia Acumulada (MXN)',
    template='plotly_white',
    height=500,
    hovermode='x unified'
)

fig.show()

# %%
# === COMPARACIÓN CON ALTERNATIVAS ===

print("\n" + "="*80)
print("COMPARACIÓN CON ALTERNATIVAS")
print("="*80 + "\n")

alternativas = [
    {
        'opcion': 'Flipping (Este proyecto)',
        'inversion_inicial': CONTEXTO['capital_disponible'],
        'horas_totales': total_horas,
        'ganancia_esperada': resultados_escenarios['Realista'].iloc[-1]['ganancia_acumulada'],
        'riesgo': 'Alto',
        'aprendizaje': 'Negocios, análisis de datos, logística'
    },
    {
        'opcion': 'Freelance Desarrollo Web',
        'inversion_inicial': 0,
        'horas_totales': total_horas,
        'ganancia_esperada': total_horas * 200,  # $200/hr tarifa junior
        'riesgo': 'Bajo',
        'aprendizaje': 'Programación, clientes, proyectos'
    },
    {
        'opcion': 'Tutorías (Python/Data Science)',
        'inversion_inicial': 0,
        'horas_totales': total_horas,
        'ganancia_esperada': total_horas * 150,  # $150/hr tutorías
        'riesgo': 'Bajo',
        'aprendizaje': 'Enseñanza, comunicación'
    },
    {
        'opcion': 'Vender Cosas Personales',
        'inversion_inicial': 0,
        'horas_totales': 20,  # Mucho menos tiempo
        'ganancia_esperada': 5000,  # Estimado conservador
        'riesgo': 'Muy Bajo',
        'aprendizaje': 'Mínimo'
    },
    {
        'opcion': 'Becas/Trabajo Medio Tiempo',
        'inversion_inicial': 0,
        'horas_totales': total_horas,
        'ganancia_esperada': total_horas * 80,  # Salario mínimo efectivo
        'riesgo': 'Muy Bajo',
        'aprendizaje': 'Experiencia laboral formal'
    }
]

df_alternativas = pd.DataFrame(alternativas)

# Calcular métricas adicionales
df_alternativas['ganancia_neta'] = df_alternativas['ganancia_esperada'] - df_alternativas['inversion_inicial']
df_alternativas['ganancia_por_hora'] = df_alternativas['ganancia_neta'] / df_alternativas['horas_totales']
df_alternativas['roi_pct'] = ((df_alternativas['ganancia_neta'] / df_alternativas['inversion_inicial'].replace(0, 1)) * 100).round(0)

print(df_alternativas[['opcion', 'ganancia_esperada', 'ganancia_por_hora', 'riesgo']].to_string(index=False))

# Visualizar
fig = go.Figure()

fig.add_trace(go.Bar(
    x=df_alternativas['opcion'],
    y=df_alternativas['ganancia_esperada'],
    marker_color=['#2E86AB', '#F18F01', '#06A77D', '#A4036F', '#048BA8'],
    text=df_alternativas['ganancia_esperada'].round(0),
    texttemplate='$%{text:,.0f}',
    textposition='outside'
))

fig.update_layout(
    title='Ganancia Esperada por Alternativa',
    xaxis_title='Opción',
    yaxis_title='Ganancia Esperada (MXN)',
    template='plotly_white',
    height=500,
    xaxis_tickangle=-45
)

fig.show()

print("\nGanancia por hora trabajada:")
for idx, row in df_alternativas.iterrows():
    print(f"  {row['opcion']}: ${row['ganancia_por_hora']:.2f}/hr")

# %%
# === MATRIZ DE RIESGO ===

print("\n" + "="*80)
print("MATRIZ DE RIESGO")
print("="*80 + "\n")

riesgos = [
    {
        'riesgo': 'Productos no se venden',
        'probabilidad': 'Alta',
        'prob_num': 70,
        'impacto': 'Alto',
        'impacto_num': 4,
        'mitigacion': 'Diversificar nichos, pricing dinámico, deadline de liquidación'
    },
    {
        'riesgo': 'Productos defectuosos/falsificados',
        'probabilidad': 'Media',
        'prob_num': 40,
        'impacto': 'Alto',
        'impacto_num': 4,
        'mitigacion': 'Checklist de evaluación, probar antes de comprar, comprar solo conocidos'
    },
    {
        'riesgo': 'Tiempo insuficiente (exámenes)',
        'probabilidad': 'Alta',
        'prob_num': 80,
        'impacto': 'Medio',
        'impacto_num': 3,
        'mitigacion': 'Front-load trabajo en noviembre, pausar en diciembre'
    },
    {
        'riesgo': 'Capital insuficiente para recompra',
        'probabilidad': 'Media',
        'prob_num': 50,
        'impacto': 'Medio',
        'impacto_num': 3,
        'mitigacion': 'Empezar con capital mayor, reinvertir rápido'
    },
    {
        'riesgo': 'Competencia baja precios',
        'probabilidad': 'Media',
        'prob_num': 50,
        'impacto': 'Medio',
        'impacto_num': 2,
        'mitigacion': 'Diferenciación (fotos pro, descripciones), valor agregado'
    },
    {
        'riesgo': 'Estafas en sourcing',
        'probabilidad': 'Baja',
        'prob_num': 20,
        'impacto': 'Alto',
        'impacto_num': 4,
        'mitigacion': 'Solo efectivo en persona, verificar antes de pagar'
    },
    {
        'riesgo': 'Problemas logísticos (envíos)',
        'probabilidad': 'Media',
        'prob_num': 40,
        'impacto': 'Bajo',
        'impacto_num': 2,
        'mitigacion': 'Usar Mercado Envíos, empacar bien, seguro'
    },
    {
        'riesgo': 'Afecta desempeño académico',
        'probabilidad': 'Media',
        'prob_num': 50,
        'impacto': 'Muy Alto',
        'impacto_num': 5,
        'mitigacion': 'Límite estricto 15hrs/semana, pausa en exámenes'
    }
]

df_riesgos = pd.DataFrame(riesgos)
df_riesgos['severidad'] = df_riesgos['prob_num'] * df_riesgos['impacto_num'] / 100

print("Riesgos ordenados por severidad:\n")
df_riesgos_sorted = df_riesgos.sort_values('severidad', ascending=False)

for idx, row in df_riesgos_sorted.iterrows():
    print(f"{row['riesgo']}")
    print(f"  Probabilidad: {row['probabilidad']} ({row['prob_num']}%)")
    print(f"  Impacto: {row['impacto']} ({row['impacto_num']}/5)")
    print(f"  Severidad: {row['severidad']:.1f}")
    print(f"  Mitigación: {row['mitigacion']}")
    print()

# Visualizar matriz
fig = px.scatter(
    df_riesgos,
    x='prob_num',
    y='impacto_num',
    size='severidad',
    color='severidad',
    hover_name='riesgo',
    hover_data=['probabilidad', 'impacto', 'mitigacion'],
    labels={'prob_num': 'Probabilidad (%)', 'impacto_num': 'Impacto (1-5)'},
    title='Matriz de Riesgo',
    color_continuous_scale='Reds',
    size_max=30
)

fig.update_layout(
    template='plotly_white',
    height=600,
    xaxis=dict(range=[0, 100]),
    yaxis=dict(range=[0, 6])
)

fig.show()

# %%
# === DECISIÓN GO/NO-GO ===

print("\n" + "="*80)
print("ANÁLISIS DE DECISIÓN GO/NO-GO")
print("="*80 + "\n")

criterios_decision = [
    {
        'criterio': 'Rentabilidad potencial',
        'peso': 0.25,
        'evaluacion': 8,  # 1-10
        'justificacion': 'ROI >30%, ganancia esperada razonable'
    },
    {
        'criterio': 'Factibilidad temporal',
        'peso': 0.20,
        'evaluacion': 6,
        'justificacion': 'Ajustado pero posible, riesgo en exámenes'
    },
    {
        'criterio': 'Riesgo académico',
        'peso': 0.25,
        'evaluacion': 5,
        'justificacion': 'Riesgo medio-alto de afectar estudios'
    },
    {
        'criterio': 'Capital disponible',
        'peso': 0.15,
        'evaluacion': 7,
        'justificacion': '$5,000 suficiente para empezar'
    },
    {
        'criterio': 'Aprendizaje/experiencia',
        'peso': 0.15,
        'evaluacion': 9,
        'justificacion': 'Alta curva de aprendizaje en negocios y data'
    }
]

df_decision = pd.DataFrame(criterios_decision)
df_decision['score_ponderado'] = df_decision['peso'] * df_decision['evaluacion']
score_total = df_decision['score_ponderado'].sum()

print("Evaluación de criterios:\n")
for idx, row in df_decision.iterrows():
    print(f"{row['criterio']} (Peso: {row['peso']*100:.0f}%)")
    print(f"  Evaluación: {row['evaluacion']}/10")
    print(f"  Score ponderado: {row['score_ponderado']:.2f}")
    print(f"  Justificación: {row['justificacion']}")
    print()

print(f"SCORE TOTAL: {score_total:.2f}/10\n")

# Visualizar
fig = go.Figure()

fig.add_trace(go.Bar(
    x=df_decision['criterio'],
    y=df_decision['evaluacion'],
    name='Evaluación',
    marker_color='#2E86AB'
))

fig.add_trace(go.Scatter(
    x=df_decision['criterio'],
    y=df_decision['peso'] * 10,
    name='Peso (x10)',
    mode='lines+markers',
    line=dict(color='red', width=3),
    marker=dict(size=10)
))

fig.update_layout(
    title='Evaluación de Criterios de Decisión',
    xaxis_title='Criterio',
    yaxis_title='Score (1-10)',
    template='plotly_white',
    height=500,
    xaxis_tickangle=-45
)

fig.show()

# Decisión final
print("="*80)
print("DECISIÓN FINAL")
print("="*80 + "\n")

if score_total >= 7.0:
    decision = "GO"
    color = "VERDE"
elif score_total >= 5.5:
    decision = "GO CONDICIONAL"
    color = "AMARILLO"
else:
    decision = "NO-GO"
    color = "ROJO"

print(f"VEREDICTO: {decision} ({color})")
print(f"Score: {score_total:.2f}/10\n")

if decision == "GO":
    print("Recomendaciones:")
    print("  1. Empezar con capital conservador ($3,000-5,000)")
    print("  2. Límite estricto de 15 hrs/semana")
    print("  3. Pausar completamente durante exámenes")
    print("  4. Definir KPIs y revisar semanalmente")
    print("  5. Plan de salida: liquidar todo antes de enero 20")
    
elif decision == "GO CONDICIONAL":
    print("Condiciones para proceder:")
    print("  1. Reducir riesgo académico (¿es último semestre antes de viaje?)")
    print("  2. Validar sourcing real (visitar tianguis primero)")
    print("  3. Empezar con solo 2-3 productos piloto")
    print("  4. Si no hay ventas en 2 semanas, abortar")
    print("  5. Tener plan B alternativo (freelance, tutorías)")
    
else:
    print("Razones para no proceder:")
    print("  1. Riesgo académico muy alto")
    print("  2. Timeline muy ajustado")
    print("  3. Considerar alternativas con mejor ROI/riesgo")
    print("\nAlternativas recomendadas:")
    print("  - Freelance desarrollo (mejor $/hr, menos riesgo)")
    print("  - Tutorías (aprovecha tu expertise ITAM)")
    print("  - Vender cosas personales (cero inversión)")

# %%
# === PLAN DE CONTINGENCIA ===

print("\n" + "="*80)
print("PLAN DE CONTINGENCIA")
print("="*80 + "\n")

contingencias = [
    {
        'escenario': 'No hay ventas en primeras 2 semanas',
        'accion': [
            'Reducir precios 15%',
            'Mejorar fotos y descripciones',
            'Probar otros nichos del scorecard',
            'Si persiste: liquidar y abortar'
        ]
    },
    {
        'escenario': 'Afecta calificaciones',
        'accion': [
            'Pausa inmediata del proyecto',
            'Liquidar inventario rápido (pérdida aceptable)',
            'Priorizar estudios'
        ]
    },
    {
        'escenario': 'Inventario no se liquida antes de viaje',
        'accion': [
            'Liquidación 30 días antes (precio costo)',
            'Donación a caridad (deducible)',
            'Dejar con familiar para vender',
            'Última opción: pérdida y aprendizaje'
        ]
    },
    {
        'escenario': 'No se alcanza meta de $20,000',
        'accion': [
            'Complementar con freelance en enero',
            'Ajustar presupuesto de viaje',
            'Solicitar beca parcial viaje',
            'Trabajar durante intercambio'
        ]
    }
]

for contingencia in contingencias:
    print(f"ESCENARIO: {contingencia['escenario']}")
    print("Acciones:")
    for i, accion in enumerate(contingencia['accion'], 1):
        print(f"  {i}. {accion}")
    print()

# %%
# === EXPORTAR ANÁLISIS ===

timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

# Exportar análisis de factibilidad
df_decision.to_csv(
    f'data/analytics/analisis_factibilidad_{timestamp}.csv',
    index=False,
    encoding='utf-8-sig'
)

# Exportar escenarios
for nombre, df_sim in resultados_escenarios.items():
    df_sim.to_csv(
        f'data/analytics/escenario_{nombre.lower()}_{timestamp}.csv',
        index=False,
        encoding='utf-8-sig'
    )

# Exportar matriz de riesgo
df_riesgos.to_csv(
    f'data/analytics/matriz_riesgo_{timestamp}.csv',
    index=False,
    encoding='utf-8-sig'
)

print(f"\nAnálisis exportado con timestamp: {timestamp}")
print("\nETAPA 1 COMPLETADA")
print("\nDecisión documentada. Si GO: Proceder a Etapa 2 (Operaciones)")
