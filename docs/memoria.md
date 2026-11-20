# Memoria del proyecto: mercado laboral tech en España

**Integrantes:** Alex Rodríguez y Vahab Azimzadeh
**Entrega:** 30 de noviembre de 2026

> Borrador con la estructura del enunciado (puntos 1 a 6). Cada sección indica quién la redacta; el otro la revisa.
>
> **Estado (20/11/2026):** redactados, con los datos de Tecnoempleo, la obtención por scraping (2.2), su limpieza (3.2), el EDA de variables numéricas (4.1) y las preguntas P1 (5.1) y P2 (5.2). Se actualizarán al unir los datos de Jooble.

## 1. Elección del tema, preguntas y ámbito *(ambos)*

- Por qué este tema.
- Preguntas del estudio.
- Población (ofertas tech publicadas en España durante el periodo de captura), muestra y unidad de observación (la oferta).
- Qué datos hacen falta y por qué.

### Tecnologías del estudio *(Alex)*

La lista de tecnologías que analizamos está en `data/reference/tecnologias.csv`, junto con las distintas formas en que aparece cada una en las ofertas (por ejemplo, ".NET", "dotnet", "C#" o "ASP.NET" cuentan como .NET). La misma lista se usa en `src/config.py`, de modo que el scraping y la API buscan exactamente las mismas tecnologías.

Partimos de 20 tecnologías habituales en desarrollo, datos y cloud. A petición del profesor la ampliamos:

- **Herramientas de análisis y control de versiones:** Power BI, Tableau, Excel, Git y GitHub.
- **Áreas con más crecimiento en las ofertas tecnológicas de 2025–2026:** Docker y Linux (perfiles DevOps y de sistemas), Spark y Google Cloud (ingeniería de datos), e IA generativa. Según el informe *Tech Cities 2026* de Experis, el perfil de Data Engineer es el que más ha crecido (+42 % entre 2023 y 2025), y según InfoJobs las ofertas que piden herramientas de inteligencia artificial crecieron un 64 % en el último año.
- **Herramientas que usamos en el curso:** Google Colab, Vercel y Supabase, para comprobar si el mercado las pide.

En una primera versión incluimos también Ciberseguridad, porque es uno de los perfiles más demandados, pero después la quitamos: no forma parte de nuestra especialidad. Estudiamos Inteligencia Artificial y Big Data, y la ciberseguridad es una rama distinta, así que preferimos centrar el análisis en las tecnologías de nuestro campo. La lista final tiene **33 tecnologías**.

## 2. Obtención de los datos

### 2.1 API *(Vahab)*
### 2.2 Web scraping de Tecnoempleo *(Alex)*

**Por qué Tecnoempleo.** Es un portal especializado en empleo tecnológico, con un HTML estático fácil de leer y, en cada oferta del listado, datos que no suelen dar otras fuentes: la **modalidad de trabajo** (presencial, híbrida o 100 % remota), el **salario** cuando la empresa lo publica y las **tecnologías** que pide. Las razones para descartar ticjob.es e InfoJobs están en el registro de decisiones.

**Comprobaciones legales y técnicas previas.** Revisamos el `robots.txt` del portal: para cualquier robot (`User-agent: *`) solo prohíbe rutas internas como `/profesionales/`, `/accesoempresa.php` o `/graficos_estadisticas/`, y ninguna regla afecta a los listados de ofertas (`/ofertas-trabajo/`). La base legal y las condiciones de uso están en el registro de decisiones (`docs/decisiones.md`).

**Qué páginas descargamos.** Los listados de ofertas filtrados por provincia, que se recorren con el parámetro `pagina`:

| Ciudad | URL | Páginas | Ofertas |
|---|---|---|---|
| Madrid | `https://www.tecnoempleo.com/ofertas-trabajo/?pr=,263,&pagina=N` | 35 | 1.021 |
| Barcelona | `https://www.tecnoempleo.com/ofertas-trabajo/?pr=,240,&pagina=N` | 22 | 631 |

**Cómo funciona el script (`src/scraper_tecnoempleo.py`).**

