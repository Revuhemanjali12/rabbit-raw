# RABBIT RAW — Database & Memory Layer

SQLite + Python. No server needed.

## Files
| File | Purpose |
|---|---|
| `schema.sql` | Table definitions (knowledge, experiences, capabilities, lessons) |
| `database.py` | `init_db()` plus add / get / search / update functions |
| `test_database.py` | Smoke test using a temporary database |

## Setup
1. Install Python 3.8+ (SQLite is built in, nothing else to install).
2. Put all files in one folder and open a terminal there.
3. Create the database: `python database.py` (creates `rabbit.db`)
4. Run the test: `python test_database.py` — expect `ALL TESTS PASSED`.
5. (Optional) Open `rabbit.db` in DB Browser for SQLite to view the tables.

## Usage
```python
import database as db

db.init_db()
kid = db.add_knowledge("python", "SQLite is in the stdlib", source="python.org", confidence=0.9)
eid = db.add_experience("open app", "click menu", "failed", success=False, reason="menu missing")
db.add_lesson("open_app", "Prefer shortcuts", "UI varies", source_experience_id=eid)
db.add_capability("Notepad", "open file", "CLI", "notepad.exe <path>", confidence=0.8)

db.search_knowledge("python")
db.list_experiences(success=False)       # failed attempts
db.update_knowledge(kid, confidence=0.7)
db.verify_knowledge(kid)                 # sets last_verified
```

## Rules built in
- All queries are parameterized; update column names are whitelisted.
- Failed attempts are stored (`success = 0` + `reason`).
- Every claim keeps `source` and `confidence` (0.0–1.0); nothing is assumed true.
- Store structured summaries and source references, not whole documents.
- Each function accepts `db_path=` so the Rabbit controller can use its own file.

## Git
```
git add schema.sql database.py test_database.py README.md
git commit -m "Add RABBIT database layer"
```
Add `rabbit.db` to `.gitignore`.