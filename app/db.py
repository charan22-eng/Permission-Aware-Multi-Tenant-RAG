import sqlite3
import os
from contextlib import contextmanager

DB_PATH = os.getenv("SQLITE_DB_PATH", "audit_log.db")

def init_db():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        # Phase 2 will add tenant_id, user_id, and second_layer_filter_caught flag to this schema
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                request_id TEXT NOT NULL,
                query TEXT NOT NULL,
                retrieved_chunk_ids TEXT NOT NULL,
                answer TEXT NOT NULL,
                model TEXT NOT NULL,
                latency_ms REAL NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents_acl (
                document_id TEXT PRIMARY KEY,
                tenant_id TEXT NOT NULL,
                classification TEXT NOT NULL,
                allowed_roles TEXT NOT NULL,
                allowed_users TEXT NOT NULL,
                acl_version INTEGER NOT NULL
            )
        ''')
        conn.commit()

@contextmanager
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
    finally:
        conn.close()

def log_request(request_id: str, query: str, retrieved_chunk_ids: list, answer: str, model: str, latency_ms: float):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO requests (request_id, query, retrieved_chunk_ids, answer, model, latency_ms)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (request_id, query, ",".join(retrieved_chunk_ids), answer, model, latency_ms))
        conn.commit()

init_db()
