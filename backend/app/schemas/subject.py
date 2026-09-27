from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime
import re

from app.core.subject_norm import normalize_subject


class SubjectBase(BaseModel):
    """科目基本欄位"""
    name: str = Field(..., min_length=1, max_length=50, description="科目名稱")
    description: Optional[str] = Field(None, max_length=500, description="科目描述")
    color: str = Field(default="#3B82F6", description="科目顏色代碼")
    grade: Optional[str] = Field(None, max_length=20, description="適用年級（可自訂，例如 G1, G1-G2, 初級）")

    @validator('color')
    def validate_color(cls, v):
        if not re.match(r'^#[0-9A-Fa-f]{6}$', v):
            raise ValueError('顏色格式必須是 #RRGGBB')
        return v

    @validator('grade')
    def validate_grade(cls, v):
        # 移除固定年級驗證，允許自訂年級
        if v is not None:
            v = v.strip()
            if len(v) > 20:
                raise ValueError('年級長度不能超過 20 字元')
        return v

    @validator('name')
    def validate_name(cls, v):
        v = v.strip()
        if not v:
            raise ValueError('科目名稱不能為空')
        # 已知別名（中文/首大寫英文）收斂為 canonical key；自訂科目原樣保留
        return normalize_subject(v)


class SubjectCreate(SubjectBase):
    """建立科目請求"""
    pass


class SubjectUpdate(BaseModel):
    """更新科目請求"""
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=500)
    color: Optional[str] = None
    grade: Optional[str] = None
    is_active: Optional[bool] = None

    @validator('color')
    def validate_color(cls, v):
        if v is not None and not re.match(r'^#[0-9A-Fa-f]{6}$', v):
            raise ValueError('顏色格式必須是 #RRGGBB')
        return v

    @validator('grade')
    def validate_grade(cls, v):
        # 移除固定年級驗證，允許自訂年級
        if v is not None:
            v = v.strip()
            if len(v) > 20:
                raise ValueError('年級長度不能超過 20 字元')
        return v

    @validator('name')
    def validate_name(cls, v):
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError('科目名稱不能為空')
        return v


class SubjectResponse(SubjectBase):
    """科目回應"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SubjectsListResponse(BaseModel):
    """科目清單回應"""
    subjects: list[SubjectResponse]
    total: int


class SubjectTreeGrade(BaseModel):
    """樹狀節點下的一個年級（對應一列 subjects row）"""
    id: int
    grade: str = Field(description="年級代碼（見 GET /api/subjects/grades）；'ALL'=全年級通用；''=未指定年級")


class SubjectTreeNode(BaseModel):
    """科目→年級 樹狀節點（同名科目的各年級列聚合而成）"""
    name: str
    color: str
    grades: List[SubjectTreeGrade]


class SubjectTreeResponse(BaseModel):
    """科目→年級 樹回應"""
    subjects: List[SubjectTreeNode]
    total: int = Field(description="科目（樹節點）數量")