"""
DataFlip MX - Script de Configuración Inicial
Crea la estructura de carpetas y archivos necesarios para el proyecto
"""

import os
import subprocess
import sys

def create_project_structure():
    """Crea la estructura de carpetas del proyecto"""
    
    folders = [
        'data/raw',
        'data/processed',
        'data/analytics',
        'notebooks',
        'src/scrapers',
        'src/analyzers',
        'src/utils',
        'config',
        'logs'
    ]
    
    print("📁 Creando estructura de carpetas...")
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
        print(f"   ✓ {folder}")
    
    # Crear archivos __init__.py para que Python reconozca los módulos
    init_paths = ['src', 'src/scrapers', 'src/analyzers', 'src/utils']
    for path in init_paths:
        init_file = os.path.join(path, '__init__.py')
        with open(init_file, 'w') as f:
            f.write(f"# {path} module\n")
    
    print("\n✅ Estructura creada correctamente\n")

def create_requirements_file():
    """Crea el archivo requirements.txt con todas las dependencias"""
    
    requirements = """# DataFlip MX - Dependencias del Proyecto
# Actualizado: Diciembre 2024

# === CORE ===
pandas>=2.0.0
numpy>=1.24.0
python-dotenv>=1.0.0

# === WEB SCRAPING & APIs ===
requests>=2.31.0
beautifulsoup4>=4.12.0
selenium>=4.15.0
lxml>=4.9.0

# === GOOGLE TRENDS ===
pytrends>=4.9.0

# === REDDIT API ===
praw>=7.7.0

# === DATA ANALYSIS ===
scikit-learn>=1.3.0
scipy>=1.11.0

# === VISUALIZACIÓN ===
plotly>=5.17.0
matplotlib>=3.7.0
seaborn>=0.12.0

# === JUPYTER ===
jupyter>=1.0.0
ipykernel>=6.25.0

# === UTILIDADES ===
tqdm>=4.66.0  # Progress bars
openpyxl>=3.1.0  # Para exportar Excel
"""
    
    with open('requirements.txt', 'w', encoding='utf-8') as f:
        f.write(requirements)
    
    print("📄 Archivo requirements.txt creado\n")

def create_config_file():
    """Crea el archivo de configuración template"""
    
    config = """# DataFlip MX - Configuración
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
"""
    
    with open('config/settings.py', 'w', encoding='utf-8') as f:
        f.write(config)
    
    print("⚙️  Archivo config/settings.py creado\n")

def create_env_template():
    """Crea el template del archivo .env"""
    
    env_template = """# DataFlip MX - Variables de Entorno
# Copia este archivo como .env y llena tus API keys

# === MERCADO LIBRE ===
# Obtener en: https://developers.mercadolibre.com.mx/
MELI_CLIENT_ID=tu_client_id_aqui
MELI_CLIENT_SECRET=tu_client_secret_aqui

# === REDDIT ===
# Crear app en: https://www.reddit.com/prefs/apps
REDDIT_CLIENT_ID=tu_reddit_client_id
REDDIT_CLIENT_SECRET=tu_reddit_secret
"""
    
    with open('.env.template', 'w', encoding='utf-8') as f:
        f.write(env_template)
    
    print("🔐 Archivo .env.template creado")
    print("   ⚠️  Copia este archivo como .env y agrega tus API keys\n")

def create_gitignore():
    """Crea el archivo .gitignore"""
    
    gitignore = """# DataFlip MX - Git Ignore

# === PYTHON ===
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
*.egg-info/

# === JUPYTER ===
.ipynb_checkpoints
*.ipynb_checkpoints

# === DATOS Y LOGS ===
data/raw/*
data/processed/*
data/analytics/*
logs/*
*.csv
*.json
*.xlsx

# Excepciones (mantener estructura)
!data/raw/.gitkeep
!data/processed/.gitkeep
!data/analytics/.gitkeep
!logs/.gitkeep

# === CREDENCIALES ===
.env
config/secrets.py
*.key

# === SISTEMA ===
.DS_Store
Thumbs.db
"""
    
    with open('.gitignore', 'w', encoding='utf-8') as f:
        f.write(gitignore)
    
    print("🚫 Archivo .gitignore creado\n")

