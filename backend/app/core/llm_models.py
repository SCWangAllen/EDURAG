"""可選 LLM 模型清單與「目前使用模型」的解析。

- MODEL_ALLOWLIST:精選 current-gen 模型(避免把過時模型倒給使用者)。
- list_models():真實模式試 Anthropic live 清單並用 allowlist 過濾;
  任何失敗(含舊 SDK 無 models 屬性、mock 模式)fallback 到精選硬清單。
- get_active_model(db):讀 app_settings['llm_model'],無值回設定預設。
"""
import logging
from typing import Dict, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import LLM_MODEL_NAME

logger = logging.getLogger(__name__)

# 精選可選模型(id + 顯示名)。只暴露 current-gen。
MODEL_ALLOWLIST: List[Dict[str, str]] = [
    {"id": "claude-opus-4-8", "display_name": "Claude Opus 4.8"},
    {"id": "claude-sonnet-5", "display_name": "Claude Sonnet 5"},
    {"id": "claude-haiku-4-5", "display_name": "Claude Haiku 4.5"},
    {"id": "claude-opus-4-7", "display_name": "Claude Opus 4.7"},
    {"id": "claude-sonnet-4-6", "display_name": "Claude Sonnet 4.6"},
]
_ALLOWED_IDS = {m["id"] for m in MODEL_ALLOWLIST}

DEFAULT_MODEL = "claude-opus-4-8"
SETTING_KEY = "llm_model"


def is_allowed_model(model_id: str) -> bool:
    """model_id 是否在精選 allowlist 內。"""
    return model_id in _ALLOWED_IDS


async def list_models() -> List[Dict[str, str]]:
    """回傳可選模型清單。

    真實模式:試 Anthropic `models.list()`,只保留同時在 allowlist 且帳號可存取的;
    顯示名優先用官方 display_name。任何例外(舊 SDK、網路、mock)→ 精選硬清單。
    """
    from app.core.config import ANTHROPIC_API_KEY, USE_MOCK_API

    if USE_MOCK_API or not ANTHROPIC_API_KEY:
        return [dict(m) for m in MODEL_ALLOWLIST]

    try:
        from anthropic import AsyncAnthropic

        client = AsyncAnthropic(api_key=ANTHROPIC_API_KEY)
        resp = await client.models.list(limit=100)
        live = {m.id: getattr(m, "display_name", None) or m.id for m in resp.data}
        filtered = [
            {"id": m["id"], "display_name": live.get(m["id"], m["display_name"])}
            for m in MODEL_ALLOWLIST
            if m["id"] in live
        ]
        return filtered or [dict(m) for m in MODEL_ALLOWLIST]
    except Exception as e:  # noqa: BLE001 - 任何錯誤都退回精選硬清單
        logger.warning("Anthropic models.list 失敗,改用精選硬清單: %s", e)
        return [dict(m) for m in MODEL_ALLOWLIST]


async def get_active_model(db: AsyncSession) -> str:
    """目前使用中的模型:讀 app_settings['llm_model'],無值回設定預設。"""
    from app.db.models import AppSetting

    result = await db.execute(select(AppSetting).where(AppSetting.key == SETTING_KEY))
    row = result.scalar_one_or_none()
    if row and row.value:
        return row.value
    return LLM_MODEL_NAME or DEFAULT_MODEL
