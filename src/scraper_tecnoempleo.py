"""Web scraping de ofertas de Tecnoempleo (https://www.tecnoempleo.com/).

Recorre los listados de ofertas de Madrid y Barcelona página a página y guarda:
    data/raw/tecnoempleo/<fecha>/html/<ciudad>_p<n>.html   (páginas originales)
    data/raw/tecnoempleo/<fecha>/ofertas_tecnoempleo.csv   (una fila por oferta y ciudad buscada)

Buenas prácticas que aplica:
- Comprueba robots.txt antes de cada URL y no descarga lo que esté prohibido.
- Se identifica con un User-Agent propio y espera PAUSA_SEGUNDOS entre peticiones.
- Guarda el HTML original de cada página, además del CSV extraído.
- Se detiene cuando una página no trae ofertas nuevas (fin del listado).

Uso (desde la raíz del repositorio):
    python src/scraper_tecnoempleo.py --max-paginas 2    # prueba corta
    python src/scraper_tecnoempleo.py --max-paginas 40   # descarga completa
    python src/scraper_tecnoempleo.py --desde-html RUTA.html   # prueba el extractor sin conectarse
"""
from __future__ import annotations

import argparse
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from urllib import robotparser

import pandas as pd
import requests
from bs4 import BeautifulSoup

sys.path.append(str(Path(__file__).resolve().parent))
from config import RAW_TECNOEMPLEO  # noqa: E402

BASE = "https://www.tecnoempleo.com"
USER_AGENT = "ProyectoEDA-Universidad/1.0 (proyecto academico; contacto: TODO-email)"
PAUSA_SEGUNDOS = 5

# Listados de ofertas filtrados por provincia (parámetro pr): 263 = Madrid, 240 = Barcelona.
# El número de página va en el parámetro pagina.
URLS_LISTADO = {
    "Madrid": BASE + "/ofertas-trabajo/?pr=,263,&pagina={pagina}",
    "Barcelona": BASE + "/ofertas-trabajo/?pr=,240,&pagina={pagina}",
}

RE_FECHA = re.compile(r"\d{2}/\d{2}/\d{4}")
ETIQUETAS_ESTADO = {"Nueva", "Actualizada", "Urgente"}

sesion = requests.Session()
sesion.headers.update({"User-Agent": USER_AGENT, "Accept-Language": "es-ES,es;q=0.9"})
_robots = None


def permitido(url: str) -> bool:
    """Consulta robots.txt (se descarga una sola vez)."""
    global _robots
    if _robots is None:
        _robots = robotparser.RobotFileParser(BASE + "/robots.txt")
        _robots.read()
    return _robots.can_fetch(USER_AGENT, url)


def descargar_html(url: str) -> str | None:
    if not permitido(url):
        print(f"  robots.txt no permite {url}; se omite.")
        return None
    r = sesion.get(url, timeout=30)
    time.sleep(PAUSA_SEGUNDOS)
    if r.status_code != 200:
        print(f"  ! Error {r.status_code} en {url}")
        return None
    return r.text


def extraer_oferta(tarjeta) -> dict:
    """Extrae los datos de una tarjeta de oferta del listado.

    Estructura de cada tarjeta (div.p-3.border.rounded.mb-3.bg-white):
      - h3 > a              -> título y URL de la oferta (la URL termina en rf-<id>)
      - a.text-primary      -> empresa
      - span.hidden-md-down -> resumen de la descripción + span.badge.bg-gray-500 (tecnologías)
      - div.col-lg-3        -> columna derecha: fecha, estado, <b>ubicación</b>, (modalidad),
                               categoría, salario ("18.000€ - 21.000€ b/a") y tipo de contrato
    """
    enlace = tarjeta.select_one("h3 a[href]")
    url = enlace["href"]
    empresa = tarjeta.select_one("a.text-primary")
    resumen = tarjeta.select_one("span.hidden-md-down")
    tecnologias = [b.get_text(strip=True) for b in tarjeta.select("span.badge.bg-gray-500")]
    urgente = any(b.get_text(strip=True) == "Urgente" for b in tarjeta.select("h3 span.badge"))

    # Columna derecha: la recorremos línea a línea y clasificamos cada texto
    derecha = tarjeta.select_one("div.col-lg-3")
    ubicacion_b = derecha.find("b") if derecha else None
    ubicacion = ubicacion_b.get_text(strip=True) if ubicacion_b else None
    fecha = estado = modalidad = salario = contrato = categoria = None
    for linea in (derecha.stripped_strings if derecha else []):
        if RE_FECHA.fullmatch(linea):
            fecha = linea
        elif linea in ETIQUETAS_ESTADO:
            estado = linea
        elif linea == ubicacion:
            continue
        elif linea.startswith("(") and linea.endswith(")"):
            modalidad = linea.strip("()")
        elif "€" in linea:
            salario = linea
        elif linea.lower().startswith("contrato"):
            contrato = linea
        else:
            categoria = linea

    # "100% remoto" aparece en el lugar de la ubicación
    if ubicacion and "remoto" in ubicacion.lower():
        modalidad, ubicacion = ubicacion, None

    # El resumen de la descripción es el texto del bloque sin las tecnologías
    descripcion = None
    if resumen:
        for b in resumen.select("span.badge"):
            b.extract()
        descripcion = resumen.get_text(" ", strip=True)

    return {
        "id_oferta": url.rstrip("/").split("rf-")[-1] if "rf-" in url else None,
        "titulo": enlace.get_text(" ", strip=True),
        "empresa": empresa.get_text(" ", strip=True) if empresa else None,
        "ubicacion": ubicacion,
        "modalidad": modalidad,
        "categoria": categoria,
        "salario_texto": salario,
        "tipo_contrato": contrato,
        "tecnologias": ";".join(tecnologias),
        "fecha_texto": fecha,
        "estado": estado,
        "urgente": urgente,
        "descripcion_resumen": descripcion,
        "url": url,
    }


