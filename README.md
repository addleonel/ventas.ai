# ventas.ia — Analizador de Ventas con IA

Aplicación web Flask que recibe un CSV de ventas en **Soles (S/)** y devuelve
un dashboard con métricas, gráficas analíticas y un resumen ejecutivo
redactado por IA.

## Características

- Métricas, 8 gráficas analíticas y resumen ejecutivo generado por IA.
- Carga asíncrona con skeleton loaders: las secciones se hidratan apenas
  están listas.
- UI cream + pastel, estilo neo-brutalist.
- Moneda en Soles (S/), fechas en `DD/MM/YYYY`.

## Stack

Flask · Pandas · Matplotlib · OpenAI SDK (compatible con DeepSeek) ·
`marked.js` para markdown.

## Instalación

Requiere **Python 3.10+**.

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Configuración

Crea un archivo `.env` en la raíz:

```env
OPENAI_API_KEY=tu_clave_aqui
OPENAI_BASE_URL=https://api.deepseek.com
MODEL_NAME=deepseek-chat
FLASK_SECRET_KEY=cambia-esto
```

## Ejecutar

```powershell
python app.py
```

Abre `http://127.0.0.1:5000`.

Para regenerar los CSVs de demo:

```powershell
python scripts/generar_demo.py
```

## Formato del CSV

Columnas obligatorias: `fecha`, `producto`, `categoria`, `cantidad`,
`precio_unitario`, `total`. Opcionales: `cliente`, `ciudad`.

- Fechas en `DD/MM/YYYY`.
- Montos en Soles (S/).
- UTF-8, máximo 5 MB.

## Despliegue

Recomendado: **Render** (free tier soporta Flask sin cambios).

1. Subir el repo a GitHub.
2. *New → Web Service* y conectar el repo.
3. Build: `pip install -r requirements.txt`
4. Start: `gunicorn app:app` (añadir `gunicorn` a `requirements.txt`).
5. Configurar las variables de entorno del `.env`.

