# Diccionario de datos

Responsable: Vahab. Se completa cuando exista `data/processed/ofertas.csv`.

**Unidad de observación:** _una fila = una oferta (o una oferta × tecnología en los datos de Adzuna; explicar)._
**Observaciones:** _pendiente_ · **Variables:** _pendiente_

| Variable | Descripción | Tipo | Unidades / valores | Fuente | % nulos |
|---|---|---|---|---|---|
| `fuente` | Origen de la oferta | Categórica nominal | adzuna, tecnoempleo | ambas | |
| `id_oferta` | Identificador de la oferta en su fuente | Identificador | — | ambas | |
| `titulo` | Título de la oferta | Texto | — | ambas | |
| `empresa` | Empresa que publica | Categórica nominal | — | ambas | |
| `ciudad` | Ciudad normalizada | Categórica nominal | Madrid, Barcelona | ambas | |
| `tecnologia` | Tecnología normalizada | Categórica nominal | ver `data/reference/tecnologias.csv` | ambas | |
| `modalidad` | Modalidad de trabajo | Categórica nominal | presencial, híbrido, remoto | tecnoempleo | |
| `salario_min` | Salario mínimo anunciado | Numérica continua | € brutos/año | ambas | |
| `salario_max` | Salario máximo anunciado | Numérica continua | € brutos/año | ambas | |
| `salario_medio` | Punto medio del rango | Numérica continua | € brutos/año | ambas | |
| `salario_estimado` | El salario lo estimó Adzuna | Categórica (booleana) | True / False | adzuna | |
| `tipo_contrato` | Tipo de contrato | Categórica nominal | permanent, contract… | adzuna | |
| `fecha_publicacion` | Fecha de publicación | Temporal | AAAA-MM-DD | ambas | |
| `fecha_obtencion` | Fecha de descarga | Temporal | AAAA-MM-DD | ambas | |
