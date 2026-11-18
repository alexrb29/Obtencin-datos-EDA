"""Descarga de ofertas de empleo de la API de Adzuna (España).

Documentación de la API: https://developer.adzuna.com/docs/search

Uso (desde la raíz del repositorio):
    python src/adzuna.py --prueba                      # 2 llamadas de prueba
    python src/adzuna.py --descargar --max-paginas 3   # tecnologías × ciudades
    python src/adzuna.py --histogramas                 # histograma de salarios

Qué guarda:
    data/raw/adzuna/<fecha>/search/<tecnologia>__<ciudad>__p<n>.json
    data/raw/adzuna/<fecha>/histogram/<tecnologia>__<ciudad>.json
    data/raw/adzuna/<fecha>/registro_llamadas.csv   (URL sin claves, fecha, estado)

Los JSON se guardan tal cual los devuelve la API: son los datos originales.
La conversión a tabla se hace en el cuaderno de limpieza.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv

sys.path.append(str(Path(__file__).resolve().parent))
from config import CIUDADES, RAIZ, RAW_ADZUNA, TECNOLOGIAS  # noqa: E402

URL_BASE = "https://api.adzuna.com/v1/api/jobs/es"
RESULTADOS_POR_PAGINA = 50  # máximo que permite la API
PAUSA_SEGUNDOS = 3  # margen para no superar el límite de llamadas por minuto
CATEGORIA = "it-jobs"  # se comprueba con --prueba (lista de categorías de España)
LIMITE_LLAMADAS = 240  # tope de seguridad por ejecución; ajustadlo al límite diario de vuestro panel


def cargar_claves() -> dict:
    load_dotenv(RAIZ / ".env")
    app_id = os.getenv("ADZUNA_APP_ID")
    app_key = os.getenv("ADZUNA_APP_KEY")
    if not app_id or not app_key or app_id == "tu_app_id":
        sys.exit("Faltan las claves. Copiad .env.example como .env y rellenad ADZUNA_APP_ID y ADZUNA_APP_KEY.")
    return {"app_id": app_id, "app_key": app_key}


def nombre_archivo(texto: str) -> str:
    """Convierte 'Node.js' en 'node_js' para usarlo en nombres de archivo."""
    return re.sub(r"[^a-z0-9]+", "_", texto.lower()).strip("_")


class ClienteAdzuna:
    """Hace las llamadas, cuenta cuántas lleva y registra cada una."""

    def __init__(self, carpeta: Path, limite: int = LIMITE_LLAMADAS):
        self.claves = cargar_claves()
        self.carpeta = carpeta
        self.limite = limite
        self.llamadas = 0
        self.carpeta.mkdir(parents=True, exist_ok=True)
        self.registro = self.carpeta / "registro_llamadas.csv"
        if not self.registro.exists():
            with open(self.registro, "w", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow(["fecha_hora", "endpoint", "parametros", "estado", "archivo"])

    def get(self, endpoint: str, params: dict, archivo: Path | None = None) -> dict | None:
        if self.llamadas >= self.limite:
            raise RuntimeError(f"Alcanzado el tope de {self.limite} llamadas en esta ejecución.")
        url = f"{URL_BASE}/{endpoint}"
        r = requests.get(url, params={**self.claves, **params, "content-type": "application/json"}, timeout=30)
        self.llamadas += 1
        # Registramos los parámetros SIN las claves
        with open(self.registro, "a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow([
                datetime.now().isoformat(timespec="seconds"), endpoint,
                json.dumps(params, ensure_ascii=False), r.status_code, archivo.name if archivo else "",
            ])
        time.sleep(PAUSA_SEGUNDOS)
        if r.status_code == 429:
            raise RuntimeError("La API responde 429: límite de llamadas superado. Esperad y volved a ejecutar.")
        if r.status_code != 200:
            print(f"  ! Error {r.status_code} en {endpoint} {params}: {r.text[:200]}")
            return None
        datos = r.json()
        if archivo:
            archivo.parent.mkdir(parents=True, exist_ok=True)
            archivo.write_text(json.dumps(datos, ensure_ascii=False, indent=2), encoding="utf-8")
        return datos


def prueba() -> None:
    """Dos llamadas: una búsqueda para ver los campos y la lista de categorías."""
    cliente = ClienteAdzuna(RAW_ADZUNA / "prueba", limite=2)
    datos = cliente.get("search/1", {"what": "python", "where": "madrid", "results_per_page": 5})
    if not datos:
        return
    print(f"Ofertas totales encontradas: {datos.get('count')}")
    print(f"Salario medio según Adzuna: {datos.get('mean')}")
    for oferta in datos.get("results", []):
        print("-" * 60)
        print("Título:     ", oferta.get("title"))
        print("Empresa:    ", oferta.get("company", {}).get("display_name"))
        print("Ubicación:  ", oferta.get("location", {}).get("display_name"))
        print("Salario:    ", oferta.get("salary_min"), "-", oferta.get("salary_max"),
              "(estimado)" if str(oferta.get("salary_is_predicted")) == "1" else "(declarado)")
        print("Contrato:   ", oferta.get("contract_type"), oferta.get("contract_time"))
        print("Fecha:      ", oferta.get("created"))
    print("-" * 60)
    print("Campos disponibles en cada oferta:", sorted(datos["results"][0].keys()) if datos.get("results") else "—")

    categorias = cliente.get("categories", {})
    if categorias:
        tags = [c.get("tag") for c in categorias.get("results", [])]
        print(f"\nCategorías disponibles en España: {tags}")
        if CATEGORIA not in tags:
            print(f"OJO: la categoría '{CATEGORIA}' no existe. Cambiad CATEGORIA en src/adzuna.py.")


def descargar(max_paginas: int) -> None:
    """Descarga hasta max_paginas × 50 ofertas por cada tecnología y ciudad."""
    carpeta = RAW_ADZUNA / datetime.now().strftime("%Y-%m-%d")
    cliente = ClienteAdzuna(carpeta)
    total = len(TECNOLOGIAS) * len(CIUDADES)
    n = 0
    for tec, what in TECNOLOGIAS.items():
        for ciudad, where in CIUDADES.items():
            n += 1
            for pagina in range(1, max_paginas + 1):
                archivo = carpeta / "search" / f"{nombre_archivo(tec)}__{nombre_archivo(ciudad)}__p{pagina}.json"
                if archivo.exists():  # permite reanudar si se corta
                    continue
                params = {"what": what, "where": where, "results_per_page": RESULTADOS_POR_PAGINA,
                          "category": CATEGORIA}
                datos = cliente.get(f"search/{pagina}", params, archivo)
                recibidos = len(datos.get("results", [])) if datos else 0
                print(f"[{n}/{total}] {tec} · {ciudad} · pág. {pagina}: {recibidos} ofertas "
                      f"(llamadas: {cliente.llamadas})")
                if recibidos < RESULTADOS_POR_PAGINA:
                    break  # no hay más páginas
    print(f"\nHecho. {cliente.llamadas} llamadas. Datos en {carpeta}")


def histogramas() -> None:
    """Distribución de salarios por tecnología y ciudad (endpoint /histogram)."""
    carpeta = RAW_ADZUNA / datetime.now().strftime("%Y-%m-%d")
    cliente = ClienteAdzuna(carpeta)
    for tec, what in TECNOLOGIAS.items():
        for ciudad, where in CIUDADES.items():
            archivo = carpeta / "histogram" / f"{nombre_archivo(tec)}__{nombre_archivo(ciudad)}.json"
            if archivo.exists():
                continue
            cliente.get("histogram", {"what": what, "where": where}, archivo)
            print(f"Histograma {tec} · {ciudad} (llamadas: {cliente.llamadas})")
    print(f"\nHecho. {cliente.llamadas} llamadas. Datos en {carpeta}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Descarga de ofertas de Adzuna (España)")
    grupo = parser.add_mutually_exclusive_group(required=True)
    grupo.add_argument("--prueba", action="store_true", help="hace 1 llamada y muestra los campos")
    grupo.add_argument("--descargar", action="store_true", help="descarga tecnologías × ciudades")
    grupo.add_argument("--histogramas", action="store_true", help="descarga los histogramas de salario")
    parser.add_argument("--max-paginas", type=int, default=3, help="páginas de 50 ofertas por consulta")
    args = parser.parse_args()

    if args.prueba:
        prueba()
    elif args.descargar:
        descargar(args.max_paginas)
    else:
        histogramas()
