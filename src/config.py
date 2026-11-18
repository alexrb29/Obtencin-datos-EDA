"""Configuración común del proyecto: rutas, tecnologías y ciudades.

La lista de tecnologías y ciudades se decide en la tarjeta de Trello
"Definir preguntas, población y ámbito del estudio". Si cambia, se cambia aquí
y se anota en docs/decisiones.md.
"""
from pathlib import Path

# --- Rutas -----------------------------------------------------------------
RAIZ = Path(__file__).resolve().parents[1]
DATA = RAIZ / "data"
RAW = DATA / "raw"
RAW_ADZUNA = RAW / "adzuna"
RAW_TECNOEMPLEO = RAW / "tecnoempleo"
PROCESSED = DATA / "processed"
REFERENCE = DATA / "reference"

# --- Ámbito del estudio ----------------------------------------------------
# Clave: nombre normalizado que usaremos en el análisis.
# Valor: término de búsqueda que se envía a la API (parámetro "what").
TECNOLOGIAS = {
    "Python": "python",
    "Java": "java",
    "JavaScript": "javascript",
    "TypeScript": "typescript",
    "React": "react",
    "Angular": "angular",
    "Node.js": "node",
    ".NET": ".net",
    "PHP": "php",
    "SQL": "sql",
    "AWS": "aws",
    "Azure": "azure",
    "Kubernetes": "kubernetes",
    "SAP": "sap",
    "Salesforce": "salesforce",
    "Go": "golang",
    "Kotlin": "kotlin",
    "Swift": "swift",
    "Data Science": "data scientist",
    "Machine Learning": "machine learning",
}

# Clave: ciudad normalizada. Valor: término de búsqueda (parámetro "where").
CIUDADES = {
    "Madrid": "madrid",
    "Barcelona": "barcelona",
}
