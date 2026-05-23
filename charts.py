"""Genera graficos PNG con Matplotlib y los guarda en static/charts/.

Tema visual alineado con la paleta de la plataforma (cream/pastel + ink).
"""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")  # backend sin GUI, necesario para Flask

import matplotlib.pyplot as plt
import pandas as pd

from config import CHARTS_DIR

PALETA = {
    "ink":     "#1a1a1a",
    "ink_soft": "#3a3a3a",
    "cream":   "#f3e9d2",
    "yellow":  "#ffe066",
    "mint":    "#b6f0c2",
    "pink":    "#ffb6c8",
    "orange":  "#ffb877",
    "blue":    "#a8c8ff",
    "muted":   "#6b6253",
}

SERIES = [
    PALETA["yellow"], PALETA["mint"], PALETA["pink"],
    PALETA["orange"], PALETA["blue"],
]


def _setup(fig, ax):
    fig.patch.set_alpha(0)
    ax.set_facecolor("none")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    for s in ("bottom", "left"):
        ax.spines[s].set_color(PALETA["ink"])
        ax.spines[s].set_linewidth(1.2)
    ax.tick_params(colors=PALETA["ink"], labelsize=9)
    ax.title.set_color(PALETA["ink"])
    ax.title.set_fontsize(13)
    ax.title.set_fontweight("bold")
    ax.yaxis.label.set_color(PALETA["ink"])
    ax.xaxis.label.set_color(PALETA["ink"])
    ax.yaxis.label.set_size(10)
    ax.xaxis.label.set_size(10)
    ax.grid(True, axis="y", linestyle="--", color=PALETA["ink"], alpha=0.12)


def _guardar(fig, nombre: str) -> str:
    ruta = CHARTS_DIR / nombre
    fig.tight_layout()
    fig.savefig(ruta, dpi=110, bbox_inches="tight", transparent=True)
    plt.close(fig)
    return f"charts/{nombre}"


# ============================================================================
# Hero chart (alargado)
# ============================================================================
def grafico_tendencia_diaria(df_diario: pd.DataFrame) -> str:
    if df_diario.empty:
        return ""
    fig, ax = plt.subplots(figsize=(13, 4.2))
    _setup(fig, ax)
    ax.fill_between(
        df_diario["fecha"], df_diario["ma"],
        color=PALETA["mint"], alpha=0.55, label="Promedio móvil 7d",
    )
    ax.plot(
        df_diario["fecha"], df_diario["total"],
        color=PALETA["ink"], linewidth=0.9, alpha=0.45, label="Ventas diarias",
    )
    ax.plot(
        df_diario["fecha"], df_diario["ma"],
        color=PALETA["ink"], linewidth=2.6, label="Tendencia (PM 7d)",
    )
    ax.set_title("Tendencia diaria de ingresos · promedio móvil de 7 días")
    ax.set_ylabel("Ingresos (S/)")
    ax.ticklabel_format(style="plain", axis="y")
    leg = ax.legend(frameon=False, loc="upper left", fontsize=9)
    for text in leg.get_texts():
        text.set_color(PALETA["ink"])
    return _guardar(fig, "tendencia_diaria.png")


# ============================================================================
# Crecimiento MoM
# ============================================================================
def grafico_crecimiento_mom(df_mom: pd.DataFrame) -> str:
    if len(df_mom) < 2:
        return ""
    datos = df_mom.iloc[1:]  # primer mes no tiene comparación
    fig, ax = plt.subplots(figsize=(8, 4.5))
    _setup(fig, ax)
    colores = [PALETA["mint"] if v >= 0 else PALETA["pink"] for v in datos["pct_change"]]
    bars = ax.bar(
        datos["mes_etiqueta"], datos["pct_change"],
        color=colores, edgecolor=PALETA["ink"], linewidth=1.4,
    )
    ax.axhline(0, color=PALETA["ink"], linewidth=1.2)
    rango = max(abs(datos["pct_change"].max()), abs(datos["pct_change"].min()), 5)
    pad = rango * 0.12
    ax.set_ylim(-rango - pad * 2, rango + pad * 2)
    for bar, val in zip(bars, datos["pct_change"]):
        offset = pad if val >= 0 else -pad
        ax.text(
            bar.get_x() + bar.get_width() / 2, val + offset,
            f"{val:+.1f}%",
            ha="center", va="center", fontsize=9,
            color=PALETA["ink"], fontweight="bold",
        )
    ax.set_title("Crecimiento mensual vs. mes anterior")
    ax.set_ylabel("Variación (%)")
    plt.xticks(rotation=30, ha="right")
    return _guardar(fig, "crecimiento_mom.png")


