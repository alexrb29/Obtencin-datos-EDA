"""
Test inicial de scraping en ticjob.es

1. Descarga una página de listado (HTML estático, no hace falta Selenium/Playwright)
2. Extrae los enlaces a las ofertas
3. Lee el JSON-LD (schema.org JobPosting) de las 3 primeras ofertas

Requisitos: Python 3.10+, `pip install requests beautifulsoup4`
Ejecutar:   python test_ticjob.py
"""

import json
import time
from html import unescape

import requests
from bs4 import BeautifulSoup

LISTADO = "https://ticjob.es/esp/ofertas-trabajo-it/barcelona"
HEADERS = {
    # Identificaos como proyecto académico (cambiad el email)
    "User-Agent": "Mozilla/5.0 (proyecto academico EDA; contacto: tu-email@ejemplo.com)"
}
PAUSA_SEG = 2  # pausa entre peticiones para no cargar el servidor


def get_html(url: str) -> str:
    """Descarga una página y devuelve su HTML como texto."""
    respuesta = requests.get(url, headers=HEADERS, timeout=15)
    respuesta.raise_for_status()  # lanza error si el status no es 2xx
    return respuesta.text


def enlaces_ofertas(html: str) -> list[str]:
    """Devuelve las URLs únicas de ofertas (/esp/trabajo/...) de una página de listado."""
    soup = BeautifulSoup(html, "html.parser")
    urls = {
        a["href"].strip()
        for a in soup.find_all("a", href=True)
        if "/esp/trabajo/" in a["href"]
    }
    return sorted(urls)


def leer_jobposting(html: str) -> dict | None:
    """Busca el bloque JSON-LD de tipo JobPosting dentro del HTML de una oferta."""
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup.find_all("script", type="application/ld+json"):
        # strict=False: ticjob deja saltos de línea dentro de los strings del JSON,
        # y con el modo estricto json.loads daría error.
        try:
            data = json.loads(tag.get_text(), strict=False)
        except json.JSONDecodeError:
            continue
        if isinstance(data, dict) and data.get("@type") == "JobPosting":
            return data
    return None


if __name__ == "__main__":
    html_listado = get_html(LISTADO)
    urls = enlaces_ofertas(html_listado)
    print(f"Ofertas encontradas en el listado: {len(urls)}")

    for url in urls[:3]:
        time.sleep(PAUSA_SEG)
        oferta = leer_jobposting(get_html(url))
        if oferta is None:
            print("Sin JSON-LD (¿oferta caducada?):", url)
            continue

        direccion = oferta.get("jobLocation", {}).get("address", {})
        print("-" * 60)
        print("Título :", unescape(oferta.get("title", "")))
        print("Empresa:", oferta.get("hiringOrganization", {}).get("name"))
        print("Ciudad :", direccion.get("addressLocality"), "/", direccion.get("addressRegion"))
        print("Fecha  :", oferta.get("datePosted"), "| Jornada:", oferta.get("employmentType"))
        print("URL    :", url)
