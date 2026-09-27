import logging
from app.core.subject_colors import is_unassigned_color, pick_subject_color
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_, func
from sqlalchemy.exc import IntegrityError

from app.db.models import Subject, Template
from app.schemas.subject import SubjectCreate, SubjectUpdate
from app.core.subject_norm import GRADE_WILDCARD, VALID_GRADES

logger = logging.getLogger(__name__)

# 年級排序權重：這裡刻意讓 ALL（全年級通用）排最前——這是科目管理樹狀 UI 既有的顯示慣例
# （教師編輯科目年級時預期先看到「全年級」這個選項），與 subject_norm.grade_sort_key()
# 用於文件/範本/圖片題目清單排序時「ALL 排最後」的慣例不同，兩者服務不同的畫面，刻意不合併。
# 已知年級代碼（K1/K2/A1/A2、G1–G6、JR4–JR9）沿用 subject_norm 的 band 順序；自訂值殿後。
_GRADE_ORDER = {GRADE_WILDCARD: 0}
_GRADE_ORDER.update(
    {code: idx + 1 for idx, code in enumerate(VALID_GRADES) if code != GRADE_WILDCARD}
)


def build_subject_tree(subjects) -> List[dict]:
    """把 (name, grade) 平面科目列聚合成 科目→年級 樹。

    純函式（不觸 DB），供 service 與測試共用。
    color 取同名第一列；grades 依 ALL, G1..G6, 自訂值排序。
    """
    nodes: dict = {}
    for s in subjects:
        node = nodes.setdefault(
            s.name, {"name": s.name, "color": s.color, "grades": []}
        )
        node["grades"].append({"id": s.id, "grade": (s.grade or "").strip()})

    for node in nodes.values():
        node["grades"].sort(
            key=lambda g: (_GRADE_ORDER.get(g["grade"], 99), g["grade"])
        )
    return sorted(nodes.values(), key=lambda n: n["name"])


