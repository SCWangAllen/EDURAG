"""教學手冊截圖 + 自動加框編號。

用 gstack browse(無頭 Chromium)對本機前端截圖,元素座標由頁面 JS 回傳,再用 PIL 畫紅框與編號。
用法:python docs/user-guide/tools/capture_guide.py [--base http://localhost:8989] [--only 03,07]
輸出:docs/user-guide/images/NN-name.png(原始未加框圖在 /tmp/guide/raw/)。
"""

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

B = os.path.expanduser("~/.claude/skills/gstack/browse/dist/browse")
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "images"
RAW = Path("/tmp/guide/raw")
FONT = "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"


def b(*args, timeout=60):
    r = subprocess.run([B, *args], capture_output=True, text=True, timeout=timeout)
    return (r.stdout + r.stderr).strip()


def js(code):
    out = b("js", code)
    return out.splitlines()[-1] if out else ""


def rects_from_js(expr):
    """expr 需回傳 [[label, {x,y,w,h}], ...] 的 JSON 字串。"""
    raw = js(expr)
    try:
        return [(k, r) for k, r in json.loads(raw) if r]
    except Exception:
        print("  rects parse failed:", raw[:200])
        return []


# 常用 JS 片段
R = "(el => el ? (r => ({x:r.x,y:r.y,w:r.width,h:r.height}))(el.getBoundingClientRect()) : null)"
BTN = "(txt => Array.from(document.querySelectorAll('button, a')).find(b => new RegExp(txt,'i').test(b.textContent.trim())))"
SMALL = "(re => { const els = Array.from(document.querySelectorAll('body *')).filter(e => re.test(e.textContent) && e.children.length <= 3 && e.getBoundingClientRect().width > 0); els.sort((a,b) => (a.getBoundingClientRect().width*a.getBoundingClientRect().height) - (b.getBoundingClientRect().width*b.getBoundingClientRect().height)); return els[0] || null })"
GEAR = "(() => Array.from(document.querySelectorAll('button')).filter(b => b.getBoundingClientRect().top < 60 && b.getBoundingClientRect().width > 0).sort((a,b) => b.getBoundingClientRect().right - a.getBoundingClientRect().right)[0])"
UNION = "((a, b) => { if (!a) return null; const r1 = a.getBoundingClientRect(), r2 = (b || a).getBoundingClientRect(); const x = Math.min(r1.x, r2.x), y = Math.min(r1.y, r2.y); return {x, y, w: Math.max(r1.right, r2.right) - x, h: Math.max(r1.bottom, r2.bottom) - y} })"
LABELNEXT = "(txt => { const l = Array.from(document.querySelectorAll('label')).find(l => new RegExp(txt,'i').test(l.textContent)); return l ? (l.nextElementSibling || l.parentElement) : null })"
LABELFIELD = "(txt => { const l = Array.from(document.querySelectorAll('label')).find(l => new RegExp(txt,'i').test(l.textContent)); return l ? (l.parentElement) : null })"


def annotate(raw_path, out_path, rects, pad=4, crop=None):
    im = Image.open(raw_path).convert("RGB")
    if crop:
        im = im.crop(crop)  # (left, top, right, bottom);座標仍以未裁切的視口為準
    d = ImageDraw.Draw(im)
    font = ImageFont.truetype(FONT, 18)
    n = 0
    for label, r in rects:
        # 不在視口內(捲動後在畫面外)的元素跳過,免得畫出反向矩形
        if r["y"] >= im.height or r["x"] >= im.width or r["y"] + r["h"] <= 0 or r["w"] <= 0 or r["h"] <= 0:
            print(f"  skip off-screen box: {label}")
            continue
        n += 1
        i = n
        x0, y0 = max(0, r["x"] - pad), max(0, r["y"] - pad)
        x1, y1 = min(im.width - 1, r["x"] + r["w"] + pad), min(im.height - 1, r["y"] + r["h"] + pad)
        d.rectangle([x0, y0, x1, y1], outline=(220, 38, 38), width=3)
        # 編號徽章(左上角,略突出框外)
        bx, by = x0 - 2, y0 - 26
        if by < 0:
            by = y0 + 2
        d.rounded_rectangle([bx, by, bx + 26, by + 24], radius=6, fill=(220, 38, 38))
        d.text((bx + 13, by + 12), str(i), fill="white", font=font, anchor="mm")
    im.save(out_path)


FIGS = []


def fig(name, url, setup=None, rects=None, wait=2.0, after=None, after_setup_scroll=None, crop=None):
    FIGS.append(dict(name=name, url=url, setup=setup or [], rects=rects or "[]", wait=wait, after=after or [], scroll=after_setup_scroll, crop=crop))


