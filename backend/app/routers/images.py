"""靜態圖片服務 API 端點"""
from fastapi import APIRouter, HTTPException, Query, UploadFile, File, Form, Depends
from fastapi.responses import FileResponse
from pathlib import Path
from typing import Literal, Optional, List
import logging
import re

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from app.core.config import QUESTION_IMAGES_DIR, ANSWER_IMAGES_DIR
from app.db.database import get_db
from app.db.models import ImageQuestion
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/images", tags=["images"])

# 圖片目錄路徑
QUESTION_IMAGES_PATH = Path(QUESTION_IMAGES_DIR)
ANSWER_IMAGES_PATH = Path(ANSWER_IMAGES_DIR)

# 支援的圖片格式
SUPPORTED_EXTENSIONS = ["jpg", "jpeg", "png", "gif", "webp"]

# MIME 類型映射
MIME_TYPES = {
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "png": "image/png",
    "gif": "image/gif",
    "webp": "image/webp",
}


class ImageListItem(BaseModel):
    """圖片列表項目"""
    name: str
    filename: str
    extension: str
    path: str


class ImageListResponse(BaseModel):
    """圖片列表回應"""
    images: List[ImageListItem]
    total: int
    image_type: str


class ImageUploadResponse(BaseModel):
    """圖片上傳回應"""
    success: bool
    filename: str
    name: str
    extension: str
    image_type: str
    path: str
    message: str


class ImageRenameRequest(BaseModel):
    """圖片重命名請求"""
    old_name: str
    new_name: str
    update_questions: bool = True


class ImageRenameResponse(BaseModel):
    """圖片重命名回應"""
    success: bool
    old_name: str
    new_name: str
    affected_questions: int
    message: str


class ImageReferenceItem(BaseModel):
    """圖片引用項目"""
    id: int
    subject: str
    grade: Optional[str]
    chapter: Optional[str]
    question_image: str
    answer_image: Optional[str]
    reference_type: str  # 'question' 或 'answer'


class ImageReferencesResponse(BaseModel):
    """圖片引用查詢回應"""
    image_name: str
    image_type: str
    references: List[ImageReferenceItem]
    total: int


# 圖片名稱驗證正則表達式（只允許字母、數字、底線、連字號）
IMAGE_NAME_PATTERN = re.compile(r'^[a-zA-Z0-9_\-]+$')

# 最大檔案大小（10MB）
MAX_IMAGE_SIZE = 10 * 1024 * 1024


def _get_image_dir(image_type: str) -> Path:
    """取得圖片目錄路徑"""
    if image_type == "answers":
        return ANSWER_IMAGES_PATH
    return QUESTION_IMAGES_PATH


def find_image_file(filename: str, image_dir: Path) -> tuple[Path, str] | None:
    """尋找圖片檔案，支援自動偵測副檔名

    Args:
        filename: 檔案名（可含或不含副檔名）
        image_dir: 圖片目錄

    Returns:
        (Path, extension) 或 None
    """
    # 先檢查是否已包含副檔名
    file_path = image_dir / filename
    if file_path.exists() and file_path.is_file():
        ext = file_path.suffix.lstrip(".")
        if ext.lower() in SUPPORTED_EXTENSIONS:
            return file_path, ext

    # 嘗試各種常見副檔名
    base_name = filename.rsplit(".", 1)[0] if "." in filename else filename
    for ext in SUPPORTED_EXTENSIONS:
        test_path = image_dir / f"{base_name}.{ext}"
        if test_path.exists() and test_path.is_file():
            return test_path, ext

    return None


def _validate_path_within_dir(file_path: Path, allowed_dir: Path) -> Path:
    """驗證路徑是否在指定目錄內，防止路徑穿越攻擊"""
    try:
        resolved_path = file_path.resolve()
        allowed_dir_resolved = allowed_dir.resolve()
        resolved_path.relative_to(allowed_dir_resolved)
        return resolved_path
    except ValueError:
        raise HTTPException(status_code=403, detail="無效的檔案路徑")