# ============================================================================
# Producto estrella - evolución semanal
# ============================================================================
def grafico_producto_estrella(estrella: dict | None) -> str:
    if not estrella or estrella["serie"].empty:
        return ""
    serie = estrella["serie"]
    fig, ax = plt.subplots(figsize=(8, 4.5))
    _setup(fig, ax)
    x = range(len(serie))
    ax.fill_between(x, serie["total"], color=PALETA["orange"], alpha=0.5)
    ax.plot(
        x, serie["total"],
        color=PALETA["ink"], linewidth=2.4, marker="o",
        markersize=6, markerfacecolor=PALETA["orange"],
        markeredgecolor=PALETA["ink"], markeredgewidth=1.4,
    )
    ax.set_xticks(list(x))
    ax.set_xticklabels(serie["etiqueta"], rotation=40, ha="right", fontsize=8)
    nombre_corto = estrella["producto"]
    if len(nombre_corto) > 32:
        nombre_corto = nombre_corto[:30] + "…"
    ax.set_title(f"Producto estrella · {nombre_corto}")
    ax.set_ylabel("Ingresos semanales (S/)")
    ax.ticklabel_format(style="plain", axis="y")
    return _guardar(fig, "producto_estrella.png")


# ============================================================================
# Ventas por mes (evolución)
# ============================================================================
def grafico_ventas_mes(df_mes: pd.DataFrame) -> str:
    fig, ax = plt.subplots(figsize=(8, 5))
    _setup(fig, ax)
    ax.fill_between(
        df_mes["mes_etiqueta"], df_mes["total"],
        color=PALETA["mint"], alpha=0.45,
    )
    ax.plot(
        df_mes["mes_etiqueta"], df_mes["total"],
        marker="o", color=PALETA["ink"], linewidth=2.5,
        markerfacecolor=PALETA["yellow"],
        markeredgecolor=PALETA["ink"], markeredgewidth=1.4, markersize=8,
    )
    ax.set_xlabel("Mes")
    ax.set_ylabel("Ingresos (S/)")
    ax.set_title("Evolución mensual de ingresos")
    ax.ticklabel_format(style="plain", axis="y")
    plt.xticks(rotation=40, ha="right")
    return _guardar(fig, "ventas_mes.png")


# ============================================================================
# Top productos
# ============================================================================
def grafico_top_productos(df_top: pd.DataFrame) -> str:
    fig, ax = plt.subplots(figsize=(8, 5))
    _setup(fig, ax)
    ax.grid(True, axis="x", linestyle="--", color=PALETA["ink"], alpha=0.12)
    ax.grid(False, axis="y")
    bars = ax.barh(
        df_top["producto"][::-1], df_top["total"][::-1],
        color=PALETA["yellow"], edgecolor=PALETA["ink"], linewidth=1.4,
    )
    for bar, val in zip(bars, df_top["total"][::-1]):
        ax.text(
            val, bar.get_y() + bar.get_height() / 2,
            f"  S/ {val:,.0f}",
            va="center", fontsize=8.5, color=PALETA["ink"],
        )
    ax.set_xlabel("Ventas totales (S/)")
    ax.set_title("Top productos por ventas")
    ax.ticklabel_format(style="plain", axis="x")
    return _guardar(fig, "top_productos.png")


