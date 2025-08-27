from dotenv import load_dotenv, find_dotenv
import os

# 自動尋找並載入專案根目錄的 .env
load_dotenv(find_dotenv())

DATABASE_URL = os.getenv("DATABASE_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
USE_MOCK_API = os.getenv("USE_MOCK_API", "false").lower() in ("1", "true", "yes")

if not USE_MOCK_API and not DATABASE_URL:
    raise RuntimeError("請先在 .env 設定 DATABASE_URL，再啟動服務。")