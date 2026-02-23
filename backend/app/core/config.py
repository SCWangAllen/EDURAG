from dotenv import load_dotenv, find_dotenv
import os

# 自動尋找並載入專案根目錄的 .env
load_dotenv(find_dotenv())

DATABASE_URL = os.getenv("DATABASE_URL")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
LLM_PROVIDER = "anthropic"  # 只支持 Claude
USE_MOCK_API = os.getenv("USE_MOCK_API", "false").lower() in ("1", "true", "yes")

# CORS 允許來源（逗號分隔），預設本機開發 + Docker 部署
_DEFAULT_ORIGINS = (
    "http://localhost:5173,http://localhost:5174,"
    "http://127.0.0.1:5173,http://127.0.0.1:5174,"
    "http://localhost:8989,http://127.0.0.1:8989"
)
CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", _DEFAULT_ORIGINS).split(",")
    if origin.strip()
]

# ---------- Application constants ----------
# Retrieval
RETRIEVAL_TOP_K = int(os.getenv("RETRIEVAL_TOP_K", "8"))
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.1"))

# Text chunking
DEFAULT_CHUNK_SIZE = int(os.getenv("DEFAULT_CHUNK_SIZE", "300"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))
UPLOAD_CHUNK_SIZE = int(os.getenv("UPLOAD_CHUNK_SIZE", "500"))

# LLM
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "claude-3-7-sonnet-20250219")

# Image questions
IMAGES_BASE_DIR = os.getenv("IMAGES_BASE_DIR", "/app/data/images")
QUESTION_IMAGES_DIR = os.getenv("QUESTION_IMAGES_DIR", f"{IMAGES_BASE_DIR}/questions")
ANSWER_IMAGES_DIR = os.getenv("ANSWER_IMAGES_DIR", f"{IMAGES_BASE_DIR}/answers")

if not USE_MOCK_API and not DATABASE_URL:
    raise RuntimeError("請先在 .env 設定 DATABASE_URL，再啟動服務。")

if not USE_MOCK_API and not ANTHROPIC_API_KEY:
    raise RuntimeError("請先在 .env 設定 ANTHROPIC_API_KEY。")