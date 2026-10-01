import os
import json
import uuid
import sys
from pathlib import Path
from qdrant_client import QdrantClient
from langchain_text_splitters import RecursiveCharacterTextSplitter

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = REPO_ROOT / "data" / "seed_data.jsonl"
QUESTIONS_PATH = REPO_ROOT / "eval" / "questions.jsonl"
QUESTIONS_V2_PATH = REPO_ROOT / "eval" / "questions_v2.jsonl"
MAPPING_PATH = REPO_ROOT / "eval" / "id_mapping.json"
QDRANT_PATH = os.getenv("QDRANT_PATH", str(REPO_ROOT / "qdrant_storage"))

CHUNK_NAMESPACE = uuid.uuid5(uuid.NAMESPACE_DNS, 'rag.chunks')

def main():
    client = QdrantClient(path=QDRANT_PATH)
    
    try:
        scroll_res = client.scroll(collection_name="chunks", limit=10000, with_payload=True)
        old_points = scroll_res[0]
    except Exception as e:
        print(f"Error reading Qdrant 'chunks' collection: {e}")
        return
        
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=200,
        length_function=len,
        is_separator_regex=False,
    )
    
    text_to_new_id = {}
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip(): continue
            doc = json.loads(line)
            chunks = text_splitter.create_documents([doc["content"]])
            for i, chunk in enumerate(chunks):
                new_id = str(uuid.uuid5(CHUNK_NAMESPACE, f"{doc['id']}:{i}"))
                text_to_new_id[chunk.page_content] = new_id

    mapping = {}
    mapping["unanswerable"] = "unanswerable"
    
    for pt in old_points:
        text = pt.payload.get("text", "")
        old_id = pt.id
        if text in text_to_new_id:
            mapping[old_id] = text_to_new_id[text]
        else:
            pass # We'll catch unmapped things during question processing
            
    unmapped_count = 0
    with open(QUESTIONS_PATH, "r", encoding="utf-8") as fin, open(QUESTIONS_V2_PATH, "w", encoding="utf-8") as fout:
        for line in fin:
            if not line.strip(): continue
            q = json.loads(line)
            old_id = q["source_chunk_id"]
            
            if old_id not in mapping:
                print(f"Warning: Could not map ground-truth chunk for question: {q['question']} (Old ID: {old_id})")
                unmapped_count += 1
                q["source_chunk_id"] = "UNMAPPED_" + str(old_id)
            else:
                q["source_chunk_id"] = mapping[old_id]
                
            fout.write(json.dumps(q) + "\n")
            
    with open(MAPPING_PATH, "w", encoding="utf-8") as f:
        json.dump(mapping, f, indent=2)
        
    print(f"Migration complete. Saved to {QUESTIONS_V2_PATH}.")
    if unmapped_count > 0:
        print(f"Failed to map {unmapped_count} questions.")

if __name__ == "__main__":
    main()
