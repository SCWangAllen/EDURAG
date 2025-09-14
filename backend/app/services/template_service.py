from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from sqlalchemy.orm import selectinload
from app.db.models import Template, Subject
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
        # 使用 selectinload 預載 subject 關聯
        query = select(Template).options(selectinload(Template.subject_obj)).where(Template.is_active == True)
        
        if subject:
            # 支持同時查詢舊欄位和新關聯
            query = query.where(
                (Template.subject == subject) | 
                (Template.subject_obj.has(Subject.name == subject))
            )
            
        query = query.offset(skip).limit(limit).order_by(Template.created_at.desc())
        
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_template_by_id(self, template_id: int) -> Optional[Template]:
        """依 ID 取得模板"""
        query = select(Template).options(selectinload(Template.subject_obj)).where(
            Template.id == template_id,
            Template.is_active == True
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_template(self, template_data: TemplateCreate) -> Template:
        """建立新模板"""
        logger.info(f"Creating template with subject_id: {template_data.subject_id}")
        
        # 驗證必要欄位
        if not template_data.name:
            raise ValueError("模板名稱不能為空")
        if not template_data.content:
            raise ValueError("模板內容不能為空")
        if not template_data.subject_id:
            raise ValueError("必須選擇科目")
        
        # 檢查 subject_id 是否存在，並取得科目名稱
        subject_name = None
        if template_data.subject_id:
            subject_query = select(Subject).where(Subject.id == template_data.subject_id)
            result = await self.db.execute(subject_query)
            subject = result.scalar_one_or_none()
            
            if not subject:
                raise ValueError(f"科目 ID {template_data.subject_id} 不存在")
            
            subject_name = subject.name
        
        # 使用 subject_name 或 fallback 到 template_data.subject
        final_subject = subject_name or template_data.subject
        
        if not final_subject:
            raise ValueError("無法確定科目名稱")
        
        template = Template(
            subject_id=template_data.subject_id,
            subject=final_subject,  # 使用查詢到的科目名稱
            name=template_data.name,
            content=template_data.content,
            params=template_data.params or {}
        )
        
        try:
            self.db.add(template)
            await self.db.commit()
            await self.db.refresh(template)
            
            # 預載關聯資料
            if template.subject_id:
                await self.db.refresh(template, ['subject_obj'])
            
            logger.info(f"Created template: {template.name} for subject: {template.subject_name}")
            return template
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Database error creating template: {str(e)}")
            raise

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
            # 如果更新了 subject_id，也需要同步更新 subject 欄位
            if 'subject_id' in update_data and update_data['subject_id']:
                from app.db.models import Subject
                subject_query = select(Subject).where(Subject.id == update_data['subject_id'])
                subject_result = await self.db.execute(subject_query)
                subject = subject_result.scalar_one_or_none()
                if subject:
                    update_data['subject'] = subject.name
            
            query = (
                update(Template)
                .where(Template.id == template_id)
                .values(**update_data)
            )
            await self.db.execute(query)
            await self.db.commit()
            
            # 重新查詢模板以載入最新資料
            template = await self.get_template_by_id(template_id)
            
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
            .values(is_active=False)
        )
        await self.db.execute(query)
        await self.db.commit()
        
        logger.info(f"Deleted template: {template.name}")
        return True

    async def get_templates_count(self, subject: Optional[str] = None) -> int:
        """取得模板總數"""
        query = select(func.count(Template.id)).where(Template.is_active == True)
        
        if subject:
            query = query.where(Template.subject == subject)
            
        result = await self.db.execute(query)
        return result.scalar()

    async def get_subjects(self) -> List[str]:
        """取得所有科目清單"""
        query = (
            select(Template.subject)
            .where(Template.is_active == True)
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
                    Template.is_active == True
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
                    "is_active": True,
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
        templates = [t for t in self.templates if t["is_active"] == True]
        
        if subject:
            templates = [t for t in templates if t["subject"] == subject]
            
        return templates[skip:skip+limit]

    async def get_template_by_id(self, template_id: int) -> Optional[dict]:
        for template in self.templates:
            if template["id"] == template_id and template["is_active"] == True:
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
            "is_active": True,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }
        self.templates.append(template)
        self.next_id += 1
        return template

    async def get_templates_count(self, subject: Optional[str] = None) -> int:
        templates = [t for t in self.templates if t["is_active"] == True]
        if subject:
            templates = [t for t in templates if t["subject"] == subject]
        return len(templates)

    async def get_subjects(self) -> List[str]:
        subjects = set()
        for template in self.templates:
            if template["is_active"] == True:
                subjects.add(template["subject"])
        return sorted(list(subjects))