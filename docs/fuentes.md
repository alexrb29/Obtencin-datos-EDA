# Registro de fuentes

Punto 2 del enunciado: direcciones consultadas, fecha de obtención, campos recogidos, procedimiento y revisión de `robots.txt` y de las condiciones de uso.

## 1. API de Adzuna

| Campo | Valor |
|---|---|
| Responsable | Alex |
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
| Responsable | Vahab |
| URL base | https://www.tecnoempleo.com/ |
| URLs de listado | _pendiente_ |
| Fecha de obtención | _pendiente_ |
| robots.txt | Revisado el _fecha_. Para `User-agent: *` prohíbe rutas como `/graficos_estadisticas/`, `/profesionales/` o `/accesoempresa.php`, pero no los listados de ofertas. Captura en `docs/capturas/`. |
| Aviso legal / condiciones | _pendiente_ |
| Pausa entre peticiones | 5 s |
| Script | `src/scraper_tecnoempleo.py` |

**Campos recogidos:** `titulo`, `empresa`, `ubicacion`, `modalidad`, `salario_texto`, `tecnologias`, `fecha_texto`, `url`, `ciudad_busqueda`, `fecha_obtencion`.

**Qué aporta:** modalidad de trabajo (remoto, híbrido o presencial) y salario declarado por la empresa.
