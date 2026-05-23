import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(override=True)

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = BASE_DIR / "uploads"
CHARTS_DIR = BASE_DIR / "static" / "charts"

DEMO_CSV = DATA_DIR / "ventas_demo.csv"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "").strip() or None
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "dev-only-secret")

ALLOWED_EXTENSIONS = {"csv"}
MAX_UPLOAD_MB = 5

for d in (DATA_DIR, UPLOAD_DIR, CHARTS_DIR):
    d.mkdir(parents=True, exist_ok=True)
