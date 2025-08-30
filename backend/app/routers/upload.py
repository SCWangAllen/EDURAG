from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.services.document_service import DocumentService
from app.core.config import USE_MOCK_API
from typing import Optional, Dict, Any, List
import pandas as pd
import io
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/upload", tags=["upload"])

async def get_document_service(db: AsyncSession = Depends(get_db)) -> DocumentService:
    """獲取文件服務實例"""
    return DocumentService(db)

@router.post("/excel")
async def upload_excel(
    file: UploadFile = File(...),
    preview_only: bool = Form(False),
    service: DocumentService = Depends(get_document_service)
) -> Dict[str, Any]:
    """
    上傳 Excel 文件並解析
    - file: Excel 文件
    - preview_only: 是否只預覽，不實際儲存
    """
    
    # 驗證文件類型
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="只支援 Excel 文件 (.xlsx, .xls)")
    
    try:
        # 讀取文件內容
        contents = await file.read()
        df = pd.read_excel(io.BytesIO(contents))
        
        logger.info(f"成功讀取 Excel 文件 {file.filename}，包含 {len(df)} 筆資料")
        
        # 驗證必要欄位
        required_columns = ['Words', 'Chapter', 'Subject', 'Imagesrelated']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise HTTPException(
                status_code=400, 
                detail=f"Excel 文件缺少必要欄位: {', '.join(missing_columns)}"
            )
        
        # 解析資料
        processed_documents = []
        for index, row in df.iterrows():
            # 準備資料
            content = str(row['Words']) if pd.notna(row['Words']) else ''
            chapter = str(row['Chapter']) if pd.notna(row['Chapter']) else ''
            subject = str(row['Subject']) if pd.notna(row['Subject']) else '健康'
            image_filename = str(row['Imagesrelated']) if pd.notna(row['Imagesrelated']) else None
            
            # 生成標題
            if chapter:
                title = chapter.split('\\n')[0][:100] if '\\n' in chapter else chapter[:100]
            else:
                title = content[:50] + '...' if len(content) > 50 else content
            
            # 生成內容分塊預覽（用於RAG系統）
            chunks = generate_content_chunks(content, chunk_size=500)
            
            doc_data = {
                'index': index + 1,
                'title': title.strip(),
                'content': content,
                'subject': subject,
                'chapter': chapter,
                'image_filename': image_filename,
                'chunks': chunks,
                'chunk_count': len(chunks),
                'content_length': len(content)
            }
            processed_documents.append(doc_data)
        
        # 如果只是預覽，返回處理結果
        if preview_only:
            return {
                'message': f'成功解析 Excel 文件，包含 {len(processed_documents)} 筆資料',
                'file_name': file.filename,
                'total_documents': len(processed_documents),
                'documents': processed_documents,
                'preview_mode': True
            }
        
        # 實際儲存到資料庫
        saved_count = 0
        for doc_data in processed_documents:
            try:
                # 使用 DocumentService 創建文件
                document = await service.create_document({
                    'title': doc_data['title'],
                    'content': doc_data['content'],
                    'subject': doc_data['subject'],
                    'chapter': doc_data['chapter'],
                    'image_filename': doc_data['image_filename'],
                    'import_source': 'excel_upload'
                })
                saved_count += 1
                
            except Exception as e:
                logger.error(f"儲存第 {doc_data['index']} 筆資料失敗: {e}")
        
        return {
            'message': f'成功上傳並儲存 {saved_count} 筆文件',
            'file_name': file.filename,
            'total_documents': len(processed_documents),
            'saved_documents': saved_count,
            'documents': processed_documents[:5],  # 只返回前5筆作為範例
            'preview_mode': False
        }
        
    except pd.errors.EmptyDataError:
        raise HTTPException(status_code=400, detail="Excel 文件為空或格式錯誤")
    except Exception as e:
        logger.error(f"處理 Excel 文件時發生錯誤: {e}")
        raise HTTPException(status_code=500, detail=f"處理文件時發生錯誤: {str(e)}")

def generate_content_chunks(content: str, chunk_size: int = 500, overlap: int = 50) -> List[Dict[str, Any]]:
    """
    將長文本分割成較小的塊（用於RAG系統）
    """
    if len(content) <= chunk_size:
        return [{
            'chunk_index': 1,
            'text': content,
            'start_pos': 0,
            'end_pos': len(content),
            'length': len(content)
        }]
    
    chunks = []
    start = 0
    chunk_index = 1
    
    while start < len(content):
        end = min(start + chunk_size, len(content))
        
        # 嘗試在句號或段落結束處分割
        if end < len(content):
            for break_char in ['。', '\\n', '.', '!', '?']:
                last_break = content.rfind(break_char, start, end)
                if last_break > start:
                    end = last_break + 1
                    break
        
        chunk_text = content[start:end].strip()
        if chunk_text:
            chunks.append({
                'chunk_index': chunk_index,
                'text': chunk_text,
                'start_pos': start,
                'end_pos': end,
                'length': len(chunk_text)
            })
            chunk_index += 1
        
        # 下一個塊的開始位置（有重疊）
        start = max(end - overlap, start + 1)
    
    return chunks

@router.get("/template")
async def get_excel_template():
    """
    下載 Excel 範本文件
    """
    template_data = {
        'Words': ['文件內容範例...', '另一篇文件的內容...'],
        'Chapter': ['第一章 健康飲食', '第二章 運動健身'],
        'Subject': ['健康', '健康'],
        'Imagesrelated': ['image1.jpg', None]
    }
    
    df = pd.DataFrame(template_data)
    
    # 創建 Excel 文件
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='工作表1', index=False)
    
    output.seek(0)
    
    from fastapi.responses import StreamingResponse
    return StreamingResponse(
        io.BytesIO(output.read()),
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment; filename=document_template.xlsx'}
    )