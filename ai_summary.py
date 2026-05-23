"""Genera un resumen ejecutivo usando la API de OpenAI a partir de las metricas."""
from __future__ import annotations

from openai import OpenAI, OpenAIError

from config import MODEL_NAME, OPENAI_API_KEY, OPENAI_BASE_URL

PROMPT_SISTEMA = (
    "Eres un analista de negocios en Peru. Recibes metricas de ventas resumidas "
    "de una empresa peruana, expresadas en Soles (S/), y debes redactar un "
    "resumen ejecutivo claro y util en espanol. Manten un tono profesional, "
    "evita repetir los numeros uno a uno y enfocate en hallazgos, tendencias y "
    "posibles acciones. Cuando menciones montos usa siempre el simbolo S/."
)


def _formatear_datos(analisis: dict) -> str:
    m = analisis["metricas"]
    productos = analisis["por_producto"].to_dict(orient="records")
    categorias = analisis["por_categoria"].to_dict(orient="records")
    meses = analisis["por_mes"][["mes_etiqueta", "total"]].to_dict(orient="records")
    clientes = analisis["top_clientes"].to_dict(orient="records")

    lineas = [
        f"Periodo analizado: {m['fecha_inicio']} a {m['fecha_fin']}",
        f"Ventas totales: S/ {m['total_ventas']:,.0f}",
        f"Transacciones: {m['n_transacciones']}",
        f"Ticket promedio: S/ {m['ticket_promedio']:,.0f}",
        f"Unidades vendidas: {m['unidades_vendidas']}",
        "",
        "Top productos:",
    ]
    for p in productos:
        lineas.append(f"  - {p['producto']}: S/ {p['total']:,.0f} ({p['unidades']} und)")

    lineas.append("\nVentas por categoria:")
    for c in categorias:
        lineas.append(f"  - {c['categoria']}: S/ {c['total']:,.0f}")

    lineas.append("\nVentas por mes:")
    for mes in meses:
        lineas.append(f"  - {mes['mes_etiqueta']}: S/ {mes['total']:,.0f}")

    if clientes:
        lineas.append("\nTop clientes:")
        for cli in clientes:
            lineas.append(f"  - {cli['cliente']}: S/ {cli['total']:,.0f}")

    return "\n".join(lineas)


def generar_resumen(analisis: dict) -> str:
    if not OPENAI_API_KEY or OPENAI_API_KEY == "tu_clave_aqui":
        return (
            "[Aviso] No hay una OPENAI_API_KEY configurada en .env, por lo que no "
            "se pudo generar el resumen ejecutivo automatico. Agrega tu clave en "
            "el archivo .env para activar esta funcion."
        )

    datos = _formatear_datos(analisis)
    client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)
    try:
        respuesta = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": PROMPT_SISTEMA},
                {
                    "role": "user",
                    "content": (
                        "Estas son las metricas de ventas (todos los montos en "
                        "Soles peruanos, S/). Redacta un resumen ejecutivo de 4 "
                        "a 6 parrafos cortos con hallazgos clave, tendencias "
                        "observadas y al menos 2 recomendaciones concretas.\n\n"
                        + datos
                    ),
                },
            ],
            temperature=0.5,
            max_tokens=600,
        )
        return respuesta.choices[0].message.content.strip()
    except OpenAIError as e:
        return f"[Error al consultar OpenAI] {e}"
