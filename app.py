"""Servidor Flask del analizador de ventas con IA."""
from __future__ import annotations

import threading
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from flask import Flask, flash, jsonify, redirect, render_template, request, url_for
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

JOBS: dict = {}
JOBS_LOCK = threading.Lock()
EXECUTOR = ThreadPoolExecutor(max_workers=4)
SECCIONES = ("metricas", "tabla", "charts", "resumen")


def _archivo_permitido(nombre: str) -> bool:
    return "." in nombre and nombre.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def _set_section(job_id: str, name: str, status: str, data):
    job = JOBS.get(job_id)
    if not job:
        return
    with job["lock"]:
        job["sections"][name] = {"status": status, "data": data}


def _procesar_job(job_id: str, ruta_csv: Path):
    try:
        df = analysis.cargar_csv(Path(ruta_csv))
        resultado = analysis.analizar(df)
    except Exception as e:
        for s in SECCIONES:
            _set_section(job_id, s, "error", str(e))
        return

    _set_section(job_id, "metricas", "ready", resultado["metricas"])
    _set_section(
        job_id,
        "tabla",
        "ready",
        resultado["por_producto"].to_dict(orient="records"),
    )

    def _charts():
        try:
            rutas = charts.generar_todos(resultado)
            _set_section(job_id, "charts", "ready", rutas)
        except Exception as e:
            _set_section(job_id, "charts", "error", str(e))

    def _resumen():
        try:
            texto = ai_summary.generar_resumen(resultado)
            _set_section(job_id, "resumen", "ready", texto)
        except Exception as e:
            _set_section(job_id, "resumen", "error", str(e))

    EXECUTOR.submit(_charts)
    EXECUTOR.submit(_resumen)


def _crear_job(ruta_csv: Path) -> str:
    job_id = uuid.uuid4().hex
    with JOBS_LOCK:
        JOBS[job_id] = {
            "lock": threading.Lock(),
            "sections": {s: {"status": "pending", "data": None} for s in SECCIONES},
        }
    EXECUTOR.submit(_procesar_job, job_id, ruta_csv)
    return job_id


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/subir")
def subir():
    return render_template("subir.html")


@app.route("/demo")
def demo():
    if not DEMO_CSV.exists():
        flash(
            "No se encontro el CSV de demo. Ejecuta scripts/generar_demo.py primero.",
            "error",
        )
        return redirect(url_for("index"))
    job_id = _crear_job(DEMO_CSV)
    return redirect(url_for("dashboard", job_id=job_id))


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
    job_id = _crear_job(ruta)
    return redirect(url_for("dashboard", job_id=job_id))


@app.route("/dashboard/<job_id>")
def dashboard(job_id: str):
    if job_id not in JOBS:
        flash("La sesion de analisis expiro o no existe.", "error")
        return redirect(url_for("index"))
    return render_template("dashboard.html", job_id=job_id)


@app.route("/api/job/<job_id>/<section>")
def api_job(job_id: str, section: str):
    job = JOBS.get(job_id)
    if not job:
        return jsonify({"status": "not_found"}), 404
    if section not in job["sections"]:
        return jsonify({"status": "not_found"}), 404
    with job["lock"]:
        return jsonify(job["sections"][section])


if __name__ == "__main__":
    app.run(debug=True, threaded=True)
