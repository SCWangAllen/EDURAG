from dotenv import load_dotenv, find_dotenv
import os

# 自動尋找並載入專案根目錄的 .env
load_dotenv(find_dotenv())

DATABASE_URL = os.getenv("DATABASE_URL")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
LLM_PROVIDER = "anthropic"  # 只支持 Claude
USE_MOCK_API = os.getenv("USE_MOCK_API", "false").lower() in ("1", "true", "yes")

if not USE_MOCK_API and not DATABASE_URL:
    raise RuntimeError("請先在 .env 設定 DATABASE_URL，再啟動服務。")

if not USE_MOCK_API and not ANTHROPIC_API_KEY:
    raise RuntimeError("請先在 .env 設定 ANTHROPIC_API_KEY。")