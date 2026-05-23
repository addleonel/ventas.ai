"""Genera CSVs de ventas sintéticos en Soles (S/) para usar como demo y para subir.

Ejecutar: py scripts/generar_demo.py

Salidas:
  data/ventas_demo.csv                  -> usado por el botón "Demo"
  data/samples/ventas_tecnologia.csv    -> Tienda de tecnología (mismo dataset que demo)
  data/samples/ventas_restaurante.csv   -> Restaurante criollo
  data/samples/ventas_bodega.csv        -> Bodega / minimarket
  data/samples/ventas_consultoria.csv   -> Servicios de consultoría
"""
import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "data"
SAMPLES = DATA / "samples"
DATA.mkdir(parents=True, exist_ok=True)
SAMPLES.mkdir(parents=True, exist_ok=True)

CIUDADES_PE = [
    "Lima", "Arequipa", "Trujillo", "Cusco", "Piura",
    "Chiclayo", "Huancayo", "Iquitos", "Tacna", "Puno",
]


def generar_csv(ruta, productos, clientes, n_ventas, fecha_inicio, fecha_fin, seed):
    random.seed(seed)
    delta_dias = (fecha_fin - fecha_inicio).days
    filas = []
    for i in range(1, n_ventas + 1):
        producto, categoria, precio_base = random.choice(productos)
        precio = round(precio_base * random.uniform(0.92, 1.08), 2)
        cantidad = random.choices(
            [1, 2, 3, 4, 5, 8, 12], weights=[35, 25, 15, 10, 8, 4, 3]
        )[0]
        fecha = fecha_inicio + timedelta(days=random.randint(0, delta_dias))
        filas.append({
            "_dt": fecha,
            "id_venta": i,
            "fecha": fecha.strftime("%d/%m/%Y"),
            "producto": producto,
            "categoria": categoria,
            "cantidad": cantidad,
            "precio_unitario": precio,
            "total": round(precio * cantidad, 2),
            "cliente": random.choice(clientes),
            "ciudad": random.choice(CIUDADES_PE),
        })
    filas.sort(key=lambda r: r["_dt"])
    for r in filas:
        del r["_dt"]

    with open(ruta, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(filas[0].keys()))
        writer.writeheader()
        writer.writerows(filas)
    print(f"  {ruta.relative_to(BASE)}: {len(filas)} ventas")


# ============================================================================
# 1. Tienda de tecnología (precios en Soles)
# ============================================================================
PRODUCTOS_TECH = [
    ("Laptop Lenovo IdeaPad 3", "Tecnologia", 2500),
    ("Mouse Inalambrico Logitech M170", "Tecnologia", 75),
    ("Teclado Mecanico Redragon Kumara", "Tecnologia", 180),
    ("Monitor LG 24'' Full HD", "Tecnologia", 780),
    ("Audifonos Bluetooth Sony WH-CH520", "Tecnologia", 320),
    ("USB 32GB Kingston DataTraveler", "Tecnologia", 35),
    ("Webcam Logitech C270", "Tecnologia", 180),
    ("Silla Ergonomica Oficina", "Mobiliario", 550),
    ("Escritorio Madera 120cm", "Mobiliario", 380),
    ("Lampara LED Escritorio", "Mobiliario", 75),
    ("Cuaderno Universitario A4", "Papeleria", 8),
    ("Boligrafos Caja x12", "Papeleria", 15),
    ("Resma Papel A4 75gr", "Papeleria", 22),
]
CLIENTES_TECH = [
    "Empresa Andes SAC", "Comercial Inka EIRL", "Distribuidora Pacifico SAC",
    "Inversiones Los Olivos", "Servicios Surco SAC", "Grupo Miraflores SAC",
    "Tienda San Isidro", "Negocios Lince EIRL", "Mayorista Callao",
    "Soluciones La Molina",
]

print("Generando CSVs en Soles (S/)...\n")

# Demo principal + copia en samples
generar_csv(
    DATA / "ventas_demo.csv",
    PRODUCTOS_TECH, CLIENTES_TECH,
    n_ventas=250,
    fecha_inicio=datetime(2025, 11, 1),
    fecha_fin=datetime(2026, 5, 15),
    seed=42,
)
generar_csv(
    SAMPLES / "ventas_tecnologia.csv",
    PRODUCTOS_TECH, CLIENTES_TECH,
    n_ventas=320,
    fecha_inicio=datetime(2025, 9, 1),
    fecha_fin=datetime(2026, 5, 20),
    seed=11,
)

