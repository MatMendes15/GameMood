import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
LANCEDB_URI = str(DATA_DIR / "lancedb")
RAW_DIR.mkdir(parents=True, exist_ok=True)
Path(LANCEDB_URI).mkdir(parents=True, exist_ok=True)

LLM_MODEL = "gemma3:12B"
EMBEDDING_MODEL = "nomic-embed-text"

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

TABLE_GAMES = "games_lore"
TABLE_SCIENCE = "saude_mental"


load_dotenv()
IGDB_CLIENT_ID = os.getenv("IGDB_CLIENT_ID")
IGDB_CLIENT_SECRET = os.getenv("IGDB_CLIENT_SECRET")