1. Descarga cada página con la librería `requests`, identificándose con un User-Agent propio que incluye un email de contacto, y espera 5 segundos entre peticiones para no sobrecargar la web.
2. Antes de cada petición comprueba en el `robots.txt` que la URL está permitida.
3. Guarda el **HTML original** de cada página en `data/raw/tecnoempleo/<fecha>/html/`, de modo que los datos de partida quedan disponibles aunque la web cambie.
4. Con `BeautifulSoup` localiza cada tarjeta de oferta (`div.p-3.border.rounded.mb-3.bg-white`) y extrae sus campos. Los selectores se obtuvieron inspeccionando una página de resultados guardada desde el navegador.
5. Se detiene al llegar al final del listado: cuando una página no trae ofertas nuevas o el portal responde con un error 404 porque esa página ya no existe.

**Campos obtenidos por oferta:** identificador, título, empresa, ubicación, modalidad, categoría del puesto, salario (texto, p. ej. "18.000€ - 21.000€ b/a"), tipo de contrato, tecnologías (etiquetas de la oferta), fecha de publicación o actualización, estado (nueva o actualizada), si es urgente, resumen de la descripción y URL. A cada fila se le añade la ciudad del listado, la página y la fecha de obtención. No se guardan datos personales.

**Resultado.** La descarga se hizo el **19 de noviembre de 2026**: 57 páginas HTML y un CSV con **1.652 filas**, que corresponden a **1.297 ofertas distintas**, porque las ofertas 100 % remotas aparecen tanto en el listado de Madrid como en el de Barcelona. El 30 % de las ofertas (392) publica salario.

Detalle técnico en `docs/fuentes.md`.
### 2.3 Qué aporta cada fuente *(ambos)*

## 3. Preparación de los datos

### 3.1 Limpieza de los datos de la API *(Vahab)*
### 3.2 Limpieza del scraping *(Alex)*

La limpieza está en `src/limpieza_tecnoempleo.py` y se ejecuta paso a paso, con comprobaciones, en la sección 2.2 del cuaderno `notebooks/02_limpieza.ipynb`. Los datos originales no se modifican: el resultado se guarda en `data/processed/`.

1. **Duplicados.** Las 316 ofertas 100 % remotas aparecían en los dos listados (355 filas repetidas). No son errores de la web, pero contarlas dos veces inflaría los resultados. Dejamos **una fila por oferta** (identificador `id_oferta`) y guardamos en dos columnas en qué listados apareció. Pasamos de 1.652 filas a 1.297 ofertas.

2. **Modalidad.** La normalizamos a cuatro valores: Híbrido (430), Presencial (121), Remoto (316) y No indicada (430), cuando la oferta solo muestra la ciudad.

3. **Ciudad.** Creamos una variable para comparar ciudades con cinco grupos: Madrid (659), Barcelona (267), Sin ciudad porque la oferta es remota (316), Otra ciudad (33) y No indicada (22). El grupo "Otra ciudad" existe porque los listados incluyen algunas ofertas de otras provincias; por ejemplo, 21 ofertas de Cajamar en Almería aparecían en el listado de Madrid. Las ofertas remotas no se asignan a ninguna ciudad.

4. **Salario.** El portal da el salario como texto y en tres unidades: bruto anual (387 ofertas), mensual (3) y por hora (2). Lo convertimos a números y a **euros brutos al año**: el mensual se multiplica por 12 y el de por hora por 1.760 (40 horas semanales durante 44 semanas). Un salario marcado como mensual de 30.000–45.000 € es casi seguro un salario anual con la unidad mal puesta, así que lo tratamos como anual y lo dejamos marcado en la columna `salario_corregido`. De cada rango calculamos el punto medio (`salario_medio`). La mediana resultante es de 37.500 € anuales.

5. **Valores extremos del salario.** Los salarios más bajos (7.500–14.000 €) son puestos de helpdesk a jornada parcial o de fin de semana, y los más altos (85.000–90.000 €) son puestos directivos como CTO o Head of AI. Son ofertas reales, no errores, así que no las eliminamos. Marcamos las 10 ofertas que parecen de jornada parcial (`posible_jornada_parcial`) para poder separarlas al comparar salarios.

