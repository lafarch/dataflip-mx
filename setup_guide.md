# 🚀 DATAFLIP MX - Guía de Inicio Rápido

## 📋 **Tabla de Contenidos**
1. [Requisitos Previos](#requisitos-previos)
2. [Instalación Paso a Paso](#instalación-paso-a-paso)
3. [Configuración de APIs](#configuración-de-apis)
4. [Ejecución de Análisis](#ejecución-de-análisis)
5. [Interpretación de Resultados](#interpretación-de-resultados)
6. [Solución de Problemas](#solución-de-problemas)

---

## 🔧 **Requisitos Previos**

### Software Necesario
- **Python 3.10+** ([Descargar](https://www.python.org/downloads/))
- **Git** (opcional, para control de versiones)
- **Editor de código**: VS Code, PyCharm, o Jupyter Lab

### Conocimientos Recomendados
- Python básico (variables, funciones, loops)
- Pandas básico (leer/manipular DataFrames)
- Conceptos de APIs y requests HTTP

**¿No sabes Python?** No hay problema, los notebooks están comentados línea por línea.

---

## 📥 **Instalación Paso a Paso**

### **Paso 1: Clonar el Repositorio**

```bash
# Clonar el proyecto desde GitHub
git clone https://github.com/lafarch/dataflip-mx.git
cd dataflip-mx
```
### **Paso 2: Verificar Descarga Exitosa**

```bash
ls -la
```

Deberías ver:
- Estructura de carpetas completa
- Archivo `requirements.txt` con todas las dependencias
- Configuración inicial en `config/settings.py`
- Template de variables de entorno (`.env.template`)

### **Paso 3: Crear Entorno Virtual (Recomendado)**

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

**¿Por qué entorno virtual?**
- Aísla las dependencias del proyecto
- Evita conflictos con otras instalaciones de Python
- Buena práctica en Data Science

### **Paso 4: Instalar Dependencias**

```bash
pip install -r requirements.txt
```

**Tiempo estimado:** 3-5 minutos

**Si encuentras errores:**
- Verifica tu versión de Python: `python --version`
- Actualiza pip: `python -m pip install --upgrade pip`
- Instala paquetes uno por uno para identificar el problema

---

## 🔑 **Configuración de APIs**

### **A. Mercado Libre API (GRATIS)**

1. **Crear cuenta de desarrollador:**
   - Ve a: https://developers.mercadolibre.com.mx/
   - Haz clic en "Registrar tu aplicación"
   - Inicia sesión con tu cuenta de Mercado Libre

2. **Crear una aplicación:**
   - Nombre: "DataFlip MX Análisis"
   - Descripción corta: "Análisis de mercado para reventa"
   - Callback URL: `https://localhost` (no es necesaria para búsquedas públicas)
   - Topics: Busca "Items and Searches"

3. **Obtener credenciales:**
   - Copia tu `Client ID` y `Client Secret`

4. **Configurar en el proyecto:**
   ```bash
   # Copiar template
   cp .env.template .env
   
   # Editar .env con tu editor favorito
   nano .env  # o code .env, o vim .env
   ```
   
   Agregar:
   ```env
   MELI_CLIENT_ID=tu_client_id_aqui
   MELI_CLIENT_SECRET=tu_client_secret_aqui
   ```

**💡 IMPORTANTE:** La API pública de Mercado Libre NO requiere autenticación para búsquedas básicas. Las credenciales solo son necesarias para operaciones avanzadas.

---

### **B. Google Trends (pytrends) - SIN API KEY**

✅ **No necesitas configuración adicional**

`pytrends` usa web scraping ético de Google Trends. No requiere API key.

**Limitaciones:**
- No hacer más de 1 request cada 2 segundos
- Google puede bloquear temporalmente si abusas
- Los notebooks ya incluyen delays apropiados

---

### **C. Reddit API (OPCIONAL)**

1. **Crear aplicación de Reddit:**
   - Ve a: https://www.reddit.com/prefs/apps
   - Scroll hasta abajo → "create another app..."
   - Tipo: "script"
   - Redirect URI: `http://localhost:8080`

2. **Obtener credenciales:**
   - Copia el Client ID (debajo de "personal use script")
   - Copia el Secret

3. **Configurar:**
   ```env
   REDDIT_CLIENT_ID=tu_client_id
   REDDIT_CLIENT_SECRET=tu_secret
   ```

**⚠️ NOTA:** Si no configuras Reddit, el notebook 03 saltará esa parte automáticamente.

---

## 🎯 **Ejecución de Análisis**

### **Iniciar Jupyter Notebook**

```bash
jupyter notebook
```

**Esto abrirá tu navegador con el explorador de archivos.**

---

### **📓 Orden de Ejecución**

Ejecuta los notebooks en este orden:

#### **0. `00_descubrimiento_nichos.ipynb`** (20 min) ⭐ NUEVO

**Qué hace:**
- Explora TODO Mercado Libre automáticamente
- Analiza 10+ categorías completas
- Identifica productos con alta demanda y baja competencia
- Genera lista de nichos prometedores SIN sesgo manual

**Cómo ejecutar:**
- Abre el notebook
- Run All (no requiere configuración previa)

**Output esperado:**
- Mapa visual de oportunidades (demanda vs competencia)
- Top 15-20 nichos descubiertos automáticamente
- Score de ratio demanda/competencia

**Archivos generados:**
- `data/analytics/nichos_descubiertos_[timestamp].csv` ⭐
- `data/raw/discovery_productos_[timestamp].csv`

**💡 TIP:** Este notebook reemplaza la necesidad de "adivinar" nichos manualmente.

---

#### **1. `01_mercadolibre_api.ipynb`** (30 min)

**Qué hace:**
- Busca productos en Mercado Libre
- Analiza precios, volumen de ventas, competencia
- Genera scorecard por nicho

**Cómo ejecutar:**
- Abre el notebook
- Click en "Cell" → "Run All" (o Shift+Enter en cada celda)

**Output esperado:**
- Gráficas de distribución de precios
- Top productos más vendidos
- Scorecard de nichos con scores 1-10

**Archivos generados:**
- `data/processed/meli_analisis_[timestamp].csv`
- `data/analytics/meli_scorecard_[timestamp].csv`

---

#### **2. `02_google_trends.ipynb`** (20 min)

**Qué hace:**
- Valida demanda real de búsqueda en Google
- Analiza tendencias temporales y estacionalidad
- Identifica búsquedas relacionadas

**Cómo ejecutar:**
- Run All

**Output esperado:**
- Gráfica de tendencias en el tiempo
- Análisis de estacionalidad
- Score de volumen de búsqueda

**Archivos generados:**
- `data/processed/trends_timeseries_[timestamp].csv`
- `data/analytics/trends_scores_[timestamp].csv`

---

#### **3. `03_reddit_sentiment.ipynb`** (15 min - OPCIONAL)

**Qué hace:**
- Busca menciones en Reddit
- Identifica quejas y necesidades
- Análisis cualitativo de comunidades

**Cómo ejecutar:**
- Si NO configuraste Reddit API: El notebook te avisará y saltará esta parte
- Si SÍ configuraste: Run All

**Output esperado:**
- Posts con oportunidades detectadas
- Palabras más mencionadas
- Estadísticas por subreddit

---

#### **4. `04_analisis_integrado.ipynb`** (15 min)

**Qué hace:**
- Combina TODOS los análisis anteriores
- Genera el **SCORECARD FINAL**
- Clasifica nichos en categorías (Quick Win, Cash Cow, etc.)

**Cómo ejecutar:**
- Run All
- Este notebook lee automáticamente los CSVs generados anteriormente

**Output esperado:**
- 🏆 **TOP 10 NICHOS RANKEADOS**
- Matriz de decisión
- Recomendaciones personalizadas
- Archivo Excel final

**Archivos generados:**
- `data/analytics/SCORECARD_FINAL_[timestamp].xlsx` ⭐

---

### **🕷️ Web Scraping (OPCIONAL - AVANZADO)**

Si quieres aprender web scraping:

```bash
python src/scrapers/amazon_scraper.py
```

**⚠️ IMPORTANTE:**
- Lee el código primero para entender qué hace
- Respeta `robots.txt` siempre
- Usa con moderación (delays de 3-5 segundos)
- Amazon puede bloquear IPs si detecta bot behavior

---

## 📊 **Interpretación de Resultados**

### **Entender el Scorecard Final**

| Columna | Qué Significa | Ideal |
|---------|---------------|-------|
| `SCORE_FINAL` | Score combinado de todas las fuentes | ≥ 7.5 |
| `SCORE_TOTAL` (MeLi) | Competencia + Margen + Logística | ≥ 7.0 |
| `score_final` (Trends) | Demanda de búsqueda | ≥ 7.5 |
| `precio_promedio` | Precio promedio del nicho | Depende del producto |
| `tendencia` | Crecimiento (+) o decrecimiento (-) | Positivo |
| `categoria` | Clasificación estratégica | 🔥 Quick Win |

---

### **Categorías de Nichos**

#### 🔥 **QUICK WIN** (Score ≥8, Alta demanda)
**Acción:** Empezar AHORA
- Alta demanda en Google
- Baja competencia en Mercado Libre
- Oportunidad inmediata

**Ejemplo:** Calculadora HP 12C en época de exámenes

---

#### 💰 **CASH COW** (Score ≥7, Mercado estable)
**Acción:** Invertir con confianza
- Mercado establecido
- Márgenes comprobados
- Menos riesgo

**Ejemplo:** Teclados mecánicos (siempre hay demanda)

---

#### 🌱 **EMERGING** (Tendencia positiva)
**Acción:** Validar antes de escalar
- Mercado creciendo
- Potencial alto pero riesgoso
- Ideal para early adopters

**Ejemplo:** Cámaras vintage Y2K aesthetic

---

#### ⚖️ **BALANCED** (Score 6-7)
**Acción:** Probar con inversión mínima
- Ni muy bueno ni muy malo
- Requiere más análisis manual
- Puede funcionar con buena ejecución

---

#### ❌ **AVOID** (Score <6)
**Acción:** Buscar alternativas
- Demasiada competencia o poca demanda
- No vale la pena el esfuerzo
- Busca otro nicho

---

## 🐛 **Solución de Problemas**

### **Error: "Module not found"**
```bash
# Verifica que el entorno virtual esté activado
# Reinstala las dependencias
pip install -r requirements.txt
```

---

### **Error: "API rate limit exceeded" (Google Trends)**
```bash
# Solución: Aumenta el delay en el notebook
REQUEST_DELAY = 5  # Cambiar de 2 a 5 segundos
```

---

### **Error: "503 Service Unavailable" (Amazon scraping)**
```bash
# Esto significa que Amazon detectó el bot
# Soluciones:
# 1. Aumentar MIN_DELAY y MAX_DELAY
# 2. Usar un proxy
# 3. Rotar User-Agents
# 4. Esperar unas horas antes de reintentar
```

---

### **Error: "No module named 'config'"**
```bash
# Asegúrate de estar en la carpeta raíz del proyecto
cd dataflip-mx

# Verifica que existe config/__init__.py
ls config/__init__.py
```

---

### **Los gráficos de Plotly no se muestran en Jupyter**
```bash
# Instalar extensión de Plotly
pip install "jupyterlab>=3" "ipywidgets>=7.6"

# O usar en notebook:
import plotly.io as pio
pio.renderers.default = "notebook"
```

---

## 🎓 **Próximos Pasos**

Una vez que tengas el scorecard final:

### **1. Simulador de Márgenes**
- Calcular ROI esperado
- Simular diferentes escenarios de precios
- Determinar punto de equilibrio

### **2. Plan de Ejecución**
- Sourcing: ¿Dónde comprar inventario?
- Listing: Optimizar títulos y fotos
- Pricing: Estrategia de precios dinámica

### **3. Legal y Fiscal**
- Darse de alta en SAT (Resico)
- Configurar facturación
- Entender obligaciones fiscales

---

## 📞 **Recursos Adicionales**

- **Documentación Mercado Libre API:** https://developers.mercadolibre.com.mx/
- **Reddit API (PRAW):** https://praw.readthedocs.io/
- **Pytrends:** https://github.com/GeneralMills/pytrends
- **Plotly:** https://plotly.com/python/

---

## ✅ **Checklist de Verificación**

Antes de empezar a vender, asegúrate de:

- [ ] Haber ejecutado todos los notebooks
- [ ] Tener el SCORECARD_FINAL.xlsx generado
- [ ] Haber identificado tu nicho #1
- [ ] Entender por qué ese nicho es el mejor
- [ ] Haber calculado capital inicial necesario
- [ ] Tener un plan de sourcing (dónde comprar)
- [ ] Conocer tus márgenes esperados (40%+)
- [ ] Tener cuenta de Mercado Libre lista
- [ ] Haber revisado aspectos fiscales básicos

---

## 🚀 **¡Listo para Empezar!**

Recuerda:
1. **Valida antes de escalar** - Empieza con 3-5 productos
2. **Mide todo** - Trackea cada venta, costo, ganancia
3. **Itera rápido** - Si no funciona en 2 semanas, pivotea
4. **Aprende constantemente** - Cada venta es data

**¡Mucho éxito con DataFlip MX! 📊💰**
