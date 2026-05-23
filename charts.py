"""Genera graficos PNG con Matplotlib y los guarda en static/charts/."""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")  # backend sin GUI, necesario para Flask

import matplotlib.pyplot as plt
import pandas as pd

from config import CHARTS_DIR


def _guardar(fig, nombre: str) -> str:
    """Guarda la figura y devuelve la ruta relativa para usar en HTML."""
    ruta = CHARTS_DIR / nombre
    fig.tight_layout()
    fig.savefig(ruta, dpi=100, bbox_inches="tight")
    plt.close(fig)
    return f"charts/{nombre}"


def grafico_top_productos(df_top: pd.DataFrame) -> str:
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.barh(df_top["producto"][::-1], df_top["total"][::-1], color="#4C72B0")
    ax.set_xlabel("Ventas totales ($)")
    ax.set_title("Top productos por ventas")
    ax.ticklabel_format(style="plain", axis="x")
    return _guardar(fig, "top_productos.png")


def grafico_ventas_mes(df_mes: pd.DataFrame) -> str:
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(df_mes["mes_etiqueta"], df_mes["total"], marker="o", color="#55A868", linewidth=2)
    ax.set_xlabel("Mes")
    ax.set_ylabel("Ventas ($)")
    ax.set_title("Evolucion de ventas por mes")
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.ticklabel_format(style="plain", axis="y")
    plt.xticks(rotation=45)
    return _guardar(fig, "ventas_mes.png")


def grafico_categorias(df_cat: pd.DataFrame) -> str:
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(
        df_cat["total"],
        labels=df_cat["categoria"],
        autopct="%1.1f%%",
        startangle=90,
        colors=["#4C72B0", "#DD8452", "#55A868", "#C44E52"],
    )
    ax.set_title("Distribucion de ventas por categoria")
    return _guardar(fig, "categorias.png")


def grafico_top_clientes(df_cli: pd.DataFrame) -> str:
    if df_cli.empty:
        return ""
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.bar(df_cli["cliente"], df_cli["total"], color="#8172B2")
    ax.set_ylabel("Ventas totales ($)")
    ax.set_title("Top clientes")
    ax.ticklabel_format(style="plain", axis="y")
    plt.xticks(rotation=30, ha="right")
    return _guardar(fig, "top_clientes.png")


def generar_todos(analisis: dict) -> dict:
    """Genera los 4 graficos y devuelve un dict {nombre: ruta_relativa}."""
    return {
        "top_productos": grafico_top_productos(analisis["por_producto"]),
        "ventas_mes": grafico_ventas_mes(analisis["por_mes"]),
        "categorias": grafico_categorias(analisis["por_categoria"]),
        "top_clientes": grafico_top_clientes(analisis["top_clientes"]),
    }
