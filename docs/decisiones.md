# Registro de decisiones y cambios de criterio

Sirve para escribir el punto 6 de la memoria: decisiones, sus motivos, dificultades y cambios de criterio. Añadid una fila cada vez que decidáis algo.

| Fecha | Quién | Decisión | Motivo | A qué afecta |
|---|---|---|---|---|
| 2026-11-18 | Alex y Vahab | Tema: mercado laboral tech en España (Madrid vs Barcelona) | Datos accesibles por API y scraping, y preguntas con interés práctico | Todo el proyecto |
| 2026-11-18 | Alex y Vahab | Fuentes: API de Adzuna + scraping de Tecnoempleo | Adzuna da salarios y volumen; Tecnoempleo da modalidad y salario declarado | Obtención |
| 2026-11-18 | Alex y Vahab | Unir las fuentes en dos niveles: tabla por oferta (con columna `fuente`) y tabla agregada tecnología × ciudad | La tabla agregada sola no permite estudiar las distribuciones | Preparación y EDA |
| 2026-11-18 | Alex y Vahab | Temas alternativos valorados y descartados: precio de la luz (REE + Open-Meteo), videojuegos de Steam, cine (TMDB + Wikipedia) y LaLiga (football-data.org + Transfermarkt) | Se eligió el mercado laboral tech por su interés práctico y porque las dos fuentes se pueden unir por tecnología y ciudad | Punto 1 de la memoria |
| 2026-11-18 | Vahab | Se descarta ticjob.es como fuente de scraping | Unas 103 ofertas activas en toda España; de 40 ofertas revisadas solo 1 publicaba salario numérico; sus Condiciones de uso (§2) prohíben copiar o descargar la web «por completo o en parte» | Obtención (scraping) |
| 2026-11-18 | Vahab | Se descarta InfoJobs como fuente de scraping | Su robots.txt bloquea por completo a agregadores (jobrapido) y las rutas `/react` y `/webapp` indican una web en JavaScript: más trabajo y más riesgo sin aportar nada que no den Tecnoempleo + Adzuna | Obtención (scraping) |
| 2026-11-18 | Vahab | Se confirma Tecnoempleo como fuente de scraping tras las pruebas | robots.txt permite listados (`/ofertas-trabajo/?pagina=N`) y ofertas; HTML estático; cada oferta trae JSON-LD `JobPosting` con `baseSalary` (EUR/año) cuando se publica; el «Marco Normativo» no prohíbe la extracción | Obtención (scraping) |
| 2026-11-18 | Vahab | Base legal de la extracción: arts. 134.1 y 135.1.b de la Ley de Propiedad Intelectual (extracción con fines de ilustración de la enseñanza, no comercial, citando la fuente) | Las condiciones de Tecnoempleo solo reservan los derechos de forma genérica | Memoria (punto 2) y README (citar las fuentes) |
| 2026-11-18 | Vahab | Normas del scraping: User-Agent identificado con email de contacto, pausa entre peticiones, parar ante 403/429 y no guardar datos personales (nombres, emails o teléfonos de reclutadores) | Buenas prácticas y RGPD | `src/scraper_tecnoempleo.py` |
| 2026-11-18 | Vahab | Registro en la API de Adzuna con el uso «Personal or academic research» | Los términos de Adzuna permiten la investigación académica; el análisis comercial requiere acuerdo escrito. Obliga a citar «The Adzuna API» | Obtención (API) y README |
| 2026-11-18 | Vahab | Propuesta (pendiente de confirmar): repositorio privado con acceso del profesor | Los datos originales incluyen el texto completo de las ofertas, que es contenido de terceros | GitHub |
| 2026-11-19 | Alex y Vahab | Cambio de reparto: Alex se encarga del scraping de Tecnoempleo y Vahab de la API de Adzuna (el resto del reparto no cambia) | Vahab ya tiene las credenciales de Adzuna y había hecho la prueba de la API | Obtención; memoria (puntos 2 y 6) |
| 2026-11-19 | Alex | Ampliar la lista de tecnologías de 20 a 31: Power BI, Tableau, Excel, Git, GitHub, Docker, Spark, Google Cloud, Linux, Ciberseguridad e IA generativa | Lo pidió el profesor; se añaden herramientas de análisis de datos y áreas con más crecimiento en las ofertas (datos, DevOps, cloud, ciberseguridad, IA) | `data/reference/tecnologias.csv`, `src/config.py` (consultas a Adzuna) |
| 2026-11-19 | Alex | Quitar "ia" e "inteligencia artificial" de los alias de Machine Learning | "ia" coincide con muchas palabras y se solapa con la nueva categoría IA generativa | Normalización de tecnologías |
| | | | | |
| 2026-11-19 | Alex | Añadir Google Colab, Vercel y Supabase (34 tecnologías en total) | Herramientas usadas en el propio curso; sirve para ver si el mercado las pide | `data/reference/tecnologias.csv`, `src/config.py` |
| 2026-11-19 | Alex | Quitar Ciberseguridad de la lista (33 tecnologías) | _Pendiente: añadir el motivo_ | `data/reference/tecnologias.csv`, `src/config.py` |
