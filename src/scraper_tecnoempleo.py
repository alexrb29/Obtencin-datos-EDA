"""Web scraping de ofertas de Tecnoempleo (https://www.tecnoempleo.com/).

ESTADO: esqueleto. Vahab completa los selectores CSS (marcados con TODO) después de
inspeccionar el HTML de los listados con las herramientas de desarrollador del navegador.

Buenas prácticas que ya aplica el script:
- Comprueba robots.txt antes de cada URL y no descarga lo que esté prohibido.
- Se identifica con un User-Agent propio y espera PAUSA_SEGUNDOS entre peticiones.
- Guarda el HTML original de cada página (datos originales) además del CSV extraído.

Uso (desde la raíz del repositorio):
    python src/scraper_tecnoempleo.py --max-paginas 5
"""
from __future__ import annotations

import argparse
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

sesion = requests.Session()
sesion.headers.update({"User-Agent": USER_AGENT, "Accept-Language": "es-ES,es;q=0.9"})

robots = robotparser.RobotFileParser(BASE + "/robots.txt")
robots.read()


def descargar_html(url: str) -> str | None:
    if not robots.can_fetch(USER_AGENT, url):
        print(f"  robots.txt no permite {url}; se omite.")
        return None
    r = sesion.get(url, timeout=30)
    time.sleep(PAUSA_SEGUNDOS)
    if r.status_code != 200:
        print(f"  ! Error {r.status_code} en {url}")
        return None
    return r.text


def texto(nodo, selector: str) -> str | None:
    """Devuelve el texto limpio del primer elemento que cumple el selector, o None."""
    el = nodo.select_one(selector)
    return el.get_text(" ", strip=True) if el else None


def extraer_ofertas(html: str, ciudad_busqueda: str) -> list[dict]:
    """Convierte una página de listado en una lista de ofertas.

    TODO (Vahab): ajustad los selectores al HTML real. Para encontrarlos:
    clic derecho en una oferta > Inspeccionar > buscad el contenedor que se repite.
    """
    soup = BeautifulSoup(html, "lxml")
    ofertas = []
    for tarjeta in soup.select("TODO-selector-contenedor-oferta"):
        enlace = tarjeta.select_one("a[href]")
        ofertas.append({
            "titulo": texto(tarjeta, "TODO-selector-titulo"),
            "empresa": texto(tarjeta, "TODO-selector-empresa"),
            "ubicacion": texto(tarjeta, "TODO-selector-ubicacion"),
            "modalidad": texto(tarjeta, "TODO-selector-modalidad"),     # remoto / híbrido / presencial
            "salario_texto": texto(tarjeta, "TODO-selector-salario"),   # se convierte a número en la limpieza
            "tecnologias": texto(tarjeta, "TODO-selector-tecnologias"),
            "fecha_texto": texto(tarjeta, "TODO-selector-fecha"),
            "url": BASE + enlace["href"] if enlace and enlace["href"].startswith("/") else (enlace["href"] if enlace else None),
            "ciudad_busqueda": ciudad_busqueda,
        })
    return ofertas


def main(max_paginas: int) -> None:
    fecha = datetime.now().strftime("%Y-%m-%d")
    carpeta = RAW_TECNOEMPLEO / fecha
    (carpeta / "html").mkdir(parents=True, exist_ok=True)
    todas = []
    for ciudad, plantilla in URLS_LISTADO.items():
        for pagina in range(1, max_paginas + 1):
            url = plantilla.format(pagina=pagina)
            html = descargar_html(url)
            if not html:
                break
            (carpeta / "html" / f"{ciudad.lower()}_p{pagina}.html").write_text(html, encoding="utf-8")
            ofertas = extraer_ofertas(html, ciudad)
            print(f"{ciudad} · pág. {pagina}: {len(ofertas)} ofertas")
            if not ofertas:
                break
            for o in ofertas:
                o["fecha_obtencion"] = fecha
            todas.extend(ofertas)
    df = pd.DataFrame(todas)
    salida = carpeta / "ofertas_tecnoempleo.csv"
    df.to_csv(salida, index=False, encoding="utf-8")
    print(f"\nHecho. {len(df)} ofertas guardadas en {salida}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scraping de ofertas de Tecnoempleo")
    parser.add_argument("--max-paginas", type=int, default=5)
    main(parser.parse_args().max_paginas)
