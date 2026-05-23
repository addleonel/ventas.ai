"""Genera un CSV de ventas sintético realista para usar como demo.

Ejecutar: py scripts/generar_demo.py
"""
import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

random.seed(42)

BASE = Path(__file__).resolve().parent.parent
OUT = BASE / "data" / "ventas_demo.csv"
OUT.parent.mkdir(parents=True, exist_ok=True)

PRODUCTOS = [
    ("Laptop Lenovo IdeaPad", "Tecnologia", 2_800_000),
    ("Mouse Inalambrico Logitech", "Tecnologia", 85_000),
    ("Teclado Mecanico Redragon", "Tecnologia", 220_000),
    ("Monitor LG 24''", "Tecnologia", 950_000),
    ("Silla Ergonomica Oficina", "Mobiliario", 680_000),
    ("Escritorio Madera 120cm", "Mobiliario", 450_000),
    ("Lampara LED Escritorio", "Mobiliario", 95_000),
    ("Cuaderno Universitario", "Papeleria", 12_000),
    ("Boligrafos Caja x12", "Papeleria", 18_000),
    ("Resma Papel Carta", "Papeleria", 25_000),
]

CIUDADES = ["Bogota", "Medellin", "Cali", "Barranquilla", "Cartagena", "Bucaramanga"]
CLIENTES = [
    "Empresa Alfa SAS", "Comercial Beta LTDA", "Distribuidora Gamma",
    "Inversiones Delta", "Servicios Epsilon", "Grupo Zeta SAS",
    "Tienda Eta", "Negocios Theta", "Mayorista Iota", "Soluciones Kappa",
]

FECHA_INICIO = datetime(2025, 11, 1)
FECHA_FIN = datetime(2026, 5, 15)
N_VENTAS = 250

def fecha_aleatoria():
    delta = (FECHA_FIN - FECHA_INICIO).days
    return FECHA_INICIO + timedelta(days=random.randint(0, delta))

def main():
    filas = []
    for i in range(1, N_VENTAS + 1):
        producto, categoria, precio_base = random.choice(PRODUCTOS)
        # Pequena variacion de precio (+/- 5%)
        precio = int(precio_base * random.uniform(0.95, 1.05))
        cantidad = random.choices([1, 2, 3, 4, 5, 10], weights=[40, 25, 15, 10, 5, 5])[0]
        fecha = fecha_aleatoria()
        fila = {
            "id_venta": i,
            "fecha": fecha.strftime("%Y-%m-%d"),
            "producto": producto,
            "categoria": categoria,
            "cantidad": cantidad,
            "precio_unitario": precio,
            "total": precio * cantidad,
            "cliente": random.choice(CLIENTES),
            "ciudad": random.choice(CIUDADES),
        }
        filas.append(fila)

    filas.sort(key=lambda r: r["fecha"])

    with open(OUT, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(filas[0].keys()))
        writer.writeheader()
        writer.writerows(filas)

    print(f"Generadas {len(filas)} ventas en {OUT}")

if __name__ == "__main__":
    main()
