"""Servidor Flask del analizador de ventas con IA."""
from __future__ import annotations

from pathlib import Path

from flask import Flask, flash, redirect, render_template, request, url_for
from werkzeug.utils import secure_filename

from config import (
    ALLOWED_EXTENSIONS,
    DEMO_CSV,
    FLASK_SECRET_KEY,
    MAX_UPLOAD_MB,
    UPLOAD_DIR,
)
import analysis
import charts
import ai_summary

app = Flask(__name__)
app.config["SECRET_KEY"] = FLASK_SECRET_KEY
app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_MB * 1024 * 1024


def _archivo_permitido(nombre: str) -> bool:
    return "." in nombre and nombre.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def _procesar_y_renderizar(ruta_csv: Path):
    df = analysis.cargar_csv(ruta_csv)
    resultado = analysis.analizar(df)
    rutas_graficos = charts.generar_todos(resultado)
    resumen = ai_summary.generar_resumen(resultado)
    return render_template(
        "dashboard.html",
        metricas=resultado["metricas"],
        graficos=rutas_graficos,
        resumen_ia=resumen,
        tabla_productos=resultado["por_producto"].to_dict(orient="records"),
    )


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/demo")
def demo():
    if not DEMO_CSV.exists():
        flash("No se encontro el CSV de demo. Ejecuta scripts/generar_demo.py primero.", "error")
        return redirect(url_for("index"))
    try:
        return _procesar_y_renderizar(DEMO_CSV)
    except Exception as e:
        flash(f"Error al procesar el CSV de demo: {e}", "error")
        return redirect(url_for("index"))


@app.route("/analizar", methods=["POST"])
def analizar():
    archivo = request.files.get("archivo")
    if not archivo or archivo.filename == "":
        flash("Debes seleccionar un archivo.", "error")
        return redirect(url_for("index"))
    if not _archivo_permitido(archivo.filename):
        flash("Solo se permiten archivos .csv", "error")
        return redirect(url_for("index"))

    nombre_seguro = secure_filename(archivo.filename)
    ruta = UPLOAD_DIR / nombre_seguro
    archivo.save(ruta)

    try:
        return _procesar_y_renderizar(ruta)
    except ValueError as e:
        flash(str(e), "error")
        return redirect(url_for("index"))
    except Exception as e:
        flash(f"Error al procesar el archivo: {e}", "error")
        return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
