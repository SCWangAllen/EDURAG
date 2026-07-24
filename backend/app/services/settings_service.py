"""全域設定 Service — 目前管理生成使用的 LLM 模型。"""
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.llm_models import SETTING_KEY, get_active_model, is_allowed_model
from app.db.models import AppSetting

logger = logging.getLogger(__name__)


class SettingsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_model(self) -> str:
        """目前使用中的模型(無設定時回預設)。"""
        return await get_active_model(self.db)

    async def set_model(self, model_id: str) -> str:
        """設定生成模型。model_id 必須在精選 allowlist 內,否則 raise ValueError。"""
        model_id = (model_id or "").strip()
        if not is_allowed_model(model_id):
            raise ValueError(f"不支援的模型：{model_id}")

        result = await self.db.execute(
            select(AppSetting).where(AppSetting.key == SETTING_KEY)
        )
        row = result.scalar_one_or_none()
        if row:
            row.value = model_id
        else:
            self.db.add(AppSetting(key=SETTING_KEY, value=model_id))
        await self.db.commit()
        logger.info("生成模型已切換為 %s", model_id)
        return model_id
