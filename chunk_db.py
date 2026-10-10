import json
from pathlib import Path

import database as db

CHUNK_SCHEMA = Path(__file__).with_name("chunk_schema.sql")
CHUNK_JSON = Path(__file__).with_name("chunk_data.json")


def init_chunk_table(db_path=db.DB_PATH):
    with db.get_connection(db_path) as conn:
        conn.executescript(CHUNK_SCHEMA.read_text(encoding="utf-8"))


def add_chunk(content, reason_useless, source=None, db_path=db.DB_PATH):
    with db.get_connection(db_path) as conn:
        return conn.execute(
            "INSERT INTO chunk_data (content, reason_useless, source) VALUES (?, ?, ?)",
            (content, reason_useless, source)).lastrowid


def list_chunks(reason=None, limit=100, db_path=db.DB_PATH):
    sql, params = "SELECT * FROM chunk_data", []
    if reason:
        sql += " WHERE reason_useless LIKE ?"
        params.append(f"%{reason}%")
    sql += " ORDER BY id DESC LIMIT ?"
    params.append(limit)
    with db.get_connection(db_path) as conn:
        return [dict(r) for r in conn.execute(sql, params).fetchall()]


def load_chunks_from_json(path=CHUNK_JSON, db_path=db.DB_PATH):
    items = json.loads(Path(path).read_text(encoding="utf-8"))
    return [add_chunk(i["content"], i["reason_useless"], i.get("source"), db_path)
            for i in items]


if __name__ == "__main__":
    init_chunk_table()
    print("Chunk records loaded:", len(load_chunks_from_json()))