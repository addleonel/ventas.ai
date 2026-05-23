"""Carga el CSV de ventas y calcula las metricas clave con Pandas y NumPy."""
from __future__ import annotations

import numpy as np
import pandas as pd

COLUMNAS_REQUERIDAS = {
    "fecha", "producto", "categoria", "cantidad", "precio_unitario", "total",
}

FECHA_FMT = "%d/%m/%Y"  # Día/Mes/Año

MESES_ES = {
    1: "Ene", 2: "Feb", 3: "Mar", 4: "Abr", 5: "May", 6: "Jun",
    7: "Jul", 8: "Ago", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dic",
}


def cargar_csv(ruta) -> pd.DataFrame:
    df = pd.read_csv(ruta)
    faltantes = COLUMNAS_REQUERIDAS - set(df.columns)
    if faltantes:
        raise ValueError(
            f"El CSV no tiene las columnas requeridas. Faltan: {sorted(faltantes)}"
        )
    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce", dayfirst=True)
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
        "fecha_inicio": rango_fechas[0].strftime(FECHA_FMT),
        "fecha_fin": rango_fechas[1].strftime(FECHA_FMT),
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
    serie["mes_etiqueta"] = (
        serie["mes"].dt.month.map(MESES_ES) + " " + serie["mes"].dt.year.astype(str)
    )
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


DIAS_ES = {
    "Monday": "Lun", "Tuesday": "Mar", "Wednesday": "Mie",
    "Thursday": "Jue", "Friday": "Vie", "Saturday": "Sab", "Sunday": "Dom",
}
ORDEN_DIAS = ["Lun", "Mar", "Mie", "Jue", "Vie", "Sab", "Dom"]


def crecimiento_mom(df_mes: pd.DataFrame) -> pd.DataFrame:
    out = df_mes.copy()
    out["pct_change"] = out["total"].pct_change().fillna(0) * 100
    return out


def producto_estrella_evolucion(df: pd.DataFrame):
    totales = df.groupby("producto")["total"].sum().sort_values(ascending=False)
    if totales.empty:
        return None
    nombre = totales.index[0]
    sub = df[df["producto"] == nombre]
    serie = (
        sub.set_index("fecha")["total"]
        .resample("W-MON")
        .sum()
        .reset_index()
    )
    serie["etiqueta"] = serie["fecha"].dt.strftime("%d/%m")
    return {"producto": nombre, "total": float(totales.iloc[0]), "serie": serie}


def ventas_diarias_con_ma(df: pd.DataFrame, window: int = 7) -> pd.DataFrame:
    diario = (
        df.set_index("fecha")["total"]
        .resample("D")
        .sum()
        .fillna(0)
        .reset_index()
    )
    diario["ma"] = diario["total"].rolling(window=window, min_periods=1).mean()
    return diario


def ventas_por_dia_semana(df: pd.DataFrame) -> pd.DataFrame:
    s = df.copy()
    s["dia_en"] = s["fecha"].dt.day_name()
    s["dia"] = s["dia_en"].map(DIAS_ES)
    return (
        s.groupby("dia")["total"]
        .sum()
        .reindex(ORDEN_DIAS)
        .fillna(0)
        .reset_index()
    )


def analizar(df: pd.DataFrame) -> dict:
    """Ejecuta todo el analisis y devuelve un dict con los resultados."""
    por_mes = ventas_por_mes(df)
    return {
        "metricas": metricas_generales(df),
        "por_producto": ventas_por_producto(df),
        "por_mes": por_mes,
        "por_categoria": ventas_por_categoria(df),
        "top_clientes": top_clientes(df),
        "crecimiento_mom": crecimiento_mom(por_mes),
        "producto_estrella": producto_estrella_evolucion(df),
        "diario_ma": ventas_diarias_con_ma(df),
        "dia_semana": ventas_por_dia_semana(df),
    }