def _validate_filename(filename: str) -> None:
    """驗證檔案名稱安全性"""
    if ".." in filename or filename.startswith("/") or "\\" in filename:
        raise HTTPException(status_code=400, detail="無效的檔案名稱")


@router.get("/questions/{filename:path}")
async def get_question_image(filename: str):
    """取得問題圖片

    路徑: /api/images/questions/{filename}
    """
    _validate_filename(filename)

    image_dir = QUESTION_IMAGES_PATH
    result = find_image_file(filename, image_dir)
    if not result:
        logger.warning(f"找不到問題圖片: {filename}")
        raise HTTPException(status_code=404, detail="圖片不存在")

    file_path, ext = result
    resolved_path = _validate_path_within_dir(file_path, image_dir)
    media_type = MIME_TYPES.get(ext.lower(), "application/octet-stream")

    return FileResponse(
        path=resolved_path,
        media_type=media_type,
        filename=resolved_path.name,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        }
    )


@router.get("/answers/{filename:path}")
async def get_answer_image(filename: str):
    """取得答案圖片

    路徑: /api/images/answers/{filename}
    """
    _validate_filename(filename)

    image_dir = ANSWER_IMAGES_PATH
    result = find_image_file(filename, image_dir)
    if not result:
        logger.warning(f"找不到答案圖片: {filename}")
        raise HTTPException(status_code=404, detail="圖片不存在")

    file_path, ext = result
    resolved_path = _validate_path_within_dir(file_path, image_dir)
    media_type = MIME_TYPES.get(ext.lower(), "application/octet-stream")

    return FileResponse(
        path=resolved_path,
        media_type=media_type,
        filename=resolved_path.name,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        }
    )


@router.get("/check/{image_type}/{filename:path}")
async def check_image(image_type: str, filename: str):
    """檢查圖片是否存在

    路徑: /api/images/check/questions/{filename} 或 /api/images/check/answers/{filename}
    """
    if image_type not in ("questions", "answers"):
        raise HTTPException(status_code=400, detail="image_type 必須是 'questions' 或 'answers'")

    _validate_filename(filename)

    image_dir = _get_image_dir(image_type)
    result = find_image_file(filename, image_dir)
    exists = result is not None

    if exists:
        _validate_path_within_dir(result[0], image_dir)

    return {
        "filename": filename,
        "image_type": image_type,
        "exists": exists,
        "path": str(result[0].name) if result else None,
        "extension": result[1] if result else None,
    }


