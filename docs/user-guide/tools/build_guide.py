"""USER_GUIDE.md → 自含式 HTML(圖片 base64 內嵌)→ PDF(Chrome headless)。

用法:python docs/user-guide/tools/build_guide.py [--no-pdf]
輸出:docs/user-guide/USER_GUIDE.html、docs/user-guide/USER_GUIDE.pdf
"""

import argparse
import base64
import mimetypes
import re
import subprocess
import sys
from pathlib import Path

import markdown
from markdown.extensions.toc import slugify_unicode

ROOT = Path(__file__).resolve().parents[1]
MD = ROOT / "USER_GUIDE.md"
HTML = ROOT / "USER_GUIDE.html"
PDF = ROOT / "USER_GUIDE.pdf"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

CSS = """
:root { color-scheme: light; }
* { box-sizing: border-box; }
body {
  margin: 0; padding: 32px 40px; color: #1f2937; background: #fff;
  font-family: -apple-system, "PingFang TC", "Noto Sans TC", "Microsoft JhengHei", "Segoe UI", sans-serif;
  font-size: 14px; line-height: 1.7; max-width: 960px; margin: 0 auto;
}
h1 { font-size: 28px; margin: 0 0 12px; letter-spacing: .01em; }
h2 { font-size: 21px; margin: 40px 0 12px; padding-bottom: 6px; border-bottom: 2px solid #2563eb; color: #1e3a8a; }
h3 { font-size: 16px; margin: 26px 0 8px; color: #111827; }
h4 { font-size: 14px; margin: 18px 0 6px; }
p { margin: 8px 0; }
a { color: #2563eb; text-decoration: none; }
blockquote { margin: 12px 0; padding: 8px 14px; background: #eff6ff; border-left: 4px solid #60a5fa; color: #1e3a8a; }
blockquote p { margin: 4px 0; }
code { font-family: Menlo, "SF Mono", Consolas, monospace; font-size: 12.5px; background: #f3f4f6; padding: 1px 5px; border-radius: 4px; }
pre { background: #f3f4f6; padding: 10px 12px; border-radius: 6px; overflow-x: auto; }
pre code { background: none; padding: 0; }
table { border-collapse: collapse; width: 100%; margin: 10px 0 14px; font-size: 13px; }
th, td { border: 1px solid #d1d5db; padding: 6px 10px; text-align: left; vertical-align: top; }
th { background: #f3f4f6; }
tr:nth-child(even) td { background: #fafafa; }
img { max-width: 100%; height: auto; display: block; margin: 12px auto 4px; border: 1px solid #d1d5db; border-radius: 6px; }
figure { margin: 14px 0 18px; }
figcaption { text-align: center; color: #6b7280; font-size: 12.5px; margin-top: 4px; }
ul, ol { padding-left: 24px; }
li { margin: 3px 0; }
hr { border: 0; border-top: 1px solid #e5e7eb; margin: 28px 0; }
.badge { display: inline-block; min-width: 20px; padding: 0 5px; border-radius: 5px; background: #dc2626; color: #fff; font-weight: 700; font-size: 12px; text-align: center; line-height: 20px; margin-right: 4px; }
.toc { background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 8px; padding: 12px 18px; margin: 16px 0 24px; }
.toc ul { margin: 0; padding-left: 20px; }
.meta { color: #6b7280; font-size: 12.5px; }
@media print {
  body { padding: 0; max-width: none; font-size: 12.5px; }
  h2 { page-break-before: always; break-before: page; }
  h2:first-of-type, h2[id="目錄"] { page-break-before: auto; break-before: auto; }
  figure, table, blockquote, img { page-break-inside: avoid; break-inside: avoid; }
  h2, h3, h4 { page-break-after: avoid; break-after: avoid; }
  a { color: inherit; }
}
@page { size: A4; margin: 16mm 14mm; }
"""


def embed_images(html: str) -> str:
    """把 <img src="images/xx.png"> 換成 base64 data URI,並包成 <figure> + 圖說(alt)。"""

    def repl(m):
        alt, src = m.group("alt"), m.group("src")
        path = ROOT / src
        if not path.exists():
            print(f"  ⚠ missing image: {src}", file=sys.stderr)
            return m.group(0)
        mime = mimetypes.guess_type(str(path))[0] or "image/png"
        data = base64.b64encode(path.read_bytes()).decode()
        # alt 屬性內不能放徽章 HTML,圓圈數字改成純數字;圖說保留圓圈數字給 badges() 轉換
        alt_attr = re.sub("[①-⑩]", lambda c: str(ord(c.group()) - ord("①") + 1), alt)
        return f'<figure><img src="data:{mime};base64,{data}" alt="{alt_attr}"><figcaption>{alt}</figcaption></figure>'

    return re.sub(r'<p><img alt="(?P<alt>[^"]*)" src="(?P<src>[^"]+)"\s*/?></p>', repl, html)


def badges(html: str) -> str:
    """把文中的 ①②… 圓圈數字換成紅色徽章,與截圖上的編號一致。"""
    circled = "①②③④⑤⑥⑦⑧⑨⑩"
    for i, ch in enumerate(circled, 1):
        html = html.replace(ch, f'<span class="badge">{i}</span>')
    return html


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-pdf", action="store_true")
    args = ap.parse_args()

    text = MD.read_text(encoding="utf-8")
    md = markdown.Markdown(extensions=["tables", "fenced_code", "toc", "sane_lists"], extension_configs={"toc": {"toc_depth": "2-3", "slugify": slugify_unicode}})
    body = md.convert(text)
    body = body.replace("[TOC]", "")
    body = embed_images(body)
    body = badges(body)
    title = re.search(r"^# (.+)$", text, re.M).group(1)
    doc = f"""<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>{CSS}</style>
</head>
<body>
{body}
</body>
</html>
"""
    HTML.write_text(doc, encoding="utf-8")
    print("html →", HTML, f"({HTML.stat().st_size // 1024} KB)")

    if args.no_pdf:
        return 0
    cmd = [CHROME, "--headless", "--disable-gpu", "--no-pdf-header-footer", f"--print-to-pdf={PDF}", "--virtual-time-budget=10000", HTML.as_uri()]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    if not PDF.exists():
        print("pdf failed:", r.stderr[-800:], file=sys.stderr)
        return 1
    print("pdf  →", PDF, f"({PDF.stat().st_size // 1024} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
