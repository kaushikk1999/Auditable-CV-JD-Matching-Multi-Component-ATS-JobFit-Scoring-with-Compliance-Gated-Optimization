import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Project paths
BASE_DIR = Path(__file__).parent.parent
DATA_RAW_DIR = BASE_DIR / "data" / "raw"
DATA_PROCESSED_DIR = BASE_DIR / "data" / "processed"

# Ensure directories exist
DATA_RAW_DIR.mkdir(parents=True, exist_ok=True)
DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3-pro")

# Supported formats
SUPPORTED_CV_FORMATS = [".txt", ".docx", ".pdf"]

# Schema Version
SCHEMA_VERSION = "2.0"  # Phase 2 structured schemas

# Compliance Configuration Flags
ENFORCE_UNIQUE_WORDS = True
ENFORCE_STOPWORD_BAN = True
ENFORCE_BUZZWORD_BAN = True
UNIQUENESS_SCOPE = "entire_output"  # "entire_output" or "per_section"
STOPWORD_SCOPE = "entire_output"    # "entire_output" or "per_section"
CONTRACTION_EXPANSION = True
ALLOW_NUMERIC_REPETITION = True

# Target ranges
TARGET_WORD_COUNT_MIN = 400
TARGET_WORD_COUNT_MAX = 450
TARGET_BULLET_COUNT_MIN = 12
TARGET_BULLET_COUNT_MAX = 15
