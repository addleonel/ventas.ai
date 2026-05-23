"""Carga el CSV de ventas y calcula las metricas clave con Pandas y NumPy."""
from __future__ import annotations

import numpy as np
import pandas as pd

COLUMNAS_REQUERIDAS = {
    "fecha", "producto", "categoria", "cantidad", "precio_unitario", "total",
}


def cargar_csv(ruta) -> pd.DataFrame:
    df = pd.read_csv(ruta)
    faltantes = COLUMNAS_REQUERIDAS - set(df.columns)
    if faltantes:
        raise ValueError(
            f"El CSV no tiene las columnas requeridas. Faltan: {sorted(faltantes)}"
        )
    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
    df = df.dropna(subset=["fecha"])
    df["cantidad"] = pd.to_numeric(df["cantidad"], errors="coerce").fillna(0).astype(int)
    df["precio_unitario"] = pd.to_numeric(df["precio_unitario"], errors="coerce").fillna(0.0)
    df["total"] = pd.to_numeric(df["total"], errors="coerce").fillna(
        df["cantidad"] * df["precio_unitario"]
    )
    return df


def metricas_generales(df: pd.DataFrame) -> dict:
    total_ventas = float(df["total"].sum())
    n_transacciones = int(len(df))
    ticket_promedio = float(np.mean(df["total"])) if n_transacciones else 0.0
    unidades_vendidas = int(df["cantidad"].sum())
    rango_fechas = (df["fecha"].min(), df["fecha"].max())
    return {
        "total_ventas": total_ventas,
        "n_transacciones": n_transacciones,
        "ticket_promedio": ticket_promedio,
        "unidades_vendidas": unidades_vendidas,
        "fecha_inicio": rango_fechas[0].strftime("%Y-%m-%d"),
        "fecha_fin": rango_fechas[1].strftime("%Y-%m-%d"),
    }


def ventas_por_producto(df: pd.DataFrame, top_n: int = 5) -> pd.DataFrame:
    agg = (
        df.groupby("producto")
        .agg(total=("total", "sum"), unidades=("cantidad", "sum"))
        .sort_values("total", ascending=False)
        .head(top_n)
        .reset_index()
    )
    return agg


def ventas_por_mes(df: pd.DataFrame) -> pd.DataFrame:
    serie = (
        df.set_index("fecha")["total"]
        .resample("MS")
        .sum()
        .reset_index()
        .rename(columns={"fecha": "mes"})
    )
    serie["mes_etiqueta"] = serie["mes"].dt.strftime("%Y-%m")
    return serie


def ventas_por_categoria(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("categoria")["total"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )


def top_clientes(df: pd.DataFrame, top_n: int = 5) -> pd.DataFrame:
    if "cliente" not in df.columns:
        return pd.DataFrame(columns=["cliente", "total"])
    return (
        df.groupby("cliente")["total"]
        .sum()
        .sort_values(ascending=False)
        .head(top_n)
        .reset_index()
    )


def analizar(df: pd.DataFrame) -> dict:
    """Ejecuta todo el analisis y devuelve un dict con los resultados."""
    return {
        "metricas": metricas_generales(df),
        "por_producto": ventas_por_producto(df),
        "por_mes": ventas_por_mes(df),
        "por_categoria": ventas_por_categoria(df),
        "top_clientes": top_clientes(df),
    }
