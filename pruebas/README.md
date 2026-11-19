# Pruebas de fuentes (18/11/2026)

Scripts que usamos para evaluar las fuentes **antes** de escribir el código definitivo (`src/`).
Los resultados y las decisiones están en `docs/fuentes.md` y `docs/decisiones.md`; las capturas, en `docs/capturas/`.

| Script | Qué comprueba | Resultado |
|---|---|---|
| `test_fuente.py` | Para cualquier URL: status HTTP, si el HTML es estático o necesita JavaScript, número de «€», bloques JSON-LD y si hay `baseSalary` | Tecnoempleo: HTML estático y JSON-LD `JobPosting` en cada oferta → fuente elegida |
| `test_ticjob.py` | Listado de Barcelona de ticjob.es y JSON-LD de 3 ofertas | Funciona, pero la fuente se descartó (pocas ofertas, casi sin salario, condiciones restrictivas) |

La prueba de la API de Adzuna se hace con el script definitivo: `python src/adzuna.py --prueba`.

## Uso

Desde la raíz del repositorio, con el entorno virtual activado:

```powershell
python pruebas/test_fuente.py "https://www.tecnoempleo.com/ofertas-trabajo/" --texto "TÍTULO DE UNA OFERTA VISIBLE"
python pruebas/test_fuente.py "URL_OFERTA_1" "URL_OFERTA_2" "URL_OFERTA_3"
python pruebas/test_ticjob.py
```

Antes de ejecutarlos, cambiad `tu-email@ejemplo.com` en `HEADERS` por un email de contacto.
