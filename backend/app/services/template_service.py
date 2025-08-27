from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from sqlalchemy.orm import selectinload
from app.db.models import Template
from app.schemas.template import TemplateCreate, TemplateUpdate, DEFAULT_TEMPLATES
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

class TemplateService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_templates(
        self, 
        subject: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Template]:
        """取得模板清單"""
        query = select(Template).where(Template.is_active == 'true')
        
        if subject:
            query = query.where(Template.subject == subject)
            
        query = query.offset(skip).limit(limit).order_by(Template.created_at.desc())
        
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_template_by_id(self, template_id: int) -> Optional[Template]:
        """依 ID 取得模板"""
        query = select(Template).where(
            Template.id == template_id,
            Template.is_active == 'true'
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_template(self, template_data: TemplateCreate) -> Template:
        """建立新模板"""
        template = Template(
            subject=template_data.subject,
            name=template_data.name,
            content=template_data.content,
            params=template_data.params or {}
        )
        
        self.db.add(template)
        await self.db.commit()
        await self.db.refresh(template)
        
        logger.info(f"Created template: {template.name} for subject: {template.subject}")
        return template

    async def update_template(
        self, 
        template_id: int, 
        template_data: TemplateUpdate
    ) -> Optional[Template]:
        """更新模板"""
        template = await self.get_template_by_id(template_id)
        if not template:
            return None

        update_data = template_data.dict(exclude_unset=True)
        if update_data:
            query = (
                update(Template)
                .where(Template.id == template_id)
                .values(**update_data)
            )
            await self.db.execute(query)
            await self.db.commit()
            await self.db.refresh(template)
            
            logger.info(f"Updated template: {template.name}")
        
        return template

    async def delete_template(self, template_id: int) -> bool:
        """軟刪除模板"""
        template = await self.get_template_by_id(template_id)
        if not template:
            return False

        query = (
            update(Template)
            .where(Template.id == template_id)
            .values(is_active='false')
        )
        await self.db.execute(query)
        await self.db.commit()
        
        logger.info(f"Deleted template: {template.name}")
        return True

    async def get_templates_count(self, subject: Optional[str] = None) -> int:
        """取得模板總數"""
        query = select(func.count(Template.id)).where(Template.is_active == 'true')
        
        if subject:
            query = query.where(Template.subject == subject)
            
        result = await self.db.execute(query)
        return result.scalar()

    async def get_subjects(self) -> List[str]:
        """取得所有科目清單"""
        query = (
            select(Template.subject)
            .where(Template.is_active == 'true')
            .distinct()
            .order_by(Template.subject)
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def initialize_default_templates(self):
        """初始化預設模板"""
        logger.info("Initializing default templates...")
        
        for subject, question_types in DEFAULT_TEMPLATES.items():
            for question_type, template_config in question_types.items():
                # 檢查是否已存在
                existing_query = select(Template).where(
                    Template.subject == subject,
                    Template.name == f"{subject}_{question_type}_預設模板",
                    Template.is_active == 'true'
                )
                existing = await self.db.execute(existing_query)
                
                if not existing.scalar_one_or_none():
                    template = Template(
                        subject=subject,
                        name=f"{subject}_{question_type}_預設模板",
                        content=template_config["content"],
                        params=template_config["params"]
                    )
                    self.db.add(template)
                    logger.info(f"Created default template: {template.name}")
        
        await self.db.commit()
        logger.info("Default templates initialized successfully")

# Mock 版本
class MockTemplateService:
    """Mock 模板服務，用於測試"""
    
    def __init__(self):
        self.templates = []
        self.next_id = 1
        
        # 初始化 Mock 資料
        for subject, question_types in DEFAULT_TEMPLATES.items():
            for question_type, template_config in question_types.items():
                self.templates.append({
                    "id": self.next_id,
                    "subject": subject,
                    "name": f"{subject}_{question_type}_預設模板",
                    "content": template_config["content"],
                    "params": template_config["params"],
                    "version": 1,
                    "is_active": "true",
                    "created_at": "2024-01-01T00:00:00Z",
                    "updated_at": "2024-01-01T00:00:00Z"
                })
                self.next_id += 1

    async def get_templates(
        self, 
        subject: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[dict]:
        templates = [t for t in self.templates if t["is_active"] == "true"]
        
        if subject:
            templates = [t for t in templates if t["subject"] == subject]
            
        return templates[skip:skip+limit]

    async def get_template_by_id(self, template_id: int) -> Optional[dict]:
        for template in self.templates:
            if template["id"] == template_id and template["is_active"] == "true":
                return template
        return None

    async def create_template(self, template_data: dict) -> dict:
        template = {
            "id": self.next_id,
            "subject": template_data["subject"],
            "name": template_data["name"],
            "content": template_data["content"],
            "params": template_data.get("params", {}),
            "version": 1,
            "is_active": "true",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }
        self.templates.append(template)
        self.next_id += 1
        return template

    async def get_templates_count(self, subject: Optional[str] = None) -> int:
        templates = [t for t in self.templates if t["is_active"] == "true"]
        if subject:
            templates = [t for t in templates if t["subject"] == subject]
        return len(templates)

    async def get_subjects(self) -> List[str]:
        subjects = set()
        for template in self.templates:
            if template["is_active"] == "true":
                subjects.add(template["subject"])
        return sorted(list(subjects))