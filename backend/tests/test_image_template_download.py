"""GET /api/image-questions/template:圖片題 Excel 範本下載(欄位名與匯入解析一致)。"""
import io

import pandas as pd
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.routers import image_questions

app = FastAPI()
app.include_router(image_questions.router)
client = TestClient(app)


def test_template_downloads_xlsx_with_import_columns():
    response = client.get("/api/image-questions/template")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith(
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    assert "image_question_template.xlsx" in response.headers["content-disposition"]

    sheets = pd.read_excel(io.BytesIO(response.content), sheet_name=None)
    first = list(sheets.values())[0]  # parse_excel 讀第一個 sheet
    assert list(first.columns) == [
        "q_image", "ans_image", "question", "subject", "chapter", "grade", "page", "blanks",
    ]
    assert "Instructions" in sheets
