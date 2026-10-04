import sqlite3
from contextlib import contextmanager
from pathlib import Path

DB_PATH = Path(__file__).with_name("rabbit.db")
SCHEMA_PATH = Path(__file__).with_name("schema.sql")

# Columns that may be updated per table (id is never updatable).
UPDATABLE = {
    "knowledge": {"topic", "claim", "source", "confidence", "last_verified"},
    "experiences": {"task", "action", "result", "success", "reason"},
    "capabilities": {"application_name", "capability_name", "interface_type",
                     "instructions", "evidence", "confidence", "last_verified"},
    "lessons": {"task_type", "lesson", "conditions", "source_experience_id"},
}


@contextmanager
def get_connection(db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db(db_path=DB_PATH):
    """Create all four tables (safe to call repeatedly)."""
    with get_connection(db_path) as conn:
        conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))


# ---------- generic helpers ----------
def _insert(table, data, db_path):
    cols = list(data)
    sql = (f"INSERT INTO {table} ({', '.join(cols)}) "
           f"VALUES ({', '.join('?' for _ in cols)})")
    with get_connection(db_path) as conn:
        return conn.execute(sql, tuple(data.values())).lastrowid


def _get(table, row_id, db_path):
    with get_connection(db_path) as conn:
        row = conn.execute(f"SELECT * FROM {table} WHERE id = ?", (row_id,)).fetchone()
        return dict(row) if row else None


def _update(table, row_id, changes, db_path):
    bad = set(changes) - UPDATABLE[table]
    if bad:
        raise ValueError(f"Cannot update columns on {table}: {sorted(bad)}")
    if not changes:
        return False
    sets = ", ".join(f"{c} = ?" for c in changes)
    with get_connection(db_path) as conn:
        cur = conn.execute(f"UPDATE {table} SET {sets} WHERE id = ?",
                           (*changes.values(), row_id))
        return cur.rowcount > 0


def _list(table, where="", params=(), limit=100, db_path=DB_PATH):
    # `where` is always a fixed string written in this file, never user input.
    sql = f"SELECT * FROM {table} {where} ORDER BY id DESC LIMIT ?"
    with get_connection(db_path) as conn:
        return [dict(r) for r in conn.execute(sql, (*params, limit)).fetchall()]


# ---------- A. Knowledge ----------
def add_knowledge(topic, claim, source=None, confidence=0.5, db_path=DB_PATH):
    return _insert("knowledge", {"topic": topic, "claim": claim,
                                 "source": source, "confidence": confidence}, db_path)

def get_knowledge(row_id, db_path=DB_PATH):
    return _get("knowledge", row_id, db_path)

def search_knowledge(topic, limit=100, db_path=DB_PATH):
    return _list("knowledge", "WHERE topic LIKE ?", (f"%{topic}%",), limit, db_path)

def update_knowledge(row_id, db_path=DB_PATH, **changes):
    return _update("knowledge", row_id, changes, db_path)

def verify_knowledge(row_id, confidence=None, db_path=DB_PATH):
    changes = {"last_verified": _now(db_path)}
    if confidence is not None:
        changes["confidence"] = confidence
    return _update("knowledge", row_id, changes, db_path)


# ---------- B. Experiences ----------
def add_experience(task, action, result=None, success=False, reason=None, db_path=DB_PATH):
    return _insert("experiences", {"task": task, "action": action, "result": result,
                                   "success": int(bool(success)), "reason": reason}, db_path)

def get_experience(row_id, db_path=DB_PATH):
    return _get("experiences", row_id, db_path)

def list_experiences(task=None, success=None, limit=100, db_path=DB_PATH):
    clauses, params = [], []
    if task is not None:
        clauses.append("task LIKE ?"); params.append(f"%{task}%")
    if success is not None:
        clauses.append("success = ?"); params.append(int(bool(success)))
    where = ("WHERE " + " AND ".join(clauses)) if clauses else ""
    return _list("experiences", where, tuple(params), limit, db_path)

def update_experience(row_id, db_path=DB_PATH, **changes):
    if "success" in changes:
        changes["success"] = int(bool(changes["success"]))
    return _update("experiences", row_id, changes, db_path)


# ---------- C. Capabilities ----------
def add_capability(application_name, capability_name, interface_type,
                   instructions=None, evidence=None, confidence=0.5, db_path=DB_PATH):
    return _insert("capabilities", {"application_name": application_name,
                                    "capability_name": capability_name,
                                    "interface_type": interface_type,
                                    "instructions": instructions,
                                    "evidence": evidence,
                                    "confidence": confidence}, db_path)

def get_capability(row_id, db_path=DB_PATH):
    return _get("capabilities", row_id, db_path)

def find_capabilities(application_name, limit=100, db_path=DB_PATH):
    return _list("capabilities", "WHERE application_name LIKE ?",
                 (f"%{application_name}%",), limit, db_path)

def update_capability(row_id, db_path=DB_PATH, **changes):
    return _update("capabilities", row_id, changes, db_path)


# ---------- D. Lessons ----------
def add_lesson(task_type, lesson, conditions=None, source_experience_id=None, db_path=DB_PATH):
    return _insert("lessons", {"task_type": task_type, "lesson": lesson,
                               "conditions": conditions,
                               "source_experience_id": source_experience_id}, db_path)

def get_lesson(row_id, db_path=DB_PATH):
    return _get("lessons", row_id, db_path)

def find_lessons(task_type, limit=100, db_path=DB_PATH):
    return _list("lessons", "WHERE task_type LIKE ?", (f"%{task_type}%",), limit, db_path)

def update_lesson(row_id, db_path=DB_PATH, **changes):
    return _update("lessons", row_id, changes, db_path)


def _now(db_path=DB_PATH):
    with get_connection(db_path) as conn:
        return conn.execute("SELECT datetime('now')").fetchone()[0]


if __name__ == "__main__":
    init_db()
    print(f"Database ready at {DB_PATH}")