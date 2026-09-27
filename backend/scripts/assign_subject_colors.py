"""把還是預設藍色(#3B82F6)的科目自動分配不同顏色(以科目名稱為單位,所有年級同色)。

預設只列報告;加 --apply 才寫入。已手動改過顏色的科目不動。
執行(容器內):docker compose exec -T backend python - [--apply] < backend/scripts/assign_subject_colors.py
"""

import argparse
import asyncio
import sys
from pathlib import Path

if "__file__" in globals():
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select  # noqa: E402

from app.core.subject_colors import assign_colors, is_unassigned_color  # noqa: E402
from app.db.database import AsyncSessionLocal  # noqa: E402
from app.db.models import Subject  # noqa: E402


async def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--apply", action="store_true", help="實際寫入資料庫")
    args = parser.parse_args()

    async with AsyncSessionLocal() as session:
        rows = (
            (
                await session.execute(
                    select(Subject)
                    .where(Subject.is_active.is_(True))
                    .order_by(Subject.name, Subject.id)
                )
            )
            .scalars()
            .all()
        )
        # 每個科目名稱取第一個非預設色(手動改過的優先)
        existing: dict[str, str | None] = {}
        for s in rows:
            if s.name not in existing or (
                is_unassigned_color(existing[s.name])
                and not is_unassigned_color(s.color)
            ):
                existing[s.name] = s.color
        plan = assign_colors(sorted(existing), existing)
        changes = {
            name: color
            for name, color in plan.items()
            if is_unassigned_color(existing.get(name))
        }

        print(f"科目 {len(existing)} 個,仍為預設藍需分配 {len(changes)} 個")
        for name, color in changes.items():
            print(f"  {name}: {existing.get(name) or '(無)'} → {color}")
        if not changes:
            return 0
        if not args.apply:
            print("\n(僅報告;加 --apply 寫入)")
            return 0
        updated = 0
        for s in rows:
            if s.name in changes:
                s.color = changes[s.name]
                updated += 1
        await session.commit()
        print(f"\n已更新 {updated} 列(涵蓋 {len(changes)} 個科目)")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
