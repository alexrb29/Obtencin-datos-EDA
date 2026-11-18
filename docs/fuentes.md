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
| Límites de uso | _anotar los del panel de desarrollador_ |
| Condiciones de uso | _resumir los términos de servicio; captura en `docs/capturas/`_ |
| Script | `src/adzuna.py` |

**Campos recogidos por oferta:** `id`, `title`, `description` (recortada), `created`, `company.display_name`, `location.display_name`, `location.area`, `salary_min`, `salary_max`, `salary_is_predicted`, `contract_type`, `contract_time`, `category`, `redirect_url`, `latitude`, `longitude`.
_Revisar y completar con la salida de `python src/adzuna.py --prueba`._

**Qué aporta:** volumen de ofertas y salarios por tecnología y ciudad, e histograma de salarios.
**Limitación conocida:** cuando la oferta no indica salario, Adzuna lo estima (`salary_is_predicted = 1`).

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