# ---------------------------------------------------------------- 圖片清單
fig("01-overview", "/exam-paper",
    rects=f"JSON.stringify([['sidebar', {R}(document.querySelector('aside') || document.querySelector('nav'))], ['lang', {R}({BTN}('^EN$')?.parentElement)], ['api', {R}({SMALL}(/API Status/))], ['settings', {R}({GEAR}())]])")

fig("02-template-gallery", "/templates",
    rects=f"JSON.stringify([['gallery', {R}(Array.from(document.querySelectorAll('h2')).find(h => /Create a Template/i.test(h.textContent))?.closest('div.bg-white'))], ['subjectMgmt', {R}({BTN}('Subject Management'))], ['create', {R}({BTN}('Create Template'))], ['initDefaults', {R}({BTN}('Initialize Default'))]])")

fig("03-template-filters", "/templates",
    setup=["(() => { window.scrollTo(0, 420); return 1 })()", "(() => { const b = document.querySelector('button[aria-expanded]'); b && b.click(); return 1 })()"],
    rects=f"JSON.stringify([['search', {R}({LABELFIELD}('^Search'))], ['subject', {R}(document.querySelector('button[aria-expanded]')?.parentElement)], ['subjectList', {R}(document.querySelector('[role=listbox]'))], ['grade', {R}({LABELFIELD}('Filter by Grade'))], ['sort', {R}({LABELFIELD}('Sort By'))], ['perPage', {R}({LABELFIELD}('Items per Page'))]])")

fig("04-template-custom-order", "/templates",
    setup=["(() => { const s = Array.from(document.querySelectorAll('select')).find(s => Array.from(s.options).some(o => o.value==='manual')); s.value='manual'; s.dispatchEvent(new Event('change',{bubbles:true})); return 1 })()", "(() => { window.scrollTo(0, 470); return 1 })()"],
    rects=f"JSON.stringify([['sortSelect', {R}({LABELFIELD}('Sort By'))], ['hint', {R}(Array.from(document.querySelectorAll('p')).find(p => /Drag|拖曳/.test(p.textContent)))], ['handle', {R}(document.querySelector('[title*=\"Drag\" i], [title*=\"拖曳\"]'))], ['updown', {UNION}(document.querySelector('button[title*=\"Move up\" i], button[title*=\"上移\"]'), document.querySelector('button[title*=\"Move down\" i], button[title*=\"下移\"]'))], ['actions', {UNION}({BTN}('^View$'), {BTN}('^Delete$'))]])")

fig("05-template-modal", "/templates",
    setup=["(() => { " + BTN + "('Create Template').click(); return 1 })()"],
    rects=f"JSON.stringify([['name', {R}({LABELFIELD}('Template Name'))], ['subject', {R}({LABELFIELD}('^Subject'))], ['grades', {R}({LABELFIELD}('Applicable Grades'))], ['type', {R}({LABELFIELD}('Question Type'))], ['prompt', {R}({LABELFIELD}('Prompt Template|Content'))], ['save', {R}({BTN}('^(Save|Create)$'))]])")

fig("06-subject-management", "/templates",
    setup=["(() => { " + BTN + "('Subject Management').click(); return 1 })()", "(() => { const b = document.querySelector('.fixed.inset-0 .grid button'); b && b.click(); return !!b })()"],
    rects=f"JSON.stringify([['add', {R}({BTN}('Add Subject'))], ['cards', {R}(document.querySelector('.fixed.inset-0 .grid'))], ['colorDot', {R}(document.querySelector('.fixed.inset-0 .grid [style*=\"background-color\"]'))], ['gradeGroups', {R}(Array.from(document.querySelectorAll('.fixed.inset-0 .grid *')).find(e => /^(ESL|Grade Level|Junior Class)$/i.test(e.textContent.trim()))?.parentElement)]])")

fig("07-documents", "/documents",
    rects=f"JSON.stringify([['upload', {R}({SMALL}(/Upload Excel/))], ['template', {R}({BTN}('Download Template'))], ['search', {R}({LABELFIELD}('^Search'))], ['subject', {R}(document.querySelector('button[aria-expanded]')?.parentElement)], ['grade', {R}({LABELFIELD}('^Grade'))], ['sourceFile', {R}({LABELFIELD}('Source File|Uploaded File|Upload File'))], ['sort', {R}({LABELFIELD}('^Sort'))], ['topPager', {R}(Array.from(document.querySelectorAll('div')).find(d => d.children.length >= 3 && /Previous|Next/.test(d.textContent) && d.getBoundingClientRect().height < 40))]])")

