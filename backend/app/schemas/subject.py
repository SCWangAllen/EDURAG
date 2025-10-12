from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
import re


class SubjectBase(BaseModel):
    """科目基本欄位"""
    name: str = Field(..., min_length=1, max_length=50, description="科目名稱")
    description: Optional[str] = Field(None, max_length=500, description="科目描述")
    color: str = Field(default="#3B82F6", description="科目顏色代碼")
    grade: Optional[str] = Field(None, max_length=10, description="適用年級 (G1-G6, ALL)")

    @validator('color')
    def validate_color(cls, v):
        if not re.match(r'^#[0-9A-Fa-f]{6}$', v):
            raise ValueError('顏色格式必須是 #RRGGBB')
        return v

    @validator('grade')
    def validate_grade(cls, v):
        if v is not None:
            valid_grades = ['G1', 'G2', 'G3', 'G4', 'G5', 'G6', 'ALL']
            if v not in valid_grades:
                raise ValueError(f'年級必須是以下之一: {", ".join(valid_grades)}')
        return v

    @validator('name')
    def validate_name(cls, v):
        v = v.strip()
        if not v:
            raise ValueError('科目名稱不能為空')
        return v


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
        if v is not None:
            valid_grades = ['G1', 'G2', 'G3', 'G4', 'G5', 'G6', 'ALL']
            if v not in valid_grades:
                raise ValueError(f'年級必須是以下之一: {", ".join(valid_grades)}')
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