# ============================================================================
# 2. Restaurante criollo (alto volumen, ticket bajo)
# ============================================================================
PRODUCTOS_RESTAURANTE = [
    ("Lomo Saltado", "Platos de Fondo", 28),
    ("Aji de Gallina", "Platos de Fondo", 24),
    ("Arroz con Pollo", "Platos de Fondo", 22),
    ("Tallarin Saltado", "Platos de Fondo", 25),
    ("Ceviche de Pescado", "Entradas", 32),
    ("Causa Limeña", "Entradas", 18),
    ("Anticuchos de Corazon", "Entradas", 20),
    ("Papa a la Huancaina", "Entradas", 15),
    ("Chicha Morada Jarra", "Bebidas", 12),
    ("Inca Kola Personal", "Bebidas", 5),
    ("Pisco Sour", "Bebidas", 18),
    ("Cerveza Pilsen", "Bebidas", 9),
    ("Suspiro a la Limeña", "Postres", 12),
    ("Mazamorra Morada", "Postres", 10),
    ("Picarones con Miel", "Postres", 14),
]
CLIENTES_RESTAURANTE = [
    "Mesa Familia", "Cliente Delivery", "Grupo Oficina", "Turistas Cusco",
    "Pareja", "Cliente Frecuente", "Reserva Eventos", "Almuerzo Ejecutivo",
    "Grupo Universitario",
]
generar_csv(
    SAMPLES / "ventas_restaurante.csv",
    PRODUCTOS_RESTAURANTE, CLIENTES_RESTAURANTE,
    n_ventas=420,
    fecha_inicio=datetime(2026, 2, 1),
    fecha_fin=datetime(2026, 5, 20),
    seed=7,
)

# ============================================================================
# 3. Bodega / minimarket (muy alto volumen, ticket muy bajo)
# ============================================================================
PRODUCTOS_BODEGA = [
    ("Arroz Costeño 5kg", "Abarrotes", 28),
    ("Aceite Primor 1L", "Abarrotes", 12),
    ("Azucar Rubia 1kg", "Abarrotes", 4),
    ("Fideos Don Vittorio 500g", "Abarrotes", 4),
    ("Atun Florida Lata", "Abarrotes", 6),
    ("Leche Gloria Tarro", "Lacteos", 4),
    ("Yogurt Laive 1L", "Lacteos", 8),
    ("Queso Fresco kg", "Lacteos", 22),
    ("Pan Frances Unidad", "Panaderia", 1),
    ("Pan Yema Bolsa", "Panaderia", 5),
    ("Coca Cola 1.5L", "Bebidas", 7),
    ("Agua San Luis 625ml", "Bebidas", 2),
    ("Cerveza Cristal 650ml", "Bebidas", 7),
    ("Detergente Ariel 800g", "Limpieza", 14),
    ("Papel Higienico Suave x4", "Limpieza", 8),
    ("Lavavajilla Sapolio", "Limpieza", 5),
    ("Galletas Soda Field", "Snacks", 3),
    ("Papitas Lays 150g", "Snacks", 6),
    ("Chocolate Sublime", "Snacks", 2),
]
CLIENTES_BODEGA = [
    "Vecino del Barrio", "Cliente Casual", "Familia Cercana",
    "Comprador Frecuente", "Cliente Mayorista", "Tienda Vecina",
    "Pension Estudiantes", "Negocio Local",
]
generar_csv(
    SAMPLES / "ventas_bodega.csv",
    PRODUCTOS_BODEGA, CLIENTES_BODEGA,
    n_ventas=650,
    fecha_inicio=datetime(2026, 3, 1),
    fecha_fin=datetime(2026, 5, 22),
    seed=99,
)

# ============================================================================
# 4. Servicios de consultoría (pocos tickets, alto valor)
# ============================================================================
PRODUCTOS_SERVICIOS = [
    ("Auditoria Tributaria", "Tributario", 4500),
    ("Asesoria Contable Mensual", "Contabilidad", 1200),
    ("Plan de Negocio", "Estrategia", 3800),
    ("Capacitacion SUNAT", "Capacitacion", 850),
    ("Implementacion ERP", "Tecnologia", 12000),
    ("Auditoria de Sistemas", "Tecnologia", 6500),
    ("Estudio de Mercado", "Marketing", 5200),
    ("Campaña Digital 3 meses", "Marketing", 4200),
    ("Asesoria Legal Laboral", "Legal", 1800),
    ("Constitucion de Empresa", "Legal", 2500),
]
CLIENTES_SERVICIOS = [
    "Constructora Andina SAC", "Banco Regional", "ONG Esperanza",
    "Minera del Sur SAC", "Textiles Gamarra", "Restaurante Cadena Norte",
    "Clinica Privada San Felipe", "Universidad Privada del Norte",
    "Importadora Pacifico", "Agroindustria del Valle",
]
generar_csv(
    SAMPLES / "ventas_consultoria.csv",
    PRODUCTOS_SERVICIOS, CLIENTES_SERVICIOS,
    n_ventas=85,
    fecha_inicio=datetime(2025, 10, 1),
    fecha_fin=datetime(2026, 5, 15),
    seed=123,
)

print(f"\nListo. CSVs disponibles en {DATA.relative_to(BASE)}/ y {SAMPLES.relative_to(BASE)}/")