def extraer_ofertas(html: str, ciudad_busqueda: str) -> list[dict]:
    """Convierte una página de listado en una lista de ofertas."""
    soup = BeautifulSoup(html, "lxml")
    tarjetas = [t for t in soup.select("div.p-3.border.rounded.mb-3.bg-white") if t.select_one("h3 a[href*='/rf-']")]
    ofertas = []
    for tarjeta in tarjetas:
        oferta = extraer_oferta(tarjeta)
        oferta["ciudad_busqueda"] = ciudad_busqueda
        ofertas.append(oferta)
    return ofertas


def main(max_paginas: int) -> None:
    fecha = datetime.now().strftime("%Y-%m-%d")
    carpeta = RAW_TECNOEMPLEO / fecha
    (carpeta / "html").mkdir(parents=True, exist_ok=True)
    todas = []
    for ciudad, plantilla in URLS_LISTADO.items():
        vistas = set()
        for pagina in range(1, max_paginas + 1):
            url = plantilla.format(pagina=pagina)
            html = descargar_html(url)
            if not html:
                break
            (carpeta / "html" / f"{ciudad.lower()}_p{pagina}.html").write_text(html, encoding="utf-8")
            ofertas = extraer_ofertas(html, ciudad)
            nuevas = [o for o in ofertas if o["id_oferta"] not in vistas]
            print(f"{ciudad} · pág. {pagina}: {len(ofertas)} ofertas ({len(nuevas)} nuevas)")
            if not nuevas:  # página vacía o repetida: fin del listado
                break
            for o in nuevas:
                o["pagina"] = pagina
                o["fecha_obtencion"] = fecha
                vistas.add(o["id_oferta"])
            todas.extend(nuevas)
    df = pd.DataFrame(todas)
    salida = carpeta / "ofertas_tecnoempleo.csv"
    df.to_csv(salida, index=False, encoding="utf-8")
    print(f"\nHecho. {len(df)} filas guardadas en {salida}")
    if not df.empty:
        print(f"Ofertas distintas: {df['id_oferta'].nunique()} · con salario: {df['salario_texto'].notna().mean():.0%}")


def probar_html(ruta: str) -> None:
    """Prueba el extractor con un HTML guardado, sin conectarse a la web."""
    html = Path(ruta).read_text(encoding="utf-8", errors="ignore")
    df = pd.DataFrame(extraer_ofertas(html, "prueba"))
    pd.set_option("display.max_columns", None, "display.width", 200, "display.max_colwidth", 40)
    print(f"{len(df)} ofertas extraídas\n")
    print(df[["titulo", "empresa", "ubicacion", "modalidad", "categoria", "salario_texto", "tecnologias"]].head(10))
    print("\nValores nulos por columna:\n", df.isna().sum())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scraping de ofertas de Tecnoempleo")
    parser.add_argument("--max-paginas", type=int, default=5)
    parser.add_argument("--desde-html", help="ruta de un HTML guardado para probar el extractor")
    args = parser.parse_args()
    if args.desde_html:
        probar_html(args.desde_html)
    else:
        main(args.max_paginas)
