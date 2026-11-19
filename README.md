# Mercado laboral tech en España: obtención de datos y EDA

Proyecto en parejas de la asignatura de obtención de datos y análisis exploratorio (EDA).

**Integrantes**

| Nombre | Responsabilidades principales |
|---|---|
| Alex Rodríguez | Scraping de Tecnoempleo, unión de fuentes, EDA de variables numéricas, preguntas 1 y 2 |
| Vahab Azimzadeh | API de Adzuna, diccionario de datos, EDA de variables categóricas y ausentes, pregunta 3 |

El reparto detallado y su seguimiento están en el tablero de Trello del proyecto y se resumen en la memoria (`docs/memoria.md`).

## Objetivo

Analizar las ofertas de empleo tecnológico publicadas en España para responder:

1. ¿Qué tecnologías se asocian a salarios anunciados más altos?
2. ¿Hay diferencias entre Madrid y Barcelona en volumen de ofertas y salario?
3. ¿Cómo se reparten y qué salario tienen las ofertas remotas, híbridas y presenciales?
4. (Complementaria) ¿Qué ofertas publican el salario y cuáles no?

> Unidad de análisis: **oferta publicada**, no sueldo real. Las conclusiones se refieren a salarios *anunciados*.

## Fuentes

| Fuente | Tipo | Qué aporta | Detalle |
|---|---|---|---|
| [Adzuna API](https://developer.adzuna.com/) | API REST | Volumen de ofertas y salarios por tecnología y ciudad; histograma de salarios | `docs/fuentes.md` |
| [Tecnoempleo](https://www.tecnoempleo.com/) | Web scraping | Modalidad (remoto/híbrido/presencial), salario declarado y tecnologías de cada oferta | `docs/fuentes.md` |

En `docs/fuentes.md` están las URL consultadas, la fecha de obtención, los campos recogidos, el procedimiento y la revisión de `robots.txt` y de las condiciones de uso. Allí también se explican las fuentes que probamos y descartamos (ticjob.es e InfoJobs).

**Atribución.** Datos obtenidos de [The Adzuna API](https://www.adzuna.es) y de [Tecnoempleo](https://www.tecnoempleo.com), con fines exclusivamente académicos y no comerciales.

## Organización del repositorio

```
.
├── data/
│   ├── raw/            # Datos originales tal como se descargaron (no se modifican)
│   │   ├── adzuna/
│   │   └── tecnoempleo/
│   ├── processed/      # Datos limpios y unificados listos para el análisis
│   └── reference/      # Tablas auxiliares: tecnologías y ciudades normalizadas
├── docs/
│   ├── memoria.md      # Memoria del proyecto
│   ├── fuentes.md      # Registro de fuentes y procedimiento de obtención
│   ├── decisiones.md   # Registro de decisiones y cambios de criterio
│   ├── capturas/       # Capturas de robots.txt y condiciones de uso
│   └── diccionario_datos.md
├── notebooks/          # Cuadernos del análisis, en orden de ejecución
├── src/                # Código reutilizable: descarga, scraping y limpieza
├── pruebas/            # Scripts con los que evaluamos las fuentes (18/11/2026)
├── .env.example        # Plantilla de las claves de la API
├── requirements.txt
└── README.md
```

## Instalación

Requisitos: Python 3.10 o superior.

```bash
git clone https://github.com/alexrb29/Obtenci-n-de-datos-y-EDA.git
cd Obtenci-n-de-datos-y-EDA

python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### Claves de la API de Adzuna

1. Registraos en <https://developer.adzuna.com/> y cread una aplicación.
2. Copiad `.env.example` como `.env` y pegad vuestro `app_id` y `app_key`.
3. El archivo `.env` está en `.gitignore`: **nunca** se sube al repositorio.

## Ejecución

Desde la raíz del repositorio:

```bash
# 1. Comprobar que la API responde (2 llamadas)
python src/adzuna.py --prueba

# 2. Descargar las ofertas de Adzuna (tecnologías × ciudades)
python src/adzuna.py --descargar --max-paginas 3

# 3. Scraping del portal de empleo
python src/scraper_tecnoempleo.py --max-paginas 5
```

Después, ejecutad los cuadernos de `notebooks/` en orden:

| Cuaderno | Contenido |
|---|---|
| `01_obtencion.ipynb` | Carga y revisión de los datos originales |
| `02_limpieza.ipynb` | Limpieza, normalización y unión de fuentes |
| `03_eda_univariante.ipynb` | Distribuciones de todas las variables |
| `04_eda_bivariante.ipynb` | Análisis de relaciones para responder a las preguntas |
| `05_conclusiones.ipynb` | Resultados finales y limitaciones |

Los datos ya descargados están en `data/raw/`, así que los cuadernos se pueden ejecutar sin volver a llamar a la API.
