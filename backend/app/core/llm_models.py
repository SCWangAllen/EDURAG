"""可選 LLM 模型清單與「目前使用模型」的解析。

- MODEL_ALLOWLIST:精選 current-gen 模型(避免把過時模型倒給使用者)。
- list_models():真實模式試 Anthropic live 清單並用 allowlist 過濾;
  任何失敗(含舊 SDK 無 models 屬性、mock 模式)fallback 到精選硬清單。
- get_active_model(db):讀 app_settings['llm_model'],無值回設定預設。
"""
import json
import logging
import re
from typing import Dict, List, Optional

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
RECOMMENDED_KEY = "recommended_models"  # app_settings:JSON 陣列,使用者自訂的「建議」模型 ID
# 自訂輸入的模型 ID 格式(僅接受 Anthropic 的 claude-* 命名)
MODEL_ID_PATTERN = re.compile(r"^claude-[a-z0-9][a-z0-9.\-]*$")


def looks_like_model_id(model_id: str) -> bool:
    return bool(model_id) and bool(MODEL_ID_PATTERN.match(model_id))


def is_allowed_model(model_id: str) -> bool:
    """model_id 是否在精選 allowlist 內。

    接受兩種形式:精選別名(claude-haiku-4-5),或其日期快照變體
    (claude-haiku-4-5-20251001)。有些帳號的 models.list() 只列出帶日期的 ID,
    下拉選單會直接送該 ID,故一併視為合法。
    """
    if model_id in _ALLOWED_IDS:
        return True
    return any(model_id.startswith(alias + "-") for alias in _ALLOWED_IDS)


async def _fetch_live_models() -> Optional[Dict[str, Dict[str, str]]]:
    """向 Anthropic 取帳號可用模型 {id: {display_name, created}};mock / 無 key / 失敗 → None。"""
    from app.core.config import ANTHROPIC_API_KEY, USE_MOCK_API

    if USE_MOCK_API or not ANTHROPIC_API_KEY:
        return None
    try:
        from anthropic import AsyncAnthropic

        client = AsyncAnthropic(api_key=ANTHROPIC_API_KEY)
        resp = await client.models.list(limit=100)
        return {
            m.id: {
                "display_name": getattr(m, "display_name", None) or m.id,
                "created": str(getattr(m, "created_at", None) or ""),
            }
            for m in resp.data
            if m.id.startswith("claude-")
        }
    except Exception as e:  # noqa: BLE001
        logger.warning("Anthropic models.list 失敗,改用精選硬清單: %s", e)
        return None


async def get_recommended_ids(db: Optional[AsyncSession]) -> List[str]:
    """使用者自訂的建議模型 ID(app_settings['recommended_models']);沒設定時用精選預設。"""
    if db is not None:
        from app.db.models import AppSetting

        result = await db.execute(select(AppSetting).where(AppSetting.key == RECOMMENDED_KEY))
        row = result.scalar_one_or_none()
        if row and row.value:
            try:
                ids = json.loads(row.value)
                if isinstance(ids, list):
                    return [str(i) for i in ids if i]
            except ValueError:
                logger.warning("recommended_models 內容不是合法 JSON,改用預設")
    return [m["id"] for m in MODEL_ALLOWLIST]


async def set_recommended_ids(db: AsyncSession, ids: List[str]) -> List[str]:
    """儲存建議模型 ID 清單(去重、保序);每個 ID 先經 validate_model。"""
    from app.db.models import AppSetting

    cleaned: List[str] = []
    for raw in ids:
        mid = (raw or "").strip()
        if not mid or mid in cleaned:
            continue
        await validate_model(mid)
        cleaned.append(mid)
    result = await db.execute(select(AppSetting).where(AppSetting.key == RECOMMENDED_KEY))
    row = result.scalar_one_or_none()
    value = json.dumps(cleaned)
    if row:
        row.value = value
    else:
        db.add(AppSetting(key=RECOMMENDED_KEY, value=value))
    await db.commit()
    return cleaned


async def list_models(db: Optional[AsyncSession] = None) -> List[Dict[str, str]]:
    """回傳可選模型清單,每項 {id, display_name, group}。

    group = "recommended":使用者自訂的建議清單(未設定時為精選預設),依清單順序;
    group = "other":帳號可用、但不在建議內的其他模型(新模型上線會自動出現)。
    真實模式問 Anthropic `models.list()`;失敗時只回建議清單。
    """
    recommended_ids = await get_recommended_ids(db)
    default_names = {m["id"]: m["display_name"] for m in MODEL_ALLOWLIST}
    live = await _fetch_live_models()

    def _match(alias: str):
        """建議 ID 是否在帳號可用清單:精確存在,或存在其日期快照變體。回傳實際 live id。"""
        if live is None:
            return alias
        if alias in live:
            return alias
        return next((lid for lid in live if lid.startswith(alias + "-")), None)

    recommended, used = [], set()
    for rid in recommended_ids:
        matched = _match(rid)
        if matched is None:
            # 帳號目前拿不到這個模型:仍列出,但註明,讓使用者知道要換掉
            recommended.append(
                {"id": rid, "alias": rid, "display_name": f"{rid}（帳號目前不可用）", "group": "recommended"}
            )
            continue
        used.add(matched)
        name = live[matched]["display_name"] if live else default_names.get(rid, rid)
        label = f"{name}（{matched}）" if live else name
        # id = 帳號實際可用的 ID(可能帶日期);alias = 建議清單裡存的原始 ID,前端用它比對 / 切換
        recommended.append({"id": matched, "alias": rid, "display_name": label, "group": "recommended"})

    if live is None:
        return recommended
    others = [
        {"id": lid, "display_name": f"{info['display_name']}（{lid}）", "group": "other"}
        for lid, info in live.items()
        if lid not in used
    ]
    others.sort(key=lambda x: live[x["id"]]["created"], reverse=True)
    return recommended + others


async def validate_model(model_id: str) -> None:
    """檢查模型 ID 可用,不可用時 raise ValueError(訊息給前端顯示)。

    - 格式必須是 claude-*;
    - 精選 allowlist 內直接通過;
    - 其他 ID(自訂輸入)在真實模式向 Anthropic `models.retrieve()` 確認存在且帳號可用;
      mock 模式或無 API key 時只檢查格式。
    """
    from app.core.config import ANTHROPIC_API_KEY, USE_MOCK_API

    if not looks_like_model_id(model_id):
        raise ValueError(f"模型 ID 格式不正確：{model_id}（應為 claude-... 形式）")
    if is_allowed_model(model_id):
        return
    if USE_MOCK_API or not ANTHROPIC_API_KEY:
        return
    try:
        import anthropic
        from anthropic import AsyncAnthropic

        client = AsyncAnthropic(api_key=ANTHROPIC_API_KEY)
        await client.models.retrieve(model_id)
    except anthropic.NotFoundError:
        raise ValueError(f"Anthropic 找不到模型：{model_id}，請確認 ID 是否正確")
    except Exception as e:  # noqa: BLE001
        raise ValueError(f"無法向 Anthropic 驗證模型 {model_id}：{e}")


async def get_active_model(db: AsyncSession) -> str:
    """目前使用中的模型:讀 app_settings['llm_model'],無值回設定預設。"""
    from app.db.models import AppSetting

    result = await db.execute(select(AppSetting).where(AppSetting.key == SETTING_KEY))
    row = result.scalar_one_or_none()
    if row and row.value:
        return row.value
    return LLM_MODEL_NAME or DEFAULT_MODEL