@router.get("/list/{image_type}", response_model=ImageListResponse)
async def list_images(
    image_type: Literal["questions", "answers"],
    search: Optional[str] = Query(None, description="搜尋圖片名稱"),
    limit: int = Query(50, ge=1, le=200, description="返回數量限制"),
):
    """列出可用圖片

    路徑: /api/images/list/questions 或 /api/images/list/answers
    """
    image_dir = _get_image_dir(image_type)

    if not image_dir.exists():
        logger.warning(f"圖片目錄不存在: {image_dir}")
        return ImageListResponse(images=[], total=0, image_type=image_type)

    images: List[ImageListItem] = []

    try:
        for file_path in image_dir.iterdir():
            if not file_path.is_file():
                continue

            ext = file_path.suffix.lstrip(".").lower()
            if ext not in SUPPORTED_EXTENSIONS:
                continue

            name = file_path.stem
            filename = file_path.name

            if search and search.lower() not in name.lower():
                continue

            images.append(ImageListItem(
                name=name,
                filename=filename,
                extension=ext,
                path=f"/api/images/{image_type}/{filename}",
            ))

        images.sort(key=lambda x: x.name)
        total = len(images)
        images = images[:limit]

        return ImageListResponse(
            images=images,
            total=total,
            image_type=image_type,
        )

    except Exception as e:
        logger.error(f"列出圖片時發生錯誤: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="列出圖片時發生錯誤")


@router.post("/upload/{image_type}", response_model=ImageUploadResponse)
async def upload_image(
    image_type: Literal["questions", "answers"],
    file: UploadFile = File(...),
    custom_name: Optional[str] = Form(None, description="自訂檔案名稱（不含副檔名）"),
):
    """上傳圖片

    路徑: POST /api/images/upload/questions 或 /api/images/upload/answers

    Args:
        image_type: 圖片類型（questions 或 answers）
        file: 要上傳的圖片檔案
        custom_name: 可選的自訂檔案名稱（不含副檔名）

    Returns:
        上傳結果
    """
    # 驗證檔案類型
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="只支援圖片檔案")

    # 取得副檔名
    original_filename = file.filename or "image.jpg"
    ext = original_filename.rsplit(".", 1)[-1].lower() if "." in original_filename else "jpg"

    if ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"不支援的圖片格式。支援的格式: {', '.join(SUPPORTED_EXTENSIONS)}"
        )

    # 決定檔案名稱
    if custom_name:
        # 驗證自訂名稱
        custom_name = custom_name.strip()
        if not IMAGE_NAME_PATTERN.match(custom_name):
            raise HTTPException(
                status_code=400,
                detail="圖片名稱只能包含字母、數字、底線和連字號"
            )
        name = custom_name
    else:
        # 使用原始檔案名稱（去除副檔名）
        name = original_filename.rsplit(".", 1)[0] if "." in original_filename else original_filename
        # 清理名稱中的特殊字元
        name = re.sub(r'[^a-zA-Z0-9_\-]', '_', name)

    filename = f"{name}.{ext}"

    # 取得目標目錄
    image_dir = _get_image_dir(image_type)

    # 確保目錄存在
    image_dir.mkdir(parents=True, exist_ok=True)

    # 目標檔案路徑
    file_path = image_dir / filename

    # 檢查是否已存在同名檔案
    if file_path.exists():
        raise HTTPException(
            status_code=409,
            detail=f"檔案 '{filename}' 已存在。請使用不同的名稱或先刪除現有檔案。"
        )

    try:
        # 讀取檔案內容
        contents = await file.read()

        # 檢查檔案大小
        if len(contents) > MAX_IMAGE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"檔案太大。最大允許 {MAX_IMAGE_SIZE // (1024 * 1024)}MB"
            )

        # 寫入檔案
        with open(file_path, "wb") as f:
            f.write(contents)

        logger.info(f"成功上傳圖片: {filename} 到 {image_type}")

        return ImageUploadResponse(
            success=True,
            filename=filename,
            name=name,
            extension=ext,
            image_type=image_type,
            path=f"/api/images/{image_type}/{filename}",
            message=f"圖片 '{filename}' 上傳成功",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"上傳圖片時發生錯誤: {e}", exc_info=True)
        # 如果寫入失敗，清理可能建立的檔案
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=500, detail=f"上傳圖片時發生錯誤: {str(e)}")