6. **Fechas.** Convertimos la fecha a formato fecha y calculamos la antigüedad de cada oferta respecto al día de la descarga. 155 ofertas se publicaron hace más de 90 días, algunas incluso en 2017, y siguen activas en el portal. No las borramos; las marcamos con la columna `reciente` para decidir en el análisis si se incluyen.

7. **Tecnologías.** Buscamos las 33 tecnologías del estudio en las etiquetas de cada oferta y en su título, usando las formas alternativas de `tecnologias.csv` y comparando **palabras completas**, para que "javascript" no cuente como Java ni "github" como Git. No usamos el resumen de la descripción porque llega recortado. El resultado es una tabla aparte (`tecnoempleo_tecnologias.csv`) con una fila por oferta y tecnología, porque una oferta puede pedir varias. 693 ofertas piden al menos una tecnología del estudio. Las más frecuentes son Java (141), SQL (115), SAP (93) y Python (91). **Google Colab, Vercel y Supabase no aparecen en ninguna oferta.**

8. **Otros campos.** El tipo de contrato solo aparece en 53 ofertas (temporal, freelance, prácticas u obra y servicio); en el resto lo dejamos como "No indicado".

**Conjunto final de Tecnoempleo:** `data/processed/tecnoempleo_ofertas.csv`, con 1.297 ofertas y 28 variables, y `data/processed/tecnoempleo_tecnologias.csv`.
### 3.3 Unión de las fuentes *(Alex)*
### 3.4 Descripción del conjunto final *(Vahab)*

Qué representa cada fila, número de observaciones y variables, significado, unidades y tipo (ver `docs/diccionario_datos.md`). Nulos, duplicados y errores: qué se hizo y por qué.

## 4. EDA univariante

### 4.1 Variables numéricas *(Alex)*

Cuaderno `notebooks/03_eda_univariante.ipynb`, sección 3.1. De momento con los datos de Tecnoempleo; se actualizará al unir las fuentes.

- **Salario.** Solo el 30 % de las ofertas (392) publica salario. El salario medio anunciado tiene una **mediana de 37.500 €** brutos al año; la mitad central de las ofertas está entre 30.000 y 46.500 €, y el 90 % entre 19.500 y 66.000 €.
- **Forma de la distribución.** Es asimétrica hacia la derecha (asimetría 0,90): unas pocas ofertas muy bien pagadas elevan la media (38.879 €) por encima de la mediana. Por eso, para comparar grupos usamos la mediana y el rango intercuartílico. Probamos la escala logarítmica, pero corregía de más la asimetría (−0,42), así que trabajamos en euros.
- **Tramos de 3.000 €.** El 95 % de los salarios mínimos son múltiplos de 3.000 €, lo que indica que el portal hace elegir el salario por tramos. Por eso los histogramas usan intervalos de 3.000 €.
- **Rango salarial.** La diferencia mediana entre el salario máximo y el mínimo es de 6.000 €; un 4,8 % de las ofertas da un salario fijo.
- **Valores atípicos.** Con la regla del rango intercuartílico, 13 ofertas superan los 71.250 €. Las revisamos una a una: son puestos senior o directivos (arquitectos, *leads*, CTO, Head of AI) y un perfil freelance por horas. Son ofertas reales y las mantenemos. Las 9 ofertas con salario de posible jornada parcial apenas cambian la media (de 38.879 a 39.401 €) y no cambian la mediana.
- **Antigüedad.** La mitad de las ofertas se publicó hace 8 días o menos, pero 96 llevan más de un año en el portal (hasta 9 años), lo que da una distribución muy asimétrica (5,06).
- **Número de tecnologías.** El 47 % de las ofertas no pide ninguna de las 33 tecnologías del estudio; la mayoría del resto pide una o dos.
### 4.2 Variables categóricas y valores ausentes *(Vahab)*

## 5. Análisis de relaciones y resultados

### 5.1 Tecnologías y salario *(Alex)*

Cuaderno `notebooks/04_eda_bivariante.ipynb`, pregunta P1. Como solo el 30 % de las ofertas publica salario, comparamos salarios solo en las tecnologías con **al menos 10 salarios** (10 de las 33) y mostramos siempre el tamaño de cada grupo.

