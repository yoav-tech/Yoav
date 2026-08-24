import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = ROOT / os.getenv("DATABASE_PATH", "data/youtube.db")
CHANNELS_PATH = ROOT / "config/channels.yaml"
NICHES_PATH = ROOT / "config/niches.yaml"
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434").rstrip("/")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3:8b")
GOOGLE_CLIENT_SECRET = ROOT / os.getenv("GOOGLE_CLIENT_SECRET", "secrets/client_secret.json")
GOOGLE_TOKEN_PATH = ROOT / os.getenv("GOOGLE_TOKEN_PATH", "secrets/youtube_token.json")
UPLOAD_PRIVACY_STATUS = os.getenv("UPLOAD_PRIVACY_STATUS", "private")
MIN_OUTLIER_SCORE = float(os.getenv("MIN_OUTLIER_SCORE", "60"))
MAX_DEEP_ANALYSIS_PER_RUN = int(os.getenv("MAX_DEEP_ANALYSIS_PER_RUN", "10"))
LOOKBACK_DAYS = int(os.getenv("LOOKBACK_DAYS", "90"))
