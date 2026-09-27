from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, or_, case
from sqlalchemy.orm import selectinload
from app.db.models import Template, Subject
from app.schemas.template import TemplateCreate, TemplateUpdate, DEFAULT_TEMPLATES
from app.core.subject_norm import GRADE_SORT_INDEX, VALID_GRADES, normalize_subject
from collections.abc import Sequence
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

# 手動排序基準間距:凍結順序時 sort_order = index * _MANUAL_SORT_STEP,兩兩之間
# 留出空隙,理論上可支援之後「插入」而不必整批重排(目前 move 只用上移/下移
# 兩兩互換,還用不到插入,但間距留著成本為零)。
_MANUAL_SORT_STEP = 10


def plan_move(
    ordered: Sequence[tuple[int, Optional[int]]],
    template_id: int,
    direction: str,
) -> tuple[list[tuple[int, int]], bool, Optional[int]]:
    """純函式:規劃「上移/下移一格」要寫回 DB 的 sort_order。

    ordered:目前手動排序下的 (id, sort_order) 序列，呼叫端已依
    `sort_order ASC NULLS LAST, created_at DESC, id ASC` 查好順序（此函式
    不知道 created_at，只依傳入順序運作）。

    若序列中任一 sort_order 為 None，先依目前順序指派 index * 10（把目前
    順序「凍結」下來），再處理 up/down 的兩兩互換；在邊界（最上/最下）
    不交換、也不寫入任何資料，moved=False。

    回傳 (要寫回 DB 的 (id, sort_order) 更新清單, moved, template_id 最終的 sort_order)。
    """
    ids = [i for i, _ in ordered]
    if template_id not in ids:
        raise ValueError(f"template_id {template_id} not in ordered list")

    needs_freeze = any(sort_order is None for _, sort_order in ordered)
    sort_orders = (
        [idx * _MANUAL_SORT_STEP for idx in range(len(ordered))]
        if needs_freeze
        else [sort_order for _, sort_order in ordered]
    )

    idx = ids.index(template_id)
    swap_idx = idx - 1 if direction == "up" else idx + 1
    moved = 0 <= swap_idx < len(ids)

    updates: dict[int, int] = {}
    if moved:
        if needs_freeze:
            # 第一次真的移動時才把目前順序凍結下來;在邊界按鍵不寫任何資料
            updates = dict(zip(ids, sort_orders))
        a_id, b_id = ids[idx], ids[swap_idx]
        a_val, b_val = sort_orders[idx], sort_orders[swap_idx]
        updates[a_id] = b_val
        updates[b_id] = a_val
        final_sort_order = b_val
    else:
        final_sort_order = sort_orders[idx]

    return list(updates.items()), moved, final_sort_order


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
        """sort="newest" 依建立時間新到舊；sort="manual" 依老師手動排序（見 move_template）；
        預設 "grade" 依科目 → 年級 band 順序 → 名稱 → id 排序。"""
        if sort == "newest":
            return query.order_by(Template.created_at.desc())

        if sort == "manual":
            # 尚未凍結（sort_order 為 NULL）的模板排最後，同批用建立時間新到舊、
            # 再用 id 當最終 tie-break，與 move_template 查詢排序規則一致。
            return query.order_by(
                Template.sort_order.asc().nulls_last(),
                Template.created_at.desc(),
                Template.id.asc(),
            )

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

    async def move_template(self, template_id: int, direction: str) -> Optional[dict]:
        """手動排序上移/下移一格（見 plan_move）。

        回傳 None 表示模板不存在或非啟用中（router 轉 404）；
        否則回傳 {"moved": bool, "sort_order": 最終 sort_order}。
        凍結 + 互換在同一個交易內完成。
        """
        query = (
            select(Template.id, Template.sort_order)
            .where(Template.is_active.is_(True))
            .order_by(
                Template.sort_order.asc().nulls_last(),
                Template.created_at.desc(),
                Template.id.asc(),
            )
        )
        result = await self.db.execute(query)
        ordered = [(row.id, row.sort_order) for row in result.all()]

        if template_id not in [tid for tid, _ in ordered]:
            return None

        updates, moved, final_sort_order = plan_move(ordered, template_id, direction)

        if updates:
            try:
                for tid, new_sort_order in updates:
                    await self.db.execute(
                        update(Template)
                        .where(Template.id == tid)
                        .values(sort_order=new_sort_order)
                    )
                await self.db.commit()
            except Exception:
                await self.db.rollback()
                raise

        logger.info(
            "Move template %d %s: moved=%s sort_order=%s",
            template_id, direction, moved, final_sort_order,
        )
        return {"moved": moved, "sort_order": final_sort_order}

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
                    "sort_order": None,
                    "created_at": "2024-01-01T00:00:00Z",
                    "updated_at": "2024-01-01T00:00:00Z"
                })
                self.next_id += 1

    @staticmethod
    def _manual_order(templates: list[dict]) -> list[dict]:
        """依 sort_order ASC NULLS LAST, created_at DESC, id ASC 排序（與真實版對齊）。

        用三次穩定排序由最不重要到最重要的鍵疊代，等同一次多鍵排序。
        """
        ordered = sorted(templates, key=lambda t: t["id"])
        ordered = sorted(ordered, key=lambda t: t["created_at"], reverse=True)
        ordered = sorted(
            ordered, key=lambda t: (t.get("sort_order") is None, t.get("sort_order") or 0)
        )
        return ordered

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
        elif sort == "manual":
            templates = self._manual_order(templates)
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
            "sort_order": None,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }
        self.templates.append(template)
        self.next_id += 1
        return template

    async def move_template(self, template_id: int, direction: str) -> Optional[dict]:
        """上移/下移一格（Mock 版；規則與 TemplateService.move_template 對齊）。"""
        active = [t for t in self.templates if t["is_active"]]
        ordered = self._manual_order(active)
        ids = [t["id"] for t in ordered]

        if template_id not in ids:
            return None

        pairs = [(t["id"], t.get("sort_order")) for t in ordered]
        updates, moved, final_sort_order = plan_move(pairs, template_id, direction)

        if updates:
            by_id = {t["id"]: t for t in self.templates}
            for tid, new_sort_order in updates:
                by_id[tid]["sort_order"] = new_sort_order

        return {"moved": moved, "sort_order": final_sort_order}

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