fig("08-documents-batch", "/documents",
    setup=["(() => { const cbs = document.querySelectorAll('input[type=checkbox]'); cbs[1]?.click(); cbs[2]?.click(); return cbs.length })()"],
    rects=f"JSON.stringify([['toolbar', {R}({BTN}('Copy to Grade|複製到年級')?.parentElement)], ['copy', {R}({BTN}('Copy to Grade|複製到年級'))], ['delete', {R}({BTN}('Batch Delete|Delete Selected|批次刪除'))], ['selectAll', {R}(Array.from(document.querySelectorAll('label')).find(l => /Select All|全選/i.test(l.textContent)))]])")

fig("09-copy-to-grades", "/documents",
    setup=["(() => { const cbs = document.querySelectorAll('input[type=checkbox]'); cbs[1]?.click(); return 1 })()", "(() => { " + BTN + "('Copy to Grade|複製到年級').click(); return 1 })()"],
    rects=f"JSON.stringify([['groups', {R}(document.querySelector('.fixed.inset-0 form, .fixed.inset-0 .space-y-4, .fixed.inset-0 .grid'))], ['count', {R}(Array.from(document.querySelectorAll('.fixed.inset-0 p, .fixed.inset-0 span')).find(e => /document|文件/.test(e.textContent) && /\\d/.test(e.textContent)))], ['confirm', {R}(Array.from(document.querySelectorAll('.fixed.inset-0 button')).find(b => /Copy|複製|Confirm/i.test(b.textContent) && !/Cancel/i.test(b.textContent)))]])")

fig("10-generate", "/generate",
    rects=f"JSON.stringify([['template', {R}(Array.from(document.querySelectorAll('h3')).find(h => /Template|範本/.test(h.textContent))?.parentElement)], ['pick', {R}({BTN}('Select Documents|選擇文件'))], ['count', {R}({LABELFIELD}('Number to Generate|生成數量'))], ['generate', {R}({BTN}('^Generate Questions|^Generate$|開始生成'))]])")

fig("11-document-picker", "/generate",
    setup=["(() => { " + BTN + "('Select Documents|選擇文件').click(); return 1 })()"],
    rects=f"JSON.stringify([['filters', {R}(document.querySelector('.fixed.inset-0 input[type=text], .fixed.inset-0 input[placeholder]')?.parentElement?.parentElement)], ['selectAll', {R}({BTN}('Select All Filtered|全選篩選'))], ['rows', {R}(Array.from(document.querySelectorAll('.fixed.inset-0 .overflow-y-auto')).filter(e => e.querySelector('input[type=checkbox]')).sort((a,b) => a.getBoundingClientRect().height - b.getBoundingClientRect().height)[0])], ['pager', {R}({SMALL}(/Page \\d+ of \\d+|第 \\d+/))], ['done', {R}({BTN}('^Done$|完成'))]])")

fig("12-generate-results", "/generate",
    setup=["(() => { const d = JSON.parse(localStorage.getItem('edurag:generateDraft') || '{}'); d.generatedQuestions = [{type:'single_choice', prompt:'Which organ pumps blood through the body?', options:['A. Heart','B. Lung','C. Liver','D. Skin'], answer:'A', explanation:'The heart is a muscular pump.', source:{document_id:1}}, {type:'cloze', prompt:'What organ pumps blood?', answer:'heart', explanation:'e', source:{document_id:1}}, {type:'true_false', prompt:'The heart has four chambers.', answer:'true', explanation:'e', source:{document_id:1}}]; d.savedAt = new Date().toISOString(); localStorage.setItem('edurag:generateDraft', JSON.stringify(d)); location.reload(); return 1 })()"],
    wait=4,
    after_setup_scroll="(() => { const h = Array.from(document.querySelectorAll('h2,h3')).find(h => /Generated|生成結果|Results/i.test(h.textContent)); h && h.scrollIntoView({block:'start'}); return 1 })()",
    rects=f"JSON.stringify([['summary', {R}(Array.from(document.querySelectorAll('p')).find(p => /format problem|格式有問題/.test(p.textContent)))], ['badge', {R}(Array.from(document.querySelectorAll('span')).find(s => /bg-red-100/.test(s.className)))], ['clear', {R}({BTN}('Clear Draft|清除暫存'))], ['save', {R}({BTN}('Save All|儲存全部|^Save'))]])",
    after=["(() => { localStorage.removeItem('edurag:generateDraft'); return 1 })()"])

