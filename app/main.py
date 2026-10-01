import os
import time
import uuid
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from openai import OpenAI
from app.db import log_request
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Multi-Tenant RAG API - Phase 0")

QDRANT_PATH = os.getenv("QDRANT_PATH", "qdrant_storage")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "chunks_v2")


qdrant_client = QdrantClient(path=QDRANT_PATH)
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
openai_client = OpenAI(
    api_key="ollama",
    base_url="http://localhost:11434/v1"
)

class QueryRequest(BaseModel):
    query: str
    k: int = 5

class QueryResponse(BaseModel):
    answer: str
    context_chunk_ids: list[str]
    eval_chunk_ids: list[str]

CORPUS_VERSION = int(os.getenv("CORPUS_VERSION", "2"))

@app.get("/health")
def health_check():
    return {"project": "Permission-Aware Multi-Tenant RAG", "corpus_version": CORPUS_VERSION}

@app.post("/query", response_model=QueryResponse)
def query_endpoint(req: QueryRequest):
    start_time = time.time()
    request_id = str(uuid.uuid4())
    
    # 1. Embed query
    query_vector = embedding_model.encode(req.query).tolist()
    
    # Cap k at 10
    limit_k = min(req.k, 10)
    
    # 2. Retrieve top-k from Qdrant
    search_result = qdrant_client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=limit_k
    ).points
    
    if not search_result:
        return QueryResponse(answer="I don't know.", context_chunk_ids=[], eval_chunk_ids=[])
    
    retrieved_chunk_ids = [point.id for point in search_result]
    context_chunks = search_result[:5]
    context_chunk_ids = [point.id for point in context_chunks]
    
    # Construct context for LLM using ONLY top 5 chunks
    context_blocks = []
    for point in context_chunks:
        chunk_text = point.payload.get("text", "")
        chunk_id = point.id
        context_blocks.append(f"Chunk ID: {chunk_id}\nContent: {chunk_text}")
    
    context_str = "\n\n".join(context_blocks)
    
    # 3. Generate answer with inline citations
    system_prompt = (
        "You are a helpful AI assistant. Answer the user's question based ONLY on the provided context.\n"
        "Include an inline citation at the end of your answer by referencing the Chunk ID exactly in brackets, e.g. [Chunk ID].\n"
        "Do not write 'According to Chunk ID', just append [Chunk ID] to the end of the fact.\n"
        "If you cannot answer based on the context, say 'I don't know'."
    )
    
    user_prompt = f"Context:\n{context_str}\n\nQuestion: {req.query}"
    
    llm_model = "llama3.1"
    
    for attempt in range(1):
        try:
            response = openai_client.chat.completions.create(
                model=llm_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.0,
                seed=42
            )
            answer = response.choices[0].message.content
            break
        except Exception as e:
            answer = "Error: Rate limit exhausted or API unavailable."
            break
    
    latency_ms = (time.time() - start_time) * 1000
    
    # 4. Log request to SQLite
    log_request(
        request_id=request_id,
        query=req.query,
        retrieved_chunk_ids=retrieved_chunk_ids,
        answer=answer,
        model=llm_model,
        latency_ms=latency_ms
    )
    
    return QueryResponse(answer=answer, context_chunk_ids=context_chunk_ids, eval_chunk_ids=retrieved_chunk_ids)
