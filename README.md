# 📊 DataFlip MX

Sistema de Arbitraje Comercial Guiado por Datos

## 🎯 Objetivo
Identificar oportunidades de reventa y nichos rentables usando análisis de datos, web scraping y machine learning.

## 🛠️ Instalación

```bash
# 1. Clonar repositorio o crear carpeta
mkdir dataflip-mx && cd dataflip-mx

# 2. Crear entorno virtual (recomendado)
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.template .env
# Editar .env con tus API keys
```

## 📁 Estructura del Proyecto

```
dataflip-mx/
├── data/               # Datos del proyecto
│   ├── raw/           # Datos sin procesar
│   ├── processed/     # Datos limpios
│   └── analytics/     # Reportes y visualizaciones
├── notebooks/         # Jupyter notebooks de análisis
├── src/               # Código fuente
│   ├── scrapers/     # Scripts de scraping
│   ├── analyzers/    # Análisis estadístico
│   └── utils/        # Utilidades
├── config/            # Configuración
└── logs/              # Logs de ejecución
```

## 🚀 Uso

### 1. Análisis de Mercado Libre
```bash
jupyter notebook notebooks/01_mercadolibre_api.ipynb
```

### 2. Google Trends
```bash
jupyter notebook notebooks/02_google_trends.ipynb
```

### 3. Reddit Sentiment Analysis
```bash
jupyter notebook notebooks/03_reddit_analysis.ipynb
```

## 📝 Licencia
Proyecto personal - Uso educativo

## 👤 Autor
Estudiante ITAM - Ciencia de Datos
