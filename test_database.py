"""Smoke test: creates a throwway DB, inserts sample data, reads it back."""
import os
import sqlite3
import tempfile

import database as db


def main():
    path = os.path.join(tempfile.mkdtemp(), "test_rabbit.db")
    db.init_db(path)

    with db.get_connection(path) as conn:
        tables = {r[0] for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")}
    assert tables == {"knowledge", "experiences", "capabilities", "lessons"}, tables
    print("Tables:", sorted(tables))

    # Knowledge
    k = db.add_knowledge("python", "SQLite ships with Python's stdlib",
                         source="docs.python.org/3/library/sqlite3.html", confidence=0.9, db_path=path)
    db.verify_knowledge(k, confidence=0.95, db_path=path)
    kr = db.get_knowledge(k, db_path=path)
    assert kr["confidence"] == 0.95 and kr["last_verified"], kr

    # Experiences (one failure, one success)
    e_fail = db.add_experience("open notepad", "click start menu", "menu not found",
                               success=False, reason="UI layout differed", db_path=path)
    e_ok = db.add_experience("open notepad", "use Win+R then notepad", "opened",
                             success=True, db_path=path)
    assert len(db.list_experiences(success=False, db_path=path)) == 1
    db.update_experience(e_ok, result="Notepad opened in 1s", db_path=path)

    # Capabilities
    c = db.add_capability("Notepad", "open file", "CLI", "notepad.exe <path>",
                          evidence="ran successfully", confidence=0.8, db_path=path)
    db.update_capability(c, confidence=0.9, db_path=path)
    assert db.find_capabilities("note", db_path=path)[0]["confidence"] == 0.9

    # Lessons linked to an experience
    l = db.add_lesson("open_app", "Prefer keyboard shortcuts over menu clicks",
                      "when UI layout may vary", source_experience_id=e_fail, db_path=path)
    assert db.get_lesson(l, db_path=path)["source_experience_id"] == e_fail

    # SQL-injection attempt is stored as plain text, tables survive
    db.add_knowledge("x'); DROP TABLE knowledge;--", "harmless", db_path=path)
    assert len(db.search_knowledge("DROP", db_path=path)) == 1

    # Bad column names are rejected
    try:
        db.update_knowledge(k, db_path=path, **{"claim = 'x' --": "y"})
        raise AssertionError("should have failed")
    except ValueError:
        pass

    # Constraint check: confidence out of range is rejected
    try:
        db.add_knowledge("t", "c", confidence=5, db_path=path)
        raise AssertionError("should have failed")
    except sqlite3.IntegrityError:
        pass

    print("Knowledge:", db.get_knowledge(k, db_path=path))
    print("Experiences:", len(db.list_experiences(db_path=path)))
    print("Capabilities:", db.find_capabilities("Notepad", db_path=path))
    print("Lessons:", db.find_lessons("open_app", db_path=path))
    print("\nALL TESTS PASSED")


if __name__ == "__main__":
    main()