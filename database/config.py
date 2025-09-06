from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "data.db"

DB_PATH.parent.mkdir(parents=True, exist_ok=True)