import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent

# Database
DATABASE_PATH = BASE_DIR / "data" / "armoric.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# Data files
SALES_DATA_PATH = BASE_DIR / "sales_data.csv"
FEEDBACK_DATA_PATH = BASE_DIR / "feedback_data.json"

# API settings
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))

# Ensure data directory exists
DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