fig("13-exam-step1", "/exam-paper",
    rects=f"JSON.stringify([['mode', {R}(Array.from(document.querySelectorAll('h2,h3')).find(h => /Step 1/i.test(h.textContent))?.parentElement)], ['review', {R}(Array.from(document.querySelectorAll('label')).find(l => /Review Test/i.test(l.textContent)))], ['draft', {R}({BTN}('Save Draft|儲存草稿'))], ['clearDraft', {R}({BTN}('Clear Draft|清除草稿'))]])")

fig("14-exam-step2", "/exam-paper",
    setup=["(() => { const h = Array.from(document.querySelectorAll('h2,h3')).find(h => /Step 2/i.test(h.textContent)); h && h.scrollIntoView({block:'start'}); window.scrollBy(0, -40); return 1 })()"],
    rects=f"JSON.stringify([['table', {R}(document.querySelector('input[type=number]')?.closest('div.bg-white.border'))], ['enabled', {R}(document.querySelector('input[type=number]')?.closest('.grid')?.children[2])], ['count', {R}(document.querySelector('input[type=number]'))], ['points', {R}(document.querySelectorAll('input[type=number]')[1])], ['order', {R}(document.querySelector('input[type=number]')?.closest('.grid')?.lastElementChild)]])")

fig("15-exam-draft", "/exam-paper",
    setup=["(() => { const b = " + BTN + "('Save Draft|儲存草稿'); b && b.scrollIntoView({block:'center'}); return !!b })()"],
    rects=f"JSON.stringify([['draft', {R}({BTN}('Save Draft|儲存草稿'))], ['clearDraft', {R}({BTN}('Clear Draft|清除草稿'))], ['design', {R}({BTN}('Design Exam|設計考卷'))]])")

fig("16-exam-designer", "/exam-paper",
    setup=["(() => { localStorage.removeItem('examPaperDraft'); location.reload(); return 1 })()", "1", "1", "(() => { const cbs = Array.from(document.querySelectorAll('div.cursor-pointer input[type=checkbox]')).slice(0, 5); cbs.forEach(c => c.click()); return cbs.length })()", "(() => { const b = " + BTN + "('Design Exam|設計考卷'); b && b.click(); return !!b })()", "1", "1", "(() => { const h = Array.from(document.querySelectorAll('h2,h3')).find(h => /Exam Designer/i.test(h.textContent)); h && h.scrollIntoView({block:'start'}); window.scrollBy(0, -16); return !!h })()"],
    wait=5, crop=(0, 0, 700, 860),
    rects=f"JSON.stringify([['design', {R}({LABELFIELD}('School Name')?.parentElement)], ['order', {R}(Array.from(document.querySelectorAll('h3,h4')).find(h => /Question Type Order/i.test(h.textContent))?.parentElement)], ['preview', {R}(Array.from(document.querySelectorAll('h3,h4,span')).find(h => /Live Preview/i.test(h.textContent))?.parentElement)], ['exportPaper', {R}({BTN}('Export Exam Paper'))], ['exportAnswer', {R}({BTN}('Export Answer'))]])")

fig("17-image-questions", "/image-questions",
    rects=f"JSON.stringify([['importHistory', {R}(Array.from(document.querySelectorAll('h2,h3,button')).find(e => /Import History|匯入紀錄/.test(e.textContent))?.closest('div.bg-white, section'))], ['stats', {R}(Array.from(document.querySelectorAll('div')).find(d => /Total Questions/.test(d.textContent) && d.children.length >= 4 && d.getBoundingClientRect().height < 160))], ['filters', {R}({LABELFIELD}('^Search')?.parentElement)], ['actions', {R}({BTN}('Upload Excel')?.parentElement)], ['viewBatch', {R}({BTN}('View Batch|檢視此批'))], ['deleteBatch', {R}({BTN}('Delete Batch|刪除此批'))]])")

fig("18-image-batch-toolbar", "/image-questions",
    setup=["1", "1", "(() => { const cbs = Array.from(document.querySelectorAll('input[type=checkbox]')).filter(c => c.offsetParent); cbs[1]?.click(); cbs[2]?.click(); return 1 })()", "(() => { const b = " + BTN + "('Verify Selected|驗證選中'); b && b.scrollIntoView({block:'center'}); return !!b })()"],
    rects=f"JSON.stringify([['toolbar', {R}({BTN}('Verify Selected|驗證選中')?.parentElement?.parentElement)], ['verify', {R}({BTN}('Verify Selected|驗證選中'))], ['retag', {R}({BTN}('Re-tag|改標籤'))], ['delete', {R}(Array.from(document.querySelectorAll('button')).find(b => /^Delete$|批次刪除/.test(b.textContent.trim()) && b.closest('div') === " + BTN + "('Verify Selected|驗證選中')?.closest('div')))]])")