@router.get("/references/{image_type}/{image_name}", response_model=ImageReferencesResponse)
async def get_image_references(
    image_type: Literal["questions", "answers"],
    image_name: str,
    db: AsyncSession = Depends(get_db),
):
    """查詢引用此圖片的題目列表

    路徑: GET /api/images/references/questions/{image_name}
          或 /api/images/references/answers/{image_name}

    Args:
        image_type: 圖片類型（questions 或 answers）
        image_name: 圖片名稱（不含副檔名）

    Returns:
        引用此圖片的所有題目列表
    """
    _validate_filename(image_name)

    references: List[ImageReferenceItem] = []

    try:
        if image_type == "questions":
            # 查詢引用此問題圖片的題目
            stmt = select(ImageQuestion).where(ImageQuestion.question_image == image_name)
            result = await db.execute(stmt)
            questions = result.scalars().all()

            for q in questions:
                references.append(ImageReferenceItem(
                    id=q.id,
                    subject=q.subject,
                    grade=q.grade,
                    chapter=q.chapter,
                    question_image=q.question_image,
                    answer_image=q.answer_image,
                    reference_type="question",
                ))
        else:
            # 查詢引用此答案圖片的題目
            stmt = select(ImageQuestion).where(ImageQuestion.answer_image == image_name)
            result = await db.execute(stmt)
            questions = result.scalars().all()

            for q in questions:
                references.append(ImageReferenceItem(
                    id=q.id,
                    subject=q.subject,
                    grade=q.grade,
                    chapter=q.chapter,
                    question_image=q.question_image,
                    answer_image=q.answer_image,
                    reference_type="answer",
                ))

        return ImageReferencesResponse(
            image_name=image_name,
            image_type=image_type,
            references=references,
            total=len(references),
        )

    except Exception as e:
        logger.error(f"查詢圖片引用時發生錯誤: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"查詢圖片引用時發生錯誤: {str(e)}")


@router.put("/rename/{image_type}", response_model=ImageRenameResponse)
async def rename_image(
    image_type: Literal["questions", "answers"],
    request: ImageRenameRequest,
    db: AsyncSession = Depends(get_db),
):
    """重命名圖片檔案

    路徑: PUT /api/images/rename/questions 或 /api/images/rename/answers

    Args:
        image_type: 圖片類型（questions 或 answers）
        request: 重命名請求（包含舊名稱、新名稱、是否更新題目）

    Returns:
        重命名結果和受影響的題目數量
    """
    old_name = request.old_name.strip()
    new_name = request.new_name.strip()

    # 驗證名稱
    _validate_filename(old_name)
    _validate_filename(new_name)

    if not IMAGE_NAME_PATTERN.match(new_name):
        raise HTTPException(
            status_code=400,
            detail="圖片名稱只能包含字母、數字、底線和連字號"
        )

    if old_name == new_name:
        raise HTTPException(status_code=400, detail="新名稱與舊名稱相同")

    image_dir = _get_image_dir(image_type)

    # 尋找舊檔案
    old_file_result = find_image_file(old_name, image_dir)
    if not old_file_result:
        raise HTTPException(status_code=404, detail=f"找不到圖片 '{old_name}'")

    old_file_path, ext = old_file_result
    old_file_path = _validate_path_within_dir(old_file_path, image_dir)

    # 檢查新名稱是否已存在
    new_filename = f"{new_name}.{ext}"
    new_file_path = image_dir / new_filename

    if new_file_path.exists():
        raise HTTPException(
            status_code=409,
            detail=f"圖片名稱 '{new_name}' 已存在"
        )

    affected_count = 0

    try:
        # 重命名檔案
        old_file_path.rename(new_file_path)
        logger.info(f"已重命名圖片: {old_name} -> {new_name} ({image_type})")

        # 更新資料庫中的引用
        if request.update_questions:
            if image_type == "questions":
                stmt = select(ImageQuestion).where(ImageQuestion.question_image == old_name)
                result = await db.execute(stmt)
                questions = result.scalars().all()

                for q in questions:
                    q.question_image = new_name
                    q.images_verified = False  # 重置驗證狀態
                    affected_count += 1
            else:
                stmt = select(ImageQuestion).where(ImageQuestion.answer_image == old_name)
                result = await db.execute(stmt)
                questions = result.scalars().all()

                for q in questions:
                    q.answer_image = new_name
                    q.images_verified = False  # 重置驗證狀態
                    affected_count += 1

            await db.commit()
            logger.info(f"已更新 {affected_count} 筆題目的圖片引用")

        return ImageRenameResponse(
            success=True,
            old_name=old_name,
            new_name=new_name,
            affected_questions=affected_count,
            message=f"圖片重命名成功，已更新 {affected_count} 筆題目",
        )

    except HTTPException:
        # 如果是 HTTP 例外，回滾檔案重命名
        if new_file_path.exists() and not old_file_path.exists():
            new_file_path.rename(old_file_path)
        raise
    except Exception as e:
        # 回滾檔案重命名
        if new_file_path.exists() and not old_file_path.exists():
            new_file_path.rename(old_file_path)
        await db.rollback()
        logger.error(f"重命名圖片時發生錯誤: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"重命名圖片時發生錯誤: {str(e)}")
