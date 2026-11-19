"""
Test rápido de una fuente para scraping (tecnoempleo, infojobs, ...)

Para cada URL comprueba:
  - status HTTP (403/429 = bloqueo anti-bot)
  - si un texto que ves en el navegador aparece en el HTML "crudo"
    -> SÍ: HTML estático, basta con requests + BeautifulSoup
    -> NO: el contenido se carga con JavaScript (Playwright/Selenium o API interna)
  - cuántos "€" hay (pista de si se publican salarios)
  - bloques JSON-LD (schema.org) y, si hay JobPosting, sus campos y si trae baseSalary

Requisitos: `pip install requests beautifulsoup4`
Uso:
  python test_fuente.py URL_LISTADO --texto "título de una oferta que ves en la página"
  python test_fuente.py URL_OFERTA_1 URL_OFERTA_2 URL_OFERTA_3
"""

import argparse
import json
import time

import requests
from bs4 import BeautifulSoup

HEADERS = {
    # Cambiad el email: identificaos como proyecto académico
    "User-Agent": "Mozilla/5.0 (proyecto academico EDA; contacto: tu-email@ejemplo.com)",
    "Accept-Language": "es-ES,es;q=0.9",
}
PAUSA_SEG = 2


def jsonld_bloques(soup: BeautifulSoup) -> list[dict]:
    bloques = []
    for tag in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(tag.get_text(), strict=False)
        except json.JSONDecodeError:
            continue
        # puede venir como objeto, lista o {"@graph": [...]}
        if isinstance(data, dict) and "@graph" in data:
            data = data["@graph"]
        bloques.extend(data if isinstance(data, list) else [data])
    return [b for b in bloques if isinstance(b, dict)]


def analizar(url: str, texto: str | None) -> None:
    print("=" * 70)
    print("URL:", url)
    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
    except requests.RequestException as e:
        print("ERROR de conexión:", e)
        return

    print("Status:", r.status_code, "| URL final:", r.url, "| tamaño HTML:", len(r.text))
    if r.status_code in (403, 429):
        print(">> Posible bloqueo anti-bot. No insistáis: anotadlo y descartad la fuente.")
        return

    html = r.text
    if texto:
        print(f'Texto "{texto}" en HTML crudo:', "SÍ (estático)" if texto in html else "NO (probablemente JS)")
    print("Número de '€' en el HTML:", html.count("€") + html.count("&euro;") + html.count("&#8364;"))

    soup = BeautifulSoup(html, "html.parser")
    enlaces = {a["href"] for a in soup.find_all("a", href=True)}
    print("Enlaces totales en la página:", len(enlaces))

    bloques = jsonld_bloques(soup)
    tipos = [b.get("@type") for b in bloques]
    print("JSON-LD encontrados:", tipos or "ninguno")
    for b in bloques:
        if b.get("@type") == "JobPosting":
            print("  Campos JobPosting:", sorted(b.keys()))
            print("  baseSalary:", b.get("baseSalary", "NO VIENE"))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("urls", nargs="+")
    parser.add_argument("--texto", help="texto visible en la página para comprobar si el HTML es estático")
    args = parser.parse_args()

    for i, url in enumerate(args.urls):
        if i:
            time.sleep(PAUSA_SEG)
        analizar(url, args.texto)


if __name__ == "__main__":
    main()
