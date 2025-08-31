import logging
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_
from sqlalchemy.exc import IntegrityError

from app.db.models import Subject, Template
from app.schemas.subject import SubjectCreate, SubjectUpdate

logger = logging.getLogger(__name__)


class SubjectService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_subjects(self, include_inactive: bool = False) -> List[Subject]:
        """取得科目清單"""
        query = select(Subject).order_by(Subject.name)
        
        if not include_inactive:
            query = query.where(Subject.is_active == True)
            
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_subject_by_id(self, subject_id: int) -> Optional[Subject]:
        """根據ID取得科目"""
        query = select(Subject).where(Subject.id == subject_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_subject_by_name(self, name: str) -> Optional[Subject]:
        """根據名稱取得科目"""
        query = select(Subject).where(Subject.name == name.strip())
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_subject(self, subject_data: SubjectCreate) -> Subject:
        """建立科目"""
        # 檢查名稱是否已存在
        existing = await self.get_subject_by_name(subject_data.name)
        if existing:
            raise ValueError(f"科目 '{subject_data.name}' 已存在")

        subject = Subject(
            name=subject_data.name.strip(),
            description=subject_data.description,
            color=subject_data.color
        )

        self.db.add(subject)
        await self.db.commit()
        await self.db.refresh(subject)
        
        logger.info(f"建立科目: {subject.name}")
        return subject

    async def update_subject(
        self, 
        subject_id: int, 
        subject_data: SubjectUpdate
    ) -> Optional[Subject]:
        """更新科目"""
        subject = await self.get_subject_by_id(subject_id)
        if not subject:
            return None

        update_data = subject_data.dict(exclude_unset=True)
        
        # 檢查名稱衝突
        if 'name' in update_data:
            update_data['name'] = update_data['name'].strip()
            existing = await self.get_subject_by_name(update_data['name'])
            if existing and existing.id != subject_id:
                raise ValueError(f"科目 '{update_data['name']}' 已存在")

        if update_data:
            query = (
                update(Subject)
                .where(Subject.id == subject_id)
                .values(**update_data)
            )
            await self.db.execute(query)
            await self.db.commit()
            await self.db.refresh(subject)
            
            logger.info(f"更新科目: {subject.name}")
        
        return subject

    async def delete_subject(self, subject_id: int, force: bool = False) -> bool:
        """刪除科目（軟刪除或強制刪除）"""
        subject = await self.get_subject_by_id(subject_id)
        if not subject:
            return False

        # 檢查是否有模板在使用此科目
        templates_count = await self._count_templates_using_subject(subject.name)
        
        if templates_count > 0 and not force:
            raise ValueError(f"無法刪除科目 '{subject.name}'，有 {templates_count} 個模板正在使用")

        if force:
            # 強制刪除：直接從資料庫移除
            query = delete(Subject).where(Subject.id == subject_id)
            await self.db.execute(query)
        else:
            # 軟刪除：設為非活躍
            query = (
                update(Subject)
                .where(Subject.id == subject_id)
                .values(is_active=False)
            )
            await self.db.execute(query)
        
        await self.db.commit()
        
        logger.info(f"{'強制' if force else '軟'}刪除科目: {subject.name}")
        return True

    async def _count_templates_using_subject(self, subject_name: str) -> int:
        """計算使用特定科目的模板數量"""
        query = select(Template).where(
            and_(
                Template.subject == subject_name,
                Template.is_active == True
            )
        )
        result = await self.db.execute(query)
        return len(result.scalars().all())

    async def get_subject_usage_stats(self) -> dict:
        """取得科目使用統計"""
        subjects = await self.get_subjects()
        stats = {}
        
        for subject in subjects:
            template_count = await self._count_templates_using_subject(subject.name)
            stats[subject.name] = {
                'id': subject.id,
                'template_count': template_count,
                'color': subject.color
            }
        
        return stats