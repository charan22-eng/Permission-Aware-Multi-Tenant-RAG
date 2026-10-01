import os
import json
import uuid
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter

import sys
from pathlib import Path
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(REPO_ROOT))
from app.db import get_db_connection

QDRANT_PATH = os.getenv("QDRANT_PATH", "qdrant_storage")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "chunks_v2")
CORPUS_VERSION = int(os.getenv("CORPUS_VERSION", "2"))
DATA_PATH = "data/seed_data.jsonl"
CHUNK_NAMESPACE = uuid.uuid5(uuid.NAMESPACE_DNS, 'rag.chunks')

def main():
    print("Initializing Qdrant client and embedding model...")
    client = QdrantClient(path=QDRANT_PATH)
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Initialize Collection
    try:
        client.get_collection(COLLECTION_NAME)
        print(f"Collection {COLLECTION_NAME} exists.")
    except Exception:
        print(f"Creating collection {COLLECTION_NAME}...")
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE)
        )
        
    print("Loading seed data...")
    documents = []
    with open(DATA_PATH, "r") as f:
        for line in f:
            if line.strip():
                documents.append(json.loads(line))
                
    # We use roughly 500 tokens. Using RecursiveCharacterTextSplitter as a simple approximation 
    # (assuming ~4 chars per token -> 2000 chars, 200 overlap)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=200,
        length_function=len,
        is_separator_regex=False,
    )

    points = []
    print("Chunking and embedding documents...")
    with get_db_connection() as conn:
        cursor = conn.cursor()
        for doc in documents:
            chunks = text_splitter.create_documents([doc["content"]])
            
            tenant_id = "apex"
            classification = "public"
            allowed_roles = "[]"
            allowed_users = "[]"
            acl_version = 1
            
            cursor.execute('''
                INSERT OR REPLACE INTO documents_acl 
                (document_id, tenant_id, classification, allowed_roles, allowed_users, acl_version)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (doc["id"], tenant_id, classification, allowed_roles, allowed_users, acl_version))
            
            for i, chunk in enumerate(chunks):
                chunk_id = str(uuid.uuid5(CHUNK_NAMESPACE, f"{doc['id']}:{i}"))
                text = chunk.page_content
                embedding = model.encode(text).tolist()
                
                payload = {
                    "document_id": doc["id"],
                    "tenant_id": tenant_id,
                    "classification": classification,
                    "allowed_roles": json.loads(allowed_roles),
                    "allowed_users": json.loads(allowed_users),
                    "acl_version": acl_version,
                    "text": text,
                    "corpus_version": CORPUS_VERSION
                }
                
                if not payload.get("tenant_id"):
                    print(f"Refusing to ingest chunk {chunk_id} without tenant_id")
                    continue
                    
                points.append(
                    PointStruct(
                        id=chunk_id,
                        vector=embedding,
                        payload=payload
                    )
                )
        conn.commit()

    print(f"Upserting {len(points)} points into Qdrant...")
    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points
    )
    print("Ingestion complete.")

if __name__ == "__main__":
    main()
