# common/config.py
from dotenv import load_dotenv # type: ignore
from pathlib import Path
import os

# Resolve project root: .../evoting-secure-prototype1
PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = PROJECT_ROOT / "infra" / ".env"

# Load environment variables from infra/.env
load_dotenv(dotenv_path=ENV_PATH)

# Expose settings to the app
DATABASE_URL  = os.getenv("DATABASE_URL")
AES_MASTER_KEY = os.getenv("AES_MASTER_KEY")   # hex-encoded 32-byte (64 hex chars) key
EXPORT_DIR    = os.getenv("EXPORT_DIR")
