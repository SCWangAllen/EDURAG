from fastapi import APIRouter
from app.schemas.ingest import IngestRequest, IngestResponse, ChunkInfo

router = APIRouter(prefix="/api/ingest", tags=["mock", "ingest"])

@router.post("/", response_model=IngestResponse)
async def mock_ingest(req: IngestRequest):
    """Mock文件攝取API，回傳與真實API相同的Schema"""
    
    # 模擬分塊結果
    mock_chunks = [
        ChunkInfo(
            chunk_id=1001,
            text="這是第一個文本塊的內容，包含了相關的教材內容。",
            token_count=25
        ),
        ChunkInfo(
            chunk_id=1002, 
            text="這是第二個文本塊，包含更多詳細的說明和範例。",
            token_count=22
        ),
        ChunkInfo(
            chunk_id=1003,
            text="最後一個文本塊提供了總結和重點整理。", 
            token_count=18
        )
    ]
    
    return IngestResponse(
        document_id=999,
        chunks=mock_chunks,
        total_chunks=3,
        processing_time=0.5
    )