- **Demanda.** Las tecnologías más pedidas son Java (141 ofertas), SQL (115), SAP (93) y Python (91), seguidas de AWS y Azure. Google Colab, Vercel y Supabase no aparecen en ninguna oferta.
- **Salario.** Las mejor pagadas son **SAP y .NET** (mediana de 49.500 €), seguidas de JavaScript, AWS y Azure (42.000–42.750 €). Java, Linux y Python están en torno a la mediana general (37.500 €), SQL algo por debajo (33.750 €) y **Excel muy por debajo** (21.750 €), porque aparece sobre todo en puestos de tienda, reparación o administración.
- **Más demanda no implica más salario:** Java, SQL y Python son de las más pedidas, pero no de las mejor pagadas.
- **Significación.** Las diferencias entre tecnologías son significativas según la prueba de Kruskal-Wallis (p < 0,001), y lo siguen siendo sin Excel (p = 0,024).
- **Limitación.** Los grupos son pequeños (10–30 salarios) y sus rangos se solapan, así que el orden exacto entre tecnologías cercanas no es fiable.
### 5.2 Madrid frente a Barcelona *(Alex)*

Cuaderno `notebooks/04_eda_bivariante.ipynb`, pregunta P2. Solo cuentan las ofertas con ciudad Madrid o Barcelona; las 100 % remotas no tienen ciudad.

- **Volumen.** Madrid tiene unas 2,5 veces más ofertas que Barcelona (659 frente a 267). Barcelona publica el salario algo más a menudo (34 % frente a 29 %).
- **Salario global.** Madrid queda ligeramente por encima (mediana de 37.500 € frente a 36.000 €), pero la diferencia **no es estadísticamente significativa** (prueba de Mann-Whitney, p = 0,11).
- **Efecto composición.** Los puestos de helpdesk y soporte, los peor pagados, pesan el triple en Barcelona (24 % de las ofertas con salario, frente al 8 % en Madrid). Al quitarlos, Barcelona pasa por delante en mediana (42.000 € frente a 39.000 €). Comparando dentro de la misma categoría de puesto, Barcelona anuncia salarios iguales o más altos en 4 de las 6 categorías comparables (jefe de proyecto, consultor, ingeniero y analista programador).
- **Conclusión.** Madrid ofrece mucho más empleo tecnológico, pero no paga más por el mismo tipo de puesto: la diferencia global se explica por la mezcla de puestos de cada ciudad. Las comparaciones por categoría se basan en grupos pequeños (5–24 salarios por ciudad), así que son orientativas.
### 5.3 Modalidad de trabajo *(Vahab)*
### 5.4 Comparación entre fuentes y salarios estimados *(Vahab)*
### 5.5 Conclusiones y limitaciones *(ambos)*

## 6. Proceso de trabajo *(ambos)*

- Distribución del trabajo entre los integrantes.
- Herramientas empleadas.
- Dificultades encontradas.

### Dificultades de la parte de scraping *(Alex)*

- **El script no podía leer el `robots.txt`.** En la primera ejecución se saltó todas las páginas con el aviso "robots.txt no permite…", aunque el `robots.txt` no prohíbe los listados. La causa: la función de Python que lo lee se identifica como "Python-urllib" y, si la web le responde con un error, da por prohibido todo el sitio. Lo resolvimos descargando el `robots.txt` con el mismo User-Agent del proyecto y haciendo que el script se detenga con un mensaje claro si no lo puede leer.
- **El final del listado.** Al pedir una página que ya no existe (la 36 en Madrid, la 23 en Barcelona) el portal responde con un error 404. El script lo trata como el final del listado.
- **Ofertas repetidas entre ciudades.** Al filtrar por provincia, las ofertas 100 % remotas aparecen en los dos listados, y algunas ofertas de otras provincias aparecen en el de Madrid. Esto nos obligó a quitar duplicados y a crear el grupo de ciudad.
- **Salarios en distintas unidades y con errores.** Ver el apartado 3.2.
- Cambios de criterio y cómo afectaron al proyecto (a partir de `docs/decisiones.md`).