# ============================================================================
# Distribución por categorías (donut)
# ============================================================================
def grafico_categorias(df_cat: pd.DataFrame) -> str:
    fig, ax = plt.subplots(figsize=(7, 5.5))
    fig.patch.set_alpha(0)
    ax.set_facecolor("none")
    colores = SERIES * ((len(df_cat) // len(SERIES)) + 1)
    wedges, texts, autotexts = ax.pie(
        df_cat["total"],
        labels=df_cat["categoria"],
        autopct="%1.1f%%",
        startangle=90,
        colors=colores[: len(df_cat)],
        wedgeprops={"edgecolor": PALETA["ink"], "linewidth": 1.5, "width": 0.42},
        textprops={"color": PALETA["ink"], "fontsize": 9.5, "fontweight": "500"},
        pctdistance=0.78,
    )
    for at in autotexts:
        at.set_fontweight("bold")
    ax.set_title("Distribución de ventas por categoría", color=PALETA["ink"],
                 fontsize=13, fontweight="bold", pad=10)
    return _guardar(fig, "categorias.png")


# ============================================================================
# Top clientes
# ============================================================================
def grafico_top_clientes(df_cli: pd.DataFrame) -> str:
    if df_cli.empty:
        return ""
    fig, ax = plt.subplots(figsize=(8, 4.5))
    _setup(fig, ax)
    bars = ax.bar(
        df_cli["cliente"], df_cli["total"],
        color=PALETA["pink"], edgecolor=PALETA["ink"], linewidth=1.4,
    )
    for bar in bars:
        h = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2, h,
            f"S/ {h:,.0f}",
            ha="center", va="bottom", fontsize=8.5, color=PALETA["ink"],
        )
    ax.set_ylabel("Ventas totales (S/)")
    ax.set_title("Top clientes")
    ax.ticklabel_format(style="plain", axis="y")
    plt.xticks(rotation=22, ha="right")
    return _guardar(fig, "top_clientes.png")


# ============================================================================
# Ventas por día de la semana
# ============================================================================
def grafico_dia_semana(df_dia: pd.DataFrame) -> str:
    if df_dia.empty:
        return ""
    fig, ax = plt.subplots(figsize=(8, 4.5))
    _setup(fig, ax)
    colores = [SERIES[i % len(SERIES)] for i in range(len(df_dia))]
    bars = ax.bar(
        df_dia["dia"], df_dia["total"],
        color=colores, edgecolor=PALETA["ink"], linewidth=1.4,
    )
    for bar in bars:
        h = bar.get_height()
        if h <= 0:
            continue
        ax.text(
            bar.get_x() + bar.get_width() / 2, h,
            f"S/ {h:,.0f}",
            ha="center", va="bottom", fontsize=8.5, color=PALETA["ink"],
        )
    ax.set_ylabel("Ingresos (S/)")
    ax.set_title("Ingresos por día de la semana")
    ax.ticklabel_format(style="plain", axis="y")
    return _guardar(fig, "dia_semana.png")


# ============================================================================
# Agregador
# ============================================================================
def generar_todos(analisis: dict) -> dict:
    return {
        "tendencia_diaria":  grafico_tendencia_diaria(analisis["diario_ma"]),
        "crecimiento_mom":   grafico_crecimiento_mom(analisis["crecimiento_mom"]),
        "producto_estrella": grafico_producto_estrella(analisis["producto_estrella"]),
        "ventas_mes":        grafico_ventas_mes(analisis["por_mes"]),
        "top_productos":     grafico_top_productos(analisis["por_producto"]),
        "categorias":        grafico_categorias(analisis["por_categoria"]),
        "top_clientes":      grafico_top_clientes(analisis["top_clientes"]),
        "dia_semana":        grafico_dia_semana(analisis["dia_semana"]),
    }