def create_readme():
    """Crea el README del proyecto"""
    
    readme = """# 📊 DataFlip MX

Sistema de Arbitraje Comercial Guiado por Datos

## 🎯 Objetivo
Identificar oportunidades de reventa y nichos rentables usando análisis de datos, web scraping y machine learning.

## 🛠️ Instalación

```bash
# 1. Clonar repositorio o crear carpeta
mkdir dataflip-mx && cd dataflip-mx

# 2. Crear entorno virtual (recomendado)
python -m venv venv
source venv/bin/activate  # En Windows: venv\\Scripts\\activate

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
"""
    
    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(readme)
    
    print("📖 README.md creado\n")

import os
import sys
import subprocess

def install_dependencies():
    """Pregunta al usuario si desea crear venv e instalar las dependencias"""

    print("\n" + "="*60)
    print("📦 INSTALACIÓN DE DEPENDENCIAS CON VENV")
    print("="*60)

    response = input("\n¿Deseas crear un entorno virtual y instalar las dependencias ahora? (s/n): ").lower()

    if response == 's':
        venv_dir = "venv"

        # Crear venv si no existe
        if not os.path.exists(venv_dir):
            print("\n⏳ Creando entorno virtual...\n")
            subprocess.check_call([sys.executable, "-m", "venv", venv_dir])
            print("✅ Entorno virtual creado en ./venv\n")
        else:
            print("⚠️ Ya existe un entorno virtual en ./venv\n")

        # Usar el pip del venv
        pip_path = os.path.join(venv_dir, "bin", "pip") if os.name != "nt" else os.path.join(venv_dir, "Scripts", "pip.exe")

        print("\n⏳ Instalando paquetes desde requirements.txt...\n")
        try:
            subprocess.check_call([pip_path, "install", "-r", "requirements.txt"])
            print("\n✅ Dependencias instaladas correctamente en el entorno virtual\n")
            print(f"👉 Para activarlo:\n   source {venv_dir}/bin/activate   # Linux/Mac\n   {venv_dir}\\Scripts\\activate     # Windows\n")
        except subprocess.CalledProcessError:
            print("\n❌ Error al instalar dependencias")
            print("   Intenta manualmente: pip install -r requirements.txt\n")
    else:
        print("\n⚠️ Recuerda instalar las dependencias más tarde:")
        print("   pip install -r requirements.txt\n")


def main():
    """Función principal"""
    
    print("\n" + "="*60)
    print("🚀 DATAFLIP MX - CONFIGURACIÓN INICIAL")
    print("="*60 + "\n")
    
    # Verificar versión de Python
    if sys.version_info < (3, 10):
        print("⚠️  ADVERTENCIA: Se recomienda Python 3.10 o superior")
        print(f"   Tu versión: {sys.version}\n")
    
    # Ejecutar pasos de configuración
    create_project_structure()
    create_requirements_file()
    create_config_file()
    create_env_template()
    create_gitignore()
    create_readme()
    
    # Crear archivos .gitkeep para mantener carpetas vacías en Git
    gitkeep_folders = [
        'data/raw', 'data/processed', 'data/analytics', 'logs'
    ]
    for folder in gitkeep_folders:
        with open(os.path.join(folder, '.gitkeep'), 'w') as f:
            pass
    
    print("="*60)
    print("✅ PROYECTO CONFIGURADO CORRECTAMENTE")
    print("="*60)
    
    print("\n📋 Próximos pasos:")
    print("   1. Copiar .env.template como .env")
    print("   2. Registrarte en Mercado Libre Developers")
    print("   3. Obtener tus API keys y agregarlas al .env")
    print("   4. Ejecutar: jupyter notebook\n")
    
    # Preguntar sobre instalación de dependencias
    install_dependencies()
    
    print("🎉 ¡Listo para empezar con el análisis de datos!\n")

if __name__ == '__main__':
    main()