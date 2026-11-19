# Registro de fuentes

Punto 2 del enunciado: direcciones consultadas, fecha de obtención, campos recogidos, procedimiento y revisión de `robots.txt` y de las condiciones de uso.

## 1. API de Adzuna

| Campo | Valor |
|---|---|
| Responsable | Vahab |
| Documentación | https://developer.adzuna.com/docs/search |
| Endpoints | `GET /v1/api/jobs/es/search/{pagina}`, `GET /v1/api/jobs/es/histogram`, `GET /v1/api/jobs/es/categories` |
| Parámetros | `what` (tecnología), `where` (ciudad), `category=it-jobs`, `results_per_page=50` |
| Fecha de obtención | _pendiente_ |
| Llamadas realizadas | _pendiente_ (ver `data/raw/adzuna/<fecha>/registro_llamadas.csv`) |
| Límites de uso | _anotar los del panel de desarrollador_ (los términos no publican cifras; se ven en el panel) |
| Condiciones de uso | Revisadas el 2026-11-18 ([terms of service](https://developer.adzuna.com/docs/terms_of_service)). Uso permitido: búsqueda personal de empleo e investigación personal o académica; el análisis comercial, la reventa de datos y la prospección comercial requieren acuerdo escrito. Hay que citar «The Adzuna API» como fuente, con enlace a https://www.adzuna.es. Registro hecho con el uso «Personal or academic research». |
| Script | `src/adzuna.py` |

**Campos recogidos por oferta:** `id`, `title`, `description` (recortada), `created`, `company.display_name`, `location.display_name`, `location.area`, `salary_min`, `salary_max`, `salary_is_predicted`, `contract_type`, `contract_time`, `category`, `redirect_url`, `latitude`, `longitude`.
_Revisar y completar con la salida de `python src/adzuna.py --prueba`._

**Qué aporta:** volumen de ofertas y salarios por tecnología y ciudad, e histograma de salarios.
**Limitación conocida:** cuando la oferta no indica salario, Adzuna lo estima (`salary_is_predicted = 1`).

**Prueba inicial (2026-11-18, 1 llamada: `what=python`, `where=barcelona`, `results_per_page=20`, sin `category`):**

- `count` = 765 ofertas.
- Solo 2 de 20 ofertas traen salario, y ninguna estimada (`salary_is_predicted = 0`). En esta muestra Adzuna **no** estima salarios en España: hay que comprobarlo con la descarga completa.
- `contract_type` y `contract_time` vacíos en las 5 ofertas revisadas: `tipo_contrato` tendrá probablemente muchos nulos.
- Primer atípico: «Python Developer» de Novartis con salario 420–780, que no puede ser anual (¿diario?). Ejemplo para la limpieza.
- Captura: `docs/capturas/2026-11-18_prueba_adzuna.png`.

## 2. Web scraping de Tecnoempleo

| Campo | Valor |
|---|---|
| Responsable | Alex |
| URL base | https://www.tecnoempleo.com/ |
| URLs de listado | General: `https://www.tecnoempleo.com/ofertas-trabajo/?pagina=N` (paginación comprobada el 2026-11-18). Filtradas por provincia (parámetro `pr`): Madrid `https://www.tecnoempleo.com/ofertas-trabajo/?pr=,263,&pagina=N` (35 páginas) y Barcelona `https://www.tecnoempleo.com/ofertas-trabajo/?pr=,240,&pagina=N` (22 páginas). |
| Fecha de obtención | 2026-11-19 (1.652 filas, 1.297 ofertas distintas; HTML original en `data/raw/tecnoempleo/2026-11-19/html/`) |
| robots.txt | Revisado el 2026-11-18. Para `User-agent: *` prohíbe rutas como `/graficos_estadisticas/`, `/profesionales/`, `/accesoempresa.php`, `/_ajax/select_ajax.php` o `/demanda-trabajo-informatica.php?`, pero no los listados (`/ofertas-trabajo/`, incluida la paginación `?pagina=N`) ni las páginas de oferta. Bloquea por completo a los bots de IA (AnthropicBot, ClaudeBot, GPTBot…), así que las pruebas y el scraping los ejecutamos nosotros con nuestro script. Captura en `docs/capturas/2026-11-18_robots_tecnoempleo.png`. |
| Aviso legal / condiciones | «Marco Normativo» (https://www.tecnoempleo.com/politicaymarco.php), revisado el 2026-11-18. Regula el uso por candidatos y empresas registrados y **no menciona** scraping, robots ni extracción automática. Solo reserva los derechos de forma genérica (copyright y derechos de explotación, apartados 1 y 12). Titular: CYBEREMPLEO, S.L. Base legal de nuestra extracción: arts. 134.1 y 135.1.b de la Ley de Propiedad Intelectual (extracción con fines de ilustración de la enseñanza, no comercial y citando la fuente). Captura en `docs/capturas/2026-11-18_tecnoempleo_marco_normativo.png`. |
| Pausa entre peticiones | 5 s |
| Script | `src/scraper_tecnoempleo.py` |

**Campos recogidos (por oferta, desde el listado):** `id_oferta`, `titulo`, `empresa`, `ubicacion`, `modalidad` (Presencial, Híbrido, 100% remoto), `categoria` (área del puesto), `salario_texto` (p. ej. "18.000€ - 21.000€ b/a"), `tipo_contrato`, `tecnologias` (etiquetas separadas por ";"), `fecha_texto`, `estado` (Nueva/Actualizada), `urgente`, `descripcion_resumen`, `url`, `ciudad_busqueda`, `pagina`, `fecha_obtencion`.

**Observaciones de una página de prueba (Madrid, 19/11/2026, 30 ofertas):** 13 con salario (43 %); 20 eran "100% remoto" y no indican ciudad, así que pueden aparecer también en el listado de Barcelona (deduplicar por `id_oferta`).

**Qué aporta:** modalidad de trabajo (remoto, híbrido o presencial) y salario declarado por la empresa.

### Pruebas (2026-11-18)

Scripts en `pruebas/`.

- **Listado general:** 1.767 ofertas de informática y telecomunicaciones. Por provincia: Madrid 887, Barcelona 324, Valencia 115, Bizkaia 80, Zaragoza 48, Sevilla 42, Málaga 30. Por modalidad: híbrido 1.236, presencial 821, sin especificar 618, 100 % remoto 306. La suma por modalidad (2.981) supera el total, así que una oferta puede contarse más de una vez (quizá por tener varias ubicaciones): revisarlo en la limpieza.
- **`test_fuente.py` sobre el listado:** status 200; HTML estático (el título de una oferta aparece en el HTML sin ejecutar JavaScript); 49 símbolos «€» (parte pueden ser filtros de salario de la barra lateral); sin JSON-LD.
- **`test_fuente.py` sobre 3 ofertas:** las 3 traen JSON-LD `JobPosting` con `title`, `datePosted`, `description`, `employmentType`, `hiringOrganization`, `jobLocation`, `identifier` y `directApply`. 1 de 3 trae `baseSalary` (EUR, 54.000–60.000, `unitText: YEAR`). Algunas añaden `jobLocationType` y `applicantLocationRequirements` (ofertas en remoto).
- **Implicación:** salario, fecha, empresa y ubicación se pueden leer del JSON-LD de cada oferta, con moneda y unidad explícitas, en lugar de depender solo de selectores CSS del listado. Pendiente de decidir cómo combinarlo con el listado.
- Capturas: `docs/capturas/2026-11-18_tecnoempleo_listado.png`, `2026-11-18_prueba_tecnoempleo_listado.png` y `2026-11-18_prueba_tecnoempleo_ofertas.png`.

## 3. Fuentes descartadas

### ticjob.es (scraping)

- robots.txt (2026-11-18): solo prohíbe `/legal`, `/disclaimer`, `/privacy` y `/online-cv`; listados y ofertas permitidos.
- La prueba (`pruebas/test_ticjob.py`) funcionó: HTML estático y JSON-LD `JobPosting` en cada oferta.
- Se descarta porque: tiene unas 103 ofertas activas en toda España (7 de Python, 15 en Barcelona); de 40 ofertas revisadas solo 1 publicaba salario numérico; la ubicación del JSON-LD es la comunidad («Catalonia»), no la ciudad; y sus Condiciones de uso (§2) prohíben copiar o descargar la web «por completo o en parte».
- Capturas: `docs/capturas/2026-11-18_robots_ticjob.png` y `2026-11-18_prueba_ticjob.png`.

### InfoJobs (scraping)

- robots.txt (2026-11-18): para `User-agent: *` prohíbe las URL antiguas de listados y ofertas (`/ofertas_lista.cfm`, `/ver-oferta.xhtml`, `/visualizar_oferta…`, `/buscar.empleo/`), además de `/react` y `/webapp`; bloquea por completo al agregador `jobrapido`.
- Se descarta sin probarla: web en JavaScript, postura contraria a los agregadores y no aporta nada que no den Tecnoempleo + Adzuna.
