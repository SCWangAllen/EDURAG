from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
import psycopg

class IngestResp(BaseModel):
    chunks_ingested: int

router = APIRouter()

@router.post("/{doc_id}", response_model=IngestResp, status_code=201)
async def ingest(doc_id: int):
    conn = psycopg.connect()
    doc = conn.execute("SELECT content FROM documents WHERE id=%s", (doc_id,)).fetchone()
    if not doc:
        raise HTTPException(404, "Document not found")

    splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)
    chunks = splitter.split_text(doc[0])
    embed = OpenAIEmbeddings(model="text-embedding-3-small")
    vectors = embed.embed_documents(chunks)

    with conn.transaction():
        for idx, (txt, vec) in enumerate(zip(chunks, vectors)):
            conn.execute(
                "INSERT INTO embeddings (doc_id, chunk_id, chunk_text, embedding) VALUES (%s,%s,%s,%s)",
                (doc_id, idx, txt, vec)
            )
    return {"chunks_ingested": len(chunks)}
