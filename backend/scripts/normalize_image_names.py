"""正規化 image_questions.question_image / answer_image 名稱。

背景:Excel 匯入(image_question_service.parse_excel)只對名稱做 strip(),
但圖片上傳端點(routers/images.py 的 upload_image)會清理特殊字元、且不接受
副檔名。兩邊規則不一致,正式站已知有題目引用 `..._image02.1` 但實際檔案是
`..._image02_1`、引用 `..._image01.png` 但實際檔案是 `..._image01_png`。
本腳本把題目引用的名稱正規化成與上傳端點一致的規則(見 app/core/image_names.py)。

預設只列報告;加 --apply 才寫入 DB,並對有變更的列依磁碟重新計算 images_verified。

另有 --fix-disk-suffix:反過來處理「磁碟上檔案被存成 <x>_png / <x>_jpg /
<x>_jpeg(沒有實際副檔名,是被上傳端點的字元清理規則誤轉換)」但題目引用的
`<x>.<ext>` 檔案不存在的情況,把檔案搬回正常副檔名。這與正規化資料庫名稱是
互補但獨立的操作,兩者可個別執行、個別 --apply。

執行(容器內):
  docker compose exec -T backend python - < backend/scripts/normalize_image_names.py
  docker compose exec -T backend python - --apply < backend/scripts/normalize_image_names.py
  docker compose exec -T backend python - --fix-disk-suffix < backend/scripts/normalize_image_names.py
  docker compose exec -T backend python - --fix-disk-suffix --apply < backend/scripts/normalize_image_names.py
"""

import argparse
import asyncio
import sys
from pathlib import Path

if "__file__" in globals():
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select  # noqa: E402

from app.core.config import ANSWER_IMAGES_DIR, QUESTION_IMAGES_DIR  # noqa: E402
from app.core.image_names import normalize_image_name  # noqa: E402
from app.db.database import AsyncSessionLocal  # noqa: E402
from app.db.models import ImageQuestion  # noqa: E402

QUESTION_IMAGES_PATH = Path(QUESTION_IMAGES_DIR)
ANSWER_IMAGES_PATH = Path(ANSWER_IMAGES_DIR)
SUPPORTED_EXTENSIONS = ["jpg", "jpeg", "png", "gif", "webp"]
# 上傳端點的清理規則會把 "." 轉成 "_",所以副檔名結尾的點會變成這些底線後綴
DISK_SUFFIX_EXTENSIONS = ["png", "jpg", "jpeg"]


def _name_variants(name: str, is_answer: bool = False) -> list:
    """與 ImageQuestionService._get_name_variants 一致:答案圖也接受 _answer_ / __answer__ 互換。"""
    variants = [name]
    if is_answer:
        if "_answer_" in name and "__answer__" not in name:
            variants.append(name.replace("_answer_", "__answer__"))
        elif "__answer__" in name:
            variants.append(name.replace("__answer__", "_answer_"))
    return variants


def _image_exists(image_dir: Path, name: str, is_answer: bool = False) -> bool:
    return any(
        (image_dir / f"{variant}.{ext}").exists()
        for variant in _name_variants(name, is_answer)
        for ext in SUPPORTED_EXTENSIONS
    )


async def _normalize_names(apply: bool) -> int:
    async with AsyncSessionLocal() as session:
        rows = (
            (
                await session.execute(
                    select(ImageQuestion)
                    .where(ImageQuestion.is_active.is_(True))
                    .order_by(ImageQuestion.id)
                )
            )
            .scalars()
            .all()
        )
        changed = 0
        for q in rows:
            row_changed = False
            new_question = normalize_image_name(q.question_image)
            if new_question and new_question != q.question_image:
                print(f"#{q.id} question_image: {q.question_image} → {new_question}")
                row_changed = True
                if apply:
                    q.question_image = new_question

            if q.answer_image:
                new_answer = normalize_image_name(q.answer_image)
                if new_answer and new_answer != q.answer_image:
                    print(f"#{q.id} answer_image: {q.answer_image} → {new_answer}")
                    row_changed = True
                    if apply:
                        q.answer_image = new_answer

            if row_changed:
                changed += 1
                if apply:
                    q_ok = _image_exists(QUESTION_IMAGES_PATH, q.question_image)
                    a_ok = (
                        True
                        if not q.answer_image
                        else _image_exists(
                            ANSWER_IMAGES_PATH, q.answer_image, is_answer=True
                        )
                    )
                    q.images_verified = bool(q_ok and a_ok)

        print(f"\n共 {len(rows)} 筆啟用中題目,{'已更新' if apply else '需更新'} {changed} 筆")
        if apply and changed:
            await session.commit()
        elif not apply and changed:
            print("(僅報告;加 --apply 寫入)")
    return changed


async def _collect_referenced_names() -> tuple:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(ImageQuestion.question_image, ImageQuestion.answer_image).where(
                ImageQuestion.is_active.is_(True)
            )
        )
        question_names: set = set()
        answer_names: set = set()
        for question_image, answer_image in result.all():
            if question_image:
                question_names.add(question_image)
            if answer_image:
                answer_names.add(answer_image)
        return question_names, answer_names


def _fix_disk_suffix(image_dir: Path, referenced_names: set, apply: bool) -> int:
    """檔案被存成 <x>_png.jpg 這種名字(Excel/上傳時把 ".png" 打進檔名,被字元清理規則
    轉成底線),但題目引用的是 <x> 且 <x>.<任何副檔名> 不存在時,改名為 <x>.<原副檔名>。"""
    fixed = 0
    if not image_dir.exists():
        return 0
    for file_path in sorted(image_dir.iterdir()):
        if not file_path.is_file():
            continue
        # 線上實際樣子:g4_..._image01_png.jpg(檔名尾巴多了 _png,另有真正的副檔名)
        stem = file_path.stem
        for ext in DISK_SUFFIX_EXTENSIONS:
            suffix = f"_{ext}"
            if not stem.endswith(suffix):
                continue
            base = stem[: -len(suffix)]
            if base not in referenced_names or _image_exists(image_dir, base):
                continue
            target = image_dir / f"{base}{file_path.suffix.lower()}"  # 保留真正的副檔名
            if target.exists():
                continue
            print(f"{file_path.name} → {target.name}")
            fixed += 1
            if apply:
                file_path.rename(target)
            break
    return fixed


async def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--apply", action="store_true", help="實際寫入資料庫 / 重新命名檔案")
    parser.add_argument(
        "--fix-disk-suffix",
        action="store_true",
        help="修補磁碟上被存成 <x>_png/<x>_jpg/<x>_jpeg 的檔案,搬回 <x>.<ext>",
    )
    args = parser.parse_args()

    if args.fix_disk_suffix:
        question_names, answer_names = await _collect_referenced_names()
        fixed_q = _fix_disk_suffix(QUESTION_IMAGES_PATH, question_names, args.apply)
        fixed_a = _fix_disk_suffix(ANSWER_IMAGES_PATH, answer_names, args.apply)
        total = fixed_q + fixed_a
        verb = "已修正" if args.apply else "需修正"
        print(f"\n磁碟檔名{verb} {total} 個(問題圖 {fixed_q} / 答案圖 {fixed_a})")
        if not args.apply and total:
            print("(僅報告;加 --apply 寫入)")
        return 0

    await _normalize_names(args.apply)
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