class SubjectService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_subject_tree(self) -> List[dict]:
        """取得 科目→年級 樹（僅 is_active 科目）"""
        subjects = await self.get_subjects(include_inactive=False)
        return build_subject_tree(subjects)

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

    async def get_subject_by_name(self, name: str, grade: Optional[str] = None) -> Optional[Subject]:
        """根據名稱（和年級）取得科目"""
        query = select(Subject).where(Subject.name == name.strip())
        if grade is not None:
            query = query.where(Subject.grade == grade.strip() if grade else Subject.grade.is_(None))
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_subject_by_name_and_grade(self, name: str, grade: Optional[str]) -> Optional[Subject]:
        """根據名稱和年級組合取得科目（用於唯一性檢查）"""
        # 將 None 和空字串統一處理為空字串
        normalized_grade = (grade.strip() if grade else '') or ''
        query = select(Subject).where(
            Subject.name == name.strip(),
            Subject.grade == normalized_grade
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def _color_for_name(self, name: str) -> str:
        """同名科目的既有顏色;沒有就從調色盤挑目前最少科目在用的顏色。"""
        result = await self.db.execute(
            select(Subject.name, Subject.color).where(Subject.is_active.is_(True))
        )
        rows = result.all()
        for row_name, row_color in rows:
            if row_name == name and not is_unassigned_color(row_color):
                return row_color
        # 每個科目名稱只算一次,才不會多年級的科目把顏色計數灌水
        by_name: dict[str, str] = {}
        for row_name, row_color in rows:
            if row_name != name and not is_unassigned_color(row_color):
                by_name.setdefault(row_name, row_color)
        return pick_subject_color(by_name.values())

    async def create_subject(self, subject_data: SubjectCreate) -> Subject:
        """建立科目"""
        # 檢查 (name, grade) 組合是否已存在
        existing = await self.get_subject_by_name_and_grade(
            subject_data.name,
            subject_data.grade
        )
        if existing and existing.is_active:
            grade_info = f" ({subject_data.grade})" if subject_data.grade else ""
            raise ValueError(f"科目 '{subject_data.name}'{grade_info} 已存在")

        if existing:
            # 軟刪除留下的同名同年級列:復活並套用新資料,而不是回「已存在」
            existing.is_active = True
            existing.description = subject_data.description
            existing.color = subject_data.color
            await self.db.commit()
            await self.db.refresh(existing)
            logger.info(f"復活軟刪除科目: {existing.name} (年級: {existing.grade})")
            return existing

        # 將 None 和空字串統一處理為空字串，以符合唯一約束
        normalized_grade = (subject_data.grade.strip() if subject_data.grade else '') or ''

        # 顏色以科目名稱為單位:同名科目已有顏色就沿用;沒指定(或仍是預設藍)就從調色盤
        # 挑最少人用的,避免全部都是同一個藍色而看不出差別
        color = subject_data.color
        if is_unassigned_color(color):
            color = await self._color_for_name(subject_data.name.strip())

        subject = Subject(
            name=subject_data.name.strip(),
            description=subject_data.description,
            color=color,
            grade=normalized_grade
        )

        self.db.add(subject)
        await self.db.commit()
        await self.db.refresh(subject)

        logger.info(f"建立科目: {subject.name} (年級: {subject.grade})")
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

        # 檢查 (name, grade) 組合衝突
        new_name = update_data.get('name', subject.name)
        new_grade = update_data.get('grade', subject.grade)
        if 'name' in update_data:
            new_name = update_data['name'].strip()
            update_data['name'] = new_name
        if 'grade' in update_data:
            # 將 None 和空字串統一處理為空字串
            new_grade = (update_data['grade'].strip() if update_data['grade'] else '') or ''
            update_data['grade'] = new_grade

        # 只在 name 或 grade 有變更時檢查衝突
        if 'name' in update_data or 'grade' in update_data:
            existing = await self.get_subject_by_name_and_grade(new_name, new_grade)
            if existing and existing.id != subject_id:
                grade_info = f" ({new_grade})" if new_grade else ""
                raise ValueError(f"科目 '{new_name}'{grade_info} 已存在")

        if update_data:
            query = (
                update(Subject)
                .where(Subject.id == subject_id)
                .values(**update_data)
            )
            await self.db.execute(query)
            await self.db.commit()
            await self.db.refresh(subject)

            logger.info(f"更新科目: {subject.name} (年級: {subject.grade})")

        return subject

    async def delete_subject(self, subject_id: int, force: bool = False) -> bool:
        """刪除科目（軟刪除或強制刪除）"""
        subject = await self.get_subject_by_id(subject_id)
        if not subject:
            return False

        # 檢查是否有模板在使用此科目
        templates_count = await self._count_templates_using_subject(subject)
        
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

    @staticmethod
    def _is_subject_level(grade: Optional[str]) -> bool:
        """無年級或 ALL 視為「科目層級」列。"""
        return (grade or "").strip() in ("", "ALL")

    @staticmethod
    def template_usage_condition(subject: Subject):
        """範本「使用」此科目列的條件(純函式,供測試)。

        - 新範本:templates.subject_id == 該列 id
        - 舊範本(subject_id 為 NULL、只存名稱):只歸屬同名的科目層級列。
          若也歸到各年級列,新增的年級會被同名範本牽連而永遠刪不掉。
        """
        cond = Template.subject_id == subject.id
        if SubjectService._is_subject_level(subject.grade):
            cond = or_(
                cond,
                and_(Template.subject_id.is_(None), Template.subject == subject.name),
            )
        return and_(cond, Template.is_active.is_(True))

    async def _count_templates_using_subject(self, subject: Subject) -> int:
        """計算使用此科目列的啟用中範本數量"""
        query = (
            select(func.count())
            .select_from(Template)
            .where(self.template_usage_condition(subject))
        )
        result = await self.db.execute(query)
        return int(result.scalar() or 0)

    async def get_subject_usage_stats(self) -> dict:
        """取得科目使用統計"""
        subjects = await self.get_subjects()
        stats = {}
        
        for subject in subjects:
            template_count = await self._count_templates_using_subject(subject)
            # 以列 id 當 key:同名不同年級各自一筆(以名稱當 key 會互相覆蓋)
            stats[subject.id] = {
                "id": subject.id,
                "name": subject.name,
                "grade": (subject.grade or "").strip(),
                "template_count": template_count,
                "color": subject.color,
            }
        
        return stats

    async def get_template_counts_by_name(self) -> dict:
        """各科目名稱下啟用中的範本數(含舊的只存名稱範本),供科目層級顯示。

        刪除判定用列 id(見 template_usage_condition);顯示用名稱,兩者分開。
        """
        query = (
            select(Template.subject, func.count())
            .where(Template.is_active.is_(True))
            .group_by(Template.subject)
        )
        result = await self.db.execute(query)
        return {name: int(n) for name, n in result.all() if name}
