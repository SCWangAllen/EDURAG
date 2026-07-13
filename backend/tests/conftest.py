import os

# 測試套件一律走 Mock 模式（不需 DB/LLM）。
# 必須「強制賦值」而非 setdefault：某些全域 pytest 插件（如 deepeval）會在
# conftest 之前就 load_dotenv() 把 .env 的 USE_MOCK_API=false 灌進環境。
# 此設定必須在任何 app 模組被 import 之前生效。
os.environ["USE_MOCK_API"] = "true"
