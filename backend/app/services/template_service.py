from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, or_, case
from sqlalchemy.orm import selectinload
from app.db.models import Template, Subject
from app.schemas.template import TemplateCreate, TemplateUpdate, DEFAULT_TEMPLATES
from app.core.subject_norm import GRADE_SORT_INDEX, VALID_GRADES, normalize_subject
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


def build_template_subject_filter(subject: str):
    """建立模板科目篩選條件（供 get_templates / get_templates_count 共用，避免漂移）。

    正規化後大小寫/前後空白不敏感比對 Template.subject 舊欄位；
    同時比對關聯 Subject.name（initialize_default_templates 建立的模板沒有
    subject_id，仍可靠 subject 文字欄位命中）。
    """
    normalized = normalize_subject(subject)
    norm_lower = normalized.lower()
    return or_(
        func.lower(func.trim(Template.subject)) == norm_lower,
        Template.subject_obj.has(func.lower(func.trim(Subject.name)) == norm_lower),
    )

class TemplateService:
    def __init__(self, db: AsyncSession):
        self.db = db

    def _apply_filters(self, query, subject: Optional[str], grade: Optional[str], search: Optional[str]):
        """套用 subject/grade/search 篩選條件；get_templates 與 get_templates_count 共用一份，避免漂移。"""
        if subject:
            query = query.where(build_template_subject_filter(subject))

        if grade:
            # 篩選 grades JSON 欄位包含指定年級的模板
            # PostgreSQL JSON 操作：檢查陣列是否包含指定值
            query = query.where(
                Template.grades.op('@>')(f'["{grade}"]')
            )

        if search:
            like = f"%{search}%"
            query = query.where(
                or_(Template.name.ilike(like), Template.content.ilike(like))
            )

        return query

    def _apply_sort(self, query, sort: str):
        """sort="newest" 依建立時間新到舊；預設 "grade" 依科目 → 年級 band 順序 → 名稱 → id 排序。"""
        if sort == "newest":
            return query.order_by(Template.created_at.desc())

        # 年級排序：grades 是 JSON 陣列（例如 ["G4"]，可能含多個年級代碼），取陣列第一個
        # 元素的文字值（jsonb ->> 0）依 VALID_GRADES 的 band 順序（ESL → 年級班 → 國中班
        # → ALL 最後）排序，取代過去的數字擷取（'JR4' 與 'G4' 取出的數字同為 4，會落在
        # 同一位置，band 順序會亂掉）。
        # 注意：`->> 0` 回傳的是 text，用「值比對」的 simple CASE（同 GRADE_SORT_INDEX 在
        # document_service/image_question_service 的用法）直接和 GRADE_SORT_INDEX 的字串
        # key 比對，不再需要 `@>` containment；containment 版本曾在此處把右側字面值以
        # VARCHAR 綁定，撞上 postgres 的 `jsonb @> character varying` 型別不符錯誤
        # （_apply_filters 的 grade 篩選仍用 `@>` 且運作正常，維持不動）。
        # 無任何已知代碼（例如陣列為空、第一個元素非白名單內的自訂值）排最後；
        # 最後補 id 讓完全同 key 時分頁結果穩定
        grade_rank = case(
            GRADE_SORT_INDEX, value=Template.grades.op('->>')(0), else_=len(VALID_GRADES)
        )
        return query.order_by(
            Template.subject.asc(),
            grade_rank.asc(),
            Template.name.asc(),
            Template.id.asc(),
        )

    async def get_templates(
        self,
        subject: Optional[str] = None,
        grade: Optional[str] = None,
        search: Optional[str] = None,
        sort: str = "grade",
        skip: int = 0,
        limit: int = 100
    ) -> List[Template]:
        """取得模板清單"""
        # 使用 selectinload 預載 subject 關聯
        query = select(Template).options(selectinload(Template.subject_obj)).where(Template.is_active == True)
        query = self._apply_filters(query, subject, grade, search)
        query = self._apply_sort(query, sort)
        query = query.offset(skip).limit(limit)

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
            question_type=template_data.question_type,  # 傳遞題型
            grades=template_data.grades or [],  # 適用年級列表
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

    async def get_templates_count(
        self,
        subject: Optional[str] = None,
        grade: Optional[str] = None,
        search: Optional[str] = None,
    ) -> int:
        """取得模板總數"""
        query = select(func.count(Template.id)).where(Template.is_active == True)
        query = self._apply_filters(query, subject, grade, search)

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

    async def initialize_default_templates(self) -> dict:
        """初始化預設模板（英文版）- 支援建立和更新

        Returns:
            dict: {"created": int, "updated": int} 建立和更新的模板數量
        """
        logger.info("Initializing default templates (English version)...")

        created_count = 0
        updated_count = 0

        try:
            for subject, question_types in DEFAULT_TEMPLATES.items():
                for question_type, template_config in question_types.items():
                    # 英文命名格式：Health_single_choice_Template
                    template_name = f"{subject}_{question_type}_Template"

                    # 檢查是否已存在
                    existing_query = select(Template).where(
                        Template.subject == subject,
                        Template.name == template_name,
                        Template.is_active == True
                    )
                    result = await self.db.execute(existing_query)
                    existing = result.scalar_one_or_none()

                    expected_question_type = template_config.get("question_type", question_type)

                    if existing:
                        # 檢查是否需要更新（修復舊模板缺少 question_type 的問題）
                        needs_update = (
                            existing.question_type != expected_question_type or
                            existing.content != template_config["content"]
                        )

                        if needs_update:
                            existing.question_type = expected_question_type
                            existing.content = template_config["content"]
                            existing.params = template_config.get("params", {})
                            updated_count += 1
                            logger.info(f"Updated template: {template_name} (type: {expected_question_type})")
                        else:
                            logger.debug(f"Template already up-to-date: {template_name}")
                    else:
                        # 建立新模板
                        template = Template(
                            subject=subject,
                            name=template_name,
                            content=template_config["content"],
                            question_type=expected_question_type,
                            params=template_config.get("params", {})
                        )
                        self.db.add(template)
                        created_count += 1
                        logger.info(f"Created default template: {template_name} (type: {expected_question_type})")

            await self.db.commit()
            logger.info(f"Default templates initialized: {created_count} created, {updated_count} updated")
            return {"created": created_count, "updated": updated_count}

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to initialize default templates: {str(e)}")
            raise

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
        search: Optional[str] = None,
        sort: str = "grade",
        skip: int = 0,
        limit: int = 100
    ) -> List[dict]:
        templates = [t for t in self.templates if t["is_active"] == True]

        if subject:
            templates = [t for t in templates if t["subject"] == subject]

        if search:
            needle = search.lower()
            templates = [
                t for t in templates
                if needle in t["name"].lower() or needle in t["content"].lower()
            ]

        if sort == "newest":
            templates = sorted(templates, key=lambda t: t["created_at"], reverse=True)
        else:
            templates = sorted(templates, key=lambda t: (t["subject"], t["name"]))

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

    async def get_templates_count(
        self, subject: Optional[str] = None, search: Optional[str] = None
    ) -> int:
        templates = [t for t in self.templates if t["is_active"] == True]
        if subject:
            templates = [t for t in templates if t["subject"] == subject]
        if search:
            needle = search.lower()
            templates = [
                t for t in templates
                if needle in t["name"].lower() or needle in t["content"].lower()
            ]
        return len(templates)

    async def get_subjects(self) -> List[str]:
        subjects = set()
        for template in self.templates:
            if template["is_active"] == True:
                subjects.add(template["subject"])
        return sorted(list(subjects))