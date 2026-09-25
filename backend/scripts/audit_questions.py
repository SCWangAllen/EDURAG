"""題庫稽核:用 core/question_validation 的規則掃 questions 表,找出不符題型格式的題目。

預設只列報告、不改資料。三種動作:
  --fix          能正規化的直接更新(填充題挖空格、配合題答案轉索引、選擇題答案轉字母、去 HTML)
  --delete --yes 刪掉修不了的題目(請先備份:./scripts/db-init.sh backup)
  --recast cloze=short_answer
                 修不了的 cloze 改成 short_answer(常見情況:模型出了問答題卻標成填充題);
                 改完的題不再列入刪除
  --type cloze   只處理某題型;--limit N 清單最多列 N 筆(預設 200)

執行方式(容器內有 DATABASE_URL):
  docker compose exec -T backend python - [--fix] [--delete --yes] < backend/scripts/audit_questions.py
本機:
  cd backend && DATABASE_URL=postgresql+asyncpg://... python scripts/audit_questions.py
"""

import argparse
import asyncio
import json
import sys
from collections import Counter
from pathlib import Path

# 直接以檔案路徑執行時,讓 `app` 套件可被 import(容器內 stdin 執行則 cwd 已是 /app)
if "__file__" in globals():
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select

from app.core.question_validation import SAVE_CHECKED_TYPES, normalize_question_payload
from app.db.database import AsyncSessionLocal
from app.db.models import Question


def _answer_text(value):
    return value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)


def _changes(q: Question, fields: dict) -> list[str]:
    out = []
    if fields["content"] != q.stem:
        out.append(f"stem: {q.stem[:60]!r} → {fields['content'][:60]!r}")
    new_answer = _answer_text(fields["answer"])
    if new_answer != q.answer:
        out.append(f"answer: {q.answer[:40]!r} → {new_answer[:40]!r}")
    if (fields["options"] or None) != (q.options or None):
        out.append("options: 去 HTML / 空白")
    if (fields["question_data"] or None) != (q.question_data or None):
        out.append("question_data: 去 HTML / 空白")
    return out


async def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--fix", action="store_true", help="套用可自動修正的變更")
    parser.add_argument("--delete", action="store_true", help="刪除修不了的題目(需 --yes)")
    parser.add_argument("--yes", action="store_true", help="確認刪除")
    parser.add_argument("--type", dest="qtype", help="只處理此題型")
    parser.add_argument("--limit", type=int, default=200, help="清單最多列幾筆")
    parser.add_argument(
        "--recast", metavar="FROM=TO", help="修不了的 FROM 題型改成 TO 題型,如 cloze=short_answer"
    )
    args = parser.parse_args()
    if args.delete and not args.yes:
        print("--delete 需要加 --yes 確認(先做備份)", file=sys.stderr)
        return 2
    recast_from = recast_to = None
    if args.recast:
        if "=" not in args.recast:
            print("--recast 格式:FROM=TO,例如 cloze=short_answer", file=sys.stderr)
            return 2
        recast_from, recast_to = args.recast.split("=", 1)

    async with AsyncSessionLocal() as session:
        stmt = select(Question).order_by(Question.id)
        if args.qtype:
            stmt = stmt.where(Question.question_type == args.qtype)
        rows = (await session.execute(stmt)).scalars().all()

        ok = 0
        skipped: Counter = Counter()
        fixable: list[tuple[Question, dict, list[str]]] = []
        broken: list[tuple[Question, list[str]]] = []
        for q in rows:
            if q.question_type not in SAVE_CHECKED_TYPES:
                skipped[q.question_type] += 1
                continue
            fields, problems = normalize_question_payload(
                q.question_type, q.stem, q.options, q.answer, q.question_data
            )
            if problems:
                broken.append((q, problems))
                continue
            changes = _changes(q, fields)
            if changes:
                fixable.append((q, fields, changes))
            else:
                ok += 1

        print(
            f"掃描 {len(rows)} 題:合格 {ok}、可自動修正 {len(fixable)}、修不了 {len(broken)}"
            + (f"、未檢核 {dict(skipped)}" if skipped else "")
        )

        if fixable:
            by_type = Counter(q.question_type for q, _, _ in fixable)
            print(f"\n== 可自動修正 {len(fixable)} 題 {dict(by_type)} ==")
            for q, _, changes in fixable[: args.limit]:
                print(f"  #{q.id} [{q.question_type}] " + "; ".join(changes))
            if len(fixable) > args.limit:
                print(f"  ... 另 {len(fixable) - args.limit} 題未列")

        if broken:
            reasons = Counter(r for _, problems in broken for r in problems)
            print(f"\n== 修不了 {len(broken)} 題(原因:{dict(reasons)})==")
            for q, problems in broken[: args.limit]:
                print(f"  #{q.id} [{q.question_type}] {'；'.join(problems)}")
                print(f"      題幹:{q.stem[:90]!r}  答案:{q.answer[:40]!r}")
            if len(broken) > args.limit:
                print(f"  ... 另 {len(broken) - args.limit} 題未列")

        if args.fix and fixable:
            for q, fields, _ in fixable:
                q.stem = fields["content"]
                q.answer = _answer_text(fields["answer"])
                q.options = fields["options"]
                q.question_data = fields["question_data"]
            await session.commit()
            print(f"\n已更新 {len(fixable)} 題")

        recast = [
            q for q, _ in broken if recast_from and q.question_type == recast_from
        ]
        if recast_from and recast:
            print(f"\n== 改題型 {recast_from} → {recast_to}:{[q.id for q in recast]} ==")
            if args.fix or args.delete:
                for q in recast:
                    q.question_type = recast_to
                await session.commit()
                print(f"已改 {len(recast)} 題題型")
            else:
                print("(僅報告;加 --fix 套用)")
            broken = [(q, p) for q, p in broken if q not in recast]

        if args.delete and broken:
            for q, _ in broken:
                await session.delete(q)
            await session.commit()
            print(f"\n已刪除 {len(broken)} 題:{[q.id for q, _ in broken]}")

        if not args.fix and not args.delete and (fixable or broken):
            print("\n(僅報告,未改資料。加 --fix 套用修正;--delete --yes 刪除修不了的題)")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
