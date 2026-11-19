"""Limpieza de los datos obtenidos por scraping de Tecnoempleo.

Entrada:  data/raw/tecnoempleo/<fecha>/ofertas_tecnoempleo.csv   (no se modifica)
Salidas:  data/processed/tecnoempleo_ofertas.csv       una fila por oferta
          data/processed/tecnoempleo_tecnologias.csv   una fila por oferta y tecnología normalizada

Uso (desde la raíz del repositorio):
    python src/limpieza_tecnoempleo.py

Cada decisión de limpieza está explicada junto al código y resumida en docs/decisiones.md.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent))
from config import PROCESSED, RAW_TECNOEMPLEO, REFERENCE  # noqa: E402

# --- Parámetros de limpieza (si cambian, anotadlo en docs/decisiones.md) ----
MESES_POR_ANO = 12          # salario mensual -> anual
HORAS_POR_ANO = 1760        # salario por hora -> anual (40 h/semana x 44 semanas)
UMBRAL_MENSUAL_SOSPECHOSO = 10_000  # un "mensual" por encima de esto es casi seguro anual
DIAS_RECIENTE = 90          # oferta "reciente" si se publicó en los últimos 90 días
CIUDADES_ESTUDIO = {"Madrid", "Barcelona"}

RE_SALARIO = re.compile(r"([\d\.]+)\s*€\s*-\s*([\d\.]+)\s*€\s*b/(\w)")
UNIDADES = {"a": "anual", "m": "mensual", "h": "hora"}
RE_PARCIAL = re.compile(r"parcial|fines? de semana|findes|media jornada|part[- ]time", re.IGNORECASE)


def cargar_raw(fecha: str | None = None) -> pd.DataFrame:
    """Carga el CSV original más reciente (o el de la fecha indicada)."""
    carpetas = sorted(p for p in RAW_TECNOEMPLEO.iterdir() if p.is_dir())
    carpeta = RAW_TECNOEMPLEO / fecha if fecha else carpetas[-1]
    return pd.read_csv(carpeta / "ofertas_tecnoempleo.csv")


# --- 1. Duplicados -------------------------------------------------------------
def quitar_duplicados(raw: pd.DataFrame) -> pd.DataFrame:
    """Una fila por oferta.

    Las ofertas 100 % remotas aparecen tanto en el listado de Madrid como en el de
    Barcelona. No son errores, pero contarlas dos veces inflaría los resultados.
    Guardamos en qué listados apareció cada una antes de quedarnos con una fila.
    """
    listados = raw.groupby("id_oferta")["ciudad_busqueda"].agg(lambda s: set(s))
    df = raw.drop_duplicates("id_oferta", keep="first").copy()
    df["en_listado_madrid"] = df["id_oferta"].map(lambda i: "Madrid" in listados[i])
    df["en_listado_barcelona"] = df["id_oferta"].map(lambda i: "Barcelona" in listados[i])
    return df.drop(columns=["ciudad_busqueda", "pagina"])


# --- 2. Ubicación y modalidad --------------------------------------------------
def normalizar_modalidad(m) -> str:
    if pd.isna(m):
        return "No indicada"
    m = str(m).lower()
    if "remoto" in m:
        return "Remoto"
    if "híbrido" in m or "hibrido" in m:
        return "Híbrido"
    if "presencial" in m:
        return "Presencial"
    return "No indicada"


def grupo_ciudad(fila) -> str:
    """Grupo para comparar ciudades.

    - Madrid / Barcelona: la oferta indica esa ciudad.
    - Otra ciudad: aparece en el listado pero la ubicación es otra (p. ej. Almería).
    - Sin ciudad (remoto): 100 % remota, no se puede asignar a ninguna ciudad.
    """
    if pd.isna(fila["ubicacion"]):
        return "Sin ciudad (remoto)" if fila["modalidad"] == "Remoto" else "No indicada"
    return fila["ubicacion"] if fila["ubicacion"] in CIUDADES_ESTUDIO else "Otra ciudad"


# --- 3. Salario ----------------------------------------------------------------
def parsear_salario(texto) -> pd.Series:
    """'30.000€ - 36.000€ b/a' -> mínimo, máximo y unidad en su escala original."""
    if pd.isna(texto):
        return pd.Series({"salario_min_original": np.nan, "salario_max_original": np.nan, "salario_unidad": None})
    m = RE_SALARIO.search(str(texto))
    if not m:
        return pd.Series({"salario_min_original": np.nan, "salario_max_original": np.nan, "salario_unidad": "no reconocida"})
    a, b, u = m.groups()
    return pd.Series({
        "salario_min_original": float(a.replace(".", "")),
        "salario_max_original": float(b.replace(".", "")),
        "salario_unidad": UNIDADES.get(u, u),
    })


def anualizar_salario(df: pd.DataFrame) -> pd.DataFrame:
    """Pasa todos los salarios a bruto anual.

    - Mensual x 12 y por hora x 1.760.
    - Un salario marcado como mensual pero de 10.000 € o más es casi seguro un salario
      anual con la unidad mal puesta: se trata como anual y se marca en salario_corregido.
    """
    df = df.copy()
    sospechoso = (df["salario_unidad"] == "mensual") & (df["salario_min_original"] >= UMBRAL_MENSUAL_SOSPECHOSO)
    factor = df["salario_unidad"].map({"anual": 1, "mensual": MESES_POR_ANO, "hora": HORAS_POR_ANO})
    factor[sospechoso] = 1
    df["salario_corregido"] = sospechoso
    df["salario_min"] = df["salario_min_original"] * factor
    df["salario_max"] = df["salario_max_original"] * factor
    df["salario_medio"] = (df["salario_min"] + df["salario_max"]) / 2
    df["tiene_salario"] = df["salario_medio"].notna()
    return df


# --- 4. Fechas ------------------------------------------------------------------
def tratar_fechas(df: pd.DataFrame) -> pd.DataFrame:
    """Fecha de publicación (o última actualización) y antigüedad de la oferta.

    Hay ofertas de 2017 a 2025 que siguen publicadas. No se eliminan: se marca si son
    recientes para poder filtrarlas en el análisis.
    """
    df = df.copy()
    df["fecha_publicacion"] = pd.to_datetime(df["fecha_texto"], format="%d/%m/%Y", errors="coerce")
    df["fecha_obtencion"] = pd.to_datetime(df["fecha_obtencion"])
    df["antiguedad_dias"] = (df["fecha_obtencion"] - df["fecha_publicacion"]).dt.days
    df["reciente"] = df["antiguedad_dias"] <= DIAS_RECIENTE
    return df


# --- 5. Tecnologías ---------------------------------------------------------------
def cargar_alias() -> dict[str, list[str]]:
    ref = pd.read_csv(REFERENCE / "tecnologias.csv")
    return {fila.tecnologia: [a.strip().lower() for a in fila.alias.split(";") if a.strip()] for fila in ref.itertuples()}


def patron_alias(alias: str) -> re.Pattern:
    """Coincidencia de palabra completa: 'java' no coincide con 'javascript'
    ni 'git' con 'github'."""
    return re.compile(r"(?<![\w.#+])" + re.escape(alias) + r"(?![\w#+])")


def detectar_tecnologias(df: pd.DataFrame) -> pd.DataFrame:
    """Tabla larga (id_oferta, tecnologia) a partir de las etiquetas y del título.

    Se usan las etiquetas de tecnología de la oferta y el título; no el resumen de la
    descripción, que está recortado y genera falsos positivos.
    """
    patrones = {tec: [patron_alias(a) for a in alias] for tec, alias in cargar_alias().items()}
    filas = []
    for o in df.itertuples():
        texto = " ; ".join([str(o.tecnologias or "").replace(";", " ; "), str(o.titulo or "")]).lower()
        for tec, pats in patrones.items():
            if any(p.search(texto) for p in pats):
                filas.append({"id_oferta": o.id_oferta, "tecnologia": tec})
    return pd.DataFrame(filas, columns=["id_oferta", "tecnologia"])


# --- Proceso completo --------------------------------------------------------------
def limpiar(raw: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    df = quitar_duplicados(raw)
    df["modalidad"] = df["modalidad"].map(normalizar_modalidad)
    df["ciudad"] = df.apply(grupo_ciudad, axis=1)
    df = pd.concat([df, df["salario_texto"].apply(parsear_salario)], axis=1)
    df = anualizar_salario(df)
    df = tratar_fechas(df)
    df["tipo_contrato"] = (df["tipo_contrato"].fillna("No indicado")
                           .str.replace("Contrato ", "", regex=False).str.capitalize())
    df["estado"] = df["estado"].fillna("Sin etiqueta")
    # Salarios muy bajos que no son errores: jornadas parciales o de fin de semana.
    # No se eliminan; se marcan para poder separarlos en el análisis del salario.
    df["posible_jornada_parcial"] = df["titulo"].str.contains(RE_PARCIAL, na=False)
    df["fuente"] = "tecnoempleo"

    tecnologias = detectar_tecnologias(df)
    df["n_tecnologias"] = df["id_oferta"].map(tecnologias["id_oferta"].value_counts()).fillna(0).astype(int)

    columnas = [
        "fuente", "id_oferta", "titulo", "empresa", "ciudad", "ubicacion", "modalidad", "categoria",
        "salario_min", "salario_max", "salario_medio", "tiene_salario", "salario_unidad",
        "salario_corregido", "salario_texto", "posible_jornada_parcial", "tipo_contrato", "tecnologias", "n_tecnologias",
        "fecha_publicacion", "antiguedad_dias", "reciente", "estado", "urgente",
        "en_listado_madrid", "en_listado_barcelona", "fecha_obtencion", "url",
    ]
    df = df[columnas].rename(columns={"tecnologias": "etiquetas_originales"})
    return df, tecnologias


def resumen(df: pd.DataFrame, tecnologias: pd.DataFrame) -> None:
    print(f"Ofertas: {len(df)} · columnas: {df.shape[1]}")
    print(f"Con salario: {df['tiene_salario'].sum()} ({df['tiene_salario'].mean():.0%}) · "
          f"salarios convertidos desde mensual/hora: {(df['salario_unidad'].isin(['mensual', 'hora'])).sum()} · "
          f"unidad corregida: {df['salario_corregido'].sum()}")
    print(f"Posible jornada parcial: {df['posible_jornada_parcial'].sum()}")
    print(f"Recientes (≤ {DIAS_RECIENTE} días): {df['reciente'].sum()}")
    print("Ciudad:", df["ciudad"].value_counts().to_dict())
    print("Modalidad:", df["modalidad"].value_counts().to_dict())
    print(f"Ofertas con al menos una tecnología del estudio: {(df['n_tecnologias'] > 0).sum()}")
    print("Tecnologías (top 10):", tecnologias["tecnologia"].value_counts().head(10).to_dict())


if __name__ == "__main__":
    ofertas, tecnologias = limpiar(cargar_raw())
    PROCESSED.mkdir(parents=True, exist_ok=True)
    ofertas.to_csv(PROCESSED / "tecnoempleo_ofertas.csv", index=False, encoding="utf-8")
    tecnologias.to_csv(PROCESSED / "tecnoempleo_tecnologias.csv", index=False, encoding="utf-8")
    resumen(ofertas, tecnologias)
    print(f"\nGuardado en {PROCESSED}")
