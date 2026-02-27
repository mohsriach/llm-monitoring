import os
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from typing import Any, Dict, List

DEFAULT_DB_PATH = os.getenv("MONITORING_DB_PATH", "data/monitoring/requests.db")


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS inference_logs (
    id TEXT PRIMARY KEY,
    created_at TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    model TEXT,
    status TEXT NOT NULL,
    latency_ms REAL NOT NULL,
    prompt_text TEXT,
    response_text TEXT,
    prompt_chars INTEGER,
    response_chars INTEGER,
    error_message TEXT
);
CREATE INDEX IF NOT EXISTS idx_inference_created_at ON inference_logs(created_at);
"""


def _connect(db_path: str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str = DEFAULT_DB_PATH) -> None:
    with closing(_connect(db_path)) as conn:
        conn.executescript(SCHEMA_SQL)
        conn.commit()


def log_inference(entry: Dict[str, Any], db_path: str = DEFAULT_DB_PATH) -> None:
    sql = """
    INSERT INTO inference_logs (
      id, created_at, endpoint, model, status, latency_ms,
      prompt_text, response_text, prompt_chars, response_chars, error_message
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    now = datetime.now(timezone.utc).isoformat()
    with closing(_connect(db_path)) as conn:
        conn.execute(
            sql,
            (
                entry["id"],
                entry.get("created_at", now),
                entry.get("endpoint", ""),
                entry.get("model"),
                entry.get("status", "unknown"),
                float(entry.get("latency_ms", 0.0)),
                entry.get("prompt_text"),
                entry.get("response_text"),
                int(entry.get("prompt_chars", 0)),
                int(entry.get("response_chars", 0)),
                entry.get("error_message"),
            ),
        )
        conn.commit()


def fetch_recent_logs(limit: int = 5000, db_path: str = DEFAULT_DB_PATH) -> List[Dict[str, Any]]:
    sql = """
    SELECT * FROM inference_logs
    ORDER BY created_at DESC
    LIMIT ?
    """
    with closing(_connect(db_path)) as conn:
        rows = conn.execute(sql, (limit,)).fetchall()
        return [dict(row) for row in rows]