fig("19-questions", "/questions",
    rects=f"JSON.stringify([['filters', {R}({LABELFIELD}('^Search')?.parentElement)], ['selectAll', {R}(Array.from(document.querySelectorAll('label')).find(l => /Select All|全選/i.test(l.textContent)))], ['actions', {R}(document.querySelector('button[title*=\"View\" i]')?.parentElement)]])")

fig("20-question-detail", "/questions",
    setup=["(() => { const b = document.querySelector('button[title*=\"View\" i]'); b && b.click(); return !!b })()"],
    rects=f"JSON.stringify([['panel', {R}(document.querySelector('.fixed.inset-0.bg-gray-600 > div'))], ['close', {R}(document.querySelector('.fixed.inset-0.bg-gray-600 > div button'))]])")

fig("21-settings", "/exam-paper",
    setup=["(() => { const g = " + GEAR + "(); g && g.click(); return !!g })()"],
    rects=f"JSON.stringify([['model', {R}({LABELFIELD}('Model|模型'))], ['recommended', {R}(Array.from(document.querySelectorAll('.fixed.inset-0 *')).find(e => /Recommended|建議/.test(e.textContent) && e.children.length <= 2 && e.tagName !== 'OPTION'))], ['save', {R}(Array.from(document.querySelectorAll('.fixed.inset-0 button')).find(b => /Save|儲存/.test(b.textContent)))]])")


fig("22-review-test", "/exam-paper",
    setup=["(() => { localStorage.removeItem('examPaperDraft'); location.reload(); return 1 })()", "1", "1", "(() => { const l = Array.from(document.querySelectorAll('label')).find(l => /Review Test/i.test(l.textContent)); const c = l && (l.querySelector('input') || l.previousElementSibling); (c || l).click(); return !!l })()", "1", "(() => { const s = Array.from(document.querySelectorAll('select')).find(s => Array.from(s.options).some(o => o.textContent.trim() === 'G4')); if (!s) return 0; s.value = Array.from(s.options).find(o => o.textContent.trim() === 'G4').value; s.dispatchEvent(new Event('change', {bubbles:true})); return 1 })()", "(() => { const chips = Array.from(document.querySelectorAll('label')).filter(l => /^g4_(health|science)_v4$/.test(l.textContent.trim())); chips.forEach(c => c.click()); return chips.length })()", "1", "(() => { const l = Array.from(document.querySelectorAll('label')).find(l => /Review Test/i.test(l.textContent)); l && l.scrollIntoView({block:'start'}); window.scrollBy(0, -24); return 1 })()"],
    rects=f"JSON.stringify([['review', {R}(Array.from(document.querySelectorAll('label')).find(l => /Review Test/i.test(l.textContent)))], ['grade', {R}({LABELNEXT}('Select Grade'))], ['subjects', {R}({LABELNEXT}('Select Subjects'))], ['count', {R}({LABELNEXT}('Question Count per Subject'))], ['display', {R}({LABELNEXT}('Display Mode'))]])")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://localhost:8989")
    ap.add_argument("--only", default="")
    args = ap.parse_args()
    only = {s.strip() for s in args.only.split(",") if s.strip()}
    OUT.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    b("viewport", "1280x860")
    # 側欄展開狀態存在 localStorage,先重設,避免上一輪點到漢堡鈕後所有圖都是收起的
    b("goto", args.base + "/exam-paper")
    time.sleep(2)
    js("(() => { localStorage.setItem('edurag:sidebarCollapsed', 'false'); return 1 })()")
    for f in FIGS:
        num = f["name"][:2]
        if only and num not in only:
            continue
        print("==", f["name"])
        b("goto", args.base + f["url"])
        time.sleep(2.5)
        for code in f["setup"]:
            js(code)
            time.sleep(1.2)
        time.sleep(f["wait"])
        if f.get("scroll"):
            js(f["scroll"])
            time.sleep(0.8)
        rects = rects_from_js(f["rects"])
        raw = RAW / f"{f['name']}.png"
        b("screenshot", "--viewport", str(raw))
        if not raw.exists():
            print("  screenshot missing!")
            continue
        annotate(raw, OUT / f"{f['name']}.png", rects, crop=f.get("crop"))
        print("  boxes:", [k for k, _ in rects])
        for code in f["after"]:
            js(code)
    print("done →", OUT)


if __name__ == "__main__":
    sys.exit(